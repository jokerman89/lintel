#!/usr/bin/env bash
# component: frozen-zone-warning
# implements: ADR-0005, ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: optional warn-only hook; never changes permission or freeze state
# last_intent_review: 2026-09-25

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" || exit 0
source "$ROOT/hooks/shared/_input.sh" || exit 0
TARGET_PATH="$(hook_input file_path "${1:-}")"
[ -z "$TARGET_PATH" ] && exit 0

source "$ROOT/lib/paths.sh" || exit 0
REPO="$(lintel_repo_root)" || exit 0
[ -n "$REPO" ] || exit 0

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$ROOT/bin/_audit.sh" || exit 0

# Collect frozen patterns from session + project CLAUDE.md
SESSION_ID="${LINTEL_SESSION_ID:-${CLAUDE_SESSION_ID:-${LINTEL_CYCLE_ID:-}}}"
PROJECT_CLAUDE_MD="$REPO/CLAUDE.md"

session_match=""
project_match=""

# Read the same state grammar as the producer; failure is unknown scope, not an empty list.
if [ -n "$SESSION_ID" ]; then
  python_cmd="${LINTEL_PYTHON:-python3}"
  if ! session_match=$("$python_cmd" -B "$ROOT/skills/code-freeze/scripts/freeze.py" \
      --repo "$REPO" --state-dir "$(lintel_state_dir)" --session "$SESSION_ID" \
      --legacy-file "$LINTEL_HOME/freeze/$SESSION_ID.yaml" --check "$TARGET_PATH"); then
    echo "WARN [Lintel hook]: session freeze scope could not be read; no enforcement is claimed."
    session_match=""
  fi
  session_match="${session_match%%$'\n'*}"
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
  if [ "$source" = session-freeze ]; then
    echo "WARN: Inspect /li:code-freeze --list; use --lift only for an authorized scope change. (warn-only.)"
  else
    echo "WARN: A project frozen-zone rule needs its own explicit exception; runtime --lift cannot override it."
  fi
fi

exit 0
