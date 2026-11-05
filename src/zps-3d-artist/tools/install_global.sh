#!/bin/bash
# Install the 3d-artist skill for every Claude Code session on this machine/container:
#   - copies the skill to ~/.claude/skills/3d-artist and its subagents to ~/.claude/agents/
#   - on Linux cloud containers, installs what the tools need (bpy pip module, EGL for headless
#     Workbench renders, Python packages, gltfpack + gltf-validator)
# Usage: bash <skill>/tools/install_global.sh [--skip-deps]
# Safe to run again: it overwrites the installed copy with this one.
set -euo pipefail

SKILL_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_SKILLS="${HOME}/.claude/skills"
DEST_AGENTS="${HOME}/.claude/agents"
SKIP_DEPS=0
[ "${1:-}" = "--skip-deps" ] && SKIP_DEPS=1

log() { echo "[3d-artist install] $*"; }

# 1. skill + agents
mkdir -p "$DEST_SKILLS" "$DEST_AGENTS"
rm -rf "$DEST_SKILLS/3d-artist"
cp -R "$SKILL_SRC" "$DEST_SKILLS/3d-artist"
find "$DEST_SKILLS/3d-artist" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
rm -rf "$DEST_SKILLS/3d-artist/tools/.deps"
cp "$SKILL_SRC"/agents/*.md "$DEST_AGENTS/"
log "skill -> $DEST_SKILLS/3d-artist, agents -> $DEST_AGENTS"

[ "$SKIP_DEPS" = 1 ] && { log "deps skipped"; exit 0; }

# 2. dependencies (Linux containers). On macOS use tools/setup_deps.sh with the Blender app.
if [ "$(uname -s)" != "Linux" ]; then
  log "not Linux: run tools/setup_deps.sh for Blender-app dependencies"; exit 0
fi

SUDO=""
[ "$(id -u)" != "0" ] && command -v sudo >/dev/null && SUDO="sudo"
if ! ldconfig -p 2>/dev/null | grep -q 'libEGL.so.1'; then
  log "installing libegl1 (headless Workbench renders)"
  $SUDO apt-get update -q >/dev/null && $SUDO apt-get install -y -q libegl1 libegl-mesa0 >/dev/null \
    || log "WARN: libegl1 install failed; Workbench renders will crash, Cycles still works"
fi

PY="$(command -v python3.13 || command -v python3)"
PYVER="$("$PY" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
PKGS="trimesh numpy scipy scikit-image opencv-python-headless pyyaml Pillow kneed xatlas manifold3d"
if [ "$PYVER" = "3.13" ]; then
  PKGS="bpy==5.2.3 $PKGS"
else
  log "WARN: python $PYVER found; the bpy pip module needs 3.13. Blender-side scripts need a Blender binary."
fi
log "pip install ($PYVER): $PKGS"
"$PY" -m pip install -q $PKGS 2>&1 | grep -v "Running pip as the 'root'" || true

if command -v npm >/dev/null; then
  command -v gltfpack >/dev/null || npm i -g -s gltfpack gltf-validator >/dev/null 2>&1 \
    || log "WARN: npm install of gltfpack/gltf-validator failed; sweep falls back to Blender Decimate"
  npm ls -g gltf-validator >/dev/null 2>&1 || npm i -g -s gltf-validator >/dev/null 2>&1 || true
else
  log "WARN: npm not found; no gltfpack (sweep falls back to Blender Decimate) and no glTF validator"
fi

"$PY" "$DEST_SKILLS/3d-artist/tools/preflight.py" --out "${HOME}/.claude/3d-artist-preflight.json" \
  >/dev/null 2>&1 && log "preflight -> ~/.claude/3d-artist-preflight.json" || log "WARN: preflight failed"
log "done"
