# Review with evidence

## Three independent axes

1. Art: overall impression, rhythm, personality, expression, and the relations between shape, color, edge, and material.
2. Brief fit: locked parts, style, and the questions that this stage has resolved.
3. Usability: file/mapping/import, and how it looks under the target conditions.

Read the whole, inspect, then read the whole again. Inspect only the areas that can explain or reject a judgment. Separate the observation (what the eye sees), the interpretation (possible causes), and the judgment against the goal. Do not infer topology, resolution, or performance from an image. Grayscale does not replace a visual color check. A still image does not prove motion or player reaction.

## Checks by branch

Concept: a distinguishable idea, silhouette/negative space, proportion/construction, perspective/foreshortening, hierarchy, and modeling questions. Environment adds paths/scale. Character adds gesture/identity across views. Prop adds function/joints.

Surface: material areas, stroke direction/scale, detail rhythm, art intent. Geometry/UV/normal/shader can cause the same appearance, so tell them apart. Check neutral and target lighting, other angles, and mip/compression if they are in scope. A good flat texture does not pass on-model.

Asset 2D: alpha/pivot/canvas/frame, consistency within the set, display size, and real background. Mark parts that lack evidence as not_checked. Do not judge them as defects or as passing.

UI: it matches the approved wireframe, order of attention, enough states, long text and Vietnamese text with diacritics, 9-slice at min/max size, and touch area after scaling. A safe area preview does not replace a device test. Record flow/UX problems for UX/game design. Do not score them as art defects.

## Revision round

When you track several rounds, or when the caller asks, give each important issue an ID, location/state, condition, evidence, impact, causal hypothesis, repair direction, strengths-to-preserve, and observable acceptance. A blocker is a mandatory requirement that fails at this checkpoint. A major issue significantly affects quality. A minor issue is polish. Record a preference separately. Do not block a rough concept only because final detail is missing.

Lock the artifact, the brief, and the comparison conditions. When the AD changes a requirement, mark the issue superseded with the reason. Do not count it as a fixed defect. After a fix, check for regression and check the overall idea. The reviewer proposes methods. The reviewer does not force the artist to use an exact technique if the result passes.

## Honest verdict

A self-review is not AD approval. An independent review needs a real separate context/reviewer. Do not claim independence by changing persona. The conclusion is meets_checked_criteria, needs_revision, or insufficient_evidence, limited to the stage. Use the [technical gate](scripts/README.md#evidence-gate) only when the caller asks for machine-readable acceptance. The required IDs are an agreed configuration. Do not drop them to get a pass. Do not mix missing or stale evidence with not_applicable. If you give a score, it must have a rubric and must not hide a blocker. Do not look for defects to fill a quota.

## Yes/no checks, not scales

- Write acceptance as 3–6 yes/no checks that someone can observe ("Is the silhouette readable at 64 px on the dark background?"), not as a 1–10 score. Two reviews of the same image then give the same answer.
- Each check names its evidence (image, size, background, tool output).
- If every check passes but the result is clearly not better than the previous version, the checks are wrong. Fix the checks before the next round. Do not pass the image.
