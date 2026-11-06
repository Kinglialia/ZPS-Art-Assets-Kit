---
name: zps-3d-artist
description: "Make, optimize or check static 3D game props: model from a concept yourself in Blender, or with Meshy, Tripo or ZPS 3D Gen, then retopo, UV, texture, GLB and QA. Use for modeling and polygon reduction (\"dựng model\", \"giảm mặt\", \"low poly\", \"kiểm model\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 3D Artist

**Not for:** 2D drawing, concept art or texture painting (zps-texture-artist).

This file is a router. Read it, then read only the one path file that the job needs. Static triangle-mesh props are supported. Rigging, animated characters and cloth are outside this toolset; name the unsupported part and continue the supported work.

## 1. Pick the job

| Input | Job | Read |
|---|---|---|
| A concept, and a model is wanted | Make a model | Section 2 |
| An existing model to reduce or clean | Optimize | [optimize](references/optimize.md), then [texture handoff](references/texture-handoff.md) |
| A model to check only, no edits | Review | [QA tools](tools/asset_checks/README.md) and [review rubric](templates/REVIEW-RUBRIC.md) |

All jobs use [pipeline](references/pipeline.md) for setup, intake, the QA gate, finalize and the report. Read only the section you need.

## 2. Make a model: ask the method first

If the request already names the method, use it and skip the question. Otherwise ask one question with five answers:

1. **Self-model**: the agent builds the model as code in Blender (the kit's self-build).
2. **Meshy**: Meshy makes the mesh and the texture.
3. **Tripo**: Tripo makes the mesh and the texture.
4. **ZPS 3D Gen**: the team's image-to-3D service (`zps-ai`), free, with an UltraTex texture (non-commercial license).
5. **Not sure**: the agent reads the concept and recommends one.

If the answer is "Not sure", measure the concept first (type, part count, symmetry, thin parts, text or logos, available views). Then show one table for the four methods: time, cost, who paints the texture, the risk for this concept, and your recommendation with its reason. Get the times and costs from `tools/estimate.py show` (section 4). Use this first rule set:

| Concept | Recommend | Reason |
|---|---|---|
| Architecture, modular parts, hard-surface low poly | Self-model | Exact sizes, clean topology, edits by parameter |
| Organic shape, sculpted detail | Meshy or Tripo | AI generators make organic forms better than code |
| Organic shape, fast and free | ZPS 3D Gen | Internal service, about 1 minute, no cost. UltraTex texture is for non-commercial use: say so |
| Text, logos, thin or sharp parts | Self-model, or AI with manual fixes | Generators often break text and thin parts |

Then read the path file:

| Method | Path file | Texture |
|---|---|---|
| Self-model | [self-model](paths/self-model.md) | Texture Artist |
| Meshy | [meshy](paths/meshy.md) | Meshy retexture on the final mesh |
| Tripo | [tripo](paths/tripo.md) | Tripo texture on the final mesh |
| ZPS 3D Gen | [zps3d](paths/zps3d.md) | UltraTex from the service, baked to the final mesh |

Before the work starts, check the tools of the chosen method: `python3 <SKILL>/tools/gen/gen_api.py keys` for Meshy and Tripo keys, for ZPS 3D Gen that `zps-ai` is installed and `~/.config/zps-ai/credentials.json` exists (no network; `zps-ai whoami` needs network), Blender for every method. If a Meshy or Tripo key is missing, show the user the path of the key file and ask the user to paste the key into that file, not into the chat. If the user has no key, use Self-model. Tell the user the time estimate of the chosen method before you start.

If the concept has only one view and the chosen method needs more (multi-view input for Meshy, Tripo or ZPS 3D Gen, or the hidden sides for Self-model), offer [Concept Views](../zps-concept-views/SKILL.md) first. One round of image generation costs less than a second paid 3D generation. If its hand-off package already exists, use it.

## 3. Budget

Use the budget from the brief or the project if it has one. If not, choose it yourself and do not ask: run the sweep in auto mode (the fewest triangles that pass the floor, see [optimize](references/optimize.md) §4–6), capped by the size-class budget in `config.yaml`. Ask only when the camera or the platform is unknown and the project does not record it. Record the chosen budget and its reason in `task/spec.json`.

## 4. Learn from each job

After each model, append one record: `python3 <SKILL>/tools/estimate.py log --project <project root> --method self|meshy|tripo|zps3d --minutes <total> --credits <spent> --tris <final> --complexity <0-1>`. The record goes to `<project root>/.zps-art/estimates.jsonl`, never into the skills folder. `estimate.py show --project <project root>` prints the defaults from `estimates.json`, replaced by the median of the project records when a method has 3 or more.

## Rules for every path

- Work within the AD brief, the chosen direction, the camera and the technical limits. Do not repeat an approval that the user already gave. Never relax a threshold only to pass.
- Use an asset workspace: read-only input, `task/spec.json`, versioned work, evidence, deliverables. Numbers come from measured files, not from visual guesses. Record the exact version and view that you inspected.
- In the reference files, "task giver", "visual standard keeper" and "approver" mean the user. Thresholds are in `task/spec.json`; measurements come from the scripts in `tools/`.
- One build path and one writer per asset. Builder and critic briefs ([builder](agents/3d-builder.md), [critic](agents/3d-critic.md)) are task prompts. Without authorized delegation, do a self-review and label it.
- A paid call (Meshy, Tripo) needs a dry run (`--dry-run`), the cost, and the user's approval first. Create one budget file per asset: `{"max_credits": <approved>, "used_credits": 0}`. Never run paid calls in parallel on one budget file. Never print a key.
- Number of generations: propose it from the concept and show the cost. Clear concept with enough views: 1. No back view: make the views with Concept Views, then generate once with multi-view. If the user declines that, 2 generations (one image, and multi-view) and keep the better one. If a generation fails, ask before you generate again.
- A failed mandatory geometry check blocks the final export. Label a diagnostic preview as a preview. If no mesh meets the budget, report the gap and the smallest valid alternative. A required check that did not run is pending, not passed.
- `finalize.py` checks recorded technical results only, not art approval. `report.py` makes a draft report. State source and final triangles, budget, measurements, texture source, inferred hidden surfaces, missing checks and file paths. Claim engine or device validation only if you did it.
- For learning capture that the user requests, use [Art Learning](../zps-art-learning/SKILL.md). Do not change skill thresholds or code automatically.

[AD routing](../.art-director-support/workflows/art-direction.md) selects the next capability without the full pipeline.
