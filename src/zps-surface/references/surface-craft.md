# Designing beautiful textures with character

This part is shared by all methods. The authoring way (hand painting, flat color, procedural, photo, and so on) and the shader (unlit, lit/toon, PBR) are two independent choices. The style sheet or the Bible of the project decides both.

## Material intent before maps

For each area, record:
- Material or making method.
- Scale.
- Structure direction.
- Way of use.
- Level of stylization.
- Role in the hierarchy.

"Wood" is not enough. Soft painted wood, rough hewn wood and polished wood give different forms and reactions. The characteristic must read at the real area and pixels, not only in an enlarged crop.

Build character from the relationships between the material and the world: how it is carved, joined, patched, woven. Use motifs with logic and a few chosen standout traits. Use references to understand principles. Do not copy a symbol or a recognizable detail. "Unique" is a judgment relative to the sources you have seen. It does not certify that nothing like it exists.

## Surface layout

Design large, medium and small blocks on purpose: rest areas, structure areas, accents. Do not apply a fixed percentage. Follow the faces of the form and the game camera. A UV seam is not a natural layout line. Stroke and grain direction follow the material structure, not the atlas edges.

Color, brightness, gloss and grain scale together create the feeling of a material. Separate materials with a relationship that is enough. Do not require every area to have very strong contrast. Watch for nearby colors and lighting that make you read the map color wrongly.

Each wear mark needs a cause: handling, friction, impact, standing water, sun, dust. A mark has a reasonable distribution and direction. Do not cover edges with even light lines or noise. Stylized work can exaggerate the cause, but must keep the language of the game. An area that does not need wear can stay clean.

## Economical testing

Choose an area that holds important interactions: wood–metal, cloth edge–leather, a face that changes direction, and seams. Make the base blocks and the main rhythm, then apply them to the model at once. If a stroke does not read because the UV is small, find the cause before you raise the resolution. Use a sample that is still valid instead of testing from the start again.

Compare the old and new versions with the same camera, light and exposure. Look at the model rotating and at the target size. A "beautiful" stroke on the atlas can face the wrong way, become noise, or lose its shape on the model. Separate the aesthetic result from technical map validity. Add polish only where it solves a real problem. Do not assume that more detail adds value.
