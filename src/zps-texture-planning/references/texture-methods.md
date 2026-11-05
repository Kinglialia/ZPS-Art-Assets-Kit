# Texture methods — choose the author × shader approach

A surface style = **how the color is created (author)** × **how the engine lights it (shader)**. These are two independent choices. A hand-painted texture can run unlit or PBR. A flat color can be lit or toon.

## Contents
- Author methods
- Shader
- Read the input → suggestion
- Godot mobile constraints
- Real capability of the role

## Author methods

| Method | Nature | Fits when | Trade-off | Read when working |
|---|---|---|---|---|
| Hand-painted | Paint color, light/dark and grain into the albedo | The concept has hand-painted strokes and painted-in light, and the camera is stable | High painting effort; painted-in light is wrong when the light rotates | hand-painted, painting-practice |
| Flat color / palette atlas | Each material area is a flat color cell; the engine gives the form | Low-poly, clear flat faces, color by volume, many assets share one palette | Little surface detail; depends on form and light | flat-color |
| Gradient atlas | A color cell that blends inside the cell | Same as above but depth is needed (dark root, light tip) | Gradient direction is tied to UV | flat-color |
| Vertex color | Color is assigned to vertices, no texture | Very light mobile; the mesh has enough vertices to hold the color boundaries | Color boundaries follow mesh edges; hard to add detail | flat-color |
| Bake + material | Bake normal/AO/curvature from a high-poly, then apply a material | Hero asset, PBR, close-up | Needs a high-poly and a DCC tool (Substance...); heavier | pbr |
| Tileable / trim sheet / decal | A repeating texture or a shared strip; a decal adds detail | Large environment, architecture, many meshes with the same material | UV must follow the trim convention; repeats show easily | tileable-trim |
| Triplanar | Project the texture along 3 axes, no UV needed | Rock, soil, terrain volumes; mesh without UV yet | Blurry where projections meet; costs more shader work | tileable-trim |
| Pixel texture | Large texels, limited palette, Nearest filter | Pixel/retro 3D games | Texel density must be the same across the whole game | pixel-texture |
| Photo / scan | From photos, with light removed and color balanced | Realistic or stylized based on photos | Photo rights; baked-in light; style drifts easily | photo-scan |
| Projection paint | Paint on a rendered image, then project it onto the model | Hero asset with a fixed view, paintover of a concept | Hidden parts need handling; needs a bake owner | projection |

## Shader

| Shader | When | Note |
|---|---|---|
| Unlit | Painted-in light, very light mobile | Does not react to lights/day-night |
| Lit / toon | Flat color or light hand-painting, dynamic light needed | Do not paint fixed shadow into albedo; toon uses a ramp |
| PBR (metallic-roughness) | Material needs real reflection | Albedo has no light in it; roughness/metallic/normal need the correct convention |

## Read the input → suggestion

| Observation | Lean toward |
|---|---|
| The concept has hand-painted strokes/grain and painted-in shadow | Hand-painted (unlit or light lit) |
| Color by volume, clear flat faces, almost no grain | Flat/gradient atlas or vertex color + lit/toon |
| Many meshes with the same material, large scene | Tileable/trim/decal, triplanar for terrain |
| Close-up, reflective material (metal, glossy leather) | Bake + PBR |
| Model has no UV | Vertex color, triplanar; or ask for UV |
| Much UV overlap, mirroring | Avoid asymmetric detail; flat/tileable |
| Large pixels, clear pixel edges | Pixel texture, Nearest |
| Many skins/seasons | Palette atlas swap, or a material instance that changes color |

A suggestion is a hypothesis. Check it with a test sample on a representative area of the model before you do the whole model. If the caller or the Art Style document gives a specific requirement, this table does not replace that requirement.

## Godot mobile constraints

- Godot sorts objects by material/shader. Fewer materials and a shared atlas are lighter.
- Automatic instancing exists only in Forward+. It is **not available in Mobile/Compatibility**. For many identical objects on mobile, use MultiMesh (the 3D Artist/Developer decides).
- Alpha-blended objects cannot be sorted, are drawn from far to near, and get no automatic instancing. Prefer alpha scissor/hash. Split the transparent part into its own surface.
- Vertex color: `StandardMaterial3D` ignores it by default. Turn on **Vertex Color → Use as Albedo** (usually together with **Is sRGB**).
- Decal: Mobile applies at most 8 decals per mesh resource. Compatibility does not support decals.
- `ORMMaterial3D` uses one ORM texture (occlusion, roughness, metallic).
- Godot normal maps use the OpenGL convention (Y+).

Source: Godot documentation (Standard Material 3D, Using decals, Optimizing 3D performance), repo `godotengine/godot-docs`. For texture size, compression and mipmap, use the project's tech profile.

## Real capability of the role

When you choose, prefer a method that the role can do itself to delivery quality.

- An LLM does these well: palette/gradient atlas, projection from a painted image, repeating textures, color adjustment by script.
- An LLM does these badly: hand-painting a separate texture directly on a UV layout (a generated image tends to paint light/dark by the atlas, not by the volume), high-quality high-poly bake, Substance.

The role can do these itself:
- Generate/edit an image with [gen craft](../../.art-production-support/shared/gen-craft.md).
- Palette/gradient atlas.
- Color adjustment by script.
- Check renders on the model (Blender headless).
- Paint view.

These need a person/DCC tool: sculpt a high-poly, high-quality bake, Substance, UV editing, vertex color assignment on the mesh (propose it to the 3D Artist). State this in the proposal.
