"""Checks the intent of the installer's key file: install creates it once with empty keys and mode 600,
never overwrites a key that the user pasted, and never copies it into backups or the receipt.
Usage: python3 test_key_file.py <package folder>"""
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = Path(sys.argv[1])

with tempfile.TemporaryDirectory() as d:
    d = Path(d).resolve()  # /var is a symlink on macOS; the installer refuses symlinked paths
    env = dict(os.environ, HOME=str(d), CODEX_HOME=str(d / '.codex'), ZPS_ART_ENV_FILE=str(d / 'cfg' / '.env'))
    args = [sys.executable, str(PKG / 'installer' / 'install.py'), '--install',
            '--target-root', str(d / 'skills'), '--state-root', str(d / 'state')]
    r = subprocess.run(args, input='INSTALL\n', capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    key = d / 'cfg' / '.env'
    assert key.is_file(), 'install must create the key file'
    assert stat.S_IMODE(key.stat().st_mode) == 0o600, 'only the user may read the keys'
    assert 'MESHY_API_KEY=\n' in key.read_text() and 'TRIPO_API_KEY=\n' in key.read_text()
    key.write_text('MESHY_API_KEY=pasted-by-user\n')
    r = subprocess.run(args, input='INSTALL\n', capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert key.read_text() == 'MESHY_API_KEY=pasted-by-user\n', 'a second install must keep the pasted key'
    leaked = [p for p in list((d / 'state').rglob('*')) + list((d / 'skills').rglob('*'))
              if p.is_file() and b'pasted-by-user' in p.read_bytes()]
    assert not leaked, f'key copied into {leaked}'
print('PASS: installer key file intent checks')
