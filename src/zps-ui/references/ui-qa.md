# UI QA by risk

Choose checks by output and risk. Do not replace a visual check with a file name or an exit code. Record the required checks and the extra checks. Do not lower a required check on your own when a tool is missing.

| Risk | Representative case | Tool |
|---|---|---|
| Text overflow | Longest string, Vietnamese text with diacritics, fallback, edge scale | Render with the real string |
| HUD hard to read | Light/dark/busy background, moving frame | `preview.py compare` on a game background image |
| Layout breaks | Narrow/wide aspect ratios within range, safe area | Render at the committed aspect ratios |
| Frame/asset fault | 9-slice at min/max size, alpha on light/dark background, crop | `preview.py sheet`, `inspect_image.py` |
| Wrong touch | Actions close together, occlusion by the hand | Measure the touch area after scaling |
| Unusable source | Change to a long text, replace an icon, resize one component, then export again | Record the result of the new export |
| Incomplete handoff | The recipient rebuilds one component from the source + spec only | Self-review; state clearly that it is a self-review |

Do not require a single-icon task to run a layout test. Record the reason as N/A. One passing sample does not confirm every size or state.

**Result:** pass / fail / not_checked / not_applicable (with a reason). **Severity:** blocker / major / minor, as in the [review template](../../.art-production-support/templates/review.md). Approval is a separate status.

**Validity:** for each check, record the version, environment, size, data, criterion and evidence. If you change the layout, token, font, asset or render setting, mark the affected checks as needing a new run. An old PASS is not current evidence.

Three confirmation levels are separate: design checked; compared in Godot; tested on a device. Do not use one level to confirm another. For the Godot/device part that is not done, record who does it next. It does not count as PASS.
