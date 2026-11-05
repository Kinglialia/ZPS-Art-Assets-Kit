"""Checks the intent of anim_preview.py: an agent must be able to read motion order and path from
the onion skin, a person must get a playable GIF at the requested speed, and the tool must never
overwrite evidence or hide a canvas mismatch."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

SCRIPT = Path(sys.argv[1])
BG = (128, 128, 128)


def frame(x, size=(64, 64)):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((x, 24, x + 16, 40), fill=(255, 255, 255, 255))
    return im


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    xs = [4, 16, 28, 40]
    files = []
    for i, x in enumerate(xs):
        p = d / f'f{i}.png'; frame(x).save(p); files.append(p)

    code, out = run(*files, '--out', d / 'walk', '--height', 64, '--fps', 10, '--no-tint')
    assert code == 0, out
    assert out['frames'] == 4 and out['frame_ms'] == 100

    g = Image.open(out['out']['gif'])
    assert g.n_frames == 4, 'every frame must be playable'
    assert g.info['duration'] == 100, 'GIF must play at the requested fps'

    on = Image.open(out['out']['onion']).convert('RGB')
    first = on.getpixel((xs[0] + 8, 32))
    last = on.getpixel((xs[-1] + 8, 32))
    dist = lambda c: sum(abs(a - b) for a, b in zip(c, BG))
    assert dist(first) < dist(last), 'early frames must be fainter so the order of motion is readable'
    assert dist(first) > 0, 'early frames must still be visible'

    st = Image.open(out['out']['strip'])
    assert st.width > 4 * 64, 'strip must show every frame side by side'

    code, out2 = run(*files, '--out', d / 'walk')
    assert code == 2 and 'exists' in out2['error'], 'must refuse to overwrite evidence'

    sheet = Image.new('RGBA', (64 * 4, 64))
    for i, x in enumerate(xs):
        sheet.paste(frame(x), (64 * i, 0))
    sp = d / 'sheet.png'; sheet.save(sp)
    code, out3 = run(sp, '--grid', 4, 1, '--out', d / 'sheet', '--step', 2)
    assert code == 0 and out3['frames'] == 4, out3

    bad = d / 'big.png'; frame(4, (80, 64)).save(bad)
    code, out4 = run(files[0], bad, '--out', d / 'bad')
    assert code == 2 and 'canvas' in out4['error'], 'a canvas mismatch must stop the tool, not be hidden'
    assert not (d / 'bad_strip.png').exists(), 'nothing may be written when the tool refuses'

print('PASS: anim_preview intent checks')
