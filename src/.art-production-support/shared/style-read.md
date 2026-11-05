# Read a style from references into a style sheet

Use this when you receive a concept or style reference and there is no AD Art Bible or Artist Brief that is sufficient to draw from. The goal is a short style sheet. A person who reads it must draw in the same visual language. Each rule has evidence that is visible in the images.

## Contents
- When to read the style yourself and when to hand over to the AD
- 5-step procedure
- Style sheet template and examples

## When to read the style yourself and when to hand over to the AD

| Situation | Action |
|---|---|
| There is an AD Bible/Brief, and the references illustrate the Bible correctly | Use the Bible. The style sheet records only what the Bible does not say (for example, line on a 64px icon) |
| There are consistent references, but no Bible yet | **Read the style yourself.** Present the style sheet + 1 test sample for the user/AD to confirm before you make the series. For Asset 2D and UI: make the whole set, then present it for one approval (see [set anchor](set-anchor.md)) |
| The references conflict (different render, lighting, or proportion) and the brief gives no priority | State the specific conflict. Propose a handover to the AD (`art-style-development`), or ask the user to choose the main reference |
| A style must be set for a whole new project/IP | This is AD work. The artist only supports with a test sample when assigned |

Do not mix two conflicting styles into an "average".

## Procedure

1. **Open every reference for real.** Give each an ID (R1, R2…) and a role: Inspiration / Execution reference / Avoid. Only an Execution reference is the standard for comparing pixels/lines. An Inspiration gives mood/principles only.
2. **Measure. Do not guess.** Use `preview.py compare` for a set of references at the same height. Use `preview.py value`. Use `palette_report.py` to get the real palette. Use `score_variants.py --profile` to get the mean color of the darkest 5% of pixels, the color cast of each light band, and the value p2/p50/p98. For color criteria that are easy to describe wrongly in words (dark area color, light cast), record these measurements as a check baseline. The measurements support a specific question. They do not replace judgment about the relations between color, lighting, and the expression goal.
   Record a separate palette for each reference. If a reference has a tone that differs from the majority, mark it "structure only" when you give it to the gen tool.
3. **Fill in the axes that affect the task**, from the 12 axes of the template below. A single icon may need only a few axes. A style sheet for a whole series of assets needs more. For an axis you did not consider, write "not considered". Do not invent. For each axis you fill in: a specific observation with the image ID → a rule that can be followed → the allowed range → confidence (high when 2 or more Execution references agree).
4. **Record what to avoid, with a source.** Record it as *forbidden* only when the brief/AD says so clearly, or when every Execution reference consistently avoids it and there is a visible reason (for example, a black outline would break the colored-outline language). Record something that is only "not seen" in a few references as *not seen in references*. Use it to find odd details. It is not a prohibition.
5. **Make 1 test sample** of a new subject that is not in the references. Run `preview.py compare` with the Execution reference at the same size. Score each axis: match / deviate / not checked. Fix the style sheet or the image, up to the limit in the [quality standard](../rules/art-quality.md).

## Style sheet template

```markdown
# Style sheet <name> v<number> — status: proposed | confirmed_by:<person>
Sources: R1 (Execution), R2 (Execution), R3 (Inspiration), R4 (Avoid)

| Axis | Observation (image) | Rule | Range | Confidence |
|---|---|---|---|---|
| Render | | | | |
| Line (yes/no, thickness by size, color) | | | | |
| Shape language | | | | |
| Proportion (head–body, exaggeration) | | | | |
| Value (range, key, darkest area) | | | | |
| Palette (color families, saturation, shadow color) | | | | |
| Lighting (direction, painted-in or dynamic) | | | | |
| Material (level of simplification) | | | | |
| Edge (hard/soft, where) | | | | |
| Detail density & rest areas | | | | |
| Brush/texture marks | | | | |
| Camera/viewing angle | | | | |

Avoid (source: brief/AD/reference): ...
Not seen in references (for checking, not a rule): ...
Test sample: <file> — comparison result: ...
Open questions: ...

## Production notes (update after each task)
- Set of references given to the gen tool and their roles (style/color standard · structure only):
- Standard measurements (`--profile`): darkest 5% color, cast of each band, value p2/p50/p98:
- Fixes that worked / did not work for this style (with the task record):
```

The Production notes are where you store lessons specific to the style/project. Do not write them into skill files.

## Example of a good line and a bad line

- Good: `Line | R1, R2: dark brown outline (not black), ~3px thick on a 128px icon, thinning at pointed ends | Dark outline in the material color, 2–3% of the object's long edge | ±1px | high`
- Bad: `Line | pretty, soft | use pretty line` — no observation, cannot be followed.
