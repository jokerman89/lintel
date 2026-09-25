#!/usr/bin/env bash
# tests/unit/mars-hooks.sh — MARS offer hooks and REVIEW's method-packet prompts.
# tag: mars review unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$ROOT/tests/unit/mars_hooks.py"
