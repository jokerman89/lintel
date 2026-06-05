#!/usr/bin/env bash
# hooks/shared/_input.sh — shared hook input adapter (dual-mode).
#
# Claude Code delivers tool data to a hook as a JSON object on STDIN
# (PreToolUse / UserPromptSubmit / etc.). Lintel's hooks were written to read the
# payload from $1, so under Claude Code they received nothing and silently no-op'd
# — the "blocking" finding of the v4.9 five-lens audit.
#
# hook_input reads the stdin JSON once (when present) and extracts the requested
# field; when there is no stdin payload (manual `run.sh <arg>` testing, a git-hook
# install, another CLI, or a unit test) it falls back to $1. The $1 path is
# preserved exactly, so existing call sites and tests keep working — the stdin
# path is purely additive.
#
# Idempotent source. Safe under `set -euo pipefail`.

command -v hook_input >/dev/null 2>&1 && return 0 2>/dev/null

# _hook_stdin — read stdin ONCE, cache it. Never blocks: skips a TTY, and bounds
# the read to 0.2s so an inherited-but-idle stdin (CI, test runner) cannot hang.
_hook_stdin() {
  if [ -z "${_HOOK_STDIN_READ:-}" ]; then
    _HOOK_STDIN_READ=1
    _HOOK_STDIN_JSON=""
    if [ ! -t 0 ]; then
      # -d '' reads the whole object (newlines included); -t bounds the wait.
      IFS= read -r -d '' -t 0.2 _HOOK_STDIN_JSON 2>/dev/null || true
    fi
  fi
  printf '%s' "${_HOOK_STDIN_JSON:-}"
}

# hook_input <field> [argv1]
#   field: payload | command | file_path | prompt
#   Returns the field from the Claude Code stdin JSON when available, else argv1.
#   payload = a joined text blob of every useful field (for content scanners).
hook_input() {
  local field="${1:-payload}" argv1="${2:-}" json jqf extracted
  json="$(_hook_stdin)"
  if [ -n "$json" ] && command -v jq >/dev/null 2>&1; then
    case "$field" in
      command)   jqf='.tool_input.command // empty' ;;
      file_path) jqf='.tool_input.file_path // .tool_input.path // .tool_input.notebook_path // empty' ;;
      prompt)    jqf='.prompt // .user_prompt // .message // empty' ;;
      payload|*) jqf='[.tool_input.content?, .tool_input.new_string?, .tool_input.old_string?, .tool_input.command?, .tool_input.file_path?, .prompt?, .message?] | map(select(. != null and . != "")) | join("\n")' ;;
    esac
    extracted="$(printf '%s' "$json" | jq -r "$jqf" 2>/dev/null || true)"
    if [ -n "$extracted" ]; then printf '%s' "$extracted"; return 0; fi
    # jq present but the field was empty: for payload, the raw JSON is still
    # greppable (secret scanners); for a specific field, fall through to argv1.
    [ "$field" = "payload" ] && { printf '%s' "$json"; return 0; }
  elif [ -n "$json" ]; then
    # No jq: a specific field can't be parsed, but the raw JSON is greppable.
    [ "$field" = "payload" ] && { printf '%s' "$json"; return 0; }
  fi
  printf '%s' "$argv1"
}
