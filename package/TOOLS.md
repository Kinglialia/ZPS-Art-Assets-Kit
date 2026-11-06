# Tools for {{PACKAGE}} ({{EDITION_TITLE}}) — setup on a new machine

**For the agent that installs this kit:** the user asks for the whole kit to work after install. Install the skills, then install the tools below, then run the check until every required item is OK. Do these steps in order.

The skill installer itself does not use the network and does not install tools. This file is the tool step.

## Steps

1. Install the skills: run `INSTALL.command` (or `python3 installer/install.py --install`), then `VERIFY.command`.
2. Run the check from the installed copy:

   ```sh
   python3 {{INSTALL_ROOT}}/.art-production-support/check_tools.py
   ```

   If you installed to another root with `--target-root`, use that root instead of `{{INSTALL_ROOT}}`.
3. Install each item that shows `MISS`, with the command in its `fix` line. The table below gives the same commands.
4. Run the check again. Stop when it prints `All required tools present.`
5. Report to the user: what you installed, what is still missing, and why.

## What to install

| Tool | Need | Used by | Install (macOS) |
|---|---|---|---|
| Python 3.11 or newer | Required | All scripts | Python installer from python.org. macOS system Python 3.9 is too old for resvg-py and the library tools |
| Pillow, numpy, resvg-py 0.5.0 | Required | 2D, UI, texture and review scripts (`preview`, `sprite_check`, `anim_preview`, `palette_report`, `score_variants`, `tone_match`, `structure_diff`, `svg_render`) | `python3 -m pip install --user -r {{INSTALL_ROOT}}/.art-production-support/requirements.txt` |
| Blender | Required for model work | `inspect_model`, `render_model` (texture skills) and all 3D tools | `brew install --cask blender` or blender.org (about 1 GB). If Blender is in another place, set `BLENDER=/path/to/blender` |
| 3D tools venv and Blender-side packages | Required for 3D | 3D self-build, optimize, QA | `bash {{INSTALL_ROOT}}/zps-3d-artist/tools/setup_deps.sh` after Blender is installed. It installs numpy, trimesh, scipy, opencv, scikit-image, kneed, xatlas, manifold3d, Pillow and PyYAML into `tools/.deps/` of the 3D skill |
| gltfpack | Recommended | 3D optimize sweep (else Blender Decimate) | `brew install gltfpack` or `npm i -g gltfpack` |
| Node.js + gltf-validator | Optional | 3D `export_check` | `brew install node`, then `npm i -g gltf-validator` |
| rembg | Optional, large | 3D `validate_concept` background removal | `{{INSTALL_ROOT}}/zps-3d-artist/tools/.deps/venv/bin/python -m pip install "rembg[cpu]"` |
| zps-ai CLI | Optional | 3D Artist, ZPS 3D Gen path | Ask the user first: `curl -fsSL https://zps-ai-console.zingplay.com/cli/install.sh \| sh`, then `zps-ai login` (browser sign-in, no key) |
| Meshy / Tripo keys | Optional, paid | 3D Artist, Meshy and Tripo paths | The installer creates `~/.config/zps-art-assets-kit/.env` with empty keys (mode 600). The user pastes the keys into that file. Never put a key in the chat |
| Google Chrome | Optional | Fallback for `svg_render` when resvg-py is missing | Only if resvg-py cannot be installed. The fallback does not work inside the Codex sandbox |

After the 3D setup, run the 3D preflight for a full report of 3D features:

```sh
{{INSTALL_ROOT}}/zps-3d-artist/tools/.deps/venv/bin/python {{INSTALL_ROOT}}/zps-3d-artist/tools/preflight.py --out ~/preflight.json
```

Linux: use the package manager for Python, Blender, Node.js and gltfpack. The pip commands are the same.

{{EDITION_TOOLS_NOTES}}

## If pip refuses to install

Some Python builds (for example Homebrew Python) block `pip install --user` with an "externally managed" error. Do not use `--break-system-packages`. Install Python from python.org instead, and use that `python3` for the skills.

## Do not install

- API keys or paid image-generation providers for `generate_image.py`. The user sets these up per task budget.
- Meshy or Tripo keys. Only the user pastes them into the key file.
- Godot or Figma. The skills do not need them; the people who use them install them.

## Library maintenance (only if the user maintains the offline library)

`resources/library-v0.2.0/reference-library/requirements.txt` lists Pillow for `maintain.py`. Python 3.11 or newer.
