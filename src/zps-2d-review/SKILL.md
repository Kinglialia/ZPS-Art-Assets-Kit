---
name: zps-2d-review
description: "Review in-game 2D assets and UI at real display size: readability, set consistency, alpha, pivot, tiles, 9-slice, states, long text and import notes. Use for 2D or UI review (\"review icon\", \"kiểm sprite\", \"review UI\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 2D Review

**Not for:** textures on 3D models (zps-texture-review); concept art or cross-domain style decisions (zps-artistic-critique); open image opinions (zps-visual-intelligence). Self-checks on single assets and small edits stay in zps-asset-2d and zps-ui.

Follow the [shared rules](../.art-production-support/rules/art-operation.md). Review does not need an image-generation tool, but you must be able to open the real image. Judge a 2D asset **at display size and on the real background** of the game, not only in an enlarged view.

## Intake

Collect:
- Artifact/version.
- Asset type: icon, item set, sprite/frame sequence, tile, decal, background, UI component/screen.
- Brief.
- Bible/style sheet version.
- The set anchor of the set (find and use it as described in [set anchor](../.art-production-support/shared/set-anchor.md)).
- Stage: thumbnail / test sample / final.
- Display size and target background.
- For UI, also collect the approved wireframe, the required states, the longest string and the language.

## Workflow

Follow the [review procedure](../.art-production-support/shared/review-procedure.md). The 2D parts:
- Step 1: view the asset at target size on light, dark and game backgrounds with `preview.py sheet`. Compare it with the set anchor with `preview.py compare`.
- Step 3: run the 2D specialist checks below for the asset type. Details are in [2D checks](references/2d-checks.md). For UI, also use [UI QA](../zps-ui/references/ui-qa.md).
- Also check the **import notes** that come with the asset (filter, mipmap, compression, alpha, atlas padding) against the import table in [Asset 2D production](../zps-asset-2d/references/production.md). For UI on Godot, use [Godot handoff](../zps-ui/references/ui-godot-handoff.md). Do not open the engine. Record the level reached: export checked; the person who imports the asset checks import and device.

## 2D specialist checks (choose by asset type)

| Type | What to check | Tool |
|---|---|---|
| Every asset | Readable at display size on the game background; distinguishable from other assets in the same set; no element outside the brief | `preview.py sheet` |
| Asset set | Same viewing angle, stroke weight, detail level, light direction, object scale and spacing as the set anchor | `preview.py compare` |
| Alpha | No halo/fringe on light and dark backgrounds; no fake transparent background (a painted checkerboard is not transparency); no part lost by cropping | `inspect_image.py --require-alpha` (alpha channel, `painted_checkerboard`), `sheet` on dark background |
| Canvas/pivot | File size is correct; pivot/baseline follow the contract | `inspect_image.py` |
| Frame sequence | Pivot does not jitter between frames; volume, accessories and color are consistent; no per-frame auto-crop; path and pose spacing are reasonable, not jerky | `sprite_check.py`; `anim_preview.py` (filmstrip + onion skin to view; GIF for the approver) |
| Tile | All four edges join; no prominent mark shows the repeat rhythm when tiled over many cells | `preview.py tile` |
| Pixel art | Grid, clean clusters, correct palette; no bilinear resampling | `palette_report.py` when a palette exists |
| Color | Palette, accents and ramps match the style sheet by measurement, not by eye | `palette_report.py` (`vivid`, `accents`, `--ramp`); see [color](../.art-production-support/shared/color.md) |
| Decal | Alpha and blend are correct on the target material; edge shows no outline; scale matches surrounding objects | View on the real background image/material |
| Background | Enough area for parallax/occlusion for the scope; camera and scale match gameplay; does not compete for attention with characters and UI | `preview.py compare` with a gameplay image |
| UI | Matches the wireframe; all states present; 9-slice correct at min/max; long text and Vietnamese text with diacritics do not overflow or clip; touch area after scaling | [UI QA](../zps-ui/references/ui-qa.md) |

## When Asset 2D or UI calls this skill

Asset 2D and UI call this skill when they deliver a full set, a UI screen, or an asset that the brief marks as final for acceptance. A single asset otherwise, and small edits, need only the self-check of the production skill. Run it as in the review procedure; the reviewer also receives the set anchor and the import notes.

## Output

Use the output order of the review procedure. Add, after the parts without enough evidence, the level reached (export checked / import / device). Examples of missing evidence: not yet seen in the engine or on a device; animation rhythm not yet seen by a person.

## Gotchas

- Zoom in to inspect details, but base the conclusion on readability at target size.
- Judge set mismatch against the set anchor of the set, not against a scene reference or concept.
- Deliberate stylization is not an anatomy/perspective fault.
- An agent cannot view a moving GIF. Conclude path, pose spacing and jerky spots from the onion skin. Record rhythm and motion feel as `not_checked` unless a person has viewed the GIF or run it in the game.
- A still image does not prove touch feel, flow or safe area on a device.
- Flow/UX problem: record it for UX/game design. Do not score it as an art fault.
