#!/usr/bin/env bash
# component: adaptive-review-test-entry
# implements: ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: local synthetic packet checks; no models or network
# last_intent_review: 2026-09-28
# tag: review mars unit
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$ROOT/tests/unit/adaptive_review.py"
