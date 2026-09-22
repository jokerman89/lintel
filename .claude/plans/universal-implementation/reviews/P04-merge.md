# P04 independent historical merge review: e74849d

**Date:** 2026-09-20
**Reviewer:** independent `lintel-reviewer`, Universal merge review session
`cda1fd76-c5c2-473d-8af3-251c19b178b0`.
**Verdict:** PASS for the early merge checkpoint, not final P04/A22 acceptance.
**Stage 1 (preservation/spec):** PASS. Completed before Stage 2.
**Stage 2 (integration quality):** PASS within the bounded merge-review scope.
**New findings:** P0 0, P1 0, P2 0, P3 0.

No merge-introduced loss, enterprise regression, or false current-acceptance claim was
identified. The reviewer did not implement this merge or repair any product finding.
Known SW-01 through SW-06 and A21 work remains pending; passing the existing tests does
not close those findings. This is neither A22.7 nor final Universal integrated review.

## Exact reviewed revisions

| Role | Immutable revision |
|---|---|
| Reviewed merge/head | `e74849db6b33c7b93baadb86206009cb9f9eb6d5` |
| First parent / Universal baseline | `21261f1ff76be994246060a7817924f2893f2454` |
| Second parent / historical Swarming | `275a35447c4ad271e05816ade43ac48f1acec24f` |
| Latest local main required by this card | `28061e434be455ca02f135b73244eaf4f73f3a69` |
| Parents' common ancestor / source-delta base | `e9911fcd448dc632bf2752c69304d2be80b7aa65` |

The checkout stayed at the reviewed merge throughout inspection and testing. A subsequent
commit containing only this report is evidence about **e74849d**, not a new product
snapshot reviewed here. No moving builder branch was used as a test target.

Authority read: repository entry instructions, Copilot adapter and canonical review
workflow; relevant memory and ADRs; Universal spec, plan, P04 card and handoff; the
original audit's `reviews\swarm.md` and `swarm-preservation.md`; and the child's
`reports\P04.md` and `reports\P04-preservation.md`.

## Stage 1: preservation and specification

| Checkpoint obligation | Result and evidence |
|---|---|
| A22.1.a: preserve ancestry | PASS. The merge has exactly the two supplied parents. Both parents and main `28061e4` pass `git merge-base --is-ancestor` against the reviewed head. Their common ancestor is the recorded `e9911fc`. |
| A22.1.b: retain main's protocol and hybrid model | PASS. Both-parent diffs preserve main's package execution, per-leaf acceptance, aggregate-risk review, mandatory-control boundaries and blocked-work recovery. The four generated startup protocol blocks match their canonical source. |
| A22.1.c: retain enterprise helpers and work selection | PASS. Main's changed paths were compared as Git objects; substantive reconciliations are listed below. Native/Spec Kit maps, actual PLAN/BUILD/RESUME snippets and isolated consumer installation checks pass. |
| A22.1.d: preserve all 76 source-delta paths/intents | PASS. The preservation table's unique source paths exactly equal `git diff --name-only e9911fc 275a354`. All destinations exist, all source file modes are retained, and all 76 I/R classifications match the actual comparison: 62 source-identical after LF normalization and 14 reconciled. |
| A22.2: resolve the decision-number collision | PASS for this checkpoint's renumbering/reconciliation. Main ADR-0026 is byte-identical to the first parent; there is one ADR-0027 and no second ADR-0026. The original swarm ADR body from `## Context` through EOF is byte-identical at its new destination. This does not certify the pending SW-02 parser/package implementation. |
| Preserve honest history and coordinator authority | PASS. Existing Universal/audit/memory content is unchanged, historical lane evidence is unchanged, and the work index explicitly separates current Universal authority from historical Swarming authorization. |

### Source preservation and conflict reconciliation

The first-parent delta has 78 paths: the 76 mapped source destinations, including the
ADR rename, plus the two new P04 implementation/preservation reports. There are no
other changed paths in that delta.

All 17 historical charter/topology/brief/report/review entries, including the two
directory placeholders, are byte-identical Git blobs to `275a354`. The historical
design's ADR link and historical-status qualifier are its only Markdown reconciliation;
no brief, worker result, review outcome or actor identity was rewritten. Existing
historical PASS claims remain evidence of their original attempt, not this merge.

The 14 reconciled source paths are accounted for as follows:

| Paths | Retained intent / resolution |
|---|---|
| `.claude\decisions\0026-first-class-swarming.md` -> `0027-first-class-swarming.md`; `.claude\plans\swarming-work\design.md` | Preserve the original decision/body and its Git origin; keep main's ADR-0026 authority; point historical design at the reconciled decision. |
| `.claude\plans\todo.md` | Preserve source Swarming navigation and prior gate context as history while explicitly selecting Universal as current. |
| `bin\li-copilot.py`, `bin\li-swarm.py`, `bin\li-work-artifacts.py`, `lib\swarm_contract.py` | Runtime bodies remain source-identical; changes relative to the Swarming parent are decision annotations. Relative to the first parent, work-map validation gains the shared optional swarm parser and the adapter gains its resource preflight. |
| `docs\README.md`, `docs\architecture.md` | Retain both enterprise and swarm discovery, plus main's corrected operator-home/active-pack explanation. |
| `docs\the-cycle.md`, `skills\build\SKILL.md`, `skills\plan\SKILL.md` | Keep main's short leaves and bounded packages; add opted-in, attributable candidate lanes without restoring old per-leaf dispatch as the default. |
| `skills\resume\SKILL.md` | Keep selected-work authority, target-relative state and job-scope fixes; add committed swarm recovery without initiative selection by recency. |
| `skills\CATALOG.md` | Preserve current package/profile descriptions and add swarm discovery; generated check passes. |

Of the 118 paths changed on the first-parent side since the common ancestor, 110 are
retained exactly. The other eight are `todo.md`, `docs\README.md`,
`docs\architecture.md`, `docs\the-cycle.md`, `skills\CATALOG.md`, and the BUILD,
PLAN and RESUME skills. Their both-parent hunks were reviewed directly. They retain
main's behavior while adding swarm navigation/execution guidance, rather than restoring
old branch copies.

All 32 pre-existing paths selected under `.claude\memory\`,
`.claude\plans\universal-implementation\` and the Universal audit directory are
byte-identical to the first parent. The child's merge does not complete coordinator
checkboxes or replace the current work map/handoff.

Key exact-head anchors:

- `.claude\plans\todo.md:3-16`: Universal remains current; older Swarming authorization
  and planning claims are explicitly historical.
- `.claude\decisions\0027-first-class-swarming.md:3-26`: original decision identity,
  hybrid precedence and pending cross-package binding are explicit.
- `skills\build\SKILL.md:74-133`: sequential package default, authoritative member
  leaves, aggregate review depth and isolated swarm candidate handling coexist.
- `.claude\plans\universal-implementation\reports\P04.md:3,28-34`: product repairs,
  independent package review and shared-contract binding are not claimed complete.
- `.claude\plans\universal-implementation\reports\P04-preservation.md:106-123`:
  checkpoint checks are separated from known defect acceptance and final integration.

## Stage 2: integration quality

No new actionable merge-regression finding was found. The optional map fields remain
additive; the original maps still validate. The installed-source parser is shared by
the map reader and swarm CLI instead of being duplicated. The CLI remains a read-only
validator/status/scope/evidence helper, not a scheduler or automatic dispatcher.

Focused execution preserves the actual enterprise workflow snippets, including explicit
map selection, original Spec Kit tasks, target state, scope/resume ownership, inherited
policy and returning a blocked package to BUILD. Consumer tests preserve project prose
and memory, render the complete protocol, include the swarm entry/resources, and reject
missing dependencies before target writes. These are local mechanical observations,
not proof of model-driven or client-side execution.

The P04 checkpoint's recorded baseline test results were reproduced. Its preservation
claims match the Git comparisons. `reports\P04.md:12` leaves the merge SHA to a
post-commit record; the immutable revision table above supplies that identity explicitly
without inventing historical outcomes.

## Checks actually executed

All runs set `PYTHONDONTWRITEBYTECODE=1`; direct Python invocations also used
`python -B`. Bash scripts ran under Git Bash with a process-local
`python3() { python "$@"; }` function, using the existing Python 3 interpreter rather
than installing or changing a host interpreter. All fixture writes were confined to
test-owned temporary directories.

| Command / check | Observed result |
|---|---|
| `git merge-base --is-ancestor <first-parent/second-parent/main> e74849d`; `git merge-base 21261f1 275a354` | All three ancestry checks exit 0; common ancestor matches `e9911fc`. |
| Read-only Python/Git inventory over `diff --name-only`, `ls-tree -r -z` and `show <rev>:<path>` | 76/76 source destinations and modes; 62 I / 14 R labels correct; 17/17 historical evidence entries and 32/32 protected current entries unchanged; original ADR body retained. |
| `python -B bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; current approved native map, without swarm opt-in. |
| `python -B bin\li-work-artifacts.py --repo . --map .claude\plans\swarming-work\work.json` | PASS; preserved historical approved swarm map. Structural validation only, not renewed authorization. |
| `python -B bin\li-instructions.py check` | PASS; four synchronized entry blocks. |
| `bash tests\shape\adr-numbers-unique.sh` | PASS; 27 unique numbers, matching filename/title numbers. |
| `bash tests\shape\build-workflow-contract.sh` | PASS; structural BUILD checks. |
| `bash tests\shape\swarm-contract.sh` | PASS; workflow links, opt-in, shared parser and task-authority shape. |
| `python -B tests\unit\swarm-contract.py` | 20 tests PASS, no skips. |
| `python -B tests\integration\swarm-workflow.py` | PASS; temporary map -> candidate waves -> scope/evidence -> close, plus legacy-map fallback. |
| `bash tests\unit\work-artifacts.sh` | PASS; native/Spec Kit compatibility and invalid/missing artifact cases. |
| `bash tests\integration\enterprise-workflow-snippets.sh` | PASS; real selected-work, scope/resume, inheritance and BUILD ledger snippets. |
| `python -B tests\integration\copilot-kit.py <eight selectors below>` | Eight focused tests PASS, no skips; real local adapter processes and temporary consumers. |
| `python -B bin\li-catalog.py --check` | PASS; catalog matches canonical frontmatter. |
| `python -B bin\li-copilot.py check --target . --source .` | PASS; 19 managed files, repository source; explicitly no live-host validation. |
| `git diff --check 21261f1 e74849d` and `git diff --check e9911fc 275a354` | Both exit 2 for the same two inherited blank-at-EOF notices: historical `discover.md:48` and `work.json:12`. Not a merge-created regression; no historical files changed to silence them. |
| `git status --short --untracked-files=all`; tracked equality against `e74849d` before report creation | Clean; exact reviewed HEAD retained. No repository runtime/cache output found in the checked locations. |

The eight `CopilotKit` selectors were:

```text
CopilotKit.test_fresh_portable_clone_and_idempotence
CopilotKit.test_swarm_wrapper_and_complete_source_resource_inventory
CopilotKit.test_missing_mandatory_swarm_dependency_refuses_before_writes
CopilotKit.test_preserves_existing_project_instructions_and_memory
CopilotKit.test_full_protocol_is_portable_and_project_prose_survives_update
CopilotKit.test_pack_resolver_uses_bundled_code_and_project_state
CopilotKit.test_legacy_scaffold_renders_full_protocol_from_shared_source
CopilotKit.test_bundled_scaffold_prefers_installed_source_root_over_runtime_home
```

## Boundaries and remaining acceptance

- SW-01..06 and A21 are acknowledged existing/pending work, not new regressions or
  fixes accepted by this review. A22.3-A22.7 remains outside this checkpoint's pass.
- The existing swarm integration test has no Git repository and does not prove real
  worker isolation, attributable fan-in or recovery after an actual interrupted merge.
  A22.6 and later shared P05/P08/P09 binding still require their own evidence.
- No full strict suite, CI, complete dependency/security audit, paid benchmark or
  authenticated client/model matrix was run. Local consumer packaging is not native
  Copilot, Claude, Codex, desktop-host or enterprise-policy acceptance.
- Historical lane reports were verified unchanged, not independently re-certified.
  Generated checks run here do not replace final coordinator regeneration after fan-in.
- Neutral advisory baseline only: no personal profile, private pack, live hook, remote,
  credential or production operation was invoked. No GitHub/network/auth calls or
  additional agents were used.

**Only authored repository file:** this report,
`.claude\plans\universal-implementation\reviews\P04-merge.md`.
No product, common plan/state, memory, historical evidence or source branch was edited.
The checkpoint is suitable as the preserved early merge base for continued authorized
work; final package and integrated human/independent review gates remain open.
