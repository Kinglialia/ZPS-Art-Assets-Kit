#!/bin/bash
set -eu
PACKAGE_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 "$PACKAGE_DIR/installer/install.py" --verify
