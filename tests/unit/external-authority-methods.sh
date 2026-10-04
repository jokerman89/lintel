#!/usr/bin/env bash
# component: external-authority-method-test
# implements: ADR-0024, ADR-0028, ADR-0029
# intent: docs/spec-kit.md, docs/compliance.md
# constraints: source-contract checks, not live host or model evidence
# last_intent_review: 2026-10-03
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/unit/external-authority-methods.py" "$@"
