## Codex notes

- Codex reads personal skills from `~/.agents/skills`. Call a skill with `$skill-name` or `/skills`.
- Codex runs commands in a sandbox. Blender crashes inside the sandbox on macOS, so the kit's Blender commands (texture model checks and all 3D tools) must run outside it. After the install and the tool setup, create a Codex rule that allows only the kit's own Blender scripts:

  ```sh
  python3 installer/codex_rules.py           # preview and self-test
  python3 installer/codex_rules.py --write   # write ~/.codex/rules/zps-art-assets-kit.rules
  ```

  Restart Codex after writing. Run it again after each upgrade. Without the rule, Codex asks you to approve each Blender command.
- Network is off by default in the sandbox; tool installs need your approval.
- Codex shows only a limited amount of skill descriptions at session start. Many other skills in `~/.agents/skills` can make Codex shorten or drop some descriptions. Keep that folder tidy.
