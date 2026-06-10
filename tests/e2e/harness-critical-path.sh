#!/usr/bin/env bash
# DESCRIPTION: e2e critical path — install.sh into a sandbox LINTEL_HOME, resolve a
#              _default pack field through the real parse path, render the cycle
#              footer from a fixture state. The first real e2e: closes the
#              "empty tests/e2e/ runs vacuously green" hole (punch-list #5 / P1-3).
# TAGS: claude-code-only,e2e
# Tags catalog: claude-code-only, codex-compatible, browser-required,
#               gstack-binaries-required, unit, integration, e2e, slow

set -euo pipefail

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
  IFS=',' read -ra FILTER_TAGS <<< "$LINTEL_TEST_FILTER_TAGS"
  match=0
  for ft in "${FILTER_TAGS[@]}"; do
    if echo "$TAGS_HEADER" | grep -q "$ft"; then match=1; break; fi
  done
  [ "$match" = "0" ] && skip "tag filter (need: $LINTEL_TEST_FILTER_TAGS, have: $TAGS_HEADER)"
fi

# --- SETUP ---

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SANDBOX_HOME="$TEST_TMP/lintel-home"

# --- RUN ---

# 1. install.sh into a sandbox LINTEL_HOME (same floor the install-linux CI job asserts)
install_rc=0
install_out=$(LINTEL_HOME="$SANDBOX_HOME" bash "$REPO_ROOT/install/install.sh" 2>&1 </dev/null) || install_rc=$?
assert_eq "0" "$install_rc" "install.sh exit code"
assert_dir_exists "$SANDBOX_HOME/scaffolding"
assert_dir_exists "$SANDBOX_HOME/hooks"

# 2. pack-resolver resolves _default fields through the REAL parse path.
#    voice.enforce is deliberately NOT in resolve_pack_field's hardcoded last-resort
#    fallback list — a correct value here proves pack.yaml was actually parsed.
resolver_probe() {
  LINTEL_HOME="$SANDBOX_HOME" \
  LINTEL_PACKS_DIR="$REPO_ROOT/packs" \
  LINTEL_ACTIVE_PACK_FILE="$TEST_TMP/active-pack" \
  LINTEL_SESSION_ID="e2e-$$" \
  bash -c 'source "'"$REPO_ROOT"'/lib/pack-resolver.sh" && resolve_pack_field "$1"' _ "$1" 2>/dev/null
}
printf '_default\n' > "$TEST_TMP/active-pack"
assert_eq "internal" "$(resolver_probe voice.default_tier)" "resolve voice.default_tier"
assert_eq "none" "$(resolver_probe voice.enforce)" "resolve voice.enforce (real parse, no fallback)"

# 3. cycle footer renders from a fixture append-log state (ADR-0003 contract)
printf 'phase: PLAN\nstatus: DONE\n\nphase: BUILD\nstatus: IN_PROGRESS\nnext_recommended: REVIEW\ncycle_mode: meta-infra\n' > "$TEST_TMP/00-state.md"
footer_out=$(bash -c 'source "'"$REPO_ROOT"'/lib/cycle-footer.sh" && render_cycle_footer --ascii --state "'"$TEST_TMP"'/00-state.md"' 2>&1 </dev/null)
assert_contains "$footer_out" "BUILD" "footer: you-are-here phase rendered"
assert_contains "$footer_out" "/li:review" "footer: next-command derived from state"

# --- EXIT ---
if [ "$FAILED" -gt 0 ]; then
  printf "${c_red}FAILED${c_reset} $TEST_NAME with $FAILED assertion failure(s)\n"
  exit 1
fi
exit 0
