---
name: zps-asset-2d
description: "Create or revise in-game 2D images: icons, item sets, sprites, frame animations, tiles, decals and backgrounds, at their display size. Use for 2D game assets (\"vẽ icon\", \"làm sprite\", \"làm bộ item\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Asset 2D

**Not for:** UI elements (zps-ui); 3D asset concepts (zps-concept-artist); textures on models (zps-surface).

Follow the [shared rules](../.art-production-support/rules/art-operation.md) and the [quality standard](../.art-production-support/rules/art-quality.md).

## Intake

Required:
- Brief.
- Bible/style sheet.
- Set anchor of the set (see [set anchor](../.art-production-support/shared/set-anchor.md)).
- Display size and file size.
- Alpha.
- Pivot/baseline.
- States/frames.
- Display background.

Engine specifications: for Godot, use the [tech profile](../.art-production-support/templates/tech-profile-godot.md). For other engines, use the project specifications. An approved concept (if there is one) is the Execution reference.

Design a new icon yourself within the scope of the brief. For a large design question (character/prop not yet approved), tell the user that an approved concept is needed.

If there is no complete Bible/style sheet and only reference images, read the style with [style read](../.art-production-support/shared/style-read.md). Then make the whole set and present it once. Make a single sample first only if the user asks. If the references conflict, or the whole project needs a style, propose it to the AD.

## Workflow

1. Read [production](references/production.md) when you create a new asset or change canvas/alpha/pivot/frame/import. For a revision that keeps the design, use [revision](../.art-production-support/shared/revision.md).
2. Set the detail budget by **display size**. At a small size (for example a 64px icon), give priority to the silhouette and a few main identifying points. Check with `preview.py sheet` at target size. Do not count details.
3. Generate with [gen craft](../.art-production-support/shared/gen-craft.md). Use the set anchor of the set as the input reference.
4. Post-process: remove the background, crop to a fixed canvas, set pivot/baseline, scale to the file size. Do not auto-crop each frame. Scale and blend in linear light, and pull an out-of-gamut color back by chroma, not by clipping ([color](../.art-production-support/shared/color.md)).
5. Run these tools:
   - `preview.py sheet` (target size; light, dark and game backgrounds).
   - `tile` for a tile.
   - `sprite_check.py` and `anim_preview.py` (filmstrip, onion skin, GIF) for frames.
   - `palette_report.py` when a palette exists.
   - `inspect_image.py` for the file contract; add `--require-alpha` for a transparent asset (it also catches a painted checkerboard).
6. Open the preview. Check for added elements against the [quality standard](../.art-production-support/rules/art-quality.md), the generated-image fault table and the self-check. Fix until the asset passes or the budget ends. If an image does not pass, choose the fix with the [fix playbook](../.art-production-support/shared/fix-playbook.md). For a multi-turn task or a task that needs handoff, write a [task record](../.art-production-support/templates/task-record.md).

## Self-check

- Readable at display size on the game background; distinguishable from other assets in the same set.
- Set consistency: same viewing angle, stroke weight, detail level, light direction, object scale.
- Clean alpha (no halo on dark/light backgrounds); canvas/pivot follow the contract.
- Tile joins with no visible repeat mark; frames do not jitter the pivot.

## Handoff

When you deliver a full set or a final, call [2D Review](../zps-2d-review/SKILL.md) before you deliver (section "When Asset 2D or UI calls this skill"). Fix the issues, then check only those issues again. After the AD/user approves, record the set anchor as described in [set anchor](../.art-production-support/shared/set-anchor.md).

The handoff contains:
- PNG with the correct size/alpha.
- The real source file.
- The contact sheet you opened.
- GIF animation, if there is one (for the approver to view).
- Import proposal (filter, mipmap, compression, atlas).
- Status: export checked / imported into the engine / viewed on a device.

## Gotchas

- Generated icons often add a frame, a round background, a drop shadow or an outer glow that is not in the set. Compare with the sample icon.
- Shrinking a generated image loses thin lines. First increase the stroke/shape thickness. Do not only sharpen.
- Generated images often have a fake transparent background or a white background. Check `alpha_extrema`.
- Pixel art: do not resample with bilinear; use the Nearest filter.
