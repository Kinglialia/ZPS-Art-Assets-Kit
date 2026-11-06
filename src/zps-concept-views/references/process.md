# Process detail: the other views from one concept

Read SKILL.md first. It holds the goal, the view convention, the default views, the commands and the measures. This file adds only the detail of each step.

> `<SKILL>` = the folder of this skill. `<BLENDER>` = the absolute path of Blender. `<3D SKILL>` = the folder of zps-3d-artist. `<w>` = `output/<asset>/work/self_build/` (absolute). `<abs>` = the absolute asset folder.
> Every command uses literal absolute paths. Do not use shell variables. Run Python scripts as `python3 <SKILL>/scripts/<name>.py`. Never use `blender -P`.

---

## Step 0. Ask the artist (required)

1. Read the concept brief first. Concept Artist records the albedo concept, the hidden-side notes and the real dimensions there. Reuse them. Use the albedo concept as image 1 in every prompt (see SKILL.md step 0).
2. Ask only what is missing, in one message:
   - **What do the hidden sides look like?** For each side that the concept does not show (back, top, the other side), ask for a rough sketch or a clear description: doors, number and place of windows, number of roof slopes, chimney, sign. If there is no information, **do not invent it**. Write "assumption" in the report.
   - **Is the object symmetric?** (left/right, front/back)
   - **Real size**, if known (height in metres), or a reference (door height 2 m).
   - **Which views are needed?** (see Views above)
   - **Which image tool?** If image generation costs credits, tell the artist the price and the credits left. Get approval before each call.

---

## Step 1. Build the blockout

Build the blockout with the 3D Artist self-build part graph. Do not write a separate script.

1. Write `part_graph.json` and `parts_lib.py` in `<w>`, as in [self-build part graph](../../zps-3d-artist/references/self_build.md#part-graph-part_graphjson).
2. Use simple shapes only: box, prism, cylinder. UVs and small detail are not needed.
3. **Measure the proportions on the concept.** Write each size as a named param (`wall_h`, `roof_pitch`).
4. **Build the hidden sides as the artist answered in Step 0.**
5. **Give every part a `material` label**, named for the material: `wall`, `roof`, `door`, `window`, `wood_trim`. Parts of the same material share one label. The labels appear in the report.
6. A detail whose position must be checked (door, window, sign) is **its own part with its own label**. It sticks out or sinks in at least 2 cm, so that it makes an edge in the render.
7. Keep the work dir `output/<asset>/work/self_build/`. The 3D Artist continues from the same graph later.
8. Build with the command in SKILL.md step 1.

Before you go on: render once, put the render next to the concept, and show it to the artist. **The artist confirms the blockout.** A blockout fix costs much less than a new image generation.

---

## Step 2. Render the blockout views

Run the render command in SKILL.md step 2. Output in `views_blockout/`:
- `<view>_id.png`: one flat color per material, transparent background. The script **measures** with it. Do not give it to the AI.
- `<view>_guide.png`: a render with light and edges, in the material colors. Give this **guide image** to the image AI.
- `views.json`: the list of materials and their ID colors (for example `roof = #FFE119` yellow), the sizes in metres, the metres per pixel and the convention.

To generate all views in one image:
```bash
python3 <SKILL>/scripts/sheet.py make --dir <abs>/views_blockout --suffix _guide --out <abs>/guide_sheet.png --bg "#E8E8E8"
```

---

## Step 3. Generate the images

Use the image tool of this app, as the runtime adapter describes (`../../.art-production-support/adapters/runtime.md`). Get approval before each call that costs credits. Write each request per [gen craft](../../.art-production-support/shared/gen-craft.md).

### Rules for every generation
- Use a **plain, flat, one-color background** that is not in the object. The default is `#E8E8E8` light grey. If the object is grey or white, use `#2B2B2B` or another color that differs from the object. No ground, no cast shadow, no vignette, no text.
- **Lighting:** even, neutral light, the same in every view. No shadow cast on the object (roof on wall, part on part), no strong directional light, no dark ambient-occlusion corners. Reasons: a fixed light would make the back and one side darker than the front, so the views cannot match; shadows change the measured material colors and cause false regenerations; and shadows end up in the 3D texture.
  - Exception: if the style sheet paints light into the albedo (hand-painted, for example a lighter top and darker base), keep that painted convention, and keep it the same in every view. Never use one fixed world light.
  - Write the rest of the request with the [lighting rules](../../.art-production-support/shared/gen-craft.md#lighting-and-shadows). After each generation, check for shadows and remove them by an edit before you measure.
  - The prompts below use the default lighting line. For the exception, replace it with: "Painted light as in the concept (<the convention>), the same in every view. No other shadows."
- The object is **fully inside the image**. Do not crop it. Do not stretch it.
- Save the prompt of each view, so that you can repeat it.

### Way A (recommended): one view at a time, front first
1. Generate **front** with the concept and `front_guide.png`.
2. The artist approves the front view. It is the color standard for the other views.
3. Generate each other view with the concept, the **approved front image**, `<view>_guide.png` and the hidden-side description from Step 0.
4. If the object is symmetric, make the left view by flipping the right view. Do not generate it. Write this in the report.

### Way B: one image with all views
Give the concept and `guide_sheet.png`. Ask for the whole sheet in the same layout. Then split it:
```bash
python3 <SKILL>/scripts/sheet.py split --sheet <abs>/gen_sheet.png --out <abs>/views_gen
```
This costs less, and the colors are often more consistent. But each view is smaller, and the AI often moves the cells. If the report shows a failed view, generate that view again with Way A.

### Image prompts

Replace each `[...]` with real information. Take `[MATERIAL LIST]` from `views.json`. Example: `yellow = thatched roof, blue = plastered stone wall, green = wooden door, orange = window with wooden frame, red = brick chimney`.

**Front view** (image 1 = albedo concept, image 2 = front_guide.png):
```text
Repaint image 2 (a flat-coloured 3D guide render) as a finished game-asset illustration
in the exact art style, materials, colours and level of detail of the concept art in image 1.

STRICT RULES
- Orthographic FRONT view, camera straight on, no perspective, no tilt.
- Keep EXACTLY the silhouette, proportions and position of every part of image 2.
  Do not add, remove, move, resize or rotate any part.
- Each flat colour in image 2 marks one material: [MATERIAL LIST].
  Paint each region with that material as it looks in the concept.
- Plain, flat, solid background [#E8E8E8]. No ground, no cast shadow, no vignette,
  no text, no labels, no border.
- Unlit base-color look, even ambient light, the same in every view. No shadow cast on the object,
  no strong directional light, no dark ambient-occlusion corners. The shading of the guide image
  only shows the form: do not copy it as light.
- The whole object fully visible and centred. Do not crop. Do not stretch.
```

**Other views** (image 1 = albedo concept, image 2 = approved front view, image 3 = `<view>_guide.png`):
```text
Image 2 is the approved FRONT view of an object. Image 3 is a flat-coloured 3D guide render
of the [BACK / LEFT / RIGHT / TOP / BOTTOM] view of the SAME object.
Repaint image 3 so it looks like the same object as image 2, from the [VIEW] side,
in the art style of the concept in image 1.

STRICT RULES
- Orthographic [VIEW] view, camera straight on, no perspective, no tilt.
- Keep EXACTLY the silhouette, proportions and position of every part of image 3.
  Do not add, remove, move, resize or rotate any part.
- Each flat colour in image 3 marks one material: [MATERIAL LIST].
  Every material must have the SAME colour, texture and wear as in image 2.
- What this side looks like: [HIDDEN-SIDE DESCRIPTION FROM STEP 0, in English].
- Plain, flat, solid background [#E8E8E8]. No ground, no cast shadow, no vignette,
  no text, no labels, no border.
- Unlit base-color look, even ambient light, the same in every view. No shadow cast on the object,
  no strong directional light, no dark ambient-occlusion corners. The shading of the guide image
  only shows the form: do not copy it as light.
- The whole object fully visible and centred. Do not crop. Do not stretch.
```

**Whole sheet** (image 1 = albedo concept, image 2 = `guide_sheet.png`):
```text
Image 2 is a sheet of 6 orthographic guide renders of ONE object, in a 3x2 grid:
row 1 = front, back, left; row 2 = right, top, bottom.
Repaint every cell as a finished game-asset illustration in the art style, materials
and colours of the concept in image 1, so that all six cells show the same object.

STRICT RULES
- Keep the exact same 3x2 layout, cell positions and cell sizes as image 2.
- In every cell keep EXACTLY the silhouette, proportions and part positions of the guide.
  Do not add, remove, move or resize any part.
- Each flat colour marks one material: [MATERIAL LIST]. One material = the same look in every cell.
- Hidden sides: [HIDDEN-SIDE DESCRIPTION].
- Plain, flat, solid background [#E8E8E8] everywhere. No shadows, no text, no labels, no grid lines.
- Unlit base-color look, even ambient light, the same in every view. No shadow cast on the object,
  no strong directional light, no dark ambient-occlusion corners. The shading of the guide image
  only shows the form: do not copy it as light.
```

If you did not render a view, change the sheet prompt to list only the views you have. Save the images in `views_gen/` with these names: `front.png`, `back.png`, `left.png`, `right.png`, `top.png` (`bottom.png` only on request).

---

## Step 4. Measure and report

**(Optional, recommended)** Measure the reference colors on the **albedo** concept, never on a version with light or shadows (a shadowed wall reads darker than its paint). Use `palette_report.py` on the concept (the `vivid` color of each material area) to get the hex code of each material on the concept. Save `concept_colors.json`. Use the **same material names as in `views.json`**:
```json
{ "roof": "#A1901B", "wall": "#45549A", "door": "#43844A" }
```

Then run the measure command in SKILL.md step 4 with `--concept-colors`. In `report.json`, the field `regen` lists the views to generate again. Opposite pairs and cross proportion use only the views that exist. If the organic-subject scope applies, report the silhouette numbers but do not use them as pass or fail.

---

## Step 5. Fix and repeat

1. Read `report.json` → `regen`. For each view in it, read that view's "What to fix" in `report.md` and look at its row in `overlay_sheet.png`.
2. Generate **only those views** again. Add the exact fault to the request. Examples: "the roof must be #A1901B ochre like image 2, not orange"; "the window is on the RIGHT half of the wall, exactly where the orange region of image 3 is".
3. Run Step 4 again.
4. Do at most **3 rounds**. If a view still fails after 3 rounds, stop. Tell the artist which view failed and why. Suggest one fix: change the blockout, change the image tool, or draw the view by hand.

If **many views fail on shape**, or an opposite pair fails in both views, the fault may be in the blockout and not in the AI. Check the blockout against the concept before you generate again.

---

## Final report to the artist

The report files are English. Tell the artist the summary in the artist's language. Send `report/report.md`, `report/overlay_sheet.png` and the final images, with a short summary:
- Overall score and verdict (pass / warning / fail).
- Number of rounds, which views you generated again, and why.
- What the check **cannot see**: small detail inside one material area (patterns, pane count, sign text). List what you see as wrong on the overlay, or the result of a visual check if you ran one.
- The assumptions about hidden sides.
