#!/usr/bin/env bash
# lib/wiki-gen.sh — wiki-gen helpers, sourced by bin/li-wiki-gen.
#
# Provides helpers that bin/li-wiki-gen uses for parsing + rendering.
# Phase 3 keeps most logic inline in bin/li-wiki-gen for portability;
# this file holds reusable helpers that may also be sourced by other tools.

set -uo pipefail

# Parse a YAML scalar (handles inline-flow and block form).
# Usage: wgen_yaml_scalar <file> <key>
wgen_yaml_scalar() {
  local file="${1:?}" key="${2:?}"
  grep -E "^${key}:" "$file" 2>/dev/null | head -1 | awk -F': *' '{print $2}' | tr -d '"' | tr -d "'" | tr -d '[:space:]'
}

# Parse a frontmatter scalar from a markdown file's YAML frontmatter.
wgen_fm_scalar() {
  local file="${1:?}" field="${2:?}"
  awk -v field="$field" '
    /^---$/ { if (++fm == 2) exit; next }
    fm == 1 && $0 ~ "^"field":" {
      sub("^"field":[[:space:]]*", "")
      sub("[[:space:]]*#.*$", "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      print
      exit
    }
  ' "$file"
}

# Detect if a markdown file declares workflow_root: true in frontmatter.
wgen_is_workflow_root() {
  local file="${1:?}"
  awk '
    /^---$/ { if (++fm == 2) exit; next }
    fm == 1 && /^workflow_root:[[:space:]]*true/ { print "yes"; exit }
  ' "$file"
}

# Render a markdown table row from given cells.
wgen_render_row() {
  local IFS='|'
  printf '| %s |\n' "$*"
}

# Count entries in a directory matching a glob.
wgen_count() {
  local dir="${1:?}" pattern="${2:-*}"
  find "$dir" -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Generate a deterministic timestamp for output headers (defaults to now,
# can be overridden via WGEN_TS env var for reproducible builds).
wgen_ts() {
  printf '%s' "${WGEN_TS:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
}
