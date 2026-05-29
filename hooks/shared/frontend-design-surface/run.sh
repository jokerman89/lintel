#!/usr/bin/env bash
# frontend-design-surface — Lintel surface-only hook (v3.7 Fas C)
# Passive surfacing of relevant design-patterns when operator opens/edits frontend files.
# Per design doc: read-only recommendation, throttled, <200ms budget for vault of 1-3.

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
VAULT="$LINTEL_HOME/brand/design-patterns"
AUDIT="$LINTEL_HOME/audit/hooks.jsonl"
SESSION_DIR="$LINTEL_HOME/sessions"

mkdir -p "$LINTEL_HOME/audit" "$SESSION_DIR"

# Argument: target file path (from hook event)
target_file="${1:-}"
[ -z "$target_file" ] && exit 0

# Filter on frontend file-extensions
case "$target_file" in
  *.tsx|*.jsx|*.svelte|*.vue|*.css|*.scss|*.sass) ;;
  *) exit 0 ;;  # Not a frontend file, silent exit
esac

# Vault check — silent if empty (MVP)
[ -d "$VAULT" ] || exit 0
pattern_count=$(find "$VAULT" -maxdepth 2 -name 'pattern.json' 2>/dev/null | wc -l | tr -d ' ')
[ "$pattern_count" -eq 0 ] && exit 0

# Operator-disabled escape hatch
[ -f "$HOME/.gstack/.frontend-design-surface-disabled" ] && exit 0
[ -f "$LINTEL_HOME/.frontend-design-surface-disabled" ] && exit 0

# Throttle marker — per-session, per-file
# LINTEL_SESSION_ID overrides PPID (test-context, OR explicit operator-session-tag).
# In real Claude Code usage, PPID is stable across tool invocations from same session.
session_id="${LINTEL_SESSION_ID:-${PPID:-$$}}"
marker="$SESSION_DIR/${session_id}-design-surfaced"
# Normalize path for stable matching
target_canonical=$(cd "$(dirname "$target_file")" 2>/dev/null && pwd)/$(basename "$target_file")
[ -z "$target_canonical" ] && target_canonical="$target_file"

if [ -f "$marker" ] && grep -Fxq "$target_canonical" "$marker" 2>/dev/null; then
  exit 0  # Already surfaced this file this session
fi

# Collect relevant patterns (MVP: extension-bucket match; Fas C+1 will add brief-hash matching)
# tsx/jsx → patterns that reference react in component-imports.json
# svelte → patterns that reference svelte
# vue → patterns that reference vue
# css/scss → all patterns (CSS is universal)
ext="${target_file##*.}"
relevant_patterns=()

for dir in "$VAULT"/*/; do
  [ -d "$dir" ] || continue
  pattern_file="$dir/pattern.json"
  [ -f "$pattern_file" ] || continue
  ci_file="$dir/component-imports.json"

  case "$ext" in
    tsx|jsx)
      # Check if pattern's component-imports references react-stack (shadcn/aceternity/etc are React)
      if [ -f "$ci_file" ] && grep -qE "shadcn|aceternity|magic-ui" "$ci_file" 2>/dev/null; then
        relevant_patterns+=("$(basename "$dir")")
      fi
      ;;
    svelte)
      if [ -f "$ci_file" ] && grep -qi "svelte" "$ci_file" 2>/dev/null; then
        relevant_patterns+=("$(basename "$dir")")
      fi
      ;;
    vue)
      if [ -f "$ci_file" ] && grep -qi "vue" "$ci_file" 2>/dev/null; then
        relevant_patterns+=("$(basename "$dir")")
      fi
      ;;
    css|scss|sass)
      relevant_patterns+=("$(basename "$dir")")
      ;;
  esac
done

# Cap at 3 to keep surface line readable
if [ "${#relevant_patterns[@]}" -gt 3 ]; then
  relevant_patterns=("${relevant_patterns[@]:0:3}")
  suffix=" (+more)"
else
  suffix=""
fi

# No relevant patterns → silent exit
[ "${#relevant_patterns[@]}" -eq 0 ] && exit 0

# Surface line (read-only; non-blocking)
patterns_csv=$(IFS=', '; echo "${relevant_patterns[*]}")
echo "INFO [Lintel]: design-patterns relevant to ${target_file}: ${patterns_csv}${suffix}. Reuse: /li:frontend-design --pattern <name>"

# Mark surfaced
echo "$target_canonical" >> "$marker"

# Audit-log
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
patterns_json=$(printf '"%s",' "${relevant_patterns[@]}" | sed 's/,$//')
printf '{"hook":"frontend-design-surface","tier":"surface","ts":"%s","file":"%s","patterns":[%s],"vault_size":%d}\n' \
  "$ts" "$target_canonical" "$patterns_json" "$pattern_count" >> "$AUDIT"

exit 0
