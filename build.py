#!/usr/bin/env python3
"""Build the installable packages of ZPS Art Assets Kit from src/ for each edition.

Usage:
  python3 build.py --edition all            # codex and claude
  python3 build.py --edition codex --skip-tests

Output: dist/<package>-<edition>-v<version>/ and the same folder as .zip.
The build stops with exit 1 if a check fails. Edit src/, package/ or editions/, never dist/.
Standard library only; the script tests in tests/ need Pillow and resvg-py."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
SRC, PKG, ED = ROOT / 'src', ROOT / 'package', ROOT / 'editions'
PACKAGE = 'ZPS Art Assets Kit'
SLUG = 'ZPS-Art-Assets-Kit'
SUPPORT_ROOTS = ['.art-director-support', '.art-production-support']
TEXT = {'.md', '.json', '.yaml', '.yml', '.txt', '.py', '.sh', '.command', '.mjs', '.toml'}
IGNORE = shutil.ignore_patterns('.deps', '__pycache__', '*.pyc', '.DS_Store')
DESC_MAX = 300  # Codex shortens long descriptions when the skill list exceeds its budget


def skills():
    return sorted(p.name for p in SRC.iterdir() if (p / 'SKILL.md').is_file())


def rename_pattern(names):
    # Exact skill names only, so that zps-art-library (data) and longer names stay unchanged.
    alt = '|'.join(sorted(map(re.escape, names), key=len, reverse=True))
    return re.compile(rf'(?<![\w-])({alt})(?![\w-])')


def frontmatter(text):
    if not text.startswith('---\n'):
        raise ValueError('no frontmatter')
    block = text[4:text.index('\n---', 4)]
    out = {}
    for line in block.splitlines():
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if m and m.group(2):
            v = m.group(2)
            out[m.group(1)] = json.loads(v) if v.startswith('"') else v
        m = re.match(r'^\s+version:\s*(\S+)', line)
        if m:
            out['version'] = m.group(1)
    return out


def sha(p):
    b = p.read_bytes()
    return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}


def build(edition, version, run_tests):
    cfg = json.loads((ED / edition / 'edition.json').read_text())
    names = skills()
    suffix = cfg['skill_suffix']
    final = {n: n + suffix for n in names}
    stage = ROOT / 'dist' / f'{SLUG}-{edition}-v{version}'
    if stage.exists():
        shutil.rmtree(stage)
    rt = stage / 'runtime'
    shutil.copytree(SRC, rt, ignore=IGNORE)
    for n in names:
        if suffix:
            (rt / n).rename(rt / final[n])
    shutil.copy(ED / edition / 'adapter.md', rt / '.art-production-support/adapters/runtime.md')
    if cfg.get('openai_yaml'):
        for n in names:
            src = ED / edition / 'openai' / f'{n}.yaml'
            (rt / final[n] / 'agents').mkdir(exist_ok=True)
            shutil.copy(src, rt / final[n] / 'agents/openai.yaml')
    for item in PKG.iterdir():
        dst = stage / item.name
        shutil.copytree(item, dst, ignore=IGNORE) if item.is_dir() else shutil.copy(item, dst)
    shutil.copy(ED / edition / 'removed-files.txt', stage / 'installer/removed-files.txt')
    for d in ('resources', 'release-notes'):
        shutil.copytree(ROOT / d, stage / d, ignore=IGNORE)

    conflict = cfg['conflict_roots']
    values = {
        'PACKAGE': PACKAGE, 'VERSION': version, 'EDITION_TITLE': cfg['title'], 'APP': cfg['app_name'],
        'INSTALL_ROOT': cfg['install_root'], 'STATE_ROOT': cfg['state_root'], 'SKILL_COUNT': str(len(names)),
        'CONFLICT_ROOTS_TEXT': ', '.join(f'`{c}`' for c in conflict) if conflict else 'no other folders',
        'EDITION_INSTALL_NOTES': (ED / edition / 'install-notes.md').read_text().strip(),
        'EDITION_TOOLS_NOTES': (ED / edition / 'tools-notes.md').read_text().strip(),
    }
    pat = rename_pattern(names)
    for f in [p for p in rt.rglob('*') if p.is_file()] + [p for p in stage.glob('*.md')]:
        if f.suffix not in TEXT or 'resources' in f.parts:
            continue
        t = f.read_text()
        t2 = pat.sub(lambda m: final[m.group(1)], t) if suffix else t
        for k, v in values.items():
            t2 = t2.replace('{{' + k + '}}', v)
        if f.name == 'SKILL.md':
            t2 = re.sub(r'^(  version: ).*$', rf'\g<1>{version}', t2, count=1, flags=re.M)
            t2 = re.sub(r'^(# ZPS - .+)$', rf"\g<1>{cfg['display_suffix']}", t2, count=1, flags=re.M)
        if f.name == 'skill.yaml':
            t2 = re.sub(r'"version": "[^"]*"', f'"version": "{version}"', t2)
        if t2 != t:
            f.write_text(t2)

    aliases = {}
    legacy = json.loads((ED / 'legacy-aliases.json').read_text())
    for n in names:
        al = [a for a in legacy.get(n, []) if a not in final.values()]
        if cfg.get('aliases_include_codex_names'):
            al.append(n + '-codex')
        aliases[final[n]] = sorted(set(al) - set(final.values()))
    files = {p.relative_to(rt).as_posix(): sha(p) for p in sorted(rt.rglob('*')) if p.is_file()}
    manifest = {'package': PACKAGE, 'version': version, 'edition': edition, 'app_name': cfg['app_name'],
                'install_root': cfg['install_root'], 'conflict_roots': conflict, 'state_root': cfg['state_root'],
                'skills': [final[n] for n in names], 'support_roots': SUPPORT_ROOTS,
                'legacy_aliases': aliases, 'files': files}
    (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

    errors = check(stage, manifest, names, suffix)
    if run_tests and not errors:
        errors += tests(rt)
    pkg = {p.relative_to(stage).as_posix(): sha(p) for p in sorted(stage.rglob('*')) if p.is_file()}
    (stage / 'PACKAGE-MANIFEST.json').write_text(json.dumps({'package': f'{PACKAGE} v{version} ({edition})', 'files': pkg},
                                                            indent=2, ensure_ascii=False) + '\n')
    if errors:
        print(f'[{edition}] FAILED:\n  ' + '\n  '.join(errors))
        return False
    zpath = stage.parent / (stage.name + '.zip')
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob('*')):
            z.write(p, (Path(stage.name) / p.relative_to(stage)).as_posix())
    print(f'[{edition}] OK: {zpath.relative_to(ROOT)}')
    return True


def check(stage, manifest, names, suffix):
    errors, total = [], 0
    rt = stage / 'runtime'
    for s in manifest['skills']:
        try:
            fm = frontmatter((rt / s / 'SKILL.md').read_text())
        except ValueError as e:
            errors.append(f'{s}: {e}')
            continue
        d = fm.get('description', '')
        total += len(d)
        if fm.get('name') != s:
            errors.append(f'{s}: name is {fm.get("name")!r}')
        if not d or len(d) > DESC_MAX:
            errors.append(f'{s}: description has {len(d)} characters (max {DESC_MAX})')
    for f in list(rt.rglob('*.md')) + list(stage.glob('*.md')):
        text = f.read_text()
        if '{{' in text and '}}' in text and re.search(r'\{\{[A-Z_]+\}\}', text):
            errors.append(f'{f.relative_to(stage)}: unreplaced placeholder')
        for path in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', text):
            if not path.startswith(('http', 'mailto:')) and not (f.parent / path).exists():
                errors.append(f'{f.relative_to(stage)}: broken link {path}')
    other = re.compile(r'(?<![\w-])zps-[a-z0-9-]+-codex(?![\w-])')
    if not suffix:
        for f in rt.rglob('*'):
            if f.is_file() and f.suffix in TEXT and other.search(f.read_text()):
                errors.append(f'{f.relative_to(stage)}: Codex skill name in the Claude edition')
    print(f'[{manifest["edition"]}] {len(manifest["skills"])} skills, descriptions {total} characters')
    return errors


def tests(rt):
    scripts = rt / '.art-production-support/shared/scripts'
    errors = []
    for t, target in (('test_svg_render.py', 'svg_render.py'), ('test_anim_preview.py', 'anim_preview.py')):
        r = subprocess.run([sys.executable, str(ROOT / 'tests' / t), str(scripts / target)], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f'{t} failed: {(r.stdout + r.stderr).strip()[-400:]}')
    for p in rt.rglob('__pycache__'):
        shutil.rmtree(p)
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--edition', choices=['codex', 'claude', 'all'], default='all')
    ap.add_argument('--skip-tests', action='store_true')
    a = ap.parse_args()
    version = (ROOT / 'VERSION').read_text().strip()
    eds = ['codex', 'claude'] if a.edition == 'all' else [a.edition]
    ok = all([build(e, version, not a.skip_tests) for e in eds])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
