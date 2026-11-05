"""Checks the intent of codex_rules.py: the Codex rule must let headless Blender run the kit's own
scripts outside the sandbox, and must not open a door for any other code (inline Python, other
scripts, a plain Python command). Needs Blender and the codex CLI; without them the test is skipped.
Usage: python3 test_codex_rules.py <codex_rules.py> <runtime folder of the Codex edition>"""
import subprocess
import sys
import tempfile
from pathlib import Path

script, runtime = Path(sys.argv[1]), Path(sys.argv[2])
with tempfile.TemporaryDirectory() as d:
    r = subprocess.run([sys.executable, str(script), '--skills-root', str(runtime), '--rules-dir', d],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    if r.returncode == 2 and 'Blender not found' in out:
        print('SKIP: Blender not found'); sys.exit(0)
    if 'codex CLI not found' in out:
        print('SKIP: codex CLI not found'); sys.exit(0)
    assert r.returncode == 0, out
    assert 'rule test passed' in out, 'kit commands must be allowed and other commands must not: ' + out
    assert not list(Path(d).iterdir()), 'preview mode must not write the rules file'
print('PASS: codex_rules intent checks')
