"""How much of what the player sees comes from surfaces the concept actually shows.

A face counts as "from concept" when all three hold, seen from the concept camera:
  - its normal faces the camera (dot >= facing_max),
  - its centre is not hidden by another face (ray cast from the camera),
  - its centre projects inside the concept frame.
Everything else is fill (for M1: tile; for other methods: invented by the artist). The script
renders the game camera view with that classification and reports the visible share.
Use it to judge risk, not as a pass mark on its own; a threshold is applied only when the
task sets coverage.min_visible.

Classification uses the base mesh (before modifiers); apply modifiers before measuring.

The concept frame size is read from iou.concept when present (else the scene render size).

Spec: objects, camera (same keys as render_rig: type, fov_v_deg or lens_mm, ortho_scale,
  distance_m, look_at, azimuth_deg, elevation_deg, screen), coverage.{camera_object
  (default "ConceptCam"), facing_max (0.45), min_visible (optional), azimuths (default
  [game azimuth])}.
Camera is fixed when perspective has distance_m, or ortho has ortho_scale; otherwise the
asset is framed (calibration mode, numbers are info only).
No coverage block or no concept camera in the scene: check `coverage` not_checked.
Outputs: result JSON and coverage_<az>.png (white = from concept, red = fill) next to --out.
The game camera comes from ac_common.game_camera (same as render_rig).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import bootstrap  # noqa: E402,F401  (tools/.deps/blender-py<ver> on sys.path; before third-party imports)
import bpy  # noqa: E402
import cv2  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402

import ac_common as ac  # noqa: E402


def from_concept(scene, depsgraph, ccam, objs, fmax):
    """Per object: list of booleans per polygon (True = shown by the concept)."""
    cdir = (ccam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    ortho = ccam.data.type == "ORTHO"
    cpos = ccam.matrix_world.translation
    res = {}
    for o in objs:
        mw = o.matrix_world
        nm = mw.to_3x3().inverted().transposed()
        flags = []
        for poly in o.data.polygons:
            n = (nm @ poly.normal).normalized()
            if n.dot(-cdir) < fmax:
                flags.append(False)
                continue
            c = mw @ poly.center
            v = world_to_camera_view(scene, ccam, c)
            if not (0.0 <= v.x <= 1.0 and 0.0 <= v.y <= 1.0):
                flags.append(False)
                continue
            if ortho:
                origin, direction = c - cdir * 1000.0, cdir
            else:
                origin, direction = cpos, (c - cpos).normalized()
            dist = (c - origin).length
            hit, loc, _n, idx, hob, _m = scene.ray_cast(depsgraph, origin, direction, distance=dist + 1e-3)
            visible = (not hit) or (hob.original == o and idx == poly.index) or (loc - c).length < 1e-3
            flags.append(bool(visible))
        res[o.name] = flags
    return res


def main():
    a, spec = ac.parse_args()
    cfg = spec.get("coverage", {})
    scene = bpy.context.scene
    cname = cfg.get("camera_object", "ConceptCam")
    if not cfg or cname not in bpy.data.objects:
        why = "spec has no coverage block" if not cfg else f"camera object '{cname}' not in the scene"
        ac.write_result(a.out, "concept_coverage", a.spec,
                        [ac.check("coverage", "not_checked",
                                  note=f"{why}; coverage needs a concept camera (ConceptCam) matching the concept")])
        return
    ccam = bpy.data.objects[cname]
    fmax = cfg.get("facing_max", 0.45)
    objs = ac.target_objects(spec)

    # the "inside concept frame" test uses the render aspect: set it to the concept image size
    concept_rel = spec.get("iou", {}).get("concept")
    frame_note = "scene render size"
    if concept_rel:
        cimg = cv2.imread(ac.spec_path(a.spec, concept_rel))
        if cimg is not None:
            scene.render.resolution_x, scene.render.resolution_y = cimg.shape[1], cimg.shape[0]
            frame_note = "concept image size"
    depsgraph = bpy.context.evaluated_depsgraph_get()
    flags = from_concept(scene, depsgraph, ccam, objs, fmax)
    for o in objs:
        me = o.data
        attr = me.color_attributes.get("ac_cov") or me.color_attributes.new("ac_cov", "BYTE_COLOR", "CORNER")
        for poly, ok in zip(me.polygons, flags[o.name]):
            col = (1, 1, 1, 1) if ok else (1, 0, 0, 1)
            for li in poly.loop_indices:
                attr.data[li].color = col
        me.color_attributes.active_color = attr

    cam_cfg = spec.get("camera", {})
    sw, sh_ = cam_cfg.get("screen", [1920, 1080])
    cam, fixed = ac.game_camera(scene, cam_cfg, "ac_cov_cam")
    cam_data = cam.data
    scene.camera = cam
    pts = ac.world_verts(objs)
    lo, hi = ac.bbox(pts)
    center = ac.camera_target(cam_cfg, pts)
    dist = cam_cfg.get("distance_m", (hi - lo).length * 2)
    el = math.radians(cam_cfg.get("elevation_deg", 40))

    for o in scene.objects:
        if o.type == "MESH":
            o.hide_render = o not in objs
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "FLAT"
    sh.color_type = "VERTEX"
    scene.view_settings.view_transform = "Standard"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = sw, sh_
    outdir = os.path.dirname(os.path.abspath(a.out))
    checks, data = [], {"camera_mode": "fixed" if fixed else "framed", "facing_max": fmax,
                        "occlusion": "ray_cast_from_concept_camera", "concept_frame": frame_note}
    for az_deg in cfg.get("azimuths", [cam_cfg.get("azimuth_deg", 0)]):
        az = math.radians(az_deg)
        ac.place_camera(cam, center, az, el, dist)
        if not fixed:  # frame the asset when no real game camera is given
            x0, x1, y0, y1 = ac.projected_box(scene, cam, pts)
            ext = 2 * max(abs(x0 - .5), abs(x1 - .5), abs(y0 - .5), abs(y1 - .5))
            if cam_data.type == "ORTHO":
                cam_data.ortho_scale *= ext / 0.85
            else:
                dist *= ext / 0.85
            ac.place_camera(cam, center, az, el, dist)
        p = os.path.join(outdir, f"coverage_{int(az_deg):03d}.png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        vis = im[:, :, 3] > 127
        white = vis & (im[:, :, 1] > 127)
        share = float(white.sum() / max(vis.sum(), 1))
        data[f"azimuth_{int(az_deg)}"] = {"visible_from_concept": ac.r(share, 3), "visible_px": int(vis.sum())}
        mv = cfg.get("min_visible")
        status = ("pass" if share >= mv else "fail") if (mv is not None and fixed) else "info"
        checks.append(ac.check(f"coverage.az{int(az_deg)}", status, ac.r(share, 3), mv,
                               note=None if fixed else "camera not fixed: info only"))
    ac.write_result(a.out, "concept_coverage", a.spec, checks, data)


if __name__ == "__main__":
    ac.run_main(main, "concept_coverage")
