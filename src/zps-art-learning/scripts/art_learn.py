#!/usr/bin/env python3
"""Project-local evidence ledger. No network, background hooks, threshold edits or implicit approvals."""
import argparse, collections, datetime, fcntl, hashlib, json, pathlib, sys, uuid
P = pathlib.Path

def sha(data): return hashlib.sha256(data).hexdigest()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def uid(prefix): return prefix + '-' + uuid.uuid4().hex

def read_rows(root, name):
    p = root / (name + '.jsonl')
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()] if p.exists() else []

def append(root, name, row):
    with (root / (name + '.jsonl')).open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n'); f.flush()
        import os
        os.fsync(f.fileno())

def lookup(rows, key):
    matches = [r for r in rows if r['id'] == key]
    if len(matches) != 1: raise ValueError('Unknown or duplicate ID: ' + key)
    return matches[0]

def checks(report):
    if not isinstance(report, dict) or not isinstance(report.get('checks'), list):
        raise ValueError('Report must be an object with a checks array')
    out = []
    for c in report['checks']:
        if not isinstance(c, dict): raise ValueError('Each check must be an object')
        key = c.get('id') or c.get('check')
        status = c.get('status')
        if not isinstance(key, str) or not key: raise ValueError('Missing check ID')
        if status not in ['pass', 'fail', 'warn', 'info', 'not_checked', 'skipped', 'error', 'not_applicable']:
            raise ValueError('Unsupported status: ' + str(status))
        out.append(dict(c, id=key, status=status))
    if len({c['id'] for c in out}) != len(out): raise ValueError('Duplicate check IDs')
    if not out: raise ValueError('Report needs a nonempty checks array')
    return out

def effective(verdicts):
    replaced = {v['supersedes'] for v in verdicts if v.get('supersedes')}
    return [v for v in verdicts if v['id'] not in replaced]

def load_snapshot(root, relative, expected):
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()): raise ValueError('Snapshot escapes ledger root')
    data = p.read_bytes()
    if sha(data) != expected: raise ValueError('Changed evidence: ' + str(p))
    return data

def execute(a):
    root = a.root.resolve()
    runs = read_rows(root, 'runs'); verdicts = read_rows(root, 'verdicts'); lessons = read_rows(root, 'lessons')
    if a.command == 'ingest':
        if not a.skill.strip() or not a.version.strip(): raise ValueError('Skill and version must not be blank')
        raw = a.report.read_bytes(); report = json.loads(raw); normalized = checks(report)
        if not isinstance(report.get('artifact', {}), dict): raise ValueError('artifact must be an object')
        asset_data = a.asset.read_bytes(); asset_hash = sha(asset_data)
        # When a report declares the measured artifact identity, reject a mismatch.
        declared = report.get('artifact', {}).get('sha256') or report.get('source_sha256')
        if declared and declared != asset_hash: raise ValueError('Report artifact hash does not match --asset')
        run = dict(id=uid('run'), skill=a.skill, skill_version=a.version, created=stamp(),
                   asset_path=str(a.asset.resolve()), asset_sha256=asset_hash,
                   report_sha256=sha(raw), checks=normalized, producer=report.get('tool', 'unknown'),
                   metrics=report.get('metrics', {}), warnings=report.get('warnings', []),
                   identity_declared=bool(declared))
        folder = root / 'snapshots' / run['id']; folder.mkdir(parents=True)
        (folder/'report.json').write_bytes(raw); (folder/'asset.bin').write_bytes(asset_data)
        run['report_snapshot'] = str((folder/'report.json').relative_to(root))
        run['asset_snapshot'] = str((folder/'asset.bin').relative_to(root))
        if a.spec:
            spec_data=a.spec.read_bytes();json.loads(spec_data)
            (folder/'spec.json').write_bytes(spec_data)
            run.update(spec_snapshot=str((folder/'spec.json').relative_to(root)),spec_sha256=sha(spec_data))
        append(root, 'runs', run); return run
    if a.command == 'judge':
        run=lookup(runs,a.run); lookup_check=[c for c in run['checks'] if c['id']==a.check]
        if not lookup_check: raise ValueError('Unknown check in run')
        if not a.who.strip(): raise ValueError('Reviewer identity must not be blank')
        previous=[v for v in effective(verdicts) if v['run']==a.run and v['check']==a.check]
        if previous and a.supersedes != previous[0]['id']: raise ValueError('Use --supersedes with the current verdict ID')
        if a.supersedes and (not previous or a.supersedes != previous[0]['id']): raise ValueError('Invalid superseded verdict')
        row=dict(id=uid('verdict'),run=a.run,check=a.check,auto=lookup_check[0]['status'],
                 verdict=a.verdict,source=a.source,who=a.who,correction=a.correction,
                 supersedes=a.supersedes,created=stamp())
        append(root,'verdicts',row);return row
    if a.command == 'flag':
        verdict=lookup(effective(verdicts),a.verdict_id);run=lookup(runs,verdict['run'])
        if verdict['verdict']=='skip' or not verdict['correction'].strip():
            raise ValueError('A lesson needs a non-skip verdict and an explicit correction')
        if any(l['verdict']==verdict['id'] for l in lessons): raise ValueError('Verdict already recorded as a lesson')
        raw=load_snapshot(root,run['asset_snapshot'],run['asset_sha256'])
        lesson=dict(id=uid('lesson'),run=run['id'],skill=run['skill'],trigger=verdict['check'],
                    correction=verdict['correction'],verdict=verdict['id'],status='candidate',
                    created=stamp(),asset_sha256=run['asset_sha256'],enforced_by=None)
        folder=root/'golden'/lesson['id'];folder.mkdir(parents=True)
        (folder/'asset.bin').write_bytes(raw);lesson['fixture']=str((folder/'asset.bin').relative_to(root))
        append(root,'lessons',lesson);return lesson
    if a.command == 'review':
        current=effective(verdicts);human=[v for v in current if v['source']=='human']
        paired=[v for v in human if v['auto'] in ['pass','fail'] and v['verdict'] in ['pass','fail']]
        matrix=collections.Counter(v['auto']+'->'+v['verdict'] for v in paired)
        eligible={v['id'] for v in current};groups=collections.defaultdict(list)
        for lesson in lessons:
            if lesson['verdict'] in eligible:groups[(lesson['skill'],lesson['trigger'],lesson['correction'].strip())].append(lesson)
        proposals=[]
        for (skill,trigger,correction), group in groups.items():
            assets={l['asset_sha256'] for l in group}
            proposals.append(dict(skill=skill,trigger=trigger,correction=correction,
                                  distinct_assets=len(assets),evidence=[l['id'] for l in group],
                                  recommendation='investigate repeated correction' if len(assets)>1 else 'retain candidate; more evidence needed'))
        return dict(runs=len(runs),explicit_human_verdicts=len(human),binary_pairs=len(paired),
                    matrix=dict(matrix),disagreements=sum(v['auto']!=v['verdict'] for v in paired),
                    skipped=sum(v['verdict']=='skip' for v in human),proposals=proposals,
                    limitations=['Unreviewed checks are not human passes.', 'No threshold calibration or statistical validity is claimed.',
                                 'Repeated copies of one asset do not count as independent assets.',
                                 'Proposals do not edit checks, configuration or skills.'])
    if a.command == 'doctor':
        errors=[]
        for label,rows in [('runs',runs),('verdicts',verdicts),('lessons',lessons)]:
            if len({r['id'] for r in rows})!=len(rows):errors.append('Duplicate IDs in '+label)
        for run in runs:
            for kind in ['report','asset','spec']:
                if kind+'_snapshot' in run:
                    try:load_snapshot(root,run[kind+'_snapshot'],run[kind+'_sha256'])
                    except (ValueError,OSError) as e:errors.append(str(e))
        for v in verdicts:
            try:
                r=lookup(runs,v['run'])
                if v['check'] not in {c['id'] for c in r['checks']}:raise ValueError('Unknown check for verdict '+v['id'])
                if v.get('supersedes'):
                    old=lookup(verdicts,v['supersedes'])
                    if old['run']!=v['run'] or old['check']!=v['check']:raise ValueError('Invalid supersession '+v['id'])
            except ValueError as e:errors.append(str(e))
        for lesson in lessons:
            try:
                lookup(runs,lesson['run']);lookup(verdicts,lesson['verdict'])
                load_snapshot(root,lesson['fixture'],lesson['asset_sha256'])
                if lesson.get('enforced_by'):
                    enforcer=lesson['enforced_by']
                    path=P(enforcer['path'])
                    if not path.is_absolute():path=root/path
                    if not path.is_file() or sha(path.read_bytes())!=enforcer['sha256']:raise ValueError('Enforcer missing/changed: '+str(path))
            except (ValueError,OSError,KeyError,TypeError) as e:errors.append(str(e))
        return dict(status='fail' if errors else 'pass',errors=errors,runs=len(runs),lessons=len(lessons),
                    limitation='Integrity check only; no artistic validation or executable fixture replay.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=P,required=True,help='Project ledger directory; never an installed skill directory')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('ingest');a.add_argument('--report',type=P,required=True);a.add_argument('--asset',type=P,required=True)
    a.add_argument('--skill',required=True);a.add_argument('--version',required=True);a.add_argument('--spec',type=P)
    a=sub.add_parser('judge');a.add_argument('--run',required=True);a.add_argument('--check',required=True)
    a.add_argument('--verdict',choices=['pass','fail','skip'],required=True);a.add_argument('--source',choices=['human','deterministic'],required=True)
    a.add_argument('--who',required=True);a.add_argument('--correction',default='');a.add_argument('--supersedes')
    a=sub.add_parser('flag');a.add_argument('--verdict-id',required=True)
    sub.add_parser('review');sub.add_parser('doctor');a=p.parse_args()
    try:
        if a.command in ['review','doctor']:
            # Read-only commands do not create a ledger or lock file.
            if a.root.exists():
                with (a.root/'.lock').open('r') as lock:
                    fcntl.flock(lock,fcntl.LOCK_SH);result=execute(a)
            else:result=execute(a)
        else:
            a.root.mkdir(parents=True,exist_ok=True)
            with (a.root/'.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX);result=execute(a)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result.get('status')=='fail' else 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
