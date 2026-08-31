#!/usr/bin/env bash
# sc-auth-bypass-warn — Lintel warn-only hook
# Surfaces auth-flow edits introducing high-risk bypass patterns.

set -euo pipefail
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"  # guard: unset under set -u aborts the hook (fail-closed)

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
file_edited="$(hook_input file_path "${1:-}")"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Only act on auth-flow files (heuristic + pack policy)
matches_auth=0
case "$file_edited" in
  *auth*|*oauth*|*saml*|*jwt*|*session*|*login*|*middleware*) matches_auth=1 ;;
esac

if [ "$matches_auth" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  auth_glob=$(resolve_pack_field security_compliance.auth_flow_glob 2>/dev/null || true)
  if [ -n "$auth_glob" ]; then
    IFS=',' read -ra patterns <<< "$auth_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_auth=1; break ;; esac
    done
  fi
fi

[ "$matches_auth" -eq 0 ] && exit 0

# Scan for high-risk patterns
declare -a found_patterns

# Skip-auth flags
if grep -inE '(skipAuth|skip_auth|disableAuth|disable_auth|bypassAuth|bypass_auth)[[:space:]]*[:=][[:space:]]*(true|"true"|1)' "$file_edited" 2>/dev/null | head -3 | while read -r line; do
  found_patterns+=("skip-auth-flag:${line%%:*}")
done; then :; fi

# Magic credentials (hardcoded user/pass)
if grep -inE '(username|user|email)[[:space:]]*[:=][[:space:]]*"(admin|root|test)"' "$file_edited" 2>/dev/null | head -3 | while read -r line; do
  found_patterns+=("magic-credential:${line%%:*}")
done; then :; fi

# Bypass routes
if grep -inE '(/skip[_-]auth|/test[_-]login|/dev[_-]login|/impersonate)' "$file_edited" 2>/dev/null | head -3 | while read -r line; do
  found_patterns+=("bypass-route:${line%%:*}")
done; then :; fi

# Direct role assignment
if grep -inE '(role|isAdmin|is_admin|admin)[[:space:]]*=[[:space:]]*(true|"admin")' "$file_edited" 2>/dev/null | head -3 | while read -r line; do
  found_patterns+=("direct-role-assignment:${line%%:*}")
done; then :; fi

# Simpler re-check (the while-pipe loop above can't actually populate the array — use direct grep counts)
skip_auth_count=$(grep -cE '(skipAuth|skip_auth|disableAuth|bypassAuth)[[:space:]]*[:=][[:space:]]*(true|"true"|1)' "$file_edited" 2>/dev/null) || skip_auth_count=0
magic_cred_count=$(grep -cE '(username|user|email)[[:space:]]*[:=][[:space:]]*"(admin|root|test)"' "$file_edited" 2>/dev/null) || magic_cred_count=0
bypass_route_count=$(grep -cE '(/skip[_-]auth|/test[_-]login|/dev[_-]login|/impersonate)' "$file_edited" 2>/dev/null) || bypass_route_count=0
direct_role_count=$(grep -cE '(role|isAdmin|is_admin)[[:space:]]*=[[:space:]]*(true|"admin")' "$file_edited" 2>/dev/null) || direct_role_count=0

total_findings=$((skip_auth_count + magic_cred_count + bypass_route_count + direct_role_count))

if [ "$total_findings" -gt 0 ]; then
  patterns="skip_auth:${skip_auth_count},magic_cred:${magic_cred_count},bypass_route:${bypass_route_count},direct_role:${direct_role_count}"
  audit_log "hooks" "sc_auth_bypass_warn" "hook=sc-auth-bypass-warn" "tier=warn" "file_edited=$file_edited" "patterns=$patterns" "total=$total_findings"

  echo "WARN [Lintel hook sc-auth-bypass-warn]: $file_edited"
  echo "WARN: high-risk auth pattern(s) detected — $patterns"
  echo "WARN: review under /li:sc single --action auth-flow, or pass --ignore-auth-bypass to acknowledge."
fi

exit 0
