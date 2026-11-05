# Tech profile — Godot mobile (Web: extension section for later)

One file per project, confirmed by the technical lead/AD. The artist reads this file instead of guessing parameters. An empty field means unknown. Record an assumption in the task. Do not fill it into the profile yourself.

```markdown
# Tech profile <project> — Godot <version> — status: draft | confirmed_by:<person>

## Target screen
- Design viewport (px) and stretch mode/aspect:
- Lowest reference device:
- Safe area / notch:

## Asset 2D
- Standard display size of icon/sprite (px at the design viewport):
- Draw scale versus display (for example draw at 2x and let Godot scale):
- Default filter (project setting/CanvasItem: Linear/Nearest), mipmap for 2D:
- Atlas/AtlasTexture or separate files; padding between cells:
- Alpha: straight; Fix Alpha Border (on by default):
- Compression: Lossless / Lossy / VRAM Compressed by asset type:

## Texture 3D
- Shader: unlit / StandardMaterial3D / custom shader:
- Texel density or map size by asset type:
- Color space: albedo sRGB, data maps linear; normal map convention (Godot uses OpenGL Y+):
- VRAM Compressed mobile: ETC2 (default) or ASTC (high quality); mipmap (on by default when Detect 3D):
- Delivery format (PNG/glTF), map naming convention:

## Naming & folders
- Naming convention for file/state/frame:
- Delivery folder in the project / Drive:

## Web (later)
- Download size limit, image format, compression:
```

Fixed notes for Godot 4: 2D and 3D import are configured separately on each texture (`.import`). Changing the import preset is the job of the person who owns the project. The artist only proposes. Check the image in the editor/on a device when you have permission. Do not infer from the PNG file.
