# ZPS Art Director Codex v0.5.6

This package integrates the AD + Concept v0.4.0 bundle with 2D, UI, texture, static 3D, project learning and an offline reference-library snapshot. Eighteen discoverable skills use `ZPS - <Skill name> - Codex` display names. Shared production resources are stored once; loading a skill does not load the entire package. See CAPABILITIES.md.

## Preview and install

Requires Python 3. Extract the ZIP to a stable directory. From that directory:

```sh
python3 installer/install.py
bash INSTALL.command
```

The first command is read-only preview. The second prints the changes and asks for `INSTALL`; a blank response cancels. Target: `~/.agents/skills`. No network, sudo, Codex settings, agent registrations, package dependencies or API calls are part of installation. Only files in runtime/ are copied.

Run `bash VERIFY.command` afterwards. File verification does not prove application discovery; inspect the 18 skills in a new Codex session. This build has only been installed in isolated test directories, not the user's live skills directories.

## Tools

The installer installs skills only; it does not install tools. After install, follow [TOOLS.md](TOOLS.md): run `python3 ~/.agents/skills/.art-production-support/check_tools.py`, install each missing item, and run the check again. An agent that installs this kit for the user does this step too.

## Existing names and migration

The installer checks source aliases and new names across the target, ~/.agents/skills and CODEX_HOME/skills (default ~/.codex/skills). Existing 2D, texture or 3D standalone skills may therefore block a combined install. It lists exact conflicts; it never automatically removes them. Updating an existing combined package in the selected target is supported.

Archive only the printed conflicting skill folders to a dated directory outside all skills roots, preserving their original paths for restore. Do not move the actual zps-art-library data or unrelated skills. Example for one reviewed conflict:

```python
from pathlib import Path
import shutil, datetime, uuid
source = Path('/exact/conflicting/folder/printed/by/installer')
backup = Path.home() / '.local/share/art-director-codex/migrations' / (datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
if not source.is_dir() or source.is_symlink():
    raise ValueError('Expected a reviewed, real skill directory')
backup.mkdir(parents=True, exist_ok=False)
shutil.move(str(source), str(backup / source.name))
print('Saved:', backup / source.name, 'Original:', source)
```

Repeat only for reviewed conflicts, then rerun preview. To abandon a migration after installing, first roll back the new package, then restore the archived directories only when their original locations are absent. Do not activate both generations at once.

## Upgrade from v0.5.0 or v0.5.1: archive old copies

The installer adds and updates files. It does not delete files that a newer package no longer ships. v0.5.2 moved 27 duplicate templates and review files into `.art-production-support`; `installer/removed-in-0.5.2.txt` lists the old paths. No v0.5.2 skill links to them, but an agent that browses a skill folder can still read them. After `VERIFY.command` passes, move them out of the skills root:

```sh
python3 - <<'PY'
from pathlib import Path; import datetime, shutil
root = Path.home()/'.agents/skills'   # use your --target-root if different
names = Path('installer/removed-in-0.5.2.txt').read_text().split()
archive = Path.home()/'.local/share/art-director-codex/archived'/datetime.date.today().isoformat()
for n in names:
    src = root/n
    if src.is_file():
        dst = archive/n; dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(dst)); print('archived', n)
PY
```

Run it from the extracted package folder. It moves files; it does not delete them. Empty `templates/` folders may remain.

## Backup and rollback

Changed runtime files are backed up under ~/.local/share/art-director-codex/backups/<id>. The installed .art-director-support/installed-manifest.json receipt records the exact backup path. Keep the same package to roll back:

```sh
python3 installer/install.py --rollback '/absolute/backup/path'
```

Review and type `ROLLBACK`. Later edits cause rollback to stop instead of silently overwrite them. Unrelated files remain. Installation backup and manually archived legacy folders are separate. The installed manifest covers packaged files, not later dependencies or generated data.

## Offline library and project learning

The package includes the original resources/library-v0.2.0 snapshot: 44 style entries and 132 images, plus cards, index, gallery, maintenance tools and historical metadata. These files are NOT installed as skills or copied over the user's existing library. Keep the extracted resource folder, supply its absolute reference-library path in the task, or configure the project's art-library.json. examples/art-library.example.json demonstrates a path relative to that example file; update it when copying elsewhere. Historical manager instructions inside resources are source data; the active manager is the newer runtime skill.

No cloud sync, share changes or live reference refresh occurs. Saved Drive IDs and review statuses do not prove current access or current visual inspection.

Art Learning requires an explicit project data root and a request/project convention enabling capture. It has no automatic hooks and never writes to ~/.claude, installs memory, modifies thresholds or infers approval. It provides a tested ledger foundation, not the complete statistical self-improvement system proposed in the research document.

## Tool dependencies and verification limits

Image diagnostics may need Pillow/numpy; modeling/rendering may need Blender/bpy and other dependencies described by preflight. Check the actual environment before setup. The 3D dependency installer and paid image adapters are shipped but never executed by this installer. Paid service use requires existing authorization and budget.

See REVISION-TEST-RESULTS.txt, TOOLS-TEST-RESULTS.txt, LEARNING-TEST-RESULTS.txt and LIBRARY-TEST-RESULTS.txt. Syntax, YAML, package integrity, installer, ledger and selected diagnostics were checked; full Blender modeling/render/bake, paid generation, engine integration and art-quality benchmarks were not run. Source research is preserved as unverified historical material, not new certification.
