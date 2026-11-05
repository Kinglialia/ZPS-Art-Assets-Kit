"""Sweep simplification levels, measure each, pick one (optimize.md §4-6). Pure Python; runs
gltfpack and the Blender Decimate fallback (decimate.py) as subprocesses.

Usage:
  python3 tools/optimize/sweep.py --work <w> [--spec task/spec.json] [--input <w>/ref_high.glb]
         [--budget N | --auto | --calibrate] [--engine gltfpack|blender] [--refine N]
         [--out <w>/sweep.json]

Mode: --budget N, else spec budget.mode == "budget" with budget.max_tris_total, else auto.
Levels:
  auto       every ratio in optimize.sweep_ratios, then sweep.refine_steps bisection steps (on a
             log scale) between the lowest passing ratio and the next lower ratio. When even the
             lowest listed ratio passes (dense remeshed refs), the ratio is halved until a level
             fails (not below sweep.min_tris), then bisected.
  budget     ratio = N / ref tris. If gltfpack stops above N (its -se error limit), it is re-run
             with -se 1, then Blender is used to hit N. If that level fails the floor, sweep ratios
             above it are tried in ascending order until one passes, then bisection refines
             min_pass between the last failing and the first passing ratio.
  calibrate  every sweep ratio, all level files kept, nothing chosen.
Engine: `gltfpack -i ref -o level -si R -se optimize.gltfpack_error -noq` (+ -sp when
cleanup.json says rebake and optimize.permissive_when_rebake; + -slb when optimize.lock_border).
gltfpack welds identical vertices first. When gltfpack is missing or fails, decimate.py (merge by
distance, then Decimate COLLAPSE) runs instead and warnings get "engine_fallback". The achieved
triangle count is read from the output, since gltfpack may stop early. gltfpack drops node and
mesh names; sweep writes audit's data.output_object (the asset name) back into the level's JSON
(optlib.name_single_mesh). Not -kn: it changes gltfpack's result (barrel at ratio 0.15: Hausdorff
0.86 -> 1.04 px at the same 4544 tris).
Repair: every level, either engine, gets optlib.repair_glb before it is measured (zero-area caps
split into their neighbour, collapsed needles dropped, winding made consistent; index buffers
only, UVs and textures untouched); counts in curve[].repair. measure.py's validity floors then
reject a level that still has degenerate faces or more non-manifold / winding-inconsistent edges
than the reference.
Every level is measured by measure.py (same JSON, <w>/measure/level_<ratio>_<engine>.json).
Pick:
  auto       lowest tri count passing every optimize.floor metric. Kneedle (kneed: convex,
             decreasing, S = optimize.knee_sensitivity) on (log10 tris, 1 - worst IoU) of the
             Pareto front of all measured levels gives knee_tris as a cross-check; the floor
             wins when the knee is lower.
  budget     the budget level is final_budget; when it fails, the lowest passing level is
             final_min_pass.
  At each chosen level the other engine runs at the same triangle count; the better result
  (pass, then - with UVs kept - texture error p95 beyond sweep.texture_error_tie, then
  worst-view IoU, then Hausdorff) is kept (engine_winner). When the other engine
  wins, the search continues down the sweep ratios with it (then bisection), so the result is
  the fewest tris either engine can pass with (extension of optimize.md §6).
Writes <w>/sweep.json, <w>/curve.png (1 - worst IoU and Hausdorff px vs tris, log x, floor, knee,
chosen and budget marked) and <w>/selected_<auto|budget|min_pass>.glb.

Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import measure as measure_mod  # noqa: E402
import optlib  # noqa: E402
from optlib import common  # noqa: E402

TOOL = "optimize/sweep"


def parse():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--work", required=True)
    p.add_argument("--spec")
    p.add_argument("--input")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--budget", type=int)
    g.add_argument("--auto", action="store_true")
    g.add_argument("--calibrate", action="store_true")
    p.add_argument("--engine", choices=["gltfpack", "blender"])
    p.add_argument("--refine", type=int)
    p.add_argument("--out")
    a = p.parse_args(common.script_argv())
    a.input = a.input or os.path.join(a.work, "ref_high.glb")
    a.out = a.out or os.path.join(a.work, "sweep.json")
    return a


class Sweep:
    def __init__(self, a, cfg, spec):
        self.a, self.cfg, self.spec = a, cfg, spec
        self.ocfg = cfg["optimize"]
        self.work = a.work
        self.levels = []
        self.warnings = []
        self.ref_tris = optlib.glb_tri_count(a.input)
        self.ref = measure_mod.Reference(a.input, cfg)
        cl = os.path.join(a.work, "cleanup.json")
        self.rebake = bool(common.read_json(cl)["data"].get("rebake")) if os.path.isfile(cl) else False
        self.gltfpack = self._find_gltfpack()
        self.name = optlib.output_object(a.work)   # asset name audit gave the joined object
        self.primary = a.engine or self.ocfg["engine"]
        self.fallback = self.ocfg.get("fallback")
        os.makedirs(os.path.join(a.work, "sweep"), exist_ok=True)
        os.makedirs(os.path.join(a.work, "measure"), exist_ok=True)

    def _find_gltfpack(self):
        exe = shutil.which(self.cfg["paths"].get("gltfpack") or "gltfpack")
        if not exe:
            self.warnings.append("engine_fallback: gltfpack not found on PATH; Blender Decimate used")
            return None
        if optlib.run([exe, "-v"], 30).returncode not in (0, 1):
            self.warnings.append(f"engine_fallback: {exe} -v failed; Blender Decimate used")
            return None
        return exe

    # ------------------------------------------------------------ building levels
    def _paths(self, ratio, engine, suffix=""):
        tag = f"level_{ratio:.4f}_{engine}{suffix}"
        return (os.path.join(self.work, "sweep", tag + ".glb"),
                os.path.join(self.work, "measure", tag + ".json"), tag)

    def _gltfpack(self, ratio, out, se):
        if not self.gltfpack:
            return None, "gltfpack unavailable"
        cmd = [self.gltfpack, "-i", self.a.input, "-o", out, "-si", f"{min(ratio, 1.0):.6f}",
               "-se", f"{se}", "-noq"]
        if self.rebake and self.ocfg["permissive_when_rebake"]:
            cmd.append("-sp")
        if self.ocfg["lock_border"]:
            cmd.append("-slb")
        res = optlib.run(cmd, self.cfg["sweep"]["timeout_s"])
        if res.returncode != 0 or not os.path.isfile(out):
            return None, f"gltfpack exit {res.returncode}: {optlib.tail(res.stderr or res.stdout, 5)}"
        return cmd, None

    def _blender(self, target_tris, out):
        args = ["--input", self.a.input, "--output", out, "--target-tris", str(int(target_tris)),
                "--out", os.path.splitext(out)[0] + ".decimate.json"]
        if self.a.spec:
            args += ["--spec", self.a.spec]
        cmd = optlib.blender_cmd(self.cfg, os.path.join(HERE, "decimate.py"), args)
        if cmd is None:
            return None, "no Blender binary and no bpy module"
        res = optlib.run(cmd, self.cfg["sweep"]["timeout_s"])
        if res.returncode != 0 or not os.path.isfile(out):
            return None, f"decimate.py exit {res.returncode}: {optlib.tail(res.stderr or res.stdout, 5)}"
        return cmd, None

    def make(self, ratio, engine, target_tris=None, se=None, suffix="", role=None):
        """Build one level with one engine and measure it. Returns the level dict or None."""
        target = int(round(target_tris if target_tris else ratio * self.ref_tris))
        se = self.ocfg["gltfpack_error"] if se is None else se
        out, mjson, tag = self._paths(ratio, engine, suffix)
        if engine == "gltfpack":
            cmd, err = self._gltfpack(ratio, out, se)
        else:
            cmd, err = self._blender(target, out)
        if err:
            return {"error": err}
        try:
            rep = optlib.repair_glb(out)
        except Exception as exc:  # noqa: BLE001  an unrepaired level is still measured (validity floors)
            rep = {"skipped": repr(exc)}
            self.warnings.append(f"repair failed on {tag}: {exc!r}")
        if self.name:
            optlib.name_single_mesh(out, self.name)
        m = measure_mod.measure(self.ref, out, self.cfg, mjson, spec_path=self.a.spec)
        lv = {"tag": tag, "ratio": round(ratio, 6), "engine": engine, "target_tris": target,
              "tris": m["tris"], "file": out, "measure": mjson,
              "iou_worst": m["iou_worst"], "iou_mean": m["iou_mean"], "hausdorff_px": m["hausdorff_px"],
              "mean_dist_px": m["mean_dist_px"], "hausdorff_frac_diag": m["hausdorff_frac_diag"],
              "normal_dev_p95_deg": m["normal_dev_p95_deg"], "texture_error_p95": m["texture_error_p95"],
              "pass": m["pass"], "fails": m["fails"], "repair": rep, "validity": m["validity"]}
        if engine == "gltfpack":
            lv["gltfpack_se"] = se
            lv["stopped_early"] = m["tris"] > target * 1.02 + 2
        if role:
            lv["role"] = role
        self.levels.append(lv)
        tex = "" if m["texture_error_p95"] is None else f"  tex95={m['texture_error_p95']}"
        print(f"  {tag}: {m['tris']} tris  iou_worst={m['iou_worst']}  haus={m['hausdorff_px']}px  "
              f"n95={m['normal_dev_p95_deg']}{tex}  {'PASS' if m['pass'] else 'fail ' + ','.join(m['fails'])}")
        return lv

    def build(self, ratio, target_tris=None, suffix=""):
        """Primary engine, then the fallback engine with an engine_fallback warning."""
        engines = [self.primary] + ([self.fallback] if self.fallback and self.fallback != self.primary else [])
        for i, eng in enumerate(engines):
            lv = self.make(ratio, eng, target_tris, suffix=suffix)
            if "error" not in lv:
                if i > 0:
                    self.warnings.append(f"engine_fallback: ratio {ratio:.4f} built with {eng}")
                return lv
            self.warnings.append(f"{eng} failed at ratio {ratio:.4f}: {lv['error']}")
        raise RuntimeError(f"no engine could build ratio {ratio}")

    def build_budget(self, budget):
        ratio = min(1.0, budget / self.ref_tris)
        lv = self.build(ratio, budget)
        if lv["tris"] > budget and lv["engine"] == "gltfpack":
            self.warnings.append(f"gltfpack stopped at {lv['tris']} > budget {budget} "
                                 f"(-se {self.ocfg['gltfpack_error']}); re-run with -se 1")
            relaxed = self.make(ratio, "gltfpack", budget, se=1.0, suffix="_se1")
            if "error" not in relaxed:
                lv = relaxed
        if lv["tris"] > budget:
            self.warnings.append(f"gltfpack cannot reach {budget} tris (stops at {lv['tris']}, seams or "
                                 "error limit); Blender Decimate used for the budget level")
            b = self.make(ratio, "blender", budget, suffix="_budget")
            if "error" not in b:
                lv = b
        return lv

    def refine(self, lo_ratio, hi_level, steps, engine=None):
        """Bisect (log scale) between a failing ratio and a passing level; returns the lowest
        passing level found. engine=None: primary engine with fallback."""
        best = hi_level
        lo, hi = lo_ratio, hi_level["ratio"]
        for _ in range(steps):
            mid = math.sqrt(lo * hi)
            if hi / lo < 1.05:
                break
            lv = self.build(mid) if engine is None else self.make(mid, engine, suffix="_descend")
            if "error" in lv:
                break
            if lv["pass"] and lv["tris"] < best["tris"]:
                best, hi = lv, mid
            elif lv["pass"]:
                hi = mid
            else:
                lo = mid
        return best

    def extend_below(self, lv, steps, engine=None):
        """lv passes and no listed ratio is lower: halve the ratio until a level fails (or the
        mesh would drop under sweep.min_tris), then bisect. Returns the lowest passing level."""
        best, r = lv, lv["ratio"] / 2
        while r * self.ref_tris >= self.cfg["sweep"]["min_tris"]:
            nxt = self.build(r, suffix="_ext") if engine is None else self.make(r, engine, suffix="_ext")
            if "error" in nxt:
                return best
            if not nxt["pass"]:
                return self.refine(r, best, steps, engine) if steps else best
            if nxt["tris"] < best["tris"]:
                best = nxt
            r /= 2
        return best

    def descend(self, lv, ratios, steps):
        """After the cross-check picked lv's engine over the primary one: keep stepping down the
        sweep ratios with that engine while the floor passes, then bisect. Returns the lowest
        passing level of that engine (lv itself when nothing lower passes)."""
        eng, best, lo = lv["engine"], lv, None
        for r in sorted((x for x in ratios if x * self.ref_tris < lv["tris"]), reverse=True):
            nxt = self.make(r, eng, suffix="_descend")
            if "error" in nxt:
                break
            if not nxt["pass"]:
                lo = r
                break
            best = nxt
        if lo is None:
            return self.extend_below(best, steps, eng)
        if steps:
            best = self.refine(lo, best, steps, eng)
        return best

    def other_engine(self, lv):
        """Run the other engine at lv's triangle count; return the better level."""
        other = "blender" if lv["engine"] == "gltfpack" else "gltfpack"
        if other == "gltfpack" and not self.gltfpack:
            return lv, {"engine": other, "skipped": "gltfpack unavailable"}
        alt = self.make(lv["tris"] / self.ref_tris, other, lv["tris"], suffix="_xcheck")
        if "error" in alt:
            return lv, {"engine": other, "skipped": alt["error"]}

        win, why = self.better(lv, alt)
        return win, {"engine": other, "tris": alt["tris"], "iou_worst": alt["iou_worst"],
                     "hausdorff_px": alt["hausdorff_px"], "texture_error_p95": alt["texture_error_p95"],
                     "pass": alt["pass"], "winner": win["engine"], "why": why}

    def better(self, a, b):
        """Pass beats fail; with UVs kept, clearly lower texture error p95 wins (a simplifier that
        smears UVs loses even with better geometry); then worst-view IoU (4 decimals), then
        Hausdorff. Returns (winner, reason)."""
        if a["pass"] != b["pass"]:
            w = a if a["pass"] else b
            return w, "only one passes the floor"
        ta, tb = a.get("texture_error_p95"), b.get("texture_error_p95")
        if not self.rebake and ta is not None and tb is not None and abs(ta - tb) > self.cfg["sweep"]["texture_error_tie"]:
            w = a if ta < tb else b
            return w, f"UVs kept: texture error p95 {min(ta, tb)} vs {max(ta, tb)}"
        ia, ib = round(a["iou_worst"], 4), round(b["iou_worst"], 4)
        if ia != ib:
            return (a, "higher worst-view IoU") if ia > ib else (b, "higher worst-view IoU")
        return (a, "lower Hausdorff") if a["hausdorff_px"] <= b["hausdorff_px"] else (b, "lower Hausdorff")

    # ------------------------------------------------------------ knee
    def pareto(self):
        """Levels no other level beats on both tris and worst IoU (both engines), by tris."""
        front, best_err = [], float("inf")
        for lv in sorted(self.levels, key=lambda x: (x["tris"], -x["iou_worst"])):
            err = 1 - lv["iou_worst"]
            if err < best_err:
                front.append(lv)
                best_err = err
        return front

    def knee(self):
        """Kneedle on the Pareto front: (log10 tris, 1 - worst IoU), convex, decreasing."""
        front = self.pareto()
        if len(front) < 3:
            return None, "fewer than 3 Pareto levels"
        try:
            from kneed import KneeLocator
        except ImportError:
            self.warnings.append("kneed not installed: no knee cross-check")
            return None, "kneed missing"
        x = np.log10(np.array([lv["tris"] for lv in front], float))
        y = np.array([1 - lv["iou_worst"] for lv in front], float)
        kl = KneeLocator(x, y, curve="convex", direction="decreasing", S=self.ocfg["knee_sensitivity"])
        if kl.knee is None:
            return None, "no knee found"
        return int(round(10 ** kl.knee)), None


# ---------------------------------------------------------------- curve image
def draw_curve(levels, floor, path, knee=None, marks=()):
    """PNG of 1 - worst IoU (blue, left axis) and Hausdorff px (orange, right axis) vs tris
    (log x), one line per engine (gltfpack solid, blender dashed). Points: circle = IoU error,
    square = Hausdorff; green passes the floor, red fails. Values far above the floor are drawn
    on the top edge with their value. marks: (tris, label, rgb). PIL only (no matplotlib)."""
    from PIL import Image, ImageDraw, ImageFont
    W, H, L, R, T, B = 1000, 600, 80, 80, 60, 70
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    tris_all = np.array([p["tris"] for p in levels], float)
    err_all = np.array([1 - p["iou_worst"] for p in levels])
    haus_all = np.array([p["hausdorff_px"] for p in levels])
    x0, x1 = math.log10(tris_all.min() * 0.8), math.log10(tris_all.max() * 1.25)
    e_floor, h_floor = 1 - floor["silhouette_iou_min"], floor["hausdorff_max_px"]
    e_max = max(e_floor * 3, float(np.percentile(err_all, 75))) * 1.15
    h_max = max(h_floor * 3, float(np.percentile(haus_all, 75))) * 1.15
    blue, orange = (30, 80, 200), (220, 110, 0)

    def X(t):
        return L + (math.log10(t) - x0) / (x1 - x0) * (W - L - R)

    def Y(val, vmax):
        return H - B - min(val, vmax) / vmax * (H - T - B)

    d.rectangle([L, T, W - R, H - B], outline="black")
    for dec in range(int(math.floor(x0)), int(math.ceil(x1)) + 1):
        for m in (1, 2, 3, 5, 7):
            t = m * 10 ** dec
            if x0 <= math.log10(t) <= x1:
                d.line([X(t), T, X(t), H - B], fill=(232, 232, 232))
                d.text((X(t) - 12, H - B + 6), f"{t:g}", fill="black", font=font)
    for i in range(6):
        d.text((8, Y(e_max * i / 5, e_max) - 7), f"{e_max * i / 5:.4f}", fill=blue, font=font)
        d.text((W - R + 8, Y(h_max * i / 5, h_max) - 7), f"{h_max * i / 5:.2f}", fill=orange, font=font)

    def dashed(x_a, y_a, x_b, y_b, col, width=1, on=6, off=5):
        n = max(1, int(math.hypot(x_b - x_a, y_b - y_a) // (on + off)))
        for k in range(n):
            t0, t1 = k / n, min(1.0, k / n + on / (on + off) / n)
            d.line([x_a + (x_b - x_a) * t0, y_a + (y_b - y_a) * t0,
                    x_a + (x_b - x_a) * t1, y_a + (y_b - y_a) * t1], fill=col, width=width)

    d.line([L, Y(e_floor, e_max), W - R, Y(e_floor, e_max)], fill=blue)
    d.text((L + 4, Y(e_floor, e_max) - 16), f"IoU floor {floor['silhouette_iou_min']}", fill=blue, font=font)
    dashed(L, Y(h_floor, h_max), W - R, Y(h_floor, h_max), orange)
    d.text((W - R - 160, Y(h_floor, h_max) - 16), f"Hausdorff floor {h_floor} px", fill=orange, font=font)

    for eng in sorted({p["engine"] for p in levels}):
        pts = sorted((p for p in levels if p["engine"] == eng), key=lambda p: p["tris"])
        for series, vmax, col in (([1 - p["iou_worst"] for p in pts], e_max, blue),
                                  ([p["hausdorff_px"] for p in pts], h_max, orange)):
            xy = [(X(p["tris"]), Y(v, vmax)) for p, v in zip(pts, series)]
            for (xa, ya), (xb, yb) in zip(xy, xy[1:]):
                if eng == "gltfpack":
                    d.line([xa, ya, xb, yb], fill=col, width=2)
                else:
                    dashed(xa, ya, xb, yb, col, 2)
    for p in levels:
        c = (20, 160, 60) if p["pass"] else (210, 30, 30)
        e, h, xx = 1 - p["iou_worst"], p["hausdorff_px"], X(p["tris"])
        d.ellipse([xx - 5, Y(e, e_max) - 5, xx + 5, Y(e, e_max) + 5], fill=c, outline="black")
        d.rectangle([xx - 4, Y(h, h_max) - 4, xx + 4, Y(h, h_max) + 4], fill=c, outline="black")
        if e > e_max:
            d.text((xx + 6, T + 2), f"IoU {p['iou_worst']:.3f}", fill=blue, font=font)
        if h > h_max:
            d.text((xx + 6, T + 16), f"{h:.1f}px", fill=orange, font=font)
    allm = list(marks) + ([(knee, "knee", (150, 40, 170))] if knee else [])
    for k, (t, label, col) in enumerate(allm):
        if t:
            dashed(X(t), T, X(t), H - B, col, 2, 4, 4)
            d.text((X(t) + 4, T + 34 + 16 * k), f"{label} {t}", fill=col, font=font)
    d.text((L, 12), "blue circles: 1 - worst-view IoU (left axis)   orange squares: Hausdorff px (right axis)",
           fill="black", font=font)
    d.text((L, 30), "green = passes floor, red = fails   solid line = gltfpack, dashed = blender",
           fill="black", font=font)
    d.text((W / 2 - 40, H - 30), "triangles (log)", fill="black", font=font)
    img.save(path)


def main(a):
    cfg, spec = optlib.settings(a.spec)
    ocfg = cfg["optimize"]
    sw = Sweep(a, cfg, spec)
    budget = a.budget
    sb = spec.get("budget") or {}
    if budget is None and not a.auto and not a.calibrate and sb.get("mode") == "budget":
        budget = sb.get("max_tris_total")
    mode = "calibrate" if a.calibrate else ("budget" if budget else "auto")
    refine_steps = cfg["sweep"]["refine_steps"] if a.refine is None else a.refine
    ratios = sorted(set(float(r) for r in ocfg["sweep_ratios"]), reverse=True)
    print(f"[sweep] mode={mode} ref_tris={sw.ref_tris} rebake={sw.rebake} engine={sw.primary}")

    selected, xchecks, keep = {}, {}, set()
    reason, knee, knee_note = "", None, None
    budget_lv = min_pass = chosen = None

    if mode in ("auto", "calibrate"):
        for r in ratios:
            sw.build(r)
    if mode == "auto":
        passing = [x for x in sw.levels if x["pass"]]
        if not passing:
            raise RuntimeError("no level passes the floor, not even ratio 1.0; check ref_high.glb")
        chosen = min(passing, key=lambda x: x["tris"])
        lower = [r for r in ratios if r < chosen["ratio"]]
        if not lower:
            chosen = sw.extend_below(chosen, refine_steps)
        elif refine_steps:
            chosen = sw.refine(max(lower), chosen, refine_steps)
        first_engine = chosen["engine"]
        chosen, xchecks["auto"] = sw.other_engine(chosen)
        if chosen["engine"] != first_engine:
            before = chosen["tris"]
            chosen = sw.descend(chosen, ratios, refine_steps)
            xchecks["auto"]["descended"] = {"from_tris": before, "to_tris": chosen["tris"]}
        knee, knee_note = sw.knee()
        reason = ""
        if "descended" in xchecks["auto"]:
            reason = (f"{chosen['engine']} beat {first_engine} in the cross-check at "
                      f"{xchecks['auto']['descended']['from_tris']} tris, so the search continued down with "
                      f"{chosen['engine']}. ")
        reason += (f"lowest tri count passing every floor metric: {chosen['tris']} tris "
                  f"({chosen['engine']}, ratio {chosen['ratio']}), worst IoU {chosen['iou_worst']}, "
                  f"Hausdorff {chosen['hausdorff_px']} px, normal p95 {chosen['normal_dev_p95_deg']} deg.")
        if knee is None:
            reason += f" No knee ({knee_note})."
        elif knee < chosen["tris"]:
            reason += f" Kneedle knee at {knee} tris is below it: the floor wins."
        else:
            reason += f" Kneedle knee at {knee} tris is at or above it: the curve is already flat there."
        selected["auto"] = chosen
    elif mode == "budget":
        budget_lv = sw.build_budget(budget)
        budget_lv, xchecks["budget"] = sw.other_engine(budget_lv)
        if budget_lv["pass"]:
            min_pass = budget_lv
            reason = (f"budget {budget}: level at {budget_lv['tris']} tris ({budget_lv['engine']}) passes "
                      f"the floor (worst IoU {budget_lv['iou_worst']}, Hausdorff {budget_lv['hausdorff_px']} px).")
        else:
            last_fail = budget_lv["ratio"]
            for r in sorted(x for x in ratios if x > budget_lv["ratio"]):
                lv = sw.build(r)
                if lv["pass"]:
                    min_pass = sw.refine(last_fail, lv, refine_steps) if refine_steps else lv
                    break
                last_fail = r
            if min_pass:
                first_engine = min_pass["engine"]
                min_pass, xchecks["min_pass"] = sw.other_engine(min_pass)
                if min_pass["engine"] != first_engine:
                    before = min_pass["tris"]
                    min_pass = sw.descend(min_pass, [r for r in ratios if r > budget_lv["ratio"]] or ratios,
                                          refine_steps)
                    xchecks["min_pass"]["descended"] = {"from_tris": before, "to_tris": min_pass["tris"]}
            reason = (f"budget {budget}: level at {budget_lv['tris']} tris ({budget_lv['engine']}) fails "
                      f"the floor ({', '.join(budget_lv['fails'])}: worst IoU {budget_lv['iou_worst']}, "
                      f"Hausdorff {budget_lv['hausdorff_px']} px).")
            if min_pass and "descended" in xchecks.get("min_pass", {}):
                reason += (f" {min_pass['engine']} beat {first_engine} in the cross-check, so the min_pass "
                           f"search continued down with {min_pass['engine']}.")
            if min_pass:
                reason += (f" Fewest tris that pass: {min_pass['tris']} ({min_pass['engine']}), "
                           f"{min_pass['tris'] - budget_lv['tris']} over budget. Export both and explain the gap.")
            else:
                reason += " Nothing passes the floor."
        selected["budget"] = budget_lv
        if min_pass:
            selected["min_pass"] = min_pass
        knee, knee_note = sw.knee()
    else:
        knee, knee_note = sw.knee()
        reason = "calibrate: every level exported and measured, nothing chosen"

    artifacts = {}
    for role, lv in selected.items():
        tex = lv.get("texture_error_p95")
        if not sw.rebake and tex is not None and tex > cfg["sweep"]["texture_error_warn"]:
            sw.warnings.append(f"selected_{role}: UVs kept but texture error p95 {tex} > "
                               f"{cfg['sweep']['texture_error_warn']} ({lv['engine']} moved UVs); expect bake.py "
                               "SSIM to fail, or run with gltfpack / a higher level")
        dst = os.path.join(a.work, f"selected_{role}.glb")
        shutil.copyfile(lv["file"], dst)
        lv["selected_as"] = (lv.get("selected_as", []) + [role])
        artifacts[f"selected_{role}"] = dst
        keep.add(lv["file"])
    if mode != "calibrate":
        for lv in sw.levels:
            if lv["file"] not in keep and os.path.isfile(lv["file"]):
                os.remove(lv["file"])
                lv["file_deleted"] = True

    curve = os.path.join(a.work, "curve.png")
    marks = []
    if budget:
        marks.append((budget, "budget", (110, 110, 110)))
    for role, lv in selected.items():
        marks.append((lv["tris"], f"chosen[{role}]", (20, 140, 60)))
    draw_curve(sw.levels, ocfg["floor"], curve, knee, marks)
    artifacts["curve"] = curve

    checks = []
    if mode == "auto":
        checks.append(common.check("chosen.floor", "pass" if chosen["pass"] else "fail", chosen["tris"]))
    elif mode == "budget":
        checks.append(common.check("final_budget.floor", "pass" if budget_lv["pass"] else "fail",
                                   budget_lv["tris"], budget,
                                   note=None if budget_lv["pass"] else "budget below the floor: export "
                                   "final_budget and final_min_pass, explain the gap"))
        checks.append(common.check("final_budget.within_budget", "pass" if budget_lv["tris"] <= budget else "fail",
                                   budget_lv["tris"], budget))
        if min_pass:
            checks.append(common.check("final_min_pass.floor", "pass" if min_pass["pass"] else "fail",
                                       min_pass["tris"]))
    curve_rows = sorted(sw.levels, key=lambda x: (x["tris"], x["engine"]))
    winners = {role: lv["engine"] for role, lv in selected.items()}
    data = {
        "mode": mode, "ref": os.path.abspath(a.input), "ref_tris": sw.ref_tris, "rebake": sw.rebake,
        "floor": ocfg["floor"], "curve": curve_rows,
        "knee_tris": knee, "knee_note": knee_note,
        "chosen_tris": chosen["tris"] if chosen else None,
        "budget_tris": budget_lv["tris"] if budget_lv else None, "budget": budget,
        "min_pass_tris": min_pass["tris"] if min_pass else None,
        "engine_winner": winners.get("auto") or winners.get("budget"), "engine_winners": winners,
        "engine_crosscheck": xchecks, "reason": reason,
        "selected": {role: {"file": artifacts[f"selected_{role}"], "tag": lv["tag"], "tris": lv["tris"],
                            "engine": lv["engine"], "pass": lv["pass"]} for role, lv in selected.items()},
    }
    metrics = {"levels": len(sw.levels), "ref_tris": sw.ref_tris, "knee_tris": knee,
               "chosen_tris": data["chosen_tris"], "budget_tris": data["budget_tris"],
               "min_pass_tris": data["min_pass_tris"]}
    common.write_result(a.out, TOOL, checks, metrics, sw.warnings, artifacts, data,
                        overall="info" if mode == "calibrate" else None,
                        source=a.input, spec_path=a.spec)


if __name__ == "__main__":
    args = parse()
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc, source=args.input)
        sys.exit(1)
