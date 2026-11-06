# Self-build: concept → prop as code

You (the orchestrator) run the loop. The active artist writes the part graph and part functions. Use a separate critic only when authorized and available; otherwise label self-review. Scripts solve placement, run gates and tune numbers.

Why the loop has this shape: [research notes](research_notes.md) §0.

Work dir: `output/<asset>/work/self_build/`.

## Part graph (`part_graph.json`)

```json
{
  "units": "m", "up": "+Z", "front": "-Y",
  "params": {"body_w": 0.80, "body_d": 0.50, "body_h": 0.42, "lid_h": 0.12,
             "band_t": 0.01, "lock_w": 0.08, "lock_h": 0.10, "lock_t": 0.02},
  "parts": [
    {"name": "body", "primitive": "box", "dims": ["body_w", "body_d", "body_h"], "attach": null},
    {"name": "lid", "primitive": "custom", "fn": "lid_rounded", "args": ["body_w", "body_d", "lid_h"],
     "attach": {"type": "on_top", "to": "body"}},
    {"name": "band_left", "primitive": "box", "dims": ["band_t", "body_d", "body_h"],
     "attach": {"type": "flush_edge", "to": "body", "face": "-Y", "edge": "-X", "inset": 0.06}},
    {"name": "band_right", "attach": {"type": "mirror_of", "of": "band_left", "plane": "X"}},
    {"name": "lock", "primitive": "box", "dims": ["lock_w", "lock_t", "lock_h"],
     "attach": {"type": "center_on_face", "to": "body", "face": "-Y", "offset_uv": [0.0, 0.8]}}
  ]
}
```

Rules:
- Every dimension is a name in `params`; parts never hold raw sizes. Shared sizes share a name. `inset`, `depth` and `offset_uv` may be literals or param names.
- Sizes are floats (`1.0`, not `1`). Integer params are treated as segment counts and `param_fit` never touches them.
- `fixed_params: [names]` (with `_fixed_reason`) keeps `param_fit` off a param. Use it for sizes the brief gives (heights) and for sizes the concept cannot determine — with one 3/4 view, footprint depth drifts freely under a bbox-normalised IoU, so the critic sets it and it is fixed.
- Parts are numbered from 1 in build order; `--upto` and the critic's part numbers use the same numbering.
- A `custom` part may declare `dims: [w, d, h]` for the bbox gate; otherwise its first three args are read as w, d, h.
- Parts are listed in build order, largest first; each attaches to one listed earlier.
- `primitive`: `box` (dims w,d,h), `cylinder` (dims radius, height; `segments` 8–24; `axis` X|Y|Z, default Z), `wedge` (dims w,d,h; slope rises toward +Y), or `custom`: a function in `parts_lib.py` taking the arg values and returning a `bmesh.types.BMesh` centred on its own bounding box. Functions never position themselves.
- Optional `rotation_deg` about Z, multiples of 90°.
- Optional `material` label (for example `"material": "wood"`): the surface material of the part, for the texture handoff. The scripts ignore it. Set it on `mirror_of` parts too.
- Never write a location. Placement comes only from `attach`:

| Type | Meaning | Fields |
|---|---|---|
| `on_top` | Child's bottom sits on parent's top face | `offset_uv` (−1..1 across parent's top, default [0,0]) |
| `center_on_face` | Child flush against a parent face, outside it | `face` (±X/±Y/±Z), `offset_uv` |
| `flush_edge` | Against a face, aligned to one of its edges | `face`, `edge` (±X/±Y/±Z, perpendicular to face), `inset` (m from that edge) |
| `inset_into` | Sunk into a parent face by a set depth | `face`, `offset_uv`, `depth` (m) |
| `through_axis` | Passes through the parent along an axis | `axis`, `offset_uv` |
| `mirror_of` | Mirror copy of another part across the root's centre plane | `of`, `plane` (X/Y) |

`offset_uv` maps −1..1 to the face's two in-plane axes in fixed order: for ±X faces (Y, Z), ±Y faces (X, Z), ±Z faces (X, Y). The child's own extent is subtracted so −1/+1 means flush with the face edge, not overhanging.

## Loop

**1. Measure.** From the S0 masks and the recorded height, the builder computes overall and per-part sizes and prints a table (part, w/d/h, source view, how measured) before any geometry exists. Orthographic views give measurements; a 3/4 painting does not — estimate from it only with a stated assumption.

**2. Plan.** Builder writes `part_graph.json` and `parts_lib.py`. It reviews the plan once against the concept and may only **add** (a missing part, a clearer shape); never merge or drop parts.

**2b. Concept camera (painted 3/4 views).** A painted concept is rarely drawn from exactly azimuth 45° / elevation 30°. After the first coarse build, run `<SKILL>/tools/.deps/venv/bin/python <SKILL>/tools/self_build/fit_camera.py --work <w> --rollout <k> --spec task/spec.json --write-spec`: it grid-searches azimuth/elevation for every non-orthographic view and stores them in `spec.concept.cameras` (a measurement, not a threshold; say so when you show the spec). Fit it once, then keep it fixed while `param_fit` tunes sizes. Example: rock-moss 34 view fitted at 49°/22°, IoU 0.848 → 0.874 before any shape change.

**3. Rollouts.** Use one builder by default. Only with authorized delegation and budget, use `self_build.rollouts` independent builders (none sees the others), each writing `rollouts/<k>/part_graph.json` + `parts_lib.py`. Build each coarse and keep the best:
```
<BLENDER> -b --python <SKILL>/tools/self_build/assembly.py -- --work <w> --rollout <k> --coarse --spec task/spec.json
```
`--coarse` replaces `custom` parts by boxes of the same bbox. `assembly.py` writes `assembly.json` with per-view IoU when the spec has concept views. Pick the rollout with the highest worst-view IoU; copy it to `<w>/` and record all scores.

**4. Part by part.** For each part n in order:
```
<BLENDER> -b --python <SKILL>/tools/self_build/assembly.py -- --work <w> --upto <n>
<SKILL>/tools/.deps/venv/bin/python <SKILL>/tools/self_build/gates.py --work <w> --part <name>
```
Gates: (1) runs, non-empty mesh, traceback on error; (2) contact: share of sample points on the child's attaching face within 1 mm of the parent ≥ `contact_min_ratio` (`through_axis`: both ends stick out); (3) penetration: intersection volume / child volume ≤ `penetration_max_ratio` (`inset_into`: matches `depth` ±20%); (4) floaters: connected components besides the main one with a bbox edge ≥ `floater_span_ratio` × object size, error only when the count grows; (5) health: non-manifold, zero-area, loose verts on the union; (6) part bbox within `bbox_tolerance` of what its dims declare. On failure the builder fixes that part only, using the numbers in the gate JSON. After `part_max_attempts`, commit with a warning.

**5. Fit numbers.**
```
<BLENDER> -b --python <SKILL>/tools/self_build/param_fit.py -- --work <w> --spec task/spec.json [--part <name>]
```
Nelder–Mead over all params (or one part's), clamped to ±`max_param_change`, objective = mean orthographic IoU minus a small penalty when the worst view trails the mean. Keeps old values unless IoU improves by `min_gain`. Nobody hand-tunes numbers after this.

**6. Critic loop**, up to `self_build.critic_cycles`:
1. `<BLENDER> -b --python <SKILL>/tools/self_build/render_views.py -- --work <w> --spec task/spec.json --mode critic`. Produces, each a separate PNG at most `critic_max_long_edge` px, mid-grey background:
   - `clay_<view>.png` for front, back, left, right, 34 (matte mid-grey);
   - `normal_<view>.png`, same views (world-space normal colours);
   - `overlay_<view>.png` per orthographic concept view: concept mask red, model mask blue, overlap grey; IoU and red/blue % printed in the margin;
   - `parts_<view>.png` front and 34: each part a flat colour with its number drawn on it (Set-of-Mark), legend in the margin;
   - `prev_34.png` if a previous snapshot exists (for A/B).
2. If independent review is authorized and available, use a fresh reviewer (no builder context); otherwise perform a clearly labeled self-review. Give it: concept images, the image set with labels, `part_graph.json`, `assembly.json` (IoU per view, gate warnings), the previous diagnosis if any, and the single change the builder claims. Save its JSON to `diagnoses/<n>.json`.
3. Stop if `approved` is true.
4. Apply only `top_fix`: `<SKILL>/tools/.deps/venv/bin/python <SKILL>/tools/self_build/apply_edit.py --work <w> --diagnosis <n> --spec <abs>/task/spec.json`. For `structure`, the builder edits that one part (or adds one); for `param`, the script reruns `param_fit --part`. The script refuses a second edit on the same diagnosis, refuses if renders are older than the code (hash of `part_graph.json` + `parts_lib.py`), rebuilds, re-gates, re-measures, and reverts: for a `param` fix when the worst-view IoU drops by more than `revert_tolerance` below the best seen; for a `structure` fix only when any view falls below `spec.concept.min_iou`, because fixing block language can trade a little silhouette precision for the right planes (rock-moss: 0.911 loaf → 0.880 faceted, critic A/B "better"). The critic's A/B check then decides; `--revert` undoes it.
5. A/B check: the next critic call answers "better / same / worse than previous on the targeted criterion" twice with image order swapped. Inconsistent, `same` or `worse` → `apply_edit.py --work <w> --diagnosis <n> --spec <abs>/task/spec.json --revert` (same runner as above) and mark the fix as tried. A change that does not clearly help is removed: equal means discard, and the simpler version wins a tie. Record every attempt (kept or reverted, with one sentence of reason) in `diagnoses/`.

IoU here is computed on bbox-normalised silhouettes, so it measures proportions, not absolute size. The concept has no scale; `height_m` sets it later.

Ship the best snapshot (`best.json` → `snapshots/<n>/assembled.glb`), not the last one. Then continue at Optimize: Audit (triangulates, origin bottom-centre, scales to `height_m`), skip Gate 1, run Cleanup (on the clean union it only welds and writes `ref_high.glb` + `cleanup.json`, which Sweep and Bake need), then Sweep, Bake and QA.

Attaching to pointed or curved parents (a finial on a pyramid roof): `on_top` finds almost no contact. Give the parent a flat seat (truncate the tip) or use `inset_into`, whose depth is measured as maximum penetration along the face axis.

Choosing a rollout is manual: compare `rollouts/<k>/assembly.json` worst-view IoU and copy the winner's `part_graph.json` and `parts_lib.py` into `<w>/`.

## Build rules (for the builder)

- Read `bpy_cookbook.md` first. Prefer bmesh over `bpy.ops`.
- Bevels 1–2 segments; cylinders 8–16 segments (24 max). Every segment count is a param.
- Keep silhouette-defining details (handles, rims, feet, lock); leave surface detail (planks, rivets, engravings) to texture. See `technique.md`.
- No materials beyond one default; no textures (texture step handles colour).
- Parts are unioned into one closed mesh by manifold3d. Avoid coplanar overlaps: offset touching faces by about 0.001 m when one part sits inside another.
- Change only the part a gate or critic names, and say in one line what you changed.
