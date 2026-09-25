#!/usr/bin/env bash
# TAGS: unit,ci
# component: ci-matrix-planner-test
# implements: ADR-0037
# intent: .claude/decisions/0037-pr-ci-tiering.md
# constraints: temporary git repositories only; no network
# last_intent_review: 2026-09-25
# Prevents a pull-request matrix that drops macOS or Windows for code changes, drops any suite part
# on Ubuntu, or narrows the matrix when the diff cannot be computed.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.9+ is required for the CI matrix planner tests.' >&2
  exit 1
fi
command -v git >/dev/null || { echo 'ERROR: git is required for the CI matrix planner tests.' >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/unit/ci-matrix.py"
