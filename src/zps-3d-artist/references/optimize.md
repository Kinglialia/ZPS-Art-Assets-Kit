# Optimize: existing model → fewest faces that still match

Input: a GLB/FBX/OBJ from any source (Meshy, Tripo, Hunyuan3D, an artist, a scan, the self-build path). Output: a mesh at a given budget, or the fewest triangles that still pass the floor, with no mesh errors.

Why this shape (sources in `research_notes.md` §3):
- meshoptimizer is the strongest open simplifier; its Python bindings are third-party and lag, so call the `gltfpack` CLI. Blender Decimate is the fallback.
- Unwelded vertices and dense UV seams make simplification stall far above target. Weld first. AI meshes are seam-heavy: either keep UVs and accept stopping early, or collapse across seams (`-sp`) and rebake.
- Dirty meshes (inner faces, overlapping shells, non-manifold) only get fixed reliably by voxel remesh, which destroys UVs and thin features. So the pipeline branches after an audit.
- No published "visually lossless" threshold exists for mobile. The floor below is a starting point: projected two-way Hausdorff ≤ 1 px at the prop's largest on-screen size, worst-view silhouette IoU ≥ 0.99 over 12 views. Calibrate on real assets.

Work dir: `output/<asset>/work/optimize/`.

## 1. Audit — `tools/optimize/audit.py`

```
<BLENDER> -b --python <SKILL>/tools/optimize/audit.py -- --input input/model.glb --work <w> --spec task/spec.json
```
Imports, rejects armature/shape keys (`out_of_scope_rig`), triangulates, applies transforms, converts to metres, scales to `height_m` when given (records factor), writes `<w>/ingest.glb`. Reports: tris, verts, bbox, diag, manifold edges ratio, boundary edges, shells (count, face share, bbox share), interior-face ratio (faces never hit by rays from 64 exterior directions), degenerate faces, flipped-normal estimate, UV score (layer present, share of area in 0–1, overlap ratio, island count per 1k faces), materials, textures. Decides `branch: clean | dirty` with reasons.

## 2. Gate 1 — `tools/optimize/gate1.py` (only with concept)

Tries 4 front directions (±X, ±Y), then 24 if the best is weak; picks the highest front IoU; writes `orientation` and rotates `ingest.glb` → `oriented.glb`. Reports per-view IoU for every concept view present and an overlay PNG per view. Below `gate1.silhouette_iou_min`: show the overlays, ask the user.

## 3. Cleanup — `tools/optimize/cleanup.py`

Always: merge by distance (`merge_distance_ratio` × diag), delete loose shells below `loose_part_min_ratio`, delete interior faces found by the audit (clean branch only, when the ratio is small), recalc normals, fill holes ≤ `max_hole_edges`, origin bottom-centre. Dirty branch (or `voxel_remesh.mode: always`): solidify open sheets if `solidify_thin`, voxel remesh at `resolution` voxels on the longest edge, keep `pre_remesh.glb` as the bake source, write `remeshed: true`, `rebake: true`. Output `ref_high.glb` — the only reference for every later comparison.

## 4. Sweep — `tools/optimize/sweep.py`

For each ratio in `optimize.sweep_ratios` (or `--budget N` → ratio = N / ref tris, plus the sweep below it to find `min_pass`):
- `gltfpack -i ref_high.glb -o level_<r>.glb -si <r> -se <gltfpack_error> -noq` (+ `-sp` when `rebake` and `permissive_when_rebake`, + `-slb` if `lock_border`). Note `-se`: gltfpack may stop above target; record the achieved count.
- If gltfpack is missing or fails, Blender Decimate COLLAPSE at the same ratio, `warnings += engine_fallback`.
- `measure.py` on every level.
At the chosen level, also run the other engine and keep the better (worst-view IoU, then Hausdorff). `--calibrate` exports and renders every level without choosing.

## 5. Measure — `tools/optimize/measure.py`

```
tools/.deps/venv/bin/python tools/optimize/measure.py --ref ref_high.glb --cand level_0.1.glb --out <w>/measure/level_0.1.json [--views 12] [--raster 512] [--screen-px 400]
```
Pure Python (trimesh + numpy). Silhouettes by orthographic triangle rasterisation from `cameras` directions on a sphere (including above and below), same framing for ref and candidate; IoU per view, worst view. Two-way Hausdorff and mean (surface samples → closest point) as fraction of bbox diagonal and projected to px (`× screen_px / bbox_height`). Normal deviation p95 between candidate samples and nearest ref face. Masked SSIM is added by `bake.py` when texture exists.

## 6. Pick

- Budget: the level at budget is `final_budget`; if it fails the floor, the lowest-ratio level that passes is `final_min_pass`. Export both, explain the gap. gltfpack often stops above the budget; sweep then retries with `-se 1`, then Blender, so `final_budget` is never over budget.
- Auto: the lowest tri count passing every floor metric. When even the last ratio passes (common after remesh), sweep keeps halving below the list down to `sweep.min_tris`, then bisects `sweep.refine_steps` times between the last fail and first pass.
- Engines: at each chosen level the other engine also runs. If it wins (worst IoU, then Hausdorff; with kept UVs, texture error p95 first), the search continues downward with that engine. Blender Decimate tends to smear kept UVs; the texture-error metric catches it.
- Knee: Kneedle (`kneed`, convex, decreasing) on the Pareto front of (log tris, 1 − worst IoU) across both engines. If the knee is below the floor-passing level, the floor wins; record both. At 512 px raster, IoU plateaus near 0.994 even for close geometry, so Hausdorff px is usually the limiting metric and the knee can be weak.
- Write `sweep.json`: `curve[]`, `knee_tris`, `chosen_tris`, `budget_tris`, `min_pass_tris`, `engine_winner`, `reason`; and `curve.png`.

## 7. UV and texture — `tools/optimize/bake.py`

- **keep_uv** (clean branch, UVs usable): carry original UVs and textures. Run `uv_check` for bounds, overlap and padding.
- **rebake**: `xatlas` unwrap (deterministic; Blender Smart UV Project is not), padding from `texture.padding_px_by_res`. Resolution = next power of two (rounded up) of √(surface area m²) × `texel_density_px_per_m` / √(UV occupancy), clamped to `[min_res, max_res]`. Blender Cycles CPU bake selected-to-active from `pre_remesh.glb` (or `ref_high.glb`), `max_ray_distance` = `max_ray_distance_ratio` × diag, margin `bake_margin_px`. `albedo` always; `albedo_normal` adds tangent-space normal (OpenGL convention) for `pbr`. Single material.
- **check**: render textured low and high from the same 6 cameras, masked SSIM, take the min; below `texture.ssim_min` the result carries `next_action`. bake.py does not retry by itself: you step up one sweep level (the next passing level in `sweep.json`) and rerun bake.
- `hand_painted` style: forbid mirrored or overlapping UVs where baked light differs.

## 8. Then QA

Run the full [QA gate](pipeline.md#qa-gate-every-path-and-the-review-only-job) on the baked level, then `tools/finalize.py` writes `final.glb` only if every QA result present is pass/info and `mesh_check` ran (see the finalize scope note in the QA gate). Sweep repairs each level lightly (zero-area faces, winding) and rejects levels with degenerate faces or more non-manifold/inconsistent edges than the reference, so an invalid level is never chosen.

## Pitfalls

- Weld before simplifying; the audit shows `weld_ratio`.
- `gltfpack -sa` (sloppy) merges nearby shells and ignores seams: only for far LODs, never LOD0.
- Open3D decimation drops UVs; gltf-transform `simplify` ignores UVs in its error metric. Do not substitute them.
- Voxel remesh deletes thin features (wires, blades). If the audit shows thin parts, raise `resolution` or keep the clean branch and accept more faces.
- Blender headless: `bpy.context.window` is None; avoid UI ops, use `temp_override` where an op is unavoidable; bake needs the target image node active on the low-poly material.
- PyMeshLab is GPL3 and MeshFix is non-commercial; this pipeline does not depend on either.
- Deleting interior faces on the clean branch leaves boundary edges where hidden parts met (e.g. a tap entering a barrel). `mesh_check` with `expect_closed: true` then fails. That is a spec decision: show the user the boundary count from `cleanup.json` and ask whether to set `expect_closed: false` with a `_reason`, or keep the hidden faces. Never flip it silently.
- Speed: measuring a level against a remeshed reference of ~500k tris takes ~40 s; a full dirty auto sweep can take ~15 min. Run it in the background and tell the user.
- An existing model with clean geometry but unusable UVs stays on the clean branch; only its UV plan becomes `rebake`.
