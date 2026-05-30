#!/usr/bin/env bash
# da-migration-irreversible-warn — Lintel warn-only hook
# Surfaces when a migration commit lacks a rollback path or includes destructive ops without documented data loss.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only act on migration files
case "$file_edited" in
  db/migrations/*|supabase/migrations/*|migrations/*) ;;
  *.up.sql|*-up.sql)
    # Generic up-migration pattern
    ;;
  *)
    # Check pack policy for migration_glob
    if [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
      source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
      mig_glob=$(resolve_pack_field data_architecture.migration_glob 2>/dev/null || true)
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

# Detect destructive operations
destructive_ops=""
if grep -qiE '\bDROP[[:space:]]+TABLE\b' "$file_edited" 2>/dev/null; then destructive_ops="${destructive_ops}DROP TABLE,"; fi
if grep -qiE '\bDROP[[:space:]]+COLUMN\b' "$file_edited" 2>/dev/null; then destructive_ops="${destructive_ops}DROP COLUMN,"; fi
if grep -qiE '\bTRUNCATE\b' "$file_edited" 2>/dev/null; then destructive_ops="${destructive_ops}TRUNCATE,"; fi
if grep -qiE '\bALTER[[:space:]]+COLUMN.*TYPE\b' "$file_edited" 2>/dev/null; then destructive_ops="${destructive_ops}ALTER TYPE,"; fi

destructive_ops="${destructive_ops%,}"

# Check for paired down-migration
has_rollback=false
base="${file_edited%.up.sql}"
base="${base%-up.sql}"
for candidate in "${base}.down.sql" "${base}-down.sql" "${base%.sql}.down.sql"; do
  [ -f "$candidate" ] && has_rollback=true && break
done

# In-file rollback section (single-file migrations with `-- down` markers)
if ! $has_rollback && grep -qiE '^-- ?down|^# ?down' "$file_edited" 2>/dev/null; then
  has_rollback=true
fi

if [ -n "$destructive_ops" ] && ! $has_rollback; then
  audit_log "hooks" "da_migration_irreversible_warn" "hook=da-migration-irreversible-warn" "tier=warn" "file=$file_edited" "destructive_ops=$destructive_ops" "has_rollback=false"

  echo "WARN [Lintel hook da-migration-irreversible-warn]: $file_edited"
  echo "WARN: destructive operations detected ($destructive_ops) without paired rollback"
  echo "WARN: consider /li:da single --action migration-plan for safer expand-and-contract, or pass --ignore-irreversibility to acknowledge."
fi

exit 0
