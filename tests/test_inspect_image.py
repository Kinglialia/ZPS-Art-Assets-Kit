"""Checks the intent of inspect_image.py --require-alpha: a generated image whose 'transparent'
background is a painted grey checkerboard must fail, because the engine would show the squares.
A real transparent file and a plain opaque image on a flat background must not be flagged.
Usage: python3 test_inspect_image.py <inspect_image.py>"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def run(img):
    r = subprocess.run([sys.executable, sys.argv[1], str(img), '--require-alpha'], capture_output=True, text=True)
    return {c['id']: c['status'] for c in json.loads(r.stdout)['checks']}


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    fake = Image.new('RGBA', (256, 256), (255, 255, 255, 255))
    dr = ImageDraw.Draw(fake)
    for y in range(0, 256, 16):
        for x in range(0, 256, 16):
            if (x // 16 + y // 16) % 2:
                dr.rectangle((x, y, x + 15, y + 15), fill=(204, 204, 204, 255))
    dr.ellipse((80, 80, 176, 176), fill=(200, 40, 40, 255))
    fake.save(d / 'fake.png')
    real = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    ImageDraw.Draw(real).ellipse((80, 80, 176, 176), fill=(200, 40, 40, 255))
    real.save(d / 'real.png')
    flat = Image.new('RGBA', (256, 256), (240, 240, 240, 255))
    ImageDraw.Draw(flat).ellipse((80, 80, 176, 176), fill=(200, 40, 40, 255))
    flat.save(d / 'flat.png')
    assert run(d / 'fake.png')['painted_checkerboard'] == 'fail', 'a painted checkerboard must fail'
    assert run(d / 'real.png')['painted_checkerboard'] == 'pass', 'real transparency must pass'
    assert run(d / 'flat.png')['painted_checkerboard'] == 'pass', 'a flat background is not a checkerboard'
print('PASS: inspect_image intent checks')
