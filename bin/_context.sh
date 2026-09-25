#!/usr/bin/env bash
# component: lintel-context
# implements: ADR-0006
# intent: docs/concepts/memory-v2.md
# constraints: helpers own paths/naming/discovery; content stays LLM-written
# last_intent_review: 2026-09-25
#
# bin/_context.sh — mechanical core for pause, resume and context warming.
# Closes the prose-only gap: 5 context skills shipped with zero bash. The
# LLM still writes/reads the checkpoint CONTENT; these helpers make the
# path handling, naming and discovery deterministic.
#
#   context_save_path [label]   → reserves a unique empty checkpoint; caller writes content
#   context_list [branch]       → all checkpoints newest-first (new + legacy dirs)
#   context_latest [branch]     → newest checkpoint path (empty if none)
#   context_select <flags>      → bounded literal/glob source manifest (no content execution)
#   context_checkpoint <path>   → manifest for an owned checkpoint; --explicit permits a shared path
#
# Scope: checkpoints live in <repo>/.claude/runtime/sessions/<branch>/ (v5,
# ADR-0005); the legacy ~/.lintel/sessions/<branch>/ remains an owner-filtered,
# read-only fallback. Historical checkpoints are not deleted when a date passes.
# Helper names and the -context-save.md filename grammar are persisted compatibility.

_CONTEXT_BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
command -v lintel_sessions_dir >/dev/null 2>&1 || source "$_CONTEXT_BIN_DIR/../lib/paths.sh"

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

context_resume_kind() {
  [ "$#" -ge 1 ] && [ -n "$1" ] || {
    echo 'Resume --from requires one nonempty operand.' >&2
    return 2
  }
  local value="$1" step
  shift
  case "$value" in
    *$'\n'*|*$'\r'*|--*) echo 'Invalid resume operand; use an explicit path for a flag-shaped filename.' >&2; return 2 ;;
    ./*|../*|*/*|*\\*|[A-Za-z]:*) printf 'checkpoint\n'; return 0 ;;
    SENSE|SCOPE|DEFINE|DISCOVER|PLAN|BUILD|REVIEW|SHIP|CAPTURE) printf 'phase\n'; return 0 ;;
  esac
  for step in "$@"; do
    [ "$value" != "$step" ] || { printf 'step\n'; return 0; }
  done
  printf 'checkpoint\n'
}

_context_run() {
  local python
  for python in python3 python; do
    if command -v "$python" >/dev/null 2>&1 && \
        "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
      PYTHONDONTWRITEBYTECODE=1 "$python" "$_CONTEXT_BIN_DIR/../lib/context_safety.py" "$@"
      return $?
    fi
  done
  echo 'Context helpers require Python 3.9+; no operation performed.' >&2
  return 1
}

_context_valid_branch() {
  # HEAD is the historical detached-checkout bucket, not a named branch ref.
  [ "$1" = HEAD ] && return 0
  git check-ref-format --branch "$1" >/dev/null 2>&1 || {
    echo 'Invalid checkpoint branch; refusing path traversal.' >&2
    return 1
  }
}

_context_branch() {
  local root branch
  root=$(_context_repo_identity) || return 1
  if branch=$(git -C "$root" symbolic-ref --quiet --short HEAD 2>/dev/null); then
    printf '%s\n' "$branch"
  elif git -C "$root" rev-parse --verify HEAD >/dev/null 2>&1; then
    printf 'HEAD\n'
  else
    printf 'no-branch\n'
  fi
}

_context_repo_slug() {
  local root
  root=$(_context_repo_identity) || return 1
  basename "$root"
}

_context_repo_identity() {
  local root
  root="$(lintel_repo_root 2>/dev/null)"
  (cd "${root:-.}" && pwd -P)
}

_context_repo_key() {
  local root
  root=$(_context_repo_identity) || return 1
  printf '%s' "$root" | git -C "$root" hash-object --stdin
}

# A shared legacy directory and a matching branch/slug do not establish ownership.
# New names carry a repository key; old files need an explicit canonical owner.
_context_legacy_owned() {
  local file="$1" key="$2" root="$3"
  case "$(basename "$file")" in ????????-??????-r"$key"-*) return 0 ;; esac
  grep -Fxq "**Repository:** $root" "$file" 2>/dev/null
}

# Canonical path for a NEW checkpoint. Caller writes content to it.
# Args: [label]
context_save_path() {
  local label="${1:-}"
  local branch dir ts slug key path
  branch="$(_context_branch)" || return 1
  _context_valid_branch "$branch" || return 1
  dir="$(lintel_sessions_dir 2>/dev/null)" || dir="$LINTEL_HOME/sessions"
  dir="$dir/$branch"
  ts=$(date +"%Y%m%d-%H%M%S")
  slug="$(_context_repo_slug)"
  key=$(_context_repo_key) || return 1
  # slugify the label: separators/spaces → '-', keep it filename-safe
  label=$(printf '%s' "$label" | tr ' /\\' '---' | tr -cd 'A-Za-z0-9._-')
  if [ -n "$label" ]; then
    path=$(_context_run reserve --directory "$dir" --name "$ts-r$key-$slug-$label-context-save.md") || return 1
  else
    path=$(_context_run reserve --directory "$dir" --name "$ts-r$key-$slug-context-save.md") || return 1
  fi
  # Python reports native paths; shell consumers need the Git Bash namespace.
  if command -v cygpath >/dev/null 2>&1; then path=$(cygpath -u "$path") || return 1; fi
  printf '%s\n' "$path"
}

# All checkpoints for a branch, newest first. Retains the legacy global dir
# read-only, but only with verified repository ownership.
# Args: [branch]  (default: current)
context_list() (
  set -o pipefail
  local branch="${1:-$(_context_branch)}"
  local newdir key root
  _context_valid_branch "$branch" || return 1
  root=$(_context_repo_identity) || return 1
  key=$(_context_repo_key) || return 1
  newdir="$(lintel_sessions_dir 2>/dev/null)" || newdir=""
  if [ -n "$newdir" ] && [ -d "$newdir/$branch" ]; then
    _context_run check-directory --directory "$newdir/$branch" || return 1
  fi
  if [ "$newdir" != "$LINTEL_HOME/sessions" ] && [ -d "$LINTEL_HOME/sessions/$branch" ]; then
    _context_run check-directory --directory "$LINTEL_HOME/sessions/$branch" || return 1
  fi
  {
    if [ -n "$newdir" ] && [ -d "$newdir/$branch" ]; then
      find "$newdir/$branch" -maxdepth 1 -type f -size +0c -name '*-context-save.md' || return 1
    fi
    # Legacy dir only when it is NOT what lintel_sessions_dir already resolved
    # to (un-migrated repos resolve THERE — listing it twice double-counts).
    if [ "$newdir" != "$LINTEL_HOME/sessions" ] && [ -d "$LINTEL_HOME/sessions/$branch" ]; then
      find "$LINTEL_HOME/sessions/$branch" -maxdepth 1 -type f -size +0c -name '*-context-save.md' || return 1   # legacy-fallback-ok
    fi
  } | while IFS= read -r f; do
    case "$f" in "$LINTEL_HOME/sessions/"*)
      _context_legacy_owned "$f" "$key" "$root" || continue ;;
    esac
    # prefix with basename for chronological sort (timestamps lead the name)
    printf '%s\t%s\n' "$(basename "$f")" "$f"
  done | sort -r | cut -f2 | awk '!seen[$0]++'
)

_context_fixed_scope() {
  local argument
  for argument in "$@"; do
    case "$argument" in --root|--root=*|--exclude-file|--exclude-file=*)
      echo 'Choose the repository via LINTEL_REPO_ROOT; selection arguments cannot replace its scope.' >&2
      return 1 ;;
    esac
  done
}

context_select() {
  local root state
  _context_fixed_scope "$@" || return 1
  root=$(_context_repo_identity) || return 1
  state=$(lintel_state_dir) || return 1
  _context_run select --root "$root" --exclude-file "$state/context-ignore.json" "$@"
}

context_cool() {
  local root state
  _context_fixed_scope "$@" || return 1
  root=$(_context_repo_identity) || return 1
  state=$(lintel_state_dir) || return 1
  _context_run cool --root "$root" --exclude-file "$state/context-ignore.json" "$@"
}

context_budget() { _context_run budget "$@"; }
context_perf() { _context_run perf "$@"; }

context_checkpoint() {
  local explicit=no path="${1:-}" candidates
  if [ "$path" = "--explicit" ]; then explicit=yes; path="${2:-}"; fi
  [ -n "$path" ] || { echo 'A checkpoint path is required.' >&2; return 1; }
  if [ "$explicit" = no ]; then
    candidates=$(context_list) || return 1
    printf '%s\n' "$candidates" | grep -Fxq -- "$path" || {
      echo 'Checkpoint is not owned by the current repository/branch; select a shared path explicitly.' >&2
      return 1
    }
  fi
  _context_run select --root "$(dirname "$path")" --path "$(basename "$path")" --max-files 1
}

# Newest checkpoint path for a branch (empty + rc 1 if none).
context_latest() {
  local p
  p=$(context_list "${1:-}") || return 1
  p="${p%%$'\n'*}"
  [ -n "$p" ] || return 1
  printf '%s\n' "$p"
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "_context.sh self-test:"
  echo "  branch:    $(_context_branch)"
  echo "  save path: $(context_save_path demo)"
  echo "  latest:    $(context_latest || echo '(none)')"
  echo "  count:     $(context_list | wc -l | tr -d ' ')"
fi
