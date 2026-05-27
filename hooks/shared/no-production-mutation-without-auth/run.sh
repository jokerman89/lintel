#!/usr/bin/env bash
# no-production-mutation-without-auth — JStack warn-only hook
set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

matched=""
# Heuristic patterns
echo "$CMD" | grep -qE 'kubectl.*-n\s+(production|prod)' && matched="kubectl-prod"
echo "$CMD" | grep -qE 'terraform\s+(apply|destroy).*(production|prod)' && matched="terraform-prod"
echo "$CMD" | grep -qE 'gh\s+workflow\s+run\s+deploy.*prod' && matched="gh-deploy-prod"
echo "$CMD" | grep -qE 'az\s+.*\s+--subscription\s+.*(production|prod)' && matched="az-prod-sub"
echo "$CMD" | grep -qE '(psql|pg_dump|pg_restore).*(production|prod)' && matched="prod-pgdb"

# Operator-extendable pattern file
PATTERNS="$JSTACK_HOME/production-mutation-patterns.txt"
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
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"no-production-mutation-without-auth","tier":"warn","ts":"%s","pattern":"%s","cmd_preview":"%s"}\n' \
    "$ts" "$matched" "$(echo "$CMD" | head -c 120)" >> "$AUDIT"
  echo "WARN [JStack hook]: production mutation pattern detected ($matched)"
  echo "WARN: Layer 2 requires explicit per-call auth. Confirm intentional + authorized."
fi

exit 0
