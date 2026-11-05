"""Check a frame sequence for canvas consistency and pivot drift (alpha bounds per frame).
Input: frame files in order, or one sheet split by --grid COLS ROWS. Motion can legitimately move
the body; drift limits apply only when --max-baseline-shift / --max-center-shift are given."""
import argparse
import json
from pathlib import Path
import statistics
import sys

ALPHA_MIN = 16  # ignore near-invisible fringe pixels when measuring bounds


def frames_from(paths, grid=None):
    from PIL import Image
    if grid:
        with Image.open(paths[0]) as im:
            sheet = im.convert('RGBA')
        cols, rows = grid
        if sheet.width % cols or sheet.height % rows:
            raise ValueError(f'sheet {sheet.size} is not divisible by grid {cols}x{rows}')
        w, h = sheet.width // cols, sheet.height // rows
        return [(f'r{r}c{c}', sheet.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))) for r in range(rows) for c in range(cols)]
    out = []
    for p in paths:
        with Image.open(p) as im:
            out.append((Path(p).name, im.convert('RGBA')))
    return out


def check(frames, max_baseline=None, max_center=None):
    sizes = {im.size for _, im in frames}
    measured = []
    for name, im in frames:
        mask = im.getchannel('A').point(lambda v: 255 if v >= ALPHA_MIN else 0)
        box = mask.getbbox()
        measured.append({'frame': name, 'bbox': list(box) if box else None,
                         'baseline': box[3] if box else None,
                         'center_x': (box[0] + box[2]) / 2 if box else None})
    checks = [{'id': 'canvas_consistent', 'status': 'pass' if len(sizes) == 1 else 'fail', 'sizes': sorted(map(list, sizes))},
              {'id': 'no_empty_frames', 'status': 'pass' if all(m['bbox'] for m in measured) else 'fail'}]
    valid = [m for m in measured if m['bbox']]
    for key, limit, cid in (('baseline', max_baseline, 'baseline_shift'), ('center_x', max_center, 'center_shift')):
        values = [m[key] for m in valid]
        if not values:
            continue
        ref = statistics.median(values)
        shift = max(abs(v - ref) for v in values)
        entry = {'id': cid, 'max_shift_px': shift, 'median': ref}
        entry['status'] = 'info' if limit is None else ('pass' if shift <= limit else 'fail')
        checks.append(entry)
    return {'tool': 'art_sprite_check', 'frames': measured, 'checks': checks,
            'scope': 'Alpha bounds only. Does not judge pose, timing or volume; play the sequence to review motion.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs', nargs='+', type=Path)
    p.add_argument('--grid', nargs=2, type=int, metavar=('COLS', 'ROWS'))
    p.add_argument('--max-baseline-shift', type=float)
    p.add_argument('--max-center-shift', type=float)
    a = p.parse_args()
    try:
        r = check(frames_from(a.inputs, a.grid), a.max_baseline_shift, a.max_center_shift)
        print(json.dumps(r, indent=2))
        return 1 if any(c['status'] == 'fail' for c in r['checks']) else 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
