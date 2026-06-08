#!/usr/bin/env bash
# tests/shape/cli-tiers-sync.sh
# Drift guard: the README capability table (between the CLI-TIERS markers) MUST match
# what cli_tiers_markdown_table generates from lib/cli-tiers.yaml — the single source.
# Stops the "honest table" from silently drifting from reality (the v4.9 audit's #1
# systemic issue) the moment a CLI tier changes. /li:welcome reads the same source.
# tag: onboarding cli-tiers drift-guard
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/cli-tiers-sync.sh"
echo "============================="

# shellcheck disable=SC1091
source lib/cli-tiers.sh
README="README.md"
[ -f "$README" ] || { fail "README.md missing"; exit 1; }

embedded=$(awk '
  /CLI-TIERS:START/ { grab = 1; next }
  /CLI-TIERS:END/   { grab = 0 }
  grab { sub(/\r$/, ""); print }
' "$README")

if [ -z "$embedded" ]; then
  fail "no CLI-TIERS marked section found in README.md"
else
  generated=$(cli_tiers_markdown_table)
  if [ "$embedded" = "$generated" ]; then
    pass "README CLI-TIERS table matches lib/cli-tiers.yaml (in sync)"
  else
    fail "README CLI-TIERS table is STALE vs lib/cli-tiers.yaml — refresh between the markers with:"
    echo "        source lib/cli-tiers.sh && cli_tiers_markdown_table"
    echo "      --- diff (README vs generated) ---"
    diff <(printf '%s\n' "$embedded") <(printf '%s\n' "$generated") | head -20
  fi
fi

echo ""
[ "$FAILED" -eq 0 ] && { echo "cli-tiers-sync: ALL PASS"; exit 0; } || { echo "cli-tiers-sync: FAILURES"; exit 1; }
