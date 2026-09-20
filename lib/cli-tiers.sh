#!/usr/bin/env bash
# component: client-capability-shell-compatibility
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: conservative legacy view; never a tool permission or runtime guarantee
# last_intent_review: 2026-09-20
command -v cli_tier_field >/dev/null 2>&1 && return 0 2>/dev/null
_CLI_TIERS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
_CLI_TIERS_YAML="${_CLI_TIERS_YAML:-$_CLI_TIERS_ROOT/lib/cli-tiers.yaml}"

_cli_capabilities() {
  local interpreter
  if command -v python3 >/dev/null 2>&1; then interpreter=python3
  elif command -v python >/dev/null 2>&1; then interpreter=python
  else
    printf 'ERROR: client capabilities require Python 3.9+; no capability inferred.\n' >&2
    return 1
  fi
  "$interpreter" "$_CLI_TIERS_ROOT/bin/li-client-capabilities.py" "$@" --registry "$_CLI_TIERS_YAML"
}

cli_tier_normalize() {
  _cli_capabilities field --client "${1:-other}" --field id
}

cli_tier_field() {
  _cli_capabilities field --client "${1:-other}" --field "${2:?field required}"
}

cli_tier_list() {
  _cli_capabilities list
}

cli_tiers_markdown_table() {
  _cli_capabilities table
}
