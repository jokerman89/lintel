#!/usr/bin/env bash
# component: lintel-context
# implements: ADR-0006
# intent: docs/concepts/memory-v2.md
# constraints: helpers own paths/naming/discovery; content stays LLM-written
# last_intent_review: 2026-09-08
#
# bin/_context.sh — mechanical core for the context-save/restore family.
# Closes the prose-only gap: 5 context skills shipped with zero bash. The
# LLM still writes/reads the checkpoint CONTENT; these helpers make the
# path handling, naming and discovery deterministic.
#
#   context_save_path [label]   → echoes the canonical new checkpoint path
#                                 (creates the directory; caller writes the file)
#   context_list [branch]       → all checkpoints newest-first (new + legacy dirs)
#   context_latest [branch]     → newest checkpoint path (empty if none)
#
# Scope: checkpoints live in <repo>/.claude/runtime/sessions/<branch>/ (v5,
# ADR-0005); the legacy ~/.lintel/sessions/<branch>/ is read-only fallback
# until the grace window closes (2026-09-12).

_CONTEXT_BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
command -v lintel_sessions_dir >/dev/null 2>&1 || source "$_CONTEXT_BIN_DIR/../lib/paths.sh"

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

_context_branch() {
  local root
  root=$(_context_repo_identity) || return 1
  git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'no-branch'
}

_context_repo_slug() {
  basename "$(lintel_repo_root 2>/dev/null || pwd)"
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
  local branch dir ts slug key
  branch="$(_context_branch)"
  dir="$(lintel_sessions_dir 2>/dev/null)" || dir="$LINTEL_HOME/sessions"
  dir="$dir/$branch"
  mkdir -p "$dir" 2>/dev/null || true
  ts=$(date +"%Y%m%d-%H%M%S")
  slug="$(_context_repo_slug)"
  key=$(_context_repo_key) || return 1
  # slugify the label: separators/spaces → '-', keep it filename-safe
  label=$(printf '%s' "$label" | tr ' /\\' '---' | tr -cd 'A-Za-z0-9._-')
  if [ -n "$label" ]; then
    printf '%s/%s-r%s-%s-%s-context-save.md' "$dir" "$ts" "$key" "$slug" "$label"
  else
    printf '%s/%s-r%s-%s-context-save.md' "$dir" "$ts" "$key" "$slug"
  fi
}

# All checkpoints for a branch, newest first. Includes the legacy global dir
# (read-only) during the grace window, but only with verified repository ownership.
# Args: [branch]  (default: current)
context_list() {
  local branch="${1:-$(_context_branch)}"
  local newdir key root
  root=$(_context_repo_identity) || return 1
  key=$(_context_repo_key) || return 1
  newdir="$(lintel_sessions_dir 2>/dev/null)" || newdir=""
  {
    [ -n "$newdir" ] && [ -d "$newdir/$branch" ] && \
      find "$newdir/$branch" -maxdepth 1 -name '*-context-save.md' 2>/dev/null
    # Legacy dir only when it is NOT what lintel_sessions_dir already resolved
    # to (un-migrated repos resolve THERE — listing it twice double-counts).
    if [ "$newdir" != "$LINTEL_HOME/sessions" ] && [ -d "$LINTEL_HOME/sessions/$branch" ]; then
      find "$LINTEL_HOME/sessions/$branch" -maxdepth 1 -name '*-context-save.md' 2>/dev/null   # legacy-fallback-ok
    fi
  } | while IFS= read -r f; do
    case "$f" in "$LINTEL_HOME/sessions/"*)
      _context_legacy_owned "$f" "$key" "$root" || continue ;;
    esac
    # prefix with basename for chronological sort (timestamps lead the name)
    printf '%s\t%s\n' "$(basename "$f")" "$f"
  done | sort -r | cut -f2 | awk '!seen[$0]++'
}

# Newest checkpoint path for a branch (empty + rc 1 if none).
context_latest() {
  local p
  p=$(context_list "${1:-}" | head -1)
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
