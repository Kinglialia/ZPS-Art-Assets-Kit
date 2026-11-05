#!/usr/bin/env bash
# One-time setup per machine (macOS, Linux). See SKILL.md, Setup.
#
#   bash tools/setup_deps.sh            # install
#   DRY_RUN=1 bash tools/setup_deps.sh  # print the commands, change nothing
#
# 1. Finds Blender: $BLENDER, else /Applications/Blender.app/Contents/MacOS/Blender, else
#    `blender` on PATH.
# 2. Asks Blender for its Python version and numpy version.
# 3. Creates or updates the venv tools/.deps/venv/ for the pure-Python tools.
# 4. Installs the packages the Blender-side scripts import into
#    tools/.deps/blender-py<major><minor>/ with the venv's pip:
#    pip install --target <dir> --python-version <X.Y> --only-binary=:all: --no-deps <pkgs>
#    numpy is never installed there: Blender bundles it and a second copy breaks its modules.
#    --no-deps keeps pip from pulling numpy in; the list below already holds every other
#    dependency. tools/lib/bootstrap.py puts that folder on Blender's sys.path.
# 5. Prints what to do about gltfpack and the glTF validator.
set -euo pipefail

TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS="$TOOLS/.deps"
DRY_RUN="${DRY_RUN:-0}"

# Blender-side imports beyond Blender's bundle (bpy, mathutils, bmesh, numpy).
BLENDER_PKGS=(pyyaml trimesh opencv-python-headless scipy xatlas Pillow)
# Pure-Python tools (validate_concept, gate1, sweep, measure, self_build, preflight, report, finalize).
VENV_PKGS=(numpy pyyaml trimesh scipy opencv-python-headless scikit-image kneed xatlas manifold3d Pillow)
VENV_OPTIONAL=(rembg)   # background removal; large (onnxruntime), may lack wheels for new Pythons

say() { printf '%s\n' "$*"; }
run() {
  say "+ $*"
  if [ "$DRY_RUN" != "1" ]; then "$@"; fi
}

find_blender() {
  if [ -n "${BLENDER:-}" ]; then
    printf '%s\n' "$BLENDER"; return 0
  fi
  local mac=/Applications/Blender.app/Contents/MacOS/Blender
  if [ -x "$mac" ]; then
    printf '%s\n' "$mac"; return 0
  fi
  if command -v blender >/dev/null 2>&1; then
    command -v blender; return 0
  fi
  return 1
}

find_python() {
  local p
  for p in python3.13 python3 python; do
    if command -v "$p" >/dev/null 2>&1; then command -v "$p"; return 0; fi
  done
  return 1
}

BL="$(find_blender)" || {
  say "Blender not found. Set BLENDER=/path/to/blender, or install Blender (macOS: /Applications/Blender.app)."
  say "Without the Blender app: pip install bpy (Python 3.13 -> bpy 5.2.x) into tools/.deps/venv and run every script with it."
  exit 1
}
[ -x "$BL" ] || { say "BLENDER=$BL is not executable"; exit 1; }
say "Blender: $BL"

# Blender prints its own banner lines; the probe line is tagged.
PROBE='import sys
try:
    import numpy; nv = numpy.__version__
except Exception:
    nv = "none"
print("DEPS_PROBE %d.%d %s" % (sys.version_info[0], sys.version_info[1], nv))'
LINE="$("$BL" -b --factory-startup --python-expr "$PROBE" 2>/dev/null | grep '^DEPS_PROBE ' | tail -n 1 || true)"
[ -n "$LINE" ] || { say "could not read Python/numpy versions from $BL"; exit 1; }
PYVER="$(printf '%s\n' "$LINE" | awk '{print $2}')"
NUMPY_VER="$(printf '%s\n' "$LINE" | awk '{print $3}')"
case "$PYVER" in
  [0-9]*.[0-9]*) ;;
  *) say "unexpected Python version from Blender: '$PYVER'"; exit 1 ;;
esac
TAG="${PYVER/./}"
TARGET="$DEPS/blender-py$TAG"
say "Blender Python $PYVER, numpy $NUMPY_VER -> $TARGET"
if [ "$NUMPY_VER" = "none" ]; then
  say "warning: Blender's Python has no numpy; the Blender-side tools need it (Blender normally bundles it)."
fi

PY="$(find_python)" || { say "no python3 on PATH: needed for pip and the venv"; exit 1; }
say "venv base python: $PY"

# venv first: its pip installs both sets (a system pip may refuse under PEP 668).
VENV="$DEPS/venv"
if [ ! -x "$VENV/bin/python" ]; then
  run "$PY" -m venv "$VENV"
fi
VPY="$VENV/bin/python"
run "$VPY" -m pip install --upgrade pip
run "$VPY" -m pip install --upgrade "${VENV_PKGS[@]}"
for p in "${VENV_OPTIONAL[@]}"; do
  run "$VPY" -m pip install --upgrade "$p" || say "warning: optional $p not installed (validate_concept falls back without it)"
done

run mkdir -p "$TARGET"
# --python-version: wheels for Blender's Python, whatever Python the venv runs.
run "$VPY" -m pip install --upgrade --target "$TARGET" --python-version "$PYVER" \
  --only-binary=:all: --no-deps "${BLENDER_PKGS[@]}"
if [ -d "$TARGET/numpy" ]; then
  say "removing $TARGET/numpy (Blender bundles numpy $NUMPY_VER)"
  run rm -rf "$TARGET/numpy" "$TARGET"/numpy-*.dist-info "$TARGET/numpy.libs"
fi

say ""
say "Check inside Blender:"
say "  \"$BL\" -b --python-expr 'import sys; sys.path.insert(0, \"$TOOLS/lib\"); import bootstrap, yaml, cv2, trimesh, scipy, xatlas, PIL; print(\"deps ok\", bootstrap.DEPS)'"
say ""
if command -v gltfpack >/dev/null 2>&1; then
  say "gltfpack: $(command -v gltfpack)"
else
  say "gltfpack missing (sweep falls back to Blender Decimate): brew install gltfpack, or npm i -g gltfpack"
fi
if command -v gltf_validator >/dev/null 2>&1; then
  say "glTF validator: $(command -v gltf_validator)"
elif command -v node >/dev/null 2>&1; then
  say "glTF validator: node found; for export_check run npm i -g gltf-validator (uses tools/asset_checks/gltf_validate.mjs)"
else
  say "glTF validator missing (optional, export_check): install node, then npm i -g gltf-validator"
fi
say "Next: $VENV/bin/python $TOOLS/preflight.py --out evidence/preflight.json"
