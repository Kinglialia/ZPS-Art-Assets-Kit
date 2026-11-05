# asset_checks v0.3.0

The measurement scripts run in Blender (tested with Blender 5.2.3 LTS). The scripts only measure and compare with the thresholds in the task spec. They do not grade the art. Keep the JSON results in the evidence folder of the task (for example `evidence/<step>/`). The spec (`task/spec.json`) is written from the approved brief. The task giver fixes the thresholds. After that, the artist does not change them. If a change is needed, ask.

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
T=<folder of this skill>/tools/asset_checks
$B -b asset.blend --python $T/mesh_check.py       -- --spec task/spec.json --out ev/mesh.json
$B -b asset.blend --python $T/uv_check.py         -- --spec task/spec.json --out ev/uv.json
$B -b asset.blend --python $T/contact_check.py    -- --spec task/spec.json --out ev/contact.json
$B -b asset.blend --python $T/iou_check.py        -- --spec task/spec.json --out ev/iou.json
$B -b asset.blend --python $T/concept_coverage.py -- --spec task/spec.json --out ev/coverage.json
$B -b asset.blend --python $T/screen_tris_check.py -- --spec task/spec.json --out ev/screen_tris.json
$B -b asset.blend --python $T/render_rig.py       -- --spec task/spec.json --out ev/render.json --outdir ev/renders
$B -b asset.blend --python $T/export_check.py     -- --spec task/spec.json --out ev/export.json
```
If you have no Blender app: `python3 $T/<script>.py --input asset.blend --spec ... --out ...` (module `bpy`).
Paths in the spec (concept, export) are relative to the folder that holds the spec file. The scripts do not overwrite the .blend file.

Source of thresholds: the spec first. Some checks (marked below) take a default from `config.yaml` when the spec lacks the key. The note of such a check then says `source: config_default (<key>)`. If the spec lacks the key and the config also lacks it, the result is `info` or `not_checked`. The script does not set a threshold itself.

| Script | Measures | Notes |
|---|---|---|
| mesh_check | tris/material against the budget, `budget_use` (fails when below `budget.min_tris_ratio`), size, pivot, closed mesh (`expect_closed`), part count (`expected_parts`), degenerate faces, flipped parts, distance to the floor. v0.3: vertex count after export, vertex split ratio, n-gons, hidden faces, duplicate vertices, flipped faces, smooth edges > 90° | Measured on the mesh after modifiers. See the v0.3 table |
| uv_check | islands, UVs outside 0–1, overlap, island gap (px), texel density by area. v0.3: default padding by resolution, global texel density in px/m and per island, hard edges must be UV splits (pbr) | Tolerance about 1 px |
| screen_tris_check (new) | small triangles (< `min_px_area` px²) and sliver triangles at the game camera, with `screen_tris.png` | Camera not fixed → info |
| contact_check | gap/sink between declared pairs, ratio of the bottom that touches the floor | v0.2: points inside the mesh use ray parity (correct for a closed mesh); intersecting triangles → distance 0; `vertex_depth_lower_bound_m` considers only vertices, so you must view the image; for allowed nesting, record `max_penetration_m` with a reason |
| iou_check | silhouette IoU against the concept, from the `ConceptCam` camera; per object when the spec has `iou.polygons_from` (points to `m1.json` or a file of the same form) | Threshold `iou.min_iou` (default 0.90). Image `iou_diff.png`: red = missing compared with the concept, blue = extra |
| concept_coverage | the part of the area visible at the game camera that comes from drawn concept faces: faces that face the `ConceptCam`, are not occluded, and are inside the concept frame | Risk information only, unless the task sets `min_visible`. The camera reads `fov_v_deg`/`ortho_scale` like render_rig |
| render_rig | game frame at real size, 4 angles × clay/albedo/lit/checker, `sheet.png` | v0.2: with a fixed camera (`distance_m` or `ortho_scale`), the px check is meaningful; otherwise this is calibration mode and the checks are info only |
| export_check | exports a GLB (or checks an existing GLB with `skip_export`), glTF-Validator, whether the material has `KHR_materials_unlit` (`expect_unlit`), re-imports and compares figures. v0.3: file size, vertex count in the file, height after import (up axis, unit), bottom-center pivot of the file | Vertex color in the file does not prove that the engine material uses it |

## New checks in v0.3
| Check (script) | Measures what | Threshold |
|---|---|---|
| `<obj>.exported_vertices` (mesh) | vertices the GPU receives: the number of distinct sets (material, vertex, normal by angle, all UV layers) on the loops of the mesh after modifiers, the way io_scene_gltf2 splits vertices. UV seams, sharp/flat edges, and material boundaries all split vertices | `budget.max_vertices_exported`; if missing, config `budgets.max_vertices_exported` (65534, 16-bit index) |
| `<obj>.split_vertex_ratio` (mesh) | exported vertices / source vertices | `mesh.max_split_vertex_ratio`; if missing → info, with a note when > 2× |
| `<obj>.ngons` (mesh) | faces with > 4 corners (the exporter triangulates them, and you cannot control the split direction) | `mesh.max_ngons`; if missing → info |
| `<obj>.hidden_face_ratio` (mesh) | ratio of triangles that no ray from outside reaches: rays are cast from the face center and 4 mid-points between center and corners, in 64 directions (BVH of all target objects). Two-sided: a face that points away still counts as seen. This is an estimate | `mesh.max_hidden_face_ratio`; if missing → info |
| `<obj>.duplicate_verts` (mesh) | vertices that have another vertex of the same object within `mesh.duplicate_distance_m` (default 1e-4 m) | `mesh.max_duplicate_verts`; if missing → info |
| `<obj>.flipped_faces` (mesh) | on each closed part: a ray from the face along the normal (and one oblique ray) crosses that part an odd number of times → the normal points inward. Catches odd flipped faces that `inverted_parts` (negative volume) misses | > 0 is a fail (like `inverted_parts`); if there is no closed part → not_checked |
| `<obj>.smooth_edges_over_90` (mesh) | smooth edges whose two normals form an angle > 90° (Arm: smooth angle < 90°, mark sharp) | `mesh.max_smooth_edges_over_90`; if missing → info; if all faces are flat → not_checked |
| `total.materials` (mesh) | exists since v0.2 | `budget.max_materials_total`; if missing → info, with the config value `budgets.max_materials` |
| `screen.small_tri_ratio` (screen_tris) | ratio of front-facing triangles, inside the frame, with area < `min_px_area` px² at the game camera. A triangle tilted more than 75° from the view direction (`grazing_deg`) does not count: every curved surface has them at the edge | `min_px_area`: `screen_tris.min_px_area` → `validate.sliver_min_px_area` (spec) → config `validate.sliver_min_px_area` (10). Ratio: `screen_tris.max_small_ratio`; if missing → info |
| `screen.thin_tris` (screen_tris) | triangles whose height on the longest edge is < `thin_max_px` (1) and whose longest edge is > `thin_min_long_px` (50). This also covers the rule "shortest edge < 1 px" | `screen_tris.max_thin`; if missing → info |
| `<obj>.min_island_gap_px` (uv) | same as v0.2 | `uv.min_padding_px`; if missing → config `texture.padding_px_by_res[uv.resolution]` (a resolution that is not in the table: infer from the nearest entry by ratio) |
| `<obj>.texel_density.global` / `.islands` (uv) | global px/m = √(UV area in px / real area); per island: min, max, max/min. An island < 0.5 % of the area is only listed | `uv.texel_density_px_per_m` ± `uv.density_tolerance` (ratio); if missing → info, with the config value for reference |
| `<obj>.hard_edges_without_uv_split` (uv) | hard edges (marked sharp, or next to a flat face, with 2 normals that differ by > 1°) whose 2 faces share UVs. Read from the UV coordinates, not from the seam flag | `style: pbr` → > 0 is a fail; `hand_painted` or not stated → info |
| `gltf_validator.errors` / `.warnings` / `.infos` (export) | Khronos glTF-Validator: `export.validator` → `gltf_validator` on PATH → `node gltf_validate.mjs` (the npm package `gltf-validator` is a library and has no CLI; install with `npm i -g gltf-validator`) | errors > 0 fail; warnings and infos are info with the error codes; if not found → not_checked |
| `file.size_mb` (export) | GLB file size | `validate.max_file_size_mb`; if missing → config `validate.max_file_size_mb` |
| `file.vertices.<mesh>` (export) | sum of `count` of the POSITION accessors in the file, per mesh | same as `exported_vertices` |
| `file.height_m` (export) | bbox height after re-import (glTF Y-up → Blender Z). An export that is Z-up or in cm shows up here | `height_m` ± `dimensions_tolerance`; if missing → info |
| `asset.pivot_bottom_center` (export) | bottom-center of the asset bbox after import, compared with the file origin; each object is info | when `pivot: bottom_center`: every axis ≤ 0.01 m |
| `file.reimport` (export) | whether the file can be imported again (before, the script died and wrote no JSON) | import error → fail |

Why sliver is a separate script and not part of render_rig: it needs no render (it projects triangles with the camera matrix and runs in under 1 s). It gives a pass/fail number that is quick to run again. render_rig is a tool for viewing images and is the slowest. The two scripts share `ac_common.game_camera`/`place_camera`. In calibration mode both solve for the same distance (tested: 3.537 m and 4.2939 m).

## Game camera
Every script builds the camera with `ac_common.game_camera` from `spec.camera`: `fov_v_deg` (vertical FOV, taken from the engine) or `lens_mm`; ortho needs `ortho_scale`; `distance_m`, `look_at`, `azimuth_deg`, `elevation_deg`. The camera is fixed when a perspective camera has `distance_m` or an ortho camera has `ortho_scale`. If they are missing, the pixel check and the coverage check are info only.

## Lock the game camera
The first time you run `render_rig` without `distance_m`, the script solves the distance so that it matches `target_px_height` and writes it to `data.camera`. Copy `distance_m` and `look_at` into the spec. From then on, every render uses the same camera, and the px check is a real check.

## Changes in v0.3.0
- `mesh_check`: added 7 checks in the table above; `total.materials` records the config value when the spec lacks a threshold; data has `materials_used` (materials that have faces using them).
- `uv_check`: default padding from the config; global and per-island texel density; hard edge ↔ UV split.
- `screen_tris_check.py` is new: small/sliver triangles at the game camera, image `screen_tris.png`.
- `export_check`: validator through `gltf_validate.mjs` (node), file size, vertex count in the file, height/up axis, pivot of the file; a broken file no longer kills the script.
- `ac_common`: `TOOL_VERSION` 0.3.0; `config_value`, `threshold`, `source_note` (reads `config.yaml` through `tools/lib/common.load_config`), `fibonacci_dirs`, `calibrate_distance`.
- New spec keys (optional): block `mesh` {`max_split_vertex_ratio`, `max_ngons`, `max_hidden_face_ratio`, `duplicate_distance_m`, `max_duplicate_verts`, `max_smooth_edges_over_90`}, `budget.max_vertices_exported`, `screen_tris` {`min_px_area`, `max_small_ratio`, `max_thin`, `thin_max_px`, `thin_min_long_px`, `grazing_deg`}, `uv.texel_density_px_per_m`, `uv.density_tolerance`, `validate.max_file_size_mb`, `validate.sliver_min_px_area`; the existing `height_m` and `style` are used.

## Changes since v0.1.0
- `render_rig`: fixed camera. v0.1 solved the camera by itself, so the 250px check always passed (INC-005 test rock-moss-01).
- `contact_check`: ray parity replaces the nearest-face normal. v0.1 wrongly reported a sink of 1.71 m (INC-007). `no_penetration` now also checks vertices that lie inside the other object.
- `export_check`: `skip_export`; paths are relative to the spec (INC-017).
- Added `iou_check` and `concept_coverage`; `ac_common` added `concept_mask` and `render_alpha`.

Test result on the M1 rock cluster of the v0.2 version before the files were lost (cloud, Blender 5.2.3, not yet run again on the rebuilt version): 7/7 scripts ran; IoU 0.978 (RockS 0.992, RockL 0.969); coverage at the game camera 0.687, side 0.024, back 0.0; sink RockS–RockL 0.136 m (v0.1 reported 1.08 m).

## Check of the rebuilt version (2026-11-03, cloud, bpy 5.2.3, test scene of 2 spheres — not a real asset)
- All 9 scripts ran on the same sample spec.
- `budget_use` 0.107 < 0.3 → fail. `target_px_height` calibration → info. After you copy `distance_m`/`look_at` into the spec → pass at 250 px.
- Two nested masses: `no_penetration` without `max_penetration_m` → fail. With 0.15 m → pass (deepest vertex 0.095 m).
- `iou_check` with a concept that is the silhouette of the scene itself: 0.9999. Per object through `polygons_from` ≥ 0.996.
- `export_check`: material Background → the GLB has `KHR_materials_unlit`. `expect_unlit: false` → fail. `skip_export` reads an existing GLB.
- `concept_compare.png` matches the concept position. Not yet run: glTF-Validator, Mac, Godot, a real rock concept.


## Check of v0.3.0 (2026-11-03, cloud container, Python 3.13 + module bpy 5.2.3, node 22, npm package gltf-validator 2.0.0-dev.3.10)
The test scenes were built with bpy (not real assets). The specs were written from `spec.template.json`:
- (1) `Barrel`: 832 tris, 1 material, hand UVs (3 islands, gaps > 16 px), bottom-center pivot, height 0.8 m, smooth sides, flat lid, sharp lid rim = UV split.
- (2) `BadCrate`: 216 tris, 2 materials, 5 n-gons, a closed box inside, knobs not welded (24 duplicate vertices), 2 flipped faces, a smooth fin with a 140° angle, a 2 mm strip (sliver), 12 bolts of 6 mm (small triangles), one continuous UV that is a function of position (no split at hard edges, parts overlap in UV), pivot at a corner, export `yup: false`.

Camera: run `render_rig` in calibration mode at 400 px, copy `distance_m`/`look_at` into the spec, then run all scripts again with the fixed camera.

| Check | (1) Barrel | (2) BadCrate |
|---|---|---|
| exported_vertices | 495 ≤ 65534 (config_default) pass | 406 > 300 (spec, to test the fail branch) fail |
| split_vertex_ratio | 1.184 ≤ 2 pass | 2.57 fail |
| ngons | 0 pass | 5 fail |
| hidden_face_ratio | 0.0 pass | 0.194 (42/216 tris: inner box, faces against the body) fail |
| duplicate_verts | 0 pass | 24 fail |
| flipped_faces | 0 / 448 pass | 2 / 95 fail (`inverted_parts` still passes: the volume is positive) |
| smooth_edges_over_90 | 0 pass | 3 fail |
| total.materials | 1 pass | 2 fail |
| screen.small_tri_ratio | 0 / 392 pass (8 oblique rim triangles excluded) | 48 / 106 = 0.45 fail |
| screen.thin_tris | 0 pass | 4 (strip) fail |
| min_island_gap_px (config 8 px) | > 16 pass | 1 fail |
| texel_density.global / .islands (540 ± 20 %) | 531.1 pass / 528.6–539.6 pass | 523.4 pass / min 104.8 fail |
| hard_edges_without_uv_split | 0 / 64 pass | 188 / 188 fail |
| gltf_validator.errors | 0 pass | 0 pass (valid file); GLB broken on purpose: 4 errors (ACCESSOR_TOO_LONG…) fail |
| file.size_mb | 0.021 ≤ 5 (config_default) pass | 0.016 > 0.01 (spec, to test the fail branch) fail |
| file.vertices | 495 pass | 406 fail |
| file.height_m | 0.8 pass | 0.406 instead of 1.25 (Z-up) fail |
| asset.pivot_bottom_center | [0,0,0] pass | [0.35, −0.625, −0.006] fail |

- The vertex count estimated by `mesh_check` matches the real vertex count in the GLB (validator `totalVertexCount` and accessor): 495 = 495, 406 = 406.
- Other branches: no node on PATH → `gltf_validator` not_checked; spec lacks the `mesh`/`screen_tris`/density block → info; `style: hand_painted` → info; `uv.resolution` 768 → padding 6 px inferred from 1024; broken GLB → `file.reimport` fail and the JSON is still written.
- Regression: `iou_check` (concept = silhouette of the scene itself) 1.0; `concept_coverage` 0.929; `contact_check` pass; `render_rig` pass at 400 px.
- Opened `sheet.png` of both scenes and `screen_tris.png`: (2) yellow strip, 12 red bolts; (1) no red or yellow.
- Not yet run: the Blender app (module bpy only), macOS, the native `gltf_validator` CLI (only through node), a real asset, a large mesh (hidden faces use Python rays: 64 directions × up to 5 points for hidden faces, which can be slow with > 50k faces).
