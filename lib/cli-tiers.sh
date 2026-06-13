#!/usr/bin/env bash
# lib/cli-tiers.sh — read the harness-level per-CLI capability tier from
# lib/cli-tiers.yaml. The single source shared by skills/welcome (the honest
# first-run tier message) and bin/li-wiki-gen (which generates the README
# capability table). awk-based + CRLF-safe; no yq dependency. Idempotent source.
#
# cli_tier_field <cli> <field>  -> prints the value. Fingerprint aliases
#   (copilot-cli/copilot-app -> copilot, claude -> claude-code, factory-droid ->
#   droid) land on their real row. Unknown CLI or missing field returns a SAFE
#   default (tier=best-effort, hooks_supported=false, label=the raw name), so a
#   new or unrecognized CLI degrades honestly instead of crashing or over-claiming.
# cli_tier_normalize <raw-id>   -> canonical cli-tiers.yaml key (unknown -> other).
# cli_tier_list                 -> prints each cli key, one per line (for iteration).
command -v cli_tier_field >/dev/null 2>&1 && return 0 2>/dev/null

_CLI_TIERS_YAML="${_CLI_TIERS_YAML:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cli-tiers.yaml}"

# cli_tier_normalize <raw-id> -> the canonical cli-tiers.yaml key (one of the 8 rows).
# The fingerprint runtime (skills/cli-fingerprint) emits finer-grained IDs than the
# tier table keys — map aliases onto their row; anything unrecognized maps to
# `other` (the honest best-effort row), so a row-guaranteed lookup (e.g.
# /li:welcome's first-run banner) can always reach a real entry.
cli_tier_normalize() {
  case "${1:-}" in
    claude|claude-code)                 printf 'claude-code' ;;
    copilot|copilot-cli|copilot-app)    printf 'copilot' ;;
    droid|factory-droid)                printf 'droid' ;;
    codex|cursor|gemini|opencode|other) printf '%s' "$1" ;;
    *)                                  printf 'other' ;;
  esac
}

cli_tier_field() {
  local cli="$1" field="$2" val=""
  # Alias-map fingerprint IDs onto table rows. Deliberately NOT the full
  # cli_tier_normalize: a truly-unknown ID must stay raw so the safe-default
  # fallback below echoes its name in `label` (the honest-degrade contract
  # locked by tests/unit/cli-tiers.sh) instead of borrowing the `other` row's.
  case "$cli" in
    claude)                  cli="claude-code" ;;
    copilot-cli|copilot-app) cli="copilot" ;;
    factory-droid)           cli="droid" ;;
  esac
  if [ -f "$_CLI_TIERS_YAML" ]; then
    # cli keys are indented 2 spaces under `clis:`; fields 4 spaces under each cli.
    val=$(awk -v cli="  ${cli}:" -v field="${field}:" '
      { sub(/\r$/, "") }
      $0 == cli { inblock = 1; next }
      inblock && /^  [A-Za-z._-]+:[ \t]*$/ { inblock = 0 }   # next cli block
      inblock {
        line = $0; sub(/^[ \t]+/, "", line)
        if (index(line, field) == 1) {
          v = substr(line, length(field) + 1)
          sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v)
          gsub(/^"|"$/, "", v)
          print v; exit
        }
      }
    ' "$_CLI_TIERS_YAML")
  fi
  if [ -z "$val" ]; then
    case "$field" in
      tier)                        val="best-effort" ;;
      hooks_supported|skills_native) val="false" ;;
      subagents)                   val="none" ;;
      label)                       val="$cli" ;;
      *)                           val="" ;;
    esac
  fi
  printf '%s' "$val"
}

cli_tier_list() {
  [ -f "$_CLI_TIERS_YAML" ] || return 0
  awk '
    { sub(/\r$/, "") }
    /^clis:[ \t]*$/ { inclis = 1; next }
    inclis && /^[A-Za-z]/ { inclis = 0 }              # left the clis: block
    inclis && /^  [A-Za-z._-]+:[ \t]*$/ {
      k = $0; sub(/^  /, "", k); sub(/:[ \t]*$/, "", k); print k
    }
  ' "$_CLI_TIERS_YAML"
}

# cli_tiers_markdown_table -> the honest capability table, GENERATED from cli-tiers.yaml.
# This is the single generator: README embeds its output between CLI-TIERS markers
# (refreshed by bin/li-wiki-gen) and tests/shape/cli-tiers-sync.sh asserts they match,
# so the "honest table" can never silently drift from reality again.
cli_tiers_markdown_table() {
  local c label tier sk sub hk
  printf '| CLI | Tier | Skills | Subagents | Hooks |\n'
  printf '|---|---|---|---|---|\n'
  for c in $(cli_tier_list); do
    label=$(cli_tier_field "$c" label)
    tier=$(cli_tier_field "$c" tier)
    sk=$(cli_tier_field "$c" skills_native);   [ "$sk" = "true" ] && sk="native" || sk="manual"
    sub=$(cli_tier_field "$c" subagents)
    hk=$(cli_tier_field "$c" hooks_supported)
    if [ "$hk" = "true" ]; then hk="yes"; else hk="no (Claude Code only)"; fi
    printf '| %s | %s | %s | %s | %s |\n' "$label" "$tier" "$sk" "$sub" "$hk"
  done
}
