#!/usr/bin/env bash
# component: universal-trusted-tools-tests
# implements: ADR-0005, ADR-0007, ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: synthetic homes, repositories and command stubs only; no network
# last_intent_review: 2026-09-20
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for python in python3 python; do
  if command -v "$python" >/dev/null 2>&1 &&
      "$python" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    exec "$python" "$ROOT/tests/unit/universal-trusted-tools.py" "$BASH" "$@"
  fi
done
echo "ERROR: universal-trusted-tools requires Python 3.9 or newer; no checks ran" >&2
exit 1
