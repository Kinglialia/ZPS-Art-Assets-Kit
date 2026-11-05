# 2D checks — how to check and diagnose

Read this file when you need a deep check of one group in the table in SKILL.md, or when the cause is unclear. Production rules and import proposals are in [Asset 2D production](../../zps-asset-2d/references/production.md). UI rules are in [UI QA](../../zps-ui/references/ui-qa.md). This file says what the reviewer checks, with what, and how far the conclusion can go.

## Minimum evidence by question

| Review question | Evidence needed | Not enough to conclude |
|---|---|---|
| Is it readable in the game? | Preview at display size on the real game background, or a game screenshot | Enlarged image; plain white background |
| Is the alpha clean? | `inspect_image.py` (alpha_extrema) and a view on dark + light backgrounds | The file is RGBA |
| Are pivot/frames stable? | `sprite_check.py` on the whole sequence | Viewing each frame alone |
| Does the motion follow the right path, without jerks? | Onion skin + filmstrip from `anim_preview.py` | Each frame alone; the agent viewing the GIF itself |
| Rhythm and motion feel | A person views the GIF at target fps, or runs it in the game | Onion skin (shows only the path) |
| Does it match the set? | Compare with the set anchor, as in [set anchor](../../.art-production-support/shared/set-anchor.md). If there is no anchor yet, compare the whole set side by side | Comparison with the concept or a scene reference |
| Are the import notes correct? | Check against the import table in [Asset 2D production](../../zps-asset-2d/references/production.md) | File name; "PNG exported" |
| Does the tile join? | `preview.py tile` with many cells | Viewing one cell |
| Does the UI survive long text? | Render with the real longest string, with Vietnamese diacritics | Short English sample text |
| Does it work in the engine/on a device? | Real import / test on a device | Preview from a script |

If evidence is missing for a row, record the conclusion for that row as `not_checked`. It is neither pass nor fail.

## Quick diagnosis tree

- **Hard to read at small size:** The silhouette is unclear → too many identifying points → value between object and background is too close → thin lines disappear when scaled down. Fix by simplifying the shapes or increasing the stroke weight before you sharpen.
- **Set mismatch:** Viewing angle, stroke weight, detail level, light direction or object scale differs from the set anchor. State which axis differs.
- **Light/dark outline around the asset:** It is a halo from background removal, wrong premultiplied/straight alpha, or a missing alpha border when filtering.
- **Character jitters during animation:** Canvas/pivot is not fixed between frames. The usual cause is per-frame auto-crop.
- **Tile shows its seam:** The edges do not match, or a prominent mark repeats at regular intervals. Separate the two cases because the fixes differ.
- **Pixel art looks blurry:** Bilinear resampling or non-integer scale. Or the import notes propose the Linear filter.
- **Animation is jerky:** Pose spacing on the onion skin is uneven where it must be even. Or one frame is off the path. Or character volume changes between frames.

## Severity levels

- **blocker:**
  - Cannot be read or distinguished at game size when this is the main function (for example an item icon, a UI state).
  - Alpha/canvas/pivot break the contract and the asset displays wrong.
  - Wrong import notes make the asset display wrong (pixel art without Nearest, missing atlas padding that causes bleeding).
  - UI text overflows or clips in a required string.
- **major:**
  - Clear set mismatch.
  - Halo visible on the game background.
  - Tile shows its repeat rhythm at the normal viewing distance.
- **minor:**
  - Secondary details not yet tidy.
  - A fault visible only when zoomed in.
- Record a **preference** separately for an aesthetic choice that does not violate the brief.

## UI review

Take the check criteria from [UI QA](../../zps-ui/references/ui-qa.md). The part below adds evidence and severity levels from the reviewer's view.

| Question | Evidence needed | Not enough to conclude |
|---|---|---|
| Does the text overflow or clip? | Render with the real longest string, with Vietnamese text with diacritics | Short sample text |
| Are all states present? | An image of each required state (normal, pressed, locked, selected...) | One representative state |
| Is the 9-slice correct? | Render at the smallest and largest size that will be used | The source frame image |
| Is it readable on the game? | Screen at target resolution, on the busiest game background | Plain background |
| Is the touch area big enough? | Measurement after scaling at target resolution | Image size |
| Does it match the wireframe? | Place it next to the approved wireframe | A description in words |
| Does the SVG source follow the rules? | Warnings from `svg_render.py` (text in SVG, filter, mask...); group names by component/state | Viewing only the PNG |

- **blocker:** required text overflows/clips; a required state is missing; 9-slice breaks at the real size; touch area is below the project target; differs from the approved wireframe.
- **major:** wrong attention order; HUD hard to read on a busy background; deviates from the UI kit or the chosen direction.
- **minor:** small alignment deviation; extra decoration that does not affect reading.
- Flow/UX problem: record it for UX/game design. Do not score it as an art fault.

## Role boundaries

The reviewer concludes on issues that have evidence. Fixing the asset belongs to Asset 2D or UI. Flow/wireframe problems belong to UX/game design. A style change belongs to the AD.
