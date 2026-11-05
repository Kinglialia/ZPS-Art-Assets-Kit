"""Silhouette match against the concept: render the asset from the concept camera and
compare with the concept mask (IoU = intersection / union).

The .blend must contain a camera matching the concept (M1 creates "ConceptCam"; for
other methods the artist sets it up with the concept as camera background).

Spec: objects, iou.{concept (path, relative to the spec), camera_object (default "ConceptCam"),
  background {max_min_channel, min_saturation}, min_iou (default 0.90),
  polygons_from (optional, path relative to the spec): a JSON in the m1.json form
  {"objects": [{"name": ..., "polygon": [[x,y],...]} | {"name": ..., "region": "rest"}]},
  front-most object first. It is the single source of the per-object polygons (for M1 it is
  task/m1.json itself); the spec does not copy them}.
No iou block in the spec: a result with check `iou` not_checked (the orthographic concept IoU of
the build/optimize paths lives in assembly.json / gate1.json / measure). Any error still writes
a JSON (overall `error`, traceback in data; ac_common.run_main) before exiting 1.
Outputs: result JSON, iou_render.png and iou_diff.png (red = only concept, blue = only render)
next to --out.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import bpy  # noqa: E402
import cv2  # noqa: E402
import numpy as np  # noqa: E402

import ac_common as ac  # noqa: E402


NO_IOU_NOTE = ("spec has no iou block; orthographic concept IoU comes from assembly/gate1/measure "
               "(self_build assembly.json, optimize gate1.json and measure/*.json)")


def main():
    a, spec = ac.parse_args()
    if not spec.get("iou"):
        ac.write_result(a.out, "iou_check", a.spec, [ac.check("iou", "not_checked", note=NO_IOU_NOTE)])
        return
    run(a, spec)   # errors: ac.run_main writes overall "error" with the traceback, exit 1


def run(a, spec):
    cfg = spec["iou"]
    base = os.path.dirname(os.path.abspath(a.spec))
    concept = ac.spec_path(a.spec, cfg["concept"])
    mask, w, h = ac.concept_mask(concept, cfg.get("background"))
    scene = bpy.context.scene
    cname = cfg.get("camera_object", "ConceptCam")
    if cname not in bpy.data.objects:
        ac.write_result(a.out, "iou_check", a.spec,
                        [ac.check("iou.camera", "fail", note=f"camera object '{cname}' not in the .blend")])
        return
    scene.camera = bpy.data.objects[cname]
    objs = ac.target_objects(spec)
    outdir = os.path.dirname(os.path.abspath(a.out))
    rpath = os.path.join(outdir, "iou_render.png")
    ra = ac.render_alpha(scene, rpath, objs, w, h)
    cm = mask.astype(bool)
    iou = float((ra & cm).sum() / max((ra | cm).sum(), 1))
    diff = np.full((h, w, 3), 255, np.uint8)
    diff[ra & cm] = (200, 200, 200)
    diff[cm & ~ra] = (0, 0, 255)      # BGR red: in concept, missing in render
    diff[ra & ~cm] = (255, 0, 0)      # BGR blue: extra in render
    cv2.imwrite(os.path.join(outdir, "iou_diff.png"), diff)
    min_iou = cfg.get("min_iou", 0.90)
    checks = [ac.check("iou.all", "pass" if iou >= min_iou else "fail", ac.r(iou), min_iou)]
    data = {"concept": concept, "camera": cname, "iou_all": ac.r(iou),
            "concept_px": int(cm.sum()), "render_px": int(ra.sum())}

    polys = {}
    if cfg.get("polygons_from"):
        src = os.path.normpath(os.path.join(base, cfg["polygons_from"]))
        with open(src) as fh:
            for ob in json.load(fh).get("objects", []):
                if ob.get("polygon"):
                    polys[ob["name"]] = ob["polygon"]
        data["polygons_from"] = src
    if polys and ac.TARGETS.get("mode") == "joined":   # per-object regions mean nothing on one joined mesh
        checks += [ac.spec_object_check(f"iou.{name}", name, "iou polygon") for name in polys]
        polys = {}
    if polys:
        taken = np.zeros_like(mask)
        per = {}
        for name, poly in polys.items():
            pm = np.zeros_like(mask)
            cv2.fillPoly(pm, [np.array(poly, np.int32)], 1)
            per[name] = mask & pm & (1 - taken)
            taken |= per[name]
        rest = [o.name for o in objs if o.name not in per]
        if len(rest) == 1:
            per[rest[0]] = mask & (1 - taken)
        # rendered silhouettes: front objects occlude the ones behind, as in the concept
        visible_before = np.zeros((h, w), bool)
        for name in list(polys) + rest:
            if name not in bpy.data.objects:
                checks.append(ac.spec_object_check(f"iou.{name}", name, "iou polygon"))
                continue
            ob = bpy.data.objects[name]
            ro = ac.render_alpha(scene, os.path.join(outdir, f"iou_render_{name}.png"), [ob], w, h) & ~visible_before
            visible_before |= ro
            cm_o = per[name].astype(bool)
            v = float((ro & cm_o).sum() / max((ro | cm_o).sum(), 1))
            data[f"iou_{name}"] = ac.r(v)
            checks.append(ac.check(f"iou.{name}", "pass" if v >= min_iou else "fail", ac.r(v), min_iou))
    ac.write_result(a.out, "iou_check", a.spec, checks, data)


if __name__ == "__main__":
    ac.run_main(main, "iou_check")
