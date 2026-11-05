# AGENTS.md — how to change and build ZPS Art Assets Kit

This repository is the source of an art skill kit. One source builds two editions: **Codex** and **Claude Code**. Read this file before you change anything.

## Layout

| Path | What it holds | Edit? |
|---|---|---|
| `src/` | The skills (`zps-*`) and the shared support folders (`.art-director-support`, `.art-production-support`). Skill names have no edition suffix | Yes: the only source of skill content |
| `editions/codex/`, `editions/claude/` | Per-edition files: `edition.json`, `adapter.md` (runtime adapter), install and tools notes, `removed-files.txt`; Codex also has `openai/<skill>.yaml` | Yes, only for real edition differences |
| `editions/legacy-aliases.json` | Old skill names that the installer treats as conflicts | When a skill is renamed |
| `package/` | Package files with `{{PLACEHOLDERS}}`: `INSTALL.md`, `TOOLS.md`, `CAPABILITIES.md`, `installer/`, `examples/`, command files | Yes |
| `resources/` | Offline reference-library snapshot | Only for a library update |
| `tests/` | Intent tests for scripts; `build.py` runs them | Yes |
| `release-notes/` | One note per version | Add one per version |
| `docs/` | `EDITIONS.md` and history | Yes |
| `dist/` | Build output. Not in Git | **Never edit** |

## Build

```sh
python3 build.py --edition all
```

The build, for each edition:
1. Copies `src/` to `dist/<package>-<edition>-v<VERSION>/runtime/`, adds the skill suffix (`-codex` for Codex, none for Claude) to folders and to every exact skill name in the text.
2. Copies `editions/<edition>/adapter.md` to `.art-production-support/adapters/runtime.md`, and for Codex the `agents/openai.yaml` files.
3. Fills the placeholders, sets the version in every SKILL.md and skill.yaml, and writes `manifest.json` (installer payload with hashes) and `PACKAGE-MANIFEST.json`.
4. Checks: frontmatter `name` equals the folder, `description` is 300 characters or fewer, no broken links, no unreplaced placeholders, no Codex names in the Claude edition. Then runs `tests/`.
5. Writes the ZIP. A failed check stops the build with exit 1.

The script tests need Pillow and resvg-py (see `package/TOOLS.md`). Use `--skip-tests` only to look at a failing build, never for a release.

## Rules

- Change skill content only in `src/`. Put a difference between editions in `editions/`, not in `src/`. If a sentence in `src/` is true for only one app, move it to that edition's `adapter.md`.
- Write skill content in simple technical English (ASD-STE100 style: short sentences, active voice, one instruction per sentence). Skills reply to the user in the user's language; the adapter says so.
- Keep each `description` at 300 characters or fewer. Put what the skill does first, then the trigger words, including 2–3 Vietnamese trigger phrases. Put "not for X" boundaries in the SKILL.md body, not in the description. Codex loads all descriptions at session start within a fixed budget and shortens them when they are too long.
- Refer to another skill by its neutral name (`zps-asset-2d`), and link with a relative path (`../zps-asset-2d/SKILL.md`). The build adds the suffix.
- Run scripts with `python3`, never `python`. macOS has no `python` command.
- A new tool or package that a script needs must go into `package/TOOLS.md`, `src/.art-production-support/requirements.txt` and `src/.art-production-support/check_tools.py` in the same change.
- A new script needs an intent test in `tests/`, and `build.py` must run it.
- A file removed from `src/` must be listed in `editions/<edition>/removed-files.txt` (installed path, with the edition suffix), so that users can archive the old copy after an upgrade. The installer never deletes files.
- Codex sandbox facts: Blender crashes inside the Codex sandbox on macOS (Metal GPU check), so Blender commands must run outside it; network is off by default; the skills folder is read-only. Keep these facts in `editions/codex/adapter.md`.
- Claude Code has no built-in image generation. Keep the image-tool choice in `editions/claude/adapter.md`.

## Release

1. Increase `VERSION` (semantic: minor for new behavior, patch for fixes).
2. Add `release-notes/v<VERSION>-<topic>.md`: what changed, why, what was checked, what was not checked.
3. `python3 build.py --edition all` must pass with tests.
4. Install each edition into a temporary HOME and run `--verify` (see `docs/EDITIONS.md`).
5. Commit, tag `v<VERSION>`, push, and attach both ZIP files from `dist/` to a GitHub release. Never overwrite an earlier tag or release.

## Install for the user

Each ZIP is self-contained: `bash INSTALL.command`, then `bash VERIFY.command`, then follow `TOOLS.md` with `check_tools.py`. Do not move or delete the user's existing skills without asking; the installer lists conflicts and `INSTALL.md` shows how to archive them.
