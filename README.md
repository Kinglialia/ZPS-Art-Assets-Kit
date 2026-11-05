# ZPS Art Assets Kit

Art skills for game production: concept, 2D assets and UI, textures, static 3D props, review, reference library and project learning. Version 0.5.6 (18 skills).

- Install the skills: [INSTALL.md](INSTALL.md). Run `bash INSTALL.command`, then `bash VERIFY.command`.
- Install the tools that the skills need: [TOOLS.md](TOOLS.md). Run `python3 ~/.agents/skills/.art-production-support/check_tools.py`.
- What each skill does and how loading works: [CAPABILITIES.md](CAPABILITIES.md).
- Change history: [release-notes/](release-notes/).

Skill sources are in `runtime/`. The installer copies only `runtime/` and checks every file against `manifest.json`. If you edit a file in `runtime/`, regenerate `manifest.json`, or the installer refuses to install.
