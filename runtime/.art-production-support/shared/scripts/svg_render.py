"""Render SVG sources to transparent PNGs at 1x/2x so an agent can look at them and the PNGs can ship.
Backend: resvg (pip resvg-py), else headless Chrome if found. Also warns about SVG features that
break the UI rules: live text inside SVG, and filters/masks/scripts that Figma or Godot may not keep.
Refuses to overwrite. The PNG is evidence to open; it is not a quality verdict."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

CHROME_PATHS = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium']
RISKY = {'filter': 'filter effects may render differently in Godot or be lost in Figma',
         'mask': 'masks may render differently in Godot',
         'script': 'scripts are not allowed in UI SVG sources',
         'foreignObject': 'foreignObject is not supported by Godot or Figma'}


def local(tag):
    return tag.rsplit('}', 1)[-1]


def px(value):
    if value is None:
        return None
    m = re.fullmatch(r'\s*([0-9.]+)\s*(px)?\s*', value)
    return float(m.group(1)) if m else None


def inspect_svg(path):
    """Base size in px (1x) and rule warnings."""
    root = ET.parse(path).getroot()
    if local(root.tag) != 'svg':
        raise ValueError(f'{path}: root element is not <svg>')
    w, h = px(root.get('width')), px(root.get('height'))
    if w is None or h is None:
        vb = (root.get('viewBox') or '').replace(',', ' ').split()
        if len(vb) != 4:
            raise ValueError(f'{path}: needs width/height in px or a viewBox')
        w, h = float(vb[2]), float(vb[3])
    warnings = []
    tags = {local(e.tag) for e in root.iter()}
    if 'text' in tags or 'tspan' in tags:
        warnings.append('contains <text>: UI text must stay live in the engine; convert only logos or decorative titles to paths')
    for tag, why in RISKY.items():
        if tag in tags:
            warnings.append(f'contains <{tag}>: {why}')
    return round(w), round(h), warnings


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    for name in ('google-chrome', 'chromium', 'chromium-browser', 'chrome'):
        p = shutil.which(name)
        if p:
            return p
    return None


def pick_backend(choice):
    if choice in ('auto', 'resvg'):
        try:
            import resvg_py  # noqa: F401
            return 'resvg', None
        except ImportError:
            if choice == 'resvg':
                raise ImportError('resvg-py not installed: python3 -m pip install --user resvg-py==0.5.0')
    chrome = find_chrome()
    if chrome:
        return 'chrome', chrome
    raise ImportError('no SVG renderer: install resvg-py (python3 -m pip install --user resvg-py==0.5.0) or Google Chrome')


def render_resvg(svg, width, height):
    import resvg_py
    return bytes(resvg_py.svg_to_bytes(svg_path=str(svg), width=width, height=height))


def render_chrome(chrome, svg, width, height):
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / 'page.html'
        out = Path(d) / 'out.png'
        page.write_text('<!doctype html><html><body style="margin:0;background:transparent">'
                        f'<img src="{Path(svg).resolve().as_uri()}" width="{width}" height="{height}" '
                        'style="display:block"></body></html>')
        subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--default-background-color=00000000', f'--window-size={width},{height}',
                        f'--screenshot={out}', page.as_uri()],
                       check=True, capture_output=True, timeout=60)
        return out.read_bytes()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs', nargs='+', type=Path, help='SVG files, for example one per component state')
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--scales', nargs='+', type=int, default=[1], help='1 = SVG width/height in px; 2 writes <name>@2x.png')
    p.add_argument('--backend', choices=['auto', 'resvg', 'chrome'], default='auto')
    a = p.parse_args()
    try:
        if any(s < 1 for s in a.scales):
            raise ValueError('--scales must be positive integers')
        backend, chrome = pick_backend(a.backend)
        jobs = []
        for svg in a.inputs:
            w, h, warnings = inspect_svg(svg)
            for s in a.scales:
                out = a.out_dir / (f'{svg.stem}.png' if s == 1 else f'{svg.stem}@{s}x.png')
                jobs.append((svg, out, w * s, h * s, warnings))
        existing = [str(j[1]) for j in jobs if j[1].exists()]
        if existing:
            raise OSError(f'output exists: {existing}')
        a.out_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for svg, out, w, h, warnings in jobs:
            data = render_resvg(svg, w, h) if backend == 'resvg' else render_chrome(chrome, svg, w, h)
            with out.open('xb') as f:
                f.write(data)
            results.append({'svg': str(svg), 'png': str(out.resolve()), 'size': [w, h], 'warnings': warnings})
        print(json.dumps({'tool': 'art_svg_render', 'backend': backend, 'results': results,
                          'note': 'Godot rasterizes SVG with its own renderer (ThorVG); small differences in gradients '
                                  'and stroke width are possible. Ship these PNGs by default; record the risk if SVG is imported directly.',
                          'next': 'Open the PNGs at display size (preview.py sheet) and inspect them.'}))
        return 0
    except (ImportError, OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
