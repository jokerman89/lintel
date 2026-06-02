#!/usr/bin/env bash
# dh-deploy-without-rollback-warn — Lintel warn-only hook
# Surfaces deploy/IaC commits without documented rollback.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] && exit 0

# Detect deploy/IaC files (heuristic + pack policy)
matches_deploy=0
case "$file_edited" in
  infra/*|terraform/*|*.tf|*.tfvars) matches_deploy=1 ;;
  helm/*|k8s/*|kubernetes/*|*.yaml|*.yml) [[ "$file_edited" =~ (deployment|service|ingress|helmchart) ]] && matches_deploy=1 ;;
  .github/workflows/*deploy*|*.gitlab-ci.yml) matches_deploy=1 ;;
  Dockerfile*|docker-compose*) matches_deploy=1 ;;
esac

if [ "$matches_deploy" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  deploy_glob=$(resolve_pack_field devops_hosting.deploy_path_glob 2>/dev/null || true)
  if [ -n "$deploy_glob" ]; then
    IFS=',' read -ra patterns <<< "$deploy_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_deploy=1; break ;; esac
    done
  fi
fi

[ "$matches_deploy" -eq 0 ] && exit 0

# Check for rollback declaration: recent rollback-strategy file or rollback field in file itself
rollback_strategy=$(find .lintel/state/dh -name "rollback-strategy-*.md" -type f -mtime -7 2>/dev/null | sort | tail -1)
rollback_age_days=-1
has_rollback=false

if [ -n "$rollback_strategy" ] && [ -f "$rollback_strategy" ]; then
  if stat -c "%Y" "$rollback_strategy" >/dev/null 2>&1; then
    mtime=$(stat -c "%Y" "$rollback_strategy")
  else
    mtime=$(stat -f "%m" "$rollback_strategy" 2>/dev/null || echo 0)
  fi
  rollback_age_days=$(( ($(date +%s) - mtime) / 86400 ))
  has_rollback=true
fi

# In-file rollback markers
if ! $has_rollback && grep -qiE 'rollback|revert|down.migration|undo' "$file_edited" 2>/dev/null; then
  has_rollback=true
fi

if ! $has_rollback; then
  audit_log "hooks" "dh_deploy_without_rollback_warn" "hook=dh-deploy-without-rollback-warn" "tier=warn" "file_edited=$file_edited" "rollback_age_days=$rollback_age_days"

  echo "WARN [Lintel hook dh-deploy-without-rollback-warn]: $file_edited"
  echo "WARN: deploy/IaC change without rollback declaration (no rollback-strategy-*.md in .lintel/state/dh/, no in-file rollback markers)"
  echo "WARN: consider /li:dh single --action rollback-strategy, or pass --ignore-rollback to acknowledge."
fi

exit 0
