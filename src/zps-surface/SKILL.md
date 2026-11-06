---
name: zps-surface
description: "Create, edit or fix textures and materials on a 3D model with a chosen method: hand-painted, flat or vertex color, PBR, tileable or trim, pixel, photo, projection. Use for texture work (\"vẽ texture\", \"sửa texture\", \"sửa seam\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Surface

**Not for:** choosing the method (zps-texture-planning); standalone review (zps-texture-review).

Follow the [shared rules](../.art-production-support/rules/art-operation.md) and the [quality standard](../.art-production-support/rules/art-quality.md).

## Intake

Method: if the caller names a method (or the Art Style document requires one), use it. If nobody names a method, use zps-texture-planning to choose one.

If the 3D Artist calls this skill, take the input from part A of the [3D ↔ Texture handoff](../.art-production-support/templates/3d-texture-handoff.md). Measure what you can with `inspect_model.py`. Ask only for what you cannot measure, and put all questions into one message.

Required input:
- Model, UV and shader version.
- Assigned areas.
- Style sheet.
- Map contract: channels, color space, size, and normal convention from the project specification. For Godot, see the [tech profile](../.art-production-support/templates/tech-profile-godot.md).
- Recipient.

New design (motif, symbol): if the design belongs to the task, pass it to Concept/AD. Do not change a locked identity yourself.

If there is no complete Bible or style sheet and only reference images exist, read the style with [style read](../.art-production-support/shared/style-read.md). Show one test sample on the model before you make a series. If the references conflict, or the whole project needs a style, propose it to the AD.

## Workflow

1. Read **only** the file for the chosen method (plus the shared files when needed):

| Method | Read |
|---|---|
| Hand-painted | [Hand-painted](references/hand-painted.md); recipes: [painting practice](references/painting-practice.md) |
| Flat color, gradient atlas, vertex color | [Flat color](references/flat-color.md) |
| PBR, bake, data maps | [PBR](references/pbr.md) |
| Tileable, trim sheet, decal, triplanar | [Tileable/trim](references/tileable-trim.md) |
| Pixel texture | [Pixel texture](references/pixel-texture.md) |
| Photo/scan | [Photo/scan](references/photo-scan.md) |
| Paint view for projection | [Projection](references/projection.md) |
| Shared: new material segmentation | [Surface craft](references/surface-craft.md) |
| Shared: UV, seam, bake, import | [Mapping](references/mapping-validation.md) |

2. Make a **checker + clay** render (`render_model.py`) in these cases:
   - No valid render exists for this mesh/UV version.
   - The mesh or UV changed.
   - The fault could come from UV or scale.

   For a small color fix on an unchanged mesh/UV, reuse the old evidence. If Blender is not available, ask the 3D Artist for a render image.
3. Set the material intent and the detail budget from the style sheet.
4. Make the texture with the chosen method. For parts you generate or edit, follow [gen craft](../.art-production-support/shared/gen-craft.md). For a procedural or seeded texture, record the seed and all parameters of each variant; the same seed must give the same result. For color and value ramps, see [color](../.art-production-support/shared/color.md).
5. Apply the texture to the model. Render from several angles. Use the game lighting if you know it.
6. Check for added elements against the quality standard, the generated-image fault table and the self-check. Fix the cause (UV, scale, shading) before you redo the work. If the image does not pass, choose the fix with the [fix playbook](../.art-production-support/shared/fix-playbook.md). If the task has many rounds or needs a handoff, write a [task record](../.art-production-support/templates/task-record.md).

## Self-check (on the model render)

- The result matches the method and the style sheet. Compare it with the render of an approved asset of the same type.
- Seams are not visible from the game angles. Detail follows the forms, not the UV edges.
- For lit/PBR, no fixed highlight or shadow is baked into the albedo. Channels and color space are correct.
- No detail outside the element inventory.

## Handoff

Hand off with part B of the [3D ↔ Texture handoff](../.art-production-support/templates/3d-texture-handoff.md). Include:
- The method used, and why (when you chose it yourself).
- Maps, atlas and paint views.
- The renders you opened. State the renderer: Blender is not the target engine.
- The map contract.
- The atlas cell table or trim strip table, if there is one.
- **Material setup notes** for the person who imports the asset into the engine: lit/unlit, compression, mipmap, which image is the normal map.
- Parts not checked.

Do not create a material in the engine project unless the task clearly assigns it. If the 3D Artist called this skill, return the result to the 3D Artist. The 3D Artist applies it to the model and exports the final file.

## Gotchas

- A generated image placed on a UV layout often has light and shadow painted along the atlas. Always check it in a render.
- Take material areas from the "part → material" table and the parts image in part A of the handoff template. By default, a model has only one material. If you need the 3D Artist to fix UVs or split slots, put all requests into one message.
- Other engines may use a DirectX-style normal map. Godot needs OpenGL Y+.
