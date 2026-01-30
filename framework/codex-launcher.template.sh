#!/usr/bin/env bash
# DEVFRAMEWORK:MANAGED
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CODEX_HOME="${CODEX_HOME:-$SCRIPT_DIR/framework/.codex}"
exec codex "$@"
