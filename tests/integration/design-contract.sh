#!/usr/bin/env bash
# component: direct-design-contract-runner
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P11.md
# constraints: synthetic data only; no browser, renderer, installation or P08 execution
# last_intent_review: 2026-09-22
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${LINTEL_PYTHON:-python}"
if ! "$PYTHON" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  echo 'ERROR: Python 3.9+ is required for direct design-contract tests.' >&2
  exit 127
fi
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON" "$ROOT/tests/integration/design-contract.py" --root "$ROOT" --git "$(command -v git)" "$@"
