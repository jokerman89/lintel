#!/usr/bin/env bash
# da-schema-drift-warn — Lintel warn-only hook
# Surfaces when an Edit/Write hits a schema file claimed by a schema-flavored ADR.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] && exit 0

# Schema-flavored ADRs only — heuristic match on filename or content
adr_dirs=(".lintel/decisions" "docs/decisions" "docs/adr")
matching_adr=""
matching_decision=""

for dir in "${adr_dirs[@]}"; do
  [ -d "$dir" ] || continue
  while IFS= read -r adr; do
    # Is this a schema-flavored ADR? (filename or content contains schema/migration/data-model)
    if ! grep -qiE 'schema|migration|data.model|table|column' "$adr" 2>/dev/null; then
      continue
    fi
    # Does its decisions: block list this file?
    if awk '
      /^---$/ { if (++fm == 2) exit; next }
      fm == 1 && /^decisions:/ { in_dec=1; next }
      fm == 1 && in_dec && /^[a-z_]/ { in_dec=0 }
      fm == 1 && in_dec && $0 ~ "'"$file_edited"'" { found=1 }
      END { exit (found ? 0 : 1) }
    ' "$adr" 2>/dev/null; then
      matching_adr=$(basename "$adr" .md)
      matching_decision=$(grep -m1 -E '^(#|decision:)' "$adr" 2>/dev/null | head -1 | sed 's/^# //; s/^decision: //')
      break 2
    fi
  done < <(find "$dir" -name "*.md" -type f 2>/dev/null)
done

if [ -n "$matching_adr" ]; then
  audit_log "hooks" "da_schema_drift_warn" "hook=da-schema-drift-warn" "tier=warn" "file_edited=$file_edited" "adr_id=$matching_adr" "adr_decision=$matching_decision"

  echo "WARN [Lintel hook da-schema-drift-warn]: editing $file_edited"
  echo "WARN: schema file is claimed by $matching_adr — '$matching_decision'"
  echo "WARN: consider updating the ADR, running /li:da data-contract-collision, or pass --ignore-schema-drift to override."
fi

exit 0
