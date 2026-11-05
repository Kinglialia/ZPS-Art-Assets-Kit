# UI handoff — keep only what is in scope

Use together with the [task record](../../.art-production-support/templates/task-record.md). Use relative paths. Do not include secrets or machine-specific paths.

```markdown
# UI handoff <screen/component> <version> — confirmation level: design | Godot | device

## Context
- Godot version, base size, stretch/aspect/scale, supported ratios, orientation, safe area:
- Approved wireframe/interaction spec (source):

## Output
| ID | File (PNG 1x/@2x) | Purpose | Editable source (SVG / generated raster / combination) | Tool and export method (for example `svg_render.py --scales 1 2`) |
|---|---|---|---|---|

## Component
| ID/version | Layout, sizing, Container/anchors | Text: font, fallback, overflow | State | Theme/StyleBox/asset |
|---|---|---|---|---|

## 9-slice
| Asset | Texture margin (L/T/R/B) | Content margin (L/T/R/B) | Stretch/tile | Min/max tested |
|---|---|---|---|---|

## QA
| Check | Version/environment/size | Criterion | Evidence | Result | Validity |
|---|---|---|---|---|---|

## Open items and external resources
- Issue, who handles it, whether it blocks handoff:
- Font/resource: source, license, attribution:
```
