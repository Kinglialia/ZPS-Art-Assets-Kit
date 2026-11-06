---
name: zps-art-bible-artist-direction
description: "Write a versioned Art Bible or an Artist Brief with references, deliverables and acceptance checks, from approved style rules. Use for production handoff (\"viết art bible\", \"viết brief\", \"giao việc artist\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Art Bible & Artist Direction

**Not for:** first style exploration (zps-creative-brainstorming, zps-art-style-development).

Make approved visual decisions usable by an artist who was not in the discussion. Produce the requested artifact: a shared Art Bible, an Artist Brief for a specific task, or a scoped update. Do not force both when one suffices.

## Ground the handoff

Reuse the current decision record: artifact/version, settled decisions and approval scope, evidence/limits and open decisions. Check relevant source artifacts, asset use and delivery constraints; do not repeat completed discovery or treat a summary as visual access. Resolve contradictory sources through current owner decisions; record unresolved conflicts and do not silently pick a new style.

If style development is incomplete, document stable decisions and mark provisional rules and missing approvals explicitly. Do not describe the document as production-ready while core choices remain unknown. Authoring a document does not approve its contents.

## Build an Art Bible that directs decisions

Organize by the asset families the team actually produces. Keep shared rules in one authoritative place, with domain adaptations linked to them. Include:
- Visual goals and ranked priorities; what must remain recognizable.
- Shape/proportion, palette and semantic color roles, value hierarchy, lighting/material and detail treatment as applicable.
- Camera and scale-dependent rules, including which features must survive at gameplay size.
- Relevant character, environment, prop, UI and VFX adaptations and states.
- Annotated anchors and diagnostic do/don't examples, explaining the consequence of each choice.
- Known delivery requirements, acceptance checks, version/status and unresolved decisions.

Do not fill absent domains with generic prose. A palette swatch needs a usage rule (role, share, what it is attached to in the world); a value needs units and context. Write palette values as hex plus OKLCH, measured with `palette_report.py` ([color](../.art-production-support/shared/color.md)). Distinguish normative rules from examples and artist discretion. Retain bounded exceptions with their rationale. Prefer images that demonstrate a rule; if an image cannot be accessed, mark the gap rather than claim it was reviewed.

For important anchors, name the authoritative aspects and exclusions: proportion approval does not approve palette or lighting. Resolve image/caption/rule conflicts using current owner decisions, mark superseded guidance and record remaining conflicts. Stable portions can proceed independently.

## Write a scoped Artist Brief

State the asset's purpose, player-facing function, place in the world and target viewing context. Name the Bible version and only the applicable rules. Specify what is fixed and what the artist should explore, with references annotated by role rather than a request to imitate an entire game.

List the actual deliverables: subject/variants/states/views, source editability, format, pixel dimensions or world scale, transparency and handoff location where supplied. Record known production constraints such as topology, texture or rig requirements without inventing numbers. Screen dimensions are pixels; print DPI alone does not define a game asset's size.

Identify the recipient/stage and relevant known dependencies needed to reproduce the result: textures, fonts, rigs, materials, tool versions, presets, scale or attachments. Tailor these to the deliverable; do not invent pipeline requirements.

Include review checkpoints appropriate to the task, the named approver if known, and acceptance criteria observable in the target context. Do not invent deadlines, revision allowances, usage rights or contractual terms. Mark missing facts and ask when they block production; a draft can still advance while those facts remain open.

For each necessary checkpoint, state its decision, required evidence and approval scope. A thumbnail may settle silhouette while leaving color open; do not impose a fixed review sequence.

Track artistic approval, technical verification and delivery completeness separately. An approved preview does not establish that source files open correctly or that an asset works in-game. Specify the required checks without claiming they were performed.

## Check that another artist can use it

Audit rule consistency, units, link targets and version references. Use recipient-accessible links/IDs or portable relative paths in a supplied offline package; do not require a machine-specific path or a hidden conversation. Separate reference rights from ownership of the intended output. Do not alter sharing permissions merely to make a link convenient.

Report the actual verification level: file inventory checked, source opened, asset imported or result inspected in-game. Do not treat one as evidence of the others; record missing dependencies and relevant access limits.

When handoff reproducibility must be evaluated, a meaningful test gives a fresh maker the Bible/brief and a new subject without exploratory chat. Check what they had to guess, whether the result follows rules, and what failed at target scale. Only claim this test if it was actually run; an editorial read-through is not evidence of reproducibility.

Keep rules versioned. For changes, state the changed rule, reason, affected asset families and which examples need rechecking. Do not overwrite approved anchors or quietly promote proposals. 

Separate corrections from changed requirements. Record an owner change, the superseded decision and affected assets/documents; prior compliance is not a retrospective error. Apply changes within authorization. Keep asset-specific exceptions scoped and explained instead of promoting them to global rules.

Deliver the requested document with the decision-record fields listed under Ground the handoff. A documentation-only task does not require commissioning a fresh-maker test. Style decisions requiring exploration return to Art Style Development; critique findings can drive revisions but do not themselves change the approved Bible.

Combined tasks: [Art Direction workflow](../.art-director-support/workflows/art-direction.md). A single task needs only this skill.
