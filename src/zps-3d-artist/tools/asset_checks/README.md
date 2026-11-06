# asset_checks v0.3.0

The measurement scripts run in Blender (tested with Blender 5.2.3 LTS). The scripts only measure and compare with the thresholds in the task spec. They do not grade the art. Keep the JSON results in the evidence folder of the task (for example `evidence/<step>/`). The spec (`task/spec.json`) is written from the approved brief. The task giver fixes the thresholds. After that, the artist does not change them. If a change is needed, ask.

Run each check on the GLB to check, with literal absolute paths (some hosts allow a command only by its text):

```bash
<BLENDER> -b --python <SKILL>/tools/asset_checks/mesh_check.py -- --input <abs GLB> --spec <abs>/task/spec.json --out <abs>/evidence/qa/mesh.json
```
Use the same form for `uv_check`, `contact_check`, `iou_check`, `concept_coverage`, `screen_tris_check`, `export_check`, and `render_rig` (add `--outdir <abs>/evidence/qa/renders`). `--input` also accepts a `.blend` file. Without the Blender app: `python3 <script> --input ...` with the `bpy` module.
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

Change history and test logs of these scripts: `docs/history/asset_checks-v0.3.0.md` in the source repository.
