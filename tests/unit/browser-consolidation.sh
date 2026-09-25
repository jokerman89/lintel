#!/usr/bin/env bash
# component: browser-design-consolidation-tests
# implements: ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: source checks only; caller owns the synthetic environment
# last_intent_review: 2026-09-25
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
exec "$python" "$root/tests/unit/browser-consolidation.py"
