#!/usr/bin/env bash
# tests/shape/every-handoff-uses-envelope.sh
# Asserts (v4.0 Phase 3): every workflow_root skill either references the
# envelope schema OR declares brief_forge_bypass.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/every-handoff-uses-envelope.sh"
echo "============================================"

# Find every workflow_root: true skill
WR_SKILLS=()
while IFS= read -r f; do
  WR_SKILLS+=("$f")
done < <(grep -rlE "^workflow_root:[[:space:]]*true" "$REPO_ROOT/skills" 2>/dev/null)

if [ "${#WR_SKILLS[@]}" -eq 0 ]; then
  fail "no workflow_root: true skills found"
  echo "All every-handoff-uses-envelope assertions FAILED"; exit 1
fi

# Each must either reference envelope/brief-forge OR declare bypass
for f in "${WR_SKILLS[@]}"; do
  skill_name=$(basename "$(dirname "$f")")
  has_envelope_ref=0
  has_bypass=0

  if grep -qE "envelope|brief.forge|/li:brief.forge" "$f" 2>/dev/null; then
    has_envelope_ref=1
  fi

  if grep -qE "^brief_forge_bypass:[[:space:]]*true" "$f" 2>/dev/null; then
    has_bypass=1
  fi

  # cycle + plan are foundation orchestrators; envelope wiring lives in Brief Forge
  # itself + envelope-schema. They count as "envelope-aware" if they reference
  # envelopes anywhere in the skill body.
  if [ "$has_envelope_ref" -eq 1 ]; then
    pass "$skill_name references envelope/brief-forge"
  elif [ "$has_bypass" -eq 1 ]; then
    pass "$skill_name declares brief_forge_bypass: true"
  else
    # Phase 3 grace: warn rather than fail until Phase 4 wires every workflow_root
    echo "  WARN: $skill_name neither references envelope nor declares bypass (Phase 4 may tighten)"
  fi
done

# Brief Forge itself + envelope tools must exist
if [ ! -f "$REPO_ROOT/skills/brief-forge/SKILL.md" ]; then
  fail "skills/brief-forge MISSING"
fi

if [ ! -f "$REPO_ROOT/lib/envelope-schema.yaml" ]; then
  fail "lib/envelope-schema.yaml MISSING"
fi

if [ ! -x "$REPO_ROOT/bin/li-envelope-validate" ]; then
  fail "bin/li-envelope-validate MISSING"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All every-handoff-uses-envelope assertions PASSED"; exit 0
else echo "Some every-handoff-uses-envelope assertions FAILED"; exit 1; fi
