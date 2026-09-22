#!/usr/bin/env bash
# component: intent-operation-boundary
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: recommendations only; fixtures never execute a selected workflow
# last_intent_review: 2026-09-20
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/lib/orientator-routing.sh"
failed=0
checked=0

expect_intent() {
  local expected="$1" request="$2" actual
  actual=$(classify_intent "$request")
  checked=$((checked + 1))
  if [ "$actual" != "$expected" ]; then
    printf 'FAIL: %s -> %s (expected %s)\n' "$request" "$actual" "$expected" >&2
    failed=$((failed + 1))
  fi
}

expect_intent review 'review the fix without changing code'
expect_intent research 'research deployment options only'
expect_intent review 'review the release plan'
expect_intent review 'Please audit the broken deployment'
expect_intent research 'Help me understand the release error'
expect_intent research 'Explain how to fix the crash'
expect_intent research 'How does deployment work?'
expect_intent research 'What is the release process?'
expect_intent research 'Where is the deployment configuration?'
expect_intent review $'Please\nreview the fix\nwithout changing code'
expect_intent review 'Do not deploy; review the plan'
expect_intent review "Don't fix it; review the failure"
expect_intent unclear 'Never deploy'
expect_intent unclear 'Do not fix'
expect_intent fix 'fix review comments'
expect_intent build 'build a code review service'
expect_intent build 'add deployment documentation'
expect_intent deploy 'deploy the reviewed release'
expect_intent ship 'release v2'
expect_intent resume 'continue the release review'
expect_intent scaffold 'create a new project'
expect_intent scaffold 'new repo'
expect_intent fix 'the button is broken'
expect_intent fix 'the build is broken'
expect_intent fix 'the build error needs investigation'
expect_intent unclear 'What should I do?'
expect_intent unclear ''
expect_intent unclear '   '

original_ifs="$IFS"
IFS=:
expect_intent review 'review the broken release'
expect_intent research 'research deployment options only'
expect_intent build 'build a code review service'
IFS="$original_ifs"

for request in 'review the release plan' 'research deployment options only'; do
  workflow=$(match_workflow "$(classify_intent "$request")" delivery)
  case "$workflow" in
    /li:review|'/li:cycle --mode research-dive') ;;
    *) printf 'FAIL: read request escalated to %s\n' "$workflow" >&2; failed=$((failed + 1)) ;;
  esac
  checked=$((checked + 1))
done

printf 'intent-operation-boundary: %s assertions, %s failures\n' "$checked" "$failed"
[ "$failed" -eq 0 ]
