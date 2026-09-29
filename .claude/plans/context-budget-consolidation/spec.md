# Context budget consolidation

Status: APPROVED for the bounded implementation authorized on 2026-09-29.
Parent card: `W4-2.context-budget`.
Original findings: V2 `lane-B-03` and `lane-E-05` (ContextBudgetAdvisor only).
Base: `19b30eef82abed3ac931cdae5e298a648291db54`.

## Outcome

Make context-budget the single owner of observation, watch, resource advice and
handoff-budget interpretation. Retain perf-mode, handoff-size-check and the
read-only ContextBudgetAdvisor as compatibility entry points. This package does
not retire a skill or agent, close the entire parent card, or change governance.

## Acceptance

| ID | Requirement | Observable acceptance |
|---|---|---|
| A | Preserve routing and provider results | Direct advice/handoff and compatibility routes produce the existing provider outcomes for the same inputs. Default observation and watch semantics remain unchanged. Conflicting routing selectors fail visibly. |
| B | Preserve read-only authority | No host/model configuration, active context, files or telemetry are changed by budgeting. Unknown capacity/usage/cost stay unknown; advice reports no host settings change. |
| C | Preserve selected-work evidence | Explicit work/profile/task identities, distinct artifact counting, bounded warming, missing-input errors and advisory versus required limits remain intact. Skip flags record not-run, never PASS or a waiver. |
| D | Preserve compatibility | All three canonical/native skill names and ContextBudgetAdvisor remain. Numeric advice `--budget` and watch configuration `--budget` are mode-scoped. Watch `--mode` and legacy handoff `--plan` retain their meanings. |
| E | Own the method once | Compatibility entries delegate without maintaining duplicate procedures. PLAN/CAPTURE/Spec Kit call the owner directly. Ordinary budgeting introduces no subagent or new runtime service. |
| F | Report evidence honestly | Focused executable routing/equivalence/refusal tests and generated-artifact checks cover this change. No runtime gain, whole-portfolio completion, live-host acceptance or independent review is inferred. |

## Boundaries

Use the existing `bin/_context.sh`, `lib/context_safety.py` and
`bin/li-work-artifacts.py` as engines. Skill-level `--advice` and `--handoff`
selectors are not forwarded to those engines. Watch configuration remains data
handled by the existing workflow; no new YAML parser or background watcher.

The approved implementation glue is one `skills/context-budget/references/route.sh`.
It resolves providers from its own trusted bundle, removes only its own leading
selector, preserves quoted arguments and rejects conflicting selectors visibly.
It neither evaluates command text nor adds a budget engine or parser.
Watch remains instruction-driven. Legacy `--plan` or positional-plan inspection
keeps its explicit existing-reader/manual join instead of pretending to be a new
mechanically complete mapped handoff. Tests distinguish that boundary.

Own only the selected skills, their necessary references, ContextBudgetAdvisor,
the two selected user guides and four selected test files. The integration owner
owns versions and final generated inventory. Local generation is verification,
not permission to hand-edit generated files.

The bounded review repair additionally permits only the
`categories.handoff-size-checks.kinds.size_check.producers` pointer in
`lib/event-catalog.json`: it follows the single optional instruction to the
context-budget owner. No category, schema, historical record or other producer changes.
The routing reference remains read-only; optional logging requires separate authority.

Preserve the trusted-source fixes in the base, pattern/adaptive joins, P05/P07,
original work IDs and existing required-policy semantics. No full suite, new actor,
paid model, host probe, installation, dependency, publication or cleanup is in scope.
