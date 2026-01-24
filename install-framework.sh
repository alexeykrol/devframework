#!/usr/bin/env bash
set -euo pipefail

REPO="${FRAMEWORK_REPO:-alexeykrol/devframework}"
REF="${FRAMEWORK_REF:-main}"
DEST_DIR="${FRAMEWORK_DEST:-.}"
PHASE="${FRAMEWORK_PHASE:-}"

ZIP_PATH=""
UPDATE_FLAG=0
RUN_FLAG=0
SKIP_INSTALL=0

usage() {
  cat <<'EOF'
Usage: ./install-framework.sh [options]

Options:
  --repo <owner/name>    GitHub repo (default: alexeykrol/devframework)
  --ref <ref>            Branch or tag (default: main)
  --zip <path>           Use local framework.zip instead of downloading
  --dest <dir>           Install destination (default: .)
  --update               Replace existing framework (backup is created)
  --run                  Run orchestrator after install
  --phase <main|legacy>  Force phase when running
  --legacy               Shortcut for --phase legacy
  --main                 Shortcut for --phase main
  -h, --help             Show help

Env overrides:
  FRAMEWORK_REPO, FRAMEWORK_REF, FRAMEWORK_DEST, FRAMEWORK_PHASE
  FRAMEWORK_UPDATE=1, FRAMEWORK_RUN=1
EOF
}

truthy() {
  case "${1:-}" in
    1|true|yes|on) return 0 ;;
    *) return 1 ;;
  esac
}

fetch_url() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url"
    return $?
  fi
  python3 - <<'PY' "$url"
import sys
import urllib.request
url = sys.argv[1]
try:
    with urllib.request.urlopen(url) as resp:
        sys.stdout.write(resp.read().decode("utf-8"))
except Exception as exc:
    sys.stderr.write(str(exc))
    sys.exit(1)
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"
      shift 2
      ;;
    --ref)
      REF="$2"
      shift 2
      ;;
    --zip)
      ZIP_PATH="$2"
      shift 2
      ;;
    --dest)
      DEST_DIR="$2"
      shift 2
      ;;
    --update)
      UPDATE_FLAG=1
      shift
      ;;
    --run)
      RUN_FLAG=1
      shift
      ;;
    --phase)
      PHASE="$2"
      shift 2
      ;;
    --legacy)
      PHASE="legacy"
      shift
      ;;
    --main)
      PHASE="main"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$ZIP_PATH" && -f "$1" ]]; then
        ZIP_PATH="$1"
        shift
      else
        echo "Unknown argument: $1" >&2
        usage
        exit 1
      fi
      ;;
  esac
done

if truthy "${FRAMEWORK_UPDATE:-}"; then
  UPDATE_FLAG=1
fi
if truthy "${FRAMEWORK_RUN:-}"; then
  RUN_FLAG=1
fi

ZIP_URL="${FRAMEWORK_ZIP_URL:-https://github.com/${REPO}/raw/${REF}/framework.zip}"
VERSION_URL="${FRAMEWORK_VERSION_URL:-https://raw.githubusercontent.com/${REPO}/${REF}/framework/VERSION}"

FRAMEWORK_DIR="${DEST_DIR%/}/framework"
LOCAL_VERSION=""
REMOTE_VERSION=""

if [[ -f "$FRAMEWORK_DIR/VERSION" ]]; then
  LOCAL_VERSION="$(head -n1 "$FRAMEWORK_DIR/VERSION" | tr -d '\r')"
fi

if [[ -z "$ZIP_PATH" ]]; then
  if REMOTE_VERSION="$(fetch_url "$VERSION_URL" 2>/dev/null)"; then
    REMOTE_VERSION="$(printf '%s' "$REMOTE_VERSION" | tr -d '\r' | head -n1)"
  else
    REMOTE_VERSION=""
  fi
fi

if [[ -d "$FRAMEWORK_DIR" && "$UPDATE_FLAG" -ne 1 ]]; then
  echo "Framework already installed at $FRAMEWORK_DIR" >&2
  if [[ -n "$LOCAL_VERSION" ]]; then
    echo "Local version: $LOCAL_VERSION" >&2
  fi
  if [[ -n "$REMOTE_VERSION" ]]; then
    echo "Remote version: $REMOTE_VERSION" >&2
  fi
  echo "Re-run with --update to replace (backup is created)." >&2
  exit 1
fi

if [[ -d "$FRAMEWORK_DIR" && "$UPDATE_FLAG" -eq 1 ]]; then
  if [[ -n "$LOCAL_VERSION" && -n "$REMOTE_VERSION" && "$LOCAL_VERSION" == "$REMOTE_VERSION" ]]; then
    echo "Framework is already up to date ($LOCAL_VERSION)."
    if [[ "$RUN_FLAG" -ne 1 ]]; then
      exit 0
    fi
    SKIP_INSTALL=1
  fi
fi

if [[ "$SKIP_INSTALL" -ne 1 ]]; then
  TMP_ZIP=""
  if [[ -z "$ZIP_PATH" ]]; then
    TMP_ZIP="$(mktemp -t devframework.XXXXXX.zip)"
    trap 'rm -f "$TMP_ZIP"' EXIT
    if ! fetch_url "$ZIP_URL" > "$TMP_ZIP"; then
      echo "Failed to download framework zip from $ZIP_URL" >&2
      exit 1
    fi
    ZIP_PATH="$TMP_ZIP"
  fi

  if [[ ! -f "$ZIP_PATH" ]]; then
    echo "Missing zip: $ZIP_PATH" >&2
    exit 1
  fi

  BACKUP_DIR=""
  if [[ -d "$FRAMEWORK_DIR" && "$UPDATE_FLAG" -eq 1 ]]; then
    TS="$(date +%Y%m%d%H%M%S)"
    BACKUP_DIR="${FRAMEWORK_DIR}.backup.${TS}"
    mv "$FRAMEWORK_DIR" "$BACKUP_DIR"
  fi

  python3 - <<'PY' "$ZIP_PATH" "$DEST_DIR"
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1]).resolve()
dest_dir = Path(sys.argv[2]).resolve()

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall(dest_dir)

print(f"Installed framework to {dest_dir / 'framework'}")
PY

  if [[ -n "$BACKUP_DIR" ]]; then
    for d in logs outbox review framework-review migration tasks; do
      if [[ -d "$BACKUP_DIR/$d" ]]; then
        rm -rf "$FRAMEWORK_DIR/$d"
        cp -a "$BACKUP_DIR/$d" "$FRAMEWORK_DIR/$d"
      fi
    done
    if [[ -f "$BACKUP_DIR/docs/orchestrator-run-summary.md" ]]; then
      mkdir -p "$FRAMEWORK_DIR/docs"
      cp -a "$BACKUP_DIR/docs/orchestrator-run-summary.md" "$FRAMEWORK_DIR/docs/"
    fi
    echo "Backup saved to $BACKUP_DIR"
  fi
fi

if [[ "$RUN_FLAG" -eq 1 ]]; then
  if ! git -C "$DEST_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Host project is not a git repo. Run 'git init' first." >&2
    exit 1
  fi

  if [[ -z "$PHASE" ]]; then
    PHASE="$(python3 - <<'PY' "$DEST_DIR"
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ignore = {"framework", "framework.zip", "install-framework.sh", ".git", ".gitignore", ".DS_Store"}

for entry in root.iterdir():
    if entry.name in ignore:
        continue
    print("legacy")
    sys.exit(0)

print("main")
PY
)"
  fi

  echo "Running orchestrator (phase: $PHASE)"
  python3 "$FRAMEWORK_DIR/orchestrator/orchestrator.py" \
    --config "$FRAMEWORK_DIR/orchestrator/orchestrator.yaml" \
    --phase "$PHASE"
fi
