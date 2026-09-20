#!/usr/bin/env bash
# tests/unit/cli-tiers.sh
# Locks lib/cli-tiers.sh — the per-CLI capability tier lookup that /li:welcome uses
# for its honest first-run message and that li-wiki-gen uses to generate the README
# table. The tier logic is the thing most likely to be wrong, so it gets a real test
# (plan-eng-review decision: a testable shell lib, not untestable markdown).
# tag: onboarding cli-tiers
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$REPO_ROOT/lib/cli-tiers.sh"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/cli-tiers.sh"
echo "======================="

# The legacy tier describes delivered files, not complete host certification.
[ "$(cli_tier_field claude-code tier)" = "supported" ] && pass "claude-code has a delivered route, not blanket full support" || fail "claude-code tier"
[ "$(cli_tier_field claude-code hooks_supported)" = "true" ] && pass "claude-code hooks_supported=true" || fail "claude-code hooks"
[ "$(cli_tier_field claude-code label)" = "Claude Code CLI" ] && pass "claude-code surface label resolves" || fail "claude-code label"

# Codex aliases only CLI; it does not imply app or IDE parity.
[ "$(cli_tier_field codex tier)" = "supported" ] && pass "codex tier=supported" || fail "codex tier"
[ "$(cli_tier_field codex hooks_supported)" = "false" ] && pass "codex hooks_supported=false (Claude-only enforcement)" || fail "codex hooks"

# ── supported / best-effort tiers ──
[ "$(cli_tier_field gemini tier)" = "supported" ] && pass "gemini tier=supported" || fail "gemini tier"
[ "$(cli_tier_field gemini skills_native)" = "true" ] && pass "Gemini native-format route is delivered" || fail "gemini discovery"
[ "$(cli_tier_field other tier)" = "best-effort" ] && pass "other tier=best-effort" || fail "other tier"

# ── unknown CLI → safe defaults (degrade honestly, never over-claim) ──
[ "$(cli_tier_field frobnicator tier)" = "best-effort" ] && pass "unknown CLI tier→best-effort" || fail "unknown tier"
[ "$(cli_tier_field frobnicator hooks_supported)" = "false" ] && pass "unknown CLI hooks→false" || fail "unknown hooks"
[ "$(cli_tier_field frobnicator label)" = "frobnicator" ] && pass "unknown CLI label→name" || fail "unknown label"
[ "$(cli_tier_normalize frobnicator)" = "other" ] && pass "unknown legacy ID maps to manual other" || fail "unknown normalization"
[ "$(cli_tier_normalize copilot-app)" = "copilot-app" ] && pass "desktop surface remains distinct" || fail "collapsed desktop"
[ "$(cli_tier_normalize copilot-cloud)" = "copilot-cloud" ] && pass "cloud surface remains distinct" || fail "collapsed cloud"
[ "$(cli_tier_field copilot-cli subagents)" = "sequenced" ] && pass "static compatibility hint cannot authorize concurrency" || fail "unsafe subagent tier"

# ── exactly one CLI supports hooks (the enforcement layer is Claude-Code-only) ──
hooks_clis=0
for c in $(cli_tier_list); do
  [ "$(cli_tier_field "$c" hooks_supported)" = "true" ] && hooks_clis=$((hooks_clis + 1))
done
[ "$hooks_clis" = "1" ] && pass "exactly 1 CLI supports hooks (claude-code)" || fail "hooks-supporting CLIs=$hooks_clis (expected 1)"

# ── the list enumerates the manifest CLIs ──
n=$(cli_tier_list | wc -l | tr -d ' ')
[ "$n" -ge 7 ] && pass "cli_tier_list enumerates ≥7 CLIs ($n)" || fail "cli_tier_list n=$n"

echo ""
[ "$FAILED" -eq 0 ] && { echo "cli-tiers: ALL PASS"; exit 0; } || { echo "cli-tiers: FAILURES"; exit 1; }
