# Mapping, bake and checks at the target

## Preflight by method

Reuse the existing mesh/UV version, UV set, materials, units/scale, shader, texture resolution and views. Add only the data the operation needs. If the task only assigns a channel change, repack the maps under the existing contract. Do not open the mesh for this. UV is not required for every procedural or vertex-color output. A texture output with UV needs the matching mapping. Send mesh/UV faults to the right owner, with the blocked area. A high→low bake has one owner. Keep the cage, triangulation and tangent conventions.

Check distortion with a checker on the model. Set density by priority area. Do not require every pixel or every asset to be equal. For a shared atlas, check overlap between **all objects that use the same image**, not only each object. Mirror, stack, UDIM and tiling can be valid, but they affect the bake and unique marks. A simple 0–1 script does not prove that UDIM is valid.

Tiling: an offset helps find seams, but you must still look at many repeated tiles and at the surface. Trim: follow the direction and dimension of the material. Decal: check the edge, scale and blending. Do not use a perspective warp on one concept image and assume it gives a texture clean of lighting.

## Padding and filtering

The gap between islands is not the same as the color dilation outside an island. Choose both by resolution, the largest mip in use, filtering, compression and export. No table of pixel values is valid for every case. Test seams at the target viewing distance and at low mips. Do not turn off mips as the default fix. For a map with alpha, check on light and dark backgrounds, and straight or premultiplied alpha as the renderer needs. An RGBA PNG does not confirm the convention by itself.

## Viewing conditions and causes

Lock the camera, lighting, exposure, tone mapping and import between comparison versions. Blur fault: source image → UV area/distortion → sampler/mip/compression → shader/lighting. Black fault: color space, alpha, normals and material links, before you repaint. Seam fault: UV, tangent, bake and packing, before you blur. Separate the perceived material from the implementation. A good-looking image does not prove that the maps are correct.

Evidence must match the artifact and its version. A script records pass only for the checks it ran. If a mandatory check is `not_checked`, the result is not ready. Re-importing the GLB to check structure is useful, but it does not replace an engine check. State clearly whether the image was rendered with Workbench, Eevee, Cycles or the real engine. Hand off the map, channel, color space, normal, UV, resolution, source, and the related external files. Measure the real size. Do not take the number from the prompt.
