#!/usr/bin/env bash
# dh-cost-budget-warn — Lintel warn-only hook
# Surfaces IaC commits that bump projected cost.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only act on IaC files
matches_iac=0
case "$file_edited" in
  *.tf|*.tfvars|*.bicep) matches_iac=1 ;;
  infra/*|terraform/*|bicep/*) matches_iac=1 ;;
  helm/*|k8s/*|kubernetes/*) [[ "$file_edited" =~ (deployment|hpa|statefulset|values) ]] && matches_iac=1 ;;
esac

if [ "$matches_iac" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  iac_glob=$(resolve_pack_field devops_hosting.iac_glob 2>/dev/null || true)
  if [ -n "$iac_glob" ]; then
    IFS=',' read -ra patterns <<< "$iac_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_iac=1; break ;; esac
    done
  fi
fi

[ "$matches_iac" -eq 0 ] && exit 0

# Scan for cost-increasing patterns
patterns_found=""

# SKU upsizing — Azure pattern (Standard_D2 → Standard_D8 etc.)
if grep -qiE 'Standard_[A-Z]+([1-9][0-9]+|[2-9])s?_v' "$file_edited" 2>/dev/null; then
  patterns_found="${patterns_found}sku-large,"
fi

# Replica increases (rough heuristic — looks for replicas above 5)
if grep -qE '^[[:space:]]*replicas:[[:space:]]*([5-9][0-9]*|[1-9][0-9]+)' "$file_edited" 2>/dev/null; then
  patterns_found="${patterns_found}replicas-high,"
fi

# Premium storage / premium SKUs
if grep -qiE '(premium|Premium_LRS|Premium_ZRS|p99-storage)' "$file_edited" 2>/dev/null; then
  patterns_found="${patterns_found}premium-sku,"
fi

# Always-on additions (new PVC, new always-on instance)
if grep -qiE '(PersistentVolumeClaim|always.on|reserved.instance|min_replicas:.*[5-9])' "$file_edited" 2>/dev/null; then
  patterns_found="${patterns_found}always-on,"
fi

patterns_found="${patterns_found%,}"

if [ -n "$patterns_found" ]; then
  audit_log "hooks" "dh_cost_budget_warn" "hook=dh-cost-budget-warn" "tier=warn" "file_edited=$file_edited" "patterns=$patterns_found"

  echo "WARN [Lintel hook dh-cost-budget-warn]: $file_edited"
  echo "WARN: cost-increasing pattern(s) detected — $patterns_found"
  echo "WARN: consider /li:dh single --action cost-projection to refresh projection, or pass --ignore-cost-warn to acknowledge."
fi

exit 0
