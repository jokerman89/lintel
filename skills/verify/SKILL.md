---
name: verify
layer: foundation
description: Use to check whether a change works without changing it. Runs applicable tests or document checks, reports failures and preserves bound QA evidence. Repair requires an explicit --repair request within the authorized scope.
color: blue
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /verify

Verify the selected result, not a convenient subset or an earlier revision. The default
is one read-only verification pass. An explicit repair mode retains the useful
classify/fix/rerun loop without turning a release check into an unreviewed code change.

## When to use

- After implementation, before review, to observe the applicable acceptance checks.
- Before SHIP, to check the exact reviewed result without introducing fixes.
- To reproduce CI failures locally in an authorized synthetic environment.
- With explicit repair authority, to correct bounded snapshot, lint or import drift.

Use `/diagnose` for a product-logic failure or recurring flake whose cause is unknown.
No runner or a missing dependency is a limitation to resolve, not permission to install
tools, rewrite expectations or silently skip required coverage.

## Inputs

`/verify [--scope <path>] [--json] [--verbose] [--no-fix | --repair [--max-iterations <N>]]`

- `--scope <path>` selects a test subset. Omitted scope uses the repository's canonical
  suite or the approved package's validation, not an arbitrary sample.
- `--json` returns the compatible reporting JSON below. Full logs remain separate.
- `--verbose` includes complete redacted failure traces; otherwise show the first
  10 lines per failure and the retained output location.
- `--no-fix` explicitly selects the read-only default.
- `--repair` requests bounded repairs within current authority.
- `--max-iterations <N>` is a positive integer limiting repair-and-rerun cycles
  (default 3). It requires `--repair`; it never adds retries to read-only mode.

These are workflow inputs; inspect the actual test runner's options rather than
passing these flags to it blindly.

## Modes and authority

| Invocation | Behavior |
|---|---|
| `/verify` or `/verify --no-fix` | read-only default; one run, no fixes or automatic retries |
| `/verify --repair` | baseline, bounded authorized repairs, reruns, then a separate read-only check |
| `/verify --repair --no-fix` | conflicting modes; report the conflict before execution |

Tool availability does not authorize a mutation. Existing explicit task authority
can cover a repair; do not ask again for that same scope. An unrequested product
change, frozen path, live service, credential use or new dependency needs its own
decision. SHIP always uses read-only mode, never `--repair` after review.
Read-only refers to the selected source/configuration/acceptance, not a promise
that a test runner writes no temporary files. Authorize and isolate those effects.

## Read-only verification

1. **Resolve acceptance and preflight effects.** Read the selected work map, original
   leaf criteria and expected context when supplied. Inspect the repository's runner,
   scripts and hooks for side effects before executing them. Use owned synthetic
   home/temp/data roots for fixtures, including the parent process. Do not contact
   live systems or load personal credentials merely because a test command exists.
   If several runners apply, use the accepted validation plan; resolve any remaining
   ambiguity rather than choosing the easiest green command.
2. **Single run.** Execute each required command once against the selected result.
   Capture command, source/environment/configuration identity, stdout, stderr,
   executed/failed/skipped counts and raw exit code. No automatic retry and no fixes,
   snapshot updates, formatter writes or dependency installation.
3. **Classify.** Distinguish snapshot drift, lint/format, type/import, assertion,
   flake-suspect and runner crash. A timeout is not proven flaky by its label.
4. **Report.** Give file:line, observed failure, category, evidence location and a
   one-line cause hypothesis. Recommend `/diagnose`, an explicitly authorized
   `/verify --repair`, or a new read-only run; do not perform those follow-ups implicitly.

A document-only package can require a real link/example/document check with grounded
tests N/A. Follow approved acceptance rather than inventing a universal software-test
obligation. A scope-limited or sampled run stays partial for omitted requirements.

## Authorized repair

1. Require an explicit `--repair` request and established owned paths. Read the same
   baseline as above before editing. Preserve any pre-existing failure and dirty work.
   Honor frozen scope and stop the affected repair when authority is missing.
2. Classify candidates. Verified snapshot drift, lint/format or a missing import can
   receive a targeted repair only when intended behavior is established. Never weaken
   an assertion, delete a failing test, invent expected output or change product logic
   just to get green. Unknown assertions go to `/diagnose`; a known product fix belongs
   to its authorized build card.
3. Record pre-images and this operation's attributable post-images before any recovery.
   Prefer a separate owned trial. For authorized in-place recovery, use
   `bin/li-snapshot.py` from the trusted source, with explicit paths, a non-overlapping
   store and conflict-free preflight. A later edit is a conflict, not permission to
   discard it. Retain the failed trial/journal after interrupted or failed recovery;
   never perform a whole-tree rollback.
4. Apply the smallest allowed repair, scan its payload for secrets/customer data, and
   rerun affected checks. Preserve the initial failure and each iteration's output.
   A repair that introduces a new failure stops that repair; restore only its verified
   owned post-images if authorized, otherwise retain the evidence and escalate.
   A flake retry in repair mode needs an understood, repeatable, safe command and
   remains a separate observation, not erasure of the failed run.
5. Stop after `--max-iterations` or when no safe candidate remains. Report **STUCK**
   with remaining failures and the next discriminating action. Group successful fixes
   into a reviewable diff, without staging, committing or publishing implicitly.
6. Every changed selected input requires a new context and affected checks. Return
   to independent review where required, then read-only verification of that exact
   reviewed result. A green repair iteration cannot carry the old review into SHIP.

Keep the existing authorized audit event/store for repairs, using the trusted source:
`source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"; audit_log qa-fixes auto_fix file=<path> fix_kind=<lint|snapshot|import>`.
Substitute actual values as data. Record a successful write only after the audit helper
succeeds; unavailable persistence is an explicit limitation, not a receipt.

## Evidence and acceptance

Use the [shared v2 QA/evidence procedure](../review/references/evidence.md), not a
new skill-specific evidence schema. For mapped work, the prepared `qa_requirements`
inventory and expected `context_digest` remain authoritative. Results cannot omit
IDs, retype tests as generic checks, downgrade mandatory failures, add observation-chosen
`not_applicable` exemptions or alter policy references. A changed requirement needs
a new prepared context and independent review, not relabeling a failing observation.

Pass the observed controls and hashed output to `li-review-evidence.py qa`. This helper
validates observations; it does not run tests or document checks. Preserve the work map,
original package/leaf IDs, acceptance, attempt, selected content and verified profile
context/generation/digest. Missing required policy remains unresolved.

When tests apply, zero executed tests, unknown counts, failed or skipped required
tests remain blocked, even beside a passing document check. N/A-only or advisory-only
results cannot clear mandatory QA. The shared QA gate returns exit 3 for unresolved
acceptance; preserve a runner's actual exit separately. Crashes are errors, not a
successful empty test run.

SHIP uses this exact expected context, the latest applicable independent review,
actual host/human corroboration and the shared read-only QA result. Changes to relevant
source, staged/dirty/new/deleted files, configuration, dependencies, documents or
acceptance invalidate affected evidence. Age alone neither clears nor invalidates it.

Without a work map, keep the useful ad-hoc check. Use shared `snapshot` and `inspect`
with `release_clearance: false`; do not manufacture a duplicate plan or backlog.
Partial findings and unavailable controls stay visible.

## Report and JSON compatibility

Retain the useful QA report fields in both modes:

```text
QA Status: <branch>
Mode: read-only | repair
Runner: <actual command>
Iterations: <actual runs and repair cycles>
Initial failures: <count or unknown>
Auto-fixed: <count and owned paths; 0 in read-only mode>
Remaining: <count or unknown>
Exit: <raw runner exit>
Failures: <file:line, category, observation, recommendation>
Evidence: <exact context and output locations; unrun requirements>
```

`--json` preserves `runner`, `passes`, `failures`, `skipped`, `exit` and `failures_list`.
Keep counts numeric when observed and null when unknown, never turn missing data into
zero. `exit` is the raw runner exit, not a clearance verdict. Additional mode/iteration
details are informational. Emit only the JSON report on that output channel.

```json
{
  "runner": "pytest",
  "passes": 87,
  "failures": 1,
  "skipped": 2,
  "exit": 1,
  "failures_list": [
    {
      "file": "tests/test_refund.py",
      "line": 42,
      "category": "assertion",
      "message": "Expected 100, observed 200",
      "recommendation": "/diagnose the selected refund failure"
    }
  ],
  "mode": "read-only"
}
```

This compatible summary is not a release-clearance record. Emit the unchanged shared
v2 QA artifact separately at the caller's selected evidence location; SHIP consumes
that artifact, not a summary with zero failures. For multiple commands, retain each
command's report rather than hiding failures in one aggregate.

## Failure and recovery

- **No runner, no matched tests or missing dependency:** report what could not run;
  retain unresolved acceptance rather than installing tools or guessing coverage.
- **Runner crash:** capture stderr and its actual exit; do not retry blindly.
- **Required browser/renderer/service unavailable:** leave that control unverified.
  Static checks can continue but do not substitute for runtime observation.
- **Sensitive fixture/output:** stop unsafe use, redact the report and request a
  synthetic fixture. Do not copy customer data into evidence or repair payloads.
- **Interrupted repair:** preserve its exact snapshot, paths, outputs and remaining
  work. Recheck current ownership/conflicts before continuing the same operation.

## See also

- `/diagnose` - hypothesis-led root cause analysis without applying a product fix.
- `/cross-check` - a real independent second opinion, not a second role label.
- `/review` - specification, quality and compliance review of the resulting diff.
- `/ship` - consumes the latest bound review and read-only QA; never repairs.
