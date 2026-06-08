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

# ── Claude Code: full + the only CLI with hooks ──
[ "$(cli_tier_field claude-code tier)" = "full" ] && pass "claude-code tier=full" || fail "claude-code tier=$(cli_tier_field claude-code tier)"
[ "$(cli_tier_field claude-code hooks_supported)" = "true" ] && pass "claude-code hooks_supported=true" || fail "claude-code hooks"
[ "$(cli_tier_field claude-code label)" = "Claude Code" ] && pass "claude-code label resolves" || fail "claude-code label"

# ── Codex: full tier but NO hooks (the load-bearing honesty flag) ──
[ "$(cli_tier_field codex tier)" = "full" ] && pass "codex tier=full" || fail "codex tier"
[ "$(cli_tier_field codex hooks_supported)" = "false" ] && pass "codex hooks_supported=false (Claude-only enforcement)" || fail "codex hooks"

# ── supported / best-effort tiers ──
[ "$(cli_tier_field gemini tier)" = "supported" ] && pass "gemini tier=supported" || fail "gemini tier"
[ "$(cli_tier_field other tier)" = "best-effort" ] && pass "other tier=best-effort" || fail "other tier"

# ── unknown CLI → safe defaults (degrade honestly, never over-claim) ──
[ "$(cli_tier_field frobnicator tier)" = "best-effort" ] && pass "unknown CLI tier→best-effort" || fail "unknown tier"
[ "$(cli_tier_field frobnicator hooks_supported)" = "false" ] && pass "unknown CLI hooks→false" || fail "unknown hooks"
[ "$(cli_tier_field frobnicator label)" = "frobnicator" ] && pass "unknown CLI label→name" || fail "unknown label"

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
