"""Fixed review renders so every round is compared under the same camera/light.

Outputs (in --outdir, default <dirname of --out>/renders):
  game_<mode>.png         full screen at gameplay size from the game camera
  game_<mode>_crop.png    the asset region of that frame, unscaled (what the player sees)
  game_albedo_crop_2x.png the albedo crop enlarged 2x (nearest), for reading detail
  view<az>_<mode>.png     inspection views around the asset at the game elevation
  concept_compare.png     concept | albedo render from "ConceptCam" at concept size
                          (needs iou.concept in the spec and ConceptCam in the .blend)
  sheet.png               row 1: game crops at 1:1 gameplay size, then the same crops 2x (nearest)
                          in the free width | rows 2..: one row per mode
  + result JSON (--out) with camera data, measured pixel height and file list.

Camera (v0.2): built by ac_common.game_camera from spec.camera. With a fixed camera
(perspective + distance_m, or ortho + ortho_scale; look_at optional) the target_px_height
check is a real check. Without it the script calibrates: it solves distance (or ortho_scale)
so the target object is target_px_height tall, writes the solved numbers to data.camera,
and reports the check as info. Copy distance_m / ortho_scale and look_at into the spec;
better, take them from the engine.

Modes: clay (single colour, studio light), albedo (texture, flat light),
       lit (texture, studio light), checker (UV grid replaces materials).
All modes use Workbench so they run headless and stay deterministic; this is a
review aid, not the target-engine look (check that in the engine).

Spec: objects, floor_z, camera.{type, fov_v_deg | lens_mm, ortho_scale, distance_m, look_at,
  azimuth_deg, elevation_deg, screen:[w,h], target_object, target_px_height},
  render.{inspect_px (default 768), modes, floor (bool)}, iou.{concept, camera_object}.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402

import ac_common as ac  # noqa: E402


# kept for scripts that imported them from render_rig in v0.1
world_verts = ac.world_verts
place_camera = ac.place_camera
projected_box = ac.projected_box


def set_mode(scene, mode):
    sh = scene.display.shading
    sh.light = "FLAT" if mode == "albedo" else "STUDIO"
    sh.color_type = "SINGLE" if mode == "clay" else "TEXTURE"
    sh.single_color = (0.6, 0.6, 0.6)
    sh.show_cavity = mode == "clay"
    sh.show_shadows = False


def render(scene, path, w, h):
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 100
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def load_px(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    arr = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(img)
    return arr


def save_px(arr, path):
    h, w = arr.shape[:2]
    img = bpy.data.images.new("sheet", w, h, alpha=True)
    img.pixels = arr[::-1].ravel().tolist()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def main():
    a, spec = ac.parse_args([(("--outdir",), {"help": "render folder (default: <dirname of --out>/renders)"})])
    a.outdir = a.outdir or os.path.join(os.path.dirname(os.path.abspath(a.out)), "renders")
    os.makedirs(a.outdir, exist_ok=True)
    scene = bpy.context.scene
    objs = ac.target_objects(spec)
    cam_cfg = spec.get("camera", {})
    rcfg = spec.get("render", {})
    modes = rcfg.get("modes", ["clay", "albedo", "lit", "checker"])
    sw, shh = cam_cfg.get("screen", [1920, 1080])
    az = math.radians(cam_cfg.get("azimuth_deg", 0))
    el = math.radians(cam_cfg.get("elevation_deg", 40))
    floor_z = spec.get("floor_z", 0.0)

    for o in scene.objects:  # render only the asset (+ optional floor)
        if o not in objs:
            o.hide_render = True
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.view_settings.view_transform = "Standard"
    scene.render.film_transparent = False
    scene.world = scene.world or bpy.data.worlds.new("ac_world")
    scene.world.color = (0.18, 0.18, 0.2)

    floor = None
    if rcfg.get("floor", True):
        bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, floor_z))
        floor = bpy.context.active_object
        fm = bpy.data.materials.new("ac_floor")
        fm.diffuse_color = (0.35, 0.35, 0.35, 1)
        floor.data.materials.append(fm)

    cam, fixed = ac.game_camera(scene, cam_cfg, "ac_cam")
    cam_data = cam.data
    scene.camera = cam

    pts = world_verts(objs)
    lo, hi = ac.bbox(pts)
    center = ac.camera_target(cam_cfg, pts)
    radius = (hi - lo).length / 2
    tobj, target_note = ac.camera_target_object(cam_cfg, objs)
    tpts = world_verts([tobj])
    target_px = cam_cfg.get("target_px_height")
    ortho = cam_data.type == "ORTHO"

    # --- game view: fixed camera as given, or calibrate to target_px_height
    scene.render.resolution_x, scene.render.resolution_y = sw, shh
    dist = cam_cfg.get("distance_m", radius * 4)
    if ortho and "distance_m" not in cam_cfg:
        dist = radius * 4 + 10
    place_camera(cam, center, az, el, dist)
    if not fixed and target_px:
        for _ in range(8):
            x0, x1, y0, y1 = projected_box(scene, cam, tpts)
            m = (y1 - y0) * shh
            if ortho:
                cam_data.ortho_scale *= m / target_px
            else:
                dist *= m / target_px
            place_camera(cam, center, az, el, dist)
    x0, x1, y0, y1 = projected_box(scene, cam, tpts)
    measured = (y1 - y0) * shh
    x0, x1, y0, y1 = projected_box(scene, cam, pts)
    pad = 12
    crop = (max(0, int(x0 * sw) - pad), min(sw, int(math.ceil(x1 * sw)) + pad),
            max(0, int(y0 * shh) - pad), min(shh, int(math.ceil(y1 * shh)) + pad))

    files, checks = {}, []
    checker_mat = None

    def apply_checker():
        nonlocal checker_mat
        img = bpy.data.images.new("ac_checker", 1024, 1024)
        img.generated_type = "UV_GRID"
        checker_mat = bpy.data.materials.new("ac_checker")
        checker_mat.use_nodes = True
        nt = checker_mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
        nt.nodes.active = tex
        for o in objs:
            if not o.material_slots:
                o.data.materials.append(checker_mat)
            for s in o.material_slots:
                s.link = "OBJECT"
                s.material = checker_mat
        if floor:
            floor.hide_render = True

    game_crops = []
    ordered = [m for m in modes if m != "checker"] + (["checker"] if "checker" in modes else [])
    views = [(i, (math.degrees(az) + 90 * i) % 360) for i in range(4)]
    view_imgs = {}
    ip = rcfg.get("inspect_px", 768)
    for mode in ordered:
        if mode == "checker":
            apply_checker()
        set_mode(scene, mode)
        place_camera(cam, center, az, el, dist)
        p = os.path.join(a.outdir, f"game_{mode}.png")
        render(scene, p, sw, shh)
        full = load_px(p)
        c = full[shh - crop[3]:shh - crop[2], crop[0]:crop[1]]
        cp = os.path.join(a.outdir, f"game_{mode}_crop.png")
        save_px(c, cp)
        files[f"game_{mode}"] = [p, cp]
        game_crops.append(c)
        # inspection views: frame whole asset tightly at the game elevation
        for i, deg in views:
            idist = radius * 4
            scene.render.resolution_x = scene.render.resolution_y = ip
            for _ in range(6):  # fill ~85% of the square frame
                place_camera(cam, center, math.radians(deg), el, idist)
                x0_, x1_, y0_, y1_ = projected_box(scene, cam, pts)
                extent = 2 * max(abs(x0_ - .5), abs(x1_ - .5), abs(y0_ - .5), abs(y1_ - .5))
                idist *= extent / 0.85  # off-centre safe: farthest edge stays inside
            vp = os.path.join(a.outdir, f"view{int(deg):03d}_{mode}.png")
            render(scene, vp, ip, ip)
            files[f"view{int(deg):03d}_{mode}"] = vp
            view_imgs[(mode, i)] = load_px(vp)

    # --- contact sheet
    # row 0: game crops at 1:1 gameplay size, then the same crops 2x (nearest) in the width the
    # 1:1 crops leave free (they are much narrower than the 4 inspection views below)
    rows = []
    gh = max(x.shape[0] for x in game_crops)
    row = np.full((gh * 2, ip * 4, 4), (0.18, 0.18, 0.2, 1), np.float32)
    xo, row0 = 0, []
    for scale in (1, 2):
        for mode, g in zip(ordered, game_crops):
            g2 = g if scale == 1 else np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)
            if xo + g2.shape[1] > ip * 4:
                break
            row[:g2.shape[0], xo:xo + g2.shape[1]] = g2
            row0.append(f"game_{mode}_crop {'1:1 gameplay size' if scale == 1 else '2x nearest'}")
            xo += g2.shape[1] + 8
        xo += 24
    used_h = gh * 2 if any("2x" in t for t in row0) else gh
    rows.append(row[:used_h])
    for mode in ordered:
        rows.append(np.concatenate([view_imgs[(mode, i)] for i, _ in views], axis=1))
    sheet = np.concatenate(rows, axis=0)
    sp = os.path.join(a.outdir, "sheet.png")
    save_px(sheet, sp)
    files["sheet"] = sp

    # --- 2x albedo crop and concept | render comparison
    import cv2
    if "albedo" in ordered:
        src = os.path.join(a.outdir, "game_albedo_crop.png")
        im = cv2.imread(src, cv2.IMREAD_UNCHANGED)
        p2 = os.path.join(a.outdir, "game_albedo_crop_2x.png")
        cv2.imwrite(p2, cv2.resize(im, (im.shape[1] * 2, im.shape[0] * 2), interpolation=cv2.INTER_NEAREST))
        files["game_albedo_crop_2x"] = p2
    icfg = spec.get("iou", {})
    ccam = bpy.data.objects.get(icfg.get("camera_object", "ConceptCam"))
    if icfg.get("concept") and ccam is not None and "albedo" in ordered:
        concept = ac._read_image(ac.spec_path(a.spec, icfg["concept"]))
        ch, cw = concept.shape[:2]
        for o in objs:  # restore real materials if the checker pass replaced them
            for sl in o.material_slots:
                if sl.link == "OBJECT":
                    sl.link = "DATA"
        if floor:
            floor.hide_render = True
        set_mode(scene, "albedo")
        scene.camera = ccam
        scene.render.film_transparent = True
        rp = os.path.join(a.outdir, "concept_view_albedo.png")
        render(scene, rp, cw, ch)
        scene.render.film_transparent = False
        scene.camera = cam

        def on_white(img):
            if img.shape[2] == 4:
                al = img[:, :, 3:4].astype(np.float32) / 255
                return (img[:, :, :3] * al + 255 * (1 - al)).astype(np.uint8)
            return img
        ren = on_white(cv2.imread(rp, cv2.IMREAD_UNCHANGED))
        gap = np.full((ch, 8, 3), 128, np.uint8)
        cp2 = os.path.join(a.outdir, "concept_compare.png")
        cv2.imwrite(cp2, np.concatenate([on_white(concept), gap, ren], axis=1))
        files["concept_compare"] = cp2
    else:
        why = [w for w, bad in (("no ConceptCam camera in the scene", ccam is None),
                                ("no iou.concept in the spec", not icfg.get("concept")),
                                ("albedo mode not rendered", "albedo" not in ordered)) if bad]
        checks.append(ac.check("concept_compare", "not_checked",
                               note="skipped: " + "; ".join(why) + ". Concept vs model for the build/optimize "
                                    "paths: overlays from self_build render_views / optimize gate1"))

    if target_px:
        if fixed:
            ok = abs(measured - target_px) / target_px <= 0.05
            checks.append(ac.check("game_view.target_px_height", "pass" if ok else "fail",
                                   ac.r(measured, 1), target_px))
        else:
            checks.append(ac.check("game_view.target_px_height", "info", ac.r(measured, 1), target_px,
                                   note="calibration mode: camera solved to hit the target; copy "
                                        "data.camera distance_m/ortho_scale and look_at into the spec"))
    else:
        checks.append(ac.check("game_view.target_px_height", "info", ac.r(measured, 1),
                               note="no target_px_height in spec"))
    engine = spec.get("engine")
    real_engine = engine in ("unity", "godot", "unreal")
    checks.append(ac.check("renders", "info", len(files),
                           note=f"review aid only; Workbench is not the {engine.capitalize()} look"
                           if real_engine else "review aid only (Workbench)"))
    data = {"camera": {"mode": "fixed" if fixed else "calibration",
                       "type": "ortho" if ortho else "persp",
                       "azimuth_deg": math.degrees(az), "elevation_deg": math.degrees(el),
                       "fov_v_deg": ac.r(math.degrees(cam_data.angle_y), 3),
                       "lens_mm": ac.r(cam_data.lens, 3),
                       "ortho_scale": ac.r(cam_data.ortho_scale) if ortho else None,
                       "distance_m": ac.r(dist), "look_at": [ac.r(v) for v in center],
                       "screen": [sw, shh], "crop_px": crop},
            "sheet_layout": {"row0": row0,
                             "rows": ordered, "columns_azimuth_deg": [d for _, d in views]},
            "files": files}
    if target_note:
        data["camera"]["target_note"] = target_note
        data["warnings"] = [target_note]
    ac.write_result(a.out, "render_rig", a.spec, checks, data)


if __name__ == "__main__":
    ac.run_main(main, "render_rig")
