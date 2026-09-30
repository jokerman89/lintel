# Context budget consolidation plan

Status: APPROVED within the 2026-09-29 bounded implementation release.
Parent: `W4-2.context-budget`; findings `lane-B-03`, `lane-E-05`.
This is its finite derived subscope, not a replacement remediation backlog.
Source baseline: `19b30eef82abed3ac931cdae5e298a648291db54`.

## Design and ownership

Keep default observation and the existing watch method in context-budget. Add
explicit advice and handoff routes to the existing readers, retaining provider
argument/error semantics. Move shared advice, interpretation and handoff rules to
that owner. Compatibility skills retain their names and argument translation,
not another method. ContextBudgetAdvisor stays read/search-only.

First-party PLAN/CAPTURE/Spec Kit call the owner directly. Keep the existing
handoff skip flags and selected map/profile requirements. No default agent call
or new state store is introduced.

The only new executable is directly needed selector glue in
`skills/context-budget/references/route.sh`, approved as part of this package.
Provider parsers remain unchanged. Watch and the legacy selected-plan join remain
explicit workflow steps; their limits cannot be converted into a mechanical PASS.

| Package ID | Outcome | Leaf IDs | Owner / edit boundary | Dependencies | Review |
|---|---|---|---|---|---|
| CB1 | One budget owner with compatible routes and evidence | T1, T2, T3, T4 | budget implementer; skills/context-budget, skills/perf-mode, skills/handoff-size-check, skills/plan/SKILL.md, skills/capture/SKILL.md, skills/spec-kit/SKILL.md, agents/engineering/ContextBudgetAdvisor.md, docs/power-user.md, docs/concepts/planner-as-module.md, tests/unit/context-safety.py, tests/unit/planning-consolidation.py, tests/unit/closeout-additions-present.sh, tests/shape/handoff-cap-wired.sh, lib/event-catalog.json | none | substantive |

## Tasks

### T1 Add executable routing, equivalence and refusal cases

- [x] Implement and verify the cases using the existing context fixtures.
Requirements: A, B, C, D.
Dependencies: none
Verify: focused new unittest cases fail on the unchanged owner, then pass after T2;
exercise actual providers, not only names in prose.

### T2 Centralize the budget method

- [x] Centralize observation/advice/handoff interpretation and preserve watch.
Requirements: A, B, C, D, E.
Dependencies: T1
Verify: direct and compatibility cases agree for known/estimated/unknown/error inputs;
flags retain mode-specific meanings and provider state remains unchanged.

### T3 Wire retained callers and guides

- [x] Wire compatibility skills, Advisor, first-party callers and the two guides.
Requirements: C, D, E.
Dependencies: T2
Verify: selected planning/shape checks pass; original names/tool boundary and
not-run versus required-limit semantics survive.

### T4 Return the verified candidate

- [x] Run focused checks and generated-artifact verification.
Requirements: A, B, C, D, E, F.
Dependencies: T3
Verify: record exact commands/results and scope; the existing independent reviewer
assesses the actual candidate later. No publication or parent closure here.

## Profile and verification

Establish a new named repository-local context from this worktree's actual source,
requirements and pack store. Record its returned reference and required-policy
bridge in local runtime evidence; never borrow another context or use a global
activation. Re-verify that same reference for dependent work.

Smallest checks first: selected context-safety unittest cases, selected
PlanningSourceTests, handoff-cap-wired and closeout-additions-present. Generate
native files only through the existing generator when source checks pass.
No full suite or live client/model run.

## Progress and review

CB1 is delivered in `0baa9a0c` (0.13.4). The bounded P2 repair passed the same
independent source review; the joined candidate then passed its own canonical
specification/quality review, current QA, corroborated latest reader and SHIP.
Hosted run [36617340336](https://github.com/jokerman89/lintel/actions/runs/36617340336)
passed 23 jobs and 549 strict script-file executions (183 per OS), with no
failed, skipped or partial entries. All four original leaves are complete.
The wider portfolio parent remains open; no entry retirement or governance
change follows from this package.

| Leaf | Implementer evidence |
|---|---|
| T1 | Two new routing methods failed as expected before route.sh existed; 13 failing subcases, exit 1. Final selected routing run: 11 tests PASS, including actual provider equivalence, refused selectors/selection bounds and generated-kit recipe execution. |
| T2 | Observation/advice/mapped handoff use the existing engines. Watch and legacy-plan joining remain explicitly instruction/manual-level; no new parser or mechanical completion claim. |
| T3 | PlanningSourceTests: 11 PASS. Handoff wiring: 17 assertions PASS. Closeout compatibility: 13 assertions PASS. Names, Advisor tools and existing skip/required-bound distinctions remain. |
| T4 | Local native generation and check: 172 managed files verified. Generated manifest/output is verification-only for coordinator integration. No full suite, client/model run, dependency installation, commit or publication. |

The final routing run took 48.545 seconds on this host; this is test duration,
not a performance or model-efficiency claim. Raw outputs remain in the
implementing target's ignored runtime; they are not distributed with a clone.
The earlier green routing observation and expected red result remain separate
records. The implementer evidence table is historical local evidence, not a
claim that it executed the later joined matrix.

Own profile context: `context-budget-consolidation`, generation 1, `_default` 1.0.0,
digest `sha256:5fb46129c94d8d05683ab765cd719ae3325e10176bbbb5a8892dc92be23f0049`.
Actual required-policy result: `required: false`, `status: not_required`,
`source: bundled-neutral`, `version: 1.0.0`, `applicability: not_applicable`.
The reference and context are local runtime evidence, not transferable clearance.

The initial candidate's four instructional files decreased from 17,884 to 15,558
bytes; its selector glue added 2,165 bytes. This is the preserved pre-repair
measurement, not a claim about the repaired bytes. The canonical inventory remains
97 skills and 69 agents. No
entry retirement, whole-portfolio closure or runtime saving is claimed.

The base includes a separately owned trusted-source repair candidate, not a new
acceptance result for that work. Its five canonical files and the existing budget,
work-map and profile engines were left unchanged. Versions and final catalog/wiki
and generated-inventory reconciliation remain with the integration coordinator.

### Bounded review repair

The independent source review requested restoration of the optional handoff audit
producer. The released repair moves the single example into context-budget and
changes only its catalog producer pointer, as bounded in spec.md. It also preserves
empty-array argument forwarding on older Bash syntax and restores explicit
authority-file/small-work guidance. Prior patches, receipt and test logs remain
historical inputs; new repair evidence is recorded separately. No Bash 3.2 runtime
coverage is claimed without actually running that interpreter.

The repair regressions failed before the fix (three methods, four failed assertions).
After the fix, three producer/preservation source checks and four impacted
routing/inherited-map/refusal/compatibility/generated-kit tests passed. The
available Bash 5.3.15 syntax check passed; Bash 3.2 behavior was not run. Optional
audit instruction presence and catalog agreement are checked, not a claim that
this review executed the optional audit writer.
