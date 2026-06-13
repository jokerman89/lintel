#!/usr/bin/env bash
# tests/shape/skill-descriptions-trigger.sh
# ADR-0014 / docs/concepts/prompt-house-style.md rule 1: a skill `description:` is
# the auto-invocation TRIGGER, not a workflow summary. It must state WHEN to use
# (a Use-trigger phrase) and must NOT carry version-archaeology (Phase N / Cohort /
# vN.N Feature / ADR-/L-NNN refs) that dilutes the trigger signal. This guard runs
# over the skills already migrated to trigger form (the high-traffic set); it does
# NOT yet require every skill — the full-surface sweep is incremental — but it FAILS
# if a migrated skill regresses, so the bar can only move forward.
# tag: shape craft description-trigger
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/skill-descriptions-trigger.sh"
echo "========================================="

# The skills migrated to trigger form (ADR-0014 wave). New skills should join this list.
MIGRATED="sense scope define discover plan build review ship capture cycle resume jobs status \
analyze brief-forge office-hours fix code-review qa investigate learn lessons-surface adr-new \
context-save context-restore context-warm plan-eng-review plan-ceo-review plan-and-build autoplan \
ta da sc dh tq full-engineering-pass scaffold welcome doctor pack-switch role generate"

# A trigger phrase: the description leads with / contains a Use-when form.
TRIGGER='^(description:[[:space:]]*)?(Use (when|after|to|for|at|before|during|on|whenever)|Run (when|after|to|before)|Trigger (when|after|on))'
# Archaeology that must not appear in a description.
ARCH='Phase [0-9]|Cohort [0-9]|v[0-9]+\.[0-9]+ Feature|\bADR-[0-9]|\bL-[0-9]{3}|adopted from|spec-kit|superpowers|gstack'

for s in $MIGRATED; do
  f="skills/$s/SKILL.md"
  [ -f "$f" ] || continue   # alias-only names (e.g. role-activate) have no own SKILL.md
  desc="$(grep -m1 '^description:' "$f" | sed 's/^description:[[:space:]]*//' | tr -d '\r')"
  if [ -z "$desc" ]; then fail "$s: no description"; continue; fi
  if printf '%s' "$desc" | grep -qiE "$TRIGGER" || printf 'description: %s' "$desc" | grep -qiE "$TRIGGER"; then
    : # has a trigger phrase
  else
    fail "$s: description is not in trigger form (no 'Use when/after/to…'): ${desc:0:60}…"
    continue
  fi
  if printf '%s' "$desc" | grep -qiE "$ARCH"; then
    fail "$s: description carries version-archaeology (move to body/ADR): ${desc:0:60}…"
  else
    pass "$s: trigger-form, no archaeology"
  fi
done

# No migrated skill's description may say 'founder' (operator, per ADR-0011/0013).
if grep -rl '^description:.*founder' skills --include='SKILL.md' >/dev/null 2>&1; then
  fail "a skill description still says 'founder' (use 'operator')"
  grep -rn '^description:.*founder' skills --include='SKILL.md' | sed 's/^/    /'
else
  pass "no 'founder' in any skill description"
fi

echo ""
[ "$FAILED" -eq 0 ] && { echo "skill-descriptions-trigger: ALL PASS"; exit 0; } || { echo "skill-descriptions-trigger: FAILURES"; exit 1; }
