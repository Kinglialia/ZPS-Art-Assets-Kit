# Tools — run per operation, not a required stage

Python 3.11+. Pillow is needed for preview/palette/sprite/inspect. generate_image and check_gate use the standard library. `inspect_model` and `render_model` run inside Blender (see below). Run with the absolute path to the package scripts:

```sh
ART_TOOLS=/absolute/path/to/skills/.art-production-support/shared/scripts
# Resolve this path from the actual install root.
```

Every tool that writes a file refuses to overwrite. Use versioned names (`icon_sword_v3.png`).

<a id="generate"></a>
## Generate/edit an image — costs money on every call

```sh
echo '{"max": 3, "used": 0}' > task-budget.json   # budget approved by the task/user
python3 "$ART_TOOLS/generate_image.py" --provider gemini --model "$ART_IMAGE_MODEL" \
  --prompt-file prompt_v1.txt --image style_anchor.png --image set_anchor_asset.png \
  --out icon_sword_v1.png --budget-file task-budget.json
```

Always run `--dry-run` before you change the structure of the request. Take the key only from the environment variables `GEMINI_API_KEY` / `OPENAI_API_KEY`. Each output comes with a `.json` file that records the prompt, input hash, and model. Copy it into the task record. If the budget runs out, the tool exits with code 3. Stop and diagnose. Use a mask only with OpenAI (the transparent area is the area to edit). Gemini edits by a description of the area, so check the kept area with `inspect_image.py --lock-mask`. Write the prompt according to the [quality standard](../../rules/art-quality.md).

<a id="preview"></a>
## Preview for your own viewing

```sh
python3 "$ART_TOOLS/preview.py" sheet icon_v2.png --sizes 48 64 128 --backgrounds light dark "#2b2140" --out sheet_v2.png
python3 "$ART_TOOLS/preview.py" compare icon_v2.png ref_R1.png ref_R2.png --height 256 --small 64 --out cmp_v2.png
python3 "$ART_TOOLS/preview.py" value concept_v3.png --small 96 --out value_v3.png
python3 "$ART_TOOLS/preview.py" tile ground_v1.png --repeat 3 --out tile_v1.png
```

The output is an image that you **must open and look at**. The tool does not score. Use `--nearest` for pixel art.

<a id="score"></a>
## Score and choose an option

```sh
python3 "$ART_TOOLS/score_variants.py" cand_a.png cand_b.png cand_c.png --reference ref_a.jpg --reference ref_b.jpg --palette style_palette.json
```

`--profile` (needs no candidate) prints the mean color of the darkest 5% of pixels, the cast of each band, and the value of each reference. Use it when you build a style sheet.

The tool ranks by the deviation of the color cast of each light band, the dark area color, the value, and the palette against the Execution reference **of the same deliverable type**. Lower = closer to the reference. The weights are uncalibrated estimates. Compare totals only within the same scoring run. Use it as a gate/tie-breaker. Still open the top 2–3 and review them by eye. The tool skips transparent pixels. It needs numpy.

<a id="tone-match"></a>
## Adjust color to a reference (no generation)

```sh
python3 "$ART_TOOLS/tone_match.py" scene_v3.png --reference ref_a.jpg --reference ref_b.jpg --bands shadows midtones --strength 0.8 --out scene_v3_tm1.png
python3 "$ART_TOOLS/structure_diff.py" scene_v3.png scene_v3_tm1.png --max-lightness-changed 0.02 --min-edge-agreement 0.95
```

The tool moves the color cast (a*/b* in Lab) of the dark/mid/light bands toward the cast of the reference. It keeps lightness, shape, and alpha unchanged. Use it when the structure is acceptable but the color deviates. Do not adjust the light band if the sky/highlight is already correct. It needs numpy.

`structure_diff.py` confirms that an edit keeps the shape. It reports the % of pixels whose lightness changed by more than `--l-tol`, and the ratio of edges that still match (Sobel on L*). Use it for every "change only color" edit or any edit that must keep the shape. For exact pixels, use `inspect_image --lock-mask`.

<a id="palette"></a>
## Palette

```sh
python3 "$ART_TOOLS/palette_report.py" icon_v2.png --palette bible_palette.json --max-delta 10
```

The tool reports the dominant colors, the nearest color in the palette, and ΔE (CIE76). `off_palette` is a sign that needs a look. It is not a defect by itself: antialiasing and lighting create valid intermediate colors.

<a id="sprites"></a>
## Frame sequence

```sh
python3 "$ART_TOOLS/sprite_check.py" walk_*.png --max-baseline-shift 1
python3 "$ART_TOOLS/sprite_check.py" walk_sheet.png --grid 8 1
```

The tool checks for a uniform canvas, empty frames, and baseline/center drift by alpha. It does not evaluate pose or rhythm.

```sh
python3 "$ART_TOOLS/anim_preview.py" walk_*.png --height 128 --fps 12 --out walk_v2
python3 "$ART_TOOLS/anim_preview.py" walk_sheet.png --grid 8 1 --nearest --step 2 --out walk_v2
```

The tool outputs `<out>_strip.png` (filmstrip), `<out>_onion.png` (onion skin: first frame faint, last frame strong; color shifts from blue to red in order), and `<out>.gif` at the given fps. The agent opens the filmstrip and the onion skin to see the trajectory, the spacing of poses, and jerky places. The GIF is for human viewers. The agent cannot see motion. If no human viewer has seen it, record rhythm and feel as `not_checked`. If frames have different canvas sizes, the tool stops. Run `sprite_check.py` first. The tool does not overwrite existing files.

<a id="svg"></a>
## SVG → PNG for UI

```sh
python3 "$ART_TOOLS/svg_render.py" btn_play_normal.svg btn_play_pressed.svg --scales 1 2 --out-dir export/ui
```

The tool outputs `<name>.png` (1x = width/height px of the SVG) and `<name>@2x.png`, with a transparent background. It uses resvg (`pip install --user resvg-py==0.5.0`). If resvg is not available, it uses headless Chrome if it finds one. It warns when the SVG has `<text>`, filter, mask, script, or foreignObject. It does not overwrite existing files. By default, this PNG is the file you hand to the engine. Open it with `preview.py sheet` to check it at display size.

<a id="model"></a>
## Evaluate a model (Blender headless)

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python /abs/skills/.art-production-support/shared/scripts/inspect_model.py -- prop_v4.glb --texture-size 1024
```

**Blender command form (both model scripts).** Run them inside Blender: `<Blender> -b --python <script> -- <args>`. Write the Blender path and the script path as literal absolute paths, not shell variables such as `$ART_TOOLS`. Some hosts (for example Codex rules) allow a command by matching its literal text. The Blender path comes from `paths.blender` in the 3D skill's `config.yaml`, or from the `BLENDER` environment variable. A Python that has the `bpy` module can run the same script with `python3 <script> <args>`.

The tool reports triangle count, dimensions, materials, UV sets, UV coverage/overlap (including overlap between objects that share an image)/out-of-range, vertex color, and texel density at the planned texture size. It is read-only. Use it for texture planning. Overlap and out-of-range can be intentional (mirror, tileable, trim).

<a id="render"></a>
## Render a model (Blender headless)

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python /abs/skills/.art-production-support/shared/scripts/render_model.py -- prop_v4.glb --mode checker --views 4 --out-dir /abs/task/renders_checker_v4
/Applications/Blender.app/Contents/MacOS/Blender -b --python /abs/skills/.art-production-support/shared/scripts/render_model.py -- prop_v4.glb --mode textured --texture albedo_v2.png --out-dir /abs/task/renders_tex_v2
```

Use the Blender command form above. `clay`: form. `checker`: UV distortion/density. `textured`: texture on the model. It uses Cycles CPU with neutral lighting. It does not replace a check in Godot.

<a id="image-checks"></a>
## Check an image file when you need measurements

```sh
python3 "$ART_TOOLS/inspect_image.py" /path/output.png --size 1024 1024 --require-alpha
python3 "$ART_TOOLS/inspect_image.py" /path/revision.png --reference /path/source.png --lock-mask /path/locked.png --out /path/image-checks-v2.json
```

In a grayscale mask, a non-zero value marks an area that must keep exact RGBA. This is not a default requirement for every edit. Keeping the design/identity is different from keeping every pixel. The tool rejects an empty mask or a mask of a different size. It does not auto-resize. The report records the hash of the output and of the reference/mask that it measured. It does not edit the image. --out only creates a new file, to keep the evidence of the old version.

An alpha channel can be fully opaque. A pass does not prove transparency, clean edges, or correct premultiplication. Exit 0 means the checks that ran passed. Exit 1 means at least one failed. Exit 2 means an input or dependency error. Do not accept art as passing from a decode pass. A missing Pillow blocks only these measurements. Use equivalent metadata/visual inspection when it is enough for the task, and record the parts you did not measure.

<a id="projection-guide"></a>
## Guide only when you have camera-space geometry

```sh
python3 "$ART_TOOLS/projection_guide.py" "$ART_TOOLS/examples/camera-box.json" --out /path/new-guide.svg
```

X is right, Y is up, Z is toward the scene. Perspective uses vertical FOV/aspect. Ortho uses vertical span. Do not infer the camera from an image. Do not measure artwork/anatomy. The tool does not support clipping, lens shift/distortion/crop. It refuses to overwrite. When you have no real coordinates, build the guide by observation or in a DCC you have permission to use. Do not invent numbers to make the tool run.

<a id="evidence-gate"></a>
## Gate only for defined automatic acceptance

A quick review does not need JSON or a gate. If the caller needs a gate, agree on the required IDs and the artifact version first:

```json
{"required": ["decode", "locked_pixels"], "artifact_sha256": "<SHA256 of the output to accept>"}
```

Use the saved inspector report directly. Do not recompose the JSON:

```sh
python3 "$ART_TOOLS/check_gate.py" --spec /path/gate.json --measurement /path/image-checks-v2.json
```

--measurement checks the identity of the artifact/reference/mask and uses the report file itself as evidence. The report format must be art_image_inspector schema 1. This header is not a signature. The tool checks integrity and the reported status. It does not confirm who ran it or the quality of the image.

For several kinds of evidence, use --report instead of --measurement. The report has artifact {path, sha256}, inputs if needed, and checks [{id, status, evidence: {path, sha256}, reason}]. A path is relative to the report, or absolute. A required pass must have evidence with the correct hash. Fail, not_checked, or missing blocks. N/A needs allow_not_applicable in the spec and a reason. Do not drop a required check, change the spec/version, or grant an exemption to get a pass.

Exit 0 = the required statuses/evidence are valid. Exit 1 = not enough yet. Exit 2 = bad input. Other checks are returned separately. The gate does not grant art approval. A comment in the report still needs a responsible reviewer.
