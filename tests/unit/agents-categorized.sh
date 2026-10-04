#!/usr/bin/env bash
# component: agent-inventory-entry
# implements: ADR-0028, ADR-0039
# intent: .claude/plans/v2-findings/plan.md
# constraints: derived source/member/catalog/native parity; no fixed portfolio floor
# last_intent_review: 2026-10-03
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
"${LINTEL_PYTHON:-python3}" -B "$REPO_ROOT/tests/unit/agent-inventory.py" "$@"
