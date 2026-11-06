---
name: zps-ui
description: "Create or revise game UI art: buttons, panels, HUD, bars, status icons, states, 9-slice assets and the developer handoff, from an approved wireframe. Use for UI art (\"làm UI\", \"vẽ nút\", \"HUD\", \"9-slice\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - UI Art

**Not for:** screen flow and UX design (UX or game design); item icons and sprites (zps-asset-2d); standalone UI review (zps-2d-review).

Follow the [shared rules](../.art-production-support/rules/art-operation.md) and the [quality standard](../.art-production-support/rules/art-quality.md).

## Scope

This skill covers UI images, editable sources, assets, and the handoff spec. The developer uses the handoff spec to build the scene, Theme and script. UI art delivers assets and a spec. It does not write code.

Do **not**:
- Design flow or wireframes.
- Decide game rules, rewards or prices. If these are missing, ask UX/game design.

You may give feedback when a layout is hard to draw or hard to read.

## Intake

Collect:
- Approved wireframe and interaction spec.
- Style sheet or UI kit.
- Engine/version, base size, stretch, safe area (Godot: [tech profile](../.art-production-support/templates/tech-profile-godot.md)).
- Language and longest string.
- Source format and the tools you really have.

If there is no wireframe, use the described layout if it is clear enough. Ask only about interaction or layout that affects the drawing. Do not redesign the UX.

If there is no complete Bible/style sheet and only reference images, read the style with [style read](../.art-production-support/shared/style-read.md). Present one test sample before you make the series. If the references conflict, or the whole project needs a style, propose it to the AD.

## Workflow

1. **No UI style yet:**
   - Make the number of directions the request asks for, on the same wireframe. Two directions count as one choice when a comparison is needed.
   - The directions must differ in form, not only in palette. Show them on the hardest sample screen.
   - If nobody asks you to stop and choose a direction, choose one direction yourself and record the reason. Make the whole set and present it once. Name the other directions briefly, so the AD/user can switch if they want.
   - Read [UI system](references/ui-system.md).
2. **Just-enough system:** colors by role, type levels, spacing, components with IDs, the necessary states. Prefer existing tokens/components. Check color scales with `palette_report.py --ramp`. For two adjacent fills, use the border trick in [color](../.art-production-support/shared/color.md).
3. **Production:**
   - Text, layout and components are edited independently.
   - Record source → export method → runtime file.
   - Choose the source by UI type in [UI system](references/ui-system.md). Geometric components and flat UI default to **SVG** (export PNG with `svg_render.py`). Hand-drawn frames and illustrations use generated images per [gen craft](../.art-production-support/shared/gen-craft.md). You may combine them.
   - A flat image is not a source for a whole screen.
4. **Handoff to the developer:** fill in the [UI handoff](templates/ui-handoff.md). For a Godot project, also read [Godot handoff](references/ui-godot-handoff.md). Do not change production project settings/Theme to preview.
5. **Review before delivery:** when you deliver a UI screen, a full component set or a final, call [2D Review](../zps-2d-review/SKILL.md) (section "When Asset 2D or UI calls this skill"). After the AD/user approves, record the direction or sample screen as described in [set anchor](../.art-production-support/shared/set-anchor.md).
6. **QA:** choose checks by risk in [UI QA](references/ui-qa.md). For accessibility, follow the task: [UI accessibility](references/ui-accessibility.md). If an image does not pass, choose the fix with the [fix playbook](../.art-production-support/shared/fix-playbook.md). For a multi-turn task or a task that needs handoff, write a [task record](../.art-production-support/templates/task-record.md).

## Self-check

- Matches the wireframe; attention order is clear at the real size and background.
- All required states are present; touch area after scaling meets the project target.
- 9-slice stretches correctly at min/max size; long text and Vietnamese text with diacritics do not overflow or clip.
- Asset alpha is clean; names and sizes match the spec; you can change the representative text/icon and export again.

## Gotchas

- Generated UI images often have fake text, nested frames and extra glow. Do an element inventory.
- A still image does not prove flow, touch feel, motion or safe area.
- To review one screen alone, use zps-2d-review with the criteria in UI QA.
