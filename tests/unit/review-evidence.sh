#!/usr/bin/env bash
# component: review-evidence-test
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: isolated local repositories and homes; no external services
# last_intent_review: 2026-09-20
# tags: review evidence
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
"$python" "$root/tests/unit/review_evidence.py" evidence
