> Roles in this skill: "task giver", "visual standard keeper", and "approver" all mean the user. Use "independent review" only when a truly separate reviewer exists. Do not call a subagent by default. Thresholds are in `task/spec.json`. Take measurements from the scripts in `tools/`. Source: skill art-3d-artist v0.1.0.

# Choose and verify a build solution

## 1. Analyze before you choose

Read the concept, the visual standard, the set anchor, and the task criteria. Identify the camera, the display size, the motion and interaction requirements, the engine/shader, and the known budget. If missing information affects the choice, state an assumption and its effect.

Use the reading priority in the brief. The task giver defines function and information. The visual approver defines visual features. View at the allowed angles, viewing distances, and display sizes. Do not infer importance only from the area in the concept or from an enlarged render. If information is missing, record a recommendation or an assumption. Ask only about what would change the decision.

Classify each detail by role: mass/outline; construction and joints; motion/interaction; light response; color and pattern. One detail can have several roles.

## 2. Choose a technique by its effect

| Technique | When to consider it | What to check |
|---|---|---|
| **Geometry** | The detail affects the silhouette, thickness, gaps, motion, shadow, or interaction | The shape at the needed angles; whether the quality is worth the geometry cost |
| **Bevel + custom/weighted normals** | Edges need to catch light, and large faces need stable shading | The bevel is visible enough at the target camera; it does not distort the mass or create shading faults |
| **Normal map** | The detail must change the light response but does not need real mass or gaps | It reads at the target size; tangent, UV, compression, and shader are correct |
| **Color texture/hand-painted** | Color zones, patterns, or light and dark in the style | It matches the visual language; painted lighting fits the target lighting |
| **Trim sheet/tiling** | The detail or material repeats across many surfaces or assets | Scale, pattern direction, seams, repetition, and whether the material can be shared |
| **Decal** | A symbol or local detail must be placed independently on a surface | Renderer support, layering, cost, and visibility at oblique angles |
| **Cards + alpha** | A thin form such as a leaf, hair, or a cluster of details that fits a flat plane | View angle, silhouette, shadow, mip/alpha, and overdraw; do not assume it is cheaper than geometry |
| **Parallax/POM** | The surface needs more depth than a normal map gives, and the target shader supports it | Oblique angles, artifacts, GPU cost, and limits at the edge of the object |
| **LOD** | The asset appears at many display sizes and reducing detail helps | Loss of silhouette, shading, and identifying detail, and the transition between levels; do not force a fixed reduction ratio |

Combine techniques for each part of the asset. Do not choose only from the asset type or the platform. Do not apply one depth threshold in cm to every case.

For a detail that only changes color or pattern, prefer a color texture or a material. For a detail that needs a light response but not real mass, consider a normal map. Use geometry to keep the silhouette, thickness, gaps, shadow, motion, or interaction that matters in the brief. A normal map does not replace an outline or a construction that you removed.

If you are not sure, use a small test in the existing proof step. Remove the geometry of a representative area. Replace it with a suitable texture or normal. Compare under the same camera, light, and size at the usage angles. Accept the result if it keeps the reading priority and the function. Do not conclude that the method failed only because the test map is not right. If a suitable standard or sample exists, reuse it. Do not test every scratch, and do not open an additional gate. Coordinate with the texture/material side when it exists. If you change an approved way of showing something, you must still submit it to the visual approver.

## 3. Choose how to build the shape

- **Direct mesh:** for masses that need control of specific vertices, edges, and topology.
- **Curve/sweep:** for shapes that follow a path, such as cables, tubes, trims, and curved components.
- **Sculpt:** for organic or deformed shapes that you work directly on the surface. Do retopo when the target requires it.
- **Boolean:** to make intersections or cuts that fit the construction. Check the shading and topology after the operation.
- **Procedural/modular:** for repeating or rule-based structures, or when you must edit many variants. Check the joints and any repetition that is easy to notice.
- **Mesh from a generator:** use it when it fits your authority and tools. Check the design, mesh, UV, and export like any other source.

You can combine several ways. Choose the method that keeps the design, is convenient to edit, and meets the target use.

First, build one main runtime version within the budget. Add LOD only when the camera, the display size, and the target requirements make it useful. Create LODs from a shared source when it fits. Share textures and materials if the look stays. Do not build three independent Low/Medium/High versions by default. Do not reduce faces by a fixed percentage. A high-poly sculpt for baking is a separate source when you need surface detail. It is not the same as the highest detail level of the LOD set.

## 4. Use a standard or a small test

If a standard or a set anchor still fits, reuse it. Record the version and the conditions of use. When a new risk appears, choose the smallest area that is enough to show the problem. Test it before you expand.

If you must compare two solutions, keep the same camera, display size, light, and an equivalent material. Compare the visible quality, the editability, and the relevant cost data. If you have not measured the runtime, record only the expected cost.

Example: compare an engraved mark made with geometry and with a normal map on the same area. Do not build two complete assets only to answer this question.

## 5. Decide and submit for approval

Write a short entry in the task record: `part to show | chosen technique | reason | standard/sample reused or test result | not checked`.

The 3D Artist decides the solution within the standard and the budget. Coordinate with the texture/material side when maps, materials, or bake are involved. If you do the work yourself, say so clearly. If you change an approved way of showing something, submit it to the visual approver. If the solution goes beyond the budget or the task authority, give a recommendation with the tradeoffs.
