#!/usr/bin/env bash
# da-migration-irreversible-warn — Lintel warn-only hook
# Optional filename/regex heuristic over an existing file, not a reversibility proof.
# component: da-migration-irreversible-warn
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: opt-in warning; target policy is data, not implementation code
# last_intent_review: 2026-10-03

set -euo pipefail
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"  # guard: unset under set -u aborts the hook (fail-closed)

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
source "$(dirname "${BASH_SOURCE[0]}")/../_text.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only act on migration files
case "$file_edited" in
  db/migrations/*|supabase/migrations/*|migrations/*) ;;
  *.up.sql|*-up.sql)
    # Generic up-migration pattern
    ;;
  *)
    # Optional legacy filename hint, not a typed migration-policy field.
    _resolver="$(dirname "${BASH_SOURCE[0]}")/../../../lib/pack-resolver.sh"
    [ -f "$_resolver" ] || _resolver="$LINTEL_HOME/lib/pack-resolver.sh"
    if [ -f "$_resolver" ]; then
      LINTEL_SOURCE_ROOT="$(cd "$(dirname "$_resolver")/.." && pwd)"
      source "$_resolver" 2>/dev/null
      lookup_status=0
      mig_glob=$(resolve_pack_field data_architecture.migration_glob) || lookup_status=$?
      # Missing optional advice is benign; required-profile/load errors are not.
      [ "$lookup_status" -le 1 ] || exit "$lookup_status"
      if [ -n "$mig_glob" ]; then
        match=0
        IFS=',' read -ra patterns <<< "$mig_glob"
        for p in "${patterns[@]}"; do
          p=$(printf '%s' "$p" | tr -d '[:space:]')
          case "$file_edited" in
            $p) match=1; break ;;
          esac
        done
        [ "$match" -eq 0 ] && exit 0
      else
        exit 0
      fi
    else
      exit 0
    fi
    ;;
esac

# Match SQL-looking text, including comments; no SQL parsing or execution.
destructive_ops=""
sql_patterns=('\bDROP[[:space:]]+TABLE\b' '\bDROP[[:space:]]+COLUMN\b'
  '\bTRUNCATE\b' '\bALTER[[:space:]]+COLUMN.*TYPE\b')
sql_labels=('DROP TABLE' 'DROP COLUMN' 'TRUNCATE' 'ALTER TYPE')
for index in "${!sql_patterns[@]}"; do
  count=$(hook_text_count "${sql_patterns[$index]}" "$file_edited" -i) || exit 0
  [ "$count" -eq 0 ] || destructive_ops="${destructive_ops}${sql_labels[$index]},"
done

destructive_ops="${destructive_ops%,}"

# Filename/marker presence only; neither establishes working recovery.
has_down_hint=false
base="${file_edited%.up.sql}"
base="${base%-up.sql}"
for candidate in "${base}.down.sql" "${base}-down.sql" "${base%.sql}.down.sql"; do
  [ -f "$candidate" ] && has_down_hint=true && break
done

# In-file down marker only; its implementation is not checked.
if ! $has_down_hint; then
  count=$(hook_text_count '^-- ?down|^# ?down' "$file_edited" -i) || exit 0
  [ "$count" -eq 0 ] || has_down_hint=true
fi

if [ -n "$destructive_ops" ] && ! $has_down_hint; then
  # Retain the legacy audit key; "has_rollback" records this hint, not recovery proof.
  audit_log "hooks" "da_migration_irreversible_warn" "hook=da-migration-irreversible-warn" "tier=warn" "file=$file_edited" "destructive_ops=$destructive_ops" "has_rollback=false"

  echo "WARN [Lintel hook da-migration-irreversible-warn]: $file_edited"
  echo "WARN: filename/regex heuristic matched SQL-looking text ($destructive_ops) without a down-file/marker hint."
  echo "WARN: this is not proof of irreversibility; silence or a down hint is not proof of recovery."
  echo "WARN: review actual recovery and data-loss acceptance under /li:da single --action migration-plan."
fi

exit 0
