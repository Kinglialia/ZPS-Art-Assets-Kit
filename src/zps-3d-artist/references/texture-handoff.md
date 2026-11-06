# Texture by default, and the handoff to Texture Artist

Read this file in the Self-model path and the Optimize job. The Meshy, Tripo and ZPS 3D Gen paths get their texture from the service; they read this file only when they call Texture Artist.

Texture-only work goes to [Texture Artist](../../zps-texture-artist/SKILL.md). Mesh, UV layout and high-to-low baking stay in 3D Artist. A shader or material-map request does not authorize topology edits.

## When the model needs a texture

A finished model ships with a texture. Skip the texture step only in these cases:
- The caller says that the model needs no texture.
- After retopo or optimize, the existing texture still works: the UVs were kept, or the transfer bake reaches `texture.ssim_min` and shows no visible seam or blur at the game camera.

In all other cases, call the Texture Artist skill of the runtime that you run in. If Concept Views made views of this asset, list them in part A as the reference for the hidden sides; `project_concept.py` also takes several views (`--concept front=… --concept back=…`). Send part A of the [3D ↔ Texture handoff](../../.art-production-support/templates/3d-texture-handoff.md). If the caller named a texture method, pass it on. If nobody named one, Texture Artist selects it.

## UV and materials before the handoff

- By default, unwrap unique, non-overlapping UVs and keep one material. This suits most texture methods and costs one draw call on mobile.
- Call [Texture Planning](../../zps-texture-planning/SKILL.md) before you unwrap if a sign shows that the texture needs special UVs: the caller or the Art Style document names tileable/trim, pixel texture or vertex color, or the asset is an environment or modular piece. Unwrap to the method that Planning returns.
- If the known method allows overlap (palette atlas, intended mirror), you may overlap. Set `uv.allow_overlap: true` in the spec with `_allow_overlap_reason`, and record it in part A.
- Give region information instead of material slots: the material label of each part and the `parts_<view>.png` renders. Split material slots in Blender for one model only when Texture Planning asks for a different shader per region.
- If Texture Artist asks for UV changes or slot splits, expect one combined request.

For concept projection, lock the mesh, UV and camera version, and exchange paint views. Any geometry or UV change invalidates the affected texture evidence. Use one writer at a time.

A texture that the 3D pipeline made (concept projection or transfer bake) is a temporary pass. Label it as temporary in part A. Texture Artist decides to keep it, fix it or replace it.

## When part B comes back

You own the final asset. Assign the maps to the material slots, export the final GLB, and run the QA gate again on that file. Copy the material setup notes from part B into the report for the person who imports the asset into the engine.
