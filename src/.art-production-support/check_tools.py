"""Report which tools the ZPS art skills need on this machine, and how to install what is missing.
Standard library only. It installs nothing. Run the installed copy:
  python3 {{INSTALL_ROOT}}/.art-production-support/check_tools.py [--json]
Exit 0 when every required tool is present, 1 when something required is missing."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # the skills root that holds the zps-* folders
REQ = HERE / 'requirements.txt'
TOOLS3D = ROOT / 'zps-3d-artist' / 'tools'
BLENDER_MAC = '/Applications/Blender.app/Contents/MacOS/Blender'
CHROME_MAC = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
VENV_PKGS = ['numpy', 'trimesh', 'scipy', 'cv2', 'PIL', 'yaml', 'manifold3d', 'xatlas', 'kneed', 'skimage']


def item(group, name, need, ok, found, fix, used_by):
    return {'group': group, 'tool': name, 'need': need, 'ok': bool(ok), 'found': found, 'fix': fix, 'used_by': used_by}


def has_module(name):
    return importlib.util.find_spec(name) is not None


def find_blender():
    for p in (os.environ.get('BLENDER'), BLENDER_MAC, shutil.which('blender')):
        if p and os.path.exists(p):
            return p
    return None


def venv_check(py):
    code = 'import importlib.util as u,json;print(json.dumps([m for m in %r if u.find_spec(m) is None]))' % VENV_PKGS
    try:
        r = subprocess.run([str(py), '-c', code], capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout.strip() or '["(could not run venv python)"]')
    except (OSError, ValueError, subprocess.SubprocessError):
        return ['(could not run venv python)']


def npm_global(package):
    npm = shutil.which('npm')
    if not npm:
        return None
    try:
        root = subprocess.run([npm, 'root', '-g'], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    path = Path(root) / package
    return str(path) if root and path.is_dir() else None


def venv_imports(py, modules):
    code = 'import importlib\n' + ''.join(f'importlib.import_module({m!r})\n' for m in modules)
    try:
        return subprocess.run([str(py), '-c', code], capture_output=True, timeout=120).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def collect():
    out = []
    pip = f'{sys.executable} -m pip install --user -r "{REQ}"'
    v = sys.version_info
    out.append(item('core', 'Python >= 3.11', 'required', v >= (3, 11), sys.version.split()[0],
                    'Install Python 3.11+ from python.org (macOS system Python 3.9 is too old)', 'all scripts'))
    for mod, name, use in (('PIL', 'Pillow', 'preview, sprite, palette, image checks, anim_preview'),
                           ('numpy', 'numpy', 'score_variants, tone_match, structure_diff'),
                           ('resvg_py', 'resvg-py 0.5.0', 'svg_render (UI SVG to PNG)')):
        out.append(item('core', name, 'required', has_module(mod), sys.executable if has_module(mod) else None, pip, use))
    bl = find_blender()
    out.append(item('model', 'Blender', 'required for model work', bl, bl,
                    'macOS: brew install --cask blender (about 1 GB), or blender.org; or set BLENDER=/path/to/blender',
                    'inspect_model, render_model (texture planning, surface, texture review), all 3D tools'))
    venv = TOOLS3D / '.deps' / 'venv' / 'bin' / 'python'
    setup = f'bash "{TOOLS3D / "setup_deps.sh"}"  (needs Blender first)'
    if not TOOLS3D.exists():
        out.append(item('3d', '3D Artist skill', 'required for 3D', False, None,
                        'Install the skills first (INSTALL.command), then run this check from the installed copy', '3D'))
    else:
        missing = venv_check(venv) if venv.exists() else ['(no venv)']
        out.append(item('3d', '3D tools venv', 'required for 3D', not missing, str(venv) if venv.exists() else None,
                        setup + (f'; missing: {", ".join(missing)}' if missing else ''), '3D self-build, optimize, QA'))
        bdeps = sorted((TOOLS3D / '.deps').glob('blender-py*'))
        out.append(item('3d', 'Blender-side packages', 'required for 3D', bool(bdeps), str(bdeps[0]) if bdeps else None,
                        setup, 'Blender-side 3D scripts'))
    g = shutil.which('gltfpack')
    out.append(item('3d', 'gltfpack', 'recommended', g, g, 'brew install gltfpack, or npm i -g gltfpack',
                    '3D optimize sweep (falls back to Blender Decimate)'))
    gv = shutil.which('gltf_validator') or npm_global('gltf-validator')
    out.append(item('3d', 'glTF validator', 'optional', gv, gv,
                    'install Node.js, then npm i -g gltf-validator', '3D export_check'))
    ch = CHROME_MAC if os.path.exists(CHROME_MAC) else (shutil.which('google-chrome') or shutil.which('chromium'))
    out.append(item('core', 'Google Chrome', 'optional', ch, ch, 'only a fallback when resvg-py is missing',
                    'svg_render fallback'))
    rembg_ok = venv.exists() and venv_imports(venv, ['rembg', 'onnxruntime'])
    out.append(item('3d', 'rembg', 'optional', rembg_ok, str(venv) if rembg_ok else None,
                    f'"{venv}" -m pip install "rembg[cpu]" (large)', '3D validate_concept background removal'))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    rows = collect()
    required_missing = [r for r in rows if r['ok'] is False and r['need'].startswith('required')]
    if a.json:
        print(json.dumps({'tool': 'art_check_tools', 'skills_root': str(ROOT), 'python': sys.executable,
                          'ok': not required_missing, 'items': rows}, indent=2))
    else:
        print(f'Skills root: {ROOT}\nPython: {sys.executable}\n')
        for r in rows:
            mark = 'OK  ' if r['ok'] else ('--  ' if r['ok'] is None else 'MISS')
            print(f"[{mark}] {r['group']:5} {r['tool']:24} {r['need']}")
            if r['ok'] is False:
                print(f"         fix: {r['fix']}")
        print('\nAll required tools present.' if not required_missing else
              f'\n{len(required_missing)} required item(s) missing. Install them, then run this check again.')
    return 0 if not required_missing else 1


if __name__ == '__main__':
    sys.exit(main())
