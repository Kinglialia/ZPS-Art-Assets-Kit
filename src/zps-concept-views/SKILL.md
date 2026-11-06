---
name: zps-concept-views
description: "Make the other orthographic views (back, left, right, top) of a game asset from one concept so that they match, then measure the match. Shape comes from a blockout; the image AI only paints. Use for \"gen 5 mặt\", \"turnaround\", \"các view còn lại\"."
metadata:
  version: 0.5.6
  validation: "selftest 13/13 on synthetic faults; not yet validated on real image-AI output"
---

# ZPS - Concept Views

**Not for:** full 3D models (zps-3d-artist), texture on models (zps-texture-artist), a new concept (zps-concept-artist).

**View convention.** The object faces −Y. `left` is the object's OWN left side (camera at +X). `right` is its own right side (camera at −X). This matches the 3D Artist.

**Good for** buildings, props and hard-surface objects. **Weak for** organic subjects (creatures, plants, rocks): a box blockout forces wrong shapes. For these, use the multi-view input of the 3D generators directly. Or use this skill only for color consistency, skip the silhouette thresholds, and say so in the report.

## Why AI views drift, and the fix

The AI guesses the shape of a hidden side, and it guesses differently in each view. This skill splits the work:

| Work | Who does it |
|---|---|
| Shape, proportions, hidden sides | The artist decides. The agent builds a 3D blockout. |
| Color, material, surface detail | The image AI paints over the blockout render. |
| Check | A script measures. No judgment by eye. |

Every view takes its shape from one 3D blockout, so the shapes match. The script catches what the AI can still get wrong: color, detail position, stretching.

## Views

Default views: front, back, left, right. Add top when the 3D path needs it. Make `bottom` only on request. Meshy, Tripo and ZPS 3D Gen multi-view use at most 4 views (front, back, left, right).

## Steps (detail: [process](references/process.md))

Use literal absolute paths: `<BLENDER>` (absolute Blender path), `<SKILL>` (this skill folder). No shell variables.

0. **Ask once.** Use the **albedo concept** (base color plus material, no light, from Concept Artist) as the color and material reference; a version with shadows is for mood only, because the image AI cannot tell a shadow from dark paint. If it does not exist, ask Concept Artist to make it first. Reuse the hidden-side notes and dimensions that Concept Artist recorded in the concept brief. Ask only what is missing. Never invent a hidden side.
1. **Build the blockout** with the 3D Artist self-build part graph. Write `part_graph.json` and `parts_lib.py` as in [self-build part graph](../zps-3d-artist/references/self_build.md#part-graph-part_graphjson). Give every part a `material` label (wall, roof, door). Make a detail whose position must be checked its own part with its own label. It sticks out or sinks in at least 2 cm. Work dir `<w>` is `output/<asset>/work/self_build/`, so the 3D Artist can continue from the same graph. Build:
   ```bash
   <BLENDER> -b --python <3D SKILL>/tools/self_build/assembly.py -- --work <w>
   ```
   The artist confirms the blockout before any image generation.
2. **Render the views:**
   ```bash
   <BLENDER> -b --python <SKILL>/scripts/render_blockout_views.py -- --parts <w>/parts --graph <w>/part_graph.json --out <abs>/views_blockout --res 1024
   ```
   For an existing model, use `--input <abs>/blockout.glb` instead of `--parts` and `--graph`.
3. **Generate the images.** Use the image tool of this app, as the [runtime adapter](../.art-production-support/adapters/runtime.md) describes. Get approval before each call that costs credits. Write requests per [gen craft](../.art-production-support/shared/gen-craft.md). Generate front first, get approval, then the other views. Ask for even, neutral light with no shadows on the object, the same in every view (exception for painted-in light: [process](references/process.md#rules-for-every-generation)). Save to `<abs>/views_gen/`.
4. **Measure:**
   ```bash
   python3 <SKILL>/scripts/measure_views.py --blockout <abs>/views_blockout --gen <abs>/views_gen --out <abs>/report --views front,back,left,right,top [--concept-colors <abs>/concept_colors.json]
   ```
5. **Fix and repeat.** Generate again only the views in `report.json` → `regen`. Add the reported fault to the request. If many views fail on shape, check the blockout first. Stop after 3 rounds and tell the artist.

## What the report measures

The script crops the AI image and the blockout to the object's bounding box and resizes both. A changed frame or zoom is not an error.

| Check | What it tests | Pass |
|---|---|---|
| Shape (IoU) | AI silhouette equals blockout silhouette | 0.93 or more |
| H/W ratio | The image is not stretched | error 3% or less |
| Detail position | The border of each material (door, window) is in the right place | 75% or more |
| Color dE | Color of each material against the concept, or the front view | 6 or less |
| Opposite pairs | Front/back, left/right, top/bottom are mirror images | IoU 0.93 or more, ratio error 4% or less |
| Cross proportion | Front(H/W) = Side(H/D) × Top(D/W) | error 4% or less |

Output in `report/`: `report.md`, `overlay_sheet.png` (blockout, AI image and difference per view) and `report.json`. Example: [report](examples/report.md), [overlay](examples/overlay_sheet.png).

## Hand off to 3D

The 3D Artist reads these at intake:
- The main concept.
- The passed views: `front.png`, `back.png`, `left.png`, `right.png`, `top.png`.
- `views.json` (sizes in metres, metres per pixel, convention).
- The self-build work dir with `part_graph.json`.
- `report/` (report.md, overlay_sheet.png, report.json).

## Rules

- Do not edit an image by hand or by code to pass the check. The measured image must be the AI output.
- Do not change a threshold to get a pass.
- Do not invent a hidden side. Mark each assumption in the report.
- Get approval before each generation that costs credits.

## Limits

- The script does not see small detail inside one material area: patterns, pane count, sign text. Check the overlay by eye, and write it in the report.
- If the AI background has the object's color, the object cutout fails. Choose a background that differs from the object.
- The thresholds are tested only on synthetic images. Review them after a few real assets.
- The kit build runs a self-test (13 checks, no credits).

**Language.** The report files are English. Tell the user the summary in the user's language.
