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

expect_route() {
  local expected_intent="$1" expected_workflow="$2" expected_confidence="$3" request="$4"
  local actual workflow confidence
  actual=$(classify_intent "$request")
  workflow=$(match_workflow "$actual" cycle)
  confidence=$(score_confidence "$actual" "$workflow")
  printf 'routing: %s -> intent=%s; workflow=%s; confidence=%s\n' \
    "$request" "$actual" "$workflow" "$confidence"
  checked=$((checked + 3))
  if [ "$actual" != "$expected_intent" ]; then
    printf 'FAIL: expected intent=%s for %s\n' "$expected_intent" "$request" >&2
    failed=$((failed + 1))
  fi
  if [ "$workflow" != "$expected_workflow" ]; then
    printf 'FAIL: expected workflow=%s for %s\n' "$expected_workflow" "$request" >&2
    failed=$((failed + 1))
  fi
  if [ "$confidence" != "$expected_confidence" ]; then
    printf 'FAIL: expected confidence=%s for %s\n' "$expected_confidence" "$request" >&2
    failed=$((failed + 1))
  fi
}

expect_route research '/li:cycle --mode research-dive' high 'Do not change the release plan; explain it.'
expect_route research '/li:cycle --mode research-dive' high 'Do not edit the deployment code; describe the release process.'
expect_route research '/li:cycle --mode research-dive' high 'Is it safe to deploy this release?'
expect_route unclear '/li:cycle' low 'Do not build the release.'
expect_route review '/li:review' high 'Review the release plan.'
expect_route deploy '/li:cycle --from SHIP' high 'Deploy the reviewed release.'

for request in \
  'Do not modify the build script; explain the release process.' \
  'Do not ship the deployment plan. Describe the build process.' \
  'Do not build the fix; is it safe to deploy the release?' \
  'Do not edit the release plan; can we deploy it safely?' \
  'No changes to the release plan; explain it.' \
  'Avoid editing the build; describe the release process.' \
  $'Don\xe2\x80\x99t change the release plan; explain it.' \
  'Are we ready to release the build?' \
  'Does the build need a release?' \
  'Can we deploy without changing the plan?' \
  'Would deploying the release change the plan?' \
  'Have we reviewed the release plan?' \
  'Do I need to release it?' \
  "Isn't deploying the release unsafe?" \
  'Please, is it safe to change the deployment plan?'; do
  expect_route research '/li:cycle --mode research-dive' high "$request"
done
for request in \
  'Never edit the plan or release the build.' \
  'Do not build the release or deploy the fix.' \
  'Without changing the build or release plan.' \
  'Do not edit build.release.plan.' \
  'Do not modify build.v2 or release.v3.' \
  'Do not edit anything but release notes.' \
  'Do not edit the plan. Release notes are historical.' \
  'Do not build; deploy the release.' \
  'Skip the build and release.' \
  'Could you deploy the reviewed release?' \
  'Will you change the release plan?' \
  'Deploy the reviewed release?'; do
  expect_route unclear '/li:cycle' low "$request"
done
for request in \
  "Don't write the release notes, but review the plan." \
  'Assess whether we should deploy the release.' \
  'Evaluate the release plan before deployment.'; do
  expect_route review '/li:review' high "$request"
done
expect_route deploy '/li:cycle --from SHIP' high 'Please deploy the reviewed release.'
expect_route build '/li:cycle' high 'Do build the reviewed release.'
expect_route review '/li:review' high 'Could you review the release plan?'
expect_route research '/li:cycle --mode research-dive' high 'Can you explain the deployment?'
expect_route unclear '/li:cycle' low 'Deploy the release then assess its readiness.'
original_ifs="$IFS"
IFS=:
expect_route research '/li:cycle --mode research-dive' high 'Do not change the release plan; explain it.'
expect_route research '/li:cycle --mode research-dive' high 'Is it safe to deploy this release?'
IFS="$original_ifs"

printf 'intent-operation-boundary: %s assertions, %s failures\n' "$checked" "$failed"
[ "$failed" -eq 0 ]
