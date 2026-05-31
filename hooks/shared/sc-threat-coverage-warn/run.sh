#!/usr/bin/env bash
# sc-threat-coverage-warn — Lintel warn-only hook
# Surfaces when an Edit/Write touches a security-surface file with no recent threat-model coverage.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] && exit 0

# Default surface heuristic: auth + api + data files
matches_surface=0
case "$file_edited" in
  *auth*|*oauth*|*saml*|*jwt*|*session*|*login*) matches_surface=1 ;;
  src/api/*|src/handlers/*|src/routes/*|*controller*|*handler*) matches_surface=1 ;;
  *secret*|*credential*|*token*|*password*) matches_surface=1 ;;
esac

# Pack-policy override (glob list)
if [ "$matches_surface" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  surface_glob=$(resolve_pack_field security_compliance.threat_surface_glob 2>/dev/null || true)
  if [ -n "$surface_glob" ]; then
    IFS=',' read -ra patterns <<< "$surface_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_surface=1; break ;; esac
    done
  fi
fi

[ "$matches_surface" -eq 0 ] && exit 0

# Find latest threat model
latest_model=$(find .lintel/state/sc -name "threat-model-*.md" -type f 2>/dev/null | sort | tail -1)

threat_model_age_days=-1
file_in_model=false

if [ -n "$latest_model" ] && [ -f "$latest_model" ]; then
  # Age in days
  if stat -c "%Y" "$latest_model" >/dev/null 2>&1; then
    mtime=$(stat -c "%Y" "$latest_model")
  else
    mtime=$(stat -f "%m" "$latest_model" 2>/dev/null || echo 0)
  fi
  now=$(date +%s)
  threat_model_age_days=$(( (now - mtime) / 86400 ))

  # Is the edited file referenced in the model?
  if grep -qF "$file_edited" "$latest_model" 2>/dev/null; then
    file_in_model=true
  fi
fi

# Warn if no model OR model too old OR file not covered
should_warn=false
if [ -z "$latest_model" ]; then
  should_warn=true
elif [ "$threat_model_age_days" -gt 90 ]; then
  should_warn=true
elif [ "$file_in_model" = "false" ]; then
  should_warn=true
fi

if $should_warn; then
  audit_log "hooks" "sc_threat_coverage_warn" "hook=sc-threat-coverage-warn" "tier=warn" "file_edited=$file_edited" "threat_model_age_days=$threat_model_age_days" "file_in_model=$file_in_model"

  echo "WARN [Lintel hook sc-threat-coverage-warn]: editing $file_edited"
  if [ -z "$latest_model" ]; then
    echo "WARN: no threat model found in .lintel/state/sc/"
  elif [ "$threat_model_age_days" -gt 90 ]; then
    echo "WARN: latest threat model is $threat_model_age_days days old (>90 day threshold)"
  else
    echo "WARN: file not referenced in latest threat model — coverage gap"
  fi
  echo "WARN: consider /li:sc single --action threat-model, or pass --ignore-threat-coverage to override."
fi

exit 0
