# View match report

**Overall score: 67/100 — ❌ FAIL**

- Views to generate again: Back, Left, Right, Bottom
- Comparison image: `overlay_sheet.png` (red = AI image lacks it compared with the blockout, blue = AI image has extra, yellow = where material borders must be)

## 1. Each view against the blockout

| View | Score | Shape (IoU) | H/W ratio error | Detail position | Colour dE max | Verdict |
|---|---|---|---|---|---|---|
| Front | 99 | ✅ 0.994 | ✅ +0.1% | ✅ 100% (chimney) | ✅ 0.0 | ✅ |
| Back | 49 | ✅ 0.995 | ✅ +0.2% | ❌ 0% (window) | ❌ 66.4 | ❌ |
| Left | 68 | ✅ 0.991 | ❌ +11.4% | ✅ 100% (chimney) | ✅ 5.3 | ❌ |
| Right | 74 | ✅ 0.994 | ✅ +0.0% | ✅ 100% (chimney) | ❌ 40.3 | ❌ |
| Top | 96 | ✅ 0.999 | ✅ +0.2% | ✅ 100% (chimney) | ✅ 2.4 | ✅ |
| Bottom | 5 | ❌ 0.758 | ❌ +24.4% | ❌ 0% (window) | ❌ 39.6 | ❌ |

## 2. Do the views match each other

The orthographic silhouettes of two opposite views must be mirror images of each other. This part does not need the blockout.

| Pair | IoU after flip | H/W ratio difference | Verdict |
|---|---|---|---|
| Front ↔ Back | 0.994 | -0.1% | ✅ |
| Left ↔ Right | 0.988 | +11.4% | ❌ |
| Top ↔ Bottom | 0.758 | -19.4% | ❌ |

Cross-view proportion (Front H/W = Side H/D × Top D/W): error -2.0% ✅

## 3. Colour of each material across the views

dE (CIE76, lightness at half weight, because one material looks lighter or darker on a sloped or turned face): under 6 is almost invisible, 6–12 is visible side by side, over 12 is clearly different.

| Material | Reference | Front | Back | Left | Right | Top | Bottom |
|---|---|---|---|---|---|---|---|
| chimney | #A53D4C (front view) | ✅ #A53D4C (0.0) | ✅ #A63C4C (0.8) | ✅ #A93D4D (1.6) | ✅ #A73C4C (1.2) | ✅ #AB3D4D (2.4) | — |
| door | #44854A (front view) | ✅ #44854A (0.0) | — | — | — | — | — |
| roof | #A2911D (front view) | ✅ #A2911D (0.0) | ✅ #A2911C (0.3) | ✅ #B2A13A (5.3) | ❌ #B55917 (40.3) | ✅ #A18F1B (0.7) | ❌ #B66D46 (39.6) |
| sign | #4A5AA6 (front view) | ✅ #4A5AA6 (0.0) | ✅ #4D5AA3 (1.9) | ✅ #47569E (2.3) | — | — | — |
| wall | #AA653F (front view) | ✅ #AA653F (0.0) | ✅ #A96440 (1.0) | ✅ #AA6540 (0.5) | ✅ #AA6540 (0.5) | — | ✅ #AA6540 (0.5) |
| window | #6F3C86 (front view) | ✅ #6F3C86 (0.0) | ❌ #A96540 (66.4) | — | — | — | — |

## 4. What to fix

**Back**
- Detail 'window' is misplaced or missing: only 0% of its blockout border has a matching edge in the AI image; see the yellow lines on the overlay.
- Colour 'window' is off by dE 66.4: now #A96540, needs to be close to #6F3C86 (front view).

**Left**
- Proportions are stretched: the image is 11.4% taller/narrower than the blockout; ask for no crop and no stretch.

**Right**
- Colour 'roof' is off by dE 40.3: now #B55917, needs to be close to #A2911D (front view).

**Bottom**
- Silhouette differs from the blockout, IoU 0.76: see the red/blue areas on the overlay; generate again and stress 'keep the exact silhouette of the guide render'.
- Proportions are stretched: the image is 24.4% taller/narrower than the blockout; ask for no crop and no stretch.
- Detail 'window' is misplaced or missing: only 0% of its blockout border has a matching edge in the AI image; see the yellow lines on the overlay.
- Colour 'roof' is off by dE 39.6: now #B66D46, needs to be close to #A2911D (front view).

- Left and Right do not match each other (IoU after flip 0.99, ratio difference +11.4%): generate the lower-scoring view again and give the other view as a reference.
- Top and Bottom do not match each other (IoU after flip 0.76, ratio difference -19.4%): generate the lower-scoring view again and give the other view as a reference.

## How it is calculated

- The AI image and the blockout are both cropped to the object's bounding box and resized to one size, so absolute size and position in the frame are not counted as errors.
- Shape: silhouette IoU. Pass at 0.93 or more, warn at 0.88 or more.
- Ratio: height/width of the AI image against the blockout. Pass at 3% or less, warn at 6% or less.
- Detail position: for each material, the % of its blockout border that has a matching edge in the AI image (tolerance ±4 px on a 320 px frame). Chance matches on a busy texture are subtracted. The table shows the worst material. Pass at 75% or more.
- Colour: median colour of each material region, compared with the concept if `--concept-colors` is given, else with the front view. Pass at 6.0 or less, warn at 12.0 or less.
- View score = average of shape, ratio, detail and colour, scaled to 0–100. Overall score = 80% average of the views + 20% cross-view match (opposite pairs, cross proportion).
- Limit: small detail inside one material region (patterns, number of window panes) is not measured. Check these on the overlay or with vision_check.
