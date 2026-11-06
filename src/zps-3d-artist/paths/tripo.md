# Path: Tripo

Tripo makes a dense mesh without a texture. The kit reduces it to the budget, because Tripo's own retopo costs more than a new generation. After UVs and QA, Tripo paints the texture on the final mesh.

Tools: `tools/gen/gen_api.py` (Python 3 standard library), `TRIPO_API_KEY`. Tripo bills per use: 1 credit = 0.01 USD. Check the key with `python3 <SKILL>/tools/gen/gen_api.py keys`.

## Cost (Tripo credits, prices of 2026-11-06)

| Step | Settings | Credits |
|---|---|---|
| Generate | `v3.1`, `geometry_quality: detailed`, no texture, no PBR | 40 (0.40 USD) |
| Reduce | the kit sweep in Blender | 0 |
| Texture | on the final mesh | 10 (0.10 USD) |

Do not call Tripo `mesh/decimate` (30–40 credits for each level) unless the user asks.

**Number of generations.** Propose it from the concept, and show the cost:
- Clear concept, enough views: 1 generation.
- No back view, or a hard shape: 2 generations (one image, and multi-view), then keep the better one.

Before each paid call, run the same command with `--dry-run`, show the user the step and its credits, and wait for approval. If a generation fails, ask before you generate again. Create a budget file per asset: `{"max_credits": <approved>, "used_credits": 0}`.

## Steps

1. **Intake.** [pipeline](../references/pipeline.md) §Intake, with `validate_concept.py`. Prepare each view: one object, plain or removed background, even light, PNG or JPEG.
2. **Generate.**
   ```
   python3 <SKILL>/tools/gen/gen_api.py generate --provider tripo --view front=<abs png> [--view back=<abs png>] --out <abs work>/gen/v1 --budget-file <abs work>/budget.json
   ```
   Multi-view needs `front` and at least one more view. The docs do not say whether `left` is the object's own left or the camera's left. For an asymmetric prop, send only `front` and `back`. The script uploads the images, waits, and writes `model.glb` and `task.json`. Download happens at once, because Tripo does not document how long result links stay valid.
3. **Reduce.** Use the GLB as `input/model.glb` and follow [optimize](../references/optimize.md): Audit, Gate 1, Cleanup, Sweep (`--auto`, or `--budget`). Tripo can soften hard edges: check the normal renders of hard-surface props, and say so in the report.
4. **UVs.** Run Bake in `rebake` mode on the chosen level. The untextured source gives a flat albedo; the bake is only for the UV unwrap. Run `uv_check`.
5. **Texture.**
   ```
   python3 <SKILL>/tools/gen/gen_api.py texture --provider tripo --model <abs baked GLB> --style-image <abs concept front> --out <abs work>/texture/v1 --budget-file <abs work>/budget.json
   ```
   The docs do not say whether Tripo keeps the uploaded UVs. Run `uv_check` and `mesh_check` on the returned GLB. If the UVs or the triangle count changed, run the Tripo GLB through [optimize](../references/optimize.md) again (Audit, Cleanup, Sweep with `--budget <chosen tris>`, Bake `rebake`). Bake then moves the Tripo texture onto a mesh at your count. Record that in the report.
6. **QA and deliver.** [QA gate](../references/pipeline.md#qa-gate-every-path-and-the-review-only-job), `finalize.py`, `report.py`. Call Texture Artist only if the texture fails review or the caller asks ([texture handoff](../references/texture-handoff.md)).
7. **Learn.** `tools/estimate.py log --method tripo --credits <used> …` (SKILL.md section 4).

Licence and result-link lifetime for Tripo are not confirmed. Before a commercial project, ask the user to confirm Tripo's terms for their plan.

If a call fails, read `task.json` and the error. Do not retry in a loop. Tripo does not charge failed or cancelled tasks.
