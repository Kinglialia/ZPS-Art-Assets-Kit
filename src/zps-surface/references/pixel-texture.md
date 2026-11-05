# Pixel texture on a model

Texels are large and clear, the palette is limited, and nothing is smoothed. Consistency matters more than detail.

## Principles

- **One fixed texel density for the whole game** (for example N texels per meter). Every asset uses the same value. Measure with `inspect_model.py --texture-size`, and adjust the texture size or UV to match. A density mismatch is the most visible fault of this style.
- **Limited palette** from the style sheet. Do not add intermediate colors from resizing or blur.
- **No smooth resampling.** Make the image at the exact target resolution, or shrink it with Nearest. Do not use bilinear or Lanczos.
- **UV follows the texel grid.** UV island edges lie on texel boundaries, so pixels are not cut diagonally. The 3D Artist places UV on the grid.
- **Nearest filter, no mipmap** (or a checked mipmap) on the material. See the tech profile.

## Process

1. Fix the texel density, the texture size and the palette with the AD or the tech profile.
2. Make the source at the target resolution. If you generate a large image and shrink it:
   - Shrink it with Nearest.
   - Quantize it to the palette (use `palette_report.py` to check colors outside the palette).
   - Fix faulty pixel clusters by hand.
3. Apply it to the model. Run `render_model.py` at the game viewing distance. For a flat texture, use `preview.py sheet --nearest`.

## Self-check

- All assets have the same texel density (small deviation from the standard).
- No color outside the palette. No blurry pixels or smeared edges.
- Pixel clusters read as shapes at the game viewing distance. No stray pixel noise.

## Gotchas

- A shrunk generated image often gives noisy pixels and intermediate colors. You must quantize to the palette and clean the clusters.
- Mipmaps blur pixels at distance. Decide by the tech profile and check at the longest distance.
