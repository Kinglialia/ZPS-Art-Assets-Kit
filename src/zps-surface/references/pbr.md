# Stylized lit and PBR

## Separate art from the data contract

Stylized work can use PBR. Choose proportions, palette, roughness distribution and detail on purpose. Do not add micro-noise to be "correct PBR". Judge beauty and material plausibility on the shader. Do not read them from a histogram.

For metallic-roughness: the base color of a non-metal describes the diffuse color. For a metal, it describes a colored reflection. A colored metal does not need all RGB channels to be equally high. Metallic is usually 0 or 1 for pure materials. An intermediate value can come from mixing or coverage, and it must have a meaning. Roughness controls the width and character of reflection according to the shader. It is not the same as darkness. Do not infer correct roughness, height and normal from one RGB image.

Color textures are usually encoded as sRGB. Data maps do not get an sRGB transform. glTF uses roughness in G, metallic in B, and base-color RGB in sRGB with linear, straight alpha. That is the glTF contract. Do not assume that every engine uses the same packing. Filament shader inputs are linear and use their own alpha convention. Do not mix shader values with texture bytes. Normals follow the real tangent basis and convention. Check DirectX/OpenGL and mirrored UV. Do not only rename the file.

## Author and diagnose

For a new look or an unresolved risk, make a material swatch on a surface with many directions. Reuse a passed swatch if its conditions still apply. Check base color alone, then roughness/metallic and normal, then the combination when you need to find a cause. Use neutral light to diagnose and the game lighting to approve the look. Keep exposure, tone mapping, camera and environment the same between compared versions. Do not use emissive to hide a dark color, unless the brief asks for a glow.

With dynamic lighting, do not bake fixed highlights or cast shadows into the base color. A little art shading can suit stylized-lit, but check it in lit and dark areas and at the real rotation angles. Do not call this a clean physical albedo.

A normal map does not replace the silhouette. Height needs a scale/range and a shader that supports it. Roughness can be designed in large and medium areas. Avoid tiny grain that is unstable at low mips. Detail that disappears when shrunk must be judged against the target. Do not raise the resolution by default.

## Bake and smart material

A bake transfers detail from high-poly to low-poly (normal, AO, curvature, thickness) as a base for the material. Requirements:
- The high-poly and low-poly match.
- The low-poly UV does not overlap in areas with unique detail.
- The cage/ray distance is suitable.
- The tangent convention is the same as the engine's.

A bake has one owner (usually the 3D Artist). The artist uses the baked maps as masks for edge wear and crevice dust. Do not repaint AO by hand. A smart material (Substance and similar) is an external DCC that this role cannot run by itself. Propose parameters, and check the result on the model. Godot has `ORMMaterial3D`, which uses one texture that combines occlusion, roughness and metallic.

## Verification

Choose checks by the change:
- Repaint of the look: check the light response.
- Normal change: check the convention and tangent.
- Repack only: compare the values of each channel and the target import. Do not author the swatch again.

When needed, rotate the model or the light independently, to expose reflections that were painted wrongly, inversion and seams. If compression/mip and the real runtime material are part of the output, check them. Workbench and clay do not confirm PBR. If no engine is available, hand off the level checked in the DCC, and state clearly that the runtime is not checked. Technical standards: glTF 2.0, Filament, and the documentation of the chosen engine version.
