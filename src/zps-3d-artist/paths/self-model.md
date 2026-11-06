# Path: Self-model (Blender, the kit's self-build)

The agent builds the prop as code. It writes a part graph and `bmesh` part functions, runs them in headless Blender, measures the result against the concept and fixes it part by part. No paid service is used.

Tools: Blender, the 3D tools venv (`tools/setup_deps.sh`). Every Blender command uses literal absolute paths: `<Blender> -b --python <SKILL>/tools/<dir>/<script>.py -- <args>`.

Good fit: crates, barrels, chests, pillars, fences, tables, lamps, signs, simple weapons, simple architecture. Poor fit: organic shapes, carvings, cloth, creatures. If the concept is a poor fit, say so and offer Meshy, Tripo or ZPS 3D Gen.

## Steps

1. **Intake.** Follow [pipeline](../references/pipeline.md) §Intake: `validate_concept.py`, view labels, height, texture style, budget (SKILL.md section 3). If the left/right convention is unknown or the concept views conflict, ask about the affected geometry before you build.
2. **Build.** Follow [self-build](../references/self_build.md): measure, part graph, coarse rollout, part-by-part gates, `param_fit`, critic loop. Keep fixed dimensions fixed when you fit cameras or parameters. After repeated failures, diagnose; do not retry without a new reason. Keep or revert each edit from the measured result, within the repair budget.
3. **Optimize.** Continue at [optimize](../references/optimize.md): Audit, Cleanup, Sweep (auto, or the budget), Bake for UVs.
4. **Texture.** Follow [texture handoff](../references/texture-handoff.md): call Texture Artist with part A.
5. **QA and deliver.** Run the [QA gate](../references/pipeline.md#qa-gate-every-path-and-the-review-only-job) on the textured GLB, then `finalize.py` and `report.py`.
6. **Learn.** Log the job with `tools/estimate.py log` (SKILL.md section 4).

Craft notes, only for the stage you do: [craft](../references/technique.md), [blockout](../references/blockout.md), [mesh/UV/bake](../references/mesh_uv_bake.md), [export](../references/export_engine.md), [bpy cookbook](../references/bpy_cookbook.md).
