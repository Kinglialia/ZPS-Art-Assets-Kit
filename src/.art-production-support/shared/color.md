# Color: measure, choose and fix

Read this file when a decision depends on color: a palette, a color match against a reference, a ramp or gradient, a mood choice, or a UI contrast check. Some ideas come from meodai's [color-expert skill](https://github.com/meodai/skill.color-expert) (CC BY 4.0); the text here is our own.

## Measure. Do not name colors by eye.

- Vision models misread near-greys and small lightness steps. Treat what you see as a hypothesis. Then measure.
- Sample the region with code, read its OKLCH value (lightness L, chroma C, hue h), and only then name or compare it. Use `palette_report.py` (`vivid` for the painted color, `mean` for the blended color, `accents` for small strong colors).
- Compare colors by ΔE OK (OKLab distance × 100). About 2 is just visible. About 8 is clearly a different color side by side.
- State the measured numbers in the review. "Too saturated" means a chroma value and the target value.

## Choose colors by character, not by hue angle

- Lightness and chroma set the mood more than the hue intervals of a color wheel. Two palettes with the same hues and different chroma feel different. Two palettes with different hues and the same L/C structure can feel related.
- A complement is the OKLCH hue + 180° of the real color, not the complement of its name.
- Give the palette a share plan, for example 60% dominant, 30% secondary, 10% accent. The accent is the color that the player must see first.
- In a story or a game world, a color means what it is repeatedly attached to, and how that link changes. A table of color symbolism does not define it.

## Ramps and gradients

- The steps of a ramp (UI scale, value ramp of a material, gradient stops) must look even. Run `palette_report.py --ramp <stops>`. Each step must have a similar ΔE OK, and lightness must change in one direction.
- A bump in the steps makes one transition jump. Fix the stop, not the neighbours.

## Fix colors without a hue shift

- When a color is out of gamut or too strong, reduce its chroma and keep L and h. Do not clip R, G or B: clipping shifts the hue (a saturated blue turns purple, an orange turns yellow).
- Downscale, blend alpha, blur and dither in linear light, with premultiplied alpha. In gamma space, thin bright strokes turn dark and transparent edges get a dark halo. `preview.py` already resizes in linear light.

## UI contrast: the border trick

- Two adjacent fills (two tabs, two buttons, a bar and its track) do not need 3:1 contrast between each other. Give them a shared border or gap, and give each fill 3:1 against that border.
- Text contrast rules stay as they are in [UI accessibility](../../zps-ui/references/ui-accessibility.md).
