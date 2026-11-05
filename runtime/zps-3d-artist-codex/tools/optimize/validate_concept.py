"""Validate concept images before any build or optimize step (SKILL.md, Intake).

Usage:
  python3 tools/optimize/validate_concept.py --images in/front.png in/back.png ... --work <w>
         [--spec task/spec.json] [--label in/img7.png=left] [--mask-method auto|alpha|rembg|grey]
         [--out <w>/concept/validate_concept.json]

Per image:
  label    from the file name: a token equal to one of concept.view_labels (front, left, back,
           right, 34, top; "3_4"/"3-4" count as 34). None or several -> vision_needed (label it
           yourself and re-run with --label path=label).
  mask     alpha channel when present; else rembg when importable and its model loads; else the
           bright-grey background rule (pixel is background when min channel > 225 and saturation
           < 0.12, as asset_checks/ac_common.concept_mask). Then: 3x3 opening, specks < 0.2 % of
           the image dropped, holes filled. Saved as <w>/concept/mask_<label>.png.
  checks   min(width, height) >= concept.min_resolution; mask does not touch the image border
           (object cropped); background plain: std of the background RGB (pixels more than 4 px
           from the mask) <= concept.bg_std_max (alpha masks pass).

Cross-view proportions (tolerance concept.proportion_tol), from mask bounding boxes:
  aspect   height/width: front vs back, left vs right (scale-free, always checked).
  pixels   when all four side views share one canvas size they are assumed drawn at one scale:
           height front = back = left = right, width front = back, width left = right.
  A failure names the view and how far off it is.

Complexity 0-1 per view, overall = max over views (info; > concept.complexity_warn -> warn):
  shape  = 1 - 4*pi*A / P^2              (0 for a disc, -> 1 for a jagged or thin outline)
  concav = min(1, n / 8), n = convexity defects deeper than 2 % of the mask bbox diagonal
  edges  = min(1, d / 0.08), d = Canny(50,150) edge pixels inside the mask eroded by 3 px,
           divided by that eroded area (interior detail)
  complexity = 0.4 * shape + 0.3 * concav + 0.3 * edges

Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import optlib  # noqa: E402
from optlib import common  # noqa: E402

TOOL = "optimize/validate_concept"
SPECK_RATIO = 0.002          # as ac_common.concept_mask
GREY_MIN_CHANNEL = 225       # as ac_common.concept_mask defaults
GREY_MAX_SAT = 0.12


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", nargs="+", required=True)
    p.add_argument("--work", required=True)
    p.add_argument("--spec")
    p.add_argument("--label", action="append", default=[], help="path=label override")
    p.add_argument("--mask-method", default="auto", choices=["auto", "alpha", "rembg", "grey"])
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    a.out = a.out or os.path.join(a.work, "concept", "validate_concept.json")
    return a


def label_from_name(path, labels):
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    stem = re.sub(r"(?<![0-9])3[_\-]4(?![0-9])", "34", stem)
    tokens = set(t for t in re.split(r"[^a-z0-9]+", stem) if t)
    found = [lab for lab in labels if str(lab).lower() in tokens]
    return found[0] if len(found) == 1 else None


def read_rgba(path):
    import cv2
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise ValueError(f"cannot read image: {path}")
    if im.dtype != np.uint8:
        im = (im / 257).astype(np.uint8)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    alpha = im[:, :, 3] if im.shape[2] == 4 else None
    rgb = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2RGB)
    return rgb, alpha


_REMBG = {}


def rembg_mask(rgb, model):
    """Foreground mask via rembg, or (None, reason) when rembg or its model is unavailable."""
    try:
        if "session" not in _REMBG:
            from rembg import new_session
            _REMBG["session"] = new_session(model)
        from rembg import remove
        out = remove(rgb, session=_REMBG["session"], only_mask=True)
        out = np.asarray(out)
        if out.ndim == 3:
            out = out[:, :, -1]
        return out > 127, None
    except Exception as exc:  # noqa: BLE001  (no network for the model, missing onnxruntime, ...)
        _REMBG["session"] = None
        return None, repr(exc)[:200]


def grey_mask(rgb):
    x = rgb.astype(np.float32)
    mn, mx = x.min(axis=2), x.max(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    return ~((mn > GREY_MIN_CHANNEL) & (sat < GREY_MAX_SAT))


def clean_mask(m):
    import cv2
    h, w = m.shape
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= SPECK_RATIO * w * h:
            keep[lab == i] = 1
    cnts, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(keep)
    cv2.drawContours(filled, cnts, -1, 1, thickness=-1)
    return filled.astype(bool)


def make_mask(rgb, alpha, method, model, warnings):
    if method in ("auto", "alpha") and alpha is not None and alpha.min() < 250:
        return alpha > 127, "alpha"
    if method == "alpha":
        warnings.append("no usable alpha channel; fell back to the grey background rule")
    if method in ("auto", "rembg") and _REMBG.get("session", True) is not None:
        m, err = rembg_mask(rgb, model)
        if m is not None:
            share = m.mean()
            if 0.005 < share < 0.95:
                return m, "rembg"
            warnings.append(f"rembg mask covers {share:.1%} of the image; used the grey rule instead")
        else:
            warnings.append(f"rembg unavailable ({err}); used the grey background rule")
    return grey_mask(rgb), "grey"


def complexity(mask, rgb):
    import cv2
    m8 = mask.astype(np.uint8)
    cnts, _ = cv2.findContours(m8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return {"complexity": 0.0}
    c = max(cnts, key=cv2.contourArea)
    area = float(cv2.contourArea(c))
    perim = float(cv2.arcLength(c, True))
    shape = 1 - 4 * np.pi * area / max(perim * perim, 1e-9)
    x, y, w, h = cv2.boundingRect(c)
    diag = float(np.hypot(w, h))
    n_def = 0
    hull = cv2.convexHull(c, returnPoints=False)
    if hull is not None and len(hull) > 3:
        try:
            defects = cv2.convexityDefects(c, hull)
        except cv2.error:
            defects = None
        if defects is not None:
            n_def = int((defects.reshape(-1, 4)[:, 3] / 256.0 > 0.02 * diag).sum())
    concav = min(1.0, n_def / 8)
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(grey, 50, 150) > 0
    inner = cv2.erode(m8, np.ones((7, 7), np.uint8)) > 0
    density = float(edges[inner].sum() / max(inner.sum(), 1))
    edge_s = min(1.0, density / 0.08)
    total = 0.4 * shape + 0.3 * concav + 0.3 * edge_s
    return {"complexity": round(float(total), 4), "shape": round(float(shape), 4),
            "concavities": n_def, "concav": round(concav, 4),
            "edge_density": round(density, 4), "edges": round(edge_s, 4)}


def main(a):
    import cv2
    cfg, _spec = optlib.settings(a.spec)
    ccfg = cfg["concept"]
    labels = [str(x) for x in ccfg["view_labels"]]
    overrides = {}
    for item in a.label:
        path, _, lab = item.rpartition("=")
        overrides[os.path.abspath(path)] = lab
    cdir = os.path.join(a.work, "concept")
    os.makedirs(cdir, exist_ok=True)
    checks, warnings, views, vision_needed = [], [], {}, []
    tol = ccfg["proportion_tol"]

    for path in a.images:
        lab = overrides.get(os.path.abspath(path)) or label_from_name(path, labels)
        rgb, alpha = read_rgba(path)
        h, w = rgb.shape[:2]
        raw, method = make_mask(rgb, alpha, a.mask_method, ccfg["rembg_model"], warnings)
        mask = clean_mask(raw)
        name = lab or "unlabeled_" + re.sub(r"[^A-Za-z0-9_-]+", "_", os.path.splitext(os.path.basename(path))[0])
        tag = f"{name} ({os.path.basename(path)})"
        if lab is None:
            vision_needed.append(os.path.abspath(path))
            checks.append(common.check(f"label.{name}", "not_checked",
                                       note="vision_needed: no single view label in the file name; "
                                            "label it and re-run with --label path=label"))
        elif lab in views:
            checks.append(common.check(f"label.{lab}", "fail",
                                       note=f"two images labelled {lab}: {views[lab]['image']} and {path}"))
            continue
        mpath = os.path.join(cdir, f"mask_{name}.png")
        cv2.imwrite(mpath, mask.astype(np.uint8) * 255)
        res_ok = min(w, h) >= ccfg["min_resolution"]
        checks.append(common.check(f"resolution.{name}", "pass" if res_ok else "fail",
                                   f"{w}x{h}", ccfg["min_resolution"]))
        if not mask.any():
            checks.append(common.check(f"mask.{name}", "fail", note=f"{tag}: empty mask ({method})"))
            continue
        border = int(mask[0].sum() + mask[-1].sum() + mask[:, 0].sum() + mask[:, -1].sum())
        checks.append(common.check(f"border.{name}", "pass" if border == 0 else "fail", border, 0,
                                   note=None if border == 0 else f"{tag}: object touches the image border "
                                                                 f"({border} px); it may be cropped"))
        if method == "alpha":
            bg_std = 0.0
        else:
            far = cv2.dilate(mask.astype(np.uint8), np.ones((9, 9), np.uint8)) == 0
            bg_std = float(rgb[far].reshape(-1, 3).std(axis=0).max()) if far.any() else 0.0
        checks.append(common.check(f"background_plain.{name}", "pass" if bg_std <= ccfg["bg_std_max"] else "fail",
                                   round(bg_std, 2), ccfg["bg_std_max"],
                                   note=None if bg_std <= ccfg["bg_std_max"] else
                                   f"{tag}: background is not plain; the mask may be wrong (check mask_{name}.png)"))
        ys, xs = np.nonzero(mask)
        bw, bh = int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
        info = {"image": os.path.abspath(path), "label": lab, "mask": mpath, "mask_method": method,
                "size": [w, h], "bbox_px": [int(xs.min()), int(ys.min()), bw, bh],
                "width_px": bw, "height_px": bh, "aspect_h_over_w": round(bh / bw, 4),
                "background_std": round(bg_std, 2)}
        info.update(complexity(mask, rgb))
        views[name] = info

    # ---------------------------------------------------------------- proportions
    def pct(x, ref):
        return abs(x - ref) / ref

    def prop_check(name, a_view, b_view, key, what):
        if a_view not in views or b_view not in views:
            return
        va, vb = views[a_view][key], views[b_view][key]
        off = pct(vb, va)
        ok = off <= tol
        checks.append(common.check(name, "pass" if ok else "fail", round(off, 4), tol,
                                   note=None if ok else f"{b_view}: {what} {off:.1%} off {a_view} "
                                                        f"({vb} vs {va}; tolerance {tol:.0%})"))

    prop_check("proportion.aspect.front_back", "front", "back", "aspect_h_over_w", "height/width")
    prop_check("proportion.aspect.left_right", "left", "right", "aspect_h_over_w", "height/width")
    side = [v for v in ("front", "back", "left", "right") if v in views]
    same_scale = len(side) >= 2 and len({tuple(views[v]["size"]) for v in side}) == 1
    if same_scale:
        ref = side[0]
        for v in side[1:]:
            prop_check(f"proportion.height.{ref}_{v}", ref, v, "height_px", "height")
        prop_check("proportion.width.front_back", "front", "back", "width_px", "width")
        prop_check("proportion.width.left_right", "left", "right", "width_px", "width")
    elif len(side) >= 2:
        checks.append(common.check("proportion.height.cross_view", "not_checked",
                                   note="views have different canvas sizes, so no shared scale; "
                                        "only height/width aspect pairs were compared"))

    comp = {k: v["complexity"] for k, v in views.items() if "complexity" in v}
    overall_c = max(comp.values()) if comp else None
    if overall_c is not None:
        warn = overall_c > ccfg["complexity_warn"]
        checks.append(common.check("complexity", "info", overall_c, ccfg["complexity_warn"],
                                   note="above complexity_warn: warn before self-build" if warn else None))
    metrics = {"views": len(views), "vision_needed": len(vision_needed), "complexity": overall_c,
               "same_scale_assumed": same_scale}
    data = {"views": views, "vision_needed": vision_needed, "mask_dir": cdir,
            "complexity_formula": "0.4*(1-4*pi*A/P^2) + 0.3*min(1,defects/8) + 0.3*min(1,edge_density/0.08)"}
    common.write_result(a.out, TOOL, checks, metrics, warnings,
                        {f"mask_{k}": v["mask"] for k, v in views.items()}, data, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc)
        sys.exit(1)
