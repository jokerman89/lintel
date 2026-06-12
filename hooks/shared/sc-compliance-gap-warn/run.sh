#!/usr/bin/env bash
# sc-compliance-gap-warn — Lintel warn-only hook
# Surfaces edits to regulated-data paths without current compliance evidence.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE="$LINTEL_HOME/profile.yaml"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] && exit 0

# Detect regulated-path matches
matches_regulated=0
case "$file_edited" in
  *payment*|*billing*|*card*|*invoice*) matches_regulated=1 ;;
  *patient*|*medical*|*health*|*hipaa*) matches_regulated=1 ;;
  *gdpr*|*consent*|*pii*|*personal*) matches_regulated=1 ;;
  *audit*|*compliance*) matches_regulated=1 ;;
esac

if [ "$matches_regulated" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  reg_glob=$(resolve_pack_field security_compliance.regulated_path_glob 2>/dev/null || true)
  if [ -n "$reg_glob" ]; then
    IFS=',' read -ra patterns <<< "$reg_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_regulated=1; break ;; esac
    done
  fi
fi

[ "$matches_regulated" -eq 0 ] && exit 0

# Read required frameworks
frameworks_csv=""
if [ -f "$PROFILE" ]; then
  frameworks_csv=$(awk '/^engineering:/{in_eng=1; next} /^[a-z]/{in_eng=0}
                       in_eng && /security_compliance:/{in_sc=1; next} in_eng && /^[[:space:]]+[a-z]/ && !/security_compliance/{in_sc=0}
                       in_sc && /compliance_frameworks:/{print $NF; exit}' "$PROFILE" 2>/dev/null | tr -d '[]"' | tr -d "'")
fi
frameworks_csv="${frameworks_csv:-soc2,gdpr}"

# For each framework: check evidence
total_gap=0
oldest_age=-1
sc_state_dir=".claude/runtime/state/sc"
[ -d "$sc_state_dir" ] || sc_state_dir=".lintel/state/sc" # legacy-fallback-ok
IFS=',' read -ra frameworks <<< "$frameworks_csv"
for fw in "${frameworks[@]}"; do
  fw=$(printf '%s' "$fw" | tr -d '[:space:]')
  evidence_file="$sc_state_dir/compliance-evidence-${fw}.md"
  if [ ! -f "$evidence_file" ]; then
    total_gap=$((total_gap + 1))
    continue
  fi
  if stat -c "%Y" "$evidence_file" >/dev/null 2>&1; then
    mtime=$(stat -c "%Y" "$evidence_file")
  else
    mtime=$(stat -f "%m" "$evidence_file" 2>/dev/null || echo 0)
  fi
  now=$(date +%s)
  age=$(( (now - mtime) / 86400 ))
  if [ "$age" -gt 90 ]; then
    total_gap=$((total_gap + 1))
  fi
  [ "$age" -gt "$oldest_age" ] && oldest_age="$age"

  # Count known gaps in the evidence file (lines mentioning "gap")
  gap_lines=$(grep -ciE 'verdict:[[:space:]]*gap' "$evidence_file" 2>/dev/null || echo 0)
  total_gap=$((total_gap + gap_lines))
done

if [ "$total_gap" -gt 0 ]; then
  audit_log "hooks" "sc_compliance_gap_warn" "hook=sc-compliance-gap-warn" "tier=warn" "file_edited=$file_edited" "required_frameworks=$frameworks_csv" "evidence_age_days=$oldest_age" "gap_count=$total_gap"

  echo "WARN [Lintel hook sc-compliance-gap-warn]: editing $file_edited"
  echo "WARN: regulated path with $total_gap compliance gap(s) across $frameworks_csv (oldest evidence: $oldest_age days)"
  echo "WARN: consider /li:sc single --action compliance-evidence, or pass --ignore-compliance-gap to acknowledge."
fi

exit 0
