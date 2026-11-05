"""Describe a 3D model for texture planning: size, polygon count, materials, UV sets, UV
coverage/overlap/out-of-range, vertex colors and texel density for a planned texture size.
Read-only. Run with a Python that has `bpy` or `blender -b -P inspect_model.py -- ...`.

UV metrics are estimates from a coarse raster of UV triangles (default 256x256 cells):
- uv_coverage: share of 0-1 UV space used by at least one face.
- uv_overlap: share of used cells covered by more than one face (mirroring/stacking or error).
- uv_out_of_range: share of UV triangle vertices outside 0-1 (tiling/trim/UDIM or error).
- texel_density_px_per_m: planned texture size * sqrt(UV area / surface area); compare
  between assets, not as an absolute pass/fail."""
import argparse
import json
import math
from pathlib import Path
import sys

GRID = 256  # cells per UV side; fine enough to see coverage/overlap, cheap in pure Python


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
    p.add_argument('--texture-size', type=int, default=1024, help='planned square texture size in px')
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


def tri_area(a, b, c):
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2


def raster(tri, counts, face_cells):
    """Mark grid cells whose centers fall inside a UV triangle (clamped to 0-1)."""
    xs = [min(max(p[0], 0.0), 1.0) * GRID for p in tri]
    ys = [min(max(p[1], 0.0), 1.0) * GRID for p in tri]
    (x0, y0), (x1, y1), (x2, y2) = zip(xs, ys)
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-12:
        return
    for gx in range(int(min(xs)), min(int(max(xs)) + 1, GRID)):
        for gy in range(int(min(ys)), min(int(max(ys)) + 1, GRID)):
            px, py = gx + 0.5, gy + 0.5
            l0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            l1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            if l0 >= 0 and l1 >= 0 and l0 + l1 <= 1:
                cell = gy * GRID + gx
                if cell not in face_cells:
                    face_cells.add(cell)
                    counts[cell] = counts.get(cell, 0) + 1


def inspect(bpy, meshes, texture_size):
    from mathutils import Vector
    depsgraph = bpy.context.evaluated_depsgraph_get()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    size = [round(max(p[i] for p in pts) - min(p[i] for p in pts), 4) for i in range(3)]
    tris = surface = uv_area = 0.0
    materials, uv_sets, vcol = set(), set(), False
    counts, out_of_range, uv_points = {}, 0, 0
    per_object = []
    for o in meshes:
        ev = o.evaluated_get(depsgraph)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        materials.update(m.name for m in me.materials if m)
        uv_sets.update(uv.name for uv in me.uv_layers)
        vcol = vcol or bool(getattr(me, 'color_attributes', None) and len(me.color_attributes))
        uv = me.uv_layers.active.data if me.uv_layers else None
        mw = o.matrix_world
        o_tris = len(me.loop_triangles)
        for lt in me.loop_triangles:
            v = [mw @ me.vertices[i].co for i in lt.vertices]
            surface += ((v[1] - v[0]).cross(v[2] - v[0])).length / 2
            if uv:
                t = [tuple(uv[i].uv) for i in lt.loops]
                uv_area += tri_area(*t)
                uv_points += 3
                out_of_range += sum(1 for p in t if not (0 <= p[0] <= 1 and 0 <= p[1] <= 1))
                raster(t, counts, set())
        tris += o_tris
        per_object.append({'name': o.name, 'triangles': o_tris, 'uv_sets': [u.name for u in me.uv_layers],
                           'materials': [m.name for m in me.materials if m]})
        ev.to_mesh_clear()
    used = len(counts)
    result = {
        'tool': 'art_inspect_model', 'objects': len(meshes), 'triangles': int(tris),
        'bounding_size_m': size, 'surface_area_m2': round(surface, 4),
        'materials': sorted(materials), 'uv_sets': sorted(uv_sets), 'has_vertex_colors': vcol,
        'per_object': per_object,
    }
    if uv_points:
        result.update({
            'uv_coverage': round(used / (GRID * GRID), 4),
            'uv_overlap': round(sum(1 for c in counts.values() if c > 1) / used, 4) if used else 0.0,
            'uv_out_of_range': round(out_of_range / uv_points, 4),
            'texel_density_px_per_m': round(texture_size * math.sqrt(uv_area / surface), 1) if surface else None,
            'texture_size_assumed': texture_size,
        })
    else:
        result['uv_note'] = 'no UVs: only vertex color, triplanar or procedural methods apply until UVs exist'
    result['scope'] = 'Geometry/UV facts for planning. Not a quality verdict; open render_model.py renders too.'
    return result


def main(argv):
    a = parse(argv)
    import bpy
    with quiet_stdout():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        report = inspect(bpy, import_model(bpy, a.model.resolve()), a.texture_size)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except (ImportError, OSError, ValueError, RuntimeError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Requires bpy (Blender as a Python module) or blender -b -P.'}))
        sys.exit(2)
