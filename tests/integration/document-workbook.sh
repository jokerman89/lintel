#!/usr/bin/env bash
# DESCRIPTION: Standalone workbook formula/cache/source integrity; no native calculation or renderer claim.
# TAGS: integration,codex-compatible
# component: document-workbook-entry
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: owned synthetic fixtures; no application launch or dependency install
# last_intent_review: 2026-09-22
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || {
  printf '%s\n' "Missing Python 3.9+; no dependency was installed." >&2
  exit 127
}
exec "$python" -I -B "$root/tests/integration/document-workbook.py" "$@"
