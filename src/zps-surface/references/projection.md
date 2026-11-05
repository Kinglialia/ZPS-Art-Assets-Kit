# Projection paint — separate the paint stage and the integration stage

## Minimum contract

If the task assigns **painting a view**, you receive:
- A guide render for each angle.
- The design/reference, with its role.
- What to keep and what to change.
- Output size/framing.
- The lighting model.

The source model/version and the camera come from the caller as IDs or information. Do not require the artist to open the mesh/UV if the caller owns projection/bake. For simple paint, clay + mask/landmark may be enough. Depth, normal, position, UV and material-ID passes are required only when the method or a specific check needs them. Do not use a pass with missing encoding or coordinate system as an exact measurement.

If the task assigns **baking and verifying on the model**, you need the mesh, camera, mapping and suitable tools. This stage has a clear owner. Do not assume the artist must do more work after the views are handed off.

## Paint the view

The tool must accept the source and let you adjust the layout. If it does not, report the paint part as blocked. Choose an anchor. Keep color, material and landmarks between angles. Do not paint camera-dependent specular or rim light into the projected color, unless the design or the target allows it. Tell a real edge stroke apart from a silhouette outline. Read hand-painted or PBR only when you need to solve a stroke or shading problem. Do not require the whole surface pipeline.

Open the output. Check framing, size, landmarks and the kept parts. Resizing fixes the canvas. It does not prove alignment. Alpha that you just applied with a mask only verifies masking. It does not prove that the content fits the geometry. Process the image with the tools and permissions of the session. For hidden parts with no source, record the inference. Do not reopen the design yourself.

## When integration evidence exists

The owner projects or bakes, then renders the source views and, when needed, angles the author did not use, to confirm coverage and seams. The artist uses the result to fix the assigned areas. Do not bake again. Grazing or occluded views need suitable weighting/visibility. Even blending can blur detail. The edge of a flat pattern does not need to match a depth edge. Compare color at the matching surface area, in the same space and conditions. Do not apply a ΔE or pixel threshold that nobody defined.

## Hand off within scope

Hand off paint_<view>, the source guide/version, the checks and the inferences. Hand off the palette/schema only if the caller needs them. If the paint meets the contract, you may record the paint stage as complete, and integration as not checked or owned by the caller. If the task requires integration as well and it is missing, record that part as partial/blocked. Do not claim seamless or game-ready from paint views alone. Baked lighting rotates with the object. Record the pose/lighting range that you checked.
