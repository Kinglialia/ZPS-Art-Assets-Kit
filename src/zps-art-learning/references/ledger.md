# Project ledger CLI

Python standard library on macOS/Linux. Locate `scripts/art_learn.py` under this skill. All commands require an explicit `--root` pointing to a project data folder outside installed skills. No automatic ingestion hook is enabled. Writes are serialized with flock; keep one shared filesystem capable of file locking. Do not store credentials or private unrelated artifacts.

```sh
python /absolute/skill/scripts/art_learn.py --root /project/.art-learning ingest --report /project/evidence/check.json --asset /project/work/asset.glb --skill zps-3d-artist --version {{VERSION}} --spec /project/task/spec.json
python /absolute/skill/scripts/art_learn.py --root /project/.art-learning judge --run <run-id> --check <check-id> --verdict fail --source human --who <reviewer> --correction 'The silhouette check missed a required protrusion'
python /absolute/skill/scripts/art_learn.py --root /project/.art-learning flag --verdict-id <verdict-id>
python /absolute/skill/scripts/art_learn.py --root /project/.art-learning review
python /absolute/skill/scripts/art_learn.py --root /project/.art-learning doctor
```

`ingest` accepts JSON with checks containing `id` or `check` and a supported status, including 3D common.write_result and the 2D image inspector. Give the artifact actually measured by that report. It checks a declared report artifact hash if present, snapshots the report and artifact, and optionally JSON spec. For multi-file assets, package the needed dependencies deliberately; the CLI snapshots only the supplied file. Missing declared hash is recorded as unbound identity, not silently verified.

`judge` requires an explicit pass/fail/skip, named reviewer and source. This CLI cannot authenticate a human; the caller is responsible for truthful attribution. Replacing a verdict requires `--supersedes <current-id>`. It never asks a blank-default approval question.

`flag` uses an existing non-skip verdict with a correction and copies the run's artifact snapshot into golden/. It creates a candidate lesson, not an executable test. `review` uses current verdicts and counts disagreements only for explicit human pass/fail paired with automatic pass/fail; warn/info/not_checked and skipped verdicts are not approval. Matching corrections are grouped exactly, not by semantic inference. Repeated assets do not increase independent-asset counts.

`doctor` verifies ledger relationships and snapshot hashes; optional lesson `enforced_by` records may contain {path, sha256}. It detects missing/changed enforcer files, but does not execute them or certify a repair. These bindings require a separate authorized implementation workflow. Orphan snapshots from an interrupted ingest are not lessons; do not automatically delete them.

Data: runs.jsonl, verdicts.jsonl, lessons.jsonl are append-only; snapshots/ and golden/ retain evidence. Reports are read-only views; no command lowers gates, modifies source/config, syncs cloud or schedules future runs. Review/doctor do not create a ledger. Exit 0 success, 1 doctor found integrity failures, 2 invalid input. Keep original data for audit and make any cleanup an explicit project operation.

Not implemented: statistical calibration, semantic lesson clustering, automatic enforcer generation and executable golden replay. Research notes are archived outside runtime as an unverified proposal, not adopted numerical policy.
