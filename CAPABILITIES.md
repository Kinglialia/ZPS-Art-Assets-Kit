# Capabilities and loading — v0.5.6

The bundle name is ZPS Art Director Codex. There is no mandatory umbrella AD SKILL.md. Call the specific capability directly, or let the assistant select it from the request. The 2D Artist and Texture Artist entrypoints are optional routers for unclear tasks. No automatic multi-agent team is installed.

| Group | Display names (each prefixed ZPS - and suffixed - Codex) | Load when |
| --- | --- | --- |
| AD | Visual Intelligence, Creative Brainstorming, Visual Research, Art Style Development, Art Bible & Artist Direction, Artistic Critique, Art Director Library Manager | Direction, analysis, rules, research, general review or library work |
| Concept | Concept Artist | Actual concept image creation/editing or grey-box paint-over |
| 2D/UI | 2D Artist, Asset 2D, UI Art, 2D Review | In-game images, UI visuals or specialist image review |
| Texture | Texture Artist, Texture Planning, Surface, Texture Review | Model surface methods, maps or material review |
| Geometry | 3D Artist | Static prop building, mesh/UV/bake, optimization or QA |
| Learning | Art Learning | Requested project evidence capture and improvement proposals |

Discovery exposes names/descriptions according to host behavior. A selected skill's body and references are read on demand; linking another skill does not itself load it. Shared rules, adapters, scripts, templates and the shared review method are in one .art-production-support directory. Script code is not automatically included in prompts. Library images/index and learning ledgers remain data outside skill entrypoints. This packaging has not been instrumented to measure actual Codex context consumption.

Use one lead output capability. Concept is a design image, Asset 2D is an in-game image, UI Art is visual UI handoff, 3D owns mesh/UV/bake, Texture owns maps/materials on a specified model version. Specialized 2D/texture reviews serve their domain without also requiring a duplicate general critique. Current user/project constraints take precedence over source defaults such as Godot/mobile assumptions.

No role claims self-check is owner approval. Independent review is labeled only when a separate reviewer actually exists. Missing tools block dependent work only; the package does not promise every supplied script can run without its dependencies.
