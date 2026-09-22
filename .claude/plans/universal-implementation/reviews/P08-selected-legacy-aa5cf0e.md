# P08 selected legacy provider compatibility review

**Scoped SPEC: PASS. Subsequent QUALITY: PASS.**
Findings: **P1 0 / P2 0 / P3 0**. The released named-singleton correction is
ready for exact-source provider dependency consumption. P04's composed caller
verification remains a separate owner gate; this is not whole-P08 acceptance.

## Immutable scope and report provenance

| Item | Exact identity |
|---|---|
| Reviewed recovery commit | `aa5cf0e408604dbe8f5b47df8b453622a0db5f13` |
| Candidate parent | `27b43e3066160f9b555a10b267edeafd43bc97bd` |
| Independent reviewer | `9dbf0a9b-750d-45c2-968c-41a5acb11c92` |
| Coordinator | `88aecc43-40f9-41d4-8947-6c2fb0a55481` |
| Preserved detached reviewer/report parent | `e98e7da8d50a8119064507f8b6d3597f0fbf5e57` |
| Exact export manifest SHA-256 | `271c32e8ab19f17158516c79d680a3b4e0041c62401ada5f8667b4c813c830a6` |
| Private evidence index SHA-256 | `59c0c754b5015817accffc462d5d864f5fc329f53a4ff7d06125f842a0d51259` |

Authority is the candidate's final **Selected legacy singleton recognition**
section in `packages/P08.md:494-525`. Only the affected A08.3.a refinement
was reopened. The reviewer did not implement this correction.

This is a **clearly separate exact-export review**. The reviewer checkout was
clean and detached at intake and is not switched to the recovery product.
The report-only commit preserves that existing history; it must not be mistaken
for a product child or used as the reviewed source revision. Test execution used
only the separately sealed raw Git export of the exact recovery commit above.
No resets, source normalization, native re-pinning or product imports occurred.

The candidate changes exactly six paths: `bin/li-work-artifacts.py`,
`tests/integration/universal-work-lifecycle.py`,
`tests/integration/work-context-provider.sh`, `docs/spec-kit.md`, and the
existing P08 card/plan context. No P04 caller, shared parser/schema or provider
dependency is modified. This reviewer authors only this committed report and
private runtime evidence.

| Reviewed component | Git blob | Mode |
|---|---|---|
| `bin/li-work-artifacts.py` | `281cd8f4ce6c5652b3739fd8c54d474b79a73421` | `100755` |
| `tests/integration/universal-work-lifecycle.py` | `33bdbbea78d84ccd66c9e8c276df7539daa76e68` | `100644` |
| `tests/integration/work-context-provider.sh` | `fb89e1cc8dcdb6cfe42cb407e4adeb50f4785f8f` | `100755` |
| `docs/spec-kit.md` | `870136ec41602fe17a076b74e62038b851f7960b` | `100644` |

All 1,024 exported files match their Git blob bytes; the four components above
are LF with no CRLF in this committed export. That is not a claim about the
working EOLs of the frozen native fixture or another workspace. Both the complete
source file inventory and every exported file hash remain unchanged.

## Stage 1: selected specification

Read the complete affected provider, work-map contract and updated Spec Kit
documentation; inspected the relevant P04 task/package/coordination parser,
P03 bounded selector/budget, P05 acceptance binding, and actual test fixtures.
All 39 pre-existing lifecycle test method ASTs are unchanged; exactly the three
released methods were added. Eleven shared dependency blobs/modes match the
candidate parent, including P03/P04/P05 helpers, workflow/state and both imported
fixture modules. No circular or independent replacement parser was introduced.

| Released obligation | Disposition | Source and independent evidence |
|---|---|---|
| Read explicit named singleton `core` without binding/approval | PASS | `bin/li-work-artifacts.py:102-108`; new named method plus actual CLI probe; returned original core text, package membership and incomplete status |
| Reuse validated coordination and P04 task/package APIs | PASS | Provider lines 72,102-108; `swarm_contract.py:473-632,788-810`; actual CLI packages equal the shared P04 result |
| Include coordination once in bounded manifest | PASS | Provider lines 80-91; duplicate warming remains one file; exact five-file/computed-byte limit succeeds and one-file/one-byte-short bounds refuse |
| Preserve ordinary IDs and unrecognized prose | PASS | Provider lines 108-112; original selected-map case, unselected Overview/core prose case, and P04 flat/phased/tree/Spec Kit/package regressions |
| Keep DRAFT inspection read-only and non-clearing | PASS | New DRAFT method and CLI success with null binding/source-status-only; explicit DRAFT binding exits 1 with no stdout |
| Refuse wrong selected map/backpointer | PASS | Provider lines 75,102-105 and shared validator; actual existing wrong map and incompatible backpointer yield specific `work_map.mismatch`/`work_map.coordination` errors, no writes |
| Preserve optional actual P05 binding | PASS | Provider lines 113-122; retained binding/progress test and named APPROVED CLI binding equal actual `bind_work` inside the verified synthetic child |
| Preserve no-write and advisory budget behavior | PASS | Before/after fixture manifests, retained capacity/headroom controls, unchanged source seals; `release_clearance` stays false at lines 128,136 |

The independent CLI's selected manifest has exactly five files and **1,138
actual bytes**; coordination contributes 710 bytes once. This is the observed
probe fixture, not a hardcoded product budget. The separate new regression
checks its own computed exact bounds, including both refusal thresholds.

The scoped SPEC PASS is recorded before quality in private `spec-stage.md`,
SHA-256 `0a96749f27ccb57fefae430b9fa654cd91603781b8859cc377e5e139d8d076c2`.
No mandatory selected provider control remained failed or unverified when
quality began. This does not close unrelated A08 parent or native criteria.

## Independent commands and outcomes

Private invocation entry: `.claude\runtime\p08-selected-legacy-review\invoke.ps1`.
Each command constructed a fresh allowlisted child environment and completed
effective-path/Git-discovery preflight before invoking the actual source.

| Actual invocation | Selection | Literal outcome | Command / unittest seconds |
|---|---|---|---|
| `-Mode run -Case n01` | Three new plus five retained provider methods, through Bash | 8 tests, OK, exit 0, no skips | 5.437 / 3.145 |
| `-Mode run -Case p04` | Three existing P04 parser/coordination compatibility methods | 3 tests, OK, exit 0, no skips | 1.812 / 0.981 |
| `-Mode run -Case i01` | Two finite independent CLI/actual-binding/refusal probes | 2 tests, OK, exit 0, no skips | 7.110 / 6.274 |
| `-Mode quality` | Immutable parent-to-candidate `git diff --check` | exit 0 | retained receipt |

The exact n01 payload ran in `bash --noprofile --norc -s`:

```bash
exec "$LINTEL_PYTHON" "$LINTEL_SOURCE_ROOT/tests/integration/universal-work-lifecycle.py" --root "$LINTEL_SOURCE_ROOT" -v \
  WorkSelectionTests.test_named_swarm_singleton_uses_selected_coordination_without_acceptance \
  WorkSelectionTests.test_selected_coordination_is_counted_once_and_cannot_switch_initiatives \
  WorkSelectionTests.test_ordinary_heading_does_not_become_a_task_without_explicit_selection \
  WorkSelectionTests.test_explicit_map_original_ids_and_no_writes \
  WorkSelectionTests.test_manifest_measures_selected_and_warming_bytes_once \
  WorkSelectionTests.test_budget_matches_reported_capacity_boundary_without_a_default_cap \
  WorkSelectionTests.test_binding_uses_p05_and_original_mapped_task_progress \
  WorkSelectionTests.test_missing_selected_artifact_not_hidden_by_other_initiative
```

The command's recorded stdin has those same arguments on one line, preceded
by `set -euo pipefail`. The existing provider entrypoint hardcodes all 25 methods;
it was inspected, not relabeled as this targeted eight-method execution.

The p04 command invokes the unchanged `tests/unit/swarm-contract.py` with
`-v` and these exact selectors:

```text
SwarmContractTests.test_swarm_work_map_fields_are_atomic_and_point_back
SwarmContractTests.test_current_flat_phased_tree_and_spec_kit_task_formats
SwarmContractTests.test_packages_reference_unchanged_leaves_and_review_depth
```

The i01 command invokes the reviewer-owned `selected_probe.py` with Python
`-I -S -B`, the exact exported source and its own evidence directory. Its two
methods are `SelectedLegacyTests.test_named_cli_draft_and_actual_binding` and
`SelectedLegacyTests.test_existing_wrong_map_and_backpointer_refuse`.
They execute six actual provider CLI calls: APPROVED inspection, explicit
binding, DRAFT inspection, DRAFT binding refusal, existing wrong-map refusal,
and wrong-backpointer refusal. Expected negative CLI exits are 1 with empty
stdout and explicit errors; they are not mislabeled successful product calls.
Direct P04/P05 comparisons execute inside the same verified child environment.

Coordinator-reported RED3/two failures, GREEN6 and full-provider25/219.954s
remain separately attributed builder evidence. They were not rerun or counted
as this reviewer's results. No broad/full suite or native case was executed.

## Isolation and preservation

All execution and output use reviewer-owned `.claude/runtime/p8legaa5x/`.
The launcher clears inherited environment and reconstructs only the intentional
system/tool bindings and synthetic HOME, USERPROFILE, HOMEDRIVE/HOMEPATH,
AppData, XDG, temp, cache, LINTEL_HOME, Claude and Gstack roots.
No inherited Lintel/profile/session, Git, BASH_ENV/ENV or Python redirects are
retained. PATHEXT is explicitly `.COM;.EXE;.BAT;.CMD`.

Before each runner, actual resolved pack/pointer/profile/audit/jobs/registry/
state/session/source paths and Python home/temp were checked inside this
fixture. Actual Git discovery rejects an uninitialized nested directory with
exit 128 while correctly discovering an initialized child. The ceiling prevents
accidental discovery of the reviewer repository. Hooks/templates/config remain
synthetic and empty, with command-local settings only; no global change.

Environment, argv/stdin, stdout/stderr hashes, exits and timings are retained per
invocation under `n01/`, `p04/` and `i01/`. CLI probes additionally retain exact
before/after target manifests and the actual process environment for direct
binding. Temporary fixture cleanup completed with no residue; the two named
probe fixtures are intentionally retained as private evidence, not hidden
cleanup errors. Full source inventory/hash verification shows no executing
source or test modification, including no new runtime file in the export.

The frozen `70469296` native source, original f2 workspace, native contexts and
prior report histories were not changed, re-pinned or retested. shell27 and q02
remain INVALID/excluded; this new inside-child binding evidence does not
rehabilitate them. Real-home effects remain unknown and were not inspected,
cleaned or rolled back.

## Stage 2: scoped quality

Quality began only after recorded scoped SPEC PASS, at
`2026-09-22T20:31:40.160911+00:00`, and concluded PASS at
`2026-09-22T20:36:20.586244+00:00`.
The affected provider, complete patch, new regression logic, runner selection
and direct documentation were reinspected. P1 0 / P2 0 / P3 0.

The correction derives recognition hints from authoritative validated package
membership instead of parsing heading names independently or inventing P05
approval. Required coordination is accounted for through the existing bounded
selector. Wrong identity is a visible error rather than a fallback to another
initiative. Non-Swarm fallback and optional acceptance-binding code remain
separate. The unchanged shared contracts retain ownership of their semantics.

Regression coverage distinguishes DRAFT read from approval, literal source IDs
from prose, and exact byte/file limits from approximate success. The private
existing-map probes additionally demonstrate that refusal is not merely a
missing-file error. No new dependencies, source/schema migration, hidden
mutation or unnecessary abstraction is introduced. Documentation matches the
observed interface. No actionable quality defect was found within this scope.

## Remaining gates

This supplies the requested bounded independent provider acceptance for exact
commit `aa5cf0e408604dbe8f5b47df8b453622a0db5f13` only. P04 must still run its
composed caller after consuming that correction; this review did not import or
validate an uncommitted P04 caller. An unchanged function or passing source
fixture is not evidence of native discovery/orchestration or a live workflow.

No whole-P08 selected SPEC/QUALITY, A08 parent, semantic/native, A13.1/.2/.4,
P10/P14 or release gate is closed. Prior partial findings, deferred controls,
incident distinctions and native host/actor limitations remain as recorded.
The nine phases are unchanged; resume remains a utility. No PLAN/BUILD/SHIP,
publication, hook activation, real-home mutation or new policy authority is
granted by this report. Shared plan checkboxes are left to the coordinator.
