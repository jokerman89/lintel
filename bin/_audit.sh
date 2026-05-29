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
# Writes to: ~/.lintel/audit/meta-infra-overrides.jsonl

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

mkdir -p "$LINTEL_AUDIT_DIR" 2>/dev/null || true

_audit_iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Escape a value for JSON
_audit_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g'
}

# Write an audit record
# Args: <category-file> <kind> [<key=value> ...]
audit_log() {
  local category_file="${1:-misc}"
  local kind="${2:-event}"
  shift 2 || true

  local out="$LINTEL_AUDIT_DIR/${category_file}.jsonl"
  local ts cycle_id operator
  ts=$(_audit_iso_now)
  cycle_id="${LINTEL_CYCLE_ID:-${CYCLE_ID:-unknown}}"
  operator="${LINTEL_OPERATOR:-$(whoami 2>/dev/null || echo unknown)}"

  # Build the JSON record manually (no jq dependency at audit-time)
  local rec
  rec=$(printf '{"ts":"%s","kind":"%s","operator":"%s","cycle_id":"%s"' \
    "$ts" "$(_audit_escape "$kind")" "$(_audit_escape "$operator")" "$(_audit_escape "$cycle_id")")

  for kv in "$@"; do
    local k="${kv%%=*}"
    local v="${kv#*=}"
    rec="${rec},\"${k}\":\"$(_audit_escape "$v")\""
  done

  rec="${rec}}"

  printf '%s\n' "$rec" >> "$out" 2>/dev/null || true
}

# Count records by kind across a category
audit_count() {
  local category_file="$1"
  local kind="${2:-}"
  local since_iso="${3:-}"
  local out="$LINTEL_AUDIT_DIR/${category_file}.jsonl"
  [ -f "$out" ] || { printf '0'; return 0; }

  if [ -z "$kind" ]; then
    wc -l < "$out" | tr -d ' '
    return 0
  fi

  if [ -z "$since_iso" ]; then
    grep -c "\"kind\":\"${kind}\"" "$out" 2>/dev/null || printf '0'
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
