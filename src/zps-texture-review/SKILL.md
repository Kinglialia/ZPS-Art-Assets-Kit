---
name: zps-texture-review
description: "Review textures on a 3D model: seams, texel density, channels and color space, normal convention, baked light, mip and compression, style fit; find if a fault comes from map, UV or lighting. Use for texture review (\"kiểm texture\", \"texture bị seam\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Review

**Not for:** 2D sprites and UI (zps-2d-review); mesh and topology checks (zps-3d-artist); concept or cross-domain critique (zps-artistic-critique). Self-checks stay in zps-surface.

Follow the [shared rules](../.art-production-support/rules/art-operation.md). Review does not need an image-generation tool, but you must be able to open the real image/render. Judge a texture **on the model**. A flat atlas that looks good does not prove that the texture passes.

## Intake

Collect:
- Artifact/version of the **texture and the model/UV/material** you are viewing.
- Brief, Bible/style sheet version.
- Texture method (hand-painted, flat/vertex color, PBR, tileable/trim, pixel, projection...). Take it in this order:
  1. A specific requirement from the caller (AD, user, Art Style document).
  2. The method that the Texture Artist recorded when it chose the method itself (part B of the [3D ↔ Texture handoff](../.art-production-support/templates/3d-texture-handoff.md)).
  3. If you cannot find it, infer it from the texture, record it as an assumption, and record the issue "method not recorded".
- If Texture chose the method itself, also check that the choice fits the brief and the model.
- Map contract (channels, color space, size, normal convention), if there is one.
- Stage (test sample / final).
- Target camera, distance and lighting.
- The renderer of the image that was sent (Workbench, Eevee, Cycles or the real engine).

If the on-model render is missing and you cannot render it yourself, you can only comment on the atlas. Record the on-model part as `not_checked`. The verdict cannot be `meets_checked_criteria` for on-model criteria.

## Workflow

Follow the [review procedure](../.art-production-support/shared/review-procedure.md). The texture parts:
- Step 1: prefer the angle and camera distance of the game. When Blender/Pillow is available, run `render_model.py` (checker/clay/textured), `inspect_model.py` and `preview.py` yourself, to get evidence without asking again. Do not edit the model or the texture.
- Step 3: run the texture specialist checks below by method and risk. Details are in [texture checks](references/texture-checks.md).
- Diagnose before you propose a fix. The same symptom can come from the map, UV, normal/tangent, shader or lighting. If no evidence tells the causes apart, record the cause as a hypothesis and propose one cheap check that tells them apart.
- In `region`, write the area on the model and, when known, the area/cell on the atlas. If the mesh/UV changed between two versions, record that the old evidence is no longer valid for the affected areas.

## Texture specialist checks (choose by method and risk)

| Group | What to check |
|---|---|
| Seam | Seam shows at the game angle/distance; color, value or stroke-direction mismatch across a UV cut; seam shows only at low mip |
| Texel and scale | Texel density between pieces that are seen side by side; priority areas have enough resolution; grain/stroke scale is uniform across areas of the same material |
| Follows the form | Detail, strokes and color transitions follow the form of the model, not the UV edge/island; no paint mark cuts across a form |
| Light in the map | Lit/PBR: no baked highlight, fixed cast shadow or heavy AO in the albedo. Unlit/hand-painted: the painted-in light has the same direction as the convention and is consistent between pieces |
| Map contract | All channels as in the contract; correct color space (albedo sRGB; roughness/metal/AO/normal linear); normal follows the convention of the target engine (Godot: OpenGL Y+); channel packing in the correct order |
| Repeat and tiling | Prominent mark repeats over many cells; trim/decal has the correct direction, scale, edge and blending |
| Far view and compression | At the farthest distance: speckle, blur or banding from mip/compression; alpha/cutout keeps its shape |
| Mirror/stack | Unique detail (text, marks, logo) is flipped or repeated because of UV mirror/stack. It is a fault only when that area needs its own information |
| Readable materials | Material areas can be told apart at game size; detail follows visual hierarchy and does not cover every surface evenly |

## When Surface calls this skill

Surface calls this skill before it delivers a final or a set of models. A single test sample or a small fix needs only Surface's self-check. Run it as in the review procedure; the reviewer receives the on-model renders, the maps, the method and the map contract. Surface fixes the map; the 3D Artist fixes UV, mesh or bake.

## Output

Use the output order of the review procedure. Put first the method used as the check standard, and its source. In the priority issues, say whether you suspect the map, UV, lighting or shader. In the next steps, Surface fixes the map and the 3D Artist fixes UV/mesh/bake. Also state the renderer: a Blender image does not prove the result in the engine.

## Gotchas

- A good-looking flat atlas or paint view does not prove that the texture passes on the model. Always ask for, or make, a render on the model.
- Black or wrong-color fault: check color space, alpha, normal and material link before you ask for a repaint. Seam fault: check UV/tangent/bake/padding before you blur.
- A before/after comparison is valid only with the same camera, lighting, exposure, tone mapping and import.
- A still image does not prove animation, topology or performance. Do not infer texture resolution from a render image.
- Mesh, UV layout and high→low bake issues belong to the 3D Artist.

