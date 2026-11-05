"""Generate or edit one image through a hosted API (Gemini or OpenAI), with reference images,
an enforced per-task budget and a reproducibility record. Every non-dry run costs money.

Keys come only from the environment (GEMINI_API_KEY or OPENAI_API_KEY); never pass them as
arguments or write them to files. Standard library only."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid

GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
OPENAI_GEN = 'https://api.openai.com/v1/images/generations'
OPENAI_EDIT = 'https://api.openai.com/v1/images/edits'
KEY_ENV = {'gemini': 'GEMINI_API_KEY', 'openai': 'OPENAI_API_KEY'}
# Image calls routinely take 20-90 s; 300 s leaves room for large edits without hanging forever.
TIMEOUT_S = 300


class BudgetError(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_budget(path):
    data = json.loads(path.read_text())
    if not isinstance(data.get('max'), int) or not isinstance(data.get('used'), int):
        raise ValueError('budget file must contain integer "max" and "used"')
    return data


def build_request(provider, model, prompt, images, mask=None, size=None):
    """Return (url, body_bytes, content_type). Pure: no network, no key."""
    if provider == 'gemini':
        if mask:
            raise ValueError('Gemini has no mask input; describe the region in the prompt or use a provider with masks')
        parts = [{'text': prompt}]
        for p in images:
            mime = mimetypes.guess_type(p.name)[0] or 'image/png'
            parts.append({'inline_data': {'mime_type': mime, 'data': base64.b64encode(p.read_bytes()).decode()}})
        body = {'contents': [{'parts': parts}], 'generationConfig': {'responseModalities': ['IMAGE']}}
        return GEMINI_URL.format(model=model), json.dumps(body).encode(), 'application/json'
    if provider == 'openai':
        if not images:
            body = {'model': model, 'prompt': prompt, 'n': 1}
            if size:
                body['size'] = size
            return OPENAI_GEN, json.dumps(body).encode(), 'application/json'
        boundary = uuid.uuid4().hex
        chunks = []
        def field(name, value):
            chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        def file(name, p):
            mime = mimetypes.guess_type(p.name)[0] or 'image/png'
            chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{p.name}"\r\n'
                          f'Content-Type: {mime}\r\n\r\n'.encode() + p.read_bytes() + b'\r\n')
        field('model', model); field('prompt', prompt); field('n', '1')
        if size:
            field('size', size)
        for p in images:
            file('image[]', p)
        if mask:
            file('mask', mask)
        chunks.append(f'--{boundary}--\r\n'.encode())
        return OPENAI_EDIT, b''.join(chunks), f'multipart/form-data; boundary={boundary}'
    raise ValueError(f'unknown provider {provider!r}')


def extract_image(provider, payload):
    if provider == 'gemini':
        for cand in payload.get('candidates', []):
            for part in cand.get('content', {}).get('parts', []):
                data = part.get('inline_data') or part.get('inlineData')
                if data and data.get('data'):
                    return base64.b64decode(data['data'])
        reason = payload.get('promptFeedback') or [c.get('finishReason') for c in payload.get('candidates', [])]
        raise ValueError(f'no image in response: {reason}')
    items = payload.get('data') or []
    if items and items[0].get('b64_json'):
        return base64.b64decode(items[0]['b64_json'])
    raise ValueError('no b64_json image in response')


def call(provider, url, body, content_type, key):
    headers = {'Content-Type': content_type}
    if provider == 'gemini':
        headers['x-goog-api-key'] = key
    else:
        headers['Authorization'] = f'Bearer {key}'
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read()[:500].decode(errors='replace')
        raise ValueError(f'HTTP {e.code}: {detail}') from None


def run(a):
    images = list(a.image or [])
    for p in images + ([a.mask] if a.mask else []):
        if not p.is_file():
            raise ValueError(f'missing input {p}')
    prompt = a.prompt_file.read_text() if a.prompt_file else a.prompt
    if not prompt:
        raise ValueError('prompt required (--prompt or --prompt-file)')
    url, body, ctype = build_request(a.provider, a.model, prompt, images, a.mask, a.size)
    record = {'tool': 'art_generate_image', 'provider': a.provider, 'model': a.model, 'endpoint': url,
              'prompt': prompt, 'size': a.size,
              'inputs': [{'role': 'reference', 'path': str(p.resolve()), 'sha256': sha(p.read_bytes())} for p in images]
              + ([{'role': 'mask', 'path': str(a.mask.resolve()), 'sha256': sha(a.mask.read_bytes())}] if a.mask else [])}
    if a.dry_run:
        record.update(dry_run=True, request_bytes=len(body), cost='none: no request sent')
        return record
    if a.out.exists() or a.out.with_suffix('.json').exists():
        raise ValueError('output or its record already exists; choose a new versioned name')
    budget = read_budget(a.budget_file)
    if budget['used'] >= budget['max']:
        raise BudgetError(f'budget exhausted ({budget["used"]}/{budget["max"]}); diagnose before asking the user for more')
    key = os.environ.get(KEY_ENV[a.provider])
    if not key:
        raise ValueError(f'{KEY_ENV[a.provider]} is not set in the environment secrets')
    budget['used'] += 1  # count the attempt before calling: a failed paid call still spends
    a.budget_file.write_text(json.dumps(budget, indent=2) + '\n')
    image = extract_image(a.provider, call(a.provider, url, body, ctype, key))
    with a.out.open('xb') as f:
        f.write(image)
    record.update(output={'path': str(a.out.resolve()), 'sha256': sha(image)},
                  created_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  budget={'used': budget['used'], 'max': budget['max']},
                  next='Open the image, run preview.py and the quality checks before any further call.')
    with a.out.with_suffix('.json').open('x') as f:
        json.dump(record, f, indent=2)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider', choices=sorted(KEY_ENV), required=True)
    p.add_argument('--model', default=os.environ.get('ART_IMAGE_MODEL'), help='or ART_IMAGE_MODEL; see adapter for current names')
    p.add_argument('--prompt'); p.add_argument('--prompt-file', type=Path)
    p.add_argument('--image', type=Path, action='append', help='reference/source image; repeatable')
    p.add_argument('--mask', type=Path, help='OpenAI edit mask: transparent pixels are editable')
    p.add_argument('--size', help='provider size string, e.g. 1024x1024 (OpenAI)')
    p.add_argument('--out', type=Path)
    p.add_argument('--budget-file', type=Path, help='JSON {"max": N, "used": 0} for this task')
    p.add_argument('--dry-run', action='store_true', help='build and describe the request; send nothing')
    a = p.parse_args()
    if not a.model:
        p.error('--model or ART_IMAGE_MODEL required')
    if not a.dry_run and (not a.out or not a.budget_file):
        p.error('--out and --budget-file are required unless --dry-run')
    try:
        print(json.dumps(run(a), indent=2))
        return 0
    except BudgetError as e:
        print(json.dumps({'error': str(e)}))
        return 3
    except (OSError, ValueError, urllib.error.URLError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
