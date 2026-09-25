#!/usr/bin/env bash
# component: url-policy-test
# implements: ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: injected single-hop transport; no sockets or network
# last_intent_review: 2026-09-20
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.10+ is required for url-policy tests.' >&2
  exit 1
fi
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/unit/url-policy.py"
