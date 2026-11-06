"""Checks the intent of preview.py: a small preview must look like the asset on screen.
Thin bright strokes must keep their brightness when scaled down (linear-light resize), and the
color of transparent pixels must not bleed into the edge as a dark halo (premultiplied alpha).
Usage: python3 test_preview.py <preview.py>"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location('preview', sys.argv[1])
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)

# 1 px white lines every 2 px on black: half the light. At 1/4 size the screen shows a mid tone
# whose linear value is 0.5, which is about 188 in sRGB. A gamma-space resize gives about 128.
lines = Image.new('RGBA', (64, 64), (0, 0, 0, 255))
for x in range(0, 64, 2):
    for y in range(64):
        lines.putpixel((x, y), (255, 255, 255, 255))
small = preview.fit(lines, 16)
mean = float(np.asarray(small)[..., 0].mean())
assert 175 <= mean <= 200, f'thin bright strokes lost light when scaled: mean {mean:.0f}, expected about 188'

# White square on fully transparent BLACK pixels: edge pixels may lose alpha, never turn gray.
sq = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
for x in range(16, 48):
    for y in range(16, 48):
        sq.putpixel((x, y), (255, 255, 255, 255))
s2 = preview.fit(sq, 13)  # odd size: edges fall between pixels
arr = np.asarray(s2)
edge = arr[(arr[..., 3] > 20) & (arr[..., 3] < 235)]
assert len(edge), 'the test needs partially transparent edge pixels'
assert edge[:, :3].min() >= 245, 'dark halo: transparent black bled into the edge'

px = preview.fit(lines, 16, nearest=True)
assert set(np.unique(np.asarray(px)[..., 0])) <= {0, 255}, 'pixel-art mode must not blend colors'
print('PASS: preview intent checks')
