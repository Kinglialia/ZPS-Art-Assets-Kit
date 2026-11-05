---
name: zps-visual-intelligence
description: "Analyze or compare game-art images and say why they work and what to improve, with or without a brief. Use for quick opinions and image analysis (\"phân tích ảnh\", \"ảnh này đẹp không\", \"so sánh hai ảnh\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Visual Intelligence

**Not for:** acceptance reviews or issue tracking (zps-artistic-critique); in-game 2D or UI review (zps-2d-review); textures on models (zps-texture-review).

Understand how an image works, what gives it character, and which changes would meaningfully help. Preserve successful choices. Artistic judgment goes beyond technical correctness or a checklist of isolated features.

## Establish the evidence

Open the actual images before making visual findings. Identify the relevant artifact, version and viewing limitations briefly. Filenames, descriptions and extracted text do not establish visual access. If an image cannot be inspected, explain what remains unassessable and discuss only the supplied information.

Identify the question, intended use, production stage and supplied brief or references. Ask only for missing information that would materially change the judgment; continue what can be assessed. Without a brief, analyze visible construction and expression while keeping project-fit judgments provisional. Do not invent platform, audience, camera, budget or style requirements.

## Read, inspect and judge

1. **Read the whole.** Establish an initial reading of hierarchy, large shapes and value groups, mood, character and overall appeal. Treat this as a hypothesis, not a verdict.
2. **Inspect selectively.** Examine the features that could explain that reading and evidence that could contradict it. For an important finding resting on an ambiguous detail, revisit the relevant region or view at a useful scale if tools permit. Do not turn every assessment into an exhaustive inspection.
3. **Judge relationships.** Explain how elements reinforce, compete with or undermine one another. Do not infer overall quality by adding independent feature ratings. Reconsider the whole after inspecting details.
4. **Recommend.** Prioritize consequential improvements, explain their tradeoffs and protect what works. A specific local change is welcome when supported; no change is a valid recommendation.

Use only relevant dimensions:

- **Composition and hierarchy:** focal relationships, grouping, figure–ground separation, balance, rhythm, negative space and competing emphasis.
- **Shape, form and space:** silhouette, proportion, gesture, volume, overlap, perspective and spatial relationships, judged within the visual language.
- **Color and value:** hue, saturation, light–dark organization, harmony, contrast and relationships with surrounding colors.
- **Lighting:** form description, emphasis, depth and mood.
- **Material, texture and edges:** perceived material qualities, detail distribution, and sharp, soft or lost edges in relation to the whole.
- **Visual appeal and expression:** personality, vitality, emotional reading, coherence, unity and variety, restraint or exaggeration. Explain the visible choices supporting the reading; allow valid competing interpretations.

## Make the reasoning accountable

For each consequential finding, connect a specific feature or region to a visual mechanism and its likely effect. Separate:

- **Observation:** what is visible in the inspected image.
- **Interpretation:** a plausible reading or causal explanation.
- **Judgment:** why it helps or harms artistic quality or the stated purpose.

Distinguish artistic construction and expression from suitability for a project. A beautiful image may be unsuitable for its intended use; meeting a brief does not establish artistic excellence. Treat inferred intent as a hypothesis unless supplied by the owner or source.

Do not maximize contrast, clarity, detail, realism or consistency by default. Consider what each proposed change would gain and lose. Ambiguity, distortion, asymmetry and irregularity can carry expression; assess their effects rather than automatically correcting or excusing them as deliberate stylization.

When readability matters, inspect supplied target-size, camera and background conditions where available. Distinguish findings in the provided view from risks needing in-game verification. Claim thumbnail, grayscale or other diagnostic checks only when performed; each answers a limited question. Grayscale does not substitute for color-vision testing. When color carries essential information, consider supporting shape, icon or pattern cues where relevant.

Appearance alone does not identify implementation. Distinguish perceived material from material correctness; lighting, exposure and tone mapping can produce similar symptoms. Never infer topology, polygon count, texture resolution or performance from a render alone. A still cannot establish motion readability, player behavior or measured attention. Label predictions and causal hypotheses; avoid invented measurements or confidence percentages.

Discuss distinctiveness relative to inspected references when available, without certifying originality, authorship or rights from appearance. Compare images under reasonably equivalent conditions and disclose material mismatches. Do not let prestige labels, prior verdicts or requests for criticism replace visual evidence.

## Respond at the useful level

Lead with the main assessment, then include strengths to preserve, a few prioritized findings and recommendations, and material uncertainty. Adapt the format and depth to the question; do not force every dimension or a quota of issues. Avoid generic praise and vague fixes such as “make it pop.” Numerical scores require an explicit rubric and sufficient evidence.

If evidence is missing, leave the affected conclusion open rather than declaring failure or no changes needed. Explain expressive readings with appropriate confidence without presenting them as universal audience reactions.

Specific improvement advice is within scope; a quick assessment needs no issue IDs. For acceptance checks or revision tracking, Artistic Critique owns the review and includes visual reasoning in that same pass; do not create a separate preliminary report by default. Keep any material decision tied to its artifact/version. 

For combined tasks, use the [Art Direction workflow](../.art-director-support/workflows/art-direction.md) to route work and carry decisions forward. Individual tasks do not require every skill.
