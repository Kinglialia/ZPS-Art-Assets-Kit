"""Measure a candidate mesh against the reference (optimize.md §5). Pure Python (trimesh + numpy).

Usage:
  python3 tools/optimize/measure.py --ref <w>/ref_high.glb --cand <w>/sweep/level_0.1.glb
         --out <w>/measure/level_0.1.json [--spec task/spec.json] [--views 12] [--raster 512]
         [--screen-px 400] [--samples 20000]

Metrics:
  silhouette IoU  orthographic silhouettes (tools/lib/raster.py) from optimize.cameras directions
                  on a Fibonacci sphere (above and below included); per view, ref and candidate
                  share one frame (raster.union_frame), so neither is clipped. Worst and mean.
  Hausdorff       two-way: surface samples (measure.samples, seeded) plus mesh vertices (up to
                  measure.max_vertex_samples) of each mesh -> exact closest point on the other
                  (optlib.closest_points). Hausdorff = max of both directions, mean = mean of
                  both directions' means. As fraction of the ref bbox diagonal and in projected
                  px = distance / ref bbox height x screen_px (optimize.screen_px_height).
  normal dev p95  angle between each candidate surface sample's face normal and the normal of the
                  nearest ref face, 95th percentile, degrees.
  texture error   (info, only when both meshes carry UV'd base-colour textures, i.e. UVs kept)
                  ref surface samples: |ref texture colour - candidate texture colour at the
                  closest candidate point| in RGB 0-1 / sqrt(3); mean and p95. Catches UVs a
                  simplifier smeared, which silhouettes and distances cannot see.
  validity        on the position-welded candidate (optlib.topology_stats, mesh_check's rules):
                  degenerate faces (float32 area < 1e-8 m2 or collapsed), non-manifold edges,
                  winding-inconsistent edges; the reference's own counts are measured the same way.
Checks against optimize.floor: silhouette_iou_min (worst view), hausdorff_max_px, normal_dev_p95_deg;
plus validity floors (no setting): valid.degenerate_faces = 0, valid.nonmanifold_edges and
valid.winding_inconsistent_edges <= the reference's. A level that fails one is never chosen.

Import as a module: Reference(path, settings) caches the reference; measure(ref, cand_path,
settings, out) writes the same JSON and returns the summary dict (sweep.py uses this).

Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import optlib  # noqa: E402
from optlib import common  # noqa: E402
import raster  # noqa: E402

TOOL = "optimize/measure"


def sample_mesh(v, f, n, max_vertices, seed):
    """Surface samples (area-weighted, seeded) + up to max_vertices mesh vertices.
    Returns (points, face index per surface sample, number of surface samples)."""
    rng = np.random.default_rng(seed)
    t = v[f]
    area = np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1) / 2
    fi = rng.choice(len(f), size=n, p=area / area.sum())
    r1, r2 = rng.random(n), rng.random(n)
    s = np.sqrt(r1)
    pts = (1 - s)[:, None] * t[fi, 0] + (s * (1 - r2))[:, None] * t[fi, 1] + (s * r2)[:, None] * t[fi, 2]
    used = np.unique(f)
    if used.size > max_vertices:
        used = rng.choice(used, max_vertices, replace=False)
    return np.concatenate([pts, v[used]]), fi, n


def face_normals(v, f):
    cr = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    return cr / np.maximum(np.linalg.norm(cr, axis=1), 1e-30)[:, None]


class Reference:
    def __init__(self, path, settings):
        mcfg = settings["measure"]
        self.path = path
        self.v, self.f = optlib.load_mesh(path)
        lo, hi = self.v.min(0), self.v.max(0)
        self.diag = float(np.linalg.norm(hi - lo))
        self.height = float(hi[2] - lo[2])
        self.normals = face_normals(self.v, self.f)
        self.samples, self.sample_fi, self.n_surf = sample_mesh(self.v, self.f, mcfg["samples"],
                                                                mcfg["max_vertex_samples"], 1)
        self.tris = len(self.f)
        self.topology = optlib.topology_stats(self.v, self.f)
        self.tex = optlib.load_textured(path)
        if self.tex["textured"] and len(self.tex["f"]) == len(self.f):
            pts = self.samples[:self.n_surf]
            self.sample_colour = optlib.texture_colour(self.tex, self.sample_fi, pts)
        else:
            self.sample_colour = None
        self.index = optlib.TriangleIndex(self.v, self.f)
        self._sil = {}

    def silhouette(self, d, size, frame):
        """Cached: simplified meshes usually stay inside the ref's projected bbox, so the union
        frame repeats from level to level."""
        key = (tuple(d), size, tuple(float(x) for x in frame))
        if key not in self._sil:
            self._sil[key] = raster.silhouette(self.v, self.f, d, size, frame)[0]
        return self._sil[key]


def measure(ref, cand_path, settings, out=None, views=None, size=None, screen_px=None, spec_path=None):
    ocfg, mcfg = settings["optimize"], settings["measure"]
    floor = ocfg["floor"]
    views = views or ocfg["cameras"]
    size = size or ocfg["raster_size"]
    screen_px = screen_px or ocfg["screen_px_height"]
    v, f = optlib.load_mesh(cand_path)

    # silhouettes
    ious = []
    for d in raster.sphere_dirs(views):
        frame = raster.union_frame([raster.project(ref.v, d), raster.project(v, d)])
        a = ref.silhouette(d, size, frame)
        b, _ = raster.silhouette(v, f, d, size, frame)
        ious.append(raster.iou(a, b))
    ious = np.array(ious)

    # two-way distances
    cand_pts, cand_fi, n_surf = sample_mesh(v, f, mcfg["samples"], mcfg["max_vertex_samples"], 2)
    _, d_c2r, tri_r = ref.index.query(cand_pts)
    cp_r2c, d_r2c, tri_c = optlib.closest_points(ref.samples, v, f)
    haus = float(max(d_c2r.max(), d_r2c.max()))
    mean = float((d_c2r.mean() + d_r2c.mean()) / 2)
    to_px = screen_px / ref.height if ref.height > 0 else float("nan")

    # normals: candidate surface samples vs nearest ref face
    cn = face_normals(v, f)[cand_fi]
    rn = ref.normals[tri_r[:n_surf]]
    ang = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", cn, rn), -1, 1)))
    p95 = float(np.percentile(ang, 95))

    tex_mean = tex_p95 = None
    if ref.sample_colour is not None:
        ct = optlib.load_textured(cand_path)
        if ct["textured"] and len(ct["f"]) == len(f):
            col = optlib.texture_colour(ct, tri_c[:ref.n_surf], cp_r2c[:ref.n_surf])
            err = np.linalg.norm(col - ref.sample_colour, axis=1) / np.sqrt(3)
            tex_mean, tex_p95 = float(err.mean()), float(np.percentile(err, 95))

    topo = optlib.topology_stats(v, f)
    r = common.r
    res = {
        "tris": int(len(f)), "ref_tris": ref.tris,
        "iou_worst": r(ious.min()), "iou_mean": r(ious.mean()), "iou_views": [r(x) for x in ious],
        "hausdorff_frac_diag": r(haus / ref.diag, 6), "hausdorff_m": r(haus, 6),
        "hausdorff_px": r(haus * to_px), "mean_dist_px": r(mean * to_px),
        "mean_dist_frac_diag": r(mean / ref.diag, 6),
        "hausdorff_cand_to_ref_px": r(d_c2r.max() * to_px), "hausdorff_ref_to_cand_px": r(d_r2c.max() * to_px),
        "normal_dev_p95_deg": r(p95, 2), "screen_px": screen_px, "views": views, "raster": size,
        "texture_error_mean": None if tex_mean is None else r(tex_mean),
        "texture_error_p95": None if tex_p95 is None else r(tex_p95),
        "validity": topo, "ref_validity": ref.topology,
    }
    checks = [
        common.check("silhouette_iou_worst", "pass" if ious.min() >= floor["silhouette_iou_min"] else "fail",
                     res["iou_worst"], floor["silhouette_iou_min"]),
        common.check("hausdorff_px", "pass" if haus * to_px <= floor["hausdorff_max_px"] else "fail",
                     res["hausdorff_px"], floor["hausdorff_max_px"]),
        common.check("normal_dev_p95_deg", "pass" if p95 <= floor["normal_dev_p95_deg"] else "fail",
                     res["normal_dev_p95_deg"], floor["normal_dev_p95_deg"]),
        common.check("valid.degenerate_faces", "pass" if topo["degenerate_faces"] == 0 else "fail",
                     topo["degenerate_faces"], 0, note="mesh_check rule: float32 area < 1e-8 m2 or collapsed"),
        common.check("valid.nonmanifold_edges",
                     "pass" if topo["nonmanifold_edges"] <= ref.topology["nonmanifold_edges"] else "fail",
                     topo["nonmanifold_edges"], ref.topology["nonmanifold_edges"], note="<= the reference's count"),
        common.check("valid.winding_inconsistent_edges",
                     "pass" if topo["winding_inconsistent_edges"] <= ref.topology["winding_inconsistent_edges"]
                     else "fail", topo["winding_inconsistent_edges"], ref.topology["winding_inconsistent_edges"],
                     note="<= the reference's count (flipped faces)"),
    ]
    res["pass"] = all(c["status"] == "pass" for c in checks)
    if tex_mean is not None:
        checks.append(common.check("texture_error_mean", "info", r(tex_mean),
                                   note="keep_uv only; no floor in config, compared between engines by sweep.py"))
    res["fails"] = [c["check"] for c in checks if c["status"] == "fail"]
    if out:
        common.write_result(out, TOOL, checks, res, data={"ref": os.path.abspath(ref.path),
                                                          "cand": os.path.abspath(cand_path)},
                            source=cand_path, spec_path=spec_path)
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ref", required=True)
    p.add_argument("--cand", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--spec")
    p.add_argument("--views", type=int)
    p.add_argument("--raster", type=int)
    p.add_argument("--screen-px", type=float)
    p.add_argument("--samples", type=int)
    a = p.parse_args(common.script_argv())
    try:
        cfg, _ = optlib.settings(a.spec)
        if a.samples:
            cfg["measure"]["samples"] = a.samples
        measure(Reference(a.ref, cfg), a.cand, cfg, a.out, a.views, a.raster, a.screen_px, a.spec)
    except Exception as exc:  # noqa: BLE001
        common.write_error(a.out, TOOL, exc, source=a.cand)
        sys.exit(1)


if __name__ == "__main__":
    main()
