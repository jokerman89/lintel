#!/usr/bin/env bash
# tests/unit/review-method.sh — shared Review Method: catalog, packet parity, coverage and calibration.
# tag: review mars unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$ROOT/tests/unit/review_method.py"
