# Historical source; not active runtime instructions

---
name: 3d-artist
description: Build, optimize and QA game-ready static 3D props for mobile. Use when the user gives concept art (one view or a 5-view sheet) and wants a 3D model built; gives an existing model (GLB/FBX/OBJ, any source) and wants it reduced to a face budget or to the fewest faces that still match the concept/original with no mesh errors; or wants a 3D asset reviewed against a concept. Triggers on "dựng model", "model từ concept", "giảm mặt", "optimize poly", "retopo", "low poly", "budget mặt", "kiểm model", "review model 3D", or any mention of Meshy, Tripo, Hunyuan3D, Blender props.
---

# 3D Artist

Static props and environment pieces for mobile games. Triangle meshes only. Rigged or animated characters, cloth, creatures and quad retopology are out of scope: say so and stop.

Three jobs, one QA gate:

| Job | Entry | Path |
|---|---|---|
| Build from concept | concept image(s), no model | `references/self_build.md` |
| Optimize a model | model, with or without concept | `references/optimize.md` |
| Review a model | model + concept, no edits wanted | QA gate only, then report |

## Ground rules

1. **Scripts measure, you orchestrate, the critic judges.** Every number in a report comes from a script's JSON. Pass/fail on geometry comes from scripts against `task/spec.json`. Pass/fail on "looks like the concept" comes from the `3d-critic` subagent reading clay and normal renders against `templates/REVIEW-RUBRIC.md`. You never mark a criterion passed yourself. Why: VLMs agree with humans only ~50% of the time when grading 3D, but symbolic checks agree ~90% ([research_notes](references/research_notes.md) §2).
2. **Spec thresholds belong to the person who gave the task.** Write `task/spec.json` from the brief using `templates/spec.template.json` and `config.yaml` defaults, show it, get it confirmed, then never loosen a threshold to make a check pass. If a threshold looks wrong, say which key and why, and ask.
3. **Judge geometry on clay and normals, never on textured renders.** Texture adds +144 Elo in human preference without changing the mesh ([research_notes](references/research_notes.md) §2). The critic gets textured renders only for the texture step.
4. **Evidence is a file you opened.** Conclude only from images you actually viewed and JSON you actually read. Say which. "The build log is green" proves nothing about the shape.
5. **Never export a mesh that fails `mesh_check`**, even to meet a budget. Export both `final_budget.glb` and `final_min_pass.glb` and explain the gap instead.
6. **Bounded repair loops.** Max 3 critic cycles per stage, one fix per cycle, revert when the fix makes the worst view worse. Same error twice in a row: stop editing parameters and write a one-paragraph diagnosis (suspected cause, different approach) before touching anything.
7. **No paid generator call** (Meshy, Tripo) without the user's explicit yes per asset, and never past `generation.credit_cap_per_asset`. Adapters are stubs until configured.
8. Talk to the user in Vietnamese, one question at a time, 2–4 options, one marked recommended. Technical terms stay English.

## Setup

Once per machine: `bash tools/setup_deps.sh`. It finds Blender, installs the packages Blender's own Python needs into `tools/.deps/blender-py<ver>/` (Blender cannot see a venv; scripts add that folder to `sys.path` themselves), and creates `tools/.deps/venv/` for the pure-Python tools. It also needs `gltfpack` (`brew install gltfpack` or `npm i -g gltfpack`) and, optionally, `node` + `npm i -g gltf-validator` for `export_check`. Then run `tools/.deps/venv/bin/python tools/preflight.py --out evidence/preflight.json`: it records versions and turns each feature on or off. A missing tool disables its feature and adds a warning; it never silently changes a result.

Two runners, decided by the script:
- **Blender-side** (they `import bpy`: `optimize/audit.py`, `cleanup.py`, `bake.py`, `decimate.py`, `self_build/render_views.py`, every `asset_checks/*.py`): `$BLENDER -b --python tools/<dir>/<script>.py -- <args>` (`$BLENDER` = `paths.blender` in `config.yaml`).
- **Pure Python** (everything else: `validate_concept`, `gate1`, `sweep`, `measure`, `self_build/assembly`, `gates`, `param_fit`, `apply_edit`, `preflight`, `report`, `finalize`): `tools/.deps/venv/bin/python tools/<dir>/<script>.py <args>`.

Alternative without the Blender app: `pip install bpy` (Python 3.13 → bpy 5.2.x) in the venv; then every script runs as `python <script>.py <args>`. Tested on Linux and macOS (Blender 5.x app, 2026-11-03).

Work dir per asset: `output/<asset>/` with `input/` (originals, read-only), `task/spec.json`, `evidence/<step>/*.json|png`, `work/`, `final*.glb`, `report.md`, `contact_sheet.png`.

## Intake

Ask only what the brief does not already answer, in this order:

1. Asset name (default: file name).
2. Size class and real height in meters. If not given, estimate from the name and concept proportions, record `height_source: estimated`, and use it everywhere.
3. Texture style: `hand_painted` (baked light in albedo, flat palette, unlit) or `pbr`. This decides UV rules (mirroring forbidden with baked light; palette atlases may overlap on purpose).
4. Face budget (number) or `auto` (find the fewest faces that pass the floor).
5. Target engine for extra checks (`unity`, `godot`, `unreal`, or `glb_only`). Export is always glTF Y-up metres with pivot at bottom-centre.

With concept images, run `tools/optimize/validate_concept.py --images <files> --work output/<asset>/work/optimize --spec task/spec.json` first (gate1 reads masks from that work dir). It labels views from file names (`front|back|left|right|top|34`), removes backgrounds, checks cross-view proportions, scores complexity 0–1. Label any `vision_needed` image yourself. A proportion failure above `concept.proportion_tol` stops the task: name the view and the % off. Then point `spec.concept.views` at the masks it wrote (`../work/optimize/concept/mask_<label>.png`) so every later IoU uses the same masks.

View convention: the prop faces −Y. `left` is the object's **own** left side (camera at +X looking −X), `right` its own right. Many sheets label from the viewer's side instead. For an asymmetric prop, confirm with the user which one the sheet uses before building; a swapped label silently mirrors the result.

Then write `task/spec.json` and show it. Budget defaults by size class come from `config.yaml` (`small ≤500`, `medium ≤1500`, `hero ≤5000`, `environment ≤3000` tris; a guess anchored on Arm's mobile guidance, not a standard; see research_notes §5).

## Build from concept (self-build)

Read `references/self_build.md` in full before starting. Summary:

1. **Fit check.** Self-build fits crates, barrels, chests, pillars, fences, tables, lamps, signs, simple weapons, simple architecture. Complexity above `concept.complexity_warn` or organic shapes: say so, offer the optimize path with an external generator, and stop unless the user insists.
2. **Measure.** Builder computes overall and per-part sizes from the concept masks and the recorded height, and writes them down before any geometry.
3. **Part graph.** Builder writes `part_graph.json` (named params, typed attachments, no coordinates) and `parts_lib.py`. `tools/self_build/assembly.py` solves placement and unions parts with manifold3d.
4. **Rollouts.** Spawn `self_build.rollouts` builders independently; keep the one with the best worst-view IoU after a coarse build. Spend tokens on picking, not on more samples.
5. **Concept camera.** For painted 3/4 views, run `tools/self_build/fit_camera.py --write-spec` once on the first coarse build (records `spec.concept.cameras`); orthographic views need none.
6. **Part by part.** Build up to part n, run `tools/self_build/gates.py --part <name>`. Gates: runs, real contact, penetration within limit, no new floater, clean mesh, bbox within planned extents. Builder fixes only the named part.
7. **Fit numbers.** `tools/self_build/param_fit.py` tunes every param against silhouette IoU. Nobody hand-tunes after this.
8. **Critic loop.** `render_views.py --mode critic` produces the image set; spawn `3d-critic` with a fresh context; apply only `top_fix`; `apply_edit.py` reverts if the worst view drops by more than `self_build.revert_tolerance`. Up to `self_build.critic_cycles`.
9. Hand the best snapshot to **Optimize** with `--input <w>/snapshots/<best>/assembled.glb`: Audit (scales to `height_m`, origin bottom-centre), skip Gate 1, Cleanup (on a clean union it only welds and writes `ref_high.glb` + `cleanup.json`, which Sweep and Bake read), Sweep, Bake, then **QA**.
10. Texture: `tools/texture/project_concept.py --input <low GLB> --concept <view>=<concept image> --spec task/spec.json --work <dir>` projects the painted concept onto the low mesh from the (fitted) concept camera, then fills what no view sees: facet colour gradients, short UV inpaint, then a palette clustered from the concept (up-facing facets take the concept's top colour, back/down facets darkened). Unlit material for `hand_painted`. It reports coverage (projected / facet / inpaint / palette) and masked SSIM per concept view against `texture.ssim_min`. With one 3/4 view, more than half the texture is inferred: say so in the report, and show the back view. More concept views are the real fix.

## Optimize a model

Read `references/optimize.md` in full before starting. Summary:

1. **Ingest.** `tools/optimize/audit.py`: import, triangulate, apply transforms, metres, Y-up, weld, report manifold state, shell count and volume share, interior-face ratio, UV score, materials, rig/shape keys (`out_of_scope_rig` → stop).
2. **Gate 1 (if concept present).** `tools/optimize/gate1.py`: auto-orient, orthographic silhouette IoU per view vs concept. Below `gate1.silhouette_iou_min`: show the overlay and ask whether to continue.
3. **Branch.** Clean (manifold-ish, few shells, interior faces under `cleanup.interior_face_max_ratio`, usable UVs): keep UVs. Dirty: `cleanup.py` voxel-remeshes, UVs are gone, mark `rebake: true`.
4. **Sweep.** `tools/optimize/sweep.py`: weld, then `gltfpack` at `optimize.sweep_ratios` (Blender Decimate as fallback, warning recorded). Every level is measured by `measure.py`: worst-view silhouette IoU over `optimize.cameras` views, two-way Hausdorff as % of bbox diagonal, normal deviation p95, masked SSIM when texture kept.
5. **Pick.** Budget given: the level at budget, plus `min_pass` if budget is below the floor. `auto`: lowest level passing `optimize.floor`, cross-checked with the Kneedle knee. Record `reason`.
6. **UV and texture.** UVs kept: verify bounds, overlap, padding. Rebake: `xatlas` unwrap, then `bake.py` Cycles CPU selected-to-active (albedo; plus tangent normal for `pbr`). Resolution from texel density clamped to `[texture.min_res, texture.max_res]`.
7. **QA**, then export.

## QA gate (every path, and the review-only job)

Run all of `tools/asset_checks/` with `--input <the baked final GLB> --spec task/spec.json --out evidence/qa/<name>.json`: `mesh_check`, `uv_check`, `contact_check`, `iou_check` (if concept), `concept_coverage` (if concept + camera), `render_rig`, `screen_tris_check`, `export_check`. Read every JSON. Any `fail` blocks export.

Fix the game camera first: the first `render_rig` run without `camera.distance_m` is calibration (pixel checks are info only); copy `distance_m` and `look_at` from its `data.camera` into the spec, then every later run is a real check. See `tools/asset_checks/README.md`.

Multi-object assets: the optimize path joins every mesh into one object named after the asset (audit records the original names). Per-object spec keys (`objects`, `dimensions_m`, `expected_parts`, contacts between those objects) then report `not_checked` with that reason. Check per-object facts on the input before optimizing, and say in the report which checks ran on the input only.

Then the visual review: `render_rig` produced `sheet.png`, clay crops at the game camera, and `concept_compare.png` (only with a ConceptCam; otherwise use `render_views.py --input <final> --mode critic` overlays). Spawn `3d-critic` with the review set listed in `templates/REVIEW-RUBRIC.md`. Its verdict is the art verdict. `chưa đạt` → one fix cycle (rule 6), then re-run the gate.

When every QA JSON is pass/info and the critic approved: `python tools/finalize.py --work output/<asset> --from <baked GLB> [--min-pass <baked GLB>]`. It refuses while any QA result is `fail` or `error` and names them; otherwise it writes `final.glb` (and `final_budget.glb` / `final_min_pass.glb`).

## Report

Run `python tools/report.py --work output/<asset> --spec output/<asset>/task/spec.json`. It collects every result JSON, writes `report.json`, `contact_sheet.png` and a `report.md` skeleton; you then edit the prose. `report.md` in Vietnamese, short: entry, generator/path, faces (source → chosen, budget, min_pass), metrics (IoU min, Hausdorff, SSIM), texture (mode, source, resolution), validation errors, critic verdict with the images it cited, warnings, what was **not** checked (no engine, no device, estimated height), file paths. `report.json` mirrors it. `contact_sheet.png`: concept | clay | final, plus the error-vs-faces curve with knee and chosen marked.

Never call the result "game-ready" when engine or device checks were skipped. Say which milestone it reached.

## Ask the user, or stop

| Situation | Action |
|---|---|
| View labels unclear (left vs right) | Ask before any build or generator call |
| Concept proportions fail cross-view | Stop, report view and % |
| Self-build chosen, complexity above warn | Warn, ask whether to continue |
| Gate 1 fails on an existing model | Show overlay, ask |
| Input has armature or shape keys | Out of scope, stop |
| Budget below floor | Export both, explain |
| Critic says `chưa đạt` after 3 cycles | Stop, show all cycles, ask |
| Same gate fails twice with the same cause | Stop editing, write diagnosis, ask |
| Tool missing (gltfpack, xatlas, validator) | Use fallback, warn in report, continue |
| Paid generator wanted | Ask, show credit estimate, respect cap |

## Files

- `config.yaml` — defaults for every threshold, path and flag. `task/spec.json` overrides per task.
- `references/self_build.md` — part graph schema, attachment types, build loop, critic loop.
- `references/optimize.md` — audit, clean/dirty branch, sweep, metrics, pick, bake.
- `references/bpy_cookbook.md` — headless bmesh snippets. Read before writing modeling code.
- `references/technique.md` — choosing geometry vs normal map vs trim vs decal vs cards.
- `references/blockout.md`, `references/mesh_uv_bake.md`, `references/export_engine.md` — artist craft per stage.
- `references/research_notes.md` — the evidence behind the rules, with links.
- `templates/REVIEW-RUBRIC.md` — what the critic looks at, in what order, and how it writes a verdict.
- `templates/spec.template.json`, `templates/spec.example.rock-moss.json`.
- `agents/3d-builder.md`, `agents/3d-critic.md` — copy both into `.claude/agents/` (project) or `~/.claude/agents/` so they can be spawned as subagents by name.
- `tools/preflight.py`, `tools/report.py`, `tools/asset_checks/`, `tools/self_build/`, `tools/optimize/`, `tools/lib/`.
