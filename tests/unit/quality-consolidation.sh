#!/usr/bin/env bash
# component: quality-workflow-test-entry
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: documentary checks only; no external services
# last_intent_review: 2026-09-25
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python_bin="${LINTEL_PYTHON:-python3}"
if ! "$python_bin" -I -B -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  if [ -n "${LINTEL_PYTHON:-}" ]; then
    echo 'ERROR: The selected LINTEL_PYTHON must run Python 3.9+.' >&2
    exit 127
  fi
  python_bin=python
  if ! "$python_bin" -I -B -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    echo 'ERROR: Python 3.9+ is required for quality workflow checks.' >&2
    exit 127
  fi
fi
"$python_bin" -I -B "$ROOT/tests/unit/quality-consolidation.py" --root "$ROOT" "$@"
