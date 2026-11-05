# Flat color — palette atlas, gradient atlas, vertex color

The surface is a color per material area. The mesh, the engine lighting and fog/atmosphere give form, light and shade, and depth. Quality comes from **choosing colors and dividing areas**, not from painted detail.

## Choose a variant

| Variant | Use when | Notes |
|---|---|---|
| Palette atlas | Many assets share one palette; you want to change colors by swapping the atlas | One small texture shared by the whole set, few materials → fewer draw calls |
| Gradient atlas | You need a deliberate light-to-dark change inside one area (tree canopy, rock, wall) | UV sets the gradient direction. Keep the same direction across the set |
| Vertex color | You want no texture; the mesh has enough vertices at the color boundaries | Godot: turn on Vertex Color → Use as Albedo (+ Is sRGB). Assigning the colors is the job of the 3D Artist or the DCC |

## Build the atlas

1. Take the palette from the style sheet. Measure it with `palette_report.py` or `--profile` on a reference of the same type. Give each material one cell. Name each cell after its material.
2. Make each cell large enough that mipmaps do not bleed into the next cell. Leave padding between cells. Set the atlas size from the tech profile. Check at the longest viewing distance.
3. Gradient: stretch the cell along one axis. Record which direction is "top/bottom" so the 3D Artist can place the UV correctly.
4. Season/skin variants: use an atlas with the same cell layout. Change only the colors. Do not repaint.

## Assign UV to cells

Shrink the UV of each area into its color cell. For a flat cell, the UV is almost a single point. For a gradient cell, the UV spreads along the axis. UV does not need an even layout. UV may overlap between faces of the same color. Assigning UV is the job of the 3D Artist; the artist delivers the atlas and the cell table.

## Self-check

- Render with `render_model.py` from several angles under game lighting. Material areas must read clearly at screen size. The color must not shift between lit and dark faces more than the style allows.
- Compare with the render of an approved asset of the same set (`preview.py compare`, `score_variants.py`).
- No strokes, grain, noise or painted shadow, unless the style has them (fault table in gen craft).
- At low mips, color does not bleed into the next cell.

## Gotchas

- A generated image used for an atlas often adds grain and light/shade. Make the atlas with colors measured from the style sheet. Do not generate it.
- A color that looks good on a flat cell can be too dark or too bright on a model under engine lighting. Always choose colors on a render.
- Vertex color depends on vertex density. A curved color boundary needs more edges. Propose this to the 3D Artist instead of switching to a texture.
