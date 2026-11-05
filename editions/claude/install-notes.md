## Claude Code notes

- Claude Code reads personal skills from `~/.claude/skills`. Call a skill by its name, or describe the task.
- Claude Code has no built-in image generation tool. Skills that create images (Concept Artist, Asset 2D, UI) use an image tool that the session exposes (for example Gen3D `generate_image`, which can cost credits) or the Codex CLI. See `.art-production-support/adapters/runtime.md`.
