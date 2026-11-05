"""Collect every result JSON of one asset into report.json, contact_sheet.png and a report.md
skeleton (SKILL.md, Report). Pure Python (json, PIL). Reads; never measures or judges.

Usage:
  python3 tools/report.py --work output/<asset> --spec output/<asset>/task/spec.json [--out-dir <dir>]

Reads (paths relative to --work, the asset folder):
  evidence/**/*.json and work/**/*.json that are result JSONs ("tool" key): preflight,
  validate_concept, audit, gate1, cleanup, sweep, bake, assembly, gates, param_fit (fit*.json),
  apply_edit, render_views, asset_checks/*. Per-level and history folders (work/optimize/measure,
  work/optimize/sweep, snapshots, rollouts, renders/code) are not collected one by one: sweep.json,
  best.json and edits.json summarise them.
  Critic verdicts: evidence/review/*.json (newest) else work/self_build/diagnoses/<n>.json (highest n).
Writes (in --out-dir, default --work):
  report.json        entry, path, faces, metrics, texture, validation (overall per QA script),
                     critic, warnings (every JSON's warnings, deduplicated, with their tool),
                     not_checked (every not_checked check + engine/device/height facts), files,
                     missing (inputs looked for and not found; nothing is filled in for them)
  contact_sheet.png  concept | clay | final textured, plus the sweep curve (curve.png) when present.
                     Without final*.glb (finalize.py not run or refused) it stands for the newest
                     work/**/baked_*.glb: the panel label and `missing` say so
  report.md          Vietnamese skeleton with those facts; the orchestrator rewrites the prose
Exit 0; 1 on error.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QA_SCRIPTS = ["mesh_check", "uv_check", "contact_check", "iou_check", "concept_coverage",
              "render_rig", "screen_tris_check", "export_check"]
SKIP_DIRS = {"measure", "snapshots", "rollouts", "code", "__pycache__"}
REAL_ENGINES = {"unity", "godot", "unreal"}


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def rel(work, p):
    return os.path.relpath(p, work) if p else None


def resolve(work, p):
    """Paths inside result JSONs are absolute or relative to the asset folder (the tools' cwd)."""
    if not p:
        return None
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(work, p))


def collect(work):
    """All result JSONs: list of (relative path, dict). Skips per-level and history folders."""
    out = []
    for top in ("evidence", "work"):
        for root, dirs, files in os.walk(os.path.join(work, top)):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                             and not (d == "sweep" and os.path.basename(root) == "optimize"))
            for fn in sorted(files):
                if not fn.endswith(".json") or fn.endswith(".validator.json"):
                    continue
                p = os.path.join(root, fn)
                d = read(p)
                if isinstance(d, dict) and "tool" in d:
                    out.append((rel(work, p), d))
    return out


def latest(results, tool):
    """Newest result of one tool (by run_at), or (None, None)."""
    rows = [(p, d) for p, d in results if d.get("tool") == tool]
    if not rows:
        return None, None
    return max(rows, key=lambda r: r[1].get("run_at") or "")


def critic(work):
    rev = glob.glob(os.path.join(work, "evidence", "review", "*.json"))
    diags = [p for p in glob.glob(os.path.join(work, "work", "self_build", "diagnoses", "*.json"))
             if os.path.basename(p)[:-5].isdigit()]
    if rev:
        path = max(rev, key=os.path.getmtime)
    elif diags:
        path = max(diags, key=lambda p: int(os.path.basename(p)[:-5]))
    else:
        return None
    d = read(path) or {}
    concl = None
    for line in str(d.get("rubric_vi") or "").splitlines():
        if line.upper().startswith(("VERDICT", "KẾT LUẬN", "KET LUAN")):  # rubric v0.7+ uses VERDICT
            concl = line.split(":", 1)[-1].strip()
    return {"source": rel(work, path), "approved": d.get("approved"), "conclusion_vi": concl,
            "summary": d.get("summary"), "step": d.get("step"),
            "evidence_opened": d.get("evidence_opened") or [], "top_fix": d.get("top_fix"),
            "criteria_failed": [c.get("id") for c in d.get("criteria", []) if c.get("verdict") == "fail"],
            "diagnoses": sorted(rel(work, p) for p in diags)}


def first_existing(work, cands):
    for c in cands:
        p = os.path.join(work, c) if not os.path.isabs(c) else c
        if os.path.isfile(p):
            return p
    return None


def newest(work, pattern):
    hits = [p for p in glob.glob(os.path.join(work, "**", pattern), recursive=True) if os.path.isfile(p)]
    return max(hits, key=os.path.getmtime) if hits else None


def find_render(work, mode):
    """render_rig output for one mode anywhere under the asset folder: game_<mode>_crop.png, else
    game_<mode>.png (newest run), else the lowest-azimuth view<az>_<mode>.png (render_rig names
    views by azimuth, so view000 exists only when camera.azimuth_deg is 0)."""
    for pat in (f"game_{mode}_crop.png", f"game_{mode}.png"):
        p = newest(work, pat)
        if p:
            return p
    views = glob.glob(os.path.join(work, "**", f"view[0-9][0-9][0-9]_{mode}.png"), recursive=True)
    return min(views, key=lambda p: (os.path.basename(p), -os.path.getmtime(p))) if views else None


def contact_sheet(panels, path, h=512):
    """panels: list of (label, image path). One row, each scaled to height h, label above."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:
        font = ImageFont.load_default()
    ims = []
    for label, p in panels:
        im = Image.open(p)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(bg, im)
        im = im.convert("RGB")
        im = im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
        ims.append((label, im))
    pad, top = 12, 36
    w = sum(im.width for _, im in ims) + pad * (len(ims) + 1)
    sheet = Image.new("RGB", (w, h + top + pad), (235, 235, 235))
    draw = ImageDraw.Draw(sheet)
    x = pad
    for label, im in ims:
        draw.text((x, 8), label, fill=(20, 20, 20), font=font)
        sheet.paste(im, (x, top))
        x += im.width + pad
    sheet.save(path)


def build(work, spec_path):
    spec = read(spec_path) or {}
    results = collect(work)
    missing, files = [], {}

    def need(name, obj):
        if obj is None:
            missing.append(name)
        return obj

    # ---- steps present
    steps = {}
    for p, d in results:
        steps.setdefault(d["tool"], []).append({"path": p, "overall": d.get("overall"), "run_at": d.get("run_at")})
    path_steps = [t for t in ("optimize/validate_concept", "self_build/assembly", "self_build/gates",
                              "self_build/param_fit", "self_build/apply_edit", "optimize/audit",
                              "optimize/gate1", "optimize/cleanup", "optimize/sweep", "optimize/bake")
                  if t in steps]

    # ---- faces
    _, audit = latest(results, "optimize/audit")
    _, sweep = latest(results, "optimize/sweep")
    _, asm = latest(results, "self_build/assembly")
    sm = (sweep or {}).get("metrics", {})
    sd = (sweep or {}).get("data", {})
    faces = {
        "source_tris": ((audit or {}).get("metrics") or {}).get("tris"),
        "self_build_tris": ((asm or {}).get("metrics") or {}).get("tris") if asm else None,
        "chosen_tris": sm.get("chosen_tris") if sm.get("chosen_tris") is not None else sm.get("budget_tris"),
        "budget": (spec.get("budget") or {}).get("max_tris_total"),
        "budget_mode": (spec.get("budget") or {}).get("mode"),
        "min_pass_tris": sm.get("min_pass_tris"),
        "knee_tris": sm.get("knee_tris"),
        "reason": sd.get("reason"),
    }
    need("work/optimize/audit.json", audit)
    need("work/optimize/sweep.json", sweep)

    # ---- metrics
    metrics = {}
    _, gate1 = latest(results, "optimize/gate1")
    if asm and (asm.get("data") or {}).get("iou"):
        metrics["concept_iou"] = {"source": "self_build/assembly", **{k: asm["data"]["iou"].get(k)
                                  for k in ("worst", "mean", "worst_view", "per_view")}}
    elif gate1 and gate1.get("metrics"):
        pv = {k: v.get("iou") for k, v in (gate1.get("data") or {}).get("views", {}).items()}
        metrics["concept_iou"] = {"source": "optimize/gate1", "worst": gate1["metrics"].get("iou_worst"),
                                  "mean": round(sum(pv.values()) / len(pv), 4) if pv else None, "per_view": pv}
    else:
        missing.append("concept IoU (assembly.json or gate1.json)")
    sel = sd.get("selected") or {}
    curve = {c.get("tag"): c for c in sd.get("curve") or []}
    for role, s in sel.items():
        c = curve.get(s.get("tag")) or {}
        metrics[f"sweep_{role}"] = {"tris": s.get("tris"), "engine": s.get("engine"), "pass": s.get("pass"),
                                    "iou_worst_vs_ref": c.get("iou_worst"), "hausdorff_px": c.get("hausdorff_px"),
                                    "normal_dev_p95_deg": c.get("normal_dev_p95_deg"), "level": s.get("tag")}
    bakes = [(p, d) for p, d in results if d.get("tool") == "optimize/bake"]
    bake_p, bake = max(bakes, key=lambda r: r[1].get("run_at") or "") if bakes else (None, None)
    if bake:
        metrics["ssim_min"] = (bake.get("metrics") or {}).get("ssim_min")
    else:
        missing.append("work/optimize/bake_<name>.json")

    # ---- texture
    texture = None
    if bake:
        bd = bake.get("data") or {}
        texture = {"source_json": bake_p, "mode": bd.get("mode"), "unwrap": bd.get("unwrap"),
                   "bake_source": bd.get("bake_source"), "resolution": bd.get("texture_res"),
                   "uv_occupancy": bd.get("uv_occupancy"), "material": bd.get("material"),
                   "style": spec.get("style")}
    _, uvc = latest(results, "asset_checks/uv_check")
    if texture is not None and uvc:
        texture["uv_check_resolution_source"] = {k: v.get("resolution_source")
                                                 for k, v in (uvc.get("data") or {}).items() if isinstance(v, dict)}

    # ---- validation (QA gate)
    validation = {}
    for s in QA_SCRIPTS:
        p, d = latest(results, f"asset_checks/{s}")
        if d is None:
            validation[s] = {"overall": None, "path": None}
            missing.append(f"evidence/qa/{s}.json")
        else:
            validation[s] = {"overall": d.get("overall"), "summary": d.get("summary"), "path": p,
                             "fails": [c["check"] for c in d.get("checks", []) if c.get("status") == "fail"]}

    # ---- warnings and not_checked
    warnings, seen = [], set()
    qa_latest = {v["path"] for v in validation.values() if v.get("path")}
    not_checked = []
    for p, d in results:
        is_qa = d["tool"].startswith("asset_checks/")
        if is_qa and p not in qa_latest:
            continue   # superseded run of the same check (e.g. calibration render)
        for w in d.get("warnings") or []:
            key = (d["tool"], w)
            if key not in seen:
                seen.add(key)
                warnings.append({"tool": d["tool"], "path": p, "warning": w})
        for c in d.get("checks") or []:
            if c.get("status") == "not_checked":
                not_checked.append({"tool": d["tool"], "check": c.get("check"), "note": c.get("note")})
    engine = spec.get("engine")
    if engine not in REAL_ENGINES:
        not_checked.append({"tool": "spec", "check": "engine", "note": f"spec engine {engine!r}: no engine import/look check"})
    not_checked.append({"tool": "spec", "check": "device", "note": "no on-device performance test"})
    if spec.get("height_source") == "estimated":
        not_checked.append({"tool": "spec", "check": "height", "note": "height_m estimated, not given"})

    # ---- critic
    crit = critic(work)
    need("critic verdict (evidence/review/*.json or work/self_build/diagnoses/<n>.json)", crit)

    # ---- files
    for p in sorted(glob.glob(os.path.join(work, "final*.glb"))):
        files[os.path.basename(p)[:-4]] = rel(work, p)
    model = None                      # the GLB the contact sheet stands for
    if any(k.startswith("final") for k in files):
        model = "final.glb" if "final" in files else os.path.basename(files[sorted(files)[0]])
    else:
        baked = sorted(glob.glob(os.path.join(work, "work", "**", "baked_*.glb"), recursive=True),
                       key=os.path.getmtime)
        if baked:
            files["baked_fallback"] = rel(work, baked[-1])
            model = os.path.basename(baked[-1])
            missing.append(f"final*.glb: none yet (run tools/finalize.py); contact sheet and files use the "
                           f"newest baked GLB {rel(work, baked[-1])} instead")
        else:
            missing.append("final*.glb (and no work/**/baked_*.glb to fall back on)")
    if os.path.isfile(os.path.join(work, "evidence/qa/renders/sheet.png")):
        files["qa_sheet"] = "evidence/qa/renders/sheet.png"
    curve_png = newest(work, "curve.png")   # wherever sweep's --work put it
    if curve_png:
        files["curve"] = rel(work, curve_png)

    # ---- contact sheet
    cviews = (spec.get("concept") or {}).get("views") or {}
    concept = None
    for v in ("front", "34", *cviews):
        if v in cviews:
            concept = first_existing(work, [os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(spec_path)),
                                                                          cviews[v]))])
            if concept:
                break
    clay = find_render(work, "clay") or first_existing(work, ["work/self_build/renders/clay_34.png",
                                                              "work/self_build/renders/clay_front.png"])
    final_tex = find_render(work, "albedo") or find_render(work, "lit")
    panels = []
    for label, p, miss in (("concept", concept, "concept image (spec concept.views)"),
                           ("clay", clay, "clay render (render_rig game_clay*/view*_clay.png)"),
                           (f"textured ({model or 'final'})" if model and model.startswith("final") else
                            f"textured ({model}, not finalized)" if model else "final textured",
                            final_tex, "textured render (render_rig game_albedo*/view*_albedo.png)"),
                           ("error vs faces", curve_png, "sweep curve (**/curve.png)")):
        if p:
            panels.append((label, p))
        else:
            missing.append(miss)
    milestone = "chưa game-ready: chưa kiểm engine và thiết bị" if engine not in REAL_ENGINES else \
        "chưa game-ready: chưa kiểm trên thiết bị"
    report = {
        "asset": spec.get("asset") or os.path.basename(os.path.abspath(work)),
        "entry": spec.get("entry"), "generator": spec.get("generator"),
        "path": path_steps, "steps": steps,
        "faces": faces, "metrics": metrics, "texture": texture, "validation": validation,
        "qa_overall": "fail" if any(v["overall"] in ("fail", "error") for v in validation.values()) else
                      ("incomplete" if any(v["overall"] is None for v in validation.values()) else "pass"),
        "critic": crit, "warnings": warnings, "not_checked": not_checked, "milestone": milestone,
        "files": files, "contact_sheet_model": model, "contact_sheet_panels": [{"label": l, "path": rel(work, p)} for l, p in panels],
        "missing": missing, "spec": os.path.abspath(spec_path), "collected": len(results),
    }
    return report, panels


def fmt(v, nd=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}g}"
    return str(v)


def markdown(r):
    f, m, t, c = r["faces"], r["metrics"], r["texture"], r["critic"]
    L = [f"# {r['asset']} — báo cáo", "",
         "<!-- Khung do tools/report.py sinh từ JSON; orchestrator viết lại phần lời. Số liệu chỉ lấy từ report.json. -->", "",
         f"- Entry: {fmt(r['entry'])}; generator: {fmt(r['generator'])}",
         f"- Đường đi: {' → '.join(r['path']) or '—'}",
         f"- Faces: nguồn {fmt(f['source_tris'])}" + (f" (self-build {f['self_build_tris']})" if f.get("self_build_tris") else "")
         + f" → chọn {fmt(f['chosen_tris'])}; budget {fmt(f['budget'])} ({fmt(f['budget_mode'])}); min_pass {fmt(f['min_pass_tris'])}; knee {fmt(f['knee_tris'])}",
         ]
    if f.get("reason"):
        L.append(f"  - Lý do chọn (sweep.json): {f['reason']}")
    ci = m.get("concept_iou")
    L.append(f"- IoU so concept ({ci['source']}): worst {fmt(ci.get('worst'))}, mean {fmt(ci.get('mean'))}" if ci
             else "- IoU so concept: — (thiếu)")
    for k, v in m.items():
        if k.startswith("sweep_"):
            L.append(f"- Mức {k[6:]}: {fmt(v['tris'])} tris ({v['engine']}), IoU worst so ref {fmt(v['iou_worst_vs_ref'])}, "
                     f"Hausdorff {fmt(v['hausdorff_px'])} px, normal p95 {fmt(v['normal_dev_p95_deg'])}°")
    L.append(f"- SSIM min: {fmt(m.get('ssim_min'))}")
    if t:
        L.append(f"- Texture: {fmt(t['mode'])}, unwrap {fmt(t['unwrap'])}, nguồn bake {fmt(t['bake_source'])}, "
                 f"{fmt(t['resolution'])} px, UV occupancy {fmt(t['uv_occupancy'])}, material {fmt(t['material'])}")
    else:
        L.append("- Texture: — (không có bake JSON)")
    L += ["", "## Kiểm tra (QA gate)", "", "| Script | overall | fail |", "|---|---|---|"]
    for s, v in r["validation"].items():
        L.append(f"| {s} | {fmt(v['overall'])} | {', '.join(v.get('fails') or []) or '—'} |")
    L += ["", f"QA tổng: {r['qa_overall']}", "", "## Critic", ""]
    if c:
        L.append(f"- Nguồn: {c['source']}; approved: {fmt(c['approved'])}; kết luận: {fmt(c['conclusion_vi'])}")
        L.append(f"- Ảnh đã mở: {', '.join(c['evidence_opened']) or '—'}")
        if c.get("criteria_failed"):
            L.append(f"- Tiêu chí fail: {', '.join(c['criteria_failed'])}")
    else:
        L.append("- Chưa có verdict của critic.")
    L += ["", "## Cảnh báo", ""] + [f"- [{w['tool']}] {w['warning']}" for w in r["warnings"]] + (["- —"] if not r["warnings"] else [])
    L += ["", "## Chưa kiểm", ""] + [f"- [{n['tool']}] {n['check']}: {n.get('note') or ''}" for n in r["not_checked"]]
    L += ["", f"Mốc: {r['milestone']}.", "", "## File", ""]
    L += [f"- {k}: {v}" for k, v in r["files"].items()] + ["- report.json", "- report.md"]
    if r["missing"]:
        L += ["", "## Thiếu đầu vào (không suy đoán)", ""] + [f"- {x}" for x in r["missing"]]
    return "\n".join(L) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--work", required=True, help="asset folder output/<asset>")
    p.add_argument("--spec", required=True)
    p.add_argument("--out-dir")
    a = p.parse_args()
    out = a.out_dir or a.work
    os.makedirs(out, exist_ok=True)
    report, panels = build(os.path.abspath(a.work), a.spec)
    sheet = os.path.join(out, "contact_sheet.png")
    if panels:
        contact_sheet(panels, sheet)
        report["files"]["contact_sheet"] = os.path.relpath(sheet, a.work)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write(markdown(report))
    print(f"[report] qa_overall={report['qa_overall']} collected={report['collected']} "
          f"missing={len(report['missing'])} -> {os.path.join(out, 'report.json')}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"[report] error: {exc!r}", file=sys.stderr)
        sys.exit(1)
