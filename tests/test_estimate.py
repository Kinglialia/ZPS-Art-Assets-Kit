"""Checks the intent of estimate.py: estimates must improve from real project records, but a
method with too few records must keep the defaults, and records must stay in the project folder.
Usage: python3 test_estimate.py <estimate.py>"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(sys.argv[1])


def run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


with tempfile.TemporaryDirectory() as d:
    default = run('show', '--project', d, '--json')
    assert set(default) == {'self', 'meshy', 'tripo', 'zps3d'}, 'the router shows all four methods'
    assert all(r['source'] == 'default' for r in default.values())
    for m in (20, 25, 40):
        run('log', '--project', d, '--method', 'meshy', '--minutes', m, '--credits', 40)
    run('log', '--project', d, '--method', 'tripo', '--minutes', 99)
    log = Path(d) / '.zps-art' / 'estimates.jsonl'
    assert log.is_file() and len(log.read_text().splitlines()) == 4, 'records go to the project folder'
    rows = run('show', '--project', d, '--json')
    assert rows['meshy']['source'] == 'project median' and rows['meshy']['minutes'] == [20, 25, 40], rows['meshy']
    assert rows['tripo']['source'] == 'default', 'one record is noise and must not replace the default'
print('PASS: estimate intent checks')
