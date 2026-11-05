"""Audit an input model and write <work>/ingest.glb (optimize.md §1).

Usage:
  $BLENDER -b --python tools/optimize/audit.py -- --input input/model.glb --work <w> --spec task/spec.json
  python3 tools/optimize/audit.py --input input/model.glb --work <w> [--spec task/spec.json]
         [--unit auto|m|cm|mm] [--out <w>/audit.json]

Steps: import (GLB/glTF/FBX/OBJ/PLY/STL), reject armature / shape keys / animation
(`out_of_scope_rig` -> overall fail, no ingest), join all meshes with world transforms applied
into one object named spec.asset (else the input file stem; data.output_object, original names
in data.joined_objects; cleanup, sweep, decimate and bake keep that name),
triangulate, convert to metres (glTF/FBX importers already do; OBJ/PLY/STL take --unit),
scale to spec height_m when given (factor recorded), origin bottom-centre, export ingest.glb.

Reports (on ingest geometry): tris, verts, bbox, diag, weld_ratio, manifold / boundary /
non-manifold edges, winding-inconsistent edges, shells (count, face share, bbox share),
interior-face ratio (faces never hit by rays from audit.ray_directions exterior directions),
degenerate faces, flipped-normal estimate, UV score, materials, textures.

Branch: dirty when interior ratio > cleanup.interior_face_max_ratio, non-manifold edge ratio >
audit.nonmanifold_edge_max_ratio, or significant shells > audit.max_significant_shells, or
cleanup.voxel_remesh.mode == always (mode never forces clean). uv_plan: keep_uv when the branch
is clean and UVs are usable (present, inside 0-1 >= audit.uv_inside_min, overlap <=
audit.uv_overlap_max unless validate.allow_uv_overlap, islands per 1k faces <=
audit.uv_islands_per_1k_faces_max; that last rule only from audit.uv_islands_rule_min_faces tris
up, since it exists to catch dense seam-heavy meshes that stall simplification), else rebake.

Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import numpy as np  # noqa: E402

import optlib  # noqa: E402
import optbpy  # noqa: E402
from optlib import common  # noqa: E402

TOOL = "optimize/audit"
UNIT_SCALE = {"m": 1.0, "cm": 0.01, "mm": 0.001}


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--work", required=True)
    p.add_argument("--spec")
    p.add_argument("--unit", default="auto", choices=["auto", "m", "cm", "mm"],
                   help="source unit for OBJ/PLY/STL (no unit in the format); auto = m")
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    a.out = a.out or os.path.join(a.work, "audit.json")
    return a


def main(a):
    cfg, spec = optlib.settings(a.spec)
    acfg, ccfg = cfg["audit"], cfg["cleanup"]
    warnings = []
    optbpy.reset_scene()
    optbpy.import_model(a.input)

    rig = optbpy.rig_findings()
    if rig:
        common.write_result(
            a.out, TOOL, overall="fail", source=a.input, spec_path=a.spec,
            checks=[common.check("out_of_scope_rig", "fail", value=rig,
                                 note="Rigged, skinned, morphing or animated input is out of scope "
                                      "(static props only). Stop and tell the user.")],
            data={"out_of_scope_rig": True, "findings": rig})
        return

    joined_objects = optbpy.mesh_object_names()
    output_object = optlib.asset_name(spec, a.input)
    obj = optbpy.join_world(output_object)
    optbpy.triangulate(obj)
    if len(joined_objects) > 1:
        warnings.append(f"{len(joined_objects)} mesh objects {joined_objects} joined into one object "
                        f"'{output_object}'; per-object spec keys cannot be checked after optimize")

    ext = os.path.splitext(a.input)[1].lower()
    unit = a.unit
    if ext in (".glb", ".gltf", ".fbx"):
        if unit not in ("auto", "m"):
            warnings.append(f"--unit {unit} ignored: {ext} carries its own unit (importer converts to metres)")
        unit = "m"
    elif unit == "auto":
        unit = "m"
        warnings.append(f"{ext} has no unit; assumed metres (pass --unit cm|mm if wrong)")
    unit_factor = UNIT_SCALE[unit]
    if unit_factor != 1.0:
        optbpy.transform_mesh(obj, scale=unit_factor)

    v, f = optbpy.mesh_arrays(obj)
    lo, hi, _ = optbpy.bbox(v)
    src_height = float(hi[2] - lo[2])
    target_h = optlib.spec_height(spec)
    height_factor = 1.0
    if target_h:
        if src_height <= 0:
            raise ValueError("model has zero height; cannot scale to height_m")
        height_factor = target_h / src_height
        optbpy.transform_mesh(obj, scale=height_factor)
    elif not (0.01 <= src_height <= 100):
        warnings.append(f"height {src_height:.4g} m looks wrong for a prop and no spec height_m was given")
    v, f = optbpy.mesh_arrays(obj)
    optbpy.transform_mesh(obj, offset=optbpy.bottom_center_offset(v))
    ingest = os.path.join(a.work, "ingest.glb")
    optbpy.export_glb(ingest, [obj])

    # ---------------------------------------------------------------- measurements
    v, f = optbpy.mesh_arrays(obj)
    lo, hi, diag = optbpy.bbox(v)
    weld_dist = ccfg["merge_distance_ratio"] * diag
    vmap, n_welded = optbpy.weld_map(v, weld_dist)
    fw = vmap[f]
    nondeg = (fw[:, 0] != fw[:, 1]) & (fw[:, 1] != fw[:, 2]) & (fw[:, 2] != fw[:, 0])
    vw = np.zeros((n_welded, 3))
    vw[vmap] = v
    es = optbpy.edge_stats(fw[nondeg])
    shells, _ = optbpy.shells(vw, fw[nondeg], diag)
    min_faces = ccfg["loose_part_min_ratio"] * len(f)
    significant = [s for s in shells if s["faces"] >= min_faces]
    area, _ = optbpy.face_areas_normals(v, f)
    degenerate = int(((area <= 1e-12 * diag * diag) | ~nondeg).sum())

    t0 = time.time()
    vis = optbpy.visibility(v, f, acfg["ray_directions"], acfg["samples_per_face"],
                            acfg["max_faces_for_rays"])
    tested = vis["tested"]
    interior_ratio = float(vis["interior"][tested].mean())
    interior_area_ratio = float(area[tested][vis["interior"][tested]].sum() / max(area[tested].sum(), 1e-30))
    visible = tested[~vis["interior"][tested]]
    flipped_ratio = float(vis["flipped"][visible].mean()) if visible.size else 0.0
    ray_seconds = time.time() - t0
    if tested.size < len(f):
        warnings.append(f"interior-face ratio estimated on {tested.size} of {len(f)} faces")

    uv = optbpy.uv_stats(obj, fw)
    mats, tex = optbpy.materials_and_textures(obj)

    # ---------------------------------------------------------------- branch decision
    edges = max(es["edges"], 1)
    nonmanifold_ratio = es["nonmanifold"] / edges
    dirty = []
    if interior_ratio > ccfg["interior_face_max_ratio"]:
        dirty.append(f"interior faces {interior_ratio:.1%} > cleanup.interior_face_max_ratio "
                     f"{ccfg['interior_face_max_ratio']:.1%}")
    if nonmanifold_ratio > acfg["nonmanifold_edge_max_ratio"]:
        dirty.append(f"non-manifold edges {es['nonmanifold']} ({nonmanifold_ratio:.2%}) > "
                     f"audit.nonmanifold_edge_max_ratio {acfg['nonmanifold_edge_max_ratio']:.2%}")
    if len(significant) > acfg["max_significant_shells"]:
        dirty.append(f"{len(significant)} significant shells > audit.max_significant_shells "
                     f"{acfg['max_significant_shells']}")
    mode = ccfg["voxel_remesh"]["mode"]
    clean_reasons = []
    if mode == "always":
        dirty.append("cleanup.voxel_remesh.mode = always")
        branch = "dirty"
    elif mode == "never":
        branch = "clean"
        if dirty:
            warnings.append("geometry looks dirty but voxel_remesh.mode = never: " + "; ".join(dirty))
        clean_reasons.append("cleanup.voxel_remesh.mode = never")
    else:
        branch = "dirty" if dirty else "clean"
    if branch == "clean" and not clean_reasons:
        clean_reasons.append(
            f"interior {interior_ratio:.1%} <= {ccfg['interior_face_max_ratio']:.1%}, "
            f"non-manifold edges {es['nonmanifold']}, {len(significant)} significant shells")

    uv_problems, uv_notes = [], []
    if not uv["present"]:
        uv_problems.append("no UV layer")
    else:
        if uv["inside_01_share"] < acfg["uv_inside_min"]:
            uv_problems.append(f"UV area inside 0-1 {uv['inside_01_share']:.1%} < {acfg['uv_inside_min']:.0%}")
        if not cfg["validate"].get("allow_uv_overlap", False) and uv["overlap_ratio"] > acfg["uv_overlap_max"]:
            uv_problems.append(f"UV overlap {uv['overlap_ratio']:.1%} > {acfg['uv_overlap_max']:.0%}")
        island_rule_min = acfg["uv_islands_rule_min_faces"]
        if uv["islands_per_1k_faces"] > acfg["uv_islands_per_1k_faces_max"]:
            if len(f) >= island_rule_min:
                uv_problems.append(f"{uv['islands_per_1k_faces']:.1f} UV islands per 1k faces > "
                                   f"{acfg['uv_islands_per_1k_faces_max']} (seam-heavy)")
            else:
                uv_notes.append(f"{uv['islands_per_1k_faces']:.1f} UV islands per 1k faces ignored: {len(f)} tris < "
                                f"audit.uv_islands_rule_min_faces {island_rule_min} (low-poly, nothing to stall)")
    uv_usable = not uv_problems
    uv_plan = "keep_uv" if branch == "clean" and uv_usable else "rebake"
    if not tex:
        warnings.append("no image texture on the input; a bake will carry material base colours only")

    r = common.r
    checks = [
        common.check("out_of_scope_rig", "pass", note="no armature, shape keys or animation"),
        common.check("import", "pass", value=f"{len(f)} tris"),
        common.check("interior_face_ratio", "info", r(interior_ratio), ccfg["interior_face_max_ratio"]),
        common.check("nonmanifold_edge_ratio", "info", r(nonmanifold_ratio, 6), acfg["nonmanifold_edge_max_ratio"]),
        common.check("significant_shells", "info", len(significant), acfg["max_significant_shells"]),
        common.check("uv_usable", "info", uv_usable, note="; ".join(uv_problems or uv_notes) or None),
        common.check("branch", "info", branch, note="; ".join(dirty or clean_reasons)),
    ]
    metrics = {
        "tris": int(len(f)), "verts": int(len(v)), "verts_welded": int(n_welded),
        "weld_ratio": r(1 - n_welded / max(len(v), 1)),
        "bbox_min": [r(x) for x in lo], "bbox_max": [r(x) for x in hi],
        "dims_m": [r(x) for x in hi - lo], "diag_m": r(diag),
        "edges": es["edges"], "manifold_edge_ratio": r(es["manifold"] / edges),
        "boundary_edges": es["boundary"], "nonmanifold_edges": es["nonmanifold"],
        "winding_inconsistent_edges": es["winding_inconsistent"],
        "shells": len(shells), "significant_shells": len(significant),
        "small_shells": len(shells) - len(significant),
        "interior_face_ratio": r(interior_ratio), "interior_area_ratio": r(interior_area_ratio),
        "interior_faces": int(vis["interior"].sum()),
        "flipped_normal_ratio_est": r(flipped_ratio), "degenerate_faces": degenerate,
        "ray_seconds": round(ray_seconds, 1),
        "uv": {k: (r(x) if isinstance(x, float) else x) for k, x in uv.items()},
        "materials": len(mats), "textures": len(tex),
    }
    data = {
        "branch": branch, "branch_reasons": dirty or clean_reasons, "uv_plan": uv_plan,
        "uv_problems": uv_problems, "uv_notes": uv_notes, "unit": unit, "unit_factor": unit_factor,
        "source_height_m": r(src_height * unit_factor), "height_factor": r(height_factor, 6),
        "height_m": r(hi[2] - lo[2]), "height_source": "spec" if target_h else "input",
        "shells_top": [{k: (r(x) if isinstance(x, float) else x) for k, x in s.items() if k != "label"}
                       for s in shells[:10]],
        "materials": mats, "textures": tex, "ingest": ingest, "input": os.path.abspath(a.input),
        "joined_objects": joined_objects, "output_object": output_object,
    }
    common.write_result(a.out, TOOL, checks, metrics, warnings, {"ingest": ingest}, data,
                        overall="pass", source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
