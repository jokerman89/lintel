#!/usr/bin/env bash
# secret-scan-block — Lintel JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 secret pattern in staged content.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"
# Shared detection patterns (defined once). Block hook → strict `tier1` (high-confidence only).
source "$(dirname "${BASH_SOURCE[0]}")/../_patterns.sh"

# Fire on any git commit/push, however the command is phrased: `git commit`,
# `git -C path commit`, `/usr/bin/git push`, `true && git commit`, `cd x && git
# commit -am`. The old `^git` anchor was trivially bypassed (security battletest
# K2). Word-boundary match on both `git` and the subcommand.
if ! printf '%s' "$CMD" | grep -qE '(^|[^A-Za-z0-9_-])git([[:space:]]|$).*\b(commit|push)\b'; then
  exit 0
fi

# Override path — checked BEFORE everything else so an explicit override always
# audits (battletest H8: the override branch sat after the matcher and an inline
# `LINTEL_OVERRIDE_SECRET=1 git commit` left no record). Honor either the hook's
# own env OR the token in the command string the operator typed.
if [ "${LINTEL_OVERRIDE_SECRET:-}" = "1" ] || printf '%s' "$CMD" | grep -q 'LINTEL_OVERRIDE_SECRET=1'; then
  reason="${LINTEL_OVERRIDE_REASON:-no-reason-given}"
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=OVERRIDDEN" "override=true" "reason=$reason" "blocked=false"
  echo "INFO [Lintel hook]: secret-scan-block OVERRIDDEN by operator (reason: $reason). Audit-logged."
  exit 0
fi

# Scan staged AND unstaged-tracked changes. `git commit -am`/`-a` stages tracked
# edits at commit time — AFTER this PreToolUse hook runs — so a `--cached`-only
# scan misses them (battletest K2). Union covers both; push is covered by staged.
STAGED="$(git diff --cached 2>/dev/null || true)"
WORKTREE="$(git diff 2>/dev/null || true)"
CONTENT="$STAGED
$WORKTREE"
[ -z "$(printf '%s' "$CONTENT" | tr -d '[:space:]')" ] && exit 0

joined="$(scan_secrets tier1 "$CONTENT")"

if [ -n "$joined" ]; then
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "patterns_matched=$joined" "blocked=true"
  echo "ERROR [Lintel hook]: secret pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Remove the secret + re-stage." >&2
  echo "ERROR: To override (e.g. known-false-positive in test fixtures):" >&2
  echo '  LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 2   # 2 = blocking error in Claude Code; exit 1 only WARNS while the call proceeds
fi

exit 0
