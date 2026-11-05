"""Cleanup: make the reference mesh every later step compares against (optimize.md §3).

Usage:
  $BLENDER -b --python tools/optimize/cleanup.py -- --work <w> --spec task/spec.json
  python3 tools/optimize/cleanup.py --work <w> [--spec task/spec.json] [--input <w>/oriented.glb]
         [--audit <w>/audit.json] [--branch clean|dirty] [--out <w>/cleanup.json]

Input: <w>/oriented.glb when gate1 wrote it, else <w>/ingest.glb. Branch and uv_plan come from
audit.json (--branch overrides the branch).

Always, in this order:
  1. merge by distance (cleanup.merge_distance_ratio x bbox diagonal), dissolve degenerate faces
  2. delete loose shells with fewer faces than cleanup.loose_part_min_ratio x total faces
  3. fill holes with <= cleanup.max_hole_edges edges (only holes present in the input: done
     before step 4 so openings left by removed hidden faces are not capped again)
  4. clean branch only, when 0 < interior ratio <= cleanup.interior_face_max_ratio: delete faces
     never hit by rays from audit.ray_directions directions (same test as audit.py)
  5. recalculate normals outward, triangulate, origin bottom-centre
Dirty branch (or cleanup.voxel_remesh.mode = always):
  6. keep the result of 1-5 with its materials and UVs as <w>/pre_remesh.glb (the bake source)
  7. solidify open sheets by 2 voxels if voxel_remesh.solidify_thin; a shell is an open sheet
     when boundary edges are >= voxel_remesh.open_boundary_min_ratio of its edges (a few stray
     boundary edges on a closed shell, such as fins, do not count)
  8. Remesh modifier VOXEL, voxel_size = longest bbox edge / voxel_remesh.resolution,
     smooth shading; triangulate; drop loose shells again; one neutral material
Writes <w>/ref_high.glb, the only reference for every later comparison, and data.remeshed,
data.rebake (remeshed, or audit uv_plan = rebake), data.bake_source.

Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import numpy as np  # noqa: E402

import optlib  # noqa: E402
import optbpy  # noqa: E402
from optlib import common  # noqa: E402
import bmesh  # noqa: E402  (after bpy, which optbpy imported)
import bpy  # noqa: E402

TOOL = "optimize/cleanup"


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--work", required=True)
    p.add_argument("--spec")
    p.add_argument("--input")
    p.add_argument("--audit")
    p.add_argument("--branch", choices=["clean", "dirty"])
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    if not a.input:
        oriented = os.path.join(a.work, "oriented.glb")
        a.input = oriented if os.path.isfile(oriented) else os.path.join(a.work, "ingest.glb")
    a.audit = a.audit or os.path.join(a.work, "audit.json")
    a.out = a.out or os.path.join(a.work, "cleanup.json")
    return a


def bm_of(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    return bm


def bm_store(bm, obj):
    bm.to_mesh(obj.data)
    obj.data.update()


def delete_faces(obj, mask):
    """Delete faces where mask is True; drop verts and edges no face uses any more."""
    idx = np.nonzero(mask)[0]
    if idx.size == 0:
        return 0
    bm = bm_of(obj)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in idx], context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bm_store(bm, obj)
    bm.free()
    return int(idx.size)


def drop_small_shells(obj, ratio):
    v, f = optbpy.mesh_arrays(obj)
    _, _, diag = optbpy.bbox(v)
    shells, face_lab = optbpy.shells(v, f, diag)
    small = {s["label"] for s in shells if s["faces"] < ratio * len(f)}
    removed = delete_faces(obj, np.isin(face_lab, list(small))) if small else 0
    return len(small), removed, len(shells)


def topology(obj):
    v, f = optbpy.mesh_arrays(obj)
    _, _, diag = optbpy.bbox(v)
    vmap, _ = optbpy.weld_map(v, 1e-7 * diag)
    es = optbpy.edge_stats(vmap[f])
    return len(f), es


def main(a):
    cfg, spec = optlib.settings(a.spec)
    ccfg, acfg = cfg["cleanup"], cfg["audit"]
    vcfg = ccfg["voxel_remesh"]
    audit = common.read_json(a.audit)
    if audit.get("overall") not in ("pass", "info"):
        raise ValueError(f"audit overall is {audit.get('overall')}; fix the input first ({a.audit})")
    branch = a.branch or audit["data"]["branch"]
    if vcfg["mode"] == "always":
        branch = "dirty"
    elif vcfg["mode"] == "never":
        branch = "clean"
    uv_plan = audit["data"]["uv_plan"]
    warnings, steps = [], {}

    optbpy.reset_scene()
    optbpy.import_model(a.input)
    obj = optbpy.join_world(optlib.output_object(a.work))   # keeps the asset name audit gave it
    optbpy.triangulate(obj)
    v, f = optbpy.mesh_arrays(obj)
    _, _, diag = optbpy.bbox(v)
    tris_in = len(f)

    # 1. weld + degenerate
    dist = ccfg["merge_distance_ratio"] * diag
    bm = bm_of(obj)
    n0 = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    steps["welded_verts"] = n0 - len(bm.verts)
    f0 = len(bm.faces)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges)
    steps["degenerate_dissolved"] = f0 - len(bm.faces)
    bm_store(bm, obj)
    bm.free()
    optbpy.triangulate(obj)

    # 2. loose shells
    n_small, removed, n_shells = drop_small_shells(obj, ccfg["loose_part_min_ratio"])
    steps.update({"shells_before": n_shells, "loose_shells_deleted": n_small, "loose_faces_deleted": removed})

    # 3. holes present in the input
    bm = bm_of(obj)
    boundary = [e for e in bm.edges if e.is_boundary]
    filled = bmesh.ops.holes_fill(bm, edges=boundary, sides=ccfg["max_hole_edges"])["faces"]
    steps["holes_filled"] = len(filled)
    if filled:
        bmesh.ops.triangulate(bm, faces=filled)
    bm_store(bm, obj)
    bm.free()

    # 4. interior faces (clean branch only)
    steps["interior_faces_deleted"] = 0
    if branch == "clean":
        v, f = optbpy.mesh_arrays(obj)
        vis = optbpy.visibility(v, f, acfg["ray_directions"], acfg["samples_per_face"], acfg["max_faces_for_rays"])
        ratio = float(vis["interior"][vis["tested"]].mean())
        steps["interior_ratio"] = common.r(ratio)
        if 0 < ratio <= ccfg["interior_face_max_ratio"]:
            steps["interior_faces_deleted"] = delete_faces(obj, vis["interior"])
        elif ratio > ccfg["interior_face_max_ratio"]:
            warnings.append(f"clean branch but interior ratio {ratio:.1%} > {ccfg['interior_face_max_ratio']:.0%}; "
                            "interior faces kept (forced clean branch?)")

    # 5. normals, triangulate, origin
    bm = bm_of(obj)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm_store(bm, obj)
    bm.free()
    optbpy.triangulate(obj)
    v, f = optbpy.mesh_arrays(obj)
    offset = optbpy.bottom_center_offset(v)
    optbpy.transform_mesh(obj, offset=offset)
    steps["origin_offset_m"] = [common.r(x, 6) for x in offset]

    remeshed = branch == "dirty"
    pre_remesh = None
    voxel_size = None
    if remeshed:
        pre_remesh = os.path.join(a.work, "pre_remesh.glb")
        optbpy.export_glb(pre_remesh, [obj])
        v, f = optbpy.mesh_arrays(obj)
        lo, hi, _ = optbpy.bbox(v)
        voxel_size = float((hi - lo).max() / vcfg["resolution"])
        # 7. open sheets get thickness so the voxeliser sees a volume
        if vcfg["solidify_thin"]:
            shells, face_lab = optbpy.shells(v, f, float(np.linalg.norm(hi - lo)))
            bm = bm_of(obj)
            bm.faces.ensure_lookup_table()
            n_lab = int(face_lab.max()) + 1
            edges_per, boundary_per = np.zeros(n_lab), np.zeros(n_lab)
            for e in bm.edges:
                if e.link_faces:
                    lab = int(face_lab[e.link_faces[0].index])
                    edges_per[lab] += 1
                    boundary_per[lab] += e.is_boundary
            share = boundary_per / np.maximum(edges_per, 1)
            open_labels = set(np.nonzero(share >= vcfg["open_boundary_min_ratio"])[0].tolist())
            geom = [bm.faces[i] for i in np.nonzero(np.isin(face_lab, list(open_labels)))[0]]
            if geom:
                bmesh.ops.solidify(bm, geom=geom, thickness=2 * voxel_size)
            steps["open_shells_solidified"] = len(open_labels)
            bm_store(bm, obj)
            bm.free()
        # 8. voxel remesh
        mod = obj.modifiers.new("voxel", "REMESH")
        mod.mode = "VOXEL"
        mod.voxel_size = voxel_size
        mod.adaptivity = 0.0
        mod.use_smooth_shade = True
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), depsgraph=dg)
        obj.modifiers.remove(mod)
        old = obj.data
        obj.data = me
        bpy.data.meshes.remove(old)
        me.name = obj.name
        optbpy.triangulate(obj)
        n_small, removed, _ = drop_small_shells(obj, ccfg["loose_part_min_ratio"])
        steps.update({"post_remesh_shells_deleted": n_small, "voxel_size_m": common.r(voxel_size, 6)})
        obj.data.materials.clear()
        mat = bpy.data.materials.new("ref_high")
        obj.data.materials.append(mat)
        me = obj.data
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
        me.update()

    ref_high = os.path.join(a.work, "ref_high.glb")
    optbpy.export_glb(ref_high, [obj])
    tris_out, es = topology(obj)
    rebake = remeshed or uv_plan == "rebake"
    bake_source = pre_remesh if remeshed else ref_high
    if rebake and not remeshed:
        warnings.append("UVs unusable on a clean mesh: geometry kept, texture will be rebaked from ref_high.glb")

    checks = [
        common.check("ref_high.nonmanifold_edges", "pass" if es["nonmanifold"] == 0 else "fail",
                     es["nonmanifold"], 0),
        common.check("ref_high.boundary_edges", "pass" if es["boundary"] == 0 else "info", es["boundary"], 0,
                     note=None if es["boundary"] == 0 else "open boundary left (holes above max_hole_edges)"),
        common.check("ref_high.winding_inconsistent_edges", "pass" if es["winding_inconsistent"] == 0 else "fail",
                     es["winding_inconsistent"], 0),
    ]
    metrics = {"tris_in": tris_in, "tris_out": tris_out, "branch": branch, "remeshed": remeshed,
               "rebake": rebake, **steps}
    artifacts = {"ref_high": ref_high}
    if pre_remesh:
        artifacts["pre_remesh"] = pre_remesh
    data = {"branch": branch, "remeshed": remeshed, "rebake": rebake, "uv_plan": "rebake" if rebake else "keep_uv",
            "ref_high": ref_high, "pre_remesh": pre_remesh, "bake_source": bake_source,
            "voxel_size_m": voxel_size, "input": os.path.abspath(a.input), "edges": es}
    common.write_result(a.out, TOOL, checks, metrics, warnings, artifacts, data,
                        source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
