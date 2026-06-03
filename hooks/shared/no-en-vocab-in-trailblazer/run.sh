#!/usr/bin/env bash
# no-en-vocab-in-trailblazer — Lintel warn-only hook
set -euo pipefail

PAYLOAD="${1:-}"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

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
  joined=$(IFS=,; echo "${hits[*]}")
  audit_log "hooks" "no_en_vocab_in_trailblazer" "hook=no-en-vocab-in-trailblazer" "tier=warn" "tier1_hits=$joined"
  echo "WARN [Lintel hook]: Tier 1 AI-tell vocab in trailblazer payload: $joined"
  echo "WARN: Regenerate via /msvoice-rewrite or rewrite manually. /customer-voice-check WILL fail with these."
fi

exit 0
