"""Contact between declared surface pairs on evaluated meshes (world space).

Spec: floor_z (default 0), contacts: [
  {"a": "RockL", "b": "floor", "expect": "touch", "tolerance_m": 0.01, "min_support": 0.05},
  {"a": "RockS", "b": "RockL", "expect": "touch" | "gap" | "no_penetration", "tolerance_m": 0.01}]
- floor: gap = lowest vertex z - floor_z; support = share of the object's bottom-facing
  face area lying within tolerance of the floor (catches 'touches at one vertex').
- object pair: min vertex-to-surface distance both ways (0 when triangles intersect),
  penetration via BVH triangle overlap, contact_verts = vertices of A within tolerance of B.
  v0.2: a vertex counts as inside B by ray parity (odd number of hits along +X and +Z;
  valid for closed B), not by the nearest face normal (v0.1 reported 1.71 m false depth).
  vertex_depth_lower_bound_m = deepest inside vertex to B's surface. It only sees vertices:
  two shapes can overlap with no vertex inside, so look at the renders too.
  no_penetration fails on intersecting triangles or any vertex inside the other object;
  max_penetration_m allows a stated embedding (the reason goes in the task record).
expect touch: |gap| <= tol, no penetration beyond tol; gap: distance > tol; no_penetration: no overlap.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import ac_common as ac  # noqa: E402  (imports bpy first)
import bmesh  # noqa: E402


def load(name):
    me = ac.evaluated_mesh(bpy.data.objects[name])
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm, BVHTree.FromBMesh(bm)


def inside(tree, co):
    """Ray parity along two axes; both must agree (robust to grazing hits)."""
    votes = 0
    for d in (Vector((1, 0, 0)), Vector((0, 0, 1))):
        n, o = 0, co.copy()
        for _ in range(64):
            loc, _nrm, _i, _dist = tree.ray_cast(o, d)
            if loc is None:
                break
            n += 1
            o = loc + d * 1e-5
        votes += n % 2
    return votes == 2


def min_dist(bm_a, tree_b, tol):
    """Min distance from A's vertices to B, count within tol, and the deepest A vertex
    inside B (distance to B's surface; vertex-based lower bound)."""
    best, near, depth, inside_n = None, 0, 0.0, 0
    for v in bm_a.verts:
        loc, _nrm, _, d = tree_b.find_nearest(v.co)
        if loc is None:
            continue
        if inside(tree_b, v.co):
            inside_n += 1
            depth = max(depth, d)
            d = 0.0
        best = d if best is None else min(best, d)
        near += d <= tol
    return best, near, depth, inside_n


def main():
    a, spec = ac.parse_args()
    floor_z = spec.get("floor_z", 0.0)
    checks, data = [], {}
    cache = {}

    def get(name):
        if name not in cache:
            cache[name] = load(name)
        return cache[name]

    ac.target_objects(spec)   # resolves spec.objects (joined-mesh fallback) for the checks below
    for c in spec.get("contacts", []):
        key = f"{c['a']}~{c['b']}"
        tol = c.get("tolerance_m", 0.01)
        absent = [n for n in (c["a"], c["b"]) if n != "floor" and n not in bpy.data.objects]
        if absent:
            checks.append(ac.spec_object_check(key, absent[0], "contact"))
            continue
        bm_a, tree_a = get(c["a"])
        if c["b"] == "floor":
            gap = min(v.co.z for v in bm_a.verts) - floor_z
            down = [f for f in bm_a.faces if f.normal.z < -0.5]
            down_area = sum(f.calc_area() for f in down) or 1e-12
            touching = sum(f.calc_area() for f in down if all(abs(v.co.z - floor_z) <= tol for v in f.verts))
            support = touching / down_area
            data[key] = {"gap_m": ac.r(gap), "support_ratio": ac.r(support, 3)}
            ok = abs(gap) <= tol and support >= c.get("min_support", 0.0)
            checks.append(ac.check(key, "pass" if ok else "fail", data[key],
                                   {"abs_gap_m<=": tol, "support>=": c.get("min_support", 0.0)},
                                   note="negative gap = sinks below floor"))
            continue
        bm_b, tree_b = get(c["b"])
        d_ab, near_a, dep_a, in_a = min_dist(bm_a, tree_b, tol)
        d_ba, near_b, dep_b, in_b = min_dist(bm_b, tree_a, tol)
        overlap_pairs = len(tree_a.overlap(tree_b))
        dist = 0.0 if overlap_pairs else min(x for x in (d_ab, d_ba) if x is not None)
        depth = max(dep_a, dep_b)
        data[key] = {"min_distance_m": ac.r(dist), "intersecting_tri_pairs": overlap_pairs,
                     "vertex_depth_lower_bound_m": ac.r(depth),
                     "verts_inside": {"a_in_b": in_a, "b_in_a": in_b},
                     "contact_verts_a": near_a, "contact_verts_b": near_b}
        exp = c.get("expect", "touch")
        max_depth = c.get("max_penetration_m", tol)
        inside_any = in_a + in_b > 0
        note = None
        if exp == "touch":
            # resting contact: surfaces meet, slight embedding up to max_penetration_m allowed
            ok = dist <= tol and depth <= max_depth
            if overlap_pairs and depth <= max_depth:
                note = "surfaces intersect but within allowed embedding"
        elif exp == "gap":
            ok = dist > tol and overlap_pairs == 0
        else:  # no_penetration
            if "max_penetration_m" in c:
                ok = depth <= max_depth
                if overlap_pairs or inside_any:
                    note = f"embedding within the allowed {max_depth} m"
            else:
                ok = overlap_pairs == 0 and not inside_any
        checks.append(ac.check(key, "pass" if ok else "fail", data[key], {"expect": exp, "tolerance_m": tol}, note))
    for bm, _ in cache.values():
        bm.free()
    if not spec.get("contacts"):
        checks.append(ac.check("contacts", "not_checked", note="spec has no contacts"))
    ac.write_result(a.out, "contact_check", a.spec, checks, data)


if __name__ == "__main__":
    ac.run_main(main, "contact_check")
