---
name: zps-texture-artist
description: "Router for textures on 3D models: picks Texture Planning, Surface or Texture Review when the texture task is unclear. Use for a general texture request (\"texture cho model\", \"việc texture\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Artist
This is a router. Choose the production skill, then read that skill. The router has no production process of its own. Intake, style, tools, self-check and handoff are in the chosen skill. If the task is already clear, go straight to that skill.

| Task | Skill |
|---|---|
| Choose how to texture a model; method not yet chosen | [Texture planning](../zps-texture-planning/SKILL.md) |
| Texture/material, atlas, trim, paint view; method already chosen | [Surface](../zps-surface/SKILL.md) |
| Feedback, diagnosis, confirmation of a revision | [Texture Review](../zps-texture-review/SKILL.md) |
| New design: motif, symbol, material that does not exist yet | Out of scope → Concept Artist / AD |
| Icon, sprite, background, UI art | Out of scope → [2D Artist](../zps-2d-artist/SKILL.md) |
| Mesh, UV, high-poly bake, vertex color assignment | Out of scope → [3D Artist](../zps-3d-artist/SKILL.md) |

If you cannot choose because it is unclear whether the method is already chosen, treat the method as not chosen and use Texture planning. If the user describes the task directly and gives no brief, the production skill writes a minimal brief with the [Artist Brief](../.art-production-support/templates/artist-brief.md) template and records the assumptions. Always record hidden parts that are not in the concept as inferred. For work outside your expertise, hand off with the [shared workflow](../.art-director-support/workflows/art-direction.md). Do not widen the output on your own.
