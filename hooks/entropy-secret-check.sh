#!/usr/bin/env bash
# hooks/entropy-secret-check.sh
#
# v3.6 cohort 5 item 6.5: high-entropy-string check complement till befintliga
# secret-check hooks (som matchar known prefixes sk-, ghp_, AKIA, etc).
#
# Hook firing: on staged content (pre-commit).
# Exit codes: 0 = clean, 1 = high-entropy match found (warn, doesn't block).
# Override: LINTEL_OVERRIDE_ENTROPY=1 to bypass (audit-logged).

set -uo pipefail

mkdir -p "${HOME}/.lintel/audit"

# Unified audit writer (hooks/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../bin/_audit.sh"

# Override-handling
if [ "${LINTEL_OVERRIDE_ENTROPY:-0}" = "1" ]; then
  audit_log "hooks" "entropy_secret_check" "hook=entropy-secret-check" "override=true" "reason=${LINTEL_OVERRIDE_REASON:-not-specified}"
  exit 0
fi

# Get staged content
if git rev-parse --git-dir >/dev/null 2>&1; then
  staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
else
  staged_files=""
fi

[ -z "$staged_files" ] && exit 0

# High-entropy detection
check_entropy() {
  local file="$1"
  file "$file" 2>/dev/null | grep -qE 'binary|image|video|audio' && return 0

  local hits=0

  # Pattern 1: assignment with long alphanumeric value
  if grep -nE '(password|token|secret|api[_-]?key|auth)[[:space:]]*[=:][[:space:]]*["'\''`]?[A-Za-z0-9+/=_-]{32,}' "$file" 2>/dev/null | grep -v '^[[:space:]]*#' >/dev/null; then
    hits=$((hits+1))
    echo "WARN: $file — assignment-like high-entropy string (suspected secret)"
  fi

  return "$hits"
}

# Iterate staged files
total_hits=0
for f in $staged_files; do
  [ -f "$f" ] || continue
  if ! check_entropy "$f"; then
    file_hits=$?
    total_hits=$((total_hits + file_hits))
  fi
done

# Log hook execution
audit_log "hooks" "entropy_secret_check" "hook=entropy-secret-check" "hits=$total_hits"

if [ "$total_hits" -gt 0 ]; then
  echo ""
  echo "⚠ Entropy-secret-check found $total_hits high-entropy strings."
  echo "  Review above. If false positives:"
  echo "    LINTEL_OVERRIDE_ENTROPY=1 LINTEL_OVERRIDE_REASON=\"<reason>\" <command>"
  exit 1
fi

exit 0
