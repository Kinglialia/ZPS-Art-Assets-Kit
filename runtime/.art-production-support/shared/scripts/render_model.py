"""Render a model from several angles in Blender (headless, Cycles CPU) to inspect UV, form and
texture on the model. Modes: clay (form only), checker (UV distortion/density), textured (as
imported, or with --texture applied as base color). Run with a Python that has the `bpy` module
(pip install bpy matching its Python) or `blender -b -P render_model.py -- ...`.
Blender output is DCC evidence, not a Godot runtime check."""
import argparse
import json
import math
from pathlib import Path
import sys

# 16 samples + denoise-free Cycles is enough to read form/UV; not for judging final shading.
SAMPLES = 16


class quiet_stdout:
    """Send Blender's import/render logs to stderr so stdout carries only the JSON report."""
    def __enter__(self):
        import os
        sys.stdout.flush()
        self.saved = os.dup(1)
        os.dup2(2, 1)
        return self

    def __exit__(self, *exc):
        import os
        sys.stdout.flush()
        os.dup2(self.saved, 1)
        os.close(self.saved)
        return False


def parse(argv):
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', type=Path, help='.glb/.gltf/.obj/.fbx')
    p.add_argument('--mode', choices=['clay', 'checker', 'textured'], default='textured')
    p.add_argument('--texture', type=Path, help='apply as base color to every material (textured mode)')
    p.add_argument('--views', type=int, default=4, help='turntable views around the vertical axis')
    p.add_argument('--elevation', type=float, default=20.0, help='camera elevation in degrees')
    p.add_argument('--size', type=int, default=768)
    p.add_argument('--out-dir', type=Path, required=True, help='must not exist; created')
    return p.parse_args(argv)


def import_model(bpy, path):
    ext = path.suffix.lower()
    if ext in ('.glb', '.gltf'):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError(f'unsupported model format {ext}')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise ValueError('no mesh objects imported')
    return meshes


def bounds(meshes):
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, (hi - lo).length / 2


def make_material(bpy, name, image=None, color=(0.6, 0.6, 0.6, 1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = 0.8
    if image is None:
        bsdf.inputs['Base Color'].default_value = color
    else:
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = image
        mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def assign(meshes, mat):
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(mat)


def setup_scene(bpy, size):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = False
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.film_transparent = False
    world = scene.world or bpy.data.worlds.new('World')
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.5, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    sun = bpy.data.objects.new('KeySun', bpy.data.lights.new('KeySun', 'SUN'))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    return scene, cam


def main(argv):
    a = parse(argv)
    import bpy
    from mathutils import Vector
    if a.out_dir.exists():
        raise ValueError(f'{a.out_dir} exists; choose a new versioned folder')
    if a.texture and a.mode != 'textured':
        raise ValueError('--texture only applies to textured mode')
    with quiet_stdout():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        meshes = import_model(bpy, a.model.resolve())
    if a.mode == 'clay':
        assign(meshes, make_material(bpy, 'Clay'))
    elif a.mode == 'checker':
        img = bpy.data.images.new('Checker', 1024, 1024)
        img.generated_type = 'UV_GRID'
        assign(meshes, make_material(bpy, 'Checker', img))
    elif a.texture:
        assign(meshes, make_material(bpy, 'Texture', bpy.data.images.load(str(a.texture.resolve()))))
    missing_uv = [o.name for o in meshes if not o.data.uv_layers]
    scene, cam = setup_scene(bpy, a.size)
    center, radius = bounds(meshes)
    cam.data.lens = 50
    distance = radius / math.tan(cam.data.angle / 2) * 1.15
    a.out_dir.mkdir(parents=True)
    renders = []
    for i in range(a.views):
        az = 2 * math.pi * i / a.views
        el = math.radians(a.elevation)
        offset = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * distance
        cam.location = center + offset
        cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
        out = a.out_dir / f'{a.mode}_view{i:02d}.png'
        scene.render.filepath = str(out)
        with quiet_stdout():
            bpy.ops.render.render(write_still=True)
        renders.append(str(out.resolve()))
    print(json.dumps({'tool': 'art_render_model', 'blender': bpy.app.version_string, 'model': str(a.model.resolve()),
                      'mode': a.mode, 'renders': renders, 'meshes_without_uv': missing_uv,
                      'scope': 'Blender Cycles CPU, neutral light. Not Godot shading, import or compression.',
                      'next': 'Open every render; combine with preview.py compare if needed.'}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except (ImportError, OSError, ValueError, RuntimeError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Requires bpy (Blender as a Python module) or blender -b -P.'}))
        sys.exit(2)
