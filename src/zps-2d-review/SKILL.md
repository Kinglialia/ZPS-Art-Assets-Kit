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

If there is no Bible, review against the brief. Record the project-fit level as provisional.

## Workflow

1. Open the image. Look at the whole image, then inspect the area that explains your judgment, then look at the whole image again. View it at target size on light, dark and game backgrounds with `preview.py sheet`. Compare it with the set anchor with `preview.py compare`.
2. Check art quality and style fit. Use the relevant dimensions of the 6 (composition, shape/silhouette, color/value, lighting, material/texture, visual appeal). Keep this separate from the technical check in step 3.
3. Run the 2D specialist checks below for the asset type. Details are in [2D checks](references/2d-checks.md). For UI, also use the criteria in [UI QA](../zps-ui/references/ui-qa.md).
4. Check the **import notes** that come with the asset (filter, mipmap, compression, alpha, atlas padding). They must be complete and correct for the asset type, as in the import table in [Asset 2D production](../zps-asset-2d/references/production.md). For UI, use [Godot handoff](../zps-ui/references/ui-godot-handoff.md) when the project uses Godot. Do not open the engine. Record the level reached: export checked; the person who imports the asset into the engine checks import and device.
5. Check the generated-image fault table in [gen craft](../.art-production-support/shared/gen-craft.md). A detail that you cannot trace to the brief is an issue. If another person or agent does the review, send the request with the [review request](../.art-production-support/templates/review-request.md) template.
6. For a quick review, state a few issues with evidence. Score and ID are not required. When you track revisions or do acceptance, record each issue with the [review template](../.art-production-support/templates/review.md). It has the same fields as the AD template: id, priority, region, viewing_condition, evidence, consequence, confidence, repair, preserve, acceptance, status.
7. Prioritize the 1-3 items with the largest impact. Keep the full list when the review is tracked.
8. For a revised asset, keep the id. Set `resolved` only when the new image proves the acceptance criterion. Look for regressions and for strengths that were lost.

Read the [deep method](../.art-production-support/shared/visual-review.md) when there are many criteria, many rounds or an unclear cause.

## 2D specialist checks (choose by asset type)

| Type | What to check | Tool |
|---|---|---|
| Every asset | Readable at display size on the game background; distinguishable from other assets in the same set; no element outside the brief | `preview.py sheet` |
| Asset set | Same viewing angle, stroke weight, detail level, light direction, object scale and spacing as the set anchor | `preview.py compare` |
| Alpha | No halo/fringe on light and dark backgrounds; no fake transparent background; no part lost by cropping | `inspect_image.py`, `sheet` on dark background |
| Canvas/pivot | File size is correct; pivot/baseline follow the contract | `inspect_image.py` |
| Frame sequence | Pivot does not jitter between frames; volume, accessories and color are consistent; no per-frame auto-crop; path and pose spacing are reasonable, not jerky | `sprite_check.py`; `anim_preview.py` (filmstrip + onion skin to view; GIF for the approver) |
| Tile | All four edges join; no prominent mark shows the repeat rhythm when tiled over many cells | `preview.py tile` |
| Pixel art | Grid, clean clusters, correct palette; no bilinear resampling | `palette_report.py` when a palette exists |
| Decal | Alpha and blend are correct on the target material; edge shows no outline; scale matches surrounding objects | View on the real background image/material |
| Background | Enough area for parallax/occlusion for the scope; camera and scale match gameplay; does not compete for attention with characters and UI | `preview.py compare` with a gameplay image |
| UI | Matches the wireframe; all states present; 9-slice correct at min/max; long text and Vietnamese text with diacritics do not overflow or clip; touch area after scaling | [UI QA](../zps-ui/references/ui-qa.md) |

## When Asset 2D or UI calls this skill

Asset 2D and UI call this skill when they deliver a full set, deliver a final, or make a UI screen. For a single asset and small edits, the self-check of the production skill is enough.

- If the environment allows, run the review in a new subagent. The subagent receives only the asset, brief, style sheet, set anchor and import notes. It does not receive the production process. Record the result as an independent review.
- If you cannot run a subagent, record that it is a self-review.
- If there are issues, the production skill fixes them. In the next round, check only the open issues and regressions. Do not review everything again. The number of rounds follows the task budget.

## Output

Write in this order:
1. Strengths to keep.
2. Priority issues.
3. Next steps.
4. Parts without enough evidence (for example, not yet seen in the engine/on a device; animation rhythm not yet seen by a person).
5. Level reached (export checked / import / device).
6. Verdict: meets_checked_criteria / needs_revision / insufficient_evidence.

State whether it is a self-review or a real independent reviewer. The verdict is not AD approval.

## Gotchas

- Do not invent faults to fill a list. "No fix needed" is a valid conclusion.
- Zoom in to inspect details, but base the conclusion on readability at target size.
- Judge set mismatch against the set anchor of the set, not against a scene reference or concept.
- Deliberate stylization is not an anatomy/perspective fault.
- An agent cannot view a moving GIF. Conclude path, pose spacing and jerky spots from the onion skin. Record rhythm and motion feel as `not_checked` unless a person has viewed the GIF or run it in the game.
- A still image does not prove touch feel, flow or safe area on a device.
- Flow/UX problem: record it for UX/game design. Do not score it as an art fault.
- If you are also asked to fix: hand the issues to the production skill. Do not review everything again.
- Issue outside the scope of the role: record the issue and mark it out of scope. Do not fix it yourself.

Use the [technical gate](../.art-production-support/shared/scripts/README.md#evidence-gate) only when the caller needs a machine-readable acceptance.
