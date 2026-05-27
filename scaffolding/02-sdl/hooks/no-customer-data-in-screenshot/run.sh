#!/usr/bin/env bash
# no-customer-data-in-screenshot — JStack warn-only hook
set -euo pipefail

ARTIFACT_DIR="${1:-}"
[ -z "$ARTIFACT_DIR" ] && exit 0
[ ! -d "$ARTIFACT_DIR" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

DOM="$ARTIFACT_DIR/dom.html"
[ ! -f "$DOM" ] && exit 0

patterns_hit=()

# Reuse customer-data patterns
grep -qE '\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b' "$DOM" 2>/dev/null && patterns_hit+=("email")
grep -qE '\+?[0-9]{1,3}[ -]?\(?[0-9]{2,4}\)?[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}' "$DOM" 2>/dev/null && patterns_hit+=("phone")
grep -qE '\b[0-9]{6}[-+][0-9]{4}\b' "$DOM" 2>/dev/null && patterns_hit+=("personnummer")

if [ ${#patterns_hit[@]} -gt 0 ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  printf '{"hook":"no-customer-data-in-screenshot","tier":"warn","ts":"%s","artifact_dir":"%s","patterns_matched":"%s"}\n' \
    "$ts" "$ARTIFACT_DIR" "$joined" >> "$AUDIT"
  echo "WARN [JStack hook]: screenshot DOM at $ARTIFACT_DIR contains customer-data tells ($joined)"
  echo "WARN: Quarantine the artifact before sharing. Consider mv to ~/.jstack/quarantine/"
fi

exit 0
