#!/usr/bin/env bash
# sc-auth-bypass-warn — Lintel warn-only hook
# Optional filename/regex heuristic over an existing file, not authorization proof.
# component: sc-auth-bypass-warn
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: opt-in warning; target policy is data, not implementation code
# last_intent_review: 2026-10-03

set -euo pipefail
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"  # guard: unset under set -u aborts the hook (fail-closed)

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
source "$(dirname "${BASH_SOURCE[0]}")/../_text.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only act on filename hints (built-in names plus optional legacy preference data).
matches_auth=0
case "$file_edited" in
  *auth*|*oauth*|*saml*|*jwt*|*session*|*login*|*middleware*) matches_auth=1 ;;
esac

_resolver="$(dirname "${BASH_SOURCE[0]}")/../../../lib/pack-resolver.sh"
[ -f "$_resolver" ] || _resolver="$LINTEL_HOME/lib/pack-resolver.sh"
if [ "$matches_auth" -eq 0 ] && [ -f "$_resolver" ]; then
  LINTEL_SOURCE_ROOT="$(cd "$(dirname "$_resolver")/.." && pwd)"
  source "$_resolver" 2>/dev/null
  lookup_status=0
  auth_glob=$(resolve_pack_field security_compliance.auth_flow_glob) || lookup_status=$?
  # Missing optional advice is benign; required-profile/load errors are not.
  [ "$lookup_status" -le 1 ] || exit "$lookup_status"
  if [ -n "$auth_glob" ]; then
    IFS=',' read -ra patterns <<< "$auth_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_auth=1; break ;; esac
    done
  fi
fi

[ "$matches_auth" -eq 0 ] && exit 0

# Count matching lines with the existing effective regexes (case-sensitive).
# Comments and strings can match; these are not reachable-flow or authorization checks.
skip_auth_count=$(hook_text_count '(skipAuth|skip_auth|disableAuth|bypassAuth)[[:space:]]*[:=][[:space:]]*(true|"true"|1)' "$file_edited") || exit 0
magic_cred_count=$(hook_text_count '(username|user|email)[[:space:]]*[:=][[:space:]]*"(admin|root|test)"' "$file_edited") || exit 0
bypass_route_count=$(hook_text_count '(/skip[_-]auth|/test[_-]login|/dev[_-]login|/impersonate)' "$file_edited") || exit 0
direct_role_count=$(hook_text_count '(role|isAdmin|is_admin)[[:space:]]*=[[:space:]]*(true|"admin")' "$file_edited") || exit 0

total_findings=$((skip_auth_count + magic_cred_count + bypass_route_count + direct_role_count))

if [ "$total_findings" -gt 0 ]; then
  patterns="skip_auth:${skip_auth_count},magic_cred:${magic_cred_count},bypass_route:${bypass_route_count},direct_role:${direct_role_count}"
  audit_log "hooks" "sc_auth_bypass_warn" "hook=sc-auth-bypass-warn" "tier=warn" "file_edited=$file_edited" "patterns=$patterns" "total=$total_findings"

  echo "WARN [Lintel hook sc-auth-bypass-warn]: $file_edited"
  echo "WARN: filename/regex heuristic matched text — $patterns"
  echo "WARN: this is not proof of an auth bypass; silence is not proof of correct authorization."
  echo "WARN: review the actual flow and trust boundaries under /li:sc single --action auth-flow."
fi

exit 0
