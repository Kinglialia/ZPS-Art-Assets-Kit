## Codex notes

- Codex reads personal skills from `~/.agents/skills`. Call a skill with `$skill-name` or `/skills`.
- Codex runs commands in a sandbox. Blender crashes inside the sandbox on macOS, so every Blender command (texture model checks and all 3D tools) must run outside it, with your approval each time or with a Codex rule that allows the Blender command. Network is off by default; tool installs need your approval.
- Codex shows only a limited amount of skill descriptions at session start. Many other skills in `~/.agents/skills` can make Codex shorten or drop some descriptions. Keep that folder tidy.
