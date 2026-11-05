# Texture checks — how to check and diagnose

Read this file when you need a deep check of one group in the table in SKILL.md, or when the cause is unclear. Technical details on UV, bake, padding and import are in [Mapping, bake and checks at the target](../../zps-surface/references/mapping-validation.md). This file says only what the reviewer checks, with what, and how far the conclusion can go.

## Minimum evidence by question

| Review question | Evidence needed | Not enough to conclude |
|---|---|---|
| Does the texture fit the style? | On-model render at the game camera, compared with an approved asset of the same type under the same lighting | Flat atlas, paint view, generated image |
| Does the seam show? | Renders from many angles at game distance, including a view straight at the main UV cuts | One good angle; UV layout image |
| Is the texel density even? | Checker render, or the texel density numbers from `inspect_model.py` | Texture file size |
| Do the maps follow the contract? | List of channels, color space and normal convention from the real file/import | File name, description in the prompt |
| Is it readable far away? | Render at the farthest distance, with the real mip/compression if it is in scope | Scaling down the render image by hand |
| Does it pass in the engine? | Image or capture from the target engine | Blender render (state clearly that it is Blender) |

If evidence is missing for a row, record the conclusion for that row as `not_checked`. It is neither pass nor fail.

## Extra checks by texture method

Before you check, ask for the chosen method or read it from the brief. The same symptom can be right for one method and wrong for another (for example, painted-in light).

| Method | Specific points to check | Do not count as a fault |
|---|---|---|
| Hand-painted unlit | The painted-in light has one assumed direction on every piece; the light does not "follow" the object wrongly when the object rotates within the game range; strokes follow the form | Shading painted into the albedo |
| Hand-painted / stylized lit | No baked highlight, specular or fixed cast shadow; deliberate shading is still right in lit and dark areas when the light rotates | A little art shading that the brief has approved |
| Flat color / gradient atlas / vertex color | Material areas read clearly at screen size; atlas cells do not bleed at low mip; no stroke, grain or noise that the style does not have | UV overlap between faces of the same color |
| PBR | Base color has no lighting in it; roughness/metallic are reasonable under a rotating light; normal follows the convention; channel packing follows the contract | Base color darker or lighter than the concept image when the engine lighting compensates |
| Tileable / trim / decal | The repeat does not show at the game viewing distance; trim strip edges do not bleed; decal has the correct scale, edge and blending | A repeat seen only in a close inspection outside the game camera |
| Pixel texture | Texel density is uniform between assets; Nearest filter; no color outside the palette; pixels do not blur at a distance | Deliberate jagged edges |
| Photo / scan | The light and shadow of the source photo are removed; real photo detail does not look "off style" next to an approved asset | — |
| Projection (paint view) | The paint sticks to the geometry at the projection angle; areas that cannot be seen are filled reasonably and recorded as inferred; the back or bottom has been viewed | An inferred area that is simpler than the projected area |

Details for each method are in the files in [Surface references](../../zps-surface/references/).

## Quick diagnosis tree

- **Blurry:** Is the source image sharp enough? → Do the UV islands have enough area and no stretching (checker)? → Mip/filter/compression? → Does the shader/lighting remove detail?
- **Black, wrong color, too bright:** Color space of each map → alpha mode → normal with a flipped Y channel → material link/shader. Ask for a repaint only after these steps have been ruled out.
- **Seam:** Where the UV split is → padding/dilation → tangent/bake cage → difference in painted strokes on both sides of the cut. Blurring the seam only treats the symptom.
- **Detail follows the UV, not the form:** This is usually caused by painting/generating directly on the atlas. Propose painting on the model or in paint view along the form.
- **Light in the wrong direction or doubled:** Lighting baked into the albedo adds to the engine lighting (PBR/lit), or the painted-in light does not follow the same convention between pieces (unlit).
- **Repeat shows:** A prominent mark in the tile, a tile scale too small for the viewing distance, or no variants/decals to break the repeat.

## Severity levels

- **blocker:**
  - The map contract is wrong and the asset displays wrong in the engine (color space, normal convention, missing required channel).
  - A seam or fault breaks the readability of the material/gameplay at the game camera.
- **major:**
  - Clear style mismatch with an approved asset.
  - Texel density mismatch visible between pieces seen side by side.
  - Baked light is wrong for the pipeline.
- **minor:**
  - A seam that shows only in a close inspection outside the game camera.
  - Detail rhythm not yet good in a secondary area.
- Record a **preference** separately for an aesthetic choice that does not violate the brief.

## Role boundaries

The reviewer concludes on issues and causes that have evidence. Fixing the map belongs to Surface. Fixing the UV layout, mesh and high→low bake belongs to the 3D Artist. A style change belongs to the AD. If you cannot tell the map and the UV apart as the cause, record both hypotheses and a check that tells them apart (for example, a checker render from the same angle).
