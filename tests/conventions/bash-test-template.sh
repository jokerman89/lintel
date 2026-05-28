#!/usr/bin/env bash
# DESCRIPTION: <one-line what this test validates>
# TAGS: claude-code-only,unit
# Tags catalog: claude-code-only, codex-compatible, browser-required,
#               gstack-binaries-required, unit, integration, e2e, slow

set -euo pipefail

# --- Test harness helpers (inline; no external dep) ---

TEST_NAME="$(basename "${BASH_SOURCE[0]}" .sh)"
TEST_TMP="$(mktemp -d "/tmp/li:test-${TEST_NAME}-XXXXXX")"
FAILED=0

c_green='\033[32m'; c_red='\033[31m'; c_yellow='\033[33m'; c_reset='\033[0m'

pass() { printf "${c_green}PASS${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; }
fail() { printf "${c_red}FAIL${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; FAILED=$((FAILED+1)); }
skip() { printf "${c_yellow}SKIP${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; exit 0; }

assert_eq() {
  local expected="$1" actual="$2" label="${3:-eq}"
  if [ "$expected" = "$actual" ]; then
    pass "$label: $actual"
  else
    fail "$label: expected '$expected', got '$actual'"
  fi
}

assert_file_exists() {
  local f="$1"
  if [ -f "$f" ]; then pass "file exists: $f"; else fail "file missing: $f"; fi
}

assert_dir_exists() {
  local d="$1"
  if [ -d "$d" ]; then pass "dir exists: $d"; else fail "dir missing: $d"; fi
}

assert_contains() {
  local haystack="$1" needle="$2" label="${3:-contains}"
  if echo "$haystack" | grep -qF "$needle"; then
    pass "$label: '$needle' found"
  else
    fail "$label: '$needle' not found in input"
  fi
}

cleanup() {
  rm -rf "$TEST_TMP" 2>/dev/null || true
}
trap cleanup EXIT

# --- Tag enforcement ---

TAGS_HEADER=$(grep -m1 '^# TAGS:' "${BASH_SOURCE[0]}" 2>/dev/null | sed 's/^# TAGS: *//')

if [ -n "${LINTEL_TEST_FILTER_TAGS:-}" ]; then
  # If a tag-filter env var is set, skip if our tags don't match
  IFS=',' read -ra FILTER_TAGS <<< "$LINTEL_TEST_FILTER_TAGS"
  match=0
  for ft in "${FILTER_TAGS[@]}"; do
    if echo "$TAGS_HEADER" | grep -q "$ft"; then match=1; break; fi
  done
  [ "$match" = "0" ] && skip "tag filter (need: $LINTEL_TEST_FILTER_TAGS, have: $TAGS_HEADER)"
fi

# Skip if required deps not available
if echo "$TAGS_HEADER" | grep -q "browser-required" && [ ! -x "$HOME/.lintel/bin/chromium" ]; then
  skip "browser-required but managed Chromium not installed"
fi
if echo "$TAGS_HEADER" | grep -q "gstack-binaries-required" && [ ! -x "$HOME/.claude/skills/gstack/bin/gstack-config" ]; then
  skip "gstack-binaries-required but not installed"
fi

# --- SETUP (test-specific; replace placeholder below) ---

# Example:
#   cp tests/fixtures/sample.yaml "$TEST_TMP/sample.yaml"
#   export LINTEL_HOME="$TEST_TMP/lintel"
#   mkdir -p "$LINTEL_HOME"

# --- RUN (test-specific; replace placeholder below) ---

# Example assertions:
#   assert_eq "expected-value" "$some_var"
#   assert_file_exists "$TEST_TMP/output.txt"
#   output=$(some-command)
#   assert_contains "$output" "expected substring"

# Template default — replace with real test logic:
pass "template ran without errors (no real assertions defined)"

# --- TEARDOWN ---
# (cleanup trap handles it)

# --- EXIT ---
if [ "$FAILED" -gt 0 ]; then
  printf "${c_red}FAILED${c_reset} $TEST_NAME with $FAILED assertion failure(s)\n"
  exit 1
fi
exit 0
