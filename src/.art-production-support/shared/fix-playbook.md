# Fix playbook — choose a fix by symptom

Read this when an image does not pass and you must choose the next step. The order of fixes is based on real trials. Confidence follows the amount of evidence (low = one subject/style/tool). The detailed evidence is in the source repo (`research/trials/`), not in the package.

## Contents
- Selection procedure
- What to measure for each deliverable
- Symptom → fix table
- Choosing an option
- Recording lessons and when to stop

## Selection procedure

1. **Diagnose with numbers and your eyes.** Numbers show where the image deviates. Your eyes see what numbers do not see (render style, odd details, construction).
2. **Classify the defect**: *structure* (render, shape, layout, elements); *color/tone* (cast, palette, value); *local* (one area); *technical* (alpha, canvas, pivot, seam).
3. **Choose the cheapest method that has evidence**, using the table. If the structure is acceptable, prefer deterministic methods (script, local edit) before you regenerate.
4. **With 2 or more hypotheses**, test them in sequence (the most likely or cheapest hypothesis first). Or test them in parallel when the budget allows and parallel is cheaper than the total number of rounds. In each branch, change exactly one factor. Do not raise the budget or the number of agents on your own to test in parallel.
5. When you have several options, **score them again at the same time** under the same conditions. Review the top 2–3 by eye. Choose one and record the reason.

## What to measure for each deliverable

The reference used for scoring must be **the same type** as the output.

| Deliverable | Reference to compare | Tool |
|---|---|---|
| Concept/scene | Execution reference of the same scene type | `preview.py compare`, `value`; `score_variants.py` |
| Icon/sprite/set asset | Approved set anchor in the same set | `preview.py sheet` (target size, game background), `compare`; `score_variants.py`; `inspect_image.py`; `sprite_check.py` for frames |
| Tile/background | Approved tile/background | `preview.py tile`, `compare` |
| Texture on a model | On-model render of an approved asset under the same lighting | `render_model.py` with several angles + `compare` |
| Edit of an existing image | Source image | `structure_diff.py` (keep shape), `inspect_image.py --lock-mask` (keep pixels) |

## Symptom → fix table

| Symptom | Measure | Try first | Try after | Do not | Confidence |
|---|---|---|---|---|---|
| Wrong render style (comes out as 2D illustration, painterly, semi-realistic…) | Eyes, `compare` | Regenerate **with an Execution reference image**. Name the correct target image type | Change or add a reference with the correct render style | Add style adjectives to the text prompt | medium |
| Palette is off across the whole image, structure is acceptable | `score_variants` cast_*, off_palette | `tone_match.py --bands shadows midtones`, then `structure_diff` to confirm the shape is kept | Edit "change only colors" with a color-standard image, then pull back with `tone_match` | Regenerate the whole image just for color; hex codes in the prompt; strong color adjectives | medium |
| Color is pulled by one reference with an off tone | Palette/`--profile` of each reference | Remove the off-tone reference or mark it "structure only" | Reduce the number of references | Add references "to have enough" | low |
| Dark areas/light have the wrong tone (brown instead of cool grey, orange instead of neutral) | `score_variants` dark_hue_gap, cast_shadows/highlights | `tone_match` on the correct band. Do not adjust the light band when the sky/highlight is already correct | Regenerate with a reference that has the correct light as the color standard. Check the render style again | Describe dark colors in words in the prompt | low |
| Odd details, elements outside the brief | Element inventory | Local edit to remove (use a mask if the tool has one). Use `structure_diff` to check the remaining parts | Regenerate with a clearer exclusion list | Keep it because it "looks good" | not tried |
| Set mismatch: line, viewing angle, detail level, light direction differ from the set anchor | `sheet` + `compare` next to the set anchor, same size | Regenerate with the set anchor of the set as the main reference | Local edit of the mismatched area | Compare with a scene reference instead of the set anchor | not tried |
| Construction/perspective wrong in one area | Eyes, zoom in | Local edit + restate the invariant. Use `structure_diff` on the area outside | Regenerate with a construction reference | Fix the color to hide it | not tried |
| Texture does not follow the form, seams show, light/gloss painted per atlas | `render_model` checker + textured, several angles | Fix on the UV/paint view following the form, then render again | Report the UV to the 3D Artist | Evaluate on the flat atlas | not tried |
| Sprite pivot/baseline drifts, canvas is off | `sprite_check.py` | Reset the canvas/pivot with a script | Regenerate the off frame with a standard frame as reference | Auto-crop each frame | not tried |
| Alpha lost, halo, fake transparent background | `inspect_image --require-alpha`, `sheet` on a dark background | Require a real transparent background. Remove the background again | — | Trust that an alpha channel is clean | not tried |

Color scripts (`tone_match`, `score_variants`) skip transparent pixels and keep alpha.

## Choosing an option

- **Eyes first** (required): correct render style, element inventory, generated-image fault table, [6-dimension self-check](../templates/review.md) (the art axes; the skill's own Self-check list covers the asset contract).
- **Numbers after, only to break ties**: measurements help eliminate clearly deviating options. They also break ties when the options look almost equal by eye. A lower `score_variants` total does not prove by itself that an option is better as art. The weights are uncalibrated estimates. Compare totals only within the same scoring run and the same reference. Color measurements do not see render style, personality, or expression.
- An edit must pass `structure_diff` if the request is to keep the shape.

## Recording lessons and when to stop

- Record the methods you tried, the before/after numbers, and the choice in the **task record**. Record style-specific or project-specific points (which reference is used only for construction, which fix worked) in the **Production notes section of the style sheet**. Do not edit installed skill files.
- If a finding seems generally true for a tool or error type, propose it to the owner with evidence so the playbook in the source repo can be updated.
- Stop according to the budget in the [quality standard](../rules/art-quality.md). If you tried 2 or more methods for one error type and none made progress, stop. Diagnose again and report a different method with evidence (hand edit in a DCC, change the tool/model, change the reference). Changing the criteria is a separate decision of the AD/owner. It is not a way to get a pass.
