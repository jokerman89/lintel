# Plan: trusted workflow helper sources

**Status:** APPROVED for original card W1-1 under the operator's implementation request.
**Spec:** [spec.md](spec.md).
**Base:** `2c81267bedc213f7e895f10f9b59d8e1a1e258f6`.
**Execution:** sequential, one writer; no new swarm or competing findings register.

## Outcome and package

This is the first bounded implementation slice of the existing review findings,
not a claim that the entire remediation program is complete.

| Package ID | Outcome | Leaf IDs | Owner and edit boundary | Dependencies |
|---|---|---|---|---|
| P1 | Workflow examples never substitute target code for missing trusted helpers. | W1-1 | Coordinator: five canonical skills, their generated native copies, managed manifest, focused regression tests and directly related delivery metadata. | none |

The native generator, Patterns and Adaptive review prerequisites are already
integrated in the recorded base; they are not unfinished package dependencies.

## Original task

- [x] W1-1 Remove executable-source fallbacks from REVIEW/SHIP and the same pattern in other canonical skills; preserve source/target separation, explicitly degrade an unavailable footer, and verify R1-R4.

### W1-1 execution and acceptance

1. Add the bounded regression contract; observe the pre-fix static source failure
   without executing the unsafe fallback.
2. Replace the identified source-selection expressions using existing adapter
   conventions. Required steps refuse missing helpers; optional footers degrade
   explicitly. No new helper library is necessary.
3. Regenerate native files using the existing generator, never hand-edit them.
4. Run the focused regression, existing source/target and footer checks, and
   source/native drift checks. Record actual results and limitations.
5. Obtain independent specification and quality review of this exact package,
   then follow the existing content-bound delivery gate on the verified candidate.

## Signals and profile impact

One original defect card; no new product architecture. The hotfix route retains a
minimal mapped work contract rather than starting another whole-repository review.
Whole-cycle token use is uncalibrated and not yet measured. The previously supplied
4-8 hour first-batch estimate includes integration/review/hosted CI and is not a
guarantee. The fix explicitly selects the bundled `_default` pack in its own
repository-local context. The resolver therefore reports a required, loaded
profile (`source: invocation:LINTEL_PROFILE_PACK`, version `1.0.0`), not an
unrequested-policy exemption. Carry that actual policy result unchanged. The
neutral pack adds no company hooks. Never borrow another worktree's profile.

## Preservation

Keep the original DR/W identifiers. The operator correction to existing lesson
L-029 is a separate continuity change, not evidence that W1-1 is complete.
Do not edit `.claude/plans/todo.md`: its historical source spans bind the entire
file. Link this map from mutable working memory after the implementation.

## Review

The source correction and generated native bodies are implemented locally.
Nine focused behavioral/static regressions pass, along with the existing
source/target and footer checks, 13 workflow-contract tests, native/catalog/wiki/
instruction drift checks and the full command-surface guard. The static pre-fix
test failed before any affected workflow example was executed.

Independent specification and quality review, current bound QA, actual host
corroboration and the shared SHIP gate passed. The exact candidate's hosted
run [36589853696](https://github.com/jokerman89/lintel/actions/runs/36589853696)
passed all 23 jobs and 525 strict script-file executions, with no failed,
skipped or partial entries. W1-1 landed on main at `19b30eef` (0.13.3).
The earlier local observations above remain their original evidence, not
claims that this later capture commit ran that matrix. The broader remediation
programme is not closed by this leaf.
