#!/usr/bin/env bash
# DESCRIPTION: Phase A naming migration sanity — all v2 skill names present, all v1 names absent from frontmatter
# TAGS: claude-code-only,codex-compatible,unit

set -euo pipefail

TEST_NAME="phase-a-naming-migration"
FAILED=0

c_green='\033[32m'; c_red='\033[31m'; c_yellow='\033[33m'; c_reset='\033[0m'
pass() { printf "${c_green}PASS${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; }
fail() { printf "${c_red}FAIL${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; FAILED=$((FAILED+1)); }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/scaffolding"

# All v2 skill names that should be present (renamed ones)
V2_NAMES=(
  "jstack-release-ev2" "jstack-release-deploy-ev2" "jstack-open-managed-browser"
  "jstack-perfbench" "jstack-safe-deploy-ring" "jstack-code-freeze" "jstack-code-unfreeze"
  "jstack-setup-ev2-targets" "jstack-setup-brain" "jstack-sync-brain"
  "jstack-rais-customer-voice-check" "jstack-onecs-check" "jstack-onerai-submit-draft"
  "jstack-dsb-submit-draft" "jstack-dpia-submit-draft" "jstack-rais-sensitive-use"
  "jstack-rais-impact-assessment" "jstack-scaffold-engagement-demo" "jstack-rais-transparency-note"
  "jstack-agt-tier-stamp" "jstack-entra-agent-id-submit-draft" "jstack-context-budgetwatch"
  "jstack-cloudtest-eval-suite" "jstack-onebranch-validate"
)

# V1 names that should NO LONGER appear as `name:` value
V1_NAMES_TO_BE_GONE=(
  "jstack-ship" "jstack-land-and-deploy" "jstack-open-gstack-browser"
  "jstack-benchmark" "jstack-canary" "jstack-freeze" "jstack-unfreeze"
  "jstack-setup-deploy" "jstack-setup-gbrain" "jstack-sync-gbrain"
  "jstack-customer-voice-check" "jstack-compliance-gate" "jstack-onerai-prep"
  "jstack-dsb-prep" "jstack-dpia-prep" "jstack-sensitive-use-report"
  "jstack-rai-impact-assessment" "jstack-scaffold-customer-demo" "jstack-transparency-doc-gen"
  "jstack-tier-stamp-agents" "jstack-entra-agent-id-prep" "jstack-context-tokenwatch"
  "jstack-eval-suite-gen" "jstack-test"
)

# Verify each v2 name appears as `name:` in some SKILL.md
for v2_name in "${V2_NAMES[@]}"; do
  if grep -r -l "^name: $v2_name$" "$SKILLS_DIR" >/dev/null 2>&1; then
    pass "v2 name present: $v2_name"
  else
    fail "v2 name MISSING: $v2_name"
  fi
done

# Verify v1 names no longer appear as canonical `name:` (but they may appear in v1_alias arrays)
for v1_name in "${V1_NAMES_TO_BE_GONE[@]}"; do
  if grep -r -l "^name: $v1_name$" "$SKILLS_DIR" >/dev/null 2>&1; then
    fail "v1 name STILL canonical: $v1_name"
  else
    pass "v1 name no longer canonical: $v1_name"
  fi
done

# Verify v1 names appear in v1_alias: arrays (where applicable)
ALIAS_COUNT=$(grep -r "^v1_alias:" "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')
if [ "$ALIAS_COUNT" -ge 24 ]; then
  pass "v1_alias entries present: $ALIAS_COUNT (expected ≥24)"
else
  fail "v1_alias entries low: $ALIAS_COUNT (expected ≥24)"
fi

# Verify directory rename
[ -d "$REPO_ROOT/scaffolding/02-sdl" ] && pass "scaffolding/02-sdl/ exists" || fail "scaffolding/02-sdl/ MISSING"
[ ! -d "$REPO_ROOT/scaffolding/02-compliance" ] && pass "scaffolding/02-compliance/ removed" || fail "scaffolding/02-compliance/ still exists"

# Verify voice doc renames
for voice_doc in OurVoice-corpus.md OurVoice-test.md OurVoice-calibration.md OurVoice.md OurVoice-examples.md; do
  [ -f "$REPO_ROOT/scaffolding/03-personal-advanced/voice/$voice_doc" ] && pass "voice doc renamed: $voice_doc" || fail "voice doc MISSING: $voice_doc"
done

if [ "$FAILED" -gt 0 ]; then
  printf "${c_red}FAILED${c_reset} $TEST_NAME with $FAILED failure(s)\n"
  exit 1
fi
echo "ok: phase A naming migration verification complete"
exit 0
