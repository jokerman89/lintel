#!/usr/bin/env bash
# component: no-merge-without-review-test
# implements: ADR-0028
# intent: hooks/shared/no-merge-without-review/HOOK.md
# constraints: isolated fixture; commands are inspected as data, never merged
# last_intent_review: 2026-09-20
# tags: hooks review evidence
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
"$python" "$root/tests/unit/review_evidence.py" hook
