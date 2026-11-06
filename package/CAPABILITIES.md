# Capabilities and loading — {{PACKAGE}} v{{VERSION}} ({{EDITION_TITLE}})

There is no umbrella skill. Call the skill you need by name, or describe the task and let {{APP}} select the skill from its description. The 2D Artist and Texture Artist skills are optional routers for unclear tasks.

| Group | Skills | Use for |
| --- | --- | --- |
| Art direction | zps-visual-intelligence, zps-creative-brainstorming, zps-visual-research, zps-art-style-development, zps-art-bible-artist-direction, zps-artistic-critique, zps-art-director-library-manager | Image analysis, direction, references, style rules, Bible and briefs, formal critique, library work |
| Concept | zps-concept-artist, zps-concept-views | Concept images and grey-box paint-overs for 3D; the other orthographic views of an approved concept, measured against one blockout |
| 2D and UI | zps-2d-artist, zps-asset-2d, zps-ui, zps-2d-review | In-game images, UI art, 2D and UI review |
| Texture | zps-texture-artist, zps-texture-planning, zps-surface, zps-texture-review | Texture method, maps and materials, texture review |
| 3D | zps-3d-artist | Static props: build, optimize, QA, export |
| Learning | zps-art-learning | Recorded results and feedback, improvement proposals (only on request) |

{{APP}} reads the name and description of every skill at the start of a session. It reads a SKILL.md and its references only when it selects that skill. Script code is never loaded into the prompt; the agent runs it.

Use one lead skill per deliverable. Concept makes design images; Asset 2D makes in-game images; UI makes UI art and the developer handoff; 3D owns mesh, UV and bake; Texture owns maps and materials on a given model version. The user's and project's requirements win over defaults such as the Godot profile.

A self-check is not owner approval. A review is independent only if a separate reviewer did it. A missing tool blocks only the work that needs it.
