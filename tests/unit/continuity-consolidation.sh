#!/usr/bin/env bash
# component: continuity-consolidation-test-entry
# implements: ADR-0006, ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: ordinary repository check; caller supplies the approved synthetic environment
# last_intent_review: 2026-09-25
# tag: continuity checkpoint memory freeze
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
exec "$python" -I -B "$root/tests/unit/continuity-consolidation.py" "$@"
