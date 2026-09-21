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

expect_intent review 'inspect the release plan'
expect_intent research 'compare deployment options'
expect_intent research 'summarize the fix plan'
expect_intent research 'show me how to deploy'
expect_intent research 'tell me about the broken build'
expect_intent unclear 'review the change then deploy it'
expect_intent unclear 'fix the bug then release v2'
expect_intent build 'implement audit and review logging'
expect_intent review 'review the fix and deployment documentation'
expect_intent research 'explain how to build then deploy'
expect_intent unclear 'Do not build or deploy'
expect_intent unclear 'Never fix or release'
expect_intent review 'Do not build or deploy; review the plan'
expect_intent plan 'plan the release'
expect_intent plan 'design a fix for the deployment failure'
expect_intent review 'analyze the fix before changing code'
expect_intent research 'describe how to fix the crash'
expect_intent research 'should we build or release this?'
expect_intent research 'what changes are needed to build the service?'

original_ifs="$IFS"
IFS=:
expect_intent review 'review the broken release'
expect_intent research 'research deployment options only'
expect_intent build 'build a code review service'
risk=$(assess_risk '/li:cycle' '[cycle, plan, ship]')
[ "$risk" = high ] || { printf 'FAIL: caller IFS lowered declared workflow risk\n' >&2; failed=$((failed + 1)); }
checked=$((checked + 1))
IFS="$original_ifs"

for request in 'review the release plan' 'research deployment options only' 'plan the release'; do
  workflow=$(match_workflow "$(classify_intent "$request")" delivery)
  case "$workflow" in
    /li:review|/li:plan|'/li:cycle --mode research-dive') ;;
    *) printf 'FAIL: read request escalated to %s\n' "$workflow" >&2; failed=$((failed + 1)) ;;
  esac
  checked=$((checked + 1))
done

printf 'intent-operation-boundary: %s assertions, %s failures\n' "$checked" "$failed"
[ "$failed" -eq 0 ]
