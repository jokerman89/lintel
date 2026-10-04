#!/usr/bin/env bash
# component: core-boundary-method-test-entry
# implements: ADR-0006, ADR-0028, ADR-0033
# intent: .claude/plans/v2-findings/plan.md
# constraints: source/caller checks only; no native writer or customer communication
# last_intent_review: 2026-10-03
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
  exec python3 -B "$ROOT/tests/unit/core-boundary-methods.py" "$@"
elif command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
  exec python -B "$ROOT/tests/unit/core-boundary-methods.py" "$@"
else
  printf '%s\n' 'SKIP: Python 3.9+ required for core-boundary method checks'
  exit 2
fi
