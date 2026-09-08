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
      # Fractional -t needs bash >= 4; stock macOS bash 3.2 rejects it, the read
      # fails instantly and the gates would scan NOTHING (silent fail-open) —
      # probe once and fall back to an integer timeout. rc<=1 means EOF/timeout
      # (timeout value was accepted); rc>1 means the -t value itself was bad.
      local _t=0.2
      ( IFS= read -r -t 0.2 _ < /dev/null ) 2>/dev/null; [ $? -le 1 ] || _t=1
      IFS= read -r -d '' -t "$_t" _HOOK_STDIN_JSON 2>/dev/null || true
    fi
  fi
  printf '%s' "${_HOOK_STDIN_JSON:-}"
}

# _json_str_field <key> <json> — extract a JSON string value WITHOUT jq (sed
# fallback for machines that lack jq, e.g. stock Git-bash on Windows). Handles
# backslash-escaped chars inside the value. Best-effort: good enough for hook
# detection (git commands, file paths). The jq path is preferred when present.
_json_str_field() {
  printf '%s' "$2" | sed -nE "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"(([^\"\\\\]|\\\\.)*)\".*/\1/p" | head -1
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
    # -b preserves LF on native jq.exe; otherwise MSYS gets CR-suffixed paths.
    extracted="$(printf '%s' "$json" | jq -b -r "$jqf" 2>/dev/null || true)"
    if [ -n "$extracted" ]; then printf '%s' "$extracted"; return 0; fi
    # jq present but the field was empty: for payload, the raw JSON is still
    # greppable (secret scanners); for a specific field, fall through to argv1.
    [ "$field" = "payload" ] && { printf '%s' "$json"; return 0; }
  elif [ -n "$json" ]; then
    # No jq: extract the requested field with a sed fallback so the command/push/PII
    # block hooks still fire (payload stays raw JSON — it is greppable as-is).
    case "$field" in
      command)   extracted="$(_json_str_field command "$json")" ;;
      file_path) extracted="$(_json_str_field file_path "$json")"; [ -z "$extracted" ] && extracted="$(_json_str_field path "$json")" ;;
      prompt)    extracted="$(_json_str_field prompt "$json")"; [ -z "$extracted" ] && extracted="$(_json_str_field message "$json")" ;;
      payload|*) printf '%s' "$json"; return 0 ;;
    esac
    if [ -n "$extracted" ]; then printf '%s' "$extracted"; return 0; fi
  fi
  printf '%s' "$argv1"
}

# component: git-gate-content
# implements: ADR-0013
# intent: hooks/shared/secret-scan-block/HOOK.md
# constraints: .claude/engineering/audits/2026-06-12-launch-readiness-register.md (B3)
# last_intent_review: 2026-09-08
# Collection failure is distinct from a successful empty scan. These helpers
# never contact a remote or evaluate shell input. Unsupported target selection
# requires splitting the command or using the existing audited hook override.
_hook_git_error() { printf 'ERROR [Lintel hook]: cannot inspect Git operation: %s\n' "$1" >&2; return 2; }
# Pack transfer ignores local replacement objects; inspect that same history.
_hook_git() { git --no-replace-objects --no-pager -c core.fsmonitor=false -c log.diffMerges=separate -C "$@"; }

# Data-only shell tokenization. Quote removal preserves literal spaces; shell
# expansions, pipelines, redirections and grouping are deliberately unsupported.
# Parallel kind arrays distinguish an operator from a quoted commit message.
_hook_git_words() {
  local s="$1" i c q="" word="" started=0 next
  _HOOK_GIT_WORDS=(); _HOOK_GIT_KINDS=()
  s="${s//$'\\\r\n'/}"; s="${s//$'\\\n'/}"
  for ((i=0; i<${#s}; i++)); do
    c="${s:i:1}"; next="${s:i+1:1}"
    if [ "$q" = "'" ]; then
      if [ "$c" = "'" ]; then q=""; else word="$word$c"; fi
      continue
    fi
    if [ "$c" = '\' ]; then
      [ -n "$next" ] || { _hook_git_error 'trailing shell escape'; return 2; }
      if [ "$q" = '"' ] && [[ "$next" != '$' && "$next" != '`' && "$next" != '"' && "$next" != '\' ]]; then
        word="$word$c"
      else word="$word$next"; i=$((i+1)); fi
      started=1; continue
    fi
    case "$c" in '$'|'`') _hook_git_error 'shell expansion; use literal repository and ref arguments'; return 2 ;; esac
    if [ "$q" = '"' ]; then
      if [ "$c" = '"' ]; then q=""; else word="$word$c"; fi
      continue
    fi
    case "$c" in
      "'"|'"') q="$c"; started=1 ;;
      ' '|$'\t'|$'\r'|$'\n'|';'|'&'|'|')
        if [ "$started" = 1 ]; then
          _HOOK_GIT_WORDS+=("$word"); _HOOK_GIT_KINDS+=(word); word=""; started=0
        fi
        case "$c" in
          ';'|$'\n') _HOOK_GIT_WORDS+=(';'); _HOOK_GIT_KINDS+=(op) ;;
          '&'|'|')
            [ "$next" = "$c" ] || { _hook_git_error 'pipeline or background command'; return 2; }
            _HOOK_GIT_WORDS+=("$c$c"); _HOOK_GIT_KINDS+=(op); i=$((i+1)) ;;
        esac ;;
      '<'|'>'|'('|')'|'*'|'?'|'['|']'|'#') _hook_git_error 'unsupported shell syntax; use a literal Git command'; return 2 ;;
      *) word="$word$c"; started=1 ;;
    esac
  done
  [ -z "$q" ] || { _hook_git_error 'unclosed shell quote'; return 2; }
  if [ "$started" = 1 ]; then _HOOK_GIT_WORDS+=("$word"); _HOOK_GIT_KINDS+=(word); fi
}

# Optional config: status 1 means absent; every other failure is an inspection
# error. Callers must not turn corrupt config into an empty/default selection.
_hook_git_config() {
  local rc=0 flag="${3:---get}"
  _hook_git "$1" config "$flag" "$2" 2>/dev/null || rc=$?
  [ "$rc" -le 1 ] || { _hook_git_error 'Git configuration is unreadable'; return 2; }
}

# Read complete source history, including merge-resolution additions. Local
# tracking refs cannot prove the current destination state, so never exclude
# their ancestry. This may rescan old commits, but needs no network or cutoff.
_hook_git_history() {
  local repo="$1" spec="${2#+}" src oid
  case "$spec" in *'*'*|*'?'*|*'['*|*']'*|'^'*|'-'*) _hook_git_error 'unsupported push refspec pattern'; return 2 ;; esac
  case "$spec" in
    *:*) src="${spec%%:*}" ;;
    *) src="$spec" ;;
  esac
  [ -n "$src" ] || return 0 # deletion transfers no new objects
  oid=$(_hook_git "$repo" rev-parse --verify "$src^{commit}" 2>/dev/null) || {
    _hook_git_error 'push source is missing or is not a commit/tag pointing to a commit'; return 2;
  }
  _hook_git "$repo" log --format= --root -m -p --no-color --no-ext-diff --no-textconv --no-renames \
    "$oid" -- 2>/dev/null || {
      _hook_git_error 'outgoing commit history is unreadable'; return 2;
    }
}

_hook_git_push_content() {
  local repo="$1"; shift
  local remote="" arg options=1 all="" delete=0 follow="" branch="" configured mode refs ref spec group mirror
  local specs=()
  while [ "$#" -gt 0 ]; do
    arg="$1"; shift
    if [ "$options" = 1 ]; then
      case "$arg" in
        --) options=0; continue ;;
        --all|--branches|--tags|--mirror)
          [ -z "$all" ] || { _hook_git_error 'combined bulk push options'; return 2; }
          case "$arg" in --tags) all=tags ;; --mirror) all=all ;; *) all=heads ;; esac
          continue ;;
        --delete|-d) delete=1; continue ;;
        --follow-tags) follow=true; continue ;;
        --no-follow-tags) follow=false; continue ;;
        --repo) [ "$#" -gt 0 ] || { _hook_git_error 'missing --repo argument'; return 2; }; remote="$1"; shift; continue ;;
        --repo=*) remote="${arg#*=}"; continue ;;
        --push-option|-o) [ "$#" -gt 0 ] || { _hook_git_error 'missing push-option argument'; return 2; }; shift; continue ;;
        --push-option=*|--force-with-lease|--force-with-lease=*|--force-if-includes|--atomic|--dry-run|-n|--verbose|-v|--quiet|-q|--porcelain|--no-verify|--set-upstream|-u|--force|-f|--prune|--signed|--no-signed|--signed=*|--ipv4|--ipv6) continue ;;
        -*) _hook_git_error 'unsupported push option; use explicit source refs'; return 2 ;;
      esac
    fi
    if [ -z "$remote" ]; then remote="$arg"; else specs+=("$arg"); fi
  done
  branch=$(_hook_git "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null) || branch=""
  if [ -z "$remote" ]; then
    if [ -n "$branch" ]; then remote=$(_hook_git_config "$repo" "branch.$branch.pushRemote") || return 2; fi
    [ -n "$remote" ] || remote=$(_hook_git_config "$repo" remote.pushDefault) || return 2
    if [ -z "$remote" ] && [ -n "$branch" ]; then remote=$(_hook_git_config "$repo" "branch.$branch.remote") || return 2; fi
    [ -n "$remote" ] || remote=origin
  fi
  # Remote groups have per-remote mappings; refusing them avoids silently
  # inspecting one member while another publishes a different branch.
  group=$(_hook_git_config "$repo" "remotes.$remote" --get-all) || return 2
  [ -z "$group" ] || { _hook_git_error 'remote groups require separate explicit pushes'; return 2; }
  [ "$delete" = 0 ] || return 0
  mirror=$(_hook_git_config "$repo" "remote.$remote.mirror") || return 2
  case "$mirror" in true|yes|on|1) all=all ;; esac
  if [ -n "$all" ]; then
    [ "${#specs[@]}" -eq 0 ] || { _hook_git_error 'combined refspec and bulk push selection'; return 2; }
    case "$all" in heads) ref=refs/heads/ ;; tags) ref=refs/tags/ ;; all) ref=refs/ ;; esac
    refs=$(_hook_git "$repo" for-each-ref --format='%(refname)' "$ref") || { _hook_git_error 'push refs are unreadable'; return 2; }
    while IFS= read -r ref; do [ -z "$ref" ] || specs+=("$ref"); done <<< "$refs"
  elif [ "${#specs[@]}" -eq 0 ]; then
    configured=$(_hook_git_config "$repo" "remote.$remote.push" --get-all) || return 2
    if [ -n "$configured" ]; then
      while IFS= read -r spec; do specs+=("$spec"); done <<< "$configured"
    else
      [ -n "$branch" ] || { _hook_git_error 'default push from detached HEAD requires an explicit refspec'; return 2; }
      mode=$(_hook_git_config "$repo" push.default) || return 2
      case "${mode:-simple}" in
        simple|current) specs+=("HEAD:refs/heads/$branch") ;;
        upstream|tracking)
          ref=$(_hook_git_config "$repo" "branch.$branch.merge") || return 2
          [ -n "$ref" ] || { _hook_git_error 'upstream push has no destination ref'; return 2; }
          specs+=("HEAD:$ref") ;;
        *) _hook_git_error 'push.default requires explicit source refspecs'; return 2 ;;
      esac
    fi
  fi
  # Follow-tags transfers only tags reachable from these commits; scanning their
  # entire ancestry below already covers the added objects. Tag messages are
  # outside the existing diff-content contract, as are commit messages.
  if [ -z "$follow" ]; then follow=$(_hook_git_config "$repo" push.followTags) || return 2; fi
  for spec in "${specs[@]}"; do
    [ "$spec" != : ] || { _hook_git_error 'matching push requires explicit source refs'; return 2; }
    _hook_git_history "$repo" "$spec" || return 2
  done
}

# <command-string> -> added diff lines, rc0 (including clean); rc2 on any
# inspection failure. Commit and push are deliberately separate: unstaged files
# are relevant to commit -a, but cannot be published by a plain push.
hook_git_gate_content() {
  local cmd="${1:-}" cwd="$PWD" i start=0 end n j word repo op raw="" part ambiguous=0 inspected=0
  local args=()
  _hook_git_words "$cmd" || return 2
  n=${#_HOOK_GIT_WORDS[@]}
  for ((end=0; end<=n; end++)); do
    if [ "$end" -lt "$n" ] && [ "${_HOOK_GIT_KINDS[end]}" != op ]; then continue; fi
    args=(); for ((i=start; i<end; i++)); do args+=("${_HOOK_GIT_WORDS[i]}"); done
    start=$((end+1)); [ "${#args[@]}" -gt 0 ] || continue
    j=0
    # Only wrappers that preserve identity, lookup and environment are safe to
    # peel. Unknown wrappers/options fail below, never become an empty scan.
    while [ "$j" -lt "${#args[@]}" ]; do
      case "${args[j]}" in
        command|env)
          j=$((j+1))
          [ "${args[j]:-}" != -- ] || j=$((j+1))
          continue ;;
      esac
      if [[ "${args[j]}" =~ ^[A-Za-z_][A-Za-z_0-9]*= ]]; then
        case "${args[j]}" in GIT_*=*|PATH=*|HOME=*|XDG_CONFIG_HOME=*|CDPATH=*) _hook_git_error 'Git environment overrides require a separate command'; return 2 ;; esac
        j=$((j+1)); continue
      fi
      break
    done
    [ "$j" -lt "${#args[@]}" ] || { _hook_git_error 'wrapper or assignment has no Git command'; return 2; }
    word="${args[j]}"; j=$((j+1))
    case "$word" in
      true|:) continue ;;
      cd)
        [ "$j" -eq $((${#args[@]}-1)) ] || { _hook_git_error 'unsupported cd command'; return 2; }
        cwd=$(cd "$cwd" && cd -- "${args[j]}" && pwd -P) || { _hook_git_error 'repository directory is unavailable'; return 2; }
        continue ;;
      git|*/git) ;;
      *) _hook_git_error 'unsupported command or wrapper; use a literal Git command'; return 2 ;;
    esac
    repo="$cwd"
    while [ "$j" -lt "${#args[@]}" ] && [ "${args[j]}" = -C ]; do
      j=$((j+1)); [ "$j" -lt "${#args[@]}" ] || { _hook_git_error 'missing git -C directory'; return 2; }
      if [ -n "${args[j]}" ]; then
        repo=$(cd "$repo" && cd -- "${args[j]}" && pwd -P) || { _hook_git_error 'git -C directory is unavailable'; return 2; }
      fi
      j=$((j+1))
    done
    op="${args[j]:-}"; j=$((j+1))
    case "$op" in
      commit|push) ;;
      -*) _hook_git_error 'unsupported Git global option'; return 2 ;;
      *) _hook_git_error 'unsupported Git operation in command chain; split commands'; return 2 ;;
    esac
    [ "$ambiguous" = 0 ] || { _hook_git_error 'preceding command may change the index, repository or refs; split commands'; return 2; }
    _hook_git "$repo" rev-parse --git-dir >/dev/null 2>&1 || { _hook_git_error 'repository is unreadable'; return 2; }
    if [ "$op" = commit ]; then
      part=$(_hook_git "$repo" diff --no-color --no-ext-diff --no-textconv --cached -- 2>/dev/null) || { _hook_git_error 'index diff is unreadable'; return 2; }
      raw="$raw$part"$'\n'
      part=$(_hook_git "$repo" diff --no-color --no-ext-diff --no-textconv -- 2>/dev/null) || { _hook_git_error 'worktree diff is unreadable'; return 2; }
    else
      part=$(_hook_git_push_content "$repo" "${args[@]:j}") || return 2
    fi
    raw="$raw$part"$'\n'; ambiguous=1; inspected=1
  done
  [ "$inspected" = 1 ] || { _hook_git_error 'no Git commit or push was inspected'; return 2; }
  # awk returns success for a genuinely empty result; Git failures have already
  # returned above, so they can never be confused with a clean diff.
  printf '%s' "$raw" | awk '
    /^diff --git / { hunk=0 }
    /^@@ / { hunk=1; next }
    hunk && /^\+/ { print }
  '
}
