# Editions: Codex and Claude Code

Both editions come from the same `src/`. This table lists every difference. If you add a difference, add it here and in `editions/`.

| Item | Codex | Claude Code |
|---|---|---|
| Install folder | `~/.agents/skills` | `~/.claude/skills` |
| Skill names | `zps-<name>-codex` | `zps-<name>` |
| SKILL.md title | `# ZPS - <Name> - Codex` | `# ZPS - <Name>` |
| Runtime adapter (`.art-production-support/adapters/runtime.md`) | `editions/codex/adapter.md`: sandbox rules (Blender outside the sandbox, no network, read-only skills folder), Codex image tool, `$skill` calls | `editions/claude/adapter.md`: image tool choice (session image tool such as Gen3D, Codex CLI, or paid API), subagent for independent review |
| `agents/openai.yaml` | Yes: display name; Art Learning has `allow_implicit_invocation: false` | No |
| Installer conflict check | Target, `~/.agents/skills`, `$CODEX_HOME/skills` | Target only |
| Old names treated as conflicts | `editions/legacy-aliases.json` | Same list, plus the `-codex` names of the Codex edition |
| Backups | `~/.local/share/zps-art-assets-kit/codex/backups` | `~/.local/share/zps-art-assets-kit/claude/backups` |
| `removed-files.txt` | Files that newer versions removed from Codex installs | Files that newer versions removed from Claude installs |

## Test an edition without touching the real skills

```sh
python3 build.py --edition all
T=$(mktemp -d)
cd "dist/ZPS-Art-Assets-Kit-codex-v$(cat VERSION)"
HOME=$T python3 installer/install.py --install --target-root "$T/skills" --state-root "$T/state"
HOME=$T python3 installer/install.py --verify --target-root "$T/skills"
```

Type `INSTALL` when asked. Use the same steps for the Claude edition folder.

## Run a script inside the Codex sandbox

The Codex CLI can run one command inside its sandbox without a model call:

```sh
codex sandbox -c 'sandbox_mode="workspace-write"' python3 <script> <args>
```

Run it from a workspace folder. Use it to check that a new script works inside Codex. Known result (Codex CLI 0.164, macOS): Pillow, numpy and resvg-py scripts work; Blender crashes; Chrome headless crashes; network is blocked.
