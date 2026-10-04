#!/usr/bin/env bash
# component: selected-external-authority-test
# implements: ADR-0024, ADR-0028, ADR-0029
# intent: docs/spec-kit.md, docs/enterprise-profile-value.md
# constraints: fixture-only Git/profile creation; no external command or hook activation
# last_intent_review: 2026-10-03
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/integration/external-authority.py" "$@"
