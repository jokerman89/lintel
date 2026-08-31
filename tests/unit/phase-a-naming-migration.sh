#!/usr/bin/env bash
# DESCRIPTION: Phase A naming migration sanity — all v2 skill names present (the bare-name form), v1 li-prefixed names absent from frontmatter
# TAGS: claude-code-only,codex-compatible,unit
#
# Updated 2026-05-28 for the bare-name form: skill folder names are bare (no `li-` prefix);
# the `li-` namespace lives in the plugin manifest, not in folder names. The
# canonical skills directory is `skills/`, not `scaffolding/` (scaffolding/
# now contains layered templates only).

set -euo pipefail

TEST_NAME="phase-a-naming-migration"
FAILED=0

c_green='\033[32m'; c_red='\033[31m'; c_yellow='\033[33m'; c_reset='\033[0m'
pass() { printf "${c_green}PASS${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; }
fail() { printf "${c_red}FAIL${c_reset} %s :: %s\n" "$TEST_NAME" "$1"; FAILED=$((FAILED+1)); }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

# All v2 skill names that should be present (renamed ones) — the bare-name form
# Updated 2026-05-29 for v3.6 Cohort 4 WS-4b renames:
#   setup-brain → gbrain-setup, sync-brain → gbrain-sync, agt-tier-stamp → agent-tier-stamp
# CAIP-specific skills (release-ev2, rais-*, onecs-check, agent-tier-stamp,
# cloudtest-eval-suite, onebranch-validate, scaffold-engagement-demo, etc.) were
# moved to lintel-caip-pack in the v4.7 extraction. Only generic survivors remain.
# 2026-06-10: context-budgetwatch removed — consolidated into context-budget --watch
# (deprecated alias in config/aliases.yaml until 2026-09-10); no longer canonical.
# 2026-06-12: gbrain-setup/gbrain-sync removed (ADR-0009 0-ref pruning) — no longer canonical.
V2_NAMES=(
  "open-managed-browser" "perfbench" "code-freeze" "code-unfreeze"
)

# v1 li-prefixed names that should NEVER appear as canonical `name:` value.
# In the bare-name form no skill uses `li-` prefix in its name (the prefix lives in the
# plugin namespace `/li:<skill>` instead). Keeping these to detect regression.
V1_NAMES_TO_BE_GONE=(
  "li-ship" "li-land-and-deploy" "li-open-gstack-browser"
  "li-benchmark" "li-canary" "li-freeze" "li-unfreeze"
  "li-setup-deploy" "li-setup-gbrain" "li-sync-gbrain"
  "li-customer-voice-check" "li-compliance-gate" "li-onerai-prep"
  "li-dsb-prep" "li-dpia-prep" "li-sensitive-use-report"
  "li-rai-impact-assessment" "li-scaffold-customer-demo" "li-transparency-doc-gen"
  "li-tier-stamp-agents" "li-entra-agent-id-prep" "li-context-tokenwatch"
  "li-eval-suite-gen" "li-test"
)

# Verify each v2 name appears as `name:` in some SKILL.md
for v2_name in "${V2_NAMES[@]}"; do
  if grep -r -l "^name: $v2_name$" "$SKILLS_DIR" >/dev/null 2>&1; then
    pass "v2 name present: $v2_name"
  else
    fail "v2 name MISSING: $v2_name"
  fi
done

# Verify li-prefixed v1 names never appear as canonical `name:` in the bare-name form
for v1_name in "${V1_NAMES_TO_BE_GONE[@]}"; do
  if grep -r -l "^name: $v1_name$" "$SKILLS_DIR" >/dev/null 2>&1; then
    fail "v1 li-prefixed name STILL canonical: $v1_name"
  else
    pass "v1 li-prefixed name no longer canonical: $v1_name"
  fi
done

# Verify v1 names appear in alias arrays (v1_alias OR deprecated_aliases — v3.6 Cohort 4 added the new field).
# Three v1_alias entries dropped in Cohort 4 (setup-brain/sync-brain/agt-tier-stamp renamed +
# their li- aliases migrated to deprecated_aliases array on the new-name skill).
V1_ALIAS_COUNT=$(grep -r "^v1_alias:" "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')
DEP_ALIAS_COUNT=$(grep -r "^deprecated_aliases:" "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=$((V1_ALIAS_COUNT + DEP_ALIAS_COUNT))
# Alias count dropped after the CAIP extraction (removed skills carried v1_alias entries).
if [ "$TOTAL" -ge 5 ]; then
  pass "alias entries present: $TOTAL (v1_alias=$V1_ALIAS_COUNT + deprecated_aliases=$DEP_ALIAS_COUNT; expected ≥5 post-extraction)"
else
  fail "alias entries low: $TOTAL (v1_alias=$V1_ALIAS_COUNT + deprecated_aliases=$DEP_ALIAS_COUNT; expected ≥5)"
fi

# Post v4.7 CAIP extraction: company-specific scaffolding (02-sdl, 03-ms-team) moved
# to lintel-caip-pack. Only 01-foundation remains; packs/_default is the neutral baseline.
[ ! -d "$REPO_ROOT/scaffolding/02-sdl" ] && pass "scaffolding/02-sdl/ removed (extracted to pack)" || fail "scaffolding/02-sdl/ still present"
[ ! -d "$REPO_ROOT/scaffolding/03-ms-team" ] && pass "scaffolding/03-ms-team/ removed (extracted to pack)" || fail "scaffolding/03-ms-team/ still present"
[ -f "$REPO_ROOT/packs/_default/pack.yaml" ] && pass "packs/_default/ neutral baseline present" || fail "packs/_default/ MISSING"

if [ "$FAILED" -gt 0 ]; then
  printf "${c_red}FAILED${c_reset} $TEST_NAME with $FAILED failure(s)\n"
  exit 1
fi
echo "ok: phase A naming migration verification complete"
exit 0
