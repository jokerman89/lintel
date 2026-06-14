#!/usr/bin/env bash
# component: lintel-state
# implements: ADR-0008
# intent: docs/audit/2026-06-12-fable5-fit-audit.md (behavior-over-prose track)
# constraints: one command per phase — if the ledger costs more than one line, it gets skipped
# last_intent_review: 2026-06-12
#
# lib/state.sh — the cycle state ledger, mechanical.
# The fit audit found ZERO 00-state.md files on the whole machine after weeks of
# real cycles: the per-phase write was a prose obligation, and prose obligations
# get skipped under momentum. This makes it one cheap command:
#
#   state_append <PHASE> <STATUS> [next=PHASE] [key=value ...]
#     → appends a block to .claude/runtime/state/00-state.md (paths.sh-resolved)
#   state_last [field]
#     → prints the last block (or just one field) — read by resume + the footer
#
# The block format matches what lib/cycle-footer.sh already parses (`phase:` lines
# mark blocks; `next_recommended:` feeds the footer's "next").

_STATE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
command -v lintel_state_dir >/dev/null 2>&1 || source "$_STATE_LIB_DIR/paths.sh"

state_file() {
  local d
  d="$(lintel_state_dir 2>/dev/null)" || return 1
  printf '%s/00-state.md' "$d"
}

# Append one phase entry. Args: <PHASE> <STATUS> [next=PHASE] [key=value ...]
state_append() {
  local phase="${1:?usage: state_append <PHASE> <STATUS> [next=X] [k=v ...]}"
  local status="${2:?usage: state_append <PHASE> <STATUS> [next=X] [k=v ...]}"
  shift 2
  # Strip CR/LF from phase/status too (H8 applied this to values only): a
  # newline in either would forge ledger lines the footer + resume parse.
  phase="${phase//$'\r'/ }"; phase="${phase//$'\n'/ }"
  status="${status//$'\r'/ }"; status="${status//$'\n'/ }"
  local f
  f="$(state_file)" || { echo "WARN [lintel/state]: no repo — state entry skipped" >&2; return 0; }
  mkdir -p "$(dirname "$f")" 2>/dev/null || true

  {
    printf -- '---\n'
    printf 'phase: %s\n' "$phase"
    printf 'ts: %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf 'status: %s\n' "$status"
    printf 'operator: %s\n' "${LINTEL_OPERATOR:-${USER:-${USERNAME:-unknown}}}"
    local kv k v
    for kv in "$@"; do
      case "$kv" in *=*) : ;; *)
        echo "WARN [lintel/state]: ignoring malformed arg '$kv' (expected key=value)" >&2
        continue ;;
      esac
      k="${kv%%=*}"; v="${kv#*=}"
      k="${k//$'\r'/}"; k="${k//$'\n'/}"
      [ "$k" = "next" ] && k="next_recommended"
      # Strip CR/LF from the value (battletest H8): a raw newline would inject
      # forged ledger lines / `---` block boundaries that state_last + the footer
      # parse, letting an influenced value mis-steer resume or hide a BLOCKED.
      v="${v//$'\r'/ }"; v="${v//$'\n'/ }"
      printf '%s: %s\n' "$k" "$v"
    done
  } >> "$f"
}

# Print the last block, or one field of it. Args: [field]
state_last() {
  local field="${1:-}"
  local f
  f="$(state_file)" || return 1
  [ -f "$f" ] || return 1
  local block
  block=$(awk '{sub(/\r$/,"")} /^---$/{b=""} {b=b $0 "\n"} END{printf "%s", b}' "$f")
  if [ -z "$field" ]; then
    printf '%s' "$block"
  else
    printf '%s' "$block" | grep -E "^${field}:" | head -1 | sed -E "s/^${field}:[[:space:]]*//"
  fi
}

# state_cycle_segment [file] — print the ledger from the LAST `phase: CYCLE`
# block onward: the current cycle's segment. Multi-cycle ledgers are the
# normal state of a working repo, and resolving position / mode / completeness
# across cycle boundaries poisons every consumer — a prior cycle's
# `cycle_complete: true` rendered the "no active cycle" footer for every later
# cycle (launch register B4). Whole file when no CYCLE block exists
# (single-cycle fixtures, fresh repos, hand-written state).
state_cycle_segment() {
  local f="${1:-$(state_file 2>/dev/null)}"
  [ -n "$f" ] && [ -f "$f" ] || return 0
  awk '
    { sub(/\r$/,""); line=$0; sub(/^[ \t]+/,"",line)
      if (index(line,"phase:")==1) { v=substr(line,7); gsub(/^[ \t]+|[ \t]+$/,"",v)
        if (toupper(v) ~ /^CYCLE/) start=NR }
      buf[NR]=$0 }
    END { if (!start) start=1; for (i=start;i<=NR;i++) print buf[i] }
  ' "$f"
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "lib/state.sh self-test:"
  echo "  state file: $(state_file 2>/dev/null || echo '(no repo)')"
  echo "  last phase: $(state_last phase 2>/dev/null || echo '(none)')"
fi
