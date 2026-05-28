#!/usr/bin/env bash
# no-en-vocab-in-trailblazer — Lintel warn-only hook
set -euo pipefail

PAYLOAD="${1:-}"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"
AUDIT="$LINTEL_HOME/audit/hooks.jsonl"

# Trailblazer-tagged?
if ! echo "$PAYLOAD" | grep -qE '^voice:\s*trailblazer'; then
  exit 0
fi

# Tier 1 vocab
TIER1=(
  "delve" "crucial" "robust" "comprehensive" "multifaceted" "nuanced" "intricate"
  "paradigm" "harness" "navigate the landscape" "at the forefront" "cutting-edge"
  "game-changing" "revolutionize" "transformative" "synergy" "holistic"
  "best-in-class" "world-class" "state-of-the-art"
)

hits=()
for w in "${TIER1[@]}"; do
  # Case-insensitive word-boundary search
  if echo "$PAYLOAD" | grep -qiE "\b${w}\b"; then
    hits+=("$w")
  fi
done

if [ ${#hits[@]} -gt 0 ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  joined=$(IFS=,; echo "${hits[*]}")
  printf '{"hook":"no-en-vocab-in-trailblazer","tier":"warn","ts":"%s","tier1_hits":"%s"}\n' \
    "$ts" "$joined" >> "$AUDIT"
  echo "WARN [Lintel hook]: Tier 1 AI-tell vocab in trailblazer payload: $joined"
  echo "WARN: Regenerate via /msvoice-rewrite or rewrite manually. /customer-voice-check WILL fail with these."
fi

exit 0
