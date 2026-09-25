#!/usr/bin/env bash
# DESCRIPTION: Standalone Word/PPT source fidelity, P05/P07 controls, and optional native-artifact retention.
# TAGS: integration,codex-compatible
# component: document-format-pipeline-entry
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: explicit synthetic fixture root; no installation or native-render claim
# last_intent_review: 2026-09-22
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || {
  printf '%s\n' "Missing Python 3.9+; no dependency was installed." >&2
  exit 127
}
exec "$python" -I "$root/tests/integration/document-format-pipeline.py" "$@"
