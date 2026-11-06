# Path: ZPS 3D Gen (`zps-ai`, UltraTex)

The team's image-to-3D service makes a dense textured mesh. The kit reduces it to the budget and bakes the texture onto the final mesh. The service is free for the team.

Tools: the `zps-ai` CLI (`~/.local/bin/zps-ai`), signed in: `~/.config/zps-ai/credentials.json` exists. Every `zps-ai` command that reaches the portal needs network, also `whoami` and `guide`. If it is missing, ask the user before you install it: `curl -fsSL https://zps-ai-console.zingplay.com/cli/install.sh | sh`, then `zps-ai login` (browser sign-in). No API key is needed. Run `zps-ai guide 3d` once per session: the service admins keep the current parameters there, and they override this file.

## Facts

- Endpoints: `/send` (one image), `/send-multiview` (1–4 views: `front`, `left`, `back`, `right`). Always use `--wait`; it follows the job and downloads the GLB. Do not use `/generate`.
- Time: about 35 s for one textured image; about 75–140 s with UltraTex; about 20 s more for each view besides `front`. One GPU and one queue for the whole team: check `zps-ai status` and add the wait to the estimate.
- The service deletes results after 24 hours. Download at once (`--wait -o <dir>` does it).
- **Texture: always UltraTex** (`commercial:=false`). The project owner chose this. UltraTex uses a model with a non-commercial license. Write "texture: UltraTex (non-commercial license)" in the report and in `task/spec.json`, so that the next person knows.
- Set `metal:=true` when the object has visible metal (weapon, armour, tools, vehicle, coins). Otherwise `metal:=false`.
- View names: the guide defines `left` as the camera on the left of the object. The kit defines `left` as the object's own left (camera at +X). For an asymmetric prop, confirm which side each concept image shows before you send it. If you are not sure, send only `front` and `back`.

## Steps

1. **Intake.** [pipeline](../references/pipeline.md) §Intake, with `validate_concept.py`. Prepare each view: one object, plain or removed background, even light.
2. **Generate.** Use a dense mesh so that the sweep has room:
   ```
   zps-ai call 3d /send image@=<abs front.png> face_count:=200000 texture_size:=2048 commercial:=false metal:=false --wait -o <abs work>/gen/
   zps-ai call 3d /send-multiview views.front@=<abs front.png> views.back@=<abs back.png> commercial:=false --wait -o <abs work>/gen/
   ```
   Open the GLB renders. If the shape is wrong, run once more with another view set before you go on. Each run is free but takes queue time.
3. **Optimize.** Use the GLB as `input/model.glb` and follow [optimize](../references/optimize.md): Audit, Gate 1, Cleanup, Sweep (auto, or the budget), then Bake in `rebake` mode. The bake moves the UltraTex texture from the dense mesh to the final mesh. Check the bake SSIM against `texture.ssim_min`.
4. **QA and deliver.** [QA gate](../references/pipeline.md#qa-gate-every-path-and-the-review-only-job), `finalize.py`, `report.py`. Texture Artist is not called unless the bake fails or the caller asks for a texture change ([texture handoff](../references/texture-handoff.md)).
5. **Learn.** `tools/estimate.py log --method zps3d …` (SKILL.md section 4).

If `zps-ai` reports an error, tell the user what it says (for example a sign-in or certificate problem, which `zps-ai doctor` shows). Do not debug the service. Offer another method.
