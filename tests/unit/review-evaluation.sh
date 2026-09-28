#!/usr/bin/env bash
# tests/unit/review-evaluation.sh — offline review/benchmark scorer: denominators, provenance and refusals.
# tag: review evaluation unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$ROOT/tests/unit/review_evaluation.py"
