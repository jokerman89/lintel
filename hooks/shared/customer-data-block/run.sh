#!/usr/bin/env bash
# customer-data-block — Lintel JUSTIFIED-BLOCK hook
# Blocks git commit/push if a customer-data pattern is in staged content.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"
# Shared customer-PII patterns (defined once in _patterns.sh).
source "$(dirname "${BASH_SOURCE[0]}")/../_patterns.sh"

# Fire on any git commit/push however phrased (battletest K2 — the `^git` anchor
# was bypassed by `git -C`, abs paths, `&&` chains).
if ! printf '%s' "$CMD" | grep -qE '(^|[^A-Za-z0-9_-])git([[:space:]]|$).*\b(commit|push)\b'; then
  exit 0
fi

# Override FIRST so it always audits (battletest H8). Honor env OR command-string token.
if [ "${LINTEL_OVERRIDE_CUSTOMER_DATA:-}" = "1" ] || printf '%s' "$CMD" | grep -q 'LINTEL_OVERRIDE_CUSTOMER_DATA=1'; then
  reason="${LINTEL_OVERRIDE_REASON:-no-reason-given}"
  audit_log "hooks" "customer_data_block" "hook=customer-data-block" "tier=OVERRIDDEN" "override=true" "reason=$reason" "blocked=false"
  echo "INFO [Lintel hook]: customer-data-block OVERRIDDEN (reason: $reason). Audit-logged."
  exit 0
fi

# Staged + unstaged-tracked (covers `commit -am`; battletest K2).
STAGED="$(git diff --cached 2>/dev/null || true)"
WORKTREE="$(git diff 2>/dev/null || true)"
CONTENT="$STAGED
$WORKTREE"
[ -z "$(printf '%s' "$CONTENT" | tr -d '[:space:]')" ] && exit 0

joined="$(scan_customer "$CONTENT")"

if [ -n "$joined" ]; then
  audit_log "hooks" "customer_data_block" "hook=customer-data-block" "tier=BLOCK" "patterns_matched=$joined" "blocked=true"
  echo "ERROR [Lintel hook]: customer-data pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Sanitize the staged content (placeholders) + re-stage." >&2
  echo "ERROR: To override (e.g. confirmed placeholder, public-domain example):" >&2
  echo '  LINTEL_OVERRIDE_CUSTOMER_DATA=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 2   # 2 = blocking error in Claude Code; exit 1 only WARNS while the call proceeds
fi

exit 0
