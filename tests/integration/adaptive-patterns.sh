#!/usr/bin/env bash
# component: adaptive-pattern-test-entry
# implements: ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: synthetic local roots only; optional provider is never installed by the test
# last_intent_review: 2026-09-28
# tag: review patterns integration
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${LINTEL_PYTHON:-$(command -v python3 || command -v python)}"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$ROOT/tests/integration/adaptive-patterns.py"
