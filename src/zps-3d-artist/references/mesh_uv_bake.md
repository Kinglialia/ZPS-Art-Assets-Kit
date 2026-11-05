> Roles in this skill: "task giver", "visual standard keeper", and "approver" all mean the user. Use "independent review" only when a truly separate reviewer exists. Do not call a subagent by default. Thresholds are in `task/spec.json`. Take measurements from the scripts in `tools/`. Source: skill art-3d-artist v0.1.0.

## B. Finish the mesh / edit the model
**Receive:** the blockout/source of the correct version, the relevant approval milestones, and the delta to make.
- Record Source/Keep/Change. Work from main mass → secondary → detail. Use parametric for number-based edits. Use sculpt for organic shapes. Use retopo when the mesh needs a new structure. It is not required for every asset type. Use modular with grid/snap. Do not require every asset to start from primitives or from image-to-3D.
- Choose the topology for shading, silhouette, subdivision/deformation, and export. Do not force all-quads or watertight on every asset. Keep intersecting or open surfaces only when they are intentional and fit the pipeline. Remove degenerates, duplicate faces, flipped normals, z-fighting, and parts that float or sink by accident.
- Control scale and modifiers by their result. Do not apply all transforms and modifiers mechanically to a rig or a source. When you must keep the source, do destructive operations on a separate copy. Reduce geometry with a suitable method, including retopo or decimate, if the requirements still hold. Check the silhouette, shading, and UV again.
- Take the triangle, material, and vertex budget from the task. Check triangles after modifiers from the blockout, and at the milestone when the mass is finished. Do not wait until export to measure. If you build with a script, make the segment, bevel, and subdivision counts and the detail density into parameters that are easy to change. You do not need to open a report after every tool. Measure the export again when it exists. Make LOD, collision, and deformation only when assigned. Check the needed motion with real evidence. Do not accept it only because edge loops exist.
- For attached or assembled parts, check the support faces, the connectors, and the intersections before you hand off to texture. Use a close-up angle or a suitable cross-section. Tell an intentional gap from an open-gap fault. Do not fix z-fighting by floating all the details without checking the structure again. Record evidence for important joints. Do not infer it from the silhouette or the UV pass.
**Handoff:** the new version of the mesh/source, figures, and clay/wire or matcap images that match the problem. Also give the comparison of kept and changed parts, the remaining faults, and the downstream parts that need a re-check.

## Reduce faces and retopo when needed

Fix the cause of excess faces first. Reduce segment counts or modifiers that are too high. Dissolve edges that do not contribute. Remove small geometry that a surface can show, as in 00-style-method.md. Remove interior, bottom, or covered faces only after you confirm that the task does not need them for any view, shadow, motion, or interaction. Keep the construction that is needed.

If the mesh has a simple structure, edit it directly first. If a mesh from AI or sculpt is too dense, hard to edit, or does not meet deformation needs, consider retopo to lay out the faces again. For a fast reduction for far viewing, you can try decimate or LOD when it fits. Do not build dense and then retopo every asset by default. Do not treat auto-remesh as a guarantee that it keeps the shape or reduces triangles.

Do retopo only when the gain in budget, editability, or deformation pays for the rebuild, UV, and bake work. Keep the original. Compare before and after at the camera and the needed angles: silhouette, proportions, identifying features, normals/shading, and motion if any. Texture and UV may need to be transferred or redone. Check the affected maps. Bake surface detail when needed. Do not use a normal map to compensate for a lost mass or outline. Use the same current criteria and check milestones. Do not add a separate workflow or reviewer.

## Bevel and custom/weighted normals

### When to use

Use a bevel when an edge needs a real chamfer to catch light or to keep its shape at a close angle. Use custom/weighted normals when you need to adjust shading. For example, keep a large face looking flat while the edge area shades softly.

You can use the two techniques together. Weighted normals do not create a chamfer. They do not fix the silhouette. They do not replace the repair of faulty geometry. If the style intentionally uses flat faces or sharp edges, keep the approved way of showing them.

### How to do it

1. **Identify the edges to treat.** Choose them by concept, construction, material, and target camera. Do not bevel all edges mechanically.
2. **Choose the bevel width.** Base it on the design proportions and on how visible the bevel is at the usage size. Before you edit, check the scale and the effect of transforms and modifiers. Do not apply them destructively to the source by default.
3. **Choose enough segments, and no more.** Start with few. Increase them if the curve or highlight still breaks in a way that is not intended. Do not assume that one segment count fits every edge.
4. **Set up shading.** Choose the smooth/sharp areas on purpose. Try custom/weighted normals when you need to keep large faces clean. Check the modifier order and the real result for your Blender version.
5. **Check the hard areas.** Look at concave corners, short edges, intersections of many edges, and Boolean results. Fix bevels that overlap, distort, or create degenerate faces.
6. **Check the downstream effect.** If you use a normal bake, agree on the geometry state, the triangulation, and the normals before the bake. If you change these data after the bake, check the related maps again.

### How to check

View the model at the target camera and size, and at the close angles that you need. Use light or a matcap to read faces and edges. Check that highlights are continuous. Check that large faces do not dent or bulge by accident. Check that the silhouette is still correct.

When you must find the effect, compare with the bevel or weighted normals on and off. Check the export again to confirm that the geometry and normals are kept. Also measure the real triangles and vertices against the task budget.

### Common faults

| Sign | What to check |
|---|---|
| A flat face looks dented or bulged | Geometry, smooth/sharp, normals, and modifier order |
| Bevel width is uneven | Scale, bevel settings, and edge structure |
| A corner is pinched or intersects | Edges that are too short, bevel width, corner handling, and topology |
| An edge still breaks at an angle that must be seen | Segments, normals, and the real shape |
| More faces were added but the shape does not improve | Visibility at the target camera; reduce or remove a bevel that has no value |
| Blender is correct but the export is off | Normals, triangulation, the modifiers that are exported, and import settings |

Fix the geometric cause before you use normals to adjust shading. Keep an editable source. Record the parts that are not verified.
## C. UV → texture/bake handoff
**Receive:** a relatively stable mesh, the texture approach (unique/tiling/trim/atlas/palette), the resolution, and the bake requirements, either fixed or proposed and still open.
- Allocate UV space by the reading priority in the brief and the usage angles. Identifying areas, interactive areas, and main faces need suitable pixels. Rarely seen parts can get less. Use mirror, stack, or reuse when it fits. Keep the unique detail that is needed. Choose seams by shape, shading, and bake method. Check the checker, the distortion, and the clarity of the affected area. Do not force equal density. Do not enlarge the whole atlas to compensate for a priority area that is too small. Measure detail under the post-fix check conditions below.
- Set the padding by resolution, mip, and pipeline. Use overlap, stack, mirror, or UVs outside 0–1 only when they are intentional and fit the texture or bake method. Do not add lightmap UVs or UDIM on your own if the target does not need or support them.
- If you bake, prepare the high and low meshes, a compatible triangulation and tangent basis, and a test bake when the task assigns one. Record the parts that you did not test. Do not bake lighting into the base color as a default for every style.
**Handoff:** the source or mesh+UV with a version, the material slots and area names, the UV/checker check results, and the relevant padding and overlap. If the task requires a measurement, give the density with its method and unit. Hand off the bake setup if there is one. The texture/material side receives the texture part. The 3D Artist makes the texture only when assigned. If you fix the mesh or UV, state which texture, bake, or rig is affected.


**Bake owner:** the 3D Artist prepares the high and low meshes, the UV, and the geometry/tangent. The texture/material side transfers the look, maps, and procedurals. A high→low bake has only one owner, assigned by the task giver, with an input and output version. Do not assume that both sides do it.

**Check after a UV fix/repack, by impact:** check the checker, the distortion, the padding, and the clarity at the target camera and size, in the changed areas. Measure density, occupancy, and area by region when the task has a threshold, when the allocation changes a lot, when clarity may be lacking, or when you diagnose a fault. Do not require a full measurement of every material after a small edit. When you measure, record the units, the real resolution, the method, and the UV version. Old numbers that relate to the change become invalid. Reuse the checks for unchanged areas. Zero overlap or a pack margin does not prove that clarity or padding is reached. If clarity is lacking, adjust the allocation within your authority, or submit an exception before the full bake.

## Prepare and check a high→low normal bake

### When to use

Use this when you need to move surface detail from a high-poly mesh to a low-poly mesh. The goal is to keep the light response with less geometry. A normal map does not replace the silhouette, thickness, gaps, or real geometric shadows.

Reuse bake evidence that still fits. When a new risk appears, test a representative area before the whole asset. Confirm that the detail still reads at the target camera, display size, and shader. Do not assume that every asset needs a high-poly mesh or a normal map.

### Responsibility

The 3D Artist prepares the high and low meshes, the UV, the normals/tangent, and the triangulation state. The task giver assigns one owner to run the bake and to keep the settings so the bake can run again. The texture/material side helps check the map and the look. The 3D Artist checks faults related to geometry, UV, and the export.

### Preparation

1. **Lock the inputs for the bake.** Record the versions of the high and low meshes, the units, the transforms, the UV set, and the modifiers that affect the result. The two meshes must match in position and in the forms to transfer.
2. **Prepare the low-poly.** Keep the silhouette and the needed construction. Check the normals, the smooth/sharp areas, and the triangulation that you will use at export. If you change the topology, UV, normals, or triangulation after the bake, check the affected parts again.
3. **Prepare the UV.** A unique bake needs write areas that do not conflict. Use mirror or stack only on purpose, and with a way to avoid overwriting. Do not treat every overlap as wrong. For a tangent-space bake, split the UV at hard edges to get separate padding. A UV seam does not have to be a hard edge.
4. **Choose resolution and padding.** Base them on the UV allocation, the clarity you need, the mip, and the budget. Do not use one pixel margin for every resolution. After the bake, check the real distance and dilation.
5. **Match the target convention.** Confirm the tangent basis, the normal convention, the UV set, and the import method. Do not infer them only from the engine name or the file name.

### Procedure

1. Choose the correct high-poly source, the low-poly that receives the bake, and the target image. Check with one small bake before you run a wide one.
2. Set up the cage or the ray distance to catch all the surface to transfer and to avoid picking up nearby detail by mistake. A custom cage must meet the topology requirements of the tool.
3. For parts that are close to each other, adjust the cage, split the bake groups, or use a matching mechanism if available. Do not increase the ray distance for the whole asset to hide a local fault.
4. Bake a tangent-space normal when it fits the pipeline. Record the channel convention and the settings that you used.
5. Assign the map to the correct slot. Treat it as normal data, not as a color texture. Confirm that the shader really uses the map.

### How to check

Check both the map and the result on the low-poly. Compare with the normal on and off under the same camera, light, and material. View representative areas at the usage size and at close angles to find faults.

Check for seams, shifted detail, projection streaks, areas with lost data, convex/concave direction, and bleed when viewed from far. Open the export at the target, within the scope, to check the normal convention, the tangent, and the compression.

A map image that looks clean does not prove that the bake passes. If you did not check at the target, state the limit clearly.

### Common faults

| Sign | What to check |
|---|---|
| Detail turns from convex to concave, or catches light in the wrong direction | Channel convention, how the map is assigned, and import settings |
| Streaks at a seam or a hard edge | UV/padding, normals, tangent basis, and triangulation |
| Detail is stretched, shifted, or taken from the wrong part | Cage, ray direction/distance, and bake groups |
| Black or empty areas, or missing detail | Source/target, ray coverage, normals, and the target image |
| Looks good near but dirty or flickering far | Mip, padding, compression, and detail that is too small |
| The DCC is correct but the engine is wrong | Material, tangent, convention, import, and the real export data |

Diagnose with tests that change few variables. Do not flip the green channel or raise the resolution for every fault by default.

### Handoff

Hand off the normal map, the versions of the high and low meshes and the UV, the real resolution, the channel convention, the cage/ray settings, and the check evidence. State clearly the owner, the parts that pass, the remaining faults, and the conditions that require a new bake.
