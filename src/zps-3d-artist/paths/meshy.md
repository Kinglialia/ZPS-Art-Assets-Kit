# Path: Meshy

Meshy makes a dense mesh without a texture. The kit finds the lowest good triangle count for free. Meshy remeshes once at that count. After UVs and QA, Meshy paints the texture on the final mesh and keeps its UVs.

Tools: `tools/gen/gen_api.py` (Python 3 standard library), `MESHY_API_KEY`. The Meshy API needs a paid Meshy plan; the Free plan has no API and no remesh. Check the key with `python3 <SKILL>/tools/gen/gen_api.py keys`.

## Cost (Meshy credits, prices of 2026-11-06)

| Step | Settings | Credits |
|---|---|---|
| Generate | `meshy-7.1`, geometry 2k, no texture, no remesh, keep the pre-remesh GLB | 25 |
| Remesh | one call at the chosen count, triangle | 5 |
| Retexture | on the final mesh, keep UVs | 10 |

**Number of generations.** Propose it from the concept, and show the cost:
- Clear concept, enough views: 1 generation.
- No back view, or a hard shape: 2 generations (one image, and multi-view), then keep the better one.

Before each paid call, run the same command with `--dry-run`, show the user the step and its credits, and wait for approval. If a generation fails, ask before you generate again. Create a budget file per asset: `{"max_credits": <approved>, "used_credits": 0}`.

## Steps

1. **Intake.** [pipeline](../references/pipeline.md) §Intake, with `validate_concept.py`. Prepare each view: one object, plain or removed background, even light, more than 1040 px, near-orthographic.
2. **Generate.**
   ```
   python3 <SKILL>/tools/gen/gen_api.py generate --provider meshy --view front=<abs png> [--view back=<abs png>] --out <abs work>/gen/v1 --budget-file <abs work>/budget.json
   ```
   With more than one view, Meshy reads the first image as the front; the order of the others does not matter. It writes `glb.glb` (and `pre_remeshed_glb.glb` when present) and `task.json` with the task id. Meshy deletes results after 3 days.
3. **Find the triangle count for free.** Use the dense GLB as `input/model.glb` and follow [optimize](../references/optimize.md): Audit, Gate 1, Cleanup, Sweep (`--auto`, or `--budget`). The sweep result is the chosen count.
4. **Remesh once at that count.**
   ```
   python3 <SKILL>/tools/gen/gen_api.py remesh --provider meshy --task-id <id from task.json> --polycount <chosen tris> --topology triangle --out <abs work>/remesh/v1 --budget-file <abs work>/budget.json
   ```
   Use triangle topology for static props (Meshy keeps more detail with triangles than with quads). Measure the Meshy result with `measure.py` against `ref_high.glb`, the same way the sweep measures the kit's level. Keep the better one (worst-view IoU, then Hausdorff). Record both in the report.
5. **UVs.** Run Bake in `rebake` mode on the kept mesh. The untextured source gives a flat albedo; the bake is only for the UV unwrap. Run `uv_check`.
6. **Texture.**
   ```
   python3 <SKILL>/tools/gen/gen_api.py texture --provider meshy --model <abs baked GLB> --style-image <abs concept front> --out <abs work>/texture/v1 --budget-file <abs work>/budget.json
   ```
   It sends `enable_original_uv: true`. Run `uv_check` and `mesh_check` again on the returned GLB: confirm that the UVs and the triangle count did not change.
7. **QA and deliver.** [QA gate](../references/pipeline.md#qa-gate-every-path-and-the-review-only-job), `finalize.py`, `report.py`. Call Texture Artist only if the texture fails review or the caller asks ([texture handoff](../references/texture-handoff.md)).
8. **Learn.** `tools/estimate.py log --method meshy --credits <used> …` (SKILL.md section 4).

The user can also remesh on the Meshy website at no credit cost (paid plan). If the user wants that, give the chosen count and the remesh settings, and continue at step 5 with the file that the user supplies.

If a call fails, read `task.json` and the error. Do not retry in a loop. Failed Meshy tasks are refunded.
