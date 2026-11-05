---
name: zps-2d-artist
description: "Router for 2D game art: picks Asset 2D, UI or 2D Review when the type of 2D work is unclear. Use for a general 2D or UI request (\"làm asset 2D\", \"việc 2D\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 2D Artist
This is a router. Choose the production skill, then read that skill. The router has no production process of its own. Intake, style, tools, self-check and handoff are in the chosen skill. If the task is already clear, go straight to that skill.

| Task | Skill |
|---|---|
| Icon, item, sprite, frame, tile, decal, background | [Asset 2D](../zps-asset-2d/SKILL.md) |
| Button, panel, frame, HUD, bar, 9-slice, UI handoff spec | [UI](../zps-ui/SKILL.md) |
| Feedback, diagnosis, confirmation of a revision | [2D Review](../zps-2d-review/SKILL.md) |
| Explore a new design; character/prop not yet approved | Out of scope → Creative Brainstorming / Concept Artist |
| Texture/material on a model | Out of scope → [Texture Artist](../zps-texture-artist/SKILL.md) |
| Screen flow, wireframe, game rules | Out of scope → UX/game design |

If you cannot choose because the output type is missing, ask exactly one question about the output type. If the user describes the task directly and gives no brief, the production skill writes a minimal brief with the [Artist Brief](../.art-production-support/templates/artist-brief.md) template and records the assumptions. For work outside your expertise, hand off with the [shared workflow](../.art-director-support/workflows/art-direction.md). Do not widen the output on your own.
