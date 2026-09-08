#!/usr/bin/env bash
# component: secret-scan-block
# implements: ADR-0013
# intent: docs/compliance.md
# constraints: pattern coverage and host activation limits in docs/compliance.md
# last_intent_review: 2026-09-08
# secret-scan-block — Lintel JUSTIFIED-BLOCK hook
# Blocks git commit/push if Tier 1 secret pattern in staged content.

# NOT `set -e` (issue I1 / claude-code #60490): under -e an upstream grep/tr
# returning non-zero would exit this script BEFORE the blocking `exit 2`, and
# Claude Code treats any non-2 exit as NON-blocking — the secret commits through.
# Explicit exits only (0 = allow, 2 = block); -u/pipefail kept for correctness.
set -uo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
CMD="$(hook_input command "${1:-}")"
[ -z "$CMD" ] && exit 0

# Match against a FLATTENED copy: a line-continuation newline between `git` and
# the subcommand defeats a line-oriented grep (silent fail-open), and a newline
# inside -m lets the second line forge the '^'-anchored override token (L-012
# class). Content scanning below still sees the real multi-line diff.
CMD_FLAT="$(printf '%s' "$CMD" | tr '\n\r' '  ')"

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
if ! printf '%s' "$CMD_FLAT" | grep -qE '(^|[^A-Za-z0-9_-])git([[:space:]]|$).*\b(commit|push)\b'; then
  exit 0
fi

# Override path — checked BEFORE everything else so an explicit override always
# audits (battletest H8: the override branch sat after the matcher and an inline
# `LINTEL_OVERRIDE_SECRET=1 git commit` left no record). Honor either the hook's
# own env OR the token in the command string the operator typed.
# Honor the override via the hook's env OR a LEADING env-assignment on the
# command (`LINTEL_OVERRIDE_SECRET=1 [VAR=v ...] git commit …`) — NEVER the token
# appearing inside a quoted arg / -m message (review P0: that re-opened a
# forgeable fail-open). The anchored prefix is what the operator actually types.
if [ "${LINTEL_OVERRIDE_SECRET:-}" = "1" ] || printf '%s' "$CMD_FLAT" | grep -qE '^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*LINTEL_OVERRIDE_SECRET=1([[:space:]]|=|$)'; then
  reason="${LINTEL_OVERRIDE_REASON:-no-reason-given}"
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=OVERRIDDEN" "override=true" "reason=$reason" "blocked=false"
  echo "INFO [Lintel hook]: secret-scan-block OVERRIDDEN by operator (reason: $reason). Audit-logged."
  exit 0
fi

# The shared collector follows the literal Git target. Commits scan staged +
# tracked edits (including commit -a); pushes scan the selected commit histories.
# Fail-closed (issue I1 / ADR-0013): the matcher fired (a git commit/push is in
# flight) and it was not overridden — if the scanner failed to load, BLOCK rather
# than silently allow. Positioned AFTER matcher+override (not after the patterns
# source) so a broken scanner blocks the real threat (git commits) while non-git
# commands pass and the documented override stays reachable — ADR-0013 requires
# the error to name a USABLE override. Audit the block (launch-waves wave).
if ! command -v scan_secrets >/dev/null 2>&1; then
  command -v audit_log >/dev/null 2>&1 && audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "blocked=true" "reason=scanner-unavailable"
  echo "ERROR [Lintel hook]: secret-scan-block scanner unavailable — blocking to be safe." >&2
  echo "ERROR: source hooks/shared/_patterns.sh failed. Override only if you are certain:" >&2
  echo '  LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 2
fi

if ! CONTENT="$(hook_git_gate_content "$CMD")"; then
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "blocked=true" "reason=collection-unavailable"
  echo "ERROR [Lintel hook]: secret-scan-block could not inspect the Git operation; blocked." >&2
  echo 'Use a literal Git command, or the existing LINTEL_OVERRIDE_SECRET=1 override with LINTEL_OVERRIDE_REASON.' >&2
  exit 2
fi
[ -z "$(printf '%s' "$CONTENT" | tr -d '[:space:]')" ] && exit 0

if ! joined="$(scan_secrets tier1 "$CONTENT")"; then
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "blocked=true" "reason=scan-unavailable"
  echo "ERROR [Lintel hook]: secret-scan-block pattern scan failed; blocked." >&2
  echo 'Use the existing LINTEL_OVERRIDE_SECRET=1 override with LINTEL_OVERRIDE_REASON only after review.' >&2
  exit 2
fi

if [ -n "$joined" ]; then
  audit_log "hooks" "secret_scan_block" "hook=secret-scan-block" "tier=BLOCK" "patterns_matched=$joined" "blocked=true"
  echo "ERROR [Lintel hook]: secret pattern in staged content — $joined" >&2
  echo "ERROR: COMMIT BLOCKED. Remove the secret + re-stage." >&2
  echo "ERROR: To override (e.g. known-false-positive in test fixtures):" >&2
  echo '  LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="<reason>" git commit ...' >&2
  exit 2   # 2 = blocking error in Claude Code; exit 1 only WARNS while the call proceeds
fi

exit 0
