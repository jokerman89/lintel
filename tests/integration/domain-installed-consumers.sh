#!/usr/bin/env bash
# DESCRIPTION: Actual P10-installed domain discovery, evidence/refusal, receiver and cold-handoff consumers.
# TAGS: integration,p09-installed
# component: installed-domain-consumer-runner
# implements: ADR-0028, ADR-0030
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: no LINTEL selectors; native PS7 on Windows or explicit lifecycle surface
# last_intent_review: 2026-09-24
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 &&
    "$candidate" -I -B -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
[ -n "$PYTHON" ] || { echo 'ERROR: installed domain checks require Python 3.9+' >&2; exit 2; }
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" "$ROOT/tests/integration/domain-installed-consumers.py" \
  --bash "$(command -v bash)" --git "$(command -v git)" "$@"
