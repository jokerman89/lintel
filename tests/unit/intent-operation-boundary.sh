#!/usr/bin/env bash
# component: intent-operation-boundary
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: recommendations only; fixtures never execute a selected workflow
# last_intent_review: 2026-09-22
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

printf 'retained intent-operation-boundary: %s assertions, %s failures\n' "$checked" "$failed"

expect_safe_route() {
  local request="$1" actual workflow confidence
  actual=$(classify_intent "$request")
  workflow=$(match_workflow "$actual" cycle)
  confidence=$(score_confidence "$actual" "$workflow")
  checked=$((checked + 1))
  printf 'safe routing: %s -> %s / %s / %s\n' "$request" "$actual" "$workflow" "$confidence"
  case "$actual|$workflow|$confidence" in
    'research|/li:cycle --mode research-dive|high'|'review|/li:review|high'|'unclear|/li:cycle|low') ;;
    *) printf 'FAIL: topic or assessment supplied action authority: %s\n' "$request" >&2
       failed=$((failed + 1)) ;;
  esac
}

# The independent matrix retains its original safe-result alternatives.
expect_route research '/li:cycle --mode research-dive' high 'Do not change the release plan; explain it.'
expect_route research '/li:cycle --mode research-dive' high 'Do not edit the deployment code; describe the release process.'
expect_route research '/li:cycle --mode research-dive' high 'Is it safe to deploy this release?'
expect_route unclear '/li:cycle' low 'Do not build the release.'
expect_route review '/li:review' high 'Review the release plan.'
expect_route deploy '/li:cycle --from SHIP' high 'Deploy the reviewed release.'
expect_safe_route 'The release must not be deployed; explain the plan.'
expect_safe_route 'Release notes: explain the deployment process.'
expect_safe_route 'I want to know whether it is safe to deploy this release.'
expect_safe_route 'I need advice on whether to deploy this release.'
expect_safe_route 'Do not change the release plan, but explain the deployment process.'
expect_safe_route "Don't change the build or release notes; review the plan."
expect_safe_route 'Is the plan ready for release, or does it need review?'
expect_safe_route 'Could you deploy the reviewed release?'
expect_route unclear '/li:cycle' low 'Review the change then deploy it.'
expect_route build '/li:cycle' high 'Implement release-note validation.'
expect_route fix '/li:cycle --mode hotfix' high 'Fix review comments.'
expect_route ship '/li:cycle --from SHIP' high 'Release v2.'
expect_route deploy '/li:cycle --from SHIP' high 'Please deploy the reviewed release.'
original_ifs="$IFS"
IFS=:
expect_safe_route 'Do not change the release plan; explain it.'
expect_route deploy '/li:cycle --from SHIP' high 'Deploy the reviewed release.'
ifs_probe=$(classify_intent 'Deploy the reviewed release.'; printf '|%s' "$IFS")
[ "$ifs_probe" = 'deploy|:' ] || {
  printf 'FAIL: direct classifier invocation changed caller IFS\n' >&2
  failed=$((failed + 1))
}
checked=$((checked + 1))
IFS="$original_ifs"

for operation in build deploy release; do
  case "$operation" in
    build) direct_intent=build; direct_workflow='/li:cycle' ;;
    deploy) direct_intent=deploy; direct_workflow='/li:cycle --from SHIP' ;;
    release) direct_intent=ship; direct_workflow='/li:cycle --from SHIP' ;;
  esac
  for subject in 'release plan' 'build script' 'review checklist'; do
    expect_route "$direct_intent" "$direct_workflow" high "$operation the $subject."
    expect_route "$direct_intent" "$direct_workflow" high "Please $operation the $subject."
    expect_route "$direct_intent" "$direct_workflow" high "I need you to $operation the $subject."
    expect_route research '/li:cycle --mode research-dive' high \
      "I want to know whether to $operation the $subject."
    expect_route research '/li:cycle --mode research-dive' high \
      "I need advice on whether to $operation the $subject."
    expect_route research '/li:cycle --mode research-dive' high \
      "$subject: explain how to $operation it."
    expect_route research '/li:cycle --mode research-dive' high \
      "The $subject must not be changed; explain how to $operation it."
    expect_route review '/li:review' high "Do not $operation the $subject; review it."
    expect_route research '/li:cycle --mode research-dive' high \
      "Explain the example \"$operation the $subject\"."
    expect_route unclear '/li:cycle' low "\"$operation the $subject\""
  done
done
expect_route review '/li:review' high $'# Release the build\nReview the deployment plan.'
expect_route research '/li:cycle --mode research-dive' high 'I would like to understand how to release the build.'
expect_route build '/li:cycle' high 'I want to build a review service.'
expect_route build '/li:cycle' high 'Help me build a review service.'
expect_route build '/li:cycle' high 'Implement audit and review logging.'
expect_route unclear '/li:cycle' low 'Build the service and deploy it.'
expect_route unclear '/li:cycle' low 'Build the service; deploy it.'
expect_route unclear '/li:cycle' low 'Build the service; edit its configuration.'
expect_route unclear '/li:cycle' low 'Build the service; build its documentation.'
expect_route unclear '/li:cycle' low 'Release plan: deploy it.'
expect_route unclear '/li:cycle' low 'Do not change the release: deploy it.'
expect_route research '/li:cycle --mode research-dive' high 'Explain this command: deploy the release.'
expect_route research '/li:cycle --mode research-dive' high 'Is this command safe: deploy the release?'
expect_route research '/li:cycle --mode research-dive' high 'I need advice: build the service or release it.'
expect_route unclear '/li:cycle' low 'Release notes are ready.'
expect_route unclear '/li:cycle' low 'Release notes'
expect_route unclear '/li:cycle' low 'Deploy the release if the checks pass.'
expect_route unclear '/li:cycle' low 'Please deploy the release, but do not deploy it.'
expect_route unclear '/li:cycle' low '`release v2` is an example, not a request.'
expect_route review '/li:review' high 'Review `release v2` without executing it.'
expect_route review '/li:review' high 'Granska den trasiga releasen.'
expect_route deploy '/li:cycle --from SHIP' high 'Driftsätt till produktion.'
expect_route build '/li:cycle' high 'Bygg en ny funktion.'
expect_route scaffold 'bin/li-scaffold init' high 'Nytt projekt.'
expect_route resume '/li:resume' high 'Fortsätt med granskningen.'

printf 'intent-operation-boundary: %s assertions, %s failures\n' "$checked" "$failed"

# The independent review's 33 inputs and expectations, including literal LF.
matrix_start="$checked"
matrix_failures="$failed"
expect_route research '/li:cycle --mode research-dive' high 'Do not change the release plan; explain it.'
expect_route research '/li:cycle --mode research-dive' high 'Do not edit the deployment code; describe the release process.'
expect_route research '/li:cycle --mode research-dive' high 'Is it safe to deploy this release?'
expect_route unclear '/li:cycle' low 'Do not build the release.'
expect_route review '/li:review' high 'Review the release plan.'
expect_route deploy '/li:cycle --from SHIP' high 'Deploy the reviewed release.'
expect_safe_route 'The release must not be deployed; explain the plan.'
expect_safe_route 'Release notes: explain the deployment process.'
expect_safe_route 'I want to know whether it is safe to deploy this release.'
expect_safe_route 'I need advice on whether to deploy this release.'
expect_safe_route 'Do not change the release plan, but explain the deployment process.'
expect_safe_route "Don't change the build or release notes; review the plan."
expect_safe_route 'Is the plan ready for release, or does it need review?'
expect_safe_route 'Could you deploy the reviewed release?'
expect_route unclear '/li:cycle' low 'Review the change then deploy it.'
expect_route build '/li:cycle' high 'Implement release-note validation.'
expect_route fix '/li:cycle --mode hotfix' high 'Fix review comments.'
expect_route ship '/li:cycle --from SHIP' high 'Release v2.'
expect_route deploy '/li:cycle --from SHIP' high 'Please deploy the reviewed release.'
original_ifs="$IFS"
IFS=:
expect_safe_route 'Do not change the release plan; explain it.'
ifs_probe=$(classify_intent 'Do not change the release plan; explain it.'; printf '|%s' "$IFS")
[ "$ifs_probe" = 'research|:' ] || {
  printf 'FAIL: independent row 20 changed caller IFS or intent\n' >&2
  failed=$((failed + 1))
}
checked=$((checked + 1))
expect_route deploy '/li:cycle --from SHIP' high 'Deploy the reviewed release.'
ifs_probe=$(classify_intent 'Deploy the reviewed release.'; printf '|%s' "$IFS")
[ "$ifs_probe" = 'deploy|:' ] || {
  printf 'FAIL: independent row 21 changed caller IFS or intent\n' >&2
  failed=$((failed + 1))
}
checked=$((checked + 1))
IFS="$original_ifs"
expect_route unclear '/li:cycle' low 'Build the service and edit its configuration.'
expect_route unclear '/li:cycle' low 'Build the service; edit its configuration.'
expect_route unclear '/li:cycle' low 'Deploy the release and change the deployment manifest.'
expect_route unclear '/li:cycle' low 'Deploy the release; change the deployment manifest.'
expect_route unclear '/li:cycle' low 'Build the service and provision the environment.'
expect_route unclear '/li:cycle' low 'Build the service; provision the environment.'
expect_route unclear '/li:cycle' low $'Deploy the release\nReview the release plan.'
expect_route review '/li:review' high $'Please\nreview the fix\nwithout changing code'
expect_route research '/li:cycle --mode research-dive' high 'Explain how to build and deploy the service.'
expect_route build '/li:cycle' high 'Implement audit and review logging.'
expect_safe_route 'Release commands are prohibited; explain the plan.'
expect_route research '/li:cycle --mode research-dive' high 'I would like information about how to deploy the release.'
printf 'independent 33-case matrix: %s assertions, %s failures\n' \
  "$((checked - matrix_start))" "$((failed - matrix_failures))"

# Explicit contract fixtures, not a vocabulary or expected result read from the router.
head_count=0
while IFS='|' read -r direct_intent direct_workflow head object; do
  head_count=$((head_count + 1))
  expect_route "$direct_intent" "$direct_workflow" high "$head $object."
  for separator in ' and ' ' or ' '; ' $'\n' $'\r\n'; do
    expect_route unclear '/li:cycle' low "Build the service${separator}${head} $object."
    expect_route unclear '/li:cycle' low "Review the first report${separator}${head} $object."
  done
  expect_route "$direct_intent" "$direct_workflow" high "Please"$'\n'"$head"$'\n'"$object."
  expect_route research '/li:cycle --mode research-dive' high \
    "Explain how to"$'\n'"$head $object and $head $object."
  expect_route review '/li:review' high "Assess whether to $head $object or $head $object."
  expect_route unclear '/li:cycle' low "Do not $head $object or $head $object."
  expect_route review '/li:review' high "Do not $head $object"$'\n'"review the plan."
done <<'HEADS'
review|/li:review|review|the report
review|/li:review|audit|the change
review|/li:review|check|the configuration
review|/li:review|inspect|the patch
review|/li:review|examine|the report
review|/li:review|analyze|the change
review|/li:review|analyse|the configuration
review|/li:review|assess|the patch
review|/li:review|evaluate|the report
review|/li:review|granska|den trasiga releasen
research|/li:cycle --mode research-dive|research|the options
research|/li:cycle --mode research-dive|explore|the design
research|/li:cycle --mode research-dive|understand|the process
research|/li:cycle --mode research-dive|explain|the options
research|/li:cycle --mode research-dive|describe|the design
research|/li:cycle --mode research-dive|read|the report
research|/li:cycle --mode research-dive|compare|the options
research|/li:cycle --mode research-dive|summarize|the design
research|/li:cycle --mode research-dive|summarise|the report
research|/li:cycle --mode research-dive|show|the options
research|/li:cycle --mode research-dive|list|the options
research|/li:cycle --mode research-dive|know|the process
research|/li:cycle --mode research-dive|utforska|alternativen
research|/li:cycle --mode research-dive|förstå|processen
research|/li:cycle --mode research-dive|tell me|about the process
plan|/li:plan|plan|the release
plan|/li:plan|design|the service
plan|/li:plan|outline|the change
fix|/li:cycle --mode hotfix|fix|the bug
fix|/li:cycle --mode hotfix|fixa|felet
fix|/li:cycle --mode hotfix|felsök|felet
deploy|/li:cycle --from SHIP|deploy|the service
deploy|/li:cycle --from SHIP|deploya|tjänsten
deploy|/li:cycle --from SHIP|provision|the environment
deploy|/li:cycle --from SHIP|driftsätt|till produktion
ship|/li:cycle --from SHIP|ship|the release
ship|/li:cycle --from SHIP|release|v2
ship|/li:cycle --from SHIP|shippa|releasen
ship|/li:cycle --from SHIP|landa|ändringen
resume|/li:resume|resume|the work
resume|/li:resume|continue|the work
resume|/li:resume|fortsätt|med granskningen
resume|/li:resume|pick up|the work
scaffold|bin/li-scaffold init|scaffold|the repository
scaffold|bin/li-scaffold init|starta|projektet
scaffold|bin/li-scaffold init|new|project
scaffold|bin/li-scaffold init|new|repo
scaffold|bin/li-scaffold init|new|repository
scaffold|bin/li-scaffold init|nytt|projekt
scaffold|bin/li-scaffold init|create|a new project
build|/li:cycle|build|the service
build|/li:cycle|add|the option
build|/li:cycle|implement|the change
build|/li:cycle|create|the fixture
build|/li:cycle|edit|its configuration
build|/li:cycle|change|the manifest
build|/li:cycle|modify|the setting
build|/li:cycle|write|the adapter
build|/li:cycle|bygg|en ny funktion
build|/li:cycle|new|feature
build|/li:cycle|lägg till|en funktion
HEADS
printf 'governing-head contract fixtures: %s\n' "$head_count"

for request in \
  'Implement audit and review logging.' \
  'Implement review and audit logging.' \
  'Build research and review tools.' \
  'Build audit and check logging.' \
  $'Implement audit and\nreview logging.' \
  $'Implement audit\nand review logging.' \
  'Build test and release fixtures.'; do
  expect_route build '/li:cycle' high "$request"
done
for request in \
  'Implement audit and explain logging.' \
  'Implement audit and review the logs.' \
  'Implement audit and please review logging.' \
  'Implement audit and review logging and provision the environment.' \
  $'Implement audit;\nreview logging.' \
  'Deploy the service and review logs.' \
  'Review the report and inspect config.' \
  'Build the service and edit config.' \
  'Implement audit and edit config.' \
  'Implement audit and change state.'; do
  expect_route unclear '/li:cycle' low "$request"
done
for first_request in 'Build service' 'Build release' 'Deploy release' 'Implement adapter' 'Implement release' 'Fix bug' 'Change config' 'Review report'; do
  for separator in ' and ' ' or '; do
    expect_route unclear '/li:cycle' low "${first_request}${separator}review config."
  done
done
for request in \
  $'Please\r\nreview the fix\r\nwithout changing code' \
  $'Review the\nfix and deployment documentation.' \
  $'Review "Deploy the release\nReview the plan" without executing it.' \
  $'Review `Deploy the release\nReview the plan` without executing it.' \
  'Review build and release scripts.'; do
  expect_route review '/li:review' high "$request"
done
for request in \
  $'Explain how to build and\ndeploy the service.' \
  $'Explain how to build\nand deploy the service.' \
  $'Explain this command:\ndeploy the release.' \
  $'I want to\nknow whether to change and deploy the release.'; do
  expect_route research '/li:cycle --mode research-dive' high "$request"
done
for separator in ' and ' '; ' $'\n' $'\r\n'; do
  for wrapper in 'Please ' 'Kindly ' 'I need you to ' 'I want to ' 'I would like to ' 'Help me '; do
    expect_route unclear '/li:cycle' low "Build the service${separator}${wrapper}edit its configuration."
  done
done
original_ifs="$IFS"
for caller_ifs in ':' '|' ''; do
  IFS="$caller_ifs"
  expect_route unclear '/li:cycle' low 'Build the service and edit its configuration.'
  expect_route unclear '/li:cycle' low $'Deploy the release\nReview the release plan.'
  expect_route review '/li:review' high $'Please\nreview the fix\nwithout changing code'
  ifs_probe=$(classify_intent $'Deploy the release\nReview the release plan.'; printf '|%s' "$IFS")
  [ "$ifs_probe" = "unclear|$caller_ifs" ] || {
    printf 'FAIL: structural boundary changed caller IFS or intent\n' >&2
    failed=$((failed + 1))
  }
  checked=$((checked + 1))
done
IFS="$original_ifs"
printf 'intent-operation-boundary complete: %s assertions, %s failures\n' "$checked" "$failed"
[ "$failed" -eq 0 ]
