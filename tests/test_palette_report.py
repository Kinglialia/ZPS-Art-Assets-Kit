"""Checks the intent of palette_report.py: measure colors the way an artist reads them.
A small saturated accent must survive clustering (a red gem on a dark body must not average into
brown), colors must come with OKLCH numbers, and an uneven ramp must be flagged while an even one passes.
Usage: python3 test_palette_report.py <palette_report.py>"""
import importlib.util
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location('palette_report', sys.argv[1])
pr = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(sys.argv[1]).parent))
spec.loader.exec_module(pr)

with tempfile.TemporaryDirectory() as d:
    img = Path(d) / 'body.png'
    # A brown-grey gradient body: median-cut spends its clusters on the gradient. A 12 px red gem
    # (under 0.4% of the area) then averages into a brown cluster unless an accent pass keeps it.
    yy, xx = np.mgrid[0:200, 0:200]
    arr = np.zeros((200, 200, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = 30 + xx * 0.6, 25 + xx * 0.5, 20 + yy * 0.4, 255
    arr[150:162, 150:162] = [220, 20, 30, 255]
    Image.fromarray(arr).save(img)
    r = pr.report(img, n_colors=4)
    colors = [e['vivid'] for e in r['dominant']] + [e['vivid'] for e in r['accents']]
    reds = [c for c in colors if c['oklch'][1] > 0.15 and c['oklch'][2] is not None
            and (c['oklch'][2] < 45 or c['oklch'][2] > 330)]
    assert reds, f'the small red accent was lost: {colors}'
    assert all(len(c['oklch']) == 3 for c in colors), 'every color needs OKLCH numbers'

    pal = pr.report(img, n_colors=4, palette=[(60, 50, 40), (110, 90, 60), (140, 115, 70)])
    assert '#' in ''.join(pal['off_palette_accents']), 'an accent outside the palette must be reported'

even = pr.ramp([(20, 20, 20), (70, 70, 70), (125, 125, 125), (185, 185, 185), (245, 245, 245)])
bumpy = pr.ramp([(20, 20, 20), (30, 30, 30), (40, 40, 40), (200, 200, 200), (245, 245, 245)])
assert bumpy['status'] == 'uneven', bumpy
assert even['status'] == 'pass', f'a perceptually even grey ramp must pass: {even}'
print('PASS: palette_report intent checks')
