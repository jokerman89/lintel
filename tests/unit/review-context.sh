#!/usr/bin/env bash
# tests/unit/review-context.sh — evidenced review depth and the optional pattern-provider adapter.
# tag: review unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$ROOT/tests/unit/review_context.py"
