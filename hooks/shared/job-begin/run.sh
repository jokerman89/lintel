#!/usr/bin/env bash
# job-begin — Lintel lifecycle hook (v3.8 Feature 1)
# Fires when a skill with workflow_root: true is invoked.
# Creates .claude/runtime/jobs/<id>/ + regenerates _active.md (scope resolved by bin/_jobs.sh;
# the cross-repo registry stays at ~/.lintel/jobs/_active.md).

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)" || \
BIN_DIR="${LINTEL_HOME}/scaffolding/bin"

# Arguments: skill_path mode (mode optional)
skill_path="${1:-}"
mode="${2:-${LINTEL_MODE:-internal-tool}}"
[ -z "$skill_path" ] && exit 0

# Operator override
[ -f "$HOME/.lintel/.jobs-disabled" ] && exit 0
[ -n "${NO_JOB:-}" ] && exit 0

# Verify workflow_root flag on the invoked skill
[ -f "$skill_path" ] || exit 0
if ! grep -qE "^workflow_root:[[:space:]]*true" "$skill_path"; then
  exit 0  # Not a workflow_root skill — no job
fi

# Extract workflow name from skill frontmatter
workflow=$(grep -E "^name:" "$skill_path" | head -1 | awk '{print $2}')
[ -z "$workflow" ] && exit 0

# Source helper and create job
helper="$BIN_DIR/_jobs.sh"
if [ ! -f "$helper" ]; then
  # Fallback search
  for candidate in \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../bin" 2>/dev/null && pwd)/_jobs.sh" \
    "$LINTEL_HOME/scaffolding/bin/_jobs.sh"; do
    [ -f "$candidate" ] && { helper="$candidate"; break; }
  done
fi
[ -f "$helper" ] || exit 0

# shellcheck disable=SC1090
source "$helper"
job_id_created=$(CALLED_BY="${CALLED_BY:-operator}" job_create "$workflow" "$mode")

# Surface
echo "[lintel] Job started: $job_id_created (workflow=$workflow, mode=$mode)"

exit 0
