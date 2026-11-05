# Review — quick or tracked (same issue fields as the AD)

The issue fields, priority levels, and verdict come from [issue-fields.json](issue-fields.json). The AD `artistic-critique` uses the same set, so an issue that the artist records can pass directly to the AD and the other way around.

**Quick:** artifact/version + viewing conditions → strengths to keep → 1–3 issues that have impact + repair direction → parts with insufficient evidence.

**6-dimension self-check** (same axes as AD `visual-intelligence`): composition · shape_silhouette · color_value · lighting · material_texture · visual_appeal. For each dimension: pass / deviates (why) / not applicable / not checked.

**Tracked** when there are many defects, many revision rounds, or the AD asks:

| id | priority | region | viewing_condition | evidence | consequence | confidence | repair | preserve | acceptance | status |
|---|---|---|---|---|---|---|---|---|---|---|
| I-01 | blocker | sword hilt | 64px, dark panel background | red gem is not in the brief | wrong item tier | high | remove the gem, keep the hilt form | blade silhouette | at 64px no red dot remains on the hilt | open |

`priority`: blocker (a mandatory requirement or essential gameplay distinction fails) / major (significant quality or consistency) / minor (local polish) / preference (taste, record separately).

`status`: open / resolved / superseded (the AD changed the requirement) / regression. Keep the `id` across versions. Mark `resolved` only when the new artifact proves the `acceptance`.

Verdict: meets_checked_criteria / needs_revision / insufficient_evidence — limited to the parts that were checked. State clearly whether it is a self-review or another reviewer. The verdict is not AD approval or permission to ship.
