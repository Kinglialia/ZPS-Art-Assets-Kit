"""Checks the intent of svg_render.py: the PNG an agent reviews must be the PNG that ships (exact size,
transparent background, real colours), 1x/2x must match the SVG base size, rule breaks (live text,
filters) must be reported, evidence must never be overwritten, and the Chrome fallback must give
the same size when resvg is not the backend."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

SCRIPT = Path(sys.argv[1])
BUTTON = ('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="20" viewBox="0 0 40 20">'
          '<g id="btn_normal"><rect x="0" y="0" width="20" height="20" fill="#ff0000"/></g></svg>')
TEXTY = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 10"><text x="0" y="8">Play</text>'
         '<filter id="f"/></svg>')


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    btn = d / 'btn_normal.svg'; btn.write_text(BUTTON)
    texty = d / 'title.svg'; texty.write_text(TEXTY)

    code, out = run(btn, '--out-dir', d / 'png', '--scales', 1, 2)
    assert code == 0, out
    assert out['backend'] == 'resvg', 'resvg must be the default when installed'
    one, two = out['results']
    assert one['size'] == [40, 20] and two['size'] == [80, 40], '1x must equal the SVG px size; 2x doubles it'
    assert two['png'].endswith('btn_normal@2x.png')
    im = Image.open(one['png']).convert('RGBA')
    assert im.size == (40, 20), 'the file must have the size that is reported'
    assert im.getpixel((5, 5))[:3] == (255, 0, 0), 'colours must survive rendering'
    assert im.getpixel((35, 10))[3] == 0, 'background must stay transparent for UI assets'
    assert one['warnings'] == []

    code, out = run(texty, '--out-dir', d / 'png2')
    assert code == 0, out
    w = ' '.join(out['results'][0]['warnings'])
    assert '<text>' in w, 'live text inside SVG breaks the UI rule and must be reported'
    assert '<filter>' in w, 'filters may not survive Godot or Figma and must be reported'
    assert out['results'][0]['size'] == [30, 10], 'viewBox must give the size when width/height are missing'

    code, out = run(btn, '--out-dir', d / 'png', '--scales', 1)
    assert code == 2 and 'exists' in out['error'], 'must refuse to overwrite evidence'

    bad = d / 'bad.svg'; bad.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    code, out = run(bad, '--out-dir', d / 'png3')
    assert code == 2 and 'viewBox' in out['error'], 'an SVG without a size must stop, not guess'
    assert not (d / 'png3').exists(), 'nothing may be written when the tool refuses'

    code, out = run(btn, '--out-dir', d / 'chrome', '--backend', 'chrome')
    if code == 0:
        im = Image.open(out['results'][0]['png']).convert('RGBA')
        assert out['backend'] == 'chrome' and im.size == (40, 20), 'fallback must give the same size'
        assert im.getpixel((5, 5))[:3] == (255, 0, 0) and im.getpixel((35, 10))[3] == 0, 'fallback must keep colour and transparency'
        print('chrome fallback: checked')
    else:
        print('chrome fallback: not available here:', out.get('error'))

print('PASS: svg_render intent checks')
