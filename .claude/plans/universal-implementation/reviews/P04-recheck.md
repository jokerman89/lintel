# P04 repaired component recheck

**Date:** 2026-09-20. **Mode:** independent, read-only product review by the same
reviewer who reported F01-F03. No implementation or nested delegation.

**Component verdict: REJECT.** F01-F03 are closed, but the previously unrun full
bounded quality review found two additional P2 defects. New open finding counts:
**P0 0 / P1 0 / P2 2 / P3 0**. These counts exclude the separately deferred
SW-03/A22.7 shared-corroboration work.

| Stage | Decision |
|---|---|
| F01-F03 repaired-specification recheck | PASS; independently reproduced old failures and verified repaired boundaries |
| Initial bounded specification pass | Passed the repair and existing component checks, allowing quality review to begin |
| Final bounded component specification | FAIL after quality counterexamples: A22.4.b and A22.5 are not satisfied; A22.6 remains blocked |
| Full bounded component quality | COMPLETED, FAIL; no longer NOT RUN |
| Historical merge preservation | Previous acceptance retained; no newly demonstrated historical loss |
| A22.7 / final Swarming / Universal acceptance | OPEN, outside this component clearance |

The final specification decision incorporates the new quality evidence. An initial
green specification pass is not retained as blanket acceptance after a concrete
acceptance counterexample appears.

## Exact snapshots and scope

| Reference | Immutable commit |
|---|---|
| Reviewed repaired product | `dca635df2b3e3ddb89e29a8c73a7d04d52f5a632` |
| Builder's later report-only tip, inspected separately | `28fc0dfcc5fd703237e944369951b41b2d90c183` |
| Previously rejected component | `02be6cb1448cd9def1572ae55e321f07d974a33b` |
| Full component review base / accepted historical merge | `e74849db6b33c7b93baadb86206009cb9f9eb6d5` |
| Narrow public-accessor correction | `8ea0fc4e4280803d1093468d06828daa54f9c700` |
| Previous component review, preserved | `6bf86c3c77d6e61701aa710d421324a7618fcc11` |
| Historical checkpoint review, preserved | `4bf5315d4636206f1df6a5f0c7a68a52e9341cae` |

Reviewed all eight repair paths and the full 30-path bounded
`e74849d..dca635d` component range, including actual producers, consumers, schemas,
templates, documentation and focused tests. The repaired product was materialized
in a separate clean reviewer worktree; the two previous reviewer worktrees/refs
were preserved. `28fc0df` changes only `reports\P04.md` relative to the product.
The commit containing this review is report-only and is not the product reviewed.

Authority was the P04 card, Universal specification/plan/work map, original
`reviews\swarm.md` audit, preservation audit/report, ADR-0026/0027, prior independent
review and updated builder evidence. Builder test claims are distinguished below
from checks actually executed by this reviewer.

## New findings

All citations in this section are one-based lines at the reviewed product
`dca635df2b3e3ddb89e29a8c73a7d04d52f5a632`.

| ID | Severity | Exact source | Finding |
|---|---|---|---|
| F04 | P2 | `lib\swarm_snapshot.py:99-102,120-122,134-137` | Git result verification loses file type/mode, retaining complete evidence after an unreviewed mode or symlink change |
| F05 | P2 | `lib\swarm_contract.py:582-584,1212-1215` | A completed coordinator-only package is permanently unsatisfied when another lane depends on its package ID |

### F04 - Include current file type/mode in Git result verification

**Cause.** `_git_scope_snapshot` permits modes `100644` and `100755` but reduces
both to path/content-hash entries. `_git_working_snapshot` also stores only bytes
and dereferences paths before checking `is_file()`. The comparison therefore
cannot distinguish executable-mode changes or a current regular-file-to-symlink
replacement with identical dereferenced content. The report/review still bind the
old result digest, and `verify_result` accepts it.

**Independent reproduction.** Used the existing `SwarmFixture` in a temporary
real Git repository, one BC1 lane owning `src/core`, real base/product commits,
and synthetic report/review records bound through `snapshot_lane`. A committed
`src/core/copy.py` held the same bytes as the regular product `file.py`.

1. Actual `li-swarm.py verify` accepted the original committed regular-file result.
2. Committed only `git update-index --chmod=+x -- src/core/file.py`, leaving the
   report/review unchanged. Git itself reported
   `mode change 100644 => 100755 src/core/file.py`.
3. The same public `verify` still exited 0 with `ok=true`, BC1 `complete` and no
   diagnostics.
4. Restored the regular mode with another fixture commit, then replaced the
   working `file.py` with an actual `os.symlink("copy.py", file.py)`. Confirmed both
   `is_symlink()` and unchanged dereferenced bytes. Public `verify` again exited 0,
   reported BC1 `complete` and emitted no diagnostic.
5. Restored the regular file; the positive control remained valid. Removed the
   entire temporary fixture. No source worktree was changed.

**Impact and contract.** Material scoped Git result changes can retain stale local
clearance, contrary to A22.5. Links are not simply deferred here: the implementation
explicitly rejects them in the declared commit, yet silently accepts one in the
current result. The claim that the current Git snapshot path rejects links is too
broad (`docs\concepts\swarming-work.md:211-214` and
`reports\P04.md:227-230`). Different actor strings or later A22.7 corroboration do
not repair this local observable-result comparison.

**Requested repair.** Bind and compare supported file type/mode as well as content;
reject unsupported current links/submodules before dereferencing them. Preserve
the documented CRLF normalization and ordinary regular-file behavior. Add public
snapshot/verify regressions for mode-only and same-content type changes, including
the Windows Git metadata case. This is a newly discovered component defect, not a
historical merge regression; `swarm_snapshot.py` is unchanged by the F01-F03 repair.
**Confidence: high, reproduced at the real CLI and Git boundaries.**

### F05 - Derive unmapped package prerequisites from their authoritative leaves

**Cause.** Package prerequisite booleans are populated with
`sources.get(dependency, {}).get("complete", False)`. `sources` contains leaf IDs,
not the grouping package IDs. `_dependency_blockers` uses this false value whenever
the dependency package has no swarm lane, instead of deriving completion from its
original member leaves.

**Independent reproduction.** A temporary, valid grouped plan contained:

| Package | Original member | Member status | Ownership / lane |
|---|---|---|---|
| P0 | T0 | `[x]` complete | Mechanical coordinator preparation, deliberately no lane |
| P1 | T1 | `[ ]` pending | One substantive lane owning `src/core`, dependency P0 |

Actual `li-swarm.py validate` exited 0; `package_sources` confirmed T0 was complete.
Actual `wave` returned `ok=true`, `dispatch_task_ids=[]` and
`blocked_by={"P1":["P0"]}`. Changing only the declared dependency from P0 to its
already-complete member T0 made the same public command dispatch P1 with no blockers.
Restoring dependency P0 and adding otherwise valid bound P1 report/review evidence
left its lane state `complete`, but public `verify` exited 1 with the sole diagnostic
`close.prerequisites`.

**Impact and contract.** A documented workflow cannot progress or close without
rewriting authority or adding a needless coordinator lane. This is not an
unresolved semantic prerequisite: the helper already observes the authoritative
member as complete and accepts the equivalent leaf dependency. Coordinator-only
packages may remain unmapped (`skills\swarm\SKILL.md:99-102`); grouping must not
replace original leaf status with an absent package-status record (ADR-0026).
The result breaks A22.4.b and consequently the dependent A22.6 workflow.

**Requested repair.** Resolve a known unmapped package from its original member
leaf completion/dependencies without inventing a second package-status authority.
Keep unresolved/incomplete prerequisites fail-closed and retain evidence-based
completion for mapped lanes. Add completed/incomplete coordinator-package cases
through both frontier and close. **Confidence: high, public CLI reproduction plus
the equivalent-leaf positive control.**

## Previous finding closures

| Finding | Recheck decision | Independent discriminating evidence |
|---|---|---|
| F01, P1: hard-linked ownership | CLOSED | Real `os.link` aliases from report and review to the mapped plan, confirmed with `os.path.samefile`; old component accepted, repaired library and CLI validation/worker/reviewer scope gates rejected. Also rejected reducer-descendant aliases, directory scopes, same-wave directories and cross-lane artifact aliases. Authority bytes stayed unchanged; removing an alias restores validity; separate equal-content files remain valid. |
| F02, P1: YAML constructor diagnostics | CLOSED | Reproduced old invalid-bool marker leakage. Seven bool/int/float/timestamp/empty-scalar combinations through both full Forge and non-quiet validator: 14 public-boundary checks returned failure, no stdout, safe `ENVELOPE BLOCKED:` diagnostics and no synthetic forbidden marker/traceback in stderr or audit. Included a bool in an unrelated field. JSON succeeded under `python -S`; optional YAML without site packages failed lazily and explicitly. |
| F03, P2: discarded root package limits | CLOSED | Root `README.md`, directory `src`, quoted `new source`, and new `FUTURE.md` accepted valid owned scopes and rejected unrelated ones in the repaired library/public CLI; the old component accepted widened scopes. Empty, owner-only, placeholder, wildcard, traversal, unmatched-backtick, prose and mixed-unknown limits failed closed. Quoted multi-path boundaries retained all literal paths. |

These are scoped closures of the reported counterexamples and their coupled cases,
not a claim that green suites prove every possible alias, parser or package input.
F05 is a distinct prerequisite-resolution defect, not a reopening of the repaired
root-boundary parser.

## Original audit and per-leaf dispositions

| Audit area | Component disposition |
|---|---|
| SW-01 | Original authority-overlap problem and F01 physical aliases closed for the exercised contract |
| SW-02 | ADR reconciliation, numeric/Spec Kit parsing, membership, limits and review depth preserved; package readiness remains incomplete under F05 |
| SW-03 | Source/attempt/report/content binding and explicit no-change work operate in tested cases; F04 leaves local result identity incomplete; independent actor/shared-contract binding remains OPEN under A22.7 |
| SW-04 | Project reducers remain coordinator-owned; ordinary and physical-alias negatives pass |
| SW-05 | Actual Markdown brief -> CLI adapter -> Forge -> strict envelope/evaluator boundary passes; original rich brief is retained as data |
| SW-06 | Both actor scope modes and actual Git reviewer-change checks pass; review-only ownership is distinct from worker scope |
| A21 unsafe output/audit | Tested construction/validation/security/evaluation/audit-before-output path passes, including payload-free constructor failure and fail-open audit-helper return without a persisted receipt |

PASS below is limited to the reviewed component and the evidence stated. It does
not extend to unrun clients or final shared bindings.

| Leaf | Final spec | Quality | Evidence / limit |
|---|---|---|---|
| A22.1.a | PASS | PASS | Recorded parents and required main/Swarming ancestries retained |
| A22.1.b | PASS | PASS | Current Universal authority and accepted hybrid/session sources preserved |
| A22.1.c | PASS, preservation scope | PASS, preservation scope | Enterprise/helper sources unchanged; actual work-map consumer validates; no fresh full Copilot/client matrix claimed |
| A22.1.d | PASS | PASS | Complete 76-path inventory/destination continuity; historical artifacts unchanged |
| A22.2 | PASS | PASS | Main ADR-0026 preserved, original Swarming body retained in ADR-0027, 27 unique ADR numbers |
| A22.3.a | PASS | PASS | Direct, ancestor, alias and real hard-link artifact-ownership cases |
| A22.3.b | PASS | PASS | Reducer protection, both actors, actual reviewer Git diff and cross-lane negatives |
| A22.4.a | PASS | PASS | Flat/phased/tree/numeric/Spec Kit and legacy singleton fixtures |
| A22.4.b | FAIL | FAIL | Existing membership/order/scope/depth checks pass; completed unmapped package dependency fails, F05 |
| A21.1 | PASS | PASS | Explicit invocation remains dormant otherwise; no dispatcher/hook/scheduler added |
| A21.2 | PASS | PASS | Strict shapes, forbidden input and all requested YAML constructor cases block before release/audit payload |
| A21.3 | PASS | PASS | Real template and producer retain complete Markdown plus structured authority/scope fields |
| A21.4 | PASS | PASS | Typed public accessor, missing/unknown/error evaluator, budget, missing optional parser, source poisoning, replay and persisted-audit boundary |
| A22.5 | FAIL | FAIL | Existing stale source/result/report/attempt, nonexistent result, per-leaf and no-change tests pass; Git mode/type changes retain clearance, F04 |
| A22.6 | BLOCKED | BLOCKED | Real Git isolation/fan-in/conflict/recovery and declared serial/manual scenarios pass, but F04/F05 prevent package-level acceptance |
| A22.7 | OPEN / excluded | OPEN / excluded | Requires P05/P07/P08/P09 and independent integrated verification |

## Checks actually executed

All commands used the exact repaired product, except explicit old-component
red controls and Git-object comparisons. Tests were sequential, with temporary
synthetic homes/state/audit roots, bytecode disabled, no user/system Git config or
fixture hooks, and no network or dependency installation. Existing Python 3.11,
Git Bash, PyYAML 6.0.3 and the specifically approved jq 1.8.2 were used; jq affected
only the test process PATH.

| Reviewer execution | Actual outcome |
|---|---|
| `python -B tests\unit\swarm-contract.py` | 46 tests PASS |
| `python -B tests\integration\swarm-workflow.py` | Mapped/legacy and genuine temporary Git-worktree scenarios PASS |
| `python -B tests\integration\brief-forge-boundary.py` | 15 tests PASS |
| `bash tests\unit\brief-forge-evaluator-runs.sh` | All six retained scenarios PASS |
| `bash tests\unit\envelope-schema-validates.sh` | All six retained legacy scenarios PASS |
| `bash tests\shape\adr-numbers-unique.sh` | PASS; 27 unique ADR numbers and matching titles |
| `bash tests\shape\swarm-contract.sh` | PASS; workflow/source/authority assertions |
| `bash tests\shape\brief-forge-handoffs-canonical.sh` | PASS |
| Actual `bin\li-work-artifacts.py` against Universal `work.json`, Python `-B -S` | PASS; original approved map retained |
| Independent F01/F02/F03 red/green probes | Repairs verified as detailed above |
| Independent real-Git mode/type probe | DEFECT REPRODUCED: stale review remains `complete`, public `verify` exits 0 |
| Independent unmapped-package prerequisite probe | DEFECT REPRODUCED: completed P0 blocks P1 and close; equivalent T0 prerequisite passes |
| Git-object inventory, ancestry and authority comparisons | PASS within the preservation scope below |
| `git diff --check e74849d dca635d` and repair-range whitespace check | PASS |

The genuine Git integration test creates separate worker/result/report/review
commits and isolated worktrees, checks actual actor diffs, preserves pending review
after interruption, performs serial fan-in with ancestry assertions, rejects a
non-ignored scoped addition and exercises a merge conflict without losing source
work. Its actor/report/review records are synthetic fixtures, not actual independent
model/human reviewers. These passing checks coexist with F04/F05; neither suite
covered those discriminating cases.

## Preservation and changed surfaces

Required main `28061e434be455ca02f135b73244eaf4f73f3a69`, original Swarming
`275a35447c4ad271e05816ade43ac48f1acec24f`, `e74849d`, `8ea0fc4` and `02be6cb`
are retained ancestors. Historical merge parents remain
`21261f1ff76be994246060a7817924f2893f2454` and
`275a35447c4ad271e05816ade43ac48f1acec24f`.

The 76 inventory rows still match the original source-delta path set, with every
retained destination/mode present. All 23 historical Swarming plan/brief/report/review
paths are byte/mode-identical to the accepted merge. A final exhaustive comparison
of the existing current memory, Universal audit and Universal-plan authority prefixes
found 32 tracked paths unchanged, excluding only the two authorized P04 child reports.
Selected enterprise/helper/hybrid/generated sources also remained unchanged. Main
ADR-0026 is identical; the original Swarming ADR body from `## Context` onward is
preserved under ADR-0027. No historical PASS or outcome was rewritten or fabricated.

These are preservation observations, not a claim that all 76 source files are
unchanged or that all inherited defects are fixed. F04/F05 concern the subsequent
component implementation and do not revoke the bounded historical merge acceptance.

The exact eight-path repair is confined to the two contract libraries, their two
focused test files, Swarm skill, two concept documents and `reports\P04.md`.
The full 30-path reviewed component range is:

```text
.claude\decisions\0027-first-class-swarming.md
.claude\plans\universal-implementation\reports\P04-preservation.md
.claude\plans\universal-implementation\reports\P04.md
bin\li-envelope-replay
bin\li-envelope-validate
bin\li-swarm.py
docs\concepts\brief-forge.md
docs\concepts\envelope.md
docs\concepts\swarming-work.md
lib\brief-forge-evaluators.sh
lib\brief-forge.sh
lib\envelope-requirements.txt
lib\envelope-schema.yaml
lib\envelope_contract.py
lib\swarm-schema.json
lib\swarm_contract.py
lib\swarm_snapshot.py
scaffolding\01-foundation\templates\swarm\agent-brief.template.md
scaffolding\01-foundation\templates\swarm\agent-report.template.md
scaffolding\01-foundation\templates\swarm\agent-review.template.md
scaffolding\01-foundation\templates\swarm\charter.template.md
scaffolding\01-foundation\templates\swarm\coordination.template.json
skills\brief-forge\SKILL.md
skills\swarm\SKILL.md
tests\integration\brief-forge-boundary.py
tests\integration\brief-forge-boundary.sh
tests\integration\swarm-workflow.py
tests\shape\brief-forge-handoffs-canonical.sh
tests\unit\brief-forge-evaluator-runs.sh
tests\unit\swarm-contract.py
```

## Limitations and handoff

No whole-repository suite, fresh full consumer/enterprise suite, external advisory
scan, authenticated/native client execution or final combined-tree verification was
run in this recheck. Source preservation and actual local consumers are not substitutes
for that later host/integration evidence. Declarative actor/host/isolation references
are not independent corroboration; this report does not promote them into proof.

A22.7 remains explicitly open for P05 review/corroboration, P07 effective-profile
context/generation/digest, P08 selected-work/operation and P09 domain-result binding,
followed by coordinator-owned reducers and final integrated review. Neither this
component decision nor historical preservation acceptance closes final Swarming or
Universal delivery.

Only this review report was authored. No product fixes, shared plan/memory changes,
source-branch resets, nested agents, remote/GitHub/auth operations, private-home
inspection, global configuration/hook activation or publication were performed.
Temporary fixtures were removed. Preserve F01-F03 closures and the earlier review
refs; return F04/F05 to the original builder and request an exact repaired candidate
for a bounded recheck. The reviewer stops read-only after the report-only local
commit and MasterSession handoff.
