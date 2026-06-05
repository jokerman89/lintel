#!/usr/bin/env bash
# tq-contract-break-warn — Lintel warn-only hook
# Surfaces provider edits without paired contract-test update.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] && exit 0

# Detect provider files
matches_provider=0
case "$file_edited" in
  src/api/*|src/handlers/*|src/routes/*|src/endpoints/*|pkg/*/api/*) matches_provider=1 ;;
  *.proto|*.openapi.yaml|*.openapi.yml) matches_provider=1 ;;
esac

if [ "$matches_provider" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  provider_glob=$(resolve_pack_field testing_qa.provider_glob 2>/dev/null || true)
  if [ -n "$provider_glob" ]; then
    IFS=',' read -ra patterns <<< "$provider_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_provider=1; break ;; esac
    done
  fi
fi

[ "$matches_provider" -eq 0 ] && exit 0

# Check if same commit also touches contract-test files
contract_test_updated=false
if command -v git >/dev/null 2>&1; then
  staged_files=$(git diff --cached --name-only 2>/dev/null || true)
  if echo "$staged_files" | grep -qiE '(contract|pact|consumer-test).*\.(go|ts|js|py|rb|java|kt|rs)$' 2>/dev/null; then
    contract_test_updated=true
  fi
fi

if ! $contract_test_updated; then
  audit_log "hooks" "tq_contract_break_warn" "hook=tq-contract-break-warn" "tier=warn" "file_edited=$file_edited" "contract_test_updated=false"

  echo "WARN [Lintel hook tq-contract-break-warn]: $file_edited"
  echo "WARN: provider file changed without paired contract-test update in this commit"
  echo "WARN: consider /li:tq single --action contract-test-design, or pass --ignore-contract-break if change is contract-preserving."
fi

exit 0
