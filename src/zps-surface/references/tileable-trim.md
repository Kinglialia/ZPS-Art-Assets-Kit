# Tileable, trim sheet, decal, triplanar

For environments and architecture: few textures, shared by many meshes, with unique detail added by decals.

## Choose a technique

| Technique | Use when | Notes |
|---|---|---|
| Tileable | Large continuous surfaces: ground, wall, floor, roof | The repeat must not show. Texel density is uniform across assets |
| Trim sheet | Borders, battens, ledges, planks, pipes that repeat along one axis | Place UV by the trim strip. Record the strip convention in the handoff table |
| Decal | Unique detail on a repeating surface: stains, signs, cracks | Godot Mobile: at most 8 decals per mesh resource. Compatibility has no decals (use Sprite3D for nearly flat surfaces) |
| Triplanar | Terrain, rock, forms without good UV | Use world space so meshes join seamlessly. It blurs at intersection corners. It costs more shader time |

## Make a tileable

1. Design large, medium and small blocks by the style. Avoid one standout mark that is easy to recognize when it repeats.
2. Make the source (generate it by gen craft, or paint it). Then make the edges seamless (offset by half a tile, fix the join marks).
3. Check with `preview.py tile --repeat 3` and on the model at the game viewing distance. Look for repeat marks and join marks.
4. Variants that reduce repetition: 2–3 tiles with the same palette, or a decal/vertex color laid over it.

## Make a trim sheet

1. List the shared details you need (planks, ledges, metal borders, and so on) and their real widths.
2. Arrange the strips horizontally in order. Make the strip height proportional to the real size, at the shared texel density.
3. Each strip must repeat horizontally. Hand off the strip table (name, v position, real width).
4. Check on a few sample meshes that the 3D Artist maps. Strip edges must not bleed. Detail must not distort.

## Self-check

- Texel density is uniform across assets in the same scene (`inspect_model.py` texel_density for each mesh).
- The repeat is not visible from the game angles. Decals fit the lighting and palette.
- At low mips: no bleed from the neighboring strip (trim) or join marks (tile).

## Gotchas

- A generated image often has light from one side. A tileable must be delit or have flat lighting. If not, the repeat becomes light and dark stripes.
- A trim sheet works only if the 3D Artist maps by the convention. Agree on the strip table before you paint.
