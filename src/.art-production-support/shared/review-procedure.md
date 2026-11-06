# Review procedure (2D Review and Texture Review)

1. **Look.** Open the real image or render. Look at the whole, inspect the area that explains your judgment, then look at the whole again.
2. **Art and style fit.** Use the relevant dimensions of the 6 (composition, shape/silhouette, color/value, lighting, material/texture, visual appeal), separate from the technical checks. Measure a color finding before you state it ([color](color.md)).
3. **Specialist checks** of your skill.
4. **Generated parts:** check the [fault table](gen-craft.md#typical-faults-of-generated-images). A detail that you cannot trace to the brief is an issue.
5. **Record.** Quick review: a few issues with evidence, no score or ID. Tracked review or acceptance: the [review template](../templates/review.md), with acceptance as yes/no checks. Prioritize the 1–3 items with the largest impact.
6. **Revision round:** keep the id. Set `resolved` only when new evidence under the same conditions proves the acceptance. Look for regressions and lost strengths.

**When a production skill calls you:** run the review in a new subagent if the environment allows. Give it only the artifact, brief, style sheet, set anchor or method, and contract; record an independent review. Otherwise record a self-review. The production skill fixes the issues; the next round checks only open issues and regressions, within the task budget.

**Output order:** strengths to keep; priority issues; next steps and who does them; parts without enough evidence; verdict (meets_checked_criteria / needs_revision / insufficient_evidence). Say if it is a self-review. The verdict is not AD approval.

**Rules:** do not invent faults; "no fix needed" is valid. If asked to fix, hand the issues to the production skill. Record an out-of-scope issue with its owner; do not fix it. Without a Bible, review against the brief and mark project fit provisional.

Only when needed: [review request](../templates/review-request.md) for another reviewer, [deep method](visual-review.md) for many criteria or rounds, [technical gate](scripts/README.md#evidence-gate) for machine-readable acceptance.
