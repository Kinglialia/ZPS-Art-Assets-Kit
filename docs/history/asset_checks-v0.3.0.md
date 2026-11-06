# asset_checks v0.3.0 — change history and test logs

Moved out of `src/zps-3d-artist/tools/asset_checks/README.md` in v0.9.1 to cut the context that every 3D job reads.

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
