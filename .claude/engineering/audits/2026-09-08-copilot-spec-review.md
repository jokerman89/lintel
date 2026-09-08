# Copilot implementation review — stage 1

Date: 2026-09-08. Reviewer: independent public-surface/session-protocol workstream.
Scope: BC2/BC3, requirements R2–R6 in the approved launch specification.
Method: read implementation, adapters and canonical workflows; run the actual installer/check
in an isolated temporary consumer. No implementation edits by this reviewer.

## Initial verdict: changes required

| Requirement | Evidence | Result |
|---|---|---|
| R2 native discovery | Thirteen lowercase `li-*` wrappers, three `.agent.md` profiles, explicit Copilot manifest directories | Structural pass; no live-host validation claimed |
| R3 fresh-checkout portability | Source bundle and environment helper separate source from project output | Resume gap below blocks advertised continuity |
| R4 deterministic non-clobber install/check | Temporary consumer init/check passed; ownership preflight reviewed | Runtime ignore gap below |
| R5 honest capability | Copilot native-agent declaration; no translated Claude hooks; explicit empty Copilot hook registration | Pass for declared adapter boundary |
| R6 authoritative Spec Kit artifacts | Bridge defines exact artifact ownership and task IDs | Downstream BUILD contract conflicts with that ownership |

## Findings

### P1 — Spec Kit handoff delegates into a conflicting BUILD contract

At initial review, `skills/spec-kit/SKILL.md:44–47` created a handoff and allowed reference-only
plan/spec companions; line 68 invoked canonical BUILD. `skills/build/SKILL.md:36` and `:52`
required an APPROVED `plan.md`, and `:67`/`:86` extracted all tasks and their full text from
that file. A normal Spec Kit feature stores its tasks in `tasks.md` and need not carry Lintel's
literal approval status. A reference-only plan cannot satisfy these instructions without copying
the tasks or re-planning. R6 requires explicit mapped-artifact handling through BUILD, REVIEW
and RESUME, preserving authorization and original task IDs.

### P1 — Fresh checkout loses resume despite committed work

At initial review, `skills/resume/SKILL.md:92` declared no prior work when neither the local ledger
nor a session checkpoint existed. Both are under gitignored runtime storage. A new machine or
cloud checkout can contain committed plan/handoff/working-state/Spec Kit files and still be
redirected to a new cycle. R3 and the advertised cold handoff need a committed-state fallback
that resolves an explicit active feature or plan, without choosing the newest directory by time.

### P2 — Installer check reports verified after runtime ignore disappears

`bin/li-copilot.py` read `.gitignore` but only verified `.gitattributes` in its check branch.
Reproduction with the actual generator: temporary consumer `init` returned 0; `check` returned 0;
remove only the temporary target's `.gitignore`; `check` still returned 0 and printed
“Copilot kit verified”. This leaves session churn and potentially sensitive runtime evidence
eligible for accidental commit while integrity is reported green. Check must verify the required
runtime exclusion; add a regression for deletion and effective negation.

## Source-root observation

Many canonical snippets still located helpers through the working repository or home fallback
instead of `LINTEL_SOURCE_ROOT`, even though the portable environment intentionally separates
the two roots. Adapter prose can translate these examples, but native onboarding is stronger
when the executable examples directly resolve the bundled source. Keep state writes on the
working repository while changing helper lookup; never solve this by directing output into the
bundle. This observation was sent to the owning implementer for evaluation.

## Next review

Recheck the identified contracts after the owners' fixes. Stage 2 correctness/security review
starts only after stage 1 passes. File line numbers above record the initial reviewed state and
may move as the fixes land. Static and hermetic evidence remain separate from real Copilot
client discovery, tenant policy and model-adherence validation.

## R4 re-review

The owning implementer added runtime-ignore validation. Independent recheck: install in a new
isolated target, remove only its `.gitignore`, run `check` → exit 1 naming the missing runtime
rule; run `init` to repair and `check` → exit 0. The reported R4 failure is closed. The owner also
added effective Git-ignore verification and a negation regression; those remain separately
attributed to their test output until independently reviewed.

## Final stage 1 re-review: pass at the contract layer

The owners added a shared committed `work.json` contract and read-only validator. PLAN now
selects mapped Spec Kit work before its ordinary template pipeline; BUILD reads original tasks
and mapped approval scope; REVIEW uses the same spec/design/tasks mapping; RESUME consults
committed maps or explicit legacy links when local runtime files are absent. The R3 and R6
findings are closed. Source-only helper lookups now use LINTEL_SOURCE_ROOT while project output
continues to use the working-repository root.

This is a pass of the documented and implemented repository contract. It does not assert live
Copilot discovery, agent adherence or an enterprise tenant pilot.

## Stage 2 correctness and security review

Performed after the stage 1 fixes passed. Reviewed the work-map parser and path confinement,
status/version/workflow validation, artifact separation, source/output root handling, native
adapter paths and hook boundary. No remaining actionable findings in this review scope.

Independent CLI exercise used a fresh temporary repository with a normal Spec Kit technical
plan (no Lintel approval heading), original T017 task, separate handoff and no runtime ledger.
Validation returned the original distinct task/design paths and left all Spec Kit files
byte-identical. Invalid schema version (including boolean), workflow, status, traversal path,
Windows drive path and absent required artifact were rejected. The validator did not create
runtime state or execute artifact content.

The release-quality workstream separately tests full consumer installation, clone behavior,
managed-block ownership and effective Git-ignore negation. Those tests are not claimed as this
reviewer's independent runs. Real Copilot/model/tenant validation remains a stated external
acceptance step.
