---
name: zps-concept-artist
description: "Draw or revise concept art for 3D game assets: grey-box paint-over from the game camera, clear forms, hidden parts and extra views for the modeler. Use for concept images (\"vẽ concept\", \"paint over grey-box\", \"vẽ thêm view\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Concept Artist

**Not for:** brainstorming ideas (zps-creative-brainstorming); writing a brief (zps-art-bible-artist-direction); 2D images placed in the game (zps-asset-2d).

Turn direction into a visible concept that is clear enough for the modeler. The AD can set direction and draw the concept in the same task.

## Set the scope from existing information

Use the current brief, style decisions, and approved scope. Do not make the user fill in a form again. The [Concept brief](templates/CONCEPT-BRIEF.md) is an optional template for recording missing information and for the handoff.

Identify: the asset function, the gameplay information that must be readable, the silhouette/features to keep, the camera and display size, the shading, the image/grey-box source, and the output to deliver. Ask only when the missing information could make the design wrong or block the next step. You can make an exploratory version with clearly recorded assumptions. Do not set engine parameters on your own. Do not treat a temporary style as final.

If there is no direction yet and the user wants to explore, Creative Brainstorming helps choose ideas. The Concept Artist can make test images labeled provisional. Rules that apply across many assets belong to Art Style Development. Do not force those two skills to run before every drawing.

## Draw or revise a concept

- Open the source image before you edit. For a grey-box paint-over, keep the camera, framing, proportion, and locked forms. If the request requires changing a form, state clearly which parts may change. If there is no grey-box, use the camera that was provided. If the camera is not defined, record the illustration angle. Do not claim that it matches the game camera.
- Form before detail. The silhouette, the large planes, and the secondary forms must be readable at game size, when the size is known. Do not let surface detail hide the structure.
- Separate the presentation form from the output used for modeling. For an image used for projection/texture, avoid a background shadow close to the feet, because it can be mistaken for bottom color. Use a plain background or alpha, according to the output. A presentation image can have a contact shadow, but do not use that same version as a projection texture. Objects in a group need enough outline to separate them.
- Shading by pipeline. For unshaded, bake lighting only by the agreed convention. For lit, separate the lighting of the presentation image from the base color/albedo used in production. Do not put highlights and cast shadows into the albedo by default. A shaded concept that expresses form is still valid. If the pipeline is not clear, keep this as an assumption. Do not force one general formula.
- If the scope includes rotation, or the modeling request needs hidden parts, add views/details when useful. Keep the views consistent with each other. Record what is inferred and what is unresolved. Do not invent dimensions. A measurement must have a unit, a reference point, and a source or an estimate label.
- For a revision, record **Source / Keep / Change** and create a new version. Keep the approved version. A new user request can change the old scope, but a revision does not automatically become a shared standard.

Use the available image generate/edit tools and the instructions of that tool. If you cannot create images, deliver the brief/prompt and report that the image part is not done. Do not call a prompt a finished concept. Do not expand into model building or texture production on your own.

## Check and handoff

Open the actual result. Check the silhouette, the forms, the locked details, the framing, and the readability at the size provided. Do not claim a numeric match to the camera from a generated image alone. Record the deviation and the need for verification when you cannot compare. For a multi-view sheet, check whether identity and construction are consistent.

Deliver the concept image/PNG used for modeling, the version, the source camera/grey-box, the hidden parts/assumptions, and the questions that affect modeling. Deliver a layered file or an alpha background only when you really created it and can check it. If the tool exports only a flat image, say so. If a layered source is a mandatory requirement, state what is missing.

Keep three states separate: the self-check that was done (not an independent review), art approval by the designated person, and confirmation by the modeler that the modeling information is sufficient. Do not fill in the name/date of an approver or confirm on behalf of another person. A good concept does not prove topology, budget, or engine import ability. Do not apply a default number of revision rounds or a default cost. Use the limit that was assigned.

Artistic Critique supports review or revision tracking when needed. Art Bible & Artist Direction only turns agreed decisions into guidance. See the [AD workflow](../.art-director-support/workflows/art-direction.md) for combined tasks.
