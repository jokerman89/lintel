#!/usr/bin/env bash
# secret-scan-block — Lintel JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 secret pattern in staged content.

set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Only fire on git commit / git push
if ! echo "$CMD" | grep -qE '^git\s+(commit|push)\b'; then
  exit 0
fi

# Override path
if [ "${LINTEL_OVERRIDE_SECRET:-}" = "1" ]; then
  reason="${LINTEL_OVERRIDE_REASON:-no-reason-given}"
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=OVERRIDDEN" "override=true" "reason=$reason" "blocked=false"
  echo "INFO [Lintel hook]: secret-scan-block OVERRIDDEN by operator (reason: $reason). Audit-logged."
  exit 0
fi

# Get staged content
STAGED="$(git diff --cached 2>/dev/null || true)"
[ -z "$STAGED" ] && exit 0

patterns_hit=()
echo "$STAGED" | grep -qE 'gh[opur]_[A-Za-z0-9]{36}' && patterns_hit+=("github-token")
echo "$STAGED" | grep -qE 'sk-[A-Za-z0-9]{32,}' && patterns_hit+=("openai-key")
echo "$STAGED" | grep -qE 'xox[abposr]-[A-Za-z0-9-]{10,}' && patterns_hit+=("slack-token")
echo "$STAGED" | grep -qE 'AKIA[0-9A-Z]{16}' && patterns_hit+=("aws-access-key")
echo "$STAGED" | grep -qE 'AccountKey=[A-Za-z0-9+/=]{40,}' && patterns_hit+=("azure-account-key")
echo "$STAGED" | grep -qE 'sk-ant-[A-Za-z0-9-]{30,}' && patterns_hit+=("anthropic-key")
echo "$STAGED" | grep -qE '\-+BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY\-+' && patterns_hit+=("private-key")

if [ ${#patterns_hit[@]} -gt 0 ]; then
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "patterns_matched=$joined" "blocked=true"
  echo "ERROR [Lintel hook]: secret pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Remove the secret + re-stage." >&2
  echo "ERROR: To override (e.g. known-false-positive in test fixtures):" >&2
  echo '  LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 1
fi

exit 0
