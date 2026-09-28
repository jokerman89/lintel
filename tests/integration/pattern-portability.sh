#!/usr/bin/env bash
# component: reusable-patterns-portability-test
# implements: ADR-0038
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; Python 3.10+ and Git are explicit prerequisites of this test
# last_intent_review: 2026-09-28
# tag: integration patterns portability
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.10+ is required for reusable-pattern portability tests.' >&2
  exit 1
fi
command -v git >/dev/null || { echo 'ERROR: git is required for reusable-pattern portability tests.' >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 "$python" -I -B "$root/tests/integration/pattern-portability.py"