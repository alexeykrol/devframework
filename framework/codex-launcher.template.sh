#!/usr/bin/env bash
# DEVFRAMEWORK:MANAGED
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_CODEX_HOME="$SCRIPT_DIR/framework/.codex"

if [[ -n "${CODEX_HOME:-}" ]]; then
  EFFECTIVE_CODEX_HOME="$CODEX_HOME"
else
  GLOBAL_CODEX_HOME="$HOME/.codex"
  if [[ -d "$GLOBAL_CODEX_HOME" && -w "$GLOBAL_CODEX_HOME" ]]; then
    EFFECTIVE_CODEX_HOME="$GLOBAL_CODEX_HOME"
  else
    if mkdir -p "$GLOBAL_CODEX_HOME" 2>/dev/null && [[ -w "$GLOBAL_CODEX_HOME" ]]; then
      EFFECTIVE_CODEX_HOME="$GLOBAL_CODEX_HOME"
    else
      EFFECTIVE_CODEX_HOME="$PROJECT_CODEX_HOME"
    fi
  fi
fi

export CODEX_HOME="$EFFECTIVE_CODEX_HOME"
mkdir -p "$CODEX_HOME"
exec codex "$@"
