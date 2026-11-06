"""Checks the intent of zps-concept-views: generated views must match one blockout and each other.
No image AI, no credits. Needs Blender; without it the test is skipped.

  python3 test_concept_views.py <zps-concept-views skill folder> [--keep]

1. Builds a small house blockout in Blender, renders its views, and checks the kit view
   convention: `left` shows the object's OWN left side (+X). A wrong convention mirrors the
   3D model of an asymmetric prop, and no silhouette check would catch it.
2. Renders a blockout from self-build style parts (--parts/--graph): materials come from the
   part labels, so the blockout is built once for both the views and the 3D self-build.
3. Measures a clean stand-in set (must pass) and a set with planted faults (each must be caught,
   and no correct view may be flagged).
Exit code 0 = all checks passed.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

SCRIPTS = os.path.join(os.path.abspath(sys.argv[1]), "scripts") if len(sys.argv) > 1 else ""

BUILD_HOUSE = r'''
import bpy, bmesh, sys
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def mat(n): return bpy.data.materials.get(n) or bpy.data.materials.new(n)
def box(name, loc, scale, m):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = scale; o.data.materials.append(mat(m))
box("walls", (0, 0, 1.0), (2, 1.5, 1.0), "wall")
box("door", (0, -1.52, 0.6), (0.35, 0.05, 0.6), "door")
box("win_f", (1.2, -1.52, 1.2), (0.3, 0.05, 0.3), "window")
box("win_back", (-0.8, 1.52, 1.2), (0.4, 0.05, 0.3), "window")
box("chimney", (-1.2, 0.5, 2.6), (0.2, 0.2, 0.6), "chimney")
box("sign", (2.06, 0, 1.0), (0.05, 0.4, 0.3), "sign")  # only on the object's own left (+X)
me = bpy.data.meshes.new("roof"); bm = bmesh.new()
v = [bm.verts.new(c) for c in [(-2.2,-1.7,2),(2.2,-1.7,2),(2.2,0,3),(-2.2,0,3),(-2.2,1.7,2),(2.2,1.7,2)]]
bm.faces.new([v[0],v[1],v[2],v[3]]); bm.faces.new([v[3],v[2],v[5],v[4]])
bm.faces.new([v[0],v[3],v[4]]); bm.faces.new([v[1],v[5],v[2]]); bm.faces.new([v[0],v[4],v[5],v[1]])
bm.to_mesh(me); o = bpy.data.objects.new("roof", me); bpy.context.collection.objects.link(o)
me.materials.append(mat("roof"))
bpy.ops.export_scene.gltf(filepath=sys.argv[-1])
'''
BUILD_PARTS = r'''
import bpy, json, os, sys
out = sys.argv[-1]; os.makedirs(out + "/parts", exist_ok=True)
for name, loc in (("body", (0, 0, 0.5)), ("handle_l", (0.6, 0, 0.5)), ("handle_r", (-0.6, 0, 0.5))):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(location=loc, size=0.5 if name != "body" else 1.0)
    bpy.ops.export_scene.gltf(filepath=f"{out}/parts/{name}.glb")
json.dump({"parts": [{"name": "body", "material": "wood"},
                     {"name": "handle_l", "material": "metal"},
                     {"name": "handle_r", "attach": {"type": "mirror_of", "of": "handle_l", "plane": "X"}}]},
          open(f"{out}/part_graph.json", "w"))
'''
BG = (232, 232, 232)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-2000:])
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    return p.stdout


def flat(blk, v):
    im = Image.open(f"{blk}/{v}_guide.png").convert("RGBA")
    c = Image.new("RGB", im.size, BG)
    c.paste(im, (0, 0), im)
    return c


def place(im, scale=1.0, size=(1024, 1024), off=(0, 0)):
    sx, sy = scale if isinstance(scale, tuple) else (scale, scale)
    im = im.resize((int(im.width * sx), int(im.height * sy)))
    c = Image.new("RGB", size, BG)
    c.paste(im, ((size[0] - im.width) // 2 + off[0], (size[1] - im.height) // 2 + off[1]))
    return c


def noisy(im, rng):
    a = np.array(im).astype(float)
    obj = np.linalg.norm(a - np.array(BG), axis=-1) > 40
    a[obj] += rng.normal(0, 25, (obj.sum(), 3))
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def measure(blk, gen, out):
    run([sys.executable, f"{SCRIPTS}/measure_views.py", "--blockout", blk, "--gen", gen, "--out", out,
         "--views", "front,back,left,right,top,bottom"])
    return json.load(open(f"{out}/report.json"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    ap.add_argument("--keep", action="store_true", help="keep the temp folder and print its path")
    a = ap.parse_args()
    mac = "/Applications/Blender.app/Contents/MacOS/Blender"
    a.blender = os.environ.get("BLENDER") or (mac if os.path.exists(mac) else shutil.which("blender"))
    if not a.blender:
        print("SKIP: Blender not found")
        sys.exit(0)
    tmp = tempfile.mkdtemp(prefix="zps5view_")
    blk, clean, bad = f"{tmp}/blk", f"{tmp}/gen_clean", f"{tmp}/gen_faults"
    os.makedirs(clean)
    os.makedirs(bad)
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))

    open(f"{tmp}/build_house.py", "w").write(BUILD_HOUSE)
    run([a.blender, "-b", "--python", f"{tmp}/build_house.py", "--", f"{tmp}/house.glb"])
    run([a.blender, "-b", "--python", f"{SCRIPTS}/render_blockout_views.py", "--",
         "--input", f"{tmp}/house.glb", "--out", blk, "--res", "768"])
    meta = json.load(open(f"{blk}/views.json"))
    check("render: 6 views x 2 passes + views.json",
          all(os.path.exists(f"{blk}/{v}_{k}.png") for v in meta["views"] for k in ("id", "guide")))
    idc = np.array(Image.open(f"{blk}/front_id.png").convert("RGBA"))
    found = {"#%02X%02X%02X" % tuple(c) for c in np.unique(idc[idc[..., 3] > 127][:, :3], axis=0)}
    check("render: ID colours are exact material colours", found <= set(meta["materials"].values()), str(found))
    sign = np.array([int(meta["materials"]["sign"][i:i + 2], 16) for i in (1, 3, 5)])
    seen = {v: bool((np.array(Image.open(f"{blk}/{v}_id.png").convert("RGB")) == sign).all(-1).sum() > 50)
            for v in ("left", "right")}
    check("convention: left view shows the object's own left side", seen == {"left": True, "right": False}, str(seen))

    open(f"{tmp}/build_parts.py", "w").write(BUILD_PARTS)
    run([a.blender, "-b", "--python", f"{tmp}/build_parts.py", "--", f"{tmp}/sb"])
    run([a.blender, "-b", "--python", f"{SCRIPTS}/render_blockout_views.py", "--", "--parts", f"{tmp}/sb/parts",
         "--graph", f"{tmp}/sb/part_graph.json", "--out", f"{tmp}/sb_views", "--res", "256"])
    pm = json.load(open(f"{tmp}/sb_views/views.json"))["materials"]
    check("parts: materials come from part labels (mirror_of inherits)", set(pm) == {"wood", "metal"}, str(sorted(pm)))

    # clean set, re-framed like an AI would (different scale/offset/canvas, one jpg)
    place(flat(blk, "front"), 0.9, off=(60, -40)).save(f"{clean}/front.png")
    place(flat(blk, "back"), 1.2, size=(1200, 900)).save(f"{clean}/back.png")
    for v in ("left", "right", "bottom"):
        place(flat(blk, v)).save(f"{clean}/{v}.png")
    place(flat(blk, "top")).save(f"{clean}/top.jpg", quality=85)
    r = measure(blk, clean, f"{tmp}/report_clean")
    check("clean set passes", r["overall_verdict"] == "pass" and not r["regen"],
          f"{r['overall_score']}/100 {r['overall_verdict']} regen={r['regen']}")

    # sheet round trip
    run([sys.executable, f"{SCRIPTS}/sheet.py", "make", "--dir", blk, "--out", f"{tmp}/sheet.png", "--bg", "#E8E8E8"])
    run([sys.executable, f"{SCRIPTS}/sheet.py", "split", "--sheet", f"{tmp}/sheet.png", "--out", f"{tmp}/gen_sheet"])
    r = measure(blk, f"{tmp}/gen_sheet", f"{tmp}/report_sheet")
    check("grid sheet make/split passes", r["overall_verdict"] == "pass", f"{r['overall_score']}/100")

    # planted faults
    rng = np.random.default_rng(0)
    pal = {k: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) for k, h in meta["materials"].items()}
    noisy(place(flat(blk, "front"), 0.9), rng).save(f"{bad}/front.png")
    place(flat(blk, "left"), (1.0, 1.12)).save(f"{bad}/left.png")                     # stretched
    rr = np.array(flat(blk, "right"))
    roof = (np.array(Image.open(f"{blk}/right_id.png").convert("RGB")) == pal["roof"]).all(-1)
    rr[roof] = (rr[roof] * [1.0, 0.55, 0.35]).astype(np.uint8)                           # roof recoloured
    noisy(place(Image.fromarray(rr)), rng).save(f"{bad}/right.png")
    ba = np.array(flat(blk, "back"))
    ids = np.array(Image.open(f"{blk}/back_id.png").convert("RGB"))
    ys, xs = np.where((ids == pal["window"]).all(-1))
    y0, y1, x0, x1 = ys.min() - 5, ys.max() + 6, xs.min() - 5, xs.max() + 6
    patch = ba[y0:y1, x0:x1].copy()
    ba[y0:y1, x0:x1] = np.median(ba[(ids == pal["wall"]).all(-1)], 0)
    ba[y0:y1, x0 - 260:x1 - 260] = patch                                                  # window moved
    noisy(place(Image.fromarray(ba), 1.2, size=(1200, 900)), rng).save(f"{bad}/back.png")
    noisy(place(flat(blk, "top")), rng).save(f"{bad}/top.png")
    place(flat(blk, "left")).save(f"{bad}/bottom.png")                                    # wrong view
    r = measure(blk, bad, f"{tmp}/report_faults")
    V = r["views"]
    check("fault: stretched left view", V["left"]["status"]["aspect_err"] == "fail", f"{V['left']['aspect_err']*100:+.1f}%")
    check("fault: right roof recoloured", r["colours"]["roof"]["views"]["right"]["status"] == "fail",
          f"dE {r['colours']['roof']['views']['right']['delta_e']:.1f}")
    check("fault: back window moved (on noisy texture)",
          V["back"]["detail_worst"] == "window" and V["back"]["status"]["detail"] == "fail", f"{V['back']['detail']:.2f}")
    check("fault: bottom is the wrong view", V["bottom"]["status"]["iou"] == "fail", f"IoU {V['bottom']['iou']:.2f}")
    tb = next(m for m in r["mirrors"] if m["pair"] == "top/bottom")
    check("fault: top/bottom mirror mismatch", tb["status"] == "fail", f"IoU {tb['iou']:.2f}")
    check("regen list = exactly the broken views", set(r["regen"]) == {"left", "right", "back", "bottom"}, str(r["regen"]))
    check("no false alarm on correct noisy views", V["front"]["verdict"] == "pass" and V["top"]["verdict"] == "pass",
          f"front {V['front']['verdict']}, top {V['top']['verdict']}")

    ok = all(checks)
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
    if a.keep:
        print(f"Files kept in {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
