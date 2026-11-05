# UI system, visual direction and source/asset

## Contents
- Two visual directions
- Just-enough system
- Editable source and export
- Usage rights

## Two visual directions

Do this only when the project has no UI style yet. Build on the same approved wireframe and content. For each direction, state:
- The main feeling and the link to the game world.
- The form language (silhouette, corners, thickness, repeat rhythm).
- Typography, material, level of decoration.
- Attention order.
- The trade-off in readability and production effort.
- One recommendation.

Glow, gradient and symmetry are not faults by default. Judge them by style, focal point and readability.

## Just-enough system

| Group | Spec by scope |
|---|---|
| Color | Roles: background, text, action, state/rarity. Do not use the same signal for conflicting meanings |
| Text | Font, type levels, line height, outline/shadow, fallback, long-text rules |
| Layout | Spacing, padding, alignment, minimum size, stretching, overflow |
| Component | Stable ID, structure, variants, necessary states, touch area |
| State icon | Shape, thickness, detail at the real use size |
| Decoration | Frame, border, material and limits of use |
| Motion | Purpose, trigger, proposed duration, reduce-motion option if it applies |

Do not create a token, variant or state that nobody needs. Hover is not needed for a UI that uses touch only.

## Editable source and export

If there is a specific source-format requirement (AD, Art Style document, project), follow it. If nobody states one, choose by UI type and record the reason in one line:

| UI type | Default source |
|---|---|
| Button, panel, bar, flat or simple-gradient 9-slice frame; state icon made of shapes/strokes; flat, sci-fi, minimalist UI | **SVG** (an LLM can write it, it can be edited in Figma, and it is sharp at every size) |
| Hand-drawn decorative frame (wood, carved metal, stone, fantasy with many patterns), illustration, background | **Generated image** per [gen craft](../../.art-production-support/shared/gen-craft.md); the separate raster is the illustration source |
| Combination | SVG frame + one raster texture layer; state clearly which layer is which source |

Rules for the SVG source:
- **Text does not go in the SVG.** Text is live text in the engine. Convert to paths only a logo or a decorative title.
- **It must open in Figma.** Use only paths, shapes, gradients and groups. Name groups by component/state (for example `btn_play_pressed`), or use one file per state. Do not use filter, mask, script or foreignObject.
- The 1x size of the SVG (width/height in px) equals the display size at the project's base size.
- Export PNG with `svg_render.py` (see [scripts](../../.art-production-support/shared/scripts/README.md#svg)). The script warns when the SVG has text or risky features.

`.tscn` and `.tres` are not default sources. If you cannot create a required format, say so before production and propose a replacement.

| Part | Requirement |
|---|---|
| Layout, text, button | Edited independently; dynamic text is separate from decoration and is not baked into the image |
| Frame | Fixed area, stretch/tile area, content padding, minimum size |
| Icon/illustration | Source + export; a separate raster can be the illustration source |
| Background | Crop, tile, scale and the areas to keep |

Record the chain source → tool/version and export steps → runtime file. List fonts and dependencies. Do not list machine-specific paths. Set the export size by display area and budget. Keep image size, display size and touch area apart. Try changing to a long text, replacing an icon, or resizing one component, then export again. Record the result.

## Usage rights

For a resource that goes into the product, record the source, author, license and attribution. If not yet verified, mark it pending. A reference used for analysis is not automatically allowed for release. For a generated image, record the tool and its role.
