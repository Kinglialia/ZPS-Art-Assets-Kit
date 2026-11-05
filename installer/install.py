#!/usr/bin/env python3
"""Local, stdlib-only installer. No network, sudo, or configuration edits."""
import argparse, datetime, difflib, hashlib, json, os, pathlib, sys, tempfile, uuid
P = pathlib.Path
PACKAGE = P(__file__).resolve().parents[1]
RECEIPT = '.art-director-support/installed-manifest.json'
def digest(data): return hashlib.sha256(data).hexdigest()
def safe(path):
    path = P(os.path.abspath(str(path)))
    for part in (path, *path.parents):
        if part.is_symlink(): raise ValueError('Symlink is not supported: ' + str(part))
    return path
def relative(name):
    p = P(name)
    if p.is_absolute() or '..' in p.parts or not p.parts or str(p) != name:
        raise ValueError('Unsafe relative path: ' + name)
    return p
def read(path):
    safe(path)
    if path.exists() and not path.is_file(): raise ValueError('Not a regular file: ' + str(path))
    return path.read_bytes() if path.exists() else None
def write(path, data):
    safe(path)
    if data is None:
        if path.exists(): path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.ad-install-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as out: out.write(data)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def serialized(obj): return (json.dumps(obj, indent=2, ensure_ascii=False)+'\n').encode()
def payload():
    m = json.loads((PACKAGE/'manifest.json').read_text())
    data = {}
    for name, entry in m['files'].items():
        p = relative(name)
        if p.parts[0] not in m['skills'] + m.get('support_roots', ['.art-director-support']): raise ValueError('Unexpected payload root')
        b = read(PACKAGE/'runtime'/p)
        if b is None or digest(b) != entry['sha256'] or len(b) != entry['bytes']: raise ValueError('Payload corrupt: '+name)
        data[name] = b
    actual = set()
    for p in (PACKAGE/'runtime').rglob('*'):
        safe(p)
        if p.is_file(): actual.add(p.relative_to(PACKAGE/'runtime').as_posix())
    if actual != set(data): raise ValueError('Unlisted runtime files')
    if {n.split('/')[0] for n in data if n.endswith('/SKILL.md')} != set(m['skills']): raise ValueError('Skill list mismatch')
    return m, data
def check_conflicts(root, manifest):
    legacy = P(os.environ.get('CODEX_HOME', str(P.home()/'.codex'))).expanduser()/'skills'
    roots = {P(os.path.abspath(str(p))) for p in (root, P.home()/'.agents/skills', legacy)}
    aliases = {alias for names in manifest['legacy_aliases'].values() for alias in names}
    for name in aliases:
        if len(relative(name).parts) != 1: raise ValueError('Invalid legacy alias')
    conflicts = []
    for location in sorted(roots):
        names = aliases | (set(manifest['skills']) if location != root else set())
        for name in sorted(names):
            candidate = location/name
            if candidate.exists() or candidate.is_symlink(): conflicts.append(str(candidate))
    if conflicts:
        raise ValueError('Conflicting skill folders; nothing installed. Archive the listed folders outside all skills roots, then retry. See INSTALL.md migration instructions:\n'+'\n'.join(conflicts))

def confirm(word):
    return input('Type '+word+' to continue, or Enter to cancel: ').strip() == word
def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--verify', action='store_true')
    mode.add_argument('--rollback', type=P)
    ap.add_argument('--target-root', type=P, default=P.home()/'.agents/skills')
    ap.add_argument('--state-root', type=P, default=P.home()/'.local/share/art-director-codex/backups')
    a = ap.parse_args()
    root = safe(a.target_root.expanduser())
    m, data = payload()
    print('Target:', root)
    if a.rollback:
        backup = safe(a.rollback.expanduser())
        tx = json.loads((backup/'transaction.json').read_text())
        if str(root) != tx['target']: raise ValueError('Backup belongs to a different target')
        restore = {}
        for name, info in tx['files'].items():
            relative(name)
            if name not in data and name != RECEIPT: raise ValueError('Unexpected rollback path')
            current = read(root/name)
            if current is None or digest(current) != info['after']: raise ValueError('File changed after installation; refusing rollback: '+name)
            old = read(backup/'files'/name) if info['before'] is not None else None
            if info['before'] is not None and (old is None or digest(old) != info['before']): raise ValueError('Backup corrupt: '+name)
            restore[name] = old
        print('Restore/remove', len(restore), 'managed files; keep unrelated files.')
        if not confirm('ROLLBACK'): return
        for name, b in restore.items(): write(root/name, b)
        print('Rollback complete. Empty directories may remain. Start a new Codex session.')
        return
    check_conflicts(root, m)
    if a.verify:
        for name, b in data.items():
            if read(root/name) != b: raise ValueError('Missing or changed installed file: '+name)
        receipt = read(root/RECEIPT)
        if receipt is None or json.loads(receipt)['files'] != m['files']: raise ValueError('Missing or inconsistent installation receipt')
        print(f"PASS: all {len(m['skills'])} skills match the package. Check discovery in a NEW local Codex session.")
        return
    before = {n: read(root/n) for n in data}
    changes = {n:b for n,b in data.items() if before[n] != b}
    for n,b in changes.items():
        print(('CREATE ' if before[n] is None else 'UPDATE ')+n)
        if before[n] is not None:
            print(''.join(difflib.unified_diff(before[n].decode('utf-8',errors='replace').splitlines(True), b.decode().splitlines(True), fromfile='installed/'+n, tofile='package/'+n)))
    old_receipt = read(root/RECEIPT)
    if not changes and old_receipt is not None and json.loads(old_receipt).get('files') == m['files']:
        print('Already installed; no changes.'); return
    print('Other skills and project settings are preserved. A timestamped backup will be created.')
    if not a.install:
        print('Preview only. Run with --install to apply.'); return
    if not confirm('INSTALL'):
        print('Cancelled; no files written.'); return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    backup = safe(a.state_root.expanduser())/stamp
    receipt = dict(m, installed_at=stamp, target=str(root), backup=str(backup))
    changes[RECEIPT] = serialized(receipt)
    before[RECEIPT] = old_receipt
    for n in changes:
        if read(root/n) != before[n]: raise ValueError('Concurrent file change: '+n)
    backup.mkdir(parents=True, exist_ok=False)
    tx = {'target':str(root), 'files':{n:{'before':digest(before[n]) if before[n] is not None else None,'after':digest(b)} for n,b in changes.items()}}
    for n in changes:
        if before[n] is not None: write(backup/'files'/n,before[n])
    write(backup/'transaction.json',serialized(tx))
    done = []
    try:
        for n,b in changes.items():
            if read(root/n) != before[n]: raise ValueError('Concurrent file change: '+n)
            write(root/n,b); done.append(n)
    except BaseException:
        for n in reversed(done): write(root/n,before[n])
        raise
    print(f"Installed {len(m['skills'])} skills. Backup:", backup)
    print('Run VERIFY.command, then start a NEW Codex session on this Mac.')
    print('Then install the tools the skills need: see TOOLS.md, and run: python3 "%s"' % (root/'.art-production-support'/'check_tools.py'))
if __name__ == '__main__':
    try: main()
    except (Exception, KeyboardInterrupt) as e:
        print('STOP:', str(e), file=sys.stderr); sys.exit(1)
