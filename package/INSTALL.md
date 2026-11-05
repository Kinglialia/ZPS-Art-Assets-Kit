# {{PACKAGE}} v{{VERSION}} — {{EDITION_TITLE}} edition

This package holds {{SKILL_COUNT}} art skills for {{APP}}: concept, 2D assets and UI, textures, static 3D props, review, reference library and project learning. Shared rules, scripts and templates are stored once in `.art-production-support`. A skill loads only its own SKILL.md and the references it needs. See [CAPABILITIES.md](CAPABILITIES.md).

## Preview and install

Requires Python 3.11 or newer. Extract the ZIP to a stable folder. From that folder:

```sh
python3 installer/install.py
bash INSTALL.command
```

The first command is a read-only preview. The second shows the changes and asks you to type `INSTALL`. An empty answer cancels. Target: `{{INSTALL_ROOT}}`. The installer copies only the files in `runtime/`. It uses no network and no sudo, and it does not change {{APP}} settings.

Then run `bash VERIFY.command`, and start a new {{APP}} session to check that the skills appear.

## Tools

The installer installs skills only. After the install, follow [TOOLS.md](TOOLS.md): run `python3 {{INSTALL_ROOT}}/.art-production-support/check_tools.py`, install each missing item, and run the check again. An agent that installs this kit for the user does this step too.

{{EDITION_INSTALL_NOTES}}

## Existing names and migration

The installer looks for older copies of these skills in: the target, {{CONFLICT_ROOTS_TEXT}}. An older copy can make the app load the same skill twice, so the installer stops and lists each conflict. It never removes anything by itself. An update of this same package in the same target is allowed.

Move only the listed folders to a dated folder outside all skills roots. Keep the original path so you can restore it. Do not move the reference-library data folder (`zps-art-library`) or unrelated skills. Example for one listed folder:

```python
from pathlib import Path
import shutil, datetime, uuid
source = Path('/exact/conflicting/folder/printed/by/installer')
backup = Path.home() / '.local/share/zps-art-assets-kit/migrations' / (datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
if not source.is_dir() or source.is_symlink():
    raise ValueError('Expected a reviewed, real skill directory')
backup.mkdir(parents=True, exist_ok=False)
shutil.move(str(source), str(backup / source.name))
print('Saved:', backup / source.name, 'Original:', source)
```

Repeat for each listed folder, then run the preview again. Do not keep two generations active at the same time.

## Files that a newer version no longer ships

The installer adds and updates files. It does not delete files that a newer version removed. `installer/removed-files.txt` lists those paths. After `VERIFY.command` passes, move them out of the skills root:

```sh
python3 - <<'PY'
from pathlib import Path; import datetime, shutil
root = Path('{{INSTALL_ROOT}}').expanduser()   # use your --target-root if different
names = Path('installer/removed-files.txt').read_text().split()
archive = Path.home()/'.local/share/zps-art-assets-kit/archived'/datetime.date.today().isoformat()
for n in names:
    src = root/n
    if src.is_file():
        dst = archive/n; dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(dst)); print('archived', n)
PY
```

Run it from the extracted package folder. It moves files; it does not delete them.

## Backup and rollback

The installer backs up each changed file under `{{STATE_ROOT}}/<id>`. The receipt `.art-director-support/installed-manifest.json` in the skills root records the backup path. Keep the same package to roll back:

```sh
python3 installer/install.py --rollback '/absolute/backup/path'
```

Type `ROLLBACK` to confirm. If a file changed after the install, rollback stops instead of overwriting it.

## Offline library and project learning

`resources/library-v0.2.0` holds a snapshot of the reference library: 44 style entries and 132 images, with cards, index, gallery and maintenance tools. The installer does not install it as a skill and does not copy it over an existing library. Give its absolute `reference-library` path in the task, or set it in the project's `art-library.json` (see `examples/art-library.example.json`).

Art Learning writes only to a project data folder that you name. It has no automatic hooks and never changes thresholds or skills by itself.

## Verification limits

Each build checks links, frontmatter, description length, package integrity and the script tests in `tests/`. Full Blender modeling and bake, paid image generation, engine integration and art-quality benchmarks are not part of the build checks.
