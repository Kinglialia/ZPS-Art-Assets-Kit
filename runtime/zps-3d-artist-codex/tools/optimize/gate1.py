"""Gate 1: orient the model to the concept and compare silhouettes (optimize.md §2).

Usage:
  python3 tools/optimize/gate1.py --work <w> [--spec task/spec.json] [--input <w>/ingest.glb]
         [--concept-dir <w>/concept] [--out <w>/gate1.json]

Concept masks: <concept-dir>/mask_<label>.png from validate_concept.py, labels front, back,
left, right, top, 34 (tools/lib/raster.py VIEW_DIRS). Without masks the gate is skipped.

Orientation search: the 4 rotations about the vertical axis (front = -Y, +X, +Y, -X) first; when
the best front IoU is below gate1.silhouette_iou_min, all 24 axis-aligned rotations. The pick is
the highest front IoU; candidates within gate1.tie_tolerance of it are decided by the mean IoU
over every concept view (front and back silhouettes are mirror images, so the side views break
the tie). Without a front mask the mean IoU decides.

Specks: before scoring, shells under cleanup.loose_part_min_ratio of the faces or with a bbox
diagonal under 2 % of the model's are left out (data.specks), so a floating speck cannot stretch
the bbox normalisation; the bottom-centre of oriented.glb uses the kept shells too.

IoU per view: orthographic silhouette (raster.silhouette) and concept mask, both cropped to their
bbox and fitted into the same square (raster.normalize_to_bbox), because the concept has no scale.
Writes <w>/oriented.glb (ingest.glb under one rotation node, bottom-centre kept) and
<w>/gate1/overlay_<view>.png (red = concept only, blue = model only, grey = both).
Fails a view below gate1.silhouette_iou_min: show the overlays and ask the user.

Exit 0 on pass/fail/skipped; 1 on error (error JSON written first).
"""
import argparse
import glob
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import optlib  # noqa: E402
from optlib import common  # noqa: E402
import raster  # noqa: E402

TOOL = "optimize/gate1"


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--work", required=True)
    p.add_argument("--spec")
    p.add_argument("--input")
    p.add_argument("--concept-dir")
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    a.input = a.input or os.path.join(a.work, "ingest.glb")
    a.concept_dir = a.concept_dir or os.path.join(a.work, "concept")
    a.out = a.out or os.path.join(a.work, "gate1.json")
    return a


def rotations_z4():
    out = []
    for k in range(4):
        c, s = [(1, 0), (0, 1), (-1, 0), (0, -1)][k]
        out.append((f"rz{90 * k}", np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)))
    return out


def rotations_24():
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = np.zeros((3, 3))
            for row, (col, sg) in enumerate(zip(perm, signs)):
                m[row, col] = sg
            if np.linalg.det(m) > 0:
                out.append(("m" + "".join(f"{'+' if sg > 0 else '-'}{'xyz'[c]}" for c, sg in zip(perm, signs)), m))
    return out


def load_masks(cdir):
    import cv2
    masks = {}
    for path in sorted(glob.glob(os.path.join(cdir, "mask_*.png"))):
        label = os.path.basename(path)[5:-4]
        if label in raster.VIEW_DIRS:
            masks[label] = cv2.imread(path, cv2.IMREAD_GRAYSCALE) > 127
    return masks


SPECK_BBOX_RATIO = 0.02   # shell bbox diagonal / model diagonal below which a shell is a speck


def drop_specks(v, f, min_face_ratio, bbox_ratio=SPECK_BBOX_RATIO):
    """Faces of the shells that shape the silhouette. A shell is dropped when it holds fewer than
    min_face_ratio of the faces (cleanup.loose_part_min_ratio, the rule cleanup.py applies later)
    or its bbox diagonal is under bbox_ratio of the model's. Vertices are welded by position
    first (glTF splits them at UV seams). Returns (faces kept, info dict)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    diag = float(np.linalg.norm(v.max(0) - v.min(0))) or 1.0
    q = np.round(v / (diag * 1e-6)).astype(np.int64)
    _, weld = np.unique(q, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    fw = weld[f]
    n = int(weld.max()) + 1
    e = np.concatenate([fw[:, [0, 1]], fw[:, [1, 2]]])
    _, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)), directed=False)
    flab = lab[fw[:, 0]]
    keep = np.ones(len(f), bool)
    dropped = []
    for s_ in np.unique(flab):
        m = flab == s_
        t = v[f[m]].reshape(-1, 3)
        sd = float(np.linalg.norm(t.max(0) - t.min(0)))
        share = m.sum() / len(f)
        if share < min_face_ratio or sd < bbox_ratio * diag:
            keep &= ~m
            dropped.append({"faces": int(m.sum()), "face_share": common.r(share, 6),
                            "bbox_diag_m": common.r(sd, 5), "bbox_share": common.r(sd / diag, 5)})
    if not keep.any():   # never drop everything
        keep[:] = True
        dropped = []
    info = {"shells": int(len(np.unique(flab))), "dropped": dropped[:50], "dropped_count": len(dropped),
            "faces_dropped": int((~keep).sum()), "min_face_ratio": min_face_ratio, "bbox_ratio": bbox_ratio}
    return f[keep], info


def score(v, f, masks_n, size):
    ious, sils = {}, {}
    for label, cm in masks_n.items():
        sil, _ = raster.silhouette(v, f, raster.VIEW_DIRS[label], size)
        sn = raster.normalize_to_bbox(sil, size)
        sils[label] = sn
        ious[label] = raster.iou(cm, sn)
    return ious, sils


def main(a):
    import cv2
    cfg, _spec = optlib.settings(a.spec)
    gcfg = cfg["gate1"]
    size = cfg["optimize"]["raster_size"]
    iou_min = gcfg["silhouette_iou_min"]
    masks = load_masks(a.concept_dir)
    if not masks:
        common.write_result(a.out, TOOL, overall="skipped", source=a.input, spec_path=a.spec,
                            checks=[common.check("concept", "not_checked",
                                                 note=f"no mask_<view>.png in {a.concept_dir}; run validate_concept.py")])
        return
    masks_n = {k: raster.normalize_to_bbox(m, size) for k, m in masks.items()}
    v, f_all = optlib.load_mesh(a.input)
    # specks would stretch the bbox every silhouette is normalised to; cleanup deletes them later
    f, speck_info = drop_specks(v, f_all, cfg["cleanup"]["loose_part_min_ratio"],
                                cfg["gate1"].get("speck_bbox_ratio", SPECK_BBOX_RATIO))

    def primary(ious):
        return ious["front"] if "front" in ious else float(np.mean(list(ious.values())))

    def search(cands):
        rows = []
        for name, rot in cands:
            ious, sils = score(v @ rot.T, f, masks_n, size)
            rows.append({"name": name, "rot": rot, "ious": ious, "sils": sils,
                         "primary": primary(ious), "mean": float(np.mean(list(ious.values())))})
        return rows

    rows = search(rotations_z4())
    searched = 4
    if max(r["primary"] for r in rows) < iou_min:
        rows = search(rotations_24())
        searched = 24
    top = max(r["primary"] for r in rows)
    tied = [r for r in rows if r["primary"] >= top - gcfg["tie_tolerance"]]
    best = max(tied, key=lambda r: (r["mean"], r["primary"]))
    warnings = []
    if len(tied) > 1:
        warnings.append(f"{len(tied)} orientations tie on front IoU within {gcfg['tie_tolerance']}; "
                        f"picked {best['name']} by mean IoU over {sorted(masks)}")
    if speck_info["dropped_count"]:
        warnings.append(f"{speck_info['dropped_count']} speck shell(s), {speck_info['faces_dropped']} faces, ignored for "
                        "silhouettes and bottom-centre (cleanup.py deletes shells below loose_part_min_ratio)")
    if "front" not in masks:
        warnings.append("no front concept; orientation chosen by mean IoU over the views present")

    # rotate, then put the origin back at bottom-centre
    rot = best["rot"]
    vr = (v @ rot.T)[np.unique(f)]
    lo, hi = vr.min(0), vr.max(0)
    m4 = np.eye(4)
    m4[:3, :3] = rot
    m4[:3, 3] = [-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]]
    oriented = os.path.join(a.work, "oriented.glb")
    optlib.wrap_root_transform(a.input, oriented, m4)

    odir = os.path.join(a.work, "gate1")
    os.makedirs(odir, exist_ok=True)
    checks, artifacts, per_view = [], {"oriented": oriented}, {}
    for label in sorted(masks):
        img, red, blue = raster.overlay_image(masks_n[label], best["sils"][label])
        path = os.path.join(odir, f"overlay_{label}.png")
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        artifacts[f"overlay_{label}"] = path
        val = best["ious"][label]
        per_view[label] = {"iou": common.r(val), "concept_only_pct": common.r(red), "model_only_pct": common.r(blue)}
        checks.append(common.check(f"silhouette_iou.{label}", "pass" if val >= iou_min else "fail",
                                   common.r(val), iou_min,
                                   note=None if val >= iou_min else
                                   f"{label}: IoU {val:.3f} < {iou_min}; show {os.path.basename(path)} and ask the user"))
    metrics = {"iou_" + k: x["iou"] for k, x in per_view.items()}
    metrics.update({"iou_worst": min(x["iou"] for x in per_view.values()),
                    "orientations_searched": searched})
    data = {
        "orientation": {"name": best["name"], "rotation_zup": rot.tolist(), "matrix_zup": m4.tolist(),
                        "search": searched},
        "views": per_view,
        "specks": speck_info,
        "candidates": sorted(({"name": r["name"], "front_or_mean": common.r(r["primary"]),
                               "mean": common.r(r["mean"])} for r in rows),
                             key=lambda x: -x["front_or_mean"]),
    }
    common.write_result(a.out, TOOL, checks, metrics, warnings, artifacts, data,
                        source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
