> Historical source research, preserved for provenance. Claims and model/version limits below were not reverified during this merge; do not treat them as current Codex constraints or calibrated thresholds.

# Research notes (2026-11-03)

Why the skill's rules are what they are. Each claim has a link. Tags: **[C]** read in a primary source, **[S]** search snippet or aggregator only, **[I]** inference. Several hosts (arxiv, huggingface, docs.blender.org, polycount, Unity/Godot/Unreal docs) were not reachable when this was written, so many numbers are [S]; re-check before relying on an exact figure.


## 0. Why the self-build loop has this shape

frontier models now write bpy that runs almost every time, but the geometry stays toy-like with floating or misplaced parts; better harnesses raise executability, not shape quality (3DCodeBench). The one code-built system that matched native generators on props (Procedura) got there by constraining the representation: named parts, typed machine-checked attachments, hard gates per part, a separate critic, one patch per cycle. Placement is the weakest LLM skill (P3D-Bench part F1 ≈ 0.5). So: the builder never types a coordinate. See `research_notes.md` §1.

## 1. LLM-written geometry

- Frontier models now write executable bpy almost always, but shape quality does not improve with better harnesses; successful renders still have floating or disconnected parts. 3DCodeBench [S] — https://github.com/gaoypeng/3dcodebench
- BlenderGym: large gap between VLM systems and average human Blender users; spending inference on **verification** (re-ranking fewer candidates) beats spending it on more generations. [C/S] — https://openaccess.thecvf.com/content/CVPR2025/papers/Gu_BlenderGym_Benchmarking_Foundational_Model_Systems_for_Graphics_Editing_CVPR_2025_paper.pdf
- Part placement is the weakest MLLM 3D skill: PartMatch F1 ≈ 0.5 on assemblies. P3D-Bench [S] — https://arxiv.org/pdf/2606.11152
- Procedura (MIT, CPU-only): named parts as CSG, typed machine-checked mates, per-part gates, decoupled vision critic, one patch per cycle; rated 0.828 vs TRELLIS.2 0.810 on its own hard-surface benchmark with one VLM judge. [C/S] — https://github.com/87003697/Procedura
- LL3M: planner/coder/critic/verifier agents writing bpy; results recognisable but stylised; critic "may miss subtle spatial artifacts". [C] — https://github.com/threedle/ll3m
- BlenderAlchemy: separate edit generator and state evaluator, edit reversion when a branch regresses. [S] — https://arxiv.org/abs/2404.17672
- No paper found that fits LLM-written prop params to concept silhouettes with gradient-free search; we do it because it is cheap on CPU. [I]
- Image-to-3D generators: raw output commonly has inner faces, non-manifold edges, 50k+ triangles; Meshy `meshy-t2` and Tripo P-series/`smart_low_poly` target low poly directly. Prices drift; verify on vendor pages. [S] — https://docs.meshy.ai/api/image-to-3d.md , https://developers.tripo3d.ai/en/pricing
- No AI retopo model is commercially usable on CPU/macOS today (MeshAnything V2 non-commercial; others need CUDA). Classical: Instant Meshes CLI, QuadWild, Blender Decimate/Quadriflow. [C] — https://github.com/buaacyw/MeshAnythingV2/blob/main/LICENSE.txt , https://github.com/wjakob/instant-meshes

## 2. VLM as judge

- Textured models get +144 Elo over untextured in 123k human votes: judges reward presentation over geometry. Judge geometry on clay/normals. 3D Arena [C] — https://arxiv.org/abs/2506.18787
- GPTEval3D, 3DGen-Bench, Gen3DEval all feed normal maps alongside RGB and use pairwise comparisons. [C] — https://github.com/3dtopia/gpteval3d , https://arxiv.org/html/2503.21745v2 , https://arxiv.org/html/2504.08125v1
- VLM evaluators agree with humans 47–59%; symbolic evaluators 83–94%. VLMs are better at suggesting fixes than grading. SceneCritic [S] — https://arxiv.org/html/2604.13035v1
- Binary verification questions answered from renders, unresolved items fed back as fixes, measurably improved CAD code. CADCodeVerify [C] — https://arxiv.org/html/2410.05340v2
- Pairwise judging has position bias; judge twice with order swapped, treat disagreement as a tie. [S] — https://arxiv.org/pdf/2402.04788v3
- Claude vision: long edge 1,568 px standard tier, 2,576 px on 4.7+; features under ~200 px unreliable; localisation approximate; label each image. [C] — https://platform.claude.com/docs/en/build-with-claude/vision
- Numbered marks on regions sharply improve VLM grounding (Set-of-Mark) → part-ID renders with numbers. [C] — https://github.com/microsoft/SoM
- Self-correction without external feedback degrades; a fresh-context, read-only reviewer is the standard pattern. [C] — https://arxiv.org/html/2310.01798v2 , https://code.claude.com/docs/en/best-practices

## 3. Mesh reduction

- meshoptimizer: `simplify` may stop early; weld first or it gets stuck; `Permissive` collapses across seams; `simplifySloppy` merges shells and ignores seams; experimental voxel `remesh` in v1.3. [C] — https://github.com/zeux/meshoptimizer/blob/master/README.md
- Python bindings are third-party and lack remesh; gltfpack CLI exposes `-si`, `-se`, `-sp`, `-sa`, `-slb`. [C] — https://pypi.org/project/meshoptimizer/ , https://raw.githubusercontent.com/zeux/meshoptimizer/master/gltf/gltfpack.cpp
- gltf-transform `simplify` uses positional error only; Open3D decimation drops UVs. [C] — https://github.com/isl-org/Open3D/issues/6615
- Voxel remesh loses UVs and thin features. [C] — https://docs.blender.org/manual/en/dev/modeling/modifiers/generate/remesh.html
- Blender "Select Interior Faces" is topological, not visibility-based; use ray visibility. [C]
- Smart UV Project must run in Edit Mode and is non-deterministic; xatlas is deterministic. [C] — https://pypi.org/project/xatlas/
- No published mobile "visually lossless" threshold; LOD literature uses 1-pixel projected error. [C] — https://www.oreilly.com/library/view/level-of-detail/9780080510118/chapter-128.html
- Kneedle for the knee of an error curve is our use, not documented practice. [I] — https://github.com/arvkevi/kneed

## 4. Game-ready standards

- Arm/Android: largest on-screen objects ~3,000 tris in a 210k-tri/frame demo; hero alone on screen 11,000; keep triangles above 10 px; 16-bit index meshes cap at 65,535 vertices; smoothing angle < 90°; split UVs at hard edges. [C] — https://developer.android.com/games/optimize/geometry , https://developer.android.com/games/optimize/textures
- UV seams and hard edges duplicate vertices: count vertices after export. [S]
- UV padding scales with resolution: ~4 px @512, 8 @1024, 16 @2048. [S] — https://polycount.com/discussion/191707/padding
- Mobile texel density 256–512 px/m is the common band. [S]
- One material per static prop is the default; each material ID is a draw call per instance. [S]
- Baked lighting in albedo forbids mirrored/overlapping UVs where lighting differs; flat palette atlases may overlap on purpose. [I]
- Unity has no native glTF import (needs glTFast); Unreal is cm/Z-up; Godot is m/Y-up and imports glTF natively. [C/S]

## 5. Budgets in config.yaml

`small 500 / medium 1500 / hero 5000 / environment 3000` tris are an inference anchored on the Arm figures and practitioner ranges, not a published standard. Each project should set its own in `task/spec.json`.
