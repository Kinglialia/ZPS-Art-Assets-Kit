---
name: zps-texture-planning
description: "Choose how to texture a 3D model: read its UVs, materials, screen size and the style, then propose one or two methods with trade-offs and a small test. Use before texturing (\"nên texture kiểu gì\", \"hand-painted hay PBR\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Planning

**Not for:** texturing after the method is chosen (zps-surface).

Follow the [shared rules](../.art-production-support/rules/art-operation.md). The output is a method proposal, not a painted texture.

**Who decides the method:**
- If the caller (AD, user) states a specific method, or requires one in the Art Style document, follow it.
- If nobody states one, the skill chooses.
- Always follow the technical limits of the model (for example, no UV).
- If two specific requirements conflict, ask the caller. Do not pick a side yourself.
- When you choose, record the chosen method and the reason in one line in the handoff.
- Prefer a method that the skill can do itself to delivery quality (section "Real capability of the role" in [texture methods](references/texture-methods.md)).
- If a method needs a person or a DCC tool, say so first. Do not choose it silently.

## Intake

Collect:
- Who delivers (3D Artist, AD, user). When the 3D Artist calls, receive part A of the [3D ↔ Texture handoff](../.art-production-support/templates/3d-texture-handoff.md).
- Model and version.
- Concept or style sheet/Bible.
- Camera and size on screen.
- Number of assets of the same type, variants.
- The project's engine specifications (Godot: [tech profile](../.art-production-support/templates/tech-profile-godot.md)).

If something is missing, record an assumption. If the concept lacks material areas or hidden parts, record an inference or ask the user to mark them on the concept.

## Workflow

1. **Measure the model.** Run `inspect_model.py` (UV, material, vertex color, texel density). Run `render_model.py --mode clay` and `--mode checker` from a few angles. Open the images. See [scripts](../.art-production-support/shared/scripts/README.md#model). If there is no Blender, ask the 3D Artist for the UV image and the specifications. Record the parts not measured. Ask only what you cannot measure, in a single question.
2. **Read the concept/style.** Check for hand-painted strokes, painted-in light or engine light, surface grain, and the level of realism. If there is no style sheet, use [style read](../.art-production-support/shared/style-read.md).
3. **Choose 1–2 methods** (author × shader) from [texture methods](references/texture-methods.md). Give the reason, the trade-offs (quality, memory, draw calls, effort, variants) and the parts that need a DCC tool/person.
4. **Small test sample:** a representative area, camera angle, acceptance criteria.
5. Deliver with the [proposal template](references/proposal-template.md). When the method is already chosen, or is within the existing authority to choose, hand off to [Surface](../zps-surface/SKILL.md).

## Gotchas

- UV overlap between objects that share one texture is a fault when those areas need their own detail, bake or marks. A palette/gradient atlas, stacking and mirroring are valid when they are deliberate and no separate information is needed (see the 3D Artist spec). Confirm the intent before you call it a fault. With light baked into albedo, mirroring/stacking shows easily.
- UV outside 0–1 can be a deliberate tileable/trim layout. Ask before you call it a fault.
- If there is no UV, use only vertex color, triplanar or procedural methods until UV exists.
- If the role cannot do a method itself, say clearly which part needs a person/DCC tool.
- When the 3D Artist calls **before unwrap**, the proposal must include UV requirements for the 3D work (whether overlap is allowed, texel density, trim direction) and whether material slots must be split by area. Ask for a slot split only when the areas need different shaders. By default, keep one material.
