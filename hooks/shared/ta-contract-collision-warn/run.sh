#!/usr/bin/env bash
# ta-contract-collision-warn — Lintel warn-only hook
# Surfaces when an Edit/Write hits a file with declared consumers.

set -euo pipefail
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"  # guard: unset under set -u aborts the hook (fail-closed)

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] && exit 0

# Check pack policy for interface_glob
interface_glob=""
if [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  # shellcheck disable=SC1091
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  interface_glob=$(resolve_pack_field tech_architecture.interface_glob 2>/dev/null || true)
fi

# Default glob if pack doesn't declare
interface_glob="${interface_glob:-**/*.proto,**/*.openapi.yaml,**/*.openapi.yml,**/api/**/*.go,**/api/**/*.ts}"

# Check if file matches any of the comma-separated globs
matches_interface=0
IFS=',' read -ra globs <<< "$interface_glob"
for g in "${globs[@]}"; do
  g=$(printf '%s' "$g" | tr -d '[:space:]')
  case "$file_edited" in
    $g) matches_interface=1; break ;;
  esac
done

# Check consumer registry
consumer_count=0
registry=".claude/runtime/state/ta/consumer-registry.json"
[ -f "$registry" ] || registry=".lintel/state/ta/consumer-registry.json" # legacy-fallback-ok
if [ -f "$registry" ]; then
  consumer_count=$(grep -c "\"interface\":\"$file_edited\"" "$registry" 2>/dev/null) || consumer_count=0
fi

if [ "$matches_interface" -eq 1 ] || [ "$consumer_count" -gt 0 ]; then
  audit_log "hooks" "ta_contract_collision_warn" "hook=ta-contract-collision-warn" "tier=warn" "file_edited=$file_edited" "consumer_count=$consumer_count"

  echo "WARN [Lintel hook ta-contract-collision-warn]: editing $file_edited"
  if [ "$consumer_count" -gt 0 ]; then
    echo "WARN: $consumer_count consumer(s) registered against this interface"
  fi
  echo "WARN: consider /li:ta single --action contract-collision to assess change impact, or pass --ignore-contract-collision to override."
fi

exit 0
