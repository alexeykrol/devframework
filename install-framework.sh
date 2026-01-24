#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-framework.zip}"
DEST_DIR="${2:-.}"

if [ ! -f "$ZIP_PATH" ]; then
  echo "Missing zip: $ZIP_PATH" >&2
  exit 1
fi

if [ -d "$DEST_DIR/framework" ]; then
  echo "Target already exists: $DEST_DIR/framework" >&2
  exit 1
fi

python3 - <<'PY'
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1]).resolve()
dest_dir = Path(sys.argv[2]).resolve()

with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(dest_dir)

print(f"Installed framework to {dest_dir / 'framework'}")
PY
"$ZIP_PATH" "$DEST_DIR"
