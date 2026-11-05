# Codex runtime adapter

Use tools actually available in this session and their current schemas. Do not infer capability from this package's provenance. Skill installation does not install Blender, Pillow, numpy, API SDKs or credentials.

For images, open supplied local references before edits. Prefer the current image-generation/editing tool and its applicable skill; follow its path, reference, transparency and output handling rules. Do not assume a fixed model, output directory, mask support, login mode or quota. Copy/export deliverables to the authorized task location with versioned names when supported. Image manipulation scripts remain optional diagnostics/helpers; they do not override tool instructions on how to edit images.

The shared scripts are at `.art-production-support/shared/scripts` next to the installed skill folders. Read [script usage](../shared/scripts/README.md) for the operation needed. Run help/preflight before an unfamiliar interface; use absolute script paths and a task work directory. Pillow/numpy or Blender may be needed per script; inspect the environment first. Install dependencies only within authorized scope, never as a side effect of loading a skill. If a script fails because a tool is missing, run `python3 <skills root>/.art-production-support/check_tools.py` and report the `fix` line to the user; the package file TOOLS.md lists every tool and its install command.

`generate_image.py` is an optional paid API adapter, not the default. Live calls require an authorized provider, model and task budget. Keys come from environment secrets. Use its dry-run to inspect a request; never print keys. Its budget file is single-writer: do not run paid calls concurrently against one budget. After a timeout, count the attempt and inspect recorded state before retrying. No API call is made by the installer.

A missing tool blocks its dependent output only. A Blender render does not prove the target engine or device result. Use host-supported collaboration only when delegated work is authorized and useful; this package does not require a separate agent team.
