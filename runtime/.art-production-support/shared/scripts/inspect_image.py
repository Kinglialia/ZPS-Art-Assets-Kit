"""Read-only image contract checks. No aesthetic, PBR or perspective score."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys


def inspect(path, size=None, require_alpha=False, reference=None, lock_mask=None):
    from PIL import Image, ImageChops
    raw = path.read_bytes()
    checks = []
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        original_mode = im.mode
        has_alpha = 'A' in im.getbands() or 'transparency' in im.info
        metadata = {'size': list(im.size), 'mode': original_mode,
                    'has_alpha_channel': has_alpha, 'icc_profile_present': bool(im.info.get('icc_profile'))}
        image = im.convert('RGBA')
    alpha = image.getchannel('A')
    metadata['alpha_extrema'] = list(alpha.getextrema())
    checks.append({'id': 'decode', 'status': 'pass'})
    if size is not None:
        checks.append({'id': 'dimensions', 'status': 'pass' if tuple(size) == image.size else 'fail',
                       'expected': list(size), 'actual': list(image.size)})
    if require_alpha:
        checks.append({'id': 'alpha_channel', 'status': 'pass' if has_alpha else 'fail'})
    if bool(reference) != bool(lock_mask):
        raise ValueError('reference and lock-mask must be supplied together')
    inputs = []
    if reference:
        reference_bytes = reference.read_bytes()
        mask_bytes = lock_mask.read_bytes()
        inputs = [{'role': role, 'path': str(p.resolve()), 'sha256': hashlib.sha256(b).hexdigest()}
                  for role, p, b in [('reference', reference, reference_bytes), ('lock_mask', lock_mask, mask_bytes)]]
        with Image.open(io.BytesIO(reference_bytes)) as im:
            old = im.convert('RGBA')
        with Image.open(io.BytesIO(mask_bytes)) as im:
            mask = im.convert('L')
        if old.size != image.size or mask.size != image.size:
            raise ValueError('locked-region comparison requires identical dimensions; no implicit resize')
        if mask.getextrema()[1] == 0:
            raise ValueError('lock mask is empty; no locked pixels were tested')
        channels = ImageChops.difference(old, image).split()
        maximum = channels[0]
        for channel in channels[1:]:
            maximum = ImageChops.lighter(maximum, channel)
        locked = mask.point(lambda v: 255 if v else 0)
        changed = ImageChops.multiply(maximum, locked)
        count = sum(changed.histogram()[1:])
        checks.append({'id': 'locked_pixels', 'status': 'pass' if count == 0 else 'fail',
                       'changed_pixels': count, 'max_channel_delta': changed.getextrema()[1],
                       'definition': 'Exact stored RGBA comparison at nonzero mask pixels; no color conversion'})
    return {'tool': 'art_image_inspector', 'schema_version': 1,
            'artifact': {'path': str(path.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()},
            'inputs': inputs,
            'metadata': metadata, 'checks': checks,
            'scope': 'File contract only. Alpha presence does not prove clean edges or correct blending.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--size', nargs=2, type=int)
    p.add_argument('--require-alpha', action='store_true')
    p.add_argument('--reference', type=Path)
    p.add_argument('--lock-mask', type=Path)
    p.add_argument('--out', type=Path, help='Save a new measurement report; refuses overwrite')
    a = p.parse_args()
    try:
        result = inspect(a.image, a.size, a.require_alpha, a.reference, a.lock_mask)
        if a.out:
            with a.out.open('x') as f:
                json.dump(result, f, indent=2)
                f.write('\n')
        print(json.dumps(result, indent=2))
        return 1 if any(c['status'] == 'fail' for c in result['checks']) else 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Pillow required; install only within authorized environment setup.'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
