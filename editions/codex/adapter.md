# Codex runtime adapter

Use the tools that this session actually has, with their current schemas. Do not infer a capability from this package. Installing the skills does not install Blender, Pillow, numpy, resvg-py, API SDKs or credentials.

Reply to the user in the user's language. The skill files are in English; that does not set the reply language.

## Sandbox

Codex runs commands in a sandbox. By default it can write only inside the workspace and the temp folder, and it has no network. The skills folder is read-only.

- **Blender must run outside the sandbox.** On macOS, Blender crashes at start inside the sandbox because the sandbox blocks the Metal GPU check, also in background mode. This affects `inspect_model.py`, `render_model.py`, every Blender-side 3D tool, and `sweep.py`, `apply_edit.py` and `preflight.py` (they start Blender themselves). The kit installer offers a Codex rule (`~/.codex/rules/zps-art-assets-kit.rules`) that lets these exact commands run outside the sandbox without a prompt:
  - `<Blender> -b --python <installed kit script> -- <args>`
  - `<Blender> -b --python-exit-code 1 --python <installed kit script> -- <args>`
  - `<3D venv python> <sweep.py | apply_edit.py | preflight.py> <args>`

  Write the Blender path, the script path and the venv Python path as literal absolute paths. The rule matches the literal command, so a shell variable such as `$BLENDER` or a relative path does not match, and the command then runs in the sandbox and crashes. If the rule is not installed, ask the user to approve each Blender command outside the sandbox. Do not retry inside the sandbox.
- **Network is off.** `pip install`, Drive sync and paid image APIs (`generate_image.py`) need the user's approval to run with network. The Codex web search tool is separate and is not affected.
- **Write outputs to the workspace.** Give every script an output path inside the task folder. Never write into the skills folder.
- **SVG:** `svg_render.py` needs resvg-py inside the sandbox. Its Chrome fallback crashes inside the sandbox.

## Images

Open supplied local references before edits. For image generation and editing, use the Codex image tool and its rules for paths, reference images, transparency and output. Do not assume a fixed model, output folder, mask support or quota. Copy deliverables to the task folder with versioned names. Image scripts in this package are optional checks and helpers; they do not override the image tool's rules.

`generate_image.py` is an optional paid API adapter, not the default. A live call needs an authorized provider, model and task budget, keys from environment secrets, and network approval. Use its dry run to inspect a request; never print keys. Its budget file has one writer: do not run paid calls in parallel on one budget. After a timeout, count the attempt and read the recorded state before a retry.

## Scripts

The shared scripts are in `.art-production-support/shared/scripts` next to the skill folders. Read [script usage](../shared/scripts/README.md) for the operation you need. Run them with `python3` and absolute paths. Run `--help` before an unfamiliar interface. If a script fails because a tool is missing, run `python3 <skills root>/.art-production-support/check_tools.py` and report its `fix` line to the user. Install dependencies only when the user authorizes it, never as a side effect of loading a skill.

## Skills and delegation

The user can call a skill with `$skill-name` or `/skills`. A missing tool blocks only the output that depends on it. A Blender render does not prove the engine or device result. Use a separate agent for an independent review only when the host supports it and the user allows it; otherwise label the review as a self-review.
