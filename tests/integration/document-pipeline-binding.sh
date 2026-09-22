#!/usr/bin/env bash
# DESCRIPTION: Existing document pipeline source/work/profile binding without native rendering.
# TAGS: integration,codex-compatible
# component: document-pipeline-binding-entry
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: explicit synthetic fixture roots; no automatic dependencies or renderers
# last_intent_review: 2026-09-23
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || { printf '%s\n' "Missing Python 3.9+; no install attempted." >&2; exit 127; }
"$python" -I -B "$root/tests/integration/document-pipeline-binding.py" "$@"
