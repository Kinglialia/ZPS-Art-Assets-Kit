# Claude Code runtime adapter

Use the tools that this session actually has, with their current schemas. Do not infer a capability from this package. Installing the skills does not install Blender, Pillow, numpy, resvg-py, API SDKs or credentials.

Reply to the user in the user's language. The skill files are in English; that does not set the reply language.

## Images

Claude Code has no built-in image generation tool. Before a skill step that creates or edits an image, select one of these and tell the user which one you use:

1. An image tool that this session exposes (for example the Gen3D `generate_image` MCP tool). It can cost credits: tell the user the cost and wait for their approval when the tool requires it.
2. The Codex CLI, if it is installed and the user allows it (`codex exec` with the image tool). It uses the user's Codex account.
3. `generate_image.py` (paid API adapter) only with an authorized provider, model, task budget and keys from environment secrets.

If none is available, deliver the brief or prompt and state that the image step was not done. Do not call a prompt a finished image.

Open supplied local references before edits. Copy deliverables to the task folder with versioned names. Image scripts in this package are optional checks and helpers.

## Scripts

The shared scripts are in `.art-production-support/shared/scripts` next to the skill folders. Read only the section of [script usage](../shared/scripts/README.md) for the operation you need, not the whole file: [generate](../shared/scripts/README.md#generate), [preview](../shared/scripts/README.md#preview), [score](../shared/scripts/README.md#score), [tone match](../shared/scripts/README.md#tone-match), [palette](../shared/scripts/README.md#palette), [frames](../shared/scripts/README.md#sprites), [SVG](../shared/scripts/README.md#svg), [model check](../shared/scripts/README.md#model), [model render](../shared/scripts/README.md#render), [image checks](../shared/scripts/README.md#image-checks), [evidence gate](../shared/scripts/README.md#evidence-gate). Run them with `python3` and absolute paths. Run `--help` before an unfamiliar interface. If a script fails because a tool is missing, run `python3 <skills root>/.art-production-support/check_tools.py` and report its `fix` line to the user. Install dependencies only when the user authorizes it, never as a side effect of loading a skill. Write outputs to the task folder, never into the skills folder.

## Skills and delegation

The user can call a skill by its name. A missing tool blocks only the output that depends on it. A Blender render does not prove the engine or device result. For an independent review, use a subagent with a fresh context that receives only the artifacts and the brief, when the user allows it; otherwise label the review as a self-review.
