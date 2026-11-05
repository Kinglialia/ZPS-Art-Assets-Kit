# Photo / scan-based texture

Use a photo or a scan as the material source, for realistic or photo-based stylized work.

## Rights and source

- Use only images that you have the right to use in the product: your own photos, licensed libraries, sources the project provides. An image you can see on the web does not come with the right to use it. Record the source and license in the task record.
- Use screenshots of other games only to learn principles. Do not use them as a texture source.

## Process

1. **Choose the image.** It must be shot straight on, with even or overcast light, at a resolution that is enough for the target texel density.
2. **Remove the lighting (delight).** Remove cast shadows, highlights and baked AO from the albedo, so the engine can light it. If the style is unlit with painted lighting, keep them.
3. **Balance color** to the palette/value of the style sheet. `tone_match.py` can pull the color cast toward the reference. `structure_diff.py` confirms the shape did not change.
4. **Make it seamless/tileable** if the material repeats (see tileable-trim).
5. **Data maps** (normal, roughness) if PBR: what you infer from a photo is only an approximation. Check under a rotating light and read pbr.
6. **Stylize** if the style requires it: reduce high-frequency detail, group blocks, keep the character of the material. Compare with a reference of the same type.

## Self-check

- The albedo has no fixed shadow or highlight left (except for an unlit style).
- Color and value match the style sheet. They do not differ between assets in the same scene.
- The repeat is not visible. Sharpness matches other assets at the game viewing distance.

## Gotchas

- A photo carries the light and the viewing angle of the moment it was shot. This shows when you rotate the model or change the light.
- Real photo detail easily goes "off style" next to a stylized asset. Check it next to an approved asset.
