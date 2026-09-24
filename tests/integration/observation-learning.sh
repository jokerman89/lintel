#!/usr/bin/env bash
# component: observation-learning-tests
# implements: ADR-0006, ADR-0008, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: synthetic fixtures; does not activate hooks or prove P10/promotion integration
# last_intent_review: 2026-09-20
# tag: integration observation learning
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHONDONTWRITEBYTECODE=1 "${LINTEL_PYTHON:-python3}" \
  "$root/tests/integration/observation-learning.py" --root "$root" "$@"
