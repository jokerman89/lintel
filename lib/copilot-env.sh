#!/usr/bin/env bash
# Source this helper, then call lintel_copilot_env <working-repository> before
# canonical shell helpers. Source files and generated state have distinct roots.
_LINTEL_COPILOT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

lintel_copilot_env() {
  local repo
  repo="$(cd "${1:-.}" && pwd)" || return 1
  [ -f "$repo/AGENTS.md" ] || {
    echo "ERROR: expected a scaffolded working repository at $repo" >&2
    return 1
  }
  export LINTEL_SOURCE_ROOT="$_LINTEL_COPILOT_SOURCE"
  export LINTEL_REPO_ROOT="$repo"
  # No global installation is required. Explicit operator configuration wins.
  export LINTEL_HOME="${LINTEL_HOME:-$repo/.claude/runtime/lintel-home}"
  export LINTEL_PACKS_DIR="${LINTEL_PACKS_DIR:-$LINTEL_SOURCE_ROOT/packs}"
  export LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$repo/.claude/runtime/audit}"
}
