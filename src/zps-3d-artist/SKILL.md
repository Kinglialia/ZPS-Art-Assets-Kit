---
name: zps-3d-artist
description: "Build, optimize or technically review static 3D game props and environment pieces from concepts or existing models; covers mesh, topology, UV, bake and GLB export for the project's engine. Use for modeling, polygon reduction or mesh QA (\"dựng model\", \"model từ concept\", \"giảm mặt\", \"giảm poly\", \"optimize poly\", \"low poly\", \"budget mặt\", \"kiểm model\", \"review model 3D\"). Not for 2D drawing, concept art or standalone texture painting (zps-texture-artist)."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 3D Artist
Work within the AD brief, chosen direction, camera and supplied technical limits. Static triangle-mesh props are supported. Rigging, animated characters, cloth and quad retopology are outside this toolset; identify the unsupported part and continue independent supported work.

## Start with the requested output

- New model from concept: [self-build](references/self_build.md).
- Reduce/clean an existing model: [optimize](references/optimize.md).
- Both paths: [pipeline](references/pipeline.md) holds setup, intake, the QA gate, finalize and the report.
- Review only: run relevant checks and inspect renders, without model edits. See [QA tools](tools/asset_checks/README.md) and [review rubric](templates/REVIEW-RUBRIC.md).

Reuse the current brief. Write task/spec.json from supplied dimensions, camera, budget and texture intent. Record defaults from config.yaml as provisional, not universal standards. Resolve only missing facts that affect the chosen path; do not repeat approval already granted. Never relax a threshold merely to pass. Unknown left/right conventions or conflicting concept views require clarification for the affected geometry.

## Build and verify

Use an asset workspace with immutable input, task/spec.json, versioned work, evidence and deliverables. Open concept images; numeric dimensions and mesh metrics come from measured files, not visual guesses. Use clay/normals for shape and textured renders for surface. Record the exact version/view inspected.

Run only necessary setup within permission: scripts may require Blender/bpy, Pillow, numpy, xatlas or other dependencies. [Pipeline setup](references/pipeline.md) and preflight identify capabilities. Package installation does not install dependencies or invoke paid generators. Existing provider/asset authorization applies; stop at its budget. Generator adapters remain unconfigured unless explicitly set up.

Prefer one build path and one writer per asset. A separate builder/critic is optional when delegation is authorized; [builder brief](agents/3d-builder.md) and [critic brief](agents/3d-critic.md) are task prompts, not Claude agent registration files. Otherwise perform and label self-review. Do not claim independence or owner approval. Missing required independent review leaves that milestone pending without preventing a clearly labeled working preview.

Preserve fixed dimensions when fitting cameras or parameters. Check geometry against the spec; inspect silhouettes and internal forms at the target scale. Repeated failure requires diagnosis rather than endless retries. Keep/revert edits using observed results and the assigned repair budget. See [craft](references/technique.md), [blockout](references/blockout.md), [mesh/UV/bake](references/mesh_uv_bake.md) and [export](references/export_engine.md) only for the stage being performed.

Texture-only work routes to [Texture Artist](../zps-texture-artist/SKILL.md); see Texture by default below. Mesh, UV layout and high-to-low baking stay here. For projection, lock the mesh/UV/camera version and exchange paint views; any geometry/UV change invalidates affected texture evidence. Use a single writer at a time. A shader/material map request does not automatically authorize topology edits.

## Texture by default

A finished model ships with a texture. Skip the texture step only in these cases:
- The caller says that the model needs no texture.
- After retopo or optimize, the existing texture still works: the UVs were kept, or the transfer bake reaches `texture.ssim_min` and shows no visible seam or blur at the game camera.

In all other cases, call the Texture Artist skill of the runtime that you run in. Send part A of the [3D ↔ Texture handoff](../.art-production-support/templates/3d-texture-handoff.md). If the caller named a texture method, pass it on. If nobody named one, Texture Artist selects it.

UV and materials before the handoff:
- By default, unwrap unique, non-overlapping UVs and keep one material. This suits most texture methods and costs one draw call on mobile.
- Call [Texture Planning](../zps-texture-planning/SKILL.md) before you unwrap if a sign shows that the texture needs special UVs: the caller or the Art Style document names tileable/trim, pixel texture or vertex color, or the asset is an environment or modular piece. Unwrap to the method that Planning returns.
- If the known method allows overlap (palette atlas, intended mirror), you may overlap. Set `uv.allow_overlap: true` in the spec with `_allow_overlap_reason`, and record it in part A.
- Give region information instead of material slots: the material label of each part and the `parts_<view>.png` renders. Split material slots in Blender for one model only when Texture Planning asks for a different shader per region.
- If Texture Artist asks for UV changes or slot splits, expect one combined request.

A texture that the 3D pipeline made (concept projection or transfer bake) is a temporary pass. Label it as temporary in part A. Texture Artist decides to keep it, fix it or replace it.

When part B comes back, you own the final asset. Assign the maps to the material slots, export the final GLB, and run the QA gate again on that file. Copy the material setup notes from part B into the report for the person who imports the asset into the engine.

## Deliver the actual milestone

Read relevant QA JSON and open final renders. A failed mandatory geometry check blocks an accepted final export; diagnostic previews must be labeled and separated. If no valid mesh meets the requested budget, report the gap and a valid minimum alternative rather than labeling the failing candidate final. Required not_checked is pending, not pass.

Use finalize.py only after the required review milestone; it checks recorded technical results, not artistic approval. report.py produces a report to inspect and complete, not an automatic acceptance verdict. State source/chosen tris, budgets, measurements, texture sources, inferred unseen surfaces, missing checks and source/output paths. Only claim engine/device validation if performed.

For requested learning capture, use [Art Learning](../zps-art-learning/SKILL.md) to ingest the measured result and separately record actual reviewer feedback. Do not modify skill thresholds or code automatically.

[AD routing](../.art-director-support/workflows/art-direction.md) selects the next capability without requiring the full pipeline.
