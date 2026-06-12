#!/usr/bin/env bash
# da-retention-violation-warn — Lintel warn-only hook
# Surfaces when data-access code reads a retention-bound table without honoring the retention filter.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only data-access kinds of files (heuristic by extension + path)
case "$file_edited" in
  *repository*|*repo.*|*dao.*|*store.*|*db.*) ;;
  *.sql|*.go|*.ts|*.tsx|*.js|*.jsx|*.py|*.rb|*.rs|*.java|*.kt) ;;
  *) exit 0 ;;
esac

# Find retention-bound tables (read from policy file)
policy_file=".claude/runtime/state/da/retention-policy.md"
[ -f "$policy_file" ] || policy_file=".lintel/state/da/retention-policy.md" # legacy-fallback-ok
[ -f "$policy_file" ] || exit 0

# Heuristic extraction: lines like "- table_name: 90 days" or "table_name | 90"
declare -a retention_tables
declare -a retention_windows
declare -a retention_filters
while IFS= read -r line; do
  tbl=$(printf '%s' "$line" | awk '{print $1}' | tr -d '-:|')
  days=$(printf '%s' "$line" | grep -oE '[0-9]+[[:space:]]*(days?|d\b)' | head -1 | grep -oE '[0-9]+')
  filter=$(printf '%s' "$line" | grep -oE '(deleted_at|archived_at|retained_until|expires_at)' | head -1)
  filter="${filter:-deleted_at}"
  if [ -n "$tbl" ] && [ -n "$days" ]; then
    retention_tables+=("$tbl")
    retention_windows+=("$days")
    retention_filters+=("$filter")
  fi
done < <(grep -E '^[[:space:]]*[-|][[:space:]]*[a-z_]+' "$policy_file" 2>/dev/null)

[ "${#retention_tables[@]}" -eq 0 ] && exit 0

# For each retention-bound table, check if edited file references it and is missing the filter
violations=""
for i in "${!retention_tables[@]}"; do
  tbl="${retention_tables[$i]}"
  filter="${retention_filters[$i]}"

  # Does the file reference the table?
  if grep -qE "\\b${tbl}\\b" "$file_edited" 2>/dev/null; then
    # Does it use the retention filter?
    if ! grep -qE "\\b${filter}\\b" "$file_edited" 2>/dev/null; then
      violations="${violations}${tbl}/${filter},"
    fi
  fi
done

violations="${violations%,}"

if [ -n "$violations" ]; then
  audit_log "hooks" "da_retention_violation_warn" "hook=da-retention-violation-warn" "tier=warn" "file_edited=$file_edited" "violations=$violations"

  echo "WARN [Lintel hook da-retention-violation-warn]: $file_edited"
  echo "WARN: data access without retention filter — $violations"
  echo "WARN: add filter clause OR pass --ignore-retention if access is admin-only and audited."
fi

exit 0
