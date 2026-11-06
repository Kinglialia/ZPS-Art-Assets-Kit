# 3D ↔ Texture handoff

A shared template for the 3D Artist and the Texture Artist. The 3D Artist fills in part A when calling the Texture Artist. The Texture Artist fills in part B when returning the result. For a small task, write only the relevant lines, in an existing record.

## A. 3D → Texture (request)

```markdown
# Texture for <asset> — model v<number>, UV v<number>
- Model file: <GLB/FBX path>
- Reason for the call: new model | after retopo, old texture does not pass (state the reason) | other: …
- Texture method: <as requested by …> | nobody requested (Texture chooses)
- UV: UV0 yes/no; intentional overlap/mirror/stack at: <area> | none; within 0–1 | tile
- Texture method known at unwrap time: <method, source> | unknown (separate UV, no overlap)
- Material areas: <part → material, for example body → wood, band → metal> (from the `material` field in part_graph.json when self-built); `parts_<view>.png` image: <path>
- Material: one material (default) | slots split as requested by Texture Planning: <slot → area>
- UV check: uv_check result <JSON path>; checker image <path>
- Camera and on-screen size: <from the spec>
- Baked maps (normal/AO…) and convention: <yes/no, path>
- Temporary texture from the 3D pipeline (concept projection/bake): <yes/no, path> — temporary; Texture decides to keep/fix/redo
- Concept/view used; hidden parts are inferred: <area>
- Engine: <Godot/…>
```

## B. Texture → 3D (result)

```markdown
# Texture <asset> — for model v<number>, UV v<number>
- Method used: <author × shader> — <as requested by … | self-chosen because …>
- Texture Review: <verdict, self/independent, open issues> | not run (test sample or small fix)
- Maps/atlas delivered: <file, size, channels, color space>
- Attached to material slot: <slot → map>
- Material setup notes for the person who imports the asset into the engine: lit | unlit; compression; mipmap on/off; which image is the normal map (OpenGL/DirectX convention)
- On-model render opened: <path, renderer>
- Request to 3D to fix the UV or split material slots (if any, combine into one request): <…>
- Parts not checked / remaining defects:
```

## Usage rules

- The default is one material and a separate UV with no overlap. Material area information travels in the "part → material" table and the parts image. It does not need a separate material slot. Split slots only when Texture Planning requires different shaders per area.
- If the Texture Artist needs a different UV or a separate slot, combine all requests into one message to the 3D Artist.

- The Texture Artist measures by itself what `inspect_model.py` can measure (UV, material, vertex color, texel density). Do not ask about those items again.
- Ask only about what cannot be measured: the intent of overlapping UV, which area is which material, and the camera. If many items are missing, combine them into **one question**.
- If the model or UV changes version after you send, send part A again. Check again any texture made for the old version.
