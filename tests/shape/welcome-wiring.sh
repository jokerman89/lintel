#!/usr/bin/env bash
# tests/shape/welcome-wiring.sh
# Locks /li:welcome as a thin orchestrator: it must delegate
# to the existing pieces (/li:cli-fingerprint, the cli-tiers single source,
# /li:cycle --dry-run) rather than rebuild detection or hardcode the tier table, must
# run the demo in dry-run (no first-run mutation), and must state the hooks-Claude-only
# honesty + the no-auto-settings-edit safety.
# tag: onboarding welcome
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/welcome-wiring.sh"
echo "============================="

W="skills/welcome/SKILL.md"
[ -f "$W" ] || { fail "skills/welcome/SKILL.md missing"; exit 1; }

grep -qE '^name: welcome$' "$W"        && pass "frontmatter name: welcome"        || fail "frontmatter name"
grep -qE '^layer: foundation$' "$W"    && pass "layer: foundation"                || fail "layer"
grep -qE '^cli_support:' "$W"          && pass "declares cli_support"             || fail "cli_support"
grep -qE '^gap_if_skipped:' "$W"       && pass "declares gap_if_skipped"          || fail "gap_if_skipped"

grep -q '/li:cli-fingerprint' "$W"     && pass "delegates to /li:cli-fingerprint (no rebuilt detection)" || fail "must reference /li:cli-fingerprint"
grep -q 'cli-tiers' "$W"               && pass "reads the cli-tiers single source"                       || fail "must reference cli-tiers"
grep -q 'cli_tier_field' "$W"          && pass "uses the cli_tier_field lookup (no hardcoded tier)"      || fail "must use cli_tier_field"
grep -q '/li:cycle --dry-run' "$W"     && pass "demo via /li:cycle --dry-run (no first-run mutation)"    || fail "must use /li:cycle --dry-run"

for consumer in "$W" ".github/skills/li-welcome/SKILL.md"; do
  [ -f "$consumer" ] || { fail "$consumer missing"; continue; }
  grep -qF 'catalog/references/intent.md' "$consumer" \
    && pass "$consumer delegates to catalog intent" || fail "$consumer: catalog intent link missing"
  if grep -qF 'skill-router' "$consumer"; then
    fail "$consumer names retired skill-router in current guidance"
  else
    pass "$consumer uses current discovery ownership"
  fi
done

grep -qiE 'only on claude code|claude-code-only|fires only on claude|claude code mechanism' "$W" \
  && pass "states hooks are Claude-Code-only (honest degradation)" || fail "must state the hooks-Claude-only honesty"

grep -qiE 'never edits your settings|do not auto-edit|never auto-edit|print the exact' "$W" \
  && pass "documents print-the-snippet (no auto settings.json edit)" || fail "must not auto-edit settings.json"

echo ""
[ "$FAILED" -eq 0 ] && { echo "welcome-wiring: ALL PASS"; exit 0; } || { echo "welcome-wiring: FAILURES"; exit 1; }
