#!/usr/bin/env bash
# component: design-browser-pipeline
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P11.md
# constraints: browser-only A16; synthetic homes and explicit live browser selection
# last_intent_review: 2026-09-22
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
exec "$python" "$root/tests/integration/design-browser-pipeline.py" --root "$root" "$@"
