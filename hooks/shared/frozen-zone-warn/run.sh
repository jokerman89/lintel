#!/usr/bin/env bash
# frozen-zone-warn — Lintel warn-only hook
# Warns when Edit/Write targets a frozen-zone path.

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/../_input.sh"
TARGET_PATH="$(hook_input file_path "${1:-}")"
[ -z "$TARGET_PATH" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

# Collect frozen patterns from session + project CLAUDE.md
SESSION_ID="${LINTEL_SESSION_ID:-default}"
SESSION_FREEZE="$LINTEL_HOME/freeze/${SESSION_ID}.yaml"
PROJECT_CLAUDE_MD="$(pwd)/CLAUDE.md"

session_match=""
project_match=""

# Check session freeze (simple grep — full YAML parser would be better)
if [ -f "$SESSION_FREEZE" ]; then
  while IFS= read -r line; do
    path=$(echo "$line" | sed -n 's/^[ ]*-[ ]*path:[ ]*//p' | tr -d '\"')
    [ -z "$path" ] && continue
    if [[ "$TARGET_PATH" == "$path"* ]]; then
      session_match="$path"
      break
    fi
  done < "$SESSION_FREEZE"
fi

# Check project CLAUDE.md "Frozen zones" section (heuristic)
if [ -f "$PROJECT_CLAUDE_MD" ]; then
  in_section=0
  while IFS= read -r line; do
    if echo "$line" | grep -qE '^##+ Frozen zones'; then
      in_section=1
      continue
    fi
    if [ "$in_section" = "1" ]; then
      if echo "$line" | grep -qE '^##+ '; then
        in_section=0
        continue
      fi
      # Extract path-like tokens from bullet
      path=$(echo "$line" | sed -nE 's/^[-*][ ]+`?([^`]+)`?.*/\1/p')
      [ -z "$path" ] && continue
      if [[ "$TARGET_PATH" == *"$path"* ]]; then
        project_match="$path"
        break
      fi
    fi
  done < "$PROJECT_CLAUDE_MD"
fi

if [ -n "$session_match" ] || [ -n "$project_match" ]; then
  source=""
  matched=""
  if [ -n "$session_match" ]; then
    source="session-freeze"
    matched="$session_match"
  else
    source="project-claude-md"
    matched="$project_match"
  fi
  audit_log "hooks" "frozen_zone_warn" "hook=frozen-zone-warn" "tier=warn" "frozen_path=$matched" "edit_target=$TARGET_PATH" "source=$source"
  echo "WARN [Lintel hook]: editing $TARGET_PATH which is in frozen zone ($matched, source: $source)"
  echo "WARN: Use /unfreeze if intentional, or consider whether this edit is correct. (warn-only.)"
fi

exit 0
