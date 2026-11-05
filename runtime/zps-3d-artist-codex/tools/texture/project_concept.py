"""Texture a low-poly prop from its hand-painted concept: project the concept onto the mesh,
then fill what the concept cannot see. One albedo, one material.

Usage:
  python3 tools/texture/project_concept.py --input <low.glb> --concept 34=input/rock_34.png
         [--concept front=input/rock_front.png ...] [--mask 34=<w>/concept/mask_34.png]
         [--spec task/spec.json] --work <w>/texture [--out <w>/texture/project_concept.json] [--res N]
  $BLENDER -b --python-exit-code 1 --python tools/texture/project_concept.py -- <same args>

--input   GLB/glTF/FBX/OBJ; every mesh is joined into one object: a single mesh keeps its name,
          several (warning) take the file's stem.
--concept view=image, repeatable; view is a raster.VIEW_DIRS label (front back left right top 34).
--mask    view=mask PNG (white = object), e.g. validate_concept's mask_<view>.png; else derived
          with raster.concept_mask (alpha, else the bright-grey background rule).

1 UVs. The input's UVs are kept when every corner is inside 0-1 and the UV overlap ratio is at
  most audit.uv_overlap_max; else xatlas unwraps (bake.xatlas_unwrap, padding from
  texture.padding_px_by_res). Resolution as bake.py: next power of two of sqrt(area) x
  texture.texel_density_px_per_m / sqrt(UV occupancy), clamped to [min_res, max_res]; --res wins.
2 Camera per concept view, the rule IoU uses (gate1: raster.silhouette + normalize_to_bbox):
  orthographic along raster.view_dir(view, spec.concept.cameras) (the fitted concept camera when
  the spec has one, else VIEW_DIRS[view]), image axes raster._basis(d); the model's projected
  bbox (all vertices) maps onto the concept mask's bbox with one uniform scale (larger side to
  larger side) and centred. Pixel x = cx + (p.right - mu) * s, y = cy - (p.up - mv) * s.
3 Projection. Every texel inside a UV triangle gets its 3D point and flat face normal
  (barycentric). It is seen by a view when cos = n . (-d) > facing_min_dot and a ray from the
  point toward the camera (mathutils BVHTree) hits nothing. Its colour is the bilinear concept
  sample at the mapped pixel, used only inside the concept mask eroded by mask_shrink_px and away
  (occlusion_edge_px) from depth discontinuities of the model's own z-buffer in that view (so
  a near rock's colour does not bleed onto the one behind it). Several views: weighted by cos.
4 Fill, in this order:
  a facet: faces grouped into planar facets (region growing over shared edges, normal within
    facet_angle_deg of the seed face). A facet with at least facet_min_covered_ratio of its
    texels (and facet_min_covered_texels) projected gets its unseen texels from its projected
    texels: facet_fill mean = their average; linear (default) = a least-squares colour = a + B.p
    over 3D position where it explains the facet (R^2 >= facet_linear_min_r2, else the mean),
    clamped per channel to the projected colours' 5-95th percentiles, so a painted gradient
    (light, height) runs on under an occluder instead of leaving a flat patch.
  c palette (computed before b, since b blends into it): k-means (palette_k, numpy, Lab) over the
    eroded concept mask. Facets with projected texels vote with the cluster of their mean
    projected colour, weighted by their projected texel count: up facets (facet normal z >
    palette_up_z) for the up colour (the moss on a mossy rock), the others for the side colour;
    each is the weighted mean of its winning facets (clusters within palette_tie_share of the
    top vote count as winners too). Facet votes, not texel votes, so thin
    painted cracks and specks cannot outvote the colour the facets are painted in. A facet takes the up colour when up-facing, else the side
    colour times palette_dark_down (normal z < palette_down_z) or palette_dark_back (faces away
    from every concept camera), so unseen undersides stay darker as painted light would.
  b inpaint: per UV island with projected/facet texels, cv2.inpaint TELEA (inpaint_radius_px);
    the result is used up to inpaint_max_dist_px (scaled to the resolution, from a 1024 base)
    from known texels and blended linearly into the palette colour beyond half that distance.
  Coverage ratios (share of island texels): projected / facet / inpaint (blend weight >= 0.5) /
  palette. A palette share above palette_warn_ratio is a warning (most of the texture is guessed).
5 Gutter: texels outside the islands take the nearest island texel up to the padding, the mean
  colour beyond. Writes <work>/albedo.png, <work>/source_map.png (green projected, blue facet,
  yellow inpaint, red palette) and <work>/<object>_textured.glb: the object renamed nothing, one
  material named after the object, UV layer "bake"; unlit (bake.make_unlit, exported as
  KHR_materials_unlit) when spec style is hand_painted, else Principled.
6 Checks: the textured model rendered per concept view at the concept's resolution with the
  same camera mapping (Workbench, TEXTURE colour, flat light; Cycles when render_engine is cycles
  or Workbench fails), composited on white; SSIM (bake.masked_ssim: 7x7, per channel) against
  the concept over the concept mask: check ssim.<view> vs texture.ssim_min, warning when below.
  iou.<view> (render alpha vs mask, same frame) is info. Previews of the unseen preview_views.

New config keys live in EXTRA_DEFAULTS["texture"]["project"] (config.yaml overrides them).
Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, "..", "optimize"), os.path.join(HERE, "..", "lib"), HERE):
    _p = os.path.abspath(_p)
    if _p not in sys.path:
        sys.path.insert(0, _p)
try:
    import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
except ImportError:  # older installs without tools/lib/bootstrap.py
    pass
import numpy as np  # noqa: E402

import optlib  # noqa: E402
import optbpy  # noqa: E402
from optlib import common  # noqa: E402
import bpy  # noqa: E402
import raster  # noqa: E402
import bake  # noqa: E402  (texture_resolution, xatlas_unwrap, bake_material, make_unlit, masked_ssim)
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

TOOL = "texture/project_concept"

# Keys config.yaml does not define yet (move them under texture.project there).
EXTRA_DEFAULTS = {
    "texture": {
        "project": {
            "facing_min_dot": 0.15,          # n . to-camera above this to take a view's colour [guess]
            "mask_shrink_px": 2,             # erode the concept mask: no background bleed
            "occlusion_edge_px": 2,          # skip concept pixels this close to a depth jump [guess]
            "ray_eps_ratio": 1e-4,           # ray origin offset, of the bbox diagonal
            "facet_angle_deg": 10.0,         # faces within this of the seed normal form one facet
            "facet_min_covered_ratio": 0.10,  # facet fill needs this share of the facet projected [guess]
            "facet_min_covered_texels": 16,
            "facet_fill": "linear",          # linear (clamped planar colour fit) | mean (flat facet average)
            "facet_linear_min_r2": 0.5,      # linear only where the plane explains the facet's colour [guess]
            "inpaint_radius_px": 3,
            "inpaint_max_dist_px": 12,       # at 1024 px, scaled with the resolution [guess]
            "palette_k": 5,                  # 4-6 clusters
            "palette_samples": 50000,
            "palette_tie_share": 0.05,       # clusters this close to the top facet vote are averaged in [guess]
            "palette_up_z": 0.6,            # facet normal z above: up-facing (may take the up colour)
            "palette_down_z": -0.3,          # below: down-facing
            "palette_dark_back": 0.88,       # side colour factor, facets facing away from every concept camera [guess]
            "palette_dark_down": 0.75,       # side colour factor, down-facing facets [guess]
            "palette_warn_ratio": 0.5,       # palette share of texels above this: warning [guess]
            "render_engine": "workbench",    # workbench | cycles
            "render_samples": 16,            # cycles only
            "preview_views": ["front", "back", "left", "right", "top"],
            "preview_px": 768,
        },
    },
}

SOURCE_COLOURS = np.array([[60, 200, 60], [60, 110, 230], [235, 210, 40], [220, 50, 50]], np.uint8)
SOURCES = ("projected", "facet", "inpaint", "palette")


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--concept", action="append", required=True, help="view=image (repeatable)")
    p.add_argument("--mask", action="append", default=[], help="view=mask png (optional)")
    p.add_argument("--spec")
    p.add_argument("--work", required=True)
    p.add_argument("--out")
    p.add_argument("--res", type=int)
    a = p.parse_args(common.script_argv())
    a.out = a.out or os.path.join(a.work, "project_concept.json")
    a.concepts = _pairs(a.concept, "--concept")
    a.masks = _pairs(a.mask, "--mask")
    for v in a.masks:
        if v not in a.concepts:
            raise SystemExit(f"--mask {v}=... has no --concept {v}=...")
    return a


def _pairs(items, flag):
    out = {}
    for it in items:
        view, sep, path = it.partition("=")
        if not sep or view not in raster.VIEW_DIRS:
            raise SystemExit(f"{flag} wants view=path with view in {sorted(raster.VIEW_DIRS)}: {it!r}")
        if view in out:
            raise SystemExit(f"{flag} {view} given twice")
        out[view] = os.path.abspath(path)
    return out


def settings(spec_path):
    cfg, spec = optlib.settings(spec_path)
    return common.deep_merge(EXTRA_DEFAULTS, cfg), spec


# ------------------------------------------------------------------ raster helpers
def raster_tris(px, py, tri, w, h, z=None):
    """Triangle id and barycentrics per pixel centre (inside when all weights >= -1e-6, the test
    raster._raster_tris uses), row 0 = top. z: per-vertex depth; the smallest wins (z-buffer).
    Without z the last triangle wins (UVs: islands do not overlap).
    Returns fid (h,w) int32 (-1 empty), bary (h,w,3) float32, depth (h,w) float64 (inf empty)."""
    fid = np.full((h, w), -1, np.int32)
    bary = np.zeros((h, w, 3), np.float32)
    depth = np.full((h, w), np.inf)
    xs_all, ys_all = px[tri].tolist(), py[tri].tolist()
    zs_all = z[tri].tolist() if z is not None else None
    for i, ((x0, x1, x2), (y0, y1, y2)) in enumerate(zip(xs_all, ys_all)):
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-12:
            continue
        jx0 = max(int(math.ceil(min(x0, x1, x2) - 0.5)), 0)
        jx1 = min(int(math.floor(max(x0, x1, x2) - 0.5)), w - 1)
        jy0 = max(int(math.ceil(min(y0, y1, y2) - 0.5)), 0)
        jy1 = min(int(math.floor(max(y0, y1, y2) - 0.5)), h - 1)
        if jx1 < jx0 or jy1 < jy0:
            continue
        gx = (np.arange(jx0, jx1 + 1) + 0.5)[None, :]
        gy = (np.arange(jy0, jy1 + 1) + 0.5)[:, None]
        w0 = ((x1 - gx) * (y2 - gy) - (x2 - gx) * (y1 - gy)) / area
        w1 = ((x2 - gx) * (y0 - gy) - (x0 - gx) * (y2 - gy)) / area
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        sl = (slice(jy0, jy1 + 1), slice(jx0, jx1 + 1))
        if zs_all is not None:
            za, zb, zc = zs_all[i]
            zz = w0 * za + w1 * zb + w2 * zc
            sub = depth[sl]
            ins &= zz < sub
            sub[ins] = zz[ins]
        if not ins.any():
            continue
        fid[sl][ins] = i
        bary[sl][ins] = np.stack([w0, w1, w2], -1)[ins]
    return fid, bary, depth


def bilinear(img, x, y):
    """img (h,w,c) float at continuous coords (pixel i spans [i, i+1])."""
    h, w = img.shape[:2]
    x = np.clip(x - 0.5, 0, w - 1)
    y = np.clip(y - 0.5, 0, h - 1)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    return ((img[y0, x0] * (1 - fx) + img[y0, x1] * fx) * (1 - fy)
            + (img[y1, x0] * (1 - fx) + img[y1, x1] * fx) * fy)


# ------------------------------------------------------------------ concept views
CAMERAS = {}  # spec.concept.cameras (fitted azimuth/elevation per view), set in main()


class ViewMap:
    """Concept-pixel mapping of one view: the IoU rule (bbox to bbox, one scale, centred)."""

    def __init__(self, label, v, mask):
        self.label = label
        self.d = np.asarray(raster.view_dir(label, CAMERAS), float)
        self.d /= np.linalg.norm(self.d)
        self.right, self.up = raster._basis(self.d)
        p = raster.project(v, self.d)
        (umin, vmin), (umax, vmax) = p.min(0), p.max(0)
        bb = raster.bbox_of(mask)
        if bb is None:
            raise ValueError(f"concept mask for view {label} is empty")
        x0, x1, y0, y1 = (int(t) for t in bb)
        cw, ch = x1 + 1 - x0, y1 + 1 - y0
        self.s = max(cw, ch) / max(umax - umin, vmax - vmin, 1e-12)
        self.cx, self.cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
        self.mu, self.mv = (umin + umax) / 2, (vmin + vmax) / 2
        self.h, self.w = mask.shape
        self.info = {"mask_bbox_px": [x0, y0, cw, ch], "px_per_m": common.r(self.s, 3),
                     "model_extent_m": [common.r(umax - umin), common.r(vmax - vmin)],
                     "model_aspect_h_over_w": common.r((vmax - vmin) / max(umax - umin, 1e-12)),
                     "mask_aspect_h_over_w": common.r(ch / cw)}

    def to_px(self, pts):
        return (self.cx + (pts @ self.right - self.mu) * self.s,
                self.cy - (pts @ self.up - self.mv) * self.s)

    def camera(self, w, h):
        """(centre u, centre v, ortho_scale) of an ortho camera showing exactly this concept frame."""
        uc = self.mu + (w / 2 - self.cx) / self.s
        vc = self.mv - (h / 2 - self.cy) / self.s
        return uc, vc, max(w, h) / self.s


def read_concept(path):
    """(rgb float 0-1 composited on white, alpha bool or None)."""
    import cv2
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise ValueError(f"cannot read image: {path}")
    if im.dtype != np.uint8:
        im = (im / 257).astype(np.uint8)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    rgb = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2RGB).astype(np.float64) / 255
    if im.shape[2] == 4:
        a = im[:, :, 3:].astype(np.float64) / 255
        rgb = rgb * a + (1 - a)
    return rgb


def read_mask(path, shape, warnings, view):
    import cv2
    m = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if m is None:
        raise ValueError(f"cannot read mask: {path}")
    if m.shape != shape:
        warnings.append(f"mask {view} is {m.shape[1]}x{m.shape[0]}, concept {shape[1]}x{shape[0]}: resized (nearest)")
        m = cv2.resize(m, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
    return m > 127


def depth_edges(depth, fid, nrm, vm, grow):
    """Pixels within `grow` px of a depth jump in the model's z-buffer (or of its silhouette).
    A step between neighbours counts as a jump when it exceeds what the steeper of the two faces'
    planes allows across one pixel (x1.5, + half a pixel)."""
    import cv2
    nd = np.maximum(np.abs(nrm @ vm.d), 0.05)
    g = (np.abs(nrm @ vm.right) + np.abs(nrm @ vm.up)) / nd
    gp = np.where(fid >= 0, g[np.maximum(fid, 0)], 0.0)
    pix = 1.0 / vm.s
    edge = np.zeros(depth.shape, bool)
    fin = np.isfinite(depth)
    for sa, sb in (((slice(None), slice(None, -1)), (slice(None), slice(1, None))),
                   ((slice(None, -1), slice(None)), (slice(1, None), slice(None)))):
        a, b = depth[sa], depth[sb]
        fa, fb = fin[sa], fin[sb]
        both = fa & fb
        thr = (np.maximum(gp[sa], gp[sb]) + 0.5) * pix * 1.5
        step = np.abs(np.where(both, a, 0) - np.where(both, b, 0))
        jump = both & (step > thr)
        e = jump | (fa ^ fb)
        edge[sa] |= e
        edge[sb] |= e
    if grow > 0:
        k = 2 * grow + 1
        edge = cv2.dilate(edge.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    return edge


# ------------------------------------------------------------------ mesh helpers
def facets(v, f, nrm, area, angle_deg):
    """Planar facet label per face: region growing over shared (welded) edges from the largest
    unassigned face; a neighbour joins when its normal is within angle_deg of the seed's."""
    diag = float(np.linalg.norm(v.max(0) - v.min(0)))
    wmap, _ = optbpy.weld_map(v, 1e-6 * max(diag, 1e-9))
    fw = wmap[f]
    he = np.concatenate([fw[:, [0, 1]], fw[:, [1, 2]], fw[:, [2, 0]]])
    he_f = np.tile(np.arange(len(f)), 3)
    key = np.sort(he, axis=1)
    order = np.lexsort((key[:, 1], key[:, 0]))
    ks, fs = key[order], he_f[order]
    same = (ks[1:] == ks[:-1]).all(1)
    a_, b_ = fs[:-1][same], fs[1:][same]
    nb = [[] for _ in range(len(f))]
    for x, y in zip(a_.tolist(), b_.tolist()):
        if x != y:
            nb[x].append(y)
            nb[y].append(x)
    cos_t = math.cos(math.radians(angle_deg))
    lab = np.full(len(f), -1, np.int64)
    nl = nrm.tolist()
    k = 0
    for seed in np.argsort(-area, kind="stable").tolist():
        if lab[seed] >= 0:
            continue
        sn = nl[seed]
        lab[seed] = k
        stack = [seed]
        while stack:
            c = stack.pop()
            for o in nb[c]:
                if lab[o] < 0:
                    on = nl[o]
                    if on[0] * sn[0] + on[1] * sn[1] + on[2] * sn[2] >= cos_t:
                        lab[o] = k
                        stack.append(o)
        k += 1
    return lab, k


def uv_validity(uvt, max_overlap):
    inside = bool(((uvt >= -1e-6) & (uvt <= 1 + 1e-6)).all())
    cnt = optbpy.uv_coverage(np.clip(uvt, 0, 1), 512)
    overlap = float((cnt > 1).sum() / max((cnt > 0).sum(), 1))
    return inside and overlap <= max_overlap, {"inside_0_1": inside, "overlap_ratio": common.r(overlap)}


def choose_uvs(obj, v, f, area, cfg, res_arg, warnings):
    """(uvt (m,3,2), res, pad, info)."""
    tcfg = cfg["texture"]
    info = {}
    uvt = optbpy.loop_uvs(obj)
    if uvt is not None:
        ok, vinfo = uv_validity(uvt, cfg["audit"]["uv_overlap_max"])
        info["input_uv"] = vinfo
        if ok:
            occ = bake.uv_occupancy(uvt)
            res, raw = (res_arg, None) if res_arg else bake.texture_resolution(area, tcfg, occ)
            info.update({"unwrap": "kept input UVs", "uv_occupancy": common.r(occ),
                         "texture_res_raw": None if raw is None else round(raw, 1)})
            return uvt, res, bake.padding_for(res, tcfg["padding_px_by_res"]), info
        warnings.append(f"input UVs unusable ({vinfo}); re-unwrapped with xatlas")
    else:
        info["input_uv"] = None
    res, raw = (res_arg, None) if res_arg else bake.texture_resolution(area, tcfg)
    steps, how, uvt = [], None, None
    for _ in range(3):
        pad = bake.padding_for(res, tcfg["padding_px_by_res"])
        uvt, how = bake.xatlas_unwrap(v, f, res, pad, warnings)
        if uvt is None:
            break
        occ = bake.uv_occupancy(uvt)
        steps.append({"res": res, "occupancy": common.r(occ)})
        if res_arg:
            break
        new_res, raw = bake.texture_resolution(area, tcfg, occ)
        if new_res == res:
            break
        res = new_res
    if uvt is None:
        warnings.append(how)
        bake.smart_project(obj, warnings)
        how = "smart_project"
        uvt = optbpy.loop_uvs(obj)
        occ = bake.uv_occupancy(uvt)
        if not res_arg:
            res, raw = bake.texture_resolution(area, tcfg, occ)
        pad = bake.padding_for(res, tcfg["padding_px_by_res"])
    info.update({"unwrap": how, "uv_occupancy": common.r(bake.uv_occupancy(uvt)), "res_steps": steps,
                 "texture_res_raw": None if raw is None else round(raw, 1)})
    return uvt, res, pad, info


def kmeans(x, k, iters=40, seed=0):
    """Plain k-means with k-means++ seeding (deterministic). Returns (centres, labels)."""
    rng = np.random.default_rng(seed)
    k = max(1, min(k, len(x)))
    c = [x[rng.integers(len(x))]]
    d2 = ((x - c[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d2 / d2.sum() if d2.sum() > 0 else None
        c.append(x[rng.choice(len(x), p=p)])
        d2 = np.minimum(d2, ((x - c[-1]) ** 2).sum(1))
    c = np.array(c, float)
    lab = np.zeros(len(x), int)
    for _ in range(iters):
        lab = ((x[:, None, :] - c[None]) ** 2).sum(2).argmin(1)
        nc = np.array([x[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(k)])
        if np.allclose(nc, c, atol=1e-4):
            break
        c = nc
    return c, lab


def to_lab(rgb01):
    import cv2
    px = np.clip(rgb01 * 255 + 0.5, 0, 255).astype(np.uint8).reshape(-1, 1, 3)
    return cv2.cvtColor(px, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float64)


def hexc(c):
    c = np.clip(np.asarray(c) * 255 + 0.5, 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


# ------------------------------------------------------------------ rendering
def make_camera(scene):
    cd = bpy.data.cameras.new("pc_cam")
    cd.type = "ORTHO"
    cam = bpy.data.objects.new("pc_cam", cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def place(cam, d, right, up, uc, vc, depth0, diag, ortho_scale):
    loc = right * uc + up * vc + d * (depth0 - diag)
    m = Matrix(((right[0], up[0], -d[0], loc[0]), (right[1], up[1], -d[1], loc[1]),
                (right[2], up[2], -d[2], loc[2]), (0.0, 0.0, 0.0, 1.0)))
    cam.matrix_world = m
    cam.data.ortho_scale = ortho_scale
    cam.data.clip_start = diag * 0.01
    cam.data.clip_end = diag * 4


def setup_render(scene, engine, samples):
    scene.render.film_transparent = True
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    if engine == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = False
    else:
        scene.render.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light = "FLAT"
        sh.color_type = "TEXTURE"
        sh.show_cavity = False
        sh.show_shadows = False
        sh.show_object_outline = False
        sh.show_specular_highlight = False


def render_rgb(scene, w, h, path):
    """Render to path; returns (rgb float 0-1 composited on white, alpha float)."""
    import cv2
    scene.render.resolution_x, scene.render.resolution_y = w, h
    raw = path[:-4] + "_rgba.png"
    scene.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    im = cv2.imread(raw, cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[:2] != (h, w):
        raise RuntimeError(f"render failed: {raw}")
    if im.dtype != np.uint8:
        im = (im / 257).astype(np.uint8)
    a = im[:, :, 3].astype(np.float64) / 255
    rgb = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2RGB).astype(np.float64) / 255
    comp = rgb * a[:, :, None] + (1 - a[:, :, None])
    cv2.imwrite(path, cv2.cvtColor(np.clip(comp * 255 + 0.5, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    os.remove(raw)
    return comp, a


def cycles_materials(obj):
    """Principled materials see scene light in Cycles: swap in emission copies (unlit albedo)."""
    keep = [s.material for s in obj.material_slots]
    for s in obj.material_slots:
        s.material = bake.emission_copy(s.material)
    return keep


# ------------------------------------------------------------------ main
def main(a):
    import cv2
    from scipy import ndimage
    cfg, spec = settings(a.spec)
    global CAMERAS
    CAMERAS = ((spec or {}).get("concept") or {}).get("cameras") or {}
    tcfg, pcfg = cfg["texture"], cfg["texture"]["project"]
    os.makedirs(a.work, exist_ok=True)
    warnings, checks, artifacts = [], [], {}
    unlit = spec.get("style") == "hand_painted"

    optbpy.reset_scene()
    scene = bpy.context.scene
    objs = optbpy.import_model(a.input, merge_vertices=True)
    meshes = [o.name for o in objs if o.type == "MESH" and len(o.data.polygons)]
    name = meshes[0] if len(meshes) == 1 else os.path.splitext(os.path.basename(a.input))[0]
    obj = optbpy.join_world(name, objs)     # one mesh keeps its name; several are named after the file
    optbpy.triangulate(obj)
    if len(meshes) > 1:
        warnings.append(f"{len(meshes)} meshes in the input joined into one object '{name}'")
    v, f = optbpy.mesh_arrays(obj)
    farea, nrm = optbpy.face_areas_normals(v, f)
    area = float(farea.sum())
    diag = float(np.linalg.norm(v.max(0) - v.min(0)))
    data = {"input": a.input, "object": obj.name, "tris": len(f), "surface_area_m2": common.r(area),
            "style": spec.get("style"), "concepts": a.concepts}

    # ---- 1 UVs and resolution
    uvt, res, pad, uvinfo = choose_uvs(obj, v, f, area, cfg, a.res, warnings)
    ok_uv, vinfo = uv_validity(uvt, cfg["audit"]["uv_overlap_max"])
    checks.append(common.check("uv.inside_0_1", "pass" if vinfo["inside_0_1"] else "fail", vinfo["inside_0_1"]))
    checks.append(common.check("uv.overlap_ratio", "pass" if vinfo["overlap_ratio"] <= cfg["audit"]["uv_overlap_max"]
                               else "fail", vinfo["overlap_ratio"], cfg["audit"]["uv_overlap_max"]))
    spec_res = (spec.get("uv") or {}).get("resolution")
    if spec_res and int(spec_res) != res:
        warnings.append(f"texture is {res} px, spec uv.resolution is {spec_res} (pass --res {spec_res} to match)")
    data.update(uvinfo, texture_res=res, padding_px=pad)

    # ---- texels: 3D point and face normal
    corners = uvt.reshape(-1, 2)
    tri_idx = np.arange(len(corners)).reshape(-1, 3)
    fid, bary, _ = raster_tris(corners[:, 0] * res, (1 - corners[:, 1]) * res, tri_idx, res, res)
    isl = fid >= 0
    ty, tx = np.nonzero(isl)
    tf = fid[ty, tx]
    tb = bary[ty, tx].astype(np.float64)
    P = (tb[:, :, None] * v[f[tf]]).sum(1)
    N = nrm[tf]
    n_tex = len(tf)

    # ---- 2+3 projection per view
    tree = BVHTree.FromPolygons(v.tolist(), f.tolist(), all_triangles=True)
    eps = pcfg["ray_eps_ratio"] * diag
    acc = np.zeros((n_tex, 3))
    wsum = np.zeros(n_tex)
    concept_img, concept_mask, vmaps, views_info = {}, {}, {}, {}
    k_shrink = 2 * pcfg["mask_shrink_px"] + 1
    for view, path in a.concepts.items():
        img = read_concept(path)
        h, w = img.shape[:2]
        mask = read_mask(a.masks[view], (h, w), warnings, view) if view in a.masks else raster.concept_mask(path)
        concept_img[view], concept_mask[view] = img, mask
        vm = ViewMap(view, v, mask)
        vmaps[view] = vm
        inner = cv2.erode(mask.astype(np.uint8), np.ones((k_shrink, k_shrink), np.uint8)) > 0
        vx, vy = vm.to_px(v)
        zf, _, zdepth = raster_tris(vx, vy, f, w, h, z=v @ vm.d)
        usable = inner & ~depth_edges(zdepth, zf, nrm, vm, pcfg["occlusion_edge_px"])
        cos = -(N @ vm.d)
        cand = np.nonzero(cos > pcfg["facing_min_dot"])[0]
        to_cam = Vector(tuple(-vm.d))
        orig = (P[cand] - vm.d * eps + N[cand] * eps).tolist()
        far = 4 * diag
        free = np.fromiter((tree.ray_cast(Vector(o), to_cam, far)[0] is None for o in orig), bool, len(orig))
        seen = cand[free]
        X, Y = vm.to_px(P[seen])
        xi, yi = np.floor(X).astype(int), np.floor(Y).astype(int)
        inb = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        ok = np.zeros(len(seen), bool)
        ok[inb] = usable[yi[inb], xi[inb]]
        use = seen[ok]
        col = bilinear(img, X[ok], Y[ok])
        acc[use] += col * cos[use, None]
        wsum[use] += cos[use]
        views_info[view] = dict(vm.info, image=path, size=[w, h], mask=a.masks.get(view, "derived (raster.concept_mask)"),
                                facing_texels=int(len(cand)), unoccluded_texels=int(len(seen)),
                                projected_texels=int(len(use)), projected_ratio=common.r(len(use) / max(n_tex, 1)))
    covered = wsum > 0
    colour = np.zeros((n_tex, 3))
    colour[covered] = acc[covered] / wsum[covered, None]
    source = np.full(n_tex, -1, np.int8)
    source[covered] = 0

    # ---- 4a facet propagation
    flab, n_fac = facets(v, f, nrm, farea, pcfg["facet_angle_deg"])
    tfac = flab[tf]
    fac_n = np.bincount(tfac, minlength=n_fac)
    fac_cov = np.bincount(tfac[covered], minlength=n_fac)
    fac_mean = np.stack([np.bincount(tfac[covered], colour[covered, c], n_fac) for c in range(3)], 1)
    fac_mean /= np.maximum(fac_cov, 1)[:, None]
    fac_ok = (fac_cov >= pcfg["facet_min_covered_texels"]) & (fac_cov >= pcfg["facet_min_covered_ratio"] * fac_n)
    fill_a = ~covered & fac_ok[tfac]
    colour[fill_a] = fac_mean[tfac[fill_a]]
    linear_facets = 0
    if pcfg["facet_fill"] == "linear":
        # colour = a + B.p fitted on the facet's projected texels keeps a painted gradient across
        # the hidden part; clamped per channel to the projected range (no extrapolated colours)
        order = np.argsort(tfac, kind="stable")
        bounds = np.searchsorted(tfac[order], np.arange(n_fac + 1))
        for k in np.nonzero(fac_ok & (fac_cov < fac_n))[0]:
            idx = order[bounds[k]:bounds[k + 1]]
            cv_, hid = idx[covered[idx]], idx[~covered[idx]]
            X = np.c_[np.ones(len(cv_)), P[cv_] - P[cv_].mean(0)]
            coef, *_ = np.linalg.lstsq(X, colour[cv_], rcond=None)
            var = ((colour[cv_] - colour[cv_].mean(0)) ** 2).sum()
            r2 = 1 - ((X @ coef - colour[cv_]) ** 2).sum() / var if var > 1e-9 else 0.0
            if r2 < pcfg["facet_linear_min_r2"]:
                continue        # paint detail, not a gradient: the mean is the safer guess
            linear_facets += 1
            pred = np.c_[np.ones(len(hid)), P[hid] - P[cv_].mean(0)] @ coef
            lo, hi = np.percentile(colour[cv_], [5, 95], axis=0)
            colour[hid] = np.clip(pred, lo, hi)
    source[fill_a] = 1

    # ---- 4c palette (needed by 4b's blend)
    fnz = np.zeros((n_fac, 3))
    np.add.at(fnz, flab, nrm * farea[:, None])
    fnz /= np.maximum(np.linalg.norm(fnz, axis=1), 1e-12)[:, None]
    pix = []
    for view in a.concepts:
        inner = cv2.erode(concept_mask[view].astype(np.uint8), np.ones((k_shrink, k_shrink), np.uint8)) > 0
        pix.append(concept_img[view][inner])
    pix = np.concatenate(pix)
    rng = np.random.default_rng(0)
    if len(pix) > pcfg["palette_samples"]:
        pix = pix[rng.choice(len(pix), pcfg["palette_samples"], replace=False)]
    centres, plab = kmeans(to_lab(pix), pcfg["palette_k"])
    k_used = len(centres)
    centres_rgb = np.array([pix[plab == j].mean(0) if (plab == j).any() else pix.mean(0) for j in range(k_used)])
    fac_up = fnz[:, 2] > pcfg["palette_up_z"]
    # votes come from facets, not texels: a facet votes with the cluster of its mean projected
    # colour, weighted by its projected texel count, so thin painted cracks and specks (many
    # texels, small share of any facet) cannot outvote the colour the facets are painted in
    voters = fac_cov >= pcfg["facet_min_covered_texels"]
    fac_cl = ((to_lab(fac_mean)[:, None, :] - centres[None]) ** 2).sum(2).argmin(1)

    def dominant(sel):
        """(rgb, winning clusters, their vote share, all shares) among voting facets sel. Clusters
        within palette_tie_share of the top vote tie with it and are averaged in (by votes), so a
        near tie does not flip the colour of every unseen facet."""
        idx = np.nonzero(voters & sel)[0]
        if not idx.size:
            return None
        cnt = np.bincount(fac_cl[idx], weights=fac_cov[idx], minlength=k_used)
        share = cnt / cnt.sum()
        js = np.nonzero(share >= share.max() - pcfg["palette_tie_share"])[0]
        win = idx[np.isin(fac_cl[idx], js)]
        return ((fac_mean[win] * fac_cov[win, None]).sum(0) / fac_cov[win].sum(), [int(j) for j in js],
                float(share[js].sum()), [common.r(x) for x in share])

    side = dominant(~fac_up)
    up = dominant(fac_up)
    if side is None:
        j = int(np.bincount(plab, minlength=k_used).argmax())
        side = (centres_rgb[j], [j], None, None)
        warnings.append("no projected side facet: side palette colour is the concept's dominant cluster")
    if up is None:
        up = side
        warnings.append("no projected up-facing facet: up-facing facets use the side colour")
    cam_cos = np.stack([-(fnz @ vm.d) for vm in vmaps.values()], 1).max(1)
    fac_down = fnz[:, 2] < pcfg["palette_down_z"]
    fac_back = cam_cos < 0
    factor = np.ones(n_fac)
    factor[~fac_up & fac_back] = pcfg["palette_dark_back"]
    factor[~fac_up & fac_down] = pcfg["palette_dark_down"]
    fac_pal = np.where(fac_up[:, None], up[0][None], side[0][None] * factor[:, None])
    pal_col = np.clip(fac_pal[tfac], 0, 1)

    # ---- 4b inpaint within UV islands, blended into the palette with distance
    rest = source < 0
    img_known = np.zeros((res, res, 3))
    known_px = np.zeros((res, res), bool)
    img_known[ty, tx] = np.where(rest[:, None], pal_col, colour)
    known_px[ty, tx] = ~rest
    rest_px = np.zeros((res, res), bool)
    rest_px[ty, tx] = rest
    n_isl, isl_lab, stats, _ = cv2.connectedComponentsWithStats(isl.astype(np.uint8), connectivity=4)
    maxd = max(1.0, pcfg["inpaint_max_dist_px"] * res / 1024)
    wmap = np.zeros((res, res))
    inp = img_known.copy()
    radius = pcfg["inpaint_radius_px"]
    for i in range(1, n_isl):
        x, y, bw, bh = stats[i, :4]
        sl = (slice(y, y + bh), slice(x, x + bw))
        lab_i = isl_lab[sl] == i
        kn = known_px[sl] & lab_i
        todo = rest_px[sl] & lab_i
        if not todo.any() or not kn.any():
            continue
        dist = ndimage.distance_transform_edt(~kn)
        near = todo & (dist <= maxd)
        if not near.any():
            continue
        # known: this island's projected/facet texels and its far (palette) texels; everything
        # else in the crop, other islands included, is masked so it is never a source
        m = (~lab_i) | (todo & (dist <= 2 * maxd + radius))
        crop = np.clip(img_known[sl] * 255 + 0.5, 0, 255).astype(np.uint8)
        out = cv2.inpaint(crop, m.astype(np.uint8), radius, cv2.INPAINT_TELEA).astype(np.float64) / 255
        inp[sl][near] = out[near]
        wmap[sl][near] = np.clip((maxd - dist[near]) / (0.5 * maxd), 0, 1)
    wt = wmap[ty, tx]
    colour[rest] = wt[rest, None] * inp[ty, tx][rest] + (1 - wt[rest, None]) * pal_col[rest]
    source[rest & (wt >= 0.5)] = 2
    source[rest & (wt < 0.5)] = 3

    counts = {s: int((source == i).sum()) for i, s in enumerate(SOURCES)}
    ratios = {s: common.r(c / max(n_tex, 1)) for s, c in counts.items()}

    # ---- 5 texture, gutter, files
    tex = np.zeros((res, res, 3))
    tex[ty, tx] = np.clip(colour, 0, 1)
    dist_o, (iy, ix) = ndimage.distance_transform_edt(~isl, return_indices=True)
    out_px = ~isl
    tex[out_px] = tex[iy[out_px], ix[out_px]]
    far_px = out_px & (dist_o > pad)
    tex[far_px] = tex[ty, tx].mean(0)
    tex8 = np.clip(tex * 255 + 0.5, 0, 255).astype(np.uint8)
    albedo_png = os.path.join(a.work, "albedo.png")
    cv2.imwrite(albedo_png, cv2.cvtColor(tex8, cv2.COLOR_RGB2BGR))
    smap = np.full((res, res, 3), 255, np.uint8)
    smap[ty, tx] = SOURCE_COLOURS[source]
    source_png = os.path.join(a.work, "source_map.png")
    cv2.imwrite(source_png, cv2.cvtColor(smap, cv2.COLOR_RGB2BGR))
    artifacts.update(albedo=albedo_png, source_map=source_png)

    bake.set_uv_layer(obj, uvt)
    image = bpy.data.images.load(albedo_png, check_existing=False)
    image.name = "albedo"
    mat, ta, _ = bake.bake_material(obj, image)
    mat.name = obj.name
    if unlit:
        bake.make_unlit(mat, ta)
    mat.node_tree.nodes.active = ta
    glb = os.path.join(a.work, f"{bpy.path.clean_name(obj.name)}_textured.glb")
    optbpy.export_glb(glb, [obj])
    artifacts["glb"] = glb

    # ---- 6 renders, SSIM
    rdir = os.path.join(a.work, "renders")
    os.makedirs(rdir, exist_ok=True)
    cam = make_camera(scene)
    engine = pcfg["render_engine"]
    keep_mats = None

    def render_view(d, right, up, uc, vc, oscale, w, h, path):
        nonlocal engine, keep_mats
        place(cam, d, right, up, uc, vc, float((v @ d).min()), diag, oscale)
        try:
            return render_rgb(scene, w, h, path)
        except Exception as exc:  # noqa: BLE001  (no GPU context for Workbench)
            if engine == "cycles":
                raise
            warnings.append(f"Workbench render failed ({exc!r:.120}); rendering with Cycles emission")
            engine = "cycles"
            setup_render(scene, engine, pcfg["render_samples"])
            keep_mats = cycles_materials(obj)
            return render_rgb(scene, w, h, path)

    setup_render(scene, engine, pcfg["render_samples"])
    if engine == "cycles":
        keep_mats = cycles_materials(obj)
    ssim, ious = {}, {}
    for view, vm in vmaps.items():
        h, w = concept_mask[view].shape
        uc, vc, osc = vm.camera(w, h)
        rpath = os.path.join(rdir, f"render_{view}.png")
        rgb, alpha = render_view(vm.d, vm.right, vm.up, uc, vc, osc, w, h, rpath)
        cm = concept_mask[view]
        ssim[view] = common.r(bake.masked_ssim(concept_img[view], rgb, cm))
        ious[view] = common.r(raster.iou(cm, alpha > 0.5))
        cmp_path = os.path.join(rdir, f"compare_{view}.png")
        both = np.concatenate([concept_img[view], np.ones((h, 8, 3)), rgb], 1)
        cv2.imwrite(cmp_path, cv2.cvtColor(np.clip(both * 255 + 0.5, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        artifacts[f"render_{view}"] = rpath
        artifacts[f"compare_{view}"] = cmp_path
        good = ssim[view] >= tcfg["ssim_min"]
        checks.append(common.check(f"ssim.{view}", "pass" if good else "fail", ssim[view], tcfg["ssim_min"],
                                   note=None if good else "render vs concept below texture.ssim_min"))
        checks.append(common.check(f"iou.{view}", "info", ious[view],
                                   note="render alpha vs concept mask in the concept frame"))
        if not good:
            warnings.append(f"view {view}: SSIM {ssim[view]} < texture.ssim_min {tcfg['ssim_min']} "
                            f"(check {cmp_path}; IoU {ious[view]})")
    px = pcfg["preview_px"]
    for view in pcfg["preview_views"]:
        if view in vmaps or view not in raster.VIEW_DIRS:
            continue
        d = np.asarray(raster.view_dir(view, CAMERAS), float)
        d /= np.linalg.norm(d)
        right, upv = raster._basis(d)
        umin, umax, vmin, vmax = raster.fit_frame(raster.project(v, d), 0.05)
        rpath = os.path.join(rdir, f"preview_{view}.png")
        render_view(d, right, upv, (umin + umax) / 2, (vmin + vmax) / 2, umax - umin, px, px, rpath)
        artifacts[f"preview_{view}"] = rpath
    if keep_mats is not None:
        for s, m in zip(obj.material_slots, keep_mats):
            s.material = m

    # ---- result
    checks.append(common.check("coverage.projected", "info", ratios["projected"]))
    if ratios["palette"] > pcfg["palette_warn_ratio"]:
        warnings.append(f"{ratios['palette']:.0%} of the texels come from the palette fallback: most of the "
                        "texture is guessed; add concept views (back, top) for a better result")
    data.update({
        "views": views_info, "texels": n_tex, "coverage_texels": counts, "coverage_ratios": ratios,
        "facets": int(n_fac), "facets_filled": int((fac_ok & (fac_cov < fac_n)).sum()),
        "facets_filled_linear": linear_facets,
        "inpaint_max_dist_px": common.r(maxd, 2), "uv_islands": int(n_isl - 1),
        "palette": {
            "k": k_used, "centres": [hexc(c) for c in centres_rgb],
            "shares": [common.r(s) for s in np.bincount(plab, minlength=k_used) / len(plab)],
            "up": {"colour": hexc(up[0]), "clusters": up[1], "vote_share": None if up[2] is None else common.r(up[2]),
                   "votes": up[3]},
            "side": {"colour": hexc(side[0]), "clusters": side[1],
                     "vote_share": None if side[2] is None else common.r(side[2]), "votes": side[3]},
            "factors": {"up": 1.0, "side": 1.0, "back": pcfg["palette_dark_back"], "down": pcfg["palette_dark_down"]},
            "facets": {"up": int(fac_up.sum()), "down": int((~fac_up & fac_down).sum()),
                       "back": int((~fac_up & ~fac_down & fac_back).sum()),
                       "side": int((~fac_up & ~fac_down & ~fac_back).sum())},
        },
        "ssim_views": ssim, "iou_views": ious, "render_engine": engine,
        "material": "unlit (KHR_materials_unlit)" if unlit else "principled", "material_name": mat.name,
        "config_used": pcfg,
    })
    metrics = {"ssim_min": min(ssim.values()) if ssim else None, "texture_res": res,
               "coverage_projected": ratios["projected"], "coverage_facet": ratios["facet"],
               "coverage_inpaint": ratios["inpaint"], "coverage_palette": ratios["palette"]}
    common.write_result(a.out, TOOL, checks, metrics, warnings, artifacts, data, source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
