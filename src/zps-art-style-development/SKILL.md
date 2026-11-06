---
name: zps-art-style-development
description: "Turn a chosen art direction into clear, testable style rules and test them on new assets. Use for style rules, style sheets and style tests (\"phát triển style\", \"chốt rule style\", \"style guide\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Art Style Development

**Not for:** exploring new directions (zps-creative-brainstorming); writing the Bible or a brief (zps-art-bible-artist-direction).

Develop visual rules from the supplied direction and relevant evidence. If the direction is provisional, keep the resulting rules provisional; missing formal research is not an automatic prerequisite to drafting. Preserve locked identity choices. Reopen them only when the owner requests it or evidence reveals a material conflict; explain that conflict before proposing a change.

## Establish the working contract

Read the available brief, direction, references and assets; reuse the recorded decision and approval scope instead of repeating completed discovery. Identify the target camera, display sizes, asset families, gameplay priorities and actual production limits. Separate supplied facts from assumptions and unresolved decisions. Ask only for unknowns that would materially change the design; continue independent work.

Choose whether the task is initial development, targeted refinement, or extension of an existing style. In refinement, record the existing baseline and the specific problem. Do not replace the whole style merely because another aesthetic is appealing.

## Define rules artists can apply

Identify core visual relationships, allowed variation and exploratory choices. Each important rule must serve a visual goal; incidental anchor details are not requirements. Preserve meaningful variety across assets.

Translate desired feelings into concrete choices in silhouette, proportion, palette/value roles, lighting, materials, texture/detail and composition. Cover only relevant domains, including UI/VFX where they affect the visual system. For each consequential rule state its scope, rationale, inspection condition and allowed variation. Give ratios or values with units and reference size when useful; do not invent measured values from images.

State the intended visual effect before a tool-specific recipe. Tie implementation values to the tool, asset scale and inspection conditions. When tools or rendering conditions change, recheck the effect rather than assuming identical values reproduce it. If the target implementation is unknown, separate established visual intent from unverified implementation.

Distinguish a rule's origin (observed or proposed), owner approval and validation evidence. A prompt is an implementation aid, not the authoritative style definition. References supply principles, not permission to copy recognizable content or use their assets in production.

Define shared parent rules and justified adaptations by domain or display size. An icon and a large character need not use identical line widths. Explain which identity features survive simplification. Do not impose a universal palette count, rendering technique, prohibition on black/white, or association between genre and contrast.

For palette rules, describe color by character: lightness and chroma set the mood more than hue angles. State the share plan (for example 60/30/10) and which color the player must see first. Give palette values in OKLCH, measured from the anchors. See [color](../.art-production-support/shared/color.md).

When rules conflict, resolve by the brief's priorities and show the trade-off. Mark unresolved conflicts instead of hiding them under adjectives. Do not fabricate polycounts, staffing costs, rendering performance or production budgets; use supplied constraints and label estimates.

## Test the system, not only a hero image

Choose tests for the change being made. For a targeted refinement, inspect affected assets and likely regressions. For development across asset families or a claim of transfer, include a new subject not used to define the rules and a small representative set that exposes likely failures: confused gameplay elements, materials, relevant UI states or a busy composite. Do not require a new-subject test for every local edit; without one, leave transfer unverified.

Test relevant high-risk conditions such as lighting, distance, background, pose or effect density. State what must survive and what may adapt. Do not require all combinations or engine tests for purely visual exploration.

Use available, authorized creation tools or existing artifacts to produce visible evidence. If only a written proposal is possible, deliver it as unvalidated with a concrete test plan. Never substitute a text prompt for a rendered result or claim an asset was inspected without opening it.

For comparisons, keep subject, camera, framing, display size and other irrelevant variables equivalent. State intended differences and any uncontrolled variables. Inspect native-size context as well as enlargements. Still images do not validate animation, interaction, engine integration or production throughput.

Evaluate both compliance with the rules and retention of the chosen direction's feeling, character, hierarchy and appeal. Compare with relevant anchors under comparable conditions and account for production stage; a blockout is not expected to match finished key art. If compliance loses the intended appeal, reconsider the rules instead of automatically adding more.

Diagnose failures before changing rules: ambiguous instructions, incorrect execution, legitimate adaptation, rule conflicts or evidenced technical limits. If uncertain, record competing causes and a discriminating test. Generated-image noncompliance does not prove style infeasibility; do not rewrite valid rules to excuse a faulty sample.

Record which rules survived, failed, or needed exceptions. On new-subject tests, record missing decisions and actual effort if observed; distinguish estimates. Make the smallest justified rule change, check affected domains again, and retain useful earlier evidence. Do not iterate indefinitely: honor the agreed budget and report remaining uncertainty.

## Handoff and status

Deliver the relevant working rules, anchors, evidence and trade-offs. Suggest a next test only for a consequential remaining uncertainty. Use locators accessible to the recipient, including portable relative paths for an offline handoff.

Record approval (proposed/owner-approved) separately from validation (untested/tested within a named scope). A successful test does not approve a rule; only an executed new-subject test supports transfer. Hand rules and their status to Art Bible & Artist Direction, research gaps to Visual Research and asset issues to Artistic Critique when useful. These are responsibilities, not mandatory installed dependencies.

Combined tasks: [Art Direction workflow](../.art-director-support/workflows/art-direction.md). A single task needs only this skill.
