#!/usr/bin/env bash
# component: universal-work-lifecycle-tests
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: synthetic repository, home, profile and ledger only
# last_intent_review: 2026-09-20
# tag: integration universal lifecycle
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/integration/universal-work-lifecycle.py" --root "$root" "$@"
