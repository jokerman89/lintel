#!/usr/bin/env bash
# component: lintel-audit
# implements: ADR-0005, ADR-0008
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: audit_log stays advisory (warns, returns 0); mandatory writers verify their own read-back
# last_intent_review: 2026-09-23
#
# bin/_audit.sh — Lintel unified audit writer and its side-effect-free router.
#
# audit_log appends one JSON object per line to <category>.jsonl with the
# envelope ts, kind, operator, cycle_id followed by string key/value pairs.
# lib/event-catalog.json names every producer and its fields; bin/li-events.py
# is the structured reader. A missing record is only an unobserved event: some
# producers record only findings, blocks, overrides or failures, a write can
# fail (audit_log warns on stderr and returns 0), and some hooks discard that
# stderr.
#
# Usage:
#   source "$(dirname "$0")/_audit.sh"
#   audit_log meta-infra-overrides override detected_mode=meta-infra chosen_mode=internal-tool
#
# Scope routing (v5, ADR-0005): events about work IN a repo land in the repo's
# own audit dir (<repo>/.claude/runtime/audit/) once the repo carries the v5
# layout marker. Operator-level categories (pack lifecycle, resolver internals,
# harness migrations, usage tallies) always stay in ~/.lintel/audit/ — they are
# about the operator's install, not any one repo. Un-migrated repos keep the
# historical global path unchanged.
#
# Router (sourcing and resolving create nothing; audit_log creates its own
# directory immediately before a write):
#   audit_dir <category>         → the write directory
#   audit_file <category>        → the write file, with no fallback
#   audit_read_files <category>  → the write file, then the legacy global file
#                                  when it differs, one per line, unchecked
# Readers take the first existing file, name it, and report any later listed
# file that also exists rather than hiding pre-migration history.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
# Use the same native-to-shell root normalization as the state/memory writers.
command -v lintel_repo_root >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../lib/paths.sh"
# An EXPLICIT caller-set LINTEL_AUDIT_DIR is a hard override for ALL categories
# (the documented test seam — mirrors _jobs.sh's LINTEL_JOBS_DIR behavior).
# "Explicit" = set to something OTHER than the computed default; several sibling
# helpers pre-default the var with the same `:-$LINTEL_HOME/audit` idiom and
# must not count as an override.
_AUDIT_DIR_EXPLICIT=0
if [ -n "${LINTEL_AUDIT_DIR:-}" ] && [ "$LINTEL_AUDIT_DIR" != "$LINTEL_HOME/audit" ]; then
  _AUDIT_DIR_EXPLICIT=1
fi
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# Categories that are operator-global by nature (everything else is repo work).
_AUDIT_GLOBAL_CATEGORIES="pack-lifecycle pack-resolver migration migrations self-test"

# Repo root + layout, computed once per source (audit fires on hot paths —
# avoid a git fork per write). Note: a long-lived shell that cd's into a
# DIFFERENT repo keeps the first repo's routing; acceptable for hook processes
# (one process per event), set LINTEL_REPO_ROOT explicitly for anything else.
_AUDIT_REPO_AUDIT_DIR=""
_audit_init_repo_scope() {
  local root
  root="$(lintel_repo_root)"
  [ -n "$root" ] || return 0
  if [ -f "$root/.claude/lintel-layout.yaml" ]; then
    local v
    v=$(grep -E '^layout_version:' "$root/.claude/lintel-layout.yaml" 2>/dev/null \
        | head -1 | awk '{print $2}' | tr -d '\r')
    if [ "${v:-0}" -ge 5 ] 2>/dev/null; then
      _AUDIT_REPO_AUDIT_DIR="$root/.claude/runtime/audit"
    fi
  fi
}
_audit_init_repo_scope

# The only routing implementation: explicit env override > operator-global
# categories > migrated-repo runtime dir > ~/.lintel/audit. It assigns the
# out-variable _AUDIT_RESOLVED (no fork on the hot write path) and creates nothing.
_AUDIT_RESOLVED=""
_audit_resolve() {
  _AUDIT_RESOLVED="$LINTEL_AUDIT_DIR"
  [ "$_AUDIT_DIR_EXPLICIT" = 1 ] && return 0
  case " $_AUDIT_GLOBAL_CATEGORIES " in *" $1 "*) return 0 ;; esac
  case "$1" in usage-*) return 0 ;; esac
  [ -z "$_AUDIT_REPO_AUDIT_DIR" ] || _AUDIT_RESOLVED="$_AUDIT_REPO_AUDIT_DIR"
  return 0
}

_audit_category_ok() {
  case "${1:-}" in
    ''|.*|*/*|*\\*|*[[:space:]]*)
      printf 'ERROR [lintel/audit]: invalid audit category: %s\n' "${1:-<empty>}" >&2
      return 2 ;;
  esac
}

_AUDIT_READ_FILES=()
_audit_read_list() {
  _audit_resolve "$1"
  _AUDIT_READ_FILES=("$_AUDIT_RESOLVED/$1.jsonl")
  [ "$LINTEL_AUDIT_DIR/$1.jsonl" = "${_AUDIT_READ_FILES[0]}" ] ||
    _AUDIT_READ_FILES+=("$LINTEL_AUDIT_DIR/$1.jsonl")
}

audit_dir() {
  _audit_category_ok "${1:-}" || return 2
  _audit_resolve "$1"
  printf '%s\n' "$_AUDIT_RESOLVED"
}

audit_file() {
  _audit_category_ok "${1:-}" || return 2
  _audit_resolve "$1"
  printf '%s/%s.jsonl\n' "$_AUDIT_RESOLVED" "$1"
}

audit_read_files() {
  _audit_category_ok "${1:-}" || return 2
  _audit_read_list "$1"
  printf '%s\n' "${_AUDIT_READ_FILES[@]}"
}

# Retained for bin/li-review-log and the other historical callers; like the
# public router it is now side-effect free.
_audit_out_dir() {
  _audit_resolve "${1:-misc}"
  printf '%s' "$_AUDIT_RESOLVED"
}

_audit_iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Cycle correlation: env wins (zero fork); else derive once per source from
# the repo ledger's last `cycle_id:` line. Nothing ever exported LINTEL_CYCLE_ID
# (each tool call is a fresh process), so 100% of records said "unknown" while
# the ledger had the answer all along (launch register B4).
_AUDIT_CYCLE_ID=""
_audit_init_cycle_id() {
  _AUDIT_CYCLE_ID="${LINTEL_CYCLE_ID:-${CYCLE_ID:-}}"
  [ -n "$_AUDIT_CYCLE_ID" ] && return 0
  local root f
  root="$(lintel_repo_root)"
  [ -n "$root" ] || { _AUDIT_CYCLE_ID="unknown"; return 0; }
  f="$root/.claude/runtime/state/00-state.md"
  [ -f "$f" ] || f="$root/.lintel/state/00-state.md"
  if [ -f "$f" ]; then
    _AUDIT_CYCLE_ID="$(awk '
      { sub(/\r$/,""); line=$0; sub(/^[ \t]+/,"",line)
        if (index(line,"cycle_id:")==1) { v=substr(line,10); gsub(/^[ \t]+|[ \t]+$/,"",v); last=v } }
      END { print last }' "$f" 2>/dev/null)"
  fi
  [ -n "$_AUDIT_CYCLE_ID" ] || _AUDIT_CYCLE_ID="unknown"
}
_audit_init_cycle_id

# Escape a value for JSON, assigning the result to the variable _AUDIT_ESC.
# Pure-bash parameter expansion with an out-variable — no subprocess fork at
# all (neither a sed pipe nor a $(...) command-substitution subshell). Hooks
# fire on every Edit/Bash event, so a fork per key=value pair is ~10-50x
# costlier than this on some platforms (notably Windows/MSYS).
# Order matters: backslashes first, then quotes, then control chars. Newlines
# and CR MUST be escaped (battletest H8): an attacker-influenced value with a
# raw newline otherwise splits one record into two physical lines, breaking the
# one-JSON-object-per-line invariant every reader (wc -l, grep -c, jq) relies on
# and hiding/forging records.
_AUDIT_ESC=""
_audit_escape() {
  local s="$1"
  s="${s//\\/\\\\}"   # \   -> \\
  s="${s//\"/\\\"}"   # "   -> \"
  s="${s//$'\t'/\\t}" # tab -> \t
  s="${s//$'\r'/\\r}" # CR  -> \r
  s="${s//$'\n'/\\n}" # LF  -> \n
  _AUDIT_ESC="$s"
}

# Write an audit record
# Args: <category-file> <kind> [<key=value> ...]
audit_log() {
  local category_file="${1:-misc}"
  local kind="${2:-event}"
  shift 2 || true

  _audit_resolve "$category_file"
  local dir="$_AUDIT_RESOLVED"
  local out="$dir/${category_file}.jsonl"
  local ts cycle_id operator
  ts=$(_audit_iso_now)
  cycle_id="${LINTEL_CYCLE_ID:-${CYCLE_ID:-$_AUDIT_CYCLE_ID}}"
  # Prefer env-provided identity (zero fork). Fall back to whoami only if no
  # env var is set — hooks fire on hot paths and a whoami fork per write is
  # expensive on some platforms.
  operator="${LINTEL_OPERATOR:-${USER:-${LOGNAME:-${USERNAME:-}}}}"
  [ -n "$operator" ] || operator="$(whoami 2>/dev/null || echo unknown)"

  # Build the JSON record manually (no jq dependency at audit-time).
  # printf -v + the _audit_escape out-variable assign in-place — no
  # command-substitution subshell forks. The only remaining fork is the single
  # date(1) call for the timestamp above, which is unavoidable.
  local rec esc_kind esc_op esc_cyc
  _audit_escape "$kind"; esc_kind="$_AUDIT_ESC"
  _audit_escape "$operator"; esc_op="$_AUDIT_ESC"
  _audit_escape "$cycle_id"; esc_cyc="$_AUDIT_ESC"
  printf -v rec '{"ts":"%s","kind":"%s","operator":"%s","cycle_id":"%s"' \
    "$ts" "$esc_kind" "$esc_op" "$esc_cyc"

  for kv in "$@"; do
    local k="${kv%%=*}"
    local v="${kv#*=}"
    _audit_escape "$v"
    rec="${rec},\"${k}\":\"${_AUDIT_ESC}\""
  done

  rec="${rec}}"

  # Advisory by design: a dropped record (full disk, a path that is not a
  # directory, a bad permission) leaves a stderr warning and returns 0, so a
  # missing record never proves that nothing happened.
  [ -d "$dir" ] || mkdir -p "$dir" 2>/dev/null || true
  printf '%s\n' "$rec" >> "$out" 2>/dev/null || echo "WARN [lintel/audit]: failed to write $out" >&2
  return 0
}

# Approximate bash line counter over one category log, kept for quick shell
# checks. It greps text rather than parsing JSON; bin/li-events.py is the
# structured reader for classification and malformed-record diagnostics.
# Args: <category> [kind] [since-iso]
# Reads the first existing audit_read_files entry and names any later listed
# file that also exists. No listed file: empty stdout, `unobserved:` with the
# listed paths on stderr, return 3. An existing log prints its count, return 0.
audit_count() {
  local category_file="${1:-}" kind="${2:-}" since_iso="${3:-}" log="" f
  _audit_category_ok "$category_file" || return 2
  _audit_read_list "$category_file"
  for f in "${_AUDIT_READ_FILES[@]}"; do
    if [ -z "$log" ]; then
      [ -f "$f" ] && log="$f"
    elif [ -e "$f" ]; then
      printf 'audit_count: read %s; also present but not read: %s\n' "$log" "$f" >&2
    fi
  done
  if [ -z "$log" ]; then
    printf 'unobserved: no audit log at %s\n' "${_AUDIT_READ_FILES[*]}" >&2
    return 3
  fi

  if [ -z "$since_iso" ]; then
    if [ -z "$kind" ]; then
      wc -l < "$log" | tr -d ' '
    else
      # grep -c prints its own "0" on no-match (rc 1) — an `|| printf '0'`
      # fallback DOUBLED the output to "0\n0", breaking numeric consumers.
      grep -c "\"kind\":\"${kind}\"" "$log" 2>/dev/null || true
    fi
    return 0
  fi

  # Since filter: ISO-8601 string comparison. Records without a ts cannot be
  # placed in the window; they are excluded and reported, never silently dropped.
  awk -v kind="$kind" -v since="$since_iso" '
    BEGIN { count = 0; undated = 0 }
    kind == "" || index($0, "\"kind\":\"" kind "\"") > 0 {
      if (match($0, /"ts":"[^"]+"/)) {
        ts = substr($0, RSTART + 6, RLENGTH - 7)
        if (ts >= since) count++
      } else undated++
    }
    END {
      print count
      if (undated) printf "audit_count: %d record(s) without ts excluded by the since filter\n", undated > "/dev/stderr"
    }
  ' "$log"
}

# Helper: timestamp N days ago in ISO-8601. When the date cannot be computed it
# says so and returns 1 rather than silently widening the window to all history.
audit_days_ago() {
  local n="${1:-30}"
  case "$n" in ''|*[!0-9]*) echo "audit_days_ago: day count must be a nonnegative integer" >&2; return 2 ;; esac
  date -u -d "$n days ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
    date -u -v "-${n}d" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || {
      echo "audit_days_ago: cannot compute a date $n days ago; no since filter was applied" >&2
      return 1
    }
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "_audit.sh self-test:"
  echo "  LINTEL_AUDIT_DIR = $LINTEL_AUDIT_DIR"
  audit_log "self-test" "smoke" "key1=value1" "key2=value with spaces"
  echo "  Wrote 1 record to $(audit_file self-test)"
  echo "  Count for kind=smoke: $(audit_count self-test smoke)"
fi
