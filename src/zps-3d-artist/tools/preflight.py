"""Record what this machine has before any 3d-artist task (SKILL.md, Setup).

Usage:
  python3 tools/preflight.py [--out evidence/preflight.json] [--spec task/spec.json]

Records: Blender (paths.blender binary --version, else `blender` on PATH, else the bpy module),
gltfpack and gltf_validator (presence + version; without a native gltf_validator, the node fallback
export_check uses: node on PATH + npm gltf-validator + asset_checks/gltf_validate.mjs, probed on a
minimal glTF), and each Python package the tools use
(trimesh, manifold3d, xatlas, kneed, skimage, cv2, rembg, scipy, yaml, PIL, numpy, bpy).
Writes `features` (on/off per pipeline feature) and a warning for every missing optional piece
with its consequence. A missing tool never fails the run: overall is pass when every hard
requirement (numpy, trimesh, scipy, cv2, PIL, yaml, and some Blender) is present, else fail.
Exit 0 on pass/fail; 1 on error (error JSON written first).
"""
import argparse
import importlib
import os
import platform
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import common  # noqa: E402

TOOL = "preflight"
PACKAGES = ["numpy", "trimesh", "manifold3d", "xatlas", "kneed", "skimage", "cv2", "rembg",
            "scipy", "yaml", "PIL"]
REQUIRED = {"numpy", "trimesh", "scipy", "cv2", "PIL", "yaml"}


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, repr(exc)


def package_version(name):
    """Import in a child process so a crashing or slow import cannot take preflight down."""
    code = (f"import importlib; m = importlib.import_module({name!r}); "
            "print(getattr(m, '__version__', None) or getattr(getattr(m, 'app', None), 'version_string', '') or 'present')")
    rc, out = run([sys.executable, "-c", code], 120)
    if rc == 0:
        return {"present": True, "version": out.strip().splitlines()[-1]}
    return {"present": False, "error": out.strip().splitlines()[-1][:200] if out.strip() else "import failed"}


def blender_info(cfg):
    exe = (cfg.get("paths") or {}).get("blender")
    tried = []
    for cand in [exe, shutil.which("blender")]:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            rc, out = run([cand, "--version"], 120)
            m = re.search(r"Blender\s+([\d.]+\S*)", out or "")
            if rc == 0 and m:
                return {"present": True, "kind": "binary", "path": cand, "version": m.group(1)}
            tried.append(f"{cand}: exit {rc}")
        elif cand:
            tried.append(f"{cand}: not found")
    bpy = package_version("bpy")
    if bpy["present"]:
        return {"present": True, "kind": "bpy_module", "path": sys.executable, "version": bpy["version"],
                "tried": tried}
    return {"present": False, "tried": tried + [f"bpy: {bpy.get('error')}"]}


def cli_info(name, version_args):
    exe = shutil.which(name)
    if not exe:
        return {"present": False}
    rc, out = run([exe, *version_args], 30)
    m = re.search(r"\d+\.\d+(\.\d+)?", out or "")
    return {"present": True, "path": exe, "version": m.group(0) if m else (out or "").strip()[:80],
            "exit": rc}


def node_validator_info():
    """The fallback export_check uses when no native gltf_validator exists: node on PATH, the npm
    package gltf-validator resolvable by asset_checks/gltf_validate.mjs, and that script. Probed by
    validating a minimal glTF (exit 0 = works, 2 = package not found)."""
    import json
    import tempfile
    node = shutil.which("node")
    script = os.path.join(HERE, "asset_checks", "gltf_validate.mjs")
    info = {"present": False, "kind": "node", "node": node, "script": script if os.path.isfile(script) else None}
    if not node:
        info["reason"] = "node not on PATH"
        return info
    if not info["script"]:
        info["reason"] = "tools/asset_checks/gltf_validate.mjs missing"
        return info
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "probe.gltf")
        with open(probe, "w") as f:
            f.write('{"asset":{"version":"2.0"}}')
        rc, out = run([node, script, probe], 60)
    if rc == 0:
        try:
            ver = json.loads(out.strip().splitlines()[-1]).get("validatorVersion")
        except (ValueError, IndexError):
            ver = None
        info.update({"present": True, "version": ver, "path": f"{node} {script}"})
    else:
        info["reason"] = ("npm package gltf-validator not resolvable (npm i -g gltf-validator)" if rc == 2
                          else f"probe exit {rc}: {(out or '').strip()[-200:]}")
    return info


def main(a):
    try:
        cfg, _ = common.load_settings(a.spec)
    except ImportError:
        cfg = {"paths": {"blender": None, "gltfpack": "gltfpack", "gltf_validator": "gltf_validator"}}
    paths = cfg.get("paths") or {}
    warnings, checks = [], []
    blender = blender_info(cfg)
    if blender["present"] and blender["kind"] == "bpy_module" and paths.get("blender"):
        warnings.append(f"paths.blender ({paths['blender']}) not found; Blender scripts will run with "
                        f"`{sys.executable} script.py` (bpy module)")
    gltfpack = cli_info(paths.get("gltfpack") or "gltfpack", ["-v"])
    validator = cli_info(paths.get("gltf_validator") or "gltf_validator", ["--version"])
    if validator["present"]:
        validator["kind"] = "native"
    else:
        validator = node_validator_info()
    pkgs = {p: package_version(p) for p in PACKAGES}
    rembg_model = os.path.isfile(os.path.expanduser("~/.u2net/u2net.onnx")) or \
        os.path.isfile(os.path.expanduser("~/.rembg/models/u2net/u2net.onnx"))

    has = {p: pkgs[p]["present"] for p in PACKAGES}
    features = {
        "blender_scripts": blender["present"],
        "simplify_gltfpack": gltfpack["present"],
        "simplify_blender_fallback": blender["present"],
        "gltf_validation": validator["present"],
        "concept_masks": has["cv2"],
        "concept_rembg": has["rembg"],
        "rembg_model_cached": rembg_model,
        "measure": has["trimesh"] and has["scipy"],
        "knee": has["kneed"],
        "xatlas_unwrap": has["xatlas"],
        "boolean_union": has["manifold3d"],
        "ssim": True,  # bake.py has its own numpy SSIM
        "skimage": has["skimage"],
    }
    consequences = {
        "simplify_gltfpack": "sweep.py uses Blender Decimate for every level (engine_fallback)",
        "gltf_validation": "no glTF validator report (no native gltf_validator, and no node + npm "
                           "gltf-validator for gltf_validate.mjs); export_check relies on re-import only",
        "concept_rembg": "concept masks from alpha or the bright-grey background rule only",
        "rembg_model_cached": "rembg downloads its model (~176 MB) on first use; offline it falls back to the grey rule",
        "knee": "sweep.py records no knee cross-check",
        "xatlas_unwrap": "bake.py falls back to Blender Smart UV Project (not deterministic)",
        "boolean_union": "self_build assembly cannot union parts",
        "blender_scripts": "audit, cleanup, bake and asset_checks cannot run",
    }
    for feat, on in features.items():
        if not on and feat in consequences:
            warnings.append(f"{feat} off: {consequences[feat]}")
    missing_req = sorted(p for p in REQUIRED if not has[p])
    checks.append(common.check("required_packages", "fail" if missing_req else "pass",
                               missing_req or "all present"))
    checks.append(common.check("blender", "pass" if blender["present"] else "fail",
                               blender.get("version"), note=blender.get("kind")))
    checks.append(common.check("gltfpack", "pass" if gltfpack["present"] else "info", gltfpack.get("version")))
    checks.append(common.check("gltf_validator", "pass" if validator["present"] else "info",
                               validator.get("version"),
                               note=f"gltf_validation: on ({validator['kind']})" if validator["present"]
                               else f"gltf_validation: off ({validator.get('reason', 'no native gltf_validator')})"))
    data = {"python": sys.version.split()[0], "python_exe": sys.executable, "platform": platform.platform(),
            "blender": blender, "gltfpack": gltfpack, "gltf_validator": validator, "packages": pkgs,
            "features": features}
    common.write_result(a.out, TOOL, checks, {"features_on": sum(features.values()),
                                              "features_off": [k for k, v in features.items() if not v]},
                        warnings, data=data, spec_path=a.spec)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=os.path.join("evidence", "preflight.json"))
    p.add_argument("--spec")
    args = p.parse_args(common.script_argv())
    try:
        main(args)
    except Exception as exc:  # noqa: BLE001
        common.write_error(args.out, TOOL, exc)
        sys.exit(1)
