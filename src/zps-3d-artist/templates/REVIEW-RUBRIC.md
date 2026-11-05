# Visual review rubric — 3d-artist v0.3 (from art-3d-artist v0.1)

Use this for every review of a product that has a concept. The visual approver is the user, or the subagent `3d-critic` with a fresh context for each round. The critic receives only the review set for the step that is under review. The orchestrator uses this rubric to self-check before it sends the set. A self-check does not replace an independent approval round.

An orthographic concept (front/left/back/right) has no ConceptCam, so it has no `concept_compare.png`. Use the `overlay_*.png` files from `tools/self_build/render_views.py --input <final.glb> --mode critic` instead (concept in red, model in blue). `concept_compare.png` is required only when the spec has a ConceptCam.

In the self-build loop, the critic also receives the image set from `tools/self_build/render_views.py --mode critic` (`clay_*`, `normal_*`, `overlay_*`, `parts_*`, `prev_34`). Score item 1 (Mass) only on `clay_*` and `normal_*`, because texture hides mass faults (research_notes §2).

## Review set by step (the sender prepares it; file names follow the `render_rig`/`asset_checks` scripts; if no script exists, use equivalent images taken with the exact game camera and record the source)
| Component | File | Mass | Texture | Engine |
|---|---|:-:|:-:|:-:|
| Approved concept + brief (reading priority, game camera, allowed rotation angles, shading) | brief | ✓ | ✓ | ✓ |
| **Clay at the game camera** — view this first | `game_clay_crop.png`, `view*_clay.png` | ✓ | ✓ | ✓ |
| Measurement JSON: budget_use, coverage, IoU, dimensions | `mesh_check`, `concept_coverage`, `iou_check` | ✓ | ✓ | ✓ |
| Product at the game camera, real size and enlarged 2× | `game_albedo_crop.png`, `game_albedo_crop_2x.png` | | ✓ | ✓ |
| Concept \| product at the concept angle | `concept_compare.png` | | ✓ | ✓ |
| Rotation angles within the brief scope | `view*_albedo.png` | | ✓ | ✓ |
| uv / export JSON | `uv_check`, `export_check` | | uv | ✓ |
| Engine image at the game camera | engine screenshot | | | ✓ |

If the game camera is the same as the concept camera (the concept draws over the grey-box at the game camera), omit `game_albedo_crop.png`. Use `concept_compare.png` and `game_albedo_crop_2x.png`.

Do not send: the previous version, the work history, or the artist's explanations. If a component marked ✓ for the step under review is missing, the approver returns the review set to the sender and gives no conclusion.

## Viewing order — items 1 to 5 all block
| Item | Mass | Texture | Engine |
|---|:-:|:-:|:-:|
| 1 Mass | ✓ | ✓ | ✓ |
| 2 Silhouette, composition | ✓ | ✓ | ✓ |
| 3 Reading priority | mass part | ✓ | ✓ |
| 4 Look | | ✓ (except lighting) | ✓ |
| 5 Rotation angles | mass part | ✓ | ✓ |

Write an item that does not belong to the step under review in "Not checked". Do not count it as a fault.

1. **Mass (look only at clay at the game camera).** Does the clay show the mass language of the concept? Check the large chamfer faces, the sub-masses, and the slope of the top face. A mass that is round, has too few faces, or looks "like a loaf of bread" is `not passed`, even if the texture is good. View the clay first, so that a projected texture does not hide the rough mass.
2. **Silhouette and composition** at the concept angle and the game camera: large outlines, proportions, front/back position, and occlusion. An IoU below `iou.min_iou` in the spec is `not passed`. A high IoU does not prove the mass is correct (with M1, IoU is almost always high).
3. **Reading priority** at the game camera and real size: does each line in the brief read or not? The mass step considers only the lines that belong to the form.
4. **Look** compared with the concept: color, line, material, and level of detail. For the engine image, check the lighting twice, following the shading in the brief.
5. **Rotation angles within the brief scope:** no stretched streaks, no obvious repeating patches, no empty faces, and no objects that poke through each other. The mass step considers only objects that poke through each other and missing faces. Outside the brief scope, record only a comment.

## Record the result
```
STEP: mass | texture | engine
VERDICT: pass | not passed
Faults (largest first):
- [item 1–5] [location] → [how it differs from the concept] → [what to fix] → [sign of pass]
Minor fixes with "pass" (only technical faults that a script measures: pivot, object name, UV padding, size within tolerance; record the script + threshold):
Keep: [what already matches the concept]
Not checked: [...]
```
If there is one fault in items 1–5, the verdict is `not passed`. A fault that you see by eye is not a minor fix. The task giver (or the artist, when the task giver allows it) checks a minor fix by running the recorded script again. If it passes, keep `pass` and do not review again. One step can have only one `pass` with minor fixes.

## Examples (from test 1 and the M1 trial)
- Wrong: "Pass with conditions: body L is like a bucket; fix in the mesh step." → This is a mass fault (item 1). It must be `not passed`.
- Wrong: "The image at the concept angle is identical to the concept, IoU 0.98 → pass." → With M1, both of these are true already. You must view the clay at the game camera.
- Right: "not passed. [1] RockL at the game camera → the clay is a round mass, but the concept has about 8 large chamfer faces and 3 leg masses → cut more chamfer faces as in the concept → the large chamfer faces are clearly visible in the clay at the game camera."
