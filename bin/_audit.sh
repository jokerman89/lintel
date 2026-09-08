#!/usr/bin/env bash
# bin/_audit.sh — Lintel unified audit writer (v4.0 Phase 1)
#
# Sourced helper that writes append-only JSONL audit records to category-
# specific logs in ~/.lintel/audit/. Used by:
# - meta-infra mode override events (category=meta-infra-mode-override)
# - orientator auto-mode override events (category=orientator-override)
# - pack-resolver internal events (category=pack-resolver)
# - Brief Forge override events (category=brief-forge-override)
# - Migration tracker events (category=migration)
#
# All audit logs are append-only JSONL — grep-portable, jq-queryable,
# replay-able, portable across machines.
#
# Usage:
#   source "$(dirname "$0")/_audit.sh"
#   audit_log meta-infra-overrides override 'detected_mode=meta-infra chosen_mode=internal-tool reason="quick refactor"'
#
# Scope routing (v5, ADR-0005): events about work IN a repo land in the repo's
# own audit dir (<repo>/.claude/runtime/audit/) once the repo carries the v5
# layout marker. Operator-level categories (pack lifecycle, resolver internals,
# harness migrations, usage tallies) always stay in ~/.lintel/audit/ — they are
# about the operator's install, not any one repo. Un-migrated repos keep the
# historical global path unchanged.

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

mkdir -p "$LINTEL_AUDIT_DIR" 2>/dev/null || true

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

# Resolve the output dir for a category: explicit env override > global list >
# migrated-repo runtime dir > ~/.lintel/audit.
_audit_out_dir() {
  local category="$1"
  if [ "$_AUDIT_DIR_EXPLICIT" = 1 ]; then
    printf '%s' "$LINTEL_AUDIT_DIR"; return
  fi
  case " $_AUDIT_GLOBAL_CATEGORIES " in
    *" $category "*) printf '%s' "$LINTEL_AUDIT_DIR"; return ;;
  esac
  case "$category" in
    usage-*) printf '%s' "$LINTEL_AUDIT_DIR"; return ;;
  esac
  if [ -n "$_AUDIT_REPO_AUDIT_DIR" ]; then
    mkdir -p "$_AUDIT_REPO_AUDIT_DIR" 2>/dev/null || true
    printf '%s' "$_AUDIT_REPO_AUDIT_DIR"
  else
    printf '%s' "$LINTEL_AUDIT_DIR"
  fi
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

  local out
  out="$(_audit_out_dir "$category_file")/${category_file}.jsonl"
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

  # Fail-open by design, but never SILENTLY: a dropped record on a full disk /
  # bad permission must leave at least a stderr trace (the audit trail's value
  # is that absence of a record means absence of an event).
  printf '%s\n' "$rec" >> "$out" 2>/dev/null || echo "WARN [lintel/audit]: failed to write $out" >&2
}

# Count records by kind across a category (reads the scope-routed file; falls
# back to the global file so pre-migration history stays countable)
audit_count() {
  local category_file="$1"
  local kind="${2:-}"
  local since_iso="${3:-}"
  local out
  out="$(_audit_out_dir "$category_file")/${category_file}.jsonl"
  [ -f "$out" ] || out="$LINTEL_AUDIT_DIR/${category_file}.jsonl"
  [ -f "$out" ] || { printf '0'; return 0; }

  if [ -z "$kind" ]; then
    wc -l < "$out" | tr -d ' '
    return 0
  fi

  if [ -z "$since_iso" ]; then
    # grep -c prints its own "0" on no-match (rc 1) — an `|| printf '0'`
    # fallback DOUBLED the output to "0\n0", breaking numeric consumers.
    grep -c "\"kind\":\"${kind}\"" "$out" 2>/dev/null || true
    return 0
  fi

  # Since-iso filter (string comparison works for ISO-8601)
  awk -v kind="$kind" -v since="$since_iso" '
    BEGIN { count=0 }
    /"kind":"/ {
      if (index($0, "\"kind\":\""kind"\"") > 0) {
        match($0, /"ts":"[^"]+"/)
        ts = substr($0, RSTART+6, RLENGTH-7)
        if (ts >= since) count++
      }
    }
    END { print count }
  ' "$out"
}

# Helper: timestamp N days ago in ISO-8601
audit_days_ago() {
  local n="${1:-30}"
  date -u -d "$n days ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
    date -u -v "-${n}d" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
    printf '1970-01-01T00:00:00Z'
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "_audit.sh self-test:"
  echo "  LINTEL_AUDIT_DIR = $LINTEL_AUDIT_DIR"
  audit_log "self-test" "smoke" "key1=value1" "key2=value with spaces"
  echo "  Wrote 1 record to $LINTEL_AUDIT_DIR/self-test.jsonl"
  echo "  Count for kind=smoke: $(audit_count self-test smoke)"
fi
