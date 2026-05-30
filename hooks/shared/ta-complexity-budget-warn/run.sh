#!/usr/bin/env bash
# ta-complexity-budget-warn — Lintel warn-only hook
# Surfaces when an edit pushes a file over the operator's complexity budget.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
AUDIT="$LINTEL_HOME/audit/hooks.jsonl"
PROFILE="$LINTEL_HOME/profile.yaml"
mkdir -p "$LINTEL_HOME/audit"

file_edited="${1:-}"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Read thresholds from profile (with defaults)
budget_cyclomatic=12
budget_cognitive=18

if [ -f "$PROFILE" ]; then
  v=$(awk '/^engineering:/{in_eng=1; next} /^[a-z]/{in_eng=0}
           in_eng && /tech_architecture:/{in_ta=1; next} in_eng && /^[[:space:]]+[a-z]/ && !/tech_architecture/{in_ta=0}
           in_ta && /complexity_budget_cyclomatic:/{print $NF; exit}' "$PROFILE" 2>/dev/null || true)
  [ -n "$v" ] && budget_cyclomatic="$v"

  v=$(awk '/^engineering:/{in_eng=1; next} /^[a-z]/{in_eng=0}
           in_eng && /tech_architecture:/{in_ta=1; next} in_eng && /^[[:space:]]+[a-z]/ && !/tech_architecture/{in_ta=0}
           in_ta && /complexity_budget_cognitive:/{print $NF; exit}' "$PROFILE" 2>/dev/null || true)
  [ -n "$v" ] && budget_cognitive="$v"
fi

# Detect language by extension
ext="${file_edited##*.}"
cyclomatic=0
cognitive=0

case "$ext" in
  go)
    if command -v gocyclo >/dev/null 2>&1; then
      cyclomatic=$(gocyclo "$file_edited" 2>/dev/null | awk 'NR==1{print $1}' || echo 0)
    fi
    ;;
  py)
    if command -v radon >/dev/null 2>&1; then
      cyclomatic=$(radon cc "$file_edited" 2>/dev/null | awk 'NR==2{print $NF}' | tr -d '()' || echo 0)
    fi
    ;;
  *)
    if command -v lizard >/dev/null 2>&1; then
      cyclomatic=$(lizard "$file_edited" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
    fi
    ;;
esac

# Fall back to silent exit if no tool available (don't penalize operator for missing tooling)
[ "$cyclomatic" = 0 ] && exit 0

# Cognitive complexity often unavailable from simple tools; approximate as cyclomatic * 1.3 if not measured separately
[ "$cognitive" = 0 ] && cognitive=$(( cyclomatic * 13 / 10 ))

if [ "$cyclomatic" -gt "$budget_cyclomatic" ] || [ "$cognitive" -gt "$budget_cognitive" ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  operator=$(whoami 2>/dev/null || echo unknown)

  printf '{"hook":"ta-complexity-budget-warn","tier":"warn","ts":"%s","file_edited":"%s","cyclomatic":%d,"cognitive":%d,"budget_cyclomatic":%d,"budget_cognitive":%d,"operator":"%s"}\n' \
    "$ts" "$file_edited" "$cyclomatic" "$cognitive" "$budget_cyclomatic" "$budget_cognitive" "$operator" >> "$AUDIT"

  echo "WARN [Lintel hook ta-complexity-budget-warn]: $file_edited"
  echo "WARN: cyclomatic=$cyclomatic (budget $budget_cyclomatic), cognitive=$cognitive (budget $budget_cognitive)"
  echo "WARN: consider /li:ta single --action complexity-audit for refactor recommendations, or pass --ignore-complexity to override."
fi

exit 0
