# Gen craft — write requests for generate/edit tools and find generated-image faults

Read this before you call a tool that creates or edits images, and when you self-check the output. It applies to every tool (the session's image tool, image APIs, masked edit; the [adapter](../adapters/runtime.md) names the tools of this app).

## Contents
- Write the request
- Request template
- Errors and paid calls
- Typical faults of generated images

## Write the request

1. **Give the Execution reference image to the tool** when the tool accepts images. State the role of each image (Image 1: style/color standard; Image 2: structure only…). Words that describe a style do not replace an image. A prompt with text only tends to drift to another render style.
2. **Choose references by color.** The model follows the colors of an image more than hex codes. If a reference has a tone that differs from the style sheet, remove it, or write "structure only, ignore its colors".
3. **Name the correct target image type** for the deliverable: "in-game screenshot of a real-time 3D game", "game UI icon on transparent background", "tileable texture, flat lighting"… The words "concept art", "illustration", and "keyframe" pull the result toward a painting.
4. **Describe with concrete nouns**: object, material, viewing angle, layout. Do not stack adjectives. "Epic, highly detailed, intricate" is a command to add detail. Experience with the tools tried so far (not tested widely): strong color adjectives ("vivid", "saturated", capitalized color names) often make the color exceed the target. When you have a color-standard image, prefer "match the colors of Image N".
5. **Always state exclusion constraints**: no text, no logo, no accessory or effect outside the list, background as set by the contract.
6. **Edit**: write "change only X; keep everything else unchanged" and repeat it in every round. Change one thing per round: two changes in one round make it impossible to tell which one broke the image. Use a mask when the tool has one. When the request is to keep the shape or layout, run `structure_diff.py` against the source image. If the task intentionally changes the structure, compare by eye the areas that must stay.
7. **Record** the prompt, the input images and their roles, the tool/model, the parameters and the seed (when the tool has one) in the task record, for every variant that you score or show. The chosen variant must be possible to rebuild.

## Request template

Write the request in labeled lines. Leave out a line that has nothing to say. Do not add objects, text, logos or brand elements that the brief does not ask for. Add your own detail only when the brief is generic, and say what you added.

```
Use case: <game asset / UI element / texture / concept sheet>
Asset type: <icon 128 px, transparent background | tileable 512 texture | ...>
Input images: Image 1 = <role: style and color standard>; Image 2 = <role: structure only, ignore colors>; Image 3 = <role: edit target>
Subject: <concrete nouns: object, material, parts>
Style: <match the colors and rendering of Image 1>
Composition: <view angle, framing, position, empty margin>
Constraints: <size, background, palette, change only X; keep Y unchanged>
Avoid: <text, logo, extra accessories, glow, particles, ...>
```

## Errors and paid calls

- If the tool returns an access, quota, billing or policy error, stop. Report the error to the user. Do not change the model, the provider or the prompt to get around it without the user's approval.
- Ask before you generate extra variants beyond the agreed count.

## Typical faults of generated images

Open the image at the target size **and** zoom in on the detail areas. Set the level with the review template. **blocker**: the fault breaks a mandatory requirement, or breaks gameplay readability/distinction under the target viewing conditions. **major**: the fault significantly affects quality or consistency. **minor**: the fault is only polish. A visible fault is not automatically a blocker. An added element outside the brief must still be recorded and handled.

| Group | Signs to catch |
|---|---|
| Added elements | Patterns covering every surface; gems, cords, belts, handles without a function; duplicated motifs; light particles, bokeh, sparkle, glow, smoke, flying leaves that were not requested; strange objects in the background |
| Construction | Extra or fused fingers, limbs not connected to the body, mechanical joints that carry no load, cords passing through objects, wrong symmetry on one side |
| Text & symbols | Fake text, meaningless glyphs, faint logo/watermark, decorative runes outside the brief |
| Lighting | Several conflicting light directions, rim light around every edge, cast shadows that do not match the source, glossy highlights in a matte/flat style, whole image tinted differently from the reference |
| Surface | Noise/veins faked as "detail", airbrush gradients in a cel/flat style, blurred edges, texture that changes scale between two areas of the same material |
| Style drift | Render style differs from the reference (illustration instead of game render…), line/saturation differs, semi-realistic mixed into stylized |
| Perspective | Two vanishing points for the same family of edges, ellipses on the wrong plane, objects floating without touching the floor |
| Technical | Halo/fringe on alpha, fake transparent background, crop that loses parts, size differs from the contract |
