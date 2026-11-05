"""Validate required technical checks and evidence identities, never artistic approval."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_gate(spec, report, base):
    required = spec.get('required', [])
    if not isinstance(required, list) or not required or not all(isinstance(k, str) and k for k in required) or len(required) != len(set(required)):
        raise ValueError('required must be a nonempty list of unique IDs')
    allowed_na = set(spec.get('allow_not_applicable', []))
    if not allowed_na.issubset(required):
        raise ValueError('N/A exemptions must refer to required IDs')
    expected = spec.get('artifact_sha256')
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError('spec must bind an artifact SHA256')
    artifact = report.get('artifact', {})
    path = base / artifact.get('path', '')
    errors = []
    if not path.is_file() or digest(path) != expected or artifact.get('sha256') != expected:
        errors.append('artifact missing, changed, or not the expected version')
    for source in report.get('inputs', []):
        source_path = base / source.get('path', '')
        if not source_path.is_file() or digest(source_path) != source.get('sha256'):
            errors.append('input missing or changed: ' + str(source.get('role', source.get('path'))))
    checks = {}
    for c in report.get('checks', []):
        if not isinstance(c.get('id'), str) or c['id'] in checks:
            raise ValueError('missing/duplicate check ID')
        if c.get('status') not in ('pass', 'fail', 'not_checked', 'not_applicable'):
            raise ValueError('unknown check status')
        checks[c['id']] = c
    for key in required:
        c = checks.get(key)
        if c is None:
            errors.append(key + ': missing')
            continue
        if c['status'] == 'not_applicable':
            if key not in allowed_na or not str(c.get('reason', '')).strip():
                errors.append(key + ': N/A not justified and explicitly exempted')
            continue
        if c['status'] != 'pass':
            errors.append(key + ': ' + c['status'])
            continue
        ev = c.get('evidence', {})
        ep = base / ev.get('path', '')
        if not ep.is_file() or digest(ep) != ev.get('sha256'):
            errors.append(key + ': evidence missing or changed')
    return {'required_checks_pass': not errors, 'errors': errors,
            'scope': 'Evidence integrity and declared required statuses only; not art approval',
            'other_checks': [c for k, c in checks.items() if k not in required]}


def load_measurement(path):
    """Use a saved inspector report as evidence; not a signature or proof of art quality."""
    raw = path.read_bytes()
    report = json.loads(raw)
    if report.get('tool') != 'art_image_inspector' or report.get('schema_version') != 1:
        raise ValueError('unsupported measurement report; use --report for a curated gate report')
    evidence = {'path': str(path.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()}
    for check in report.get('checks', []):
        check['evidence'] = evidence
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', type=Path, required=True)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--report', type=Path, help='Curated report with per-check evidence')
    source.add_argument('--measurement', type=Path, help='Saved inspect_image report, no manual wrapping')
    a = p.parse_args()
    try:
        path = a.report or a.measurement
        report = load_measurement(path) if a.measurement else json.loads(path.read_text())
        result = inspect_gate(json.loads(a.spec.read_text()), report, path.resolve().parent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['required_checks_pass'] else 1
    except (OSError, ValueError, TypeError, KeyError) as e:
        print(json.dumps({'error': str(e), 'required_checks_pass': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
