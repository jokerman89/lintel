#!/usr/bin/env bash
# component: copilot-profile-bootstrap
# implements: ADR-0024, ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: selected repo runtime only; explicit approved paths remain authoritative
# last_intent_review: 2026-09-20
# Source this helper, then call lintel_copilot_env <working-repository> before
# canonical shell helpers. Source files and generated state have distinct roots.
_LINTEL_COPILOT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

lintel_copilot_env() {
  local repo context reference
  repo="$(cd "${1:-${LINTEL_REPO_ROOT:-.}}" && pwd)" || return 1
  [ -f "$repo/AGENTS.md" ] || {
    echo "ERROR: expected a scaffolded working repository at $repo" >&2
    return 1
  }
  export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-$_LINTEL_COPILOT_SOURCE}"
  export LINTEL_REPO_ROOT="$repo"
  # No global installation is required. Explicit operator configuration wins.
  export LINTEL_HOME="${LINTEL_HOME:-$repo/.claude/runtime/lintel-home}"
  export LINTEL_PACKS_DIR="${LINTEL_PACKS_DIR:-$LINTEL_HOME/packs}"
  export LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$repo/.claude/runtime/audit}"
  context="${2:-${LINTEL_PROFILE_CONTEXT:-}}"
  [ -f "$LINTEL_SOURCE_ROOT/lib/profile_context.py" ] || {
    echo "ERROR: structured profile helper missing from approved source bundle" >&2
    return 2
  }
  source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh" || return $?
  # No host ID means one explicitly selected repository work context, not a new
  # process-derived session on each call. Drift blocks before lifecycle work.
  reference=$(LINTEL_PROFILE_CONTEXT="$context" _profile_cli bootstrap) || return $?
  _profile_accept_reference "$reference" "$context"
}
