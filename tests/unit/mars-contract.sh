#!/usr/bin/env bash
# tests/unit/mars-contract.sh — MARS roster, offer gate and panel close-state behavior.
# tag: mars unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$ROOT/tests/unit/mars_contract.py"
