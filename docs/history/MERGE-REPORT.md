# Merge report — ZPS Art Director Codex v0.5.0

Date: 2026-11-05. Base: AD + Concept v0.4.0. All five requested sources were read and incorporated. Original archives and earlier combined versions remain unchanged. This package has not been installed into live skills directories.

## Source decisions

| Source | Integrated result | Preserved limits |
| --- | --- | --- |
| Codex-ZPS-2D-Artist-v0.4.0.zip | 2D Artist, Asset 2D, UI Art, 2D Review; production/UI references, templates and tool helpers | Godot/mobile conventions are target-specific; no UX redesign implied |
| Codex-ZPS-Texture-Artist-v0.4.0.zip | Texture Artist, Texture Planning, Surface, Texture Review; method-specific references and map contracts | Mesh/UV/high-to-low bake stays with 3D; texture review does not automatically change geometry |
| 3d-artist-skill.zip | 3D Artist, complete original modeling/optimization/QA tool directories, config, craft references and optional builder/critic prompts | Static props; source dependency requirements remain; optional delegated reviewers are not Claude registrations or automatic owner approval |
| Art-Director-Library-and-Manager-v0.2.0.zip | Full immutable offline snapshot in resources/library-v0.2.0; current manager documents how to locate it | Current manager retained, not downgraded to old source version; old embedded skill and Drive metadata are historical data; no cloud sync |
| learning-layer-research.md | Source proposal preserved in release-notes; Art Learning skill and project ledger CLI implemented | No claim that research citations were reverified; no automatic threshold lowering, blank-input approval, statistical calibration or self-writing skills |

## Architecture

18 named skills = existing 8 + 4 for 2D/UI + 4 for texture + 3D + Learning. No mandatory umbrella AD entrypoint or agent team was added. Each capability has a ZPS display name and Codex identifier. The AD workflow routes to specialist production/review without duplicating general critique. Role boundaries hand off authorized work inside the bundle rather than automatically stopping at every discipline boundary.

Identical 2D/texture adapters, rules and scripts were consolidated in `.art-production-support`. Shared source content was 740,567 bytes across repeated copies; consolidated/adapted content is 95,028 bytes (about 87% less). All 13 shared Python scripts are retained once. Markdown references were remapped. 3D tools remain together so their relative imports/config lookup continue working.

Runtime grows from 62,900 bytes / 21 files to 893,150 bytes / 168 files, largely because of executable 3D tooling. Combined SKILL.md bodies grow from 45,241 to 76,618 bytes across 8 -> 18 skills. These are file sizes, not measured context tokens. Scripts, conditional references, offline library and ledgers are not intended to load wholesale into context. Actual Codex loading/token use has not been instrumented.

## Behavioral adaptations

- Replace snapshot-specific Codex model/login/output-directory claims with current-tool discovery instructions. Optional API adapters retain a separate explicit budget and no live calls were tested.
- Remove automatic three-call budget extension; maintain task-authorized limits.
- Scope fixed UI option counts and approval loops to the actual request and authorization.
- Quick specialist review does not force numerical scoring or tracked issue IDs.
- Keep 3D detailed workflow in a conditional reference; use a single builder by default. Optional reviewer prompts cannot imply independent review when executed by the same agent.
- Preserve source thresholds as uncalibrated defaults; do not loosen checks to manufacture pass. The shipped finalizer checks recorded technical evidence, not art approval or all possible required engine checks.
- Keep current Library Manager and project-local configuration; source snapshot data and historical manager remain outside installed runtime.
- Learning separates measured runs, explicit attributed verdicts and candidate lessons. Empty/missing input never means human approval. Supersession is append-only. Review produces proposals only; script integrity is not artistic validation.

## Learning implementation boundary

Implemented: ingest report + artifact/spec snapshots; explicit judge; candidate flag + fixture snapshot; review current judgments and exact matching corrections; doctor ledger/evidence integrity. Uses explicit project --root, file locking and no background ingestion.

Not implemented: statistical threshold optimization, Cohen kappa/Youden analysis, semantic clustering, automated enforcer generation, executable fixture replay, self-editing instructions or scheduled review. The full source research document is retained for later work. The implemented CLI is a foundation, not a claim to have built the entire proposed research system.

## Verification

- Source ZIP CRC and declared source manifests: valid for 2D, texture and the library.
- 18 frontmatters/UI YAML parsed with Ruby Psych; identities/display names checked.
- Runtime Python syntax and all relative Markdown links checked.
- Installer: preview/cancel, fresh install/verify, idempotence, duplicate aliases in all roots, modified-file protection, upgrade backup/restore, unrelated-file retention, corrupt/unlisted payload and symlink rejection.
- Actual isolated upgrade v0.4.0 (8 skills) -> v0.5.0 (18) -> rollback -> verify original 8. Resources are not installed into skills roots.
- Library: all original manifest hashes preserved; 33 supplied unit/regression tests passed; 44 READY records and 132 image records validated. READY is source metadata, not current art approval.
- Learning: read-only no-write behavior, no inferred approvals, explicit verdicts, skip exclusion, supersession, duplicate lesson protection, fixture tampering and mismatched artifact identity tested using synthetic fixtures.
- Shared tools: synthetic RGBA inspector -> saved evidence gate; changed image detected; projection SVG generation; API dry-run without network; 3D finalizer CLI loads.

Full geometry/render/bake requires missing bpy/numpy/PyYAML and was not executed in this Python environment. No dependencies were installed, no paid generation was invoked, and no Blender/engine/device or artistic benchmark pass is claimed. YAML was tested using Ruby; the bundled Python skill validator itself remains unavailable without PyYAML. This is self-review, not independent art assessment.

See individual TEST-RESULTS text files for the checks performed. PACKAGE-MANIFEST.json covers distribution files; manifest.json covers only installed runtime; the library retains its original MANIFEST.json.
