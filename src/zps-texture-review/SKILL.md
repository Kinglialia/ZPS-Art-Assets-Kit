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

If there is no Bible, review against the brief. Record the project-fit level as provisional.

If the on-model render is missing and you cannot render it yourself, you can only comment on the atlas. Record the on-model part as `not_checked`. The verdict cannot be `meets_checked_criteria` for on-model criteria.

## Workflow

1. Open the render. Look at the whole image, then inspect the area that explains your judgment, then look at the whole image again. Prefer the angle and camera distance of the game. When Blender/Pillow is available, the reviewer may run `render_model.py` (checker/clay/textured), `inspect_model.py` and `preview.py` itself, to get evidence without asking again. Do not edit the model or the texture.
2. Check art quality and style fit. Use the relevant dimensions of the 6 (composition, shape/silhouette, color/value, lighting, material/texture, visual appeal). Keep this separate from the technical check in step 3.
3. Run the texture specialist checks below by method and risk. Details are in [texture checks](references/texture-checks.md).
4. Diagnose before you propose a fix. The same symptom can come from the map, UV, normal/tangent, shader or lighting. If you have no evidence that tells the causes apart, record the cause as a hypothesis and propose one cheap check that tells them apart.
5. When part of the texture is AI-made, check the generated-image fault table in [gen craft](../.art-production-support/shared/gen-craft.md). A detail that you cannot trace to the brief is an issue. If another person or agent does the review, send the request with the [review request](../.art-production-support/templates/review-request.md) template.
6. For a quick review, state a few issues with evidence. Score and ID are not required. When you track revisions or do acceptance, record each issue with the [review template](../.art-production-support/templates/review.md). It has the same fields as the AD template: id, priority, region, viewing_condition, evidence, consequence, confidence, repair, preserve, acceptance, status. In `region`, write the area on the model and, when known, the area/cell on the atlas.
7. Prioritize the 1-3 items with the largest impact. Keep the full list when the review is tracked.
8. For a revised texture, keep the id. Set `resolved` only when a new render under the same conditions proves the acceptance criterion. Look for regressions and for strengths that were lost. If the mesh/UV changed between the two versions, record that the old evidence is no longer valid for the affected areas.

Read the [deep method](../.art-production-support/shared/visual-review.md) when there are many criteria, many rounds or an unclear cause.

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

## Output

Write in this order:
1. The method used as the check standard, and its source.
2. Strengths to keep.
3. Priority issues (state clearly whether you suspect the map / UV / lighting / shader).
4. Next steps and who does them (Surface fixes the map; 3D Artist fixes UV/mesh/bake).
5. Parts without enough evidence.
6. Verdict: meets_checked_criteria / needs_revision / insufficient_evidence.

State whether it is a self-review or a real independent reviewer, and which renderer you used. A Blender image does not prove the result in the engine. The verdict is not AD approval.

## Gotchas

- Do not invent faults to fill a list. "No fix needed" is a valid conclusion.
- A good-looking flat atlas or paint view does not prove that the texture passes on the model. Always ask for, or make, a render on the model.
- Black or wrong-color fault: check color space, alpha, normal and material link before you ask for a repaint. Seam fault: check UV/tangent/bake/padding before you blur.
- A before/after comparison is valid only with the same camera, lighting, exposure, tone mapping and import.
- A still image does not prove animation, topology or performance. Do not infer texture resolution from a render image.
- If you are also asked to fix: hand the issues to the production skill. Do not review everything again.
- Issue outside the scope of the role (mesh, UV layout, high→low bake): record the issue and mark it for the 3D Artist. Do not fix it yourself.

Use the [technical gate](../.art-production-support/shared/scripts/README.md#evidence-gate) only when the caller needs a machine-readable acceptance.
