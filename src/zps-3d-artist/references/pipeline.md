# Detailed static-prop pipeline

Read only the section for the current job. The entrypoint defines authorization and review status. Commands are relative to the skill root; use absolute paths when the task working directory differs.

## Setup

Dependency setup is optional and must be within authorized scope: `bash tools/setup_deps.sh`. It finds Blender, installs the packages Blender's own Python needs into `tools/.deps/blender-py<ver>/` (Blender cannot see a venv; scripts add that folder to `sys.path` themselves), and creates `tools/.deps/venv/` for the pure-Python tools. It also needs `gltfpack` (`brew install gltfpack` or `npm i -g gltfpack`) and, optionally, `node` + `npm i -g gltf-validator` for `export_check`. Then run `tools/.deps/venv/bin/python tools/preflight.py --out evidence/preflight.json`: it records versions and turns each feature on or off. A missing tool disables its feature and adds a warning; it never silently changes a result.

Two runners, decided by the script:
- **Blender-side** (they `import bpy`: `optimize/audit.py`, `cleanup.py`, `bake.py`, `decimate.py`, `self_build/render_views.py`, every `asset_checks/*.py`): `<BLENDER> -b --python <SKILL>/tools/<dir>/<script>.py -- <args>`.
- **Pure Python** (everything else: `validate_concept`, `gate1`, `sweep`, `measure`, `self_build/assembly`, `gates`, `param_fit`, `apply_edit`, `preflight`, `report`, `finalize`): `<SKILL>/tools/.deps/venv/bin/python <SKILL>/tools/<dir>/<script>.py <args>`.

`<BLENDER>` is the absolute path in `paths.blender` of `config.yaml`. `<SKILL>` is the absolute path of this skill folder. Write both as literal absolute paths in every command, not as shell variables: some hosts (for example Codex rules) allow a command by matching its literal text. `sweep.py`, `apply_edit.py` and `preflight.py` start Blender themselves, so the host must let them run Blender too.

Alternative without the Blender app: `pip install bpy` (Python 3.13 → bpy 5.2.x) in the venv; then every script runs as `python3 <script>.py <args>`. Tested on Linux and macOS (Blender 5.x app, 2026-11-03).

Work dir per asset: `output/<asset>/` with `input/` (originals, read-only), `task/spec.json`, `evidence/<step>/*.json|png`, `work/`, `final*.glb`, `report.md`, `contact_sheet.png`.

## Intake

Ask only what the brief does not already answer, in this order:

1. Asset name (default: file name).
2. Size class and real height in meters. If not given, estimate from the name and concept proportions, record `height_source: estimated`, and use it everywhere.
3. Texture style (see [texture handoff](texture-handoff.md) for when to ask Texture Planning before you unwrap): `hand_painted` (baked light in albedo, flat palette, unlit) or `pbr`. This decides UV rules (mirroring forbidden with baked light; palette atlases may overlap on purpose).
4. Face budget (number) or `auto` (find the fewest faces that pass the floor).
5. Target engine for extra checks (`unity`, `godot`, `unreal`, or `glb_only`). Export is always glTF Y-up metres with pivot at bottom-centre.

With concept images, run `tools/optimize/validate_concept.py --images <files> --work output/<asset>/work/optimize --spec task/spec.json` first (gate1 reads masks from that work dir). It labels views from file names (`front|back|left|right|top|34`), removes backgrounds, checks cross-view proportions, scores complexity 0–1. Label any `vision_needed` image yourself. A proportion failure above `concept.proportion_tol` stops the task: name the view and the % off. Then point `spec.concept.views` at the masks it wrote (`../work/optimize/concept/mask_<label>.png`) so every later IoU uses the same masks.

View convention: the prop faces −Y. `left` is the object's **own** left side (camera at +X looking −X), `right` its own right. Many sheets label from the viewer's side instead. For an asymmetric prop, confirm with the user which one the sheet uses before building; a swapped label silently mirrors the result.

Reuse confirmed task constraints in `task/spec.json`; ask only about new consequential assumptions. Budget defaults by size class come from `config.yaml` (`small ≤500`, `medium ≤1500`, `hero ≤5000`, `environment ≤3000` tris; a guess anchored on Arm's mobile guidance, not a standard; see research_notes §5).

## Build from concept (self-build)

Follow [self_build.md](self_build.md); it is the only source for the build loop and its commands. Two steps live here because self_build.md does not cover them:

- **Fit check before the loop.** If `validate_concept.py` scores complexity above `concept.complexity_warn`, or the shape is organic, say so. Offer Meshy, Tripo or ZPS 3D Gen (SKILL.md section 2), and stop unless the user insists.
- **Texture after Optimize (temporary pass).** The result of this step is a temporary texture. Hand it to Texture Artist as described in [texture handoff](texture-handoff.md). `<BLENDER> -b --python <SKILL>/tools/texture/project_concept.py -- --input <low GLB> --concept <view>=<concept image> --spec task/spec.json --work <dir>` projects the painted concept onto the low mesh from the (fitted) concept camera, then fills what no view sees: facet colour gradients, short UV inpaint, then a palette clustered from the concept (up-facing facets take the concept's top colour, back/down facets darkened). Unlit material for `hand_painted`. It reports coverage (projected / facet / inpaint / palette) and masked SSIM per concept view against `texture.ssim_min`. With one 3/4 view, more than half the texture is inferred: say so in the report, and show the back view. More concept views are the real fix.

## Optimize a model

Follow [optimize.md](optimize.md); it is the only source for audit, Gate 1, cleanup, sweep, pick and bake. Then run the QA gate below.

## QA gate (every path, and the review-only job)

Run all of `tools/asset_checks/` with `--input <the baked final GLB> --spec task/spec.json --out evidence/qa/<name>.json`: `mesh_check`, `uv_check`, `contact_check`, `iou_check` (if concept), `concept_coverage` (if concept + camera), `render_rig`, `screen_tris_check`, `export_check`. Read every JSON. Any `fail` blocks export.

Fix the game camera first: the first `render_rig` run without `camera.distance_m` is calibration (pixel checks are info only); copy `distance_m` and `look_at` from its `data.camera` into the spec, then every later run is a real check. See `tools/asset_checks/README.md`.

Multi-object assets: the optimize path joins every mesh into one object named after the asset (audit records the original names). Per-object spec keys (`objects`, `dimensions_m`, `expected_parts`, contacts between those objects) then report `not_checked` with that reason. Check per-object facts on the input before optimizing, and say in the report which checks ran on the input only.

Then the visual review: `render_rig` produced `sheet.png`, clay crops at the game camera, and `concept_compare.png` (only with a ConceptCam; otherwise use `render_views.py --input <final> --mode critic` overlays). Review the image set listed in `templates/REVIEW-RUBRIC.md`. Label self-review versus independent review; neither grants owner approval. `not passed` → one fix cycle (rule 6), then re-run the gate.

When required QA checks pass and the configured visual review milestone is satisfied: `tools/.deps/venv/bin/python tools/finalize.py --work output/<asset> --from <baked GLB> [--min-pass <baked GLB>]`. It refuses while any QA result is `fail` or `error` and names them; otherwise it writes `final.glb` (and `final_budget.glb` / `final_min_pass.glb`).

Scope of `finalize.py`: it requires only a `mesh_check` result for the exact file, and it refuses any `fail` or `error` among the results present. A check that did not run is listed in `data.not_run`; finalize does not block on it. Before you call finalize, confirm yourself that every check the spec requires has a result for that file. Do not report a check in `not_run` as passed.

## Report

Run `tools/.deps/venv/bin/python tools/report.py --work output/<asset> --spec output/<asset>/task/spec.json`. It collects every result JSON, writes `report.json`, `contact_sheet.png` and a `report.md` skeleton; you then edit the prose. `report.md` in Vietnamese, short: entry, generator/path, faces (source → chosen, budget, min_pass), metrics (IoU min, Hausdorff, SSIM), texture (mode, source, resolution), validation errors, critic verdict with the images it cited, warnings, what was **not** checked (no engine, no device, estimated height), file paths. `report.json` mirrors it. `contact_sheet.png`: concept | clay | final, plus the error-vs-faces curve with knee and chosen marked.

Never call the result "game-ready" when engine or device checks were skipped. Say which milestone it reached.

