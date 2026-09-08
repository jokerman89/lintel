#!/usr/bin/env bash
# tests/unit/hook-patterns.sh
# Safety net for the shared detection patterns (hooks/shared/_patterns.sh) that
# the secret + customer-data hooks compose. Written BEFORE the refactor so the
# extraction can't silently weaken detection. Locks two things the audit's
# "dedupe the regexes" must NOT break:
#   1. the deliberate BLOCK-vs-WARN tier split (block = high-confidence Tier-1;
#      warn = Tier-1 + heuristics that can false-positive)
#   2. the Swedish customer-PII tells (ärende, personnummer) stay detected
# tag: v4.9 hooks patterns
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATS="$REPO_ROOT/hooks/shared/_patterns.sh"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/hook-patterns.sh"
echo "============================"

[ -f "$PATS" ] || { fail "_patterns.sh MISSING"; exit 1; }
# shellcheck disable=SC1090
source "$PATS"

has(){ case ",$1," in *",$2,"*) return 0;; *) return 1;; esac; }

# ── secret tier1 (block-safe, high-confidence) ──
GH='ghp_012345678901234567890123456789012345'   # gh[opur]_ + 36
T1=$(scan_secrets tier1 "token=$GH AKIA0000000000000000 -----BEGIN PRIVATE KEY-----")
has "$T1" github-token   && pass "tier1 detects github-token"   || fail "tier1 github-token ($T1)"
has "$T1" aws-access-key && pass "tier1 detects aws-access-key" || fail "tier1 aws ($T1)"
has "$T1" private-key    && pass "tier1 detects private-key"    || fail "tier1 private-key ($T1)"
# tier1 must EXCLUDE the heuristics (so the BLOCK hook stays strict)
T1b=$(scan_secrets tier1 'password = "supersecret123"  SharedAccessKey=abc')
has "$T1b" hardcoded-password && fail "tier1 MUST NOT include hardcoded-password (block-aggression)" || pass "tier1 excludes hardcoded-password heuristic"
has "$T1b" azure-shared-key   && fail "tier1 MUST NOT include azure-shared-key heuristic"            || pass "tier1 excludes azure-shared-key heuristic"

# ── secret all (warn, broad) ──
ALL=$(scan_secrets all 'password = "supersecret123"  SharedAccessKey=abc  sk-ant-01234567890123456789012345678901')
has "$ALL" hardcoded-password && pass "all detects hardcoded-password heuristic" || fail "all hardcoded-password ($ALL)"
has "$ALL" azure-shared-key   && pass "all detects azure-shared-key heuristic"   || fail "all azure-shared-key ($ALL)"
has "$ALL" anthropic-key      && pass "all detects anthropic-key"                || fail "all anthropic-key ($ALL)"

# ── clean text → empty ──
[ -z "$(scan_secrets all 'just some normal code with no secrets here')" ] && pass "clean text → no secret hits" || fail "false positive on clean text"

# ── customer PII (incl. Swedish tells) ──
C=$(scan_customer 'contact jane@example.com or +46 70 123 4567, pnr 901101-1234')
has "$C" email        && pass "customer detects email"        || fail "customer email ($C)"
has "$C" phone        && pass "customer detects phone"        || fail "customer phone ($C)"
has "$C" personnummer && pass "customer detects personnummer" || fail "customer personnummer ($C)"
# name-with-case-id: strongest variant must catch BOTH Swedish 'ärende' and English 'case'
CS=$(scan_customer 'Jane Doe, ärende #4521')
has "$CS" name-with-case-id && pass "customer detects name + Swedish ärende id" || fail "swedish case-id ($CS)"
CE=$(scan_customer 'John Smith, case #99')
has "$CE" name-with-case-id && pass "customer detects name + English case id"  || fail "english case-id ($CE)"
[ -z "$(scan_customer 'ordinary text, nothing sensitive')" ] && pass "clean text → no customer hits" || fail "false positive on clean customer text"

# A no-match is successful, but a failed regex/grep must not publish even a
# partial list of matches as a completed scan.
scan_rc=0
scan_result=$(_scan_pats $'first\tmarker\nbroken\t[' 'marker' 2>/dev/null) || scan_rc=$?
if [ "$scan_rc" -eq 2 ] && [ -z "$scan_result" ]; then
  pass 'invalid pattern fails explicitly without partial matches'
else fail "invalid pattern looked successful (rc=$scan_rc, result=$scan_result)"; fi
scan_rc=0
scan_result=$(_scan_pats $'plain\tabsent' 'ordinary text') || scan_rc=$?
if [ "$scan_rc" -eq 0 ] && [ -z "$scan_result" ]; then
  pass 'genuine no-match preserves rc0 and empty output'
else fail "no-match contract changed (rc=$scan_rc)"; fi
printf -v large_text '%*s' 262144 ''
scan_rc=0
scan_result=$(_scan_pats $'plain\tmarker' "marker$large_text") || scan_rc=$?
if [ "$scan_rc" -eq 0 ] && [ "$scan_result" = plain ]; then
  pass 'large early match does not fail through a producer SIGPIPE'
else fail "large match failed (rc=$scan_rc)"; fi

echo ""
[ "$FAILED" -eq 0 ] && { echo "hook-patterns: ALL PASS"; exit 0; } || { echo "hook-patterns: FAILURES"; exit 1; }
