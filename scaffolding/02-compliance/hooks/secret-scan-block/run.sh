#!/usr/bin/env bash
# secret-scan-block — JStack JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 secret pattern in staged content.

set -euo pipefail

CMD="${1:-}"
[ -z "$CMD" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

# Only fire on git commit / git push
if ! echo "$CMD" | grep -qE '^git\s+(commit|push)\b'; then
  exit 0
fi

# Override path
if [ "${JSTACK_OVERRIDE_SECRET:-}" = "1" ]; then
  reason="${JSTACK_OVERRIDE_REASON:-no-reason-given}"
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '{"hook":"secret-scan-block","tier":"OVERRIDDEN","ts":"%s","reason":"%s","blocked":false}\n' \
    "$ts" "$reason" >> "$AUDIT"
  echo "INFO [JStack hook]: secret-scan-block OVERRIDDEN by operator (reason: $reason). Audit-logged."
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
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  printf '{"hook":"secret-scan-block","tier":"BLOCK","ts":"%s","patterns_matched":"%s","blocked":true}\n' \
    "$ts" "$joined" >> "$AUDIT"
  echo "ERROR [JStack hook]: secret pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Remove the secret + re-stage." >&2
  echo "ERROR: To override (e.g. known-false-positive in test fixtures):" >&2
  echo '  JSTACK_OVERRIDE_SECRET=1 JSTACK_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 1
fi

exit 0
