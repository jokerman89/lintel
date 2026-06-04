#!/usr/bin/env bash
# ta-arch-drift-warn — Lintel warn-only hook
# Surfaces when an Edit/Write hits a file path claimed by an ADR's "decisions:" block.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] && exit 0

# Scan possible ADR locations
adr_dirs=(".lintel/decisions" "docs/decisions" "docs/adr")
matching_adr=""
matching_decision=""

for dir in "${adr_dirs[@]}"; do
  [ -d "$dir" ] || continue
  while IFS= read -r adr; do
    # Look for `decisions:` frontmatter listing the edited file
    if awk '
      /^---$/ { if (++fm == 2) exit; next }
      fm == 1 && /^decisions:/ { in_dec=1; next }
      fm == 1 && in_dec && /^[a-z_]/ { in_dec=0 }
      fm == 1 && in_dec && $0 ~ "'"$file_edited"'" { found=1 }
      END { exit (found ? 0 : 1) }
    ' "$adr" 2>/dev/null; then
      matching_adr=$(basename "$adr" .md)
      # Pull first non-frontmatter h1 or `decision:` line for summary
      matching_decision=$(grep -m1 -E '^(#|decision:)' "$adr" 2>/dev/null | head -1 | sed 's/^# //; s/^decision: //')
      break 2
    fi
  done < <(find "$dir" -name "*.md" -type f 2>/dev/null)
done

if [ -n "$matching_adr" ]; then
  audit_log "hooks" "ta_arch_drift_warn" "hook=ta-arch-drift-warn" "tier=warn" "file_edited=$file_edited" "adr_id=$matching_adr" "adr_decision=$matching_decision"

  echo "WARN [Lintel hook ta-arch-drift-warn]: editing $file_edited"
  echo "WARN: file is claimed by $matching_adr — '$matching_decision'"
  echo "WARN: consider updating the ADR if revising the decision, or pass --ignore-arch-drift to override."
fi

exit 0
