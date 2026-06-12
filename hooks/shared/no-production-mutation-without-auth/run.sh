#!/usr/bin/env bash
# no-production-mutation-without-auth — Lintel warn-only hook
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

matched=""
# Heuristic patterns
echo "$CMD" | grep -qE 'kubectl.*-n\s+(production|prod)' && matched="kubectl-prod"
echo "$CMD" | grep -qE 'terraform\s+(apply|destroy).*(production|prod)' && matched="terraform-prod"
echo "$CMD" | grep -qE 'gh\s+workflow\s+run\s+deploy.*prod' && matched="gh-deploy-prod"
echo "$CMD" | grep -qE 'az\s+.*\s+--subscription\s+.*(production|prod)' && matched="az-prod-sub"
echo "$CMD" | grep -qE '(psql|pg_dump|pg_restore).*(production|prod)' && matched="prod-pgdb"

# Operator-extendable pattern file
PATTERNS="$LINTEL_HOME/production-mutation-patterns.txt"
if [ -z "$matched" ] && [ -f "$PATTERNS" ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    [[ "$pat" == \#* ]] && continue
    if echo "$CMD" | grep -qE "$pat"; then
      matched="custom:$pat"
      break
    fi
  done < "$PATTERNS"
fi

if [ -n "$matched" ]; then
  audit_log "hooks" "no_production_mutation_without_auth" "hook=no-production-mutation-without-auth" "tier=warn" "pattern=$matched" "cmd_preview=$(echo "$CMD" | head -c 120)"
  echo "WARN [Lintel hook]: production mutation pattern detected ($matched)"
  echo "WARN: Layer 2 requires explicit per-call auth. Confirm intentional + authorized."
fi

exit 0
