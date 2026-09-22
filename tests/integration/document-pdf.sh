#!/usr/bin/env bash
# DESCRIPTION: Standalone PDF preparation, text/page/origin checks and non-clearing visual limits.
# TAGS: integration,codex-compatible
# component: document-pdf-entry
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: explicit local fixtures; no browser/app/raster launch or automatic installation
# last_intent_review: 2026-09-22
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
command -v "$python" >/dev/null 2>&1 || { printf '%s\n' "Missing Python 3.9+; no install attempted." >&2; exit 127; }
"$python" -I -B "$root/tests/integration/document-pdf.py" "$@"
command -v node >/dev/null 2>&1 || { printf '%s\n' "Missing Node.js 22+; no install attempted." >&2; exit 127; }
node --test --test-reporter=tap "$root/tests/integration/document-pdf.test.mjs"
