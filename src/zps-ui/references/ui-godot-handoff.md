# UI handoff for Godot

Reference point: Godot 4.5 / 4.5-stable documentation. This is **not a version requirement**. Look up the project's real version before you specify a setting.

## Contents
- Display context
- Layout and safe area
- Component, Theme, 9-slice
- Text and localization
- Asset and import
- Build comparison

## Display context

Record:
- Godot version.
- Orientation.
- Base size.
- Stretch mode/aspect/scale.
- Supported aspect-ratio range ([Multiple resolutions](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/rendering/multiple_resolutions.rst)).

Keep three things apart: design units, Godot layout units and size on the device. A button that is big enough in the image does not prove the touch area after scaling. Do not change project settings to match a screenshot.

## Layout and safe area

| Item | Spec |
|---|---|
| Screen | ID, reference size, aspect-ratio range, sample content |
| Layout | Fixed/stretching parts, suggested anchors or Container, minimum size, padding, alignment |
| Responsive | When to wrap, scroll, change the column count, crop; priority order for keeping content |
| Safe area | Parts inside the safe area; parts allowed to extend outside it |
| UI layers | Layer that receives input, Back/close, modal — as in the approved UX spec |

A Container arranges child Controls ([Containers](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/ui/gui_containers.rst)). For parts outside a Container, use [anchors](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/ui/size_and_anchors.rst). Do not write manual coordinates that conflict with them. [`DisplayServer.get_display_safe_area()`](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/DisplayServer.xml) differs by platform. A desktop preview proves only a simulation. The developer confirms on a device.

## Component, Theme, 9-slice

Record the ID, variant/state, suggested Control, and the mapping to the project's colors, fonts, constants and StyleBox. Do not force a node choice when an equivalent way exists.

For 9-slice, record these separately:
- The **four texture margins** (the parts that keep their shape).
- The **four content margins** (the space for content).
- How each axis stretches or tiles.
- The min/max sizes you tested.

Content margin can fall back to texture margin ([StyleBoxTexture](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/StyleBoxTexture.xml)). If they differ, say so.

## Text and localization

Record:
- Font/fallback.
- Size.
- Line height.
- Color.
- Outline/shadow.
- Wrap/truncate.
- Number of lines.
- Overflow.

Check with the real languages:
- Long strings.
- Vietnamese text with diacritics (diacritic clipping, fallback).
- Large numbers.
- Placeholders that change position.
- RTL, only when a related language exists.

Pseudolocalization finds length faults but does not replace a check of real glyphs ([Internationalizing games](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/i18n/internationalizing_games.rst)).

## Asset and import

By default, deliver **PNG** at the project's base size (add `@2x` if the project needs it). Export it from SVG with `svg_render.py`. Include the **source SVG** so it can be edited in Figma or exported again. The reviewer checks these PNG files.

Deliver SVG for direct import only when the developer or project asks for it (for example, an icon that needs many scale levels). In that case:
- Record the proposed import scale.
- Record the risk. Godot draws SVG with ThorVG. Gradient and stroke weight may differ slightly from the PNG that was reviewed.
- Calculate 9-slice margins on the size after scaling.

Record the file, ID, source, export/use size, alpha, purpose and proposed filter/scale. SVG is rasterized at import, so text in an SVG must become paths ([Importing images](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/assets_pipeline/importing_images.rst)). Keep an editable text source. In Godot 4, filter/repeat are set on CanvasItem, not in the import. Mipmap, compression and atlas are proposals. The Developer decides according to the budget.

## Build comparison

Record the design version and the build, the viewport, the state and the content. For each deviation, record: position, expectation, actual result, impact, direction of fix. Separate a missing design spec from a build fault. Do not claim input, safe area or performance results before you test them in the matching environment.
