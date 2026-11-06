# Set anchor

Shared by Asset 2D, UI Art, and 2D Review. The set anchor is an asset that the **AD or user has approved**. It is the measuring standard that keeps the other assets in the same set consistent: viewing angle, line thickness, detail level, light direction, scale, and padding. For UI, the anchor is the visual direction or the screen that was chosen.

## When there is no anchor

- **Make the whole set** and present the whole set for one approval. Make an anchor first only when the user asks.
- **First asset or single asset:** compare with the brief and the style sheet. Record set consistency as `not_checked`.
- **Whole set made at the same time:** put all assets side by side at the same display size (`preview.py compare` or `sheet`). Check consistency **within the set**.

## When there is an anchor

Compare each asset with the anchor at the same size and on the same background. Do not compare with the concept or a scene reference in place of the anchor.

## Record the anchor after approval

When the AD or user approves an asset or a whole set, record the set anchor. If a whole set is approved, choose one representative asset. Store the record on the project side. Never store it in the skill folder:

| Situation | Where to record |
|---|---|
| The project has a style sheet or an Art Style document | The Production notes section of the style sheet |
| The project has only an AD Art Bible (no artist style sheet) | A `_set-anchor.md` file placed next to the asset set. Do not edit the Bible |
| The project has no style sheet | A `_set-anchor.md` file placed next to the asset set |
| Global call, no project | Record it in the delivery result. Next time, the user sends the anchor image again |

What to record: the set name, the anchor file and version, the approver, the date, and the scope (for example "anchor for line and detail level, palette not final yet").

Before you add to a set or review a set, look for the anchor in the exact order of the table above.
