#!/usr/bin/env bash
# component: lintel-auto-decide
# implements: ADR-0014 (issue I3 — gstack #603 sovereignty incident)
# intent: docs/audit/2026-06-13-cli-issues-craft-synthesis.md
# constraints: --auto must never silently decide a one-way door
# last_intent_review: 2026-06-13
#
# lib/auto-decide.sh — make the "never auto-decide a one-way door" guarantee
# MECHANICAL, not prose. gstack's sovereignty incident (#603): the AI auto-decided
# a scope-altering change because "is this a one-way door" was prose-assigned and
# mis-tagged. A keyword guard can't catch everything, but it catches the obvious
# irreversible classes so --auto can't run past them regardless of how the agent
# framed the decision.
#
#   is_one_way_door "<decision text>"  → rc 0 if the decision looks irreversible
#                                        (caller must ASK, never auto-decide)
# Conservative by design: a false positive just means "ask the operator" (safe);
# a false negative is the failure we're guarding, so the keyword set is broad.

_ONE_WAY_DOOR_TERMS='delete|drop |drop table|truncate|rm -rf|force.?push|force-with-lease|rewrite history|reset --hard|push to main|merge to main|production|prod (db|database|deploy|mutation)|deploy|migrat|schema change|rename (the |a )?(table|column|skill|agent|hook)|remove (the |a )?(skill|agent|pack|hook)|secret|credential|rotate key|breaking change|drop support|public api|irreversible|one-way|cannot be undone|delete the'

is_one_way_door() {
  local text="$1"
  printf '%s' "$text" | grep -qiE "$_ONE_WAY_DOOR_TERMS"
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "lib/auto-decide.sh self-test:"
  for t in "rename the variable foo" "drop the users table" "deploy to production" "tweak a log message" "force-push the branch"; do
    is_one_way_door "$t" && echo "  ONE-WAY (ask): $t" || echo "  reversible (auto-ok): $t"
  done
fi
