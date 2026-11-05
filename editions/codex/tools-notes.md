## Codex sandbox

Run the tool installs and `setup_deps.sh` outside the Codex sandbox (they need network and write into the skills folder). Inside a Codex session, Blender commands also need to run outside the sandbox; see `.art-production-support/adapters/runtime.md`. resvg-py is required: the Chrome fallback of `svg_render.py` does not work inside the sandbox.
