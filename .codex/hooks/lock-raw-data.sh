#!/usr/bin/env bash
set -euo pipefail

# Keep existing raw-data files immutable while leaving directories writable so
# fetch steps can add new raw files.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "${CODEX_PROJECT_DIR:-$PWD}")"
RAW_DIR="$ROOT/data/raw"

if [[ ! -d "$RAW_DIR" ]]; then
  exit 0
fi

find "$RAW_DIR" -type d -exec chmod u+rwx,go+rx {} + 2>/dev/null || true
find "$RAW_DIR" -type f -exec chmod a-w {} + 2>/dev/null || true

if command -v chflags >/dev/null 2>&1; then
  find "$RAW_DIR" -type f -exec chflags uchg {} + 2>/dev/null || true
fi
