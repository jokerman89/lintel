#!/usr/bin/env bash
# component: lintel-state
# implements: ADR-0008, ADR-0022, ADR-0028
# intent: .claude/engineering/audits/2026-06-12-fable5-fit-audit.md (behavior-over-prose track)
# constraints: one command per phase — if the ledger costs more than one line, it gets skipped
# last_intent_review: 2026-09-20
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
command -v cycle_phase_known >/dev/null 2>&1 || source "$_STATE_LIB_DIR/cycle-modes.sh"

state_file() {
  local d
  d="${LINTEL_STATE_DIR:-}"
  if [ -z "$d" ]; then d="$(lintel_state_dir)" || return 1
  else
    case "$d" in
      /*|[A-Za-z]:*) : ;;
      *) d="$(lintel_repo_root)/$d" ;;
    esac
  fi
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
  local f kv k v block explicit_cycle=no cycle_id operator
  for kv in "$@"; do
    k="${kv%%=*}"
    if [[ "$kv" != *=* || ! "$k" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] ||
        [[ "$k" = phase || "$k" = ts || "$k" = status || "$k" = operator ||
           "$k" = entry_format || "$k" = entry_complete ]]; then
      printf 'ERROR [lintel/state]: invalid or reserved field: %s\n' "$k" >&2
      return 2
    fi
    [ "$k" != cycle_id ] || explicit_cycle=yes
  done
  f="$(state_file)" || { echo "ERROR [lintel/state]: no repository for state entry" >&2; return 1; }
  cycle_id="${LINTEL_CYCLE_ID:-}"
  cycle_id="${cycle_id//$'\r'/ }"; cycle_id="${cycle_id//$'\n'/ }"
  if [ "$explicit_cycle" = no ] && [ -z "$cycle_id" ] && [ -f "$f" ]; then
    cycle_id=$(state_cycle_field cycle_id "$f") || return 1
  fi
  mkdir -p "$(dirname "$f")" || return 1
  operator="${LINTEL_OPERATOR:-${USER:-${USERNAME:-unknown}}}"
  operator="${operator//$'\r'/ }"; operator="${operator//$'\n'/ }"

  block=$(
    printf -- '---\n'
    printf 'phase: %s\n' "$phase"
    printf 'entry_format: 1\n'
    printf 'ts: %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf 'status: %s\n' "$status"
    printf 'operator: %s\n' "$operator"
    if [ "$explicit_cycle" = no ] && [ -n "$cycle_id" ]; then
      printf 'cycle_id: %s\n' "$cycle_id"
    fi
    for kv in "$@"; do
      k="${kv%%=*}"; v="${kv#*=}"
      [ "$k" = "next" ] && k="next_recommended"
      # Strip CR/LF from the value (battletest H8): a raw newline would inject
      # forged ledger lines / `---` block boundaries that state_last + the footer
      # parse, letting an influenced value mis-steer resume or hide a BLOCKED.
      v="${v//$'\r'/ }"; v="${v//$'\n'/ }"
      printf '%s: %s\n' "$k" "$v"
    done
    printf 'entry_complete: true\n'
  ) || return 1
  printf '%s\n' "$block" >> "$f" || {
    echo "ERROR [lintel/state]: could not persist $f; phase remains unverified" >&2
    return 1
  }
}

# Literal key lookup shared by phase, cycle, footer and resume readers.
state_field() {
  awk -v key="${1:?field required}:" -v all="${2:-}" '
    { sub(/\r$/, ""); line=$0; sub(/^[ \t]+/, "", line)
      if (index(line,key)==1) {
        value=substr(line,length(key)+1); sub(/^[ \t]+/, "", value)
        if (key=="cycle_id:") sub(/[ \t]+$/, "", value)
        if (all=="all") print value
        last=value
      }
    }
    END { if (all!="all") print last }
  '
}

# Print the last block, or one field of it. Args: [field]
state_last() {
  local field="${1:-}"
  local f
  f="$(state_file)" || return 1
  [ -f "$f" ] || return 1
  local block
  block=$(state_cycle_segment "$f" --all | _state_phase_scan record --all) || return $?
  if [ -z "$field" ]; then
    printf '%s' "$block"
  else
    printf '%s\n' "$block" | state_field "$field"
  fi
}

# state_cycle_segment [file] [cycle_id] — select a cycle's original start and
# correlated entries, including a later resume after another initiative. CYCLE
# DONE is not a new segment. Legacy untagged entries inherit their start marker.
# Multi-cycle ledgers are the
# normal state of a working repo, and resolving position / mode / completeness
# across cycle boundaries poisons every consumer — a prior cycle's
# `cycle_complete: true` rendered the "no active cycle" footer for every later
# cycle (launch register B4). Whole file when no CYCLE block exists
# (single-cycle fixtures, fresh repos, hand-written state).
state_cycle_segment() {
  local f="${1:-$(state_file 2>/dev/null)}"
  local wanted="${2:-${LINTEL_CYCLE_ID:-}}"
  [ -n "$f" ] && [ -f "$f" ] || { [ -z "$wanted" ]; return; }
  awk -v wanted="$wanted" '
    function flush() {
      if (block=="") return
      if (format=="1" && complete!="true") {
        status="INCOMPLETE"
        block=block "status: INCOMPLETE\ncycle_complete: false\nstate_diagnostic: incomplete entry\n"
      }
      if (phase=="CYCLE" && (status=="STARTING" || status=="")) {
        generation++
        inherited=id!="" ? id : "@legacy-"generation
        if (id!="") started[id]=1
      }
      tag=id!="" ? id : inherited
      if (tag=="") tag="@legacy-0"
      count++; blocks[count]=block; tags[count]=tag; current=tag
    }
    { sub(/\r$/,""); line=$0; sub(/^[ \t]+/,"",line)
      if (index(line,"phase:")==1) {
        flush(); block=""; phase=substr(line,7); gsub(/^[ \t]+|[ \t]+$/,"",phase)
        phase=toupper(phase); status=""; id=""; format=""; complete=""
      } else if (index(line,"status:")==1) {
        status=substr(line,8); gsub(/^[ \t]+|[ \t]+$/,"",status); status=toupper(status)
      } else if (index(line,"cycle_id:")==1) {
        id=substr(line,10); gsub(/^[ \t]+|[ \t]+$/,"",id)
      } else if (index(line,"entry_format:")==1) {
        format=substr(line,14); gsub(/^[ \t]+|[ \t]+$/,"",format)
      } else if (index(line,"entry_complete:")==1) {
        complete=substr(line,16); gsub(/^[ \t]+|[ \t]+$/,"",complete)
      }
      block=block $0 "\n"
    }
    END {
      flush()
      if (wanted!="" && wanted!="--all" && !started[wanted]) exit 1
      selected=wanted!="" ? wanted : current
      for (i=1;i<=count;i++) if (wanted=="--all" || tags[i]==selected) printf "%s", blocks[i]
    }
  ' "$f"
}

state_cycle_field() {
  local segment
  segment=$(state_cycle_segment "${2:-$(state_file)}" "${3:-}") || return $?
  printf '%s\n' "$segment" | state_field "$1"
}

_state_phase_scan() {
  awk -v mode="$1" -v want="${2:-}" -v known="$(cycle_phases | tr '\n' ' ')" '
    function save() {
      if (phase!="" && (want=="--all" || index(" "known" ", " "phase" "))) {
        statuses[phase]=status
        if (want=="" || want=="--all" || toupper(want)==phase) last=block
      }
    }
    /^[ \t]*phase:/ {
      save(); block=""; status=""; phase=$0; sub(/^[ \t]*phase:[ \t]*/, "", phase)
      sub(/[ \t\r]+$/, "", phase); phase=toupper(phase)
    }
    /^[ \t]*status:/ {
      status=$0; sub(/^[ \t]*status:[ \t]*/, "", status); sub(/[ \t\r]+$/, "", status)
      status=toupper(status)
    }
    { block=block $0 "\n" }
    END {
      save()
      if (mode=="record") printf "%s", last
      else {
        count=split(known,names," ")
        for (i=1;i<=count;i++)
          if (statuses[names[i]]=="DONE" || statuses[names[i]]=="DONE_WITH_CONCERNS")
            printf "%s ", names[i]
      }
    }
  '
}

state_phase_record() {
  local segment
  segment=$(state_cycle_segment "${2:-$(state_file)}" "${3:-}") || return $?
  printf '%s\n' "$segment" | _state_phase_scan record "${1:-}"
}

state_completed_phases() { _state_phase_scan completed; }

state_resume_phase() {
  local f="${1:-$(state_file)}" id="${2:-}" record phase status next selected following="" seen=no p
  [ "$(state_cycle_field cycle_complete "$f" "$id")" != true ] || return 0
  record=$(state_phase_record "" "$f" "$id") || return $?
  phase=$(printf '%s\n' "$record" | state_field phase)
  status=$(printf '%s\n' "$record" | state_field status)
  next=$(printf '%s\n' "$record" | state_field next_recommended)
  if [ -z "$phase" ]; then
    next=$(state_cycle_field first_phase "$f" "$id") || return $?
    printf '%s\n' "${next:-SENSE}"
  else
    case "$status" in
      DONE|DONE_WITH_CONCERNS)
        selected=$(state_cycle_field phases_selected "$f" "$id") || return $?
        local IFS=' '
        for p in $selected; do
          if [ "$seen" = yes ]; then following="$p"; break; fi
          [ "$p" != "$phase" ] || seen=yes
        done
        printf '%s\n' "${following:-${next:-$phase}}" ;;
      *) printf '%s\n' "$phase" ;;
    esac
  fi
}

state_cycle_begin() {
  local id="${1:?cycle ID required}" mode="${2:?cycle mode required}" f current old kv key entries="" identifiers
  shift 2
  [[ "$id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || {
    echo "ERROR [lintel/state]: cycle ID must be an explicit stable token" >&2; return 2;
  }
  for kv in "$@"; do
    case "${kv%%=*}" in
      cycle_id|cycle_mode)
        echo "ERROR [lintel/state]: metadata cannot replace the cycle identity" >&2
        return 2 ;;
    esac
  done
  f=$(state_file) || return 1
  if [ -e "$f" ]; then
    [ -f "$f" ] || { echo "ERROR [lintel/state]: ledger is not a regular file" >&2; return 1; }
    entries=$(state_cycle_segment "$f" --all) || {
      echo "ERROR [lintel/state]: cannot inspect prior ledger; refusing a new start" >&2
      return 1
    }
  fi
  current=$(printf '%s\n' "$entries" | state_field cycle_id) || return 1
  if [ "$current" = "$id" ]; then
    if [ "$(state_cycle_field cycle_mode "$f" "$id")" != "$mode" ] ||
        [ "$(state_cycle_field cycle_complete "$f" "$id")" = true ]; then
      echo "ERROR [lintel/state]: existing cycle differs or is complete; reconcile before reuse" >&2
      return 2
    fi
    for kv in "$@"; do
      key="${kv%%=*}"; old=$(state_cycle_field "$key" "$f" "$id") || return 1
      [ "$old" = "${kv#*=}" ] || {
        echo "ERROR [lintel/state]: cycle metadata changed: $key" >&2; return 2;
      }
    done
    export LINTEL_CYCLE_ID="$id"
    return 0
  fi
  identifiers=$(printf '%s\n' "$entries" | state_field cycle_id all) || return 1
  if [[ $'\n'"$identifiers"$'\n' == *$'\n'"$id"$'\n'* ]]; then
    echo "ERROR [lintel/state]: historical cycle ID already exists; resume it explicitly" >&2
    return 2
  fi
  state_append CYCLE STARTING "cycle_id=$id" "cycle_mode=$mode" "$@" || return $?
  export LINTEL_CYCLE_ID="$id"
}

# Select, never execute, a range over the existing canonical mode/phase source.
state_cycle_phases() {
  local mode="${1:-full}" first="${2:-SENSE}" last="${3:-CAPTURE}" skip="${4:-}" token
  first=$(printf '%s' "$first" | tr '[:lower:]' '[:upper:]')
  last=$(printf '%s' "$last" | tr '[:lower:]' '[:upper:]')
  skip=$(printf '%s' "$skip" | tr ',[:lower:]' ' [:upper:]')
  for token in "$first" "$last"; do
    cycle_phase_known "$token" || { echo "ERROR [lintel/state]: unknown phase $token" >&2; return 2; }
  done
  local IFS=' '
  for token in $skip; do
    cycle_phase_known "$token" || { echo "ERROR [lintel/state]: unknown skip phase $token" >&2; return 2; }
  done
  cycle_phases | awk -v first="$first" -v last="$last" -v skip="$(cycle_mode_skips "$mode") $skip" '
    { names[NR]=$0; if ($0==first) start=NR; if ($0==last) stop=NR }
    END {
      if (!start || !stop || stop<start) {
        print "ERROR [lintel/state]: invalid phase range" > "/dev/stderr"; exit 2
      }
      for (i=start;i<=stop;i++) if (!index(" "skip" ", " "names[i]" ")) selected[++count]=names[i]
      if (!count) { print "ERROR [lintel/state]: empty phase selection" > "/dev/stderr"; exit 2 }
      for (i=1;i<=count;i++) print selected[i]
    }
  '
}

# Returns 3 for already-completed work and 2 for an interrupted/blocked attempt.
# Only an explicit --retry re-enters a phase; this helper never invokes a skill.
state_phase_begin() {
  local retry=no phase record status previous
  if [ "${1:-}" = --retry ]; then retry=yes; shift; fi
  phase="${1:?phase required}"; shift
  cycle_phase_known "$phase" || { echo "ERROR [lintel/state]: unknown phase $phase" >&2; return 2; }
  [ -n "$(state_cycle_field cycle_id)" ] || {
    echo "ERROR [lintel/state]: begin the cycle before a phase" >&2; return 2;
  }
  [ "$(state_cycle_field cycle_complete)" != true ] || {
    echo "ERROR [lintel/state]: cycle is complete" >&2; return 2;
  }
  record=$(state_phase_record "$phase") || return 1
  status=$(printf '%s\n' "$record" | state_field status)
  if [ "$retry" = no ]; then
    case "$status" in
      DONE|DONE_WITH_CONCERNS) return 3 ;;
      "") : ;;
      *) echo "ERROR [lintel/state]: $phase is $status; reconcile before --retry" >&2; return 2 ;;
    esac
    previous=$(state_phase_record | state_field status) || return 1
    case "$previous" in
      ""|DONE|DONE_WITH_CONCERNS) : ;;
      *) echo "ERROR [lintel/state]: prior phase is $previous; cannot advance to $phase" >&2; return 2 ;;
    esac
  fi
  state_append "$phase" STARTING "$@"
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "lib/state.sh self-test:"
  echo "  state file: $(state_file 2>/dev/null || echo '(no repo)')"
  echo "  last phase: $(state_last phase 2>/dev/null || echo '(none)')"
fi
