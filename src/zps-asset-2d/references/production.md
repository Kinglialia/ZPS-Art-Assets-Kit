# 2D asset production for games

First, get the output type: icon, sprite, tile, decal, portrait, background or frame sequence. Canvas, pivot, safe area, target size, states and source editability are separate requirements. DPI does not replace pixel dimensions. Check a prototype in the layout/game when one exists.

Icon: check the silhouette and identifying points at small size. Keep rhythm/scale consistent in the set. Do not force every concept detail into the icon.

Sprite: keep the pivot, baseline and crop margin. Do not auto-crop each frame, because the character will jitter.

Frame sequence: check pose, volume, accessories, color and rhythm when it really runs. A still image does not prove an animation.

Background: the layers must have enough area for parallax/occlusion for the scope. Keep the camera and scale.

Tile: check the joining edges, many cells in a repeat, and prominent marks that repeat.

Atlas: it needs extrusion/padding that is correct for the importer. Transparent pixels can also cause a wrong edge when filtering.

Decal: check alpha/blend on the target material.

Pixel art: follow the project for grid, clusters, palette and filtering. Do not resample with bilinear yourself.

Keep a layered source when the real tool can create it. A flat file is only a flat file. Export with a clear resolution, alpha mode, frame order/duration, pivot and dependent resources. Check on light, dark and game backgrounds. Metadata does not prove a clean edge.

## Godot 4 — import proposals for 2D assets

Take project specifications from the tech profile. The items below are what you must propose clearly at handoff. Do not edit `.import` or project settings outside your authority. Follow the [Godot import documentation](https://github.com/godotengine/godot-docs/blob/master/tutorials/assets_pipeline/importing_images.rst): the 2D default is Lossless, no mipmap. Since Godot 4, filter/repeat are set on CanvasItem (a project setting gives the default). They are not in the import.

| Type | Proposal to record | Reason to check |
|---|---|---|
| UI icon/sprite shown near 1:1 | Lossless, mipmap off; Linear filter on CanvasItem | Keeps small icons sharp; mipmap adds ~33% memory and gives no gain when the image is not scaled down |
| Sprite strongly scaled down by the camera | Mipmap on; check at the farthest zoom level | Avoids speckle when scaled down |
| Pixel art | Lossless, no mipmap; Nearest filter; integer scale | Keeps pixel edges |
| Large background | Consider VRAM Compressed (default ETC2 on mobile, ASTC when high quality is on); check for banding | Mobile memory |
| With alpha | Straight alpha; keep Fix Alpha Border (on by default) | Reduces dark edges with bilinear filtering |
| Atlas | Padding/extrude between cells as in the tech profile | Avoids color bleeding from the next cell |

Deliver checked images and record the level: export checked / imported into Godot / viewed on a device. For web export, use a separate section later. Scaling down is a diagnostic. It does not certify gameplay readability or accessibility.
