"""Checks the intent of gen_api.py: a paid Meshy or Tripo call must never happen by accident.
A dry run must show the exact request with the agreed settings (dense mesh, no texture) and must not
need a key or spend credits. A live call must stop before the network when the budget cannot pay it.
A key must never appear in any output.
Usage: python3 test_gen_api.py <gen_api.py>"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(sys.argv[1])
SECRET = 'sk-test-must-not-leak-1234'


def run(*args, env=None):
    e = {k: v for k, v in os.environ.items() if k not in ('MESHY_API_KEY', 'TRIPO_API_KEY')}
    e.update(env or {})
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=e)
    assert SECRET not in r.stdout + r.stderr, 'a key was printed'
    return r.returncode, json.loads(r.stdout)


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    png = d / 'front.png'
    png.write_bytes(b'\x89PNG\r\n\x1a\n' + b'0' * 32)
    back = d / 'back.png'
    back.write_bytes(png.read_bytes())
    glb = d / 'final.glb'
    glb.write_bytes(b'glTF' + b'0' * 32)
    keyfile = d / 'missing.env'
    base_env = {'ZPS_ART_ENV_FILE': str(keyfile)}

    # Dry runs: no key needed, agreed settings, nothing written.
    code, rec = run('generate', '--provider', 'meshy', '--view', f'front={png}', '--dry-run', env=base_env)
    assert code == 0 and rec['dry_run'], rec
    body = rec['steps'][0]['body']
    assert rec['steps'][0]['url'].endswith('/image-to-3d')
    assert body['ai_model'] == 'meshy-7.1' and body['should_texture'] is False and body['should_remesh'] is False, body
    assert body['save_pre_remeshed_model'] is True, 'the dense mesh is the sweep source'
    assert rec['expected_credits'] == 25

    code, rec = run('generate', '--provider', 'meshy', '--view', f'back={back}', '--view', f'front={png}', '--dry-run', env=base_env)
    urls = rec['steps'][0]['body']['image_urls']
    assert rec['steps'][0]['url'].endswith('/multi-image-to-3d')
    assert urls[0]['data_uri'] == str(png), 'Meshy reads the first image as the front view'

    code, rec = run('generate', '--provider', 'tripo', '--view', f'front={png}', '--view', f'back={back}', '--dry-run', env=base_env)
    body = rec['steps'][-1]['body']
    assert [s['method'] for s in rec['steps']] == ['UPLOAD', 'UPLOAD', 'POST']
    assert body['texture'] is False and body['pbr'] is False and body['geometry_quality'] == 'detailed', body
    assert rec['expected_credits'] == 40

    code, rec = run('remesh', '--provider', 'meshy', '--task-id', 't1', '--polycount', '1500', '--dry-run', env=base_env)
    assert rec['steps'][0]['body']['topology'] == 'triangle', 'static props use triangle remesh'
    assert rec['expected_credits'] == 5

    code, rec = run('texture', '--provider', 'meshy', '--model', glb, '--style-image', png, '--dry-run', env=base_env)
    assert rec['steps'][0]['body']['enable_original_uv'] is True, 'the retexture must keep the kit UVs'

    code, rec = run('remesh', '--provider', 'tripo', '--task-id', 't1', '--polycount', '1500', '--dry-run', env=base_env)
    assert code == 2, 'Tripo remesh is not offered: it costs more than a new generation'

    # Missing key: a clear error that names the key file, no credit spent.
    budget = d / 'budget.json'
    budget.write_text(json.dumps({'max_credits': 100, 'used_credits': 0}))
    code, rec = run('generate', '--provider', 'meshy', '--view', f'front={png}', '--out', d / 'o1', '--budget-file', budget, env=base_env)
    assert code == 2 and str(keyfile) in rec['error'], rec
    assert json.loads(budget.read_text())['used_credits'] == 0

    # Budget too small: stop before any network call (the fake key would fail at the network).
    keyfile.write_text(f'MESHY_API_KEY={SECRET}\n')
    budget.write_text(json.dumps({'max_credits': 20, 'used_credits': 0}))
    code, rec = run('generate', '--provider', 'meshy', '--view', f'front={png}', '--out', d / 'o2', '--budget-file', budget, env=base_env)
    assert code == 3 and 'budget' in rec['error'], rec
    assert json.loads(budget.read_text())['used_credits'] == 0
    assert not (d / 'o2').exists(), 'nothing is written when the budget stops the call'

    # Key status: says where the key comes from, never its value.
    code, rec = run('keys', env=base_env)
    assert rec['keys'] == {'meshy': 'key file', 'tripo': 'missing'}, rec
print('PASS: gen_api intent checks')
