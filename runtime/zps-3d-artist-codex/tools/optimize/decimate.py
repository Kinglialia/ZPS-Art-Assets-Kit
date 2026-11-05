"""Blender Decimate fallback for sweep.py (optimize.md §4).

Usage:
  $BLENDER -b --python tools/optimize/decimate.py -- --input <w>/ref_high.glb --output level.glb --ratio 0.1
  python3 tools/optimize/decimate.py --input <w>/ref_high.glb --output level.glb
         (--ratio R | --target-tris N) [--spec task/spec.json] [--out level.json]

Imports with merge_vertices, then welds by distance (cleanup.merge_distance_ratio x diagonal)
before simplifying, as gltfpack does. Decimate COLLAPSE with ratio = target / welded tris,
triangulated, exported as GLB. UVs and materials are carried by the modifier.

Exit 0 on success; 1 on error (error JSON written first).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import optlib  # noqa: E402
import optbpy  # noqa: E402
from optlib import common  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402

TOOL = "optimize/decimate"


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--ratio", type=float)
    p.add_argument("--target-tris", type=int)
    p.add_argument("--spec")
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    if (a.ratio is None) == (a.target_tris is None):
        p.error("give exactly one of --ratio, --target-tris")
    a.out = a.out or os.path.splitext(a.output)[0] + ".decimate.json"
    return a


def main(a):
    cfg, _ = optlib.settings(a.spec)
    optbpy.reset_scene()
    optbpy.import_model(a.input, merge_vertices=True)
    obj = optbpy.join_world()   # keeps the input's object name (the asset)
    optbpy.triangulate(obj)
    v, f = optbpy.mesh_arrays(obj)
    tris_in = len(f)
    _, _, diag = optbpy.bbox(v)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=cfg["cleanup"]["merge_distance_ratio"] * diag)
    bm.to_mesh(obj.data)
    bm.free()
    welded = len(obj.data.polygons)
    target = a.target_tris if a.target_tris else a.ratio * tris_in
    ratio = min(1.0, max(target / max(welded, 1), 1e-5))
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), depsgraph=dg)
    obj.modifiers.remove(mod)
    old = obj.data
    obj.data = me
    bpy.data.meshes.remove(old)
    me.name = obj.name
    optbpy.triangulate(obj)
    optbpy.export_glb(a.output, [obj])
    tris = optlib.glb_tri_count(a.output)
    common.write_result(a.out, TOOL, [common.check("decimate", "pass", tris)],
                        {"tris_in": tris_in, "tris_welded": welded, "target_tris": int(round(target)),
                         "modifier_ratio": common.r(ratio, 6), "tris": tris},
                        artifacts={"output": a.output}, source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
