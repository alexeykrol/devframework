#!/usr/bin/env bash
set -euo pipefail

REPO="${FRAMEWORK_REPO:-alexeykrol/devframework}"
REF="${FRAMEWORK_REF:-main}"
DEST_DIR="${FRAMEWORK_DEST:-.}"
PHASE="${FRAMEWORK_PHASE:-}"
TOKEN="${FRAMEWORK_TOKEN:-${GITHUB_TOKEN:-}}"
PYTHON_BIN="${FRAMEWORK_PYTHON:-python3}"

ZIP_PATH=""
UPDATE_FLAG=0
RUN_FLAG=1
SKIP_INSTALL=0
TMP_ZIP=""

usage() {
  cat <<'EOF'
Usage: ./install-framework.sh [options]

Options:
  --repo <owner/name>    GitHub repo (default: alexeykrol/devframework)
  --ref <ref>            Branch or tag (default: main)
  --zip <path>           Use local framework.zip instead of downloading
  --dest <dir>           Install destination (default: .)
  --token <token>        GitHub token for private repos (or env FRAMEWORK_TOKEN/GITHUB_TOKEN)
  --update               Replace existing framework (backup is created)
  --run                  Run orchestrator after install (default)
  --no-run               Skip running orchestrator
  --phase <main|legacy>  Force phase when running
  --legacy               Shortcut for --phase legacy
  --main                 Shortcut for --phase main
  -h, --help             Show help

Env overrides:
  FRAMEWORK_REPO, FRAMEWORK_REF, FRAMEWORK_DEST, FRAMEWORK_PHASE
  FRAMEWORK_TOKEN (or GITHUB_TOKEN)
  FRAMEWORK_PYTHON (default: python3)
  FRAMEWORK_UPDATE=1, FRAMEWORK_RUN=1 (set to 0 to skip run)
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
  local accept_raw="${2:-}"
  if command -v curl >/dev/null 2>&1; then
    if [[ -n "$TOKEN" ]]; then
      if [[ -n "$accept_raw" ]]; then
        curl -fsSL -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.raw" "$url"
      else
        curl -fsSL -H "Authorization: token $TOKEN" "$url"
      fi
    else
      curl -fsSL "$url"
    fi
    return $?
  fi
  "$PYTHON_BIN" - <<'PY' "$url" "$TOKEN" "$accept_raw"
import sys
import urllib.request
url = sys.argv[1]
token = sys.argv[2] if len(sys.argv) > 2 else ""
accept_raw = sys.argv[3] if len(sys.argv) > 3 else ""
headers = {}
if token:
    headers["Authorization"] = f"token {token}"
if accept_raw:
    headers["Accept"] = "application/vnd.github.raw"
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        sys.stdout.buffer.write(resp.read())
except Exception as exc:
    sys.stderr.write(str(exc))
    sys.exit(1)
PY
}

script_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

zip_version() {
  local zip_path="$1"
  "$PYTHON_BIN" - <<'PY' "$zip_path"
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1])
if not zip_path.exists():
    sys.exit(0)
try:
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open("framework/VERSION") as f:
            value = f.read().decode("utf-8", errors="ignore").strip()
            if value:
                print(value)
except Exception:
    pass
PY
}

has_embedded_zip() {
  grep -q "^__FRAMEWORK_ZIP_PAYLOAD_BEGIN__$" "$1"
}

extract_embedded_zip() {
  local script_path="$1"
  local out_path="$2"
  "$PYTHON_BIN" - <<'PY' "$script_path" "$out_path"
import base64
import sys
from pathlib import Path

script_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
begin = "__FRAMEWORK_ZIP_PAYLOAD_BEGIN__"
end = "__FRAMEWORK_ZIP_PAYLOAD_END__"
data_lines = []
found = False
for line in script_path.read_text(encoding="utf-8", errors="ignore").splitlines():
    if line == begin:
        found = True
        continue
    if line == end:
        break
    if found:
        data_lines.append(line.strip())
if not data_lines:
    sys.exit(1)
payload = "".join(data_lines).encode("utf-8")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_bytes(base64.b64decode(payload))
PY
}

CLEANUP_FILES=()
cleanup_add() {
  CLEANUP_FILES+=("$1")
}
cleanup_run() {
  for f in "${CLEANUP_FILES[@]}"; do
    rm -f "$f"
  done
}
trap cleanup_run EXIT

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
    --token)
      TOKEN="$2"
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
    --no-run)
      RUN_FLAG=0
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
if [[ -n "${FRAMEWORK_RUN:-}" ]]; then
  if truthy "${FRAMEWORK_RUN}"; then
    RUN_FLAG=1
  else
    RUN_FLAG=0
  fi
fi

ZIP_URL="${FRAMEWORK_ZIP_URL:-}"
VERSION_URL="${FRAMEWORK_VERSION_URL:-}"
ZIP_ACCEPT=""
VERSION_ACCEPT=""

if [[ -z "$ZIP_URL" ]]; then
  if [[ -n "$TOKEN" ]]; then
    ZIP_URL="https://api.github.com/repos/${REPO}/contents/framework.zip?ref=${REF}"
    ZIP_ACCEPT="raw"
  else
    ZIP_URL="https://github.com/${REPO}/raw/${REF}/framework.zip"
  fi
fi

if [[ -z "$VERSION_URL" ]]; then
  if [[ -n "$TOKEN" ]]; then
    VERSION_URL="https://api.github.com/repos/${REPO}/contents/framework/VERSION?ref=${REF}"
    VERSION_ACCEPT="raw"
  else
    VERSION_URL="https://raw.githubusercontent.com/${REPO}/${REF}/framework/VERSION"
  fi
fi

FRAMEWORK_DIR="${DEST_DIR%/}/framework"
LOCAL_VERSION=""
REMOTE_VERSION=""
ZIP_VERSION=""

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found: $PYTHON_BIN" >&2
  exit 1
fi

SCRIPT_DIR="$(script_dir)"

if [[ -z "$ZIP_PATH" && -f "$SCRIPT_DIR/framework.zip" ]]; then
  ZIP_PATH="$SCRIPT_DIR/framework.zip"
fi

if [[ -z "$ZIP_PATH" ]]; then
  SCRIPT_PATH="$SCRIPT_DIR/$(basename "${BASH_SOURCE[0]}")"
  if has_embedded_zip "$SCRIPT_PATH"; then
    TMP_ZIP="$(mktemp -t devframework.XXXXXX.zip)"
    cleanup_add "$TMP_ZIP"
    if extract_embedded_zip "$SCRIPT_PATH" "$TMP_ZIP"; then
      ZIP_PATH="$TMP_ZIP"
    fi
  fi
fi

if [[ -f "$FRAMEWORK_DIR/VERSION" ]]; then
  LOCAL_VERSION="$(head -n1 "$FRAMEWORK_DIR/VERSION" | tr -d '\r')"
fi

if [[ -n "$ZIP_PATH" ]]; then
  ZIP_VERSION="$(zip_version "$ZIP_PATH")"
fi

if [[ -z "$ZIP_PATH" ]]; then
  if REMOTE_VERSION="$(fetch_url "$VERSION_URL" "$VERSION_ACCEPT" 2>/dev/null)"; then
    REMOTE_VERSION="$(printf '%s' "$REMOTE_VERSION" | tr -d '\r' | head -n1)"
  else
    REMOTE_VERSION=""
  fi
fi

if [[ -d "$FRAMEWORK_DIR" && "$UPDATE_FLAG" -ne 1 ]]; then
  if [[ -n "$ZIP_PATH" ]]; then
    if [[ -n "$LOCAL_VERSION" && -n "$ZIP_VERSION" && "$LOCAL_VERSION" == "$ZIP_VERSION" ]]; then
      echo "Framework is already up to date ($LOCAL_VERSION)."
      if [[ "$RUN_FLAG" -ne 1 ]]; then
        exit 0
      fi
      SKIP_INSTALL=1
    else
      UPDATE_FLAG=1
    fi
  fi

  if [[ -z "$ZIP_PATH" && -n "$REMOTE_VERSION" ]]; then
    if [[ -n "$LOCAL_VERSION" && "$LOCAL_VERSION" == "$REMOTE_VERSION" ]]; then
      echo "Framework is already up to date ($LOCAL_VERSION)."
      if [[ "$RUN_FLAG" -ne 1 ]]; then
        exit 0
      fi
      SKIP_INSTALL=1
    else
      echo "Updating framework from $LOCAL_VERSION to $REMOTE_VERSION"
      UPDATE_FLAG=1
    fi
  elif [[ -z "$ZIP_PATH" ]]; then
    echo "Framework already installed at $FRAMEWORK_DIR" >&2
    echo "Remote version unknown. Re-run with --update or --zip to replace." >&2
    if [[ "$RUN_FLAG" -eq 1 ]]; then
      SKIP_INSTALL=1
    else
      exit 1
    fi
  fi
fi

if [[ -d "$FRAMEWORK_DIR" && "$UPDATE_FLAG" -eq 1 ]]; then
  if [[ -n "$LOCAL_VERSION" && -n "$ZIP_VERSION" && "$LOCAL_VERSION" == "$ZIP_VERSION" ]]; then
    echo "Framework is already up to date ($LOCAL_VERSION)."
    if [[ "$RUN_FLAG" -ne 1 ]]; then
      exit 0
    fi
    SKIP_INSTALL=1
  elif [[ -n "$LOCAL_VERSION" && -n "$REMOTE_VERSION" && "$LOCAL_VERSION" == "$REMOTE_VERSION" ]]; then
    echo "Framework is already up to date ($LOCAL_VERSION)."
    if [[ "$RUN_FLAG" -ne 1 ]]; then
      exit 0
    fi
    SKIP_INSTALL=1
  fi
fi

if [[ "$SKIP_INSTALL" -ne 1 ]]; then
  DOWNLOAD_ZIP=""
  if [[ -z "$ZIP_PATH" ]]; then
    DOWNLOAD_ZIP="$(mktemp -t devframework.XXXXXX.zip)"
    cleanup_add "$DOWNLOAD_ZIP"
    if ! fetch_url "$ZIP_URL" "$ZIP_ACCEPT" > "$DOWNLOAD_ZIP"; then
      echo "Failed to download framework zip from $ZIP_URL" >&2
      if [[ -z "$TOKEN" ]]; then
        echo "If the repo is private, set FRAMEWORK_TOKEN or GITHUB_TOKEN." >&2
      fi
      exit 1
    fi
    ZIP_PATH="$DOWNLOAD_ZIP"
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

  "$PYTHON_BIN" - <<'PY' "$ZIP_PATH" "$DEST_DIR"
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
    PHASE="$("$PYTHON_BIN" - <<'PY' "$DEST_DIR"
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
  "$PYTHON_BIN" "$FRAMEWORK_DIR/orchestrator/orchestrator.py" \
    --config "$FRAMEWORK_DIR/orchestrator/orchestrator.json" \
    --phase "$PHASE"
fi

if [[ -f "$FRAMEWORK_DIR/VERSION" ]]; then
  VERSION="$(head -n1 "$FRAMEWORK_DIR/VERSION" | tr -d '\r')"
  if [[ -n "$VERSION" ]]; then
    echo "Framework version: $VERSION"
  fi
fi

exit 0
__FRAMEWORK_ZIP_PAYLOAD_BEGIN__
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
l9y2ADCghyOJ5g9hpzl2FDZw3WxgzKQPgCl3u3jvqEkCjtGp/ZJ6pogL+ARQSwMEFAAAAAgAErA3
XL6InR6KAAAALQEAADIAAABmcmFtZXdvcmsvZnJhbWV3b3JrLXJldmlldy9mcmFtZXdvcmstYnVn
LXJlcG9ydC5tZMWOPQrCQBBG+5xiYBstRLRMpxDBTtQLLJsxLGadZX5icnuTtfEGdo/H++BzcGKf
8E38hKN1cMVMrFXlHJxFDGFXbeAetcd6hhsOyFGnhZshtvgKCKueOtmKpeR5WpdMMQsoAWNmai2U
cTNmDIrtwoeg5vvSmnw1BG9SwgtTJpnNI471z5X9v698AFBLAwQUAAAACAASsDdcJIKynJIAAADR
AAAANAAAAGZyYW1ld29yay9mcmFtZXdvcmstcmV2aWV3L2ZyYW1ld29yay1sb2ctYW5hbHlzaXMu
bWRFjc0KwkAMhO99ikDP4t2booLgoVhfIGxjG/YnkmwV397dinr7MjOZaeGoGOkp6uEsI2wThpex
NU3bwmVOECnjgBmb1XKe9ptC3YRGFf7PD1JjSVXsM2qmYfE5sU2Va99BVdRgXVYkYmCyElmcXRDn
aYCM5n/ilSOnscQ70ptoxOTo6/Wz3cmVFVCRDA5n+7S9AVBLAwQUAAAACACssTdcNvCPOWwAAACM
AAAAJAAAAGZyYW1ld29yay9taWdyYXRpb24vcm9sbGJhY2stcGxhbi5tZFNWCMrPyUlKTM5WCMhJ
zOPiUlZWuLD4YuOF3Rf2Xdh0YcfFfoUL+y42Xdh1YQOQ3MClqwBRsuLChgubL+xAlTTUVOAy0oSq
mASUagRCoMSFvWDDdl/YCmTtuLBVAWj+PrDUvov9IKGL/SCDAVBLAwQUAAAACACssTdcdtnx12MA
AAB7AAAAHwAAAGZyYW1ld29yay9taWdyYXRpb24vYXBwcm92YWwubWRTVnAsKCjKL0vM4eJSVla4
sODC1osdF7Ze2Hthx4WtXLoK0QqxUBWpKVBuUGpWanIJkAvWMOvCvgt7gBCo5WLThQ0XG4AadwBV
QmTnA2W3XNh/YcfFxos9CvoKQM4GkDKQAgBQSwMEFAAAAAgArLE3XGYDdLS4AAAANwEAACcAAABm
cmFtZXdvcmsvbWlncmF0aW9uL2xlZ2FjeS10ZWNoLXNwZWMubWSVjz0KwkAUhPuc4kGapBAvYqVe
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
YW1ld29yay1maXgubWRQSwECFAMUAAAACAC7BThc9Pmx8G4BAACrAgAAHwAAAAAAAAAAAAAApIHE
BAAAZnJhbWV3b3JrL3Rhc2tzL2xlZ2FjeS1hcHBseS5tZFBLAQIUAxQAAAAIACCdN1y+cQwcGQEA
AMMBAAAhAAAAAAAAAAAAAACkgW8GAABmcmFtZXdvcmsvdGFza3MvYnVzaW5lc3MtbG9naWMubWRQ
SwECFAMUAAAACACxBThcprXUZD0BAADJAQAAHwAAAAAAAAAAAAAApIHHBwAAZnJhbWV3b3JrL3Rh
c2tzL2xlZ2FjeS1hdWRpdC5tZFBLAQIUAxQAAAAIAPcWOFw90rjStAEAAJsDAAAjAAAAAAAAAAAA
AACkgUEJAABmcmFtZXdvcmsvdGFza3MvZnJhbWV3b3JrLXJldmlldy5tZFBLAQIUAxQAAAAIALkF
OFxAwJTwNwEAADUCAAAoAAAAAAAAAAAAAACkgTYLAABmcmFtZXdvcmsvdGFza3MvbGVnYWN5LW1p
Z3JhdGlvbi1wbGFuLm1kUEsBAhQDFAAAAAgApQU4XLlj7wvIAQAAMwMAAB4AAAAAAAAAAAAAAKSB
swwAAGZyYW1ld29yay90YXNrcy9yZXZpZXctcHJlcC5tZFBLAQIUAxQAAAAIAKgFOFw/7o3c6gEA
AK4DAAAZAAAAAAAAAAAAAACkgbcOAABmcmFtZXdvcmsvdGFza3MvcmV2aWV3Lm1kUEsBAhQDFAAA
AAgAIJ03XP51FpMrAQAA4AEAABwAAAAAAAAAAAAAAKSB2BAAAGZyYW1ld29yay90YXNrcy9kYi1z
Y2hlbWEubWRQSwECFAMUAAAACAAgnTdcVnRtrgsBAACnAQAAFQAAAAAAAAAAAAAApIE9EgAAZnJh
bWV3b3JrL3Rhc2tzL3VpLm1kUEsBAhQDFAAAAAgAogU4XHOTBULnAQAAfAMAABwAAAAAAAAAAAAA
AKSBexMAAGZyYW1ld29yay90YXNrcy90ZXN0LXBsYW4ubWRQSwECFAMUAAAACAArCjhcIWTlC/sA
AADNAQAAGQAAAAAAAAAAAAAApIGcFQAAZnJhbWV3b3JrL3Rvb2xzL1JFQURNRS5tZFBLAQIUAxQA
AAAIACgKOFxEXqyfBAYAADUTAAAhAAAAAAAAAAAAAADtgc4WAABmcmFtZXdvcmsvdG9vbHMvcHVi
bGlzaC1yZXBvcnQucHlQSwECFAMUAAAACACmCjhco+sqBUsHAAAuFgAAIAAAAAAAAAAAAAAA7YER
HQAAZnJhbWV3b3JrL3Rvb2xzL2V4cG9ydC1yZXBvcnQucHlQSwECFAMUAAAACADzBThcXqvisPwB
AAB5AwAAJgAAAAAAAAAAAAAApIGaJAAAZnJhbWV3b3JrL2RvY3MvcmVsZWFzZS1jaGVja2xpc3Qt
cnUubWRQSwECFAMUAAAACADwBThc4PpBOCACAAAgBAAAJwAAAAAAAAAAAAAApIHaJgAAZnJhbWV3
b3JrL2RvY3MvZGVmaW5pdGlvbi1vZi1kb25lLXJ1Lm1kUEsBAhQDFAAAAAgAAQY4XJks/fAQDAAA
kSAAACYAAAAAAAAAAAAAAKSBPykAAGZyYW1ld29yay9kb2NzL29yY2hlc3RyYXRvci1wbGFuLXJ1
Lm1kUEsBAhQDFAAAAAgAz7E3XKOUVkVoCQAAMBoAACMAAAAAAAAAAAAAAKSBkzUAAGZyYW1ld29y
ay9kb2NzL2Rlc2lnbi1wcm9jZXNzLXJ1Lm1kUEsBAhQDFAAAAAgAMZg3XGMqWvEOAQAAfAEAACcA
AAAAAAAAAAAAAKSBPD8AAGZyYW1ld29yay9kb2NzL29ic2VydmFiaWxpdHktcGxhbi1ydS5tZFBL
AQIUAxQAAAAIAPQWOFz40ezD0QYAAOISAAAqAAAAAAAAAAAAAACkgY9AAABmcmFtZXdvcmsvZG9j
cy9vcmNoZXN0cmF0aW9uLWNvbmNlcHQtcnUubWRQSwECFAMUAAAACAD2qjdcVJJVr24AAACSAAAA
HwAAAAAAAAAAAAAApIGoRwAAZnJhbWV3b3JrL3Jldmlldy9xYS1jb3ZlcmFnZS5tZFBLAQIUAxQA
AAAIAM8FOFwletu5iQEAAJECAAAgAAAAAAAAAAAAAACkgVNIAABmcmFtZXdvcmsvcmV2aWV3L3Jl
dmlldy1icmllZi5tZFBLAQIUAxQAAAAIAMoFOFxRkLtO4gEAAA8EAAAbAAAAAAAAAAAAAACkgRpK
AABmcmFtZXdvcmsvcmV2aWV3L3J1bmJvb2subWRQSwECFAMUAAAACABVqzdctYfx1doAAABpAQAA
JgAAAAAAAAAAAAAApIE1TAAAZnJhbWV3b3JrL3Jldmlldy9jb2RlLXJldmlldy1yZXBvcnQubWRQ
SwECFAMUAAAACABYqzdcv8DUCrIAAAC+AQAAHgAAAAAAAAAAAAAApIFTTQAAZnJhbWV3b3JrL3Jl
dmlldy9idWctcmVwb3J0Lm1kUEsBAhQDFAAAAAgAxAU4XItx7E2IAgAAtwUAABoAAAAAAAAAAAAA
AKSBQU4AAGZyYW1ld29yay9yZXZpZXcvUkVBRE1FLm1kUEsBAhQDFAAAAAgAzQU4XOlQnaS/AAAA
lwEAABoAAAAAAAAAAAAAAKSBAVEAAGZyYW1ld29yay9yZXZpZXcvYnVuZGxlLm1kUEsBAhQDFAAA
AAgA5Ks3XD2gS2iwAAAADwEAACAAAAAAAAAAAAAAAKSB+FEAAGZyYW1ld29yay9yZXZpZXcvdGVz
dC1yZXN1bHRzLm1kUEsBAhQDFAAAAAgAU6s3XFFQbDN0AQAAdwIAAB0AAAAAAAAAAAAAAKSB5lIA
AGZyYW1ld29yay9yZXZpZXcvdGVzdC1wbGFuLm1kUEsBAhQDFAAAAAgA46s3XL0U8m2fAQAA2wIA
ABsAAAAAAAAAAAAAAKSBlVQAAGZyYW1ld29yay9yZXZpZXcvaGFuZG9mZi5tZFBLAQIUAxQAAAAI
ABKwN1zOOHEZXwAAAHEAAAAwAAAAAAAAAAAAAACkgW1WAABmcmFtZXdvcmsvZnJhbWV3b3JrLXJl
dmlldy9mcmFtZXdvcmstZml4LXBsYW4ubWRQSwECFAMUAAAACADyFjhcKjIhkSICAADcBAAAJQAA
AAAAAAAAAAAApIEaVwAAZnJhbWV3b3JrL2ZyYW1ld29yay1yZXZpZXcvcnVuYm9vay5tZFBLAQIU
AxQAAAAIANQFOFxWaNsV3gEAAH8DAAAkAAAAAAAAAAAAAACkgX9ZAABmcmFtZXdvcmsvZnJhbWV3
b3JrLXJldmlldy9SRUFETUUubWRQSwECFAMUAAAACADwFjhc+LdiWOsAAADiAQAAJAAAAAAAAAAA
AAAApIGfWwAAZnJhbWV3b3JrL2ZyYW1ld29yay1yZXZpZXcvYnVuZGxlLm1kUEsBAhQDFAAAAAgA
ErA3XL6InR6KAAAALQEAADIAAAAAAAAAAAAAAKSBzFwAAGZyYW1ld29yay9mcmFtZXdvcmstcmV2
aWV3L2ZyYW1ld29yay1idWctcmVwb3J0Lm1kUEsBAhQDFAAAAAgAErA3XCSCspySAAAA0QAAADQA
AAAAAAAAAAAAAKSBpl0AAGZyYW1ld29yay9mcmFtZXdvcmstcmV2aWV3L2ZyYW1ld29yay1sb2ct
YW5hbHlzaXMubWRQSwECFAMUAAAACACssTdcNvCPOWwAAACMAAAAJAAAAAAAAAAAAAAApIGKXgAA
ZnJhbWV3b3JrL21pZ3JhdGlvbi9yb2xsYmFjay1wbGFuLm1kUEsBAhQDFAAAAAgArLE3XHbZ8ddj
AAAAewAAAB8AAAAAAAAAAAAAAKSBOF8AAGZyYW1ld29yay9taWdyYXRpb24vYXBwcm92YWwubWRQ
SwECFAMUAAAACACssTdcZgN0tLgAAAA3AQAAJwAAAAAAAAAAAAAApIHYXwAAZnJhbWV3b3JrL21p
Z3JhdGlvbi9sZWdhY3ktdGVjaC1zcGVjLm1kUEsBAhQDFAAAAAgArLE3XKpv6S2PAAAAtgAAADAA
AAAAAAAAAAAAAKSB1WAAAGZyYW1ld29yay9taWdyYXRpb24vbGVnYWN5LW1pZ3JhdGlvbi1wcm9w
b3NhbC5tZFBLAQIUAxQAAAAIAOoFOFzInAvvPAMAAEwHAAAeAAAAAAAAAAAAAACkgbJhAABmcmFt
ZXdvcmsvbWlncmF0aW9uL3J1bmJvb2subWRQSwECFAMUAAAACACssTdcE48edrIAAADhAAAAKAAA
AAAAAAAAAAAApIEqZQAAZnJhbWV3b3JrL21pZ3JhdGlvbi9sZWdhY3ktZ2FwLXJlcG9ydC5tZFBL
AQIUAxQAAAAIAOUFOFzK6aNraAMAAHEHAAAdAAAAAAAAAAAAAACkgSJmAABmcmFtZXdvcmsvbWln
cmF0aW9uL1JFQURNRS5tZFBLAQIUAxQAAAAIAKyxN1zMc8cLowAAAOkAAAAmAAAAAAAAAAAAAACk
gcVpAABmcmFtZXdvcmsvbWlncmF0aW9uL2xlZ2FjeS1zbmFwc2hvdC5tZFBLAQIUAxQAAAAIAKyx
N1yUse0xhwAAAKYAAAAsAAAAAAAAAAAAAACkgaxqAABmcmFtZXdvcmsvbWlncmF0aW9uL2xlZ2Fj
eS1taWdyYXRpb24tcGxhbi5tZFBLAQIUAxQAAAAIAKyxN1zSm5hPcgAAAIoAAAAtAAAAAAAAAAAA
AACkgX1rAABmcmFtZXdvcmsvbWlncmF0aW9uL2xlZ2FjeS1yaXNrLWFzc2Vzc21lbnQubWRQSwEC
FAMUAAAACACdVDhcskMtQd4CAACkEQAAKAAAAAAAAAAAAAAApIE6bAAAZnJhbWV3b3JrL29yY2hl
c3RyYXRvci9vcmNoZXN0cmF0b3IuanNvblBLAQIUAxQAAAAIAMgWOFy4Q7b6WRIAAHZIAAAmAAAA
AAAAAAAAAADtgV5vAABmcmFtZXdvcmsvb3JjaGVzdHJhdG9yL29yY2hlc3RyYXRvci5weVBLAQIU
AxQAAAAIAKBUOFyjDssgBAQAAFwPAAAoAAAAAAAAAAAAAACkgfuBAABmcmFtZXdvcmsvb3JjaGVz
dHJhdG9yL29yY2hlc3RyYXRvci55YW1sUEsFBgAAAAA0ADQAVxAAAEWGAAAAAA==
__FRAMEWORK_ZIP_PAYLOAD_END__
