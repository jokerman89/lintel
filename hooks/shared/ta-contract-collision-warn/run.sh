#!/usr/bin/env bash
# ta-contract-collision-warn — Lintel warn-only hook
# Surfaces when an Edit/Write hits a file with declared consumers.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
AUDIT="$LINTEL_HOME/audit/hooks.jsonl"
mkdir -p "$LINTEL_HOME/audit"

file_edited="${1:-}"
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
registry=".lintel/state/ta/consumer-registry.json"
if [ -f "$registry" ]; then
  consumer_count=$(grep -c "\"interface\":\"$file_edited\"" "$registry" 2>/dev/null || echo 0)
fi

if [ "$matches_interface" -eq 1 ] || [ "$consumer_count" -gt 0 ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  operator=$(whoami 2>/dev/null || echo unknown)

  printf '{"hook":"ta-contract-collision-warn","tier":"warn","ts":"%s","file_edited":"%s","consumer_count":%d,"operator":"%s"}\n' \
    "$ts" "$file_edited" "$consumer_count" "$operator" >> "$AUDIT"

  echo "WARN [Lintel hook ta-contract-collision-warn]: editing $file_edited"
  if [ "$consumer_count" -gt 0 ]; then
    echo "WARN: $consumer_count consumer(s) registered against this interface"
  fi
  echo "WARN: consider /li:ta single --action contract-collision to assess change impact, or pass --ignore-contract-collision to override."
fi

exit 0
