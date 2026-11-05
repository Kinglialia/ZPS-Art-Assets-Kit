#!/bin/bash
set -eu
PACKAGE_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Cần Python 3. Cài Python 3 từ python.org rồi chạy lại.'
  exit 1
fi
python3 "$PACKAGE_DIR/installer/install.py" --install
