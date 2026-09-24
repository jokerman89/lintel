# P10 integration and repair review

**Date:** 2026-09-24. **SPEC: PASS. QUALITY: PASS. COMPLIANCE: UNVERIFIED,
clearance blocked.** Findings remaining in the reviewed scope: **P1 0 / P2 0 / P3 0**.
F-INT-2, IC-F01's observed journal-read mechanism and F-INT-4 are closed in scope.
The initial failed integration and all historical failures retain their status.

Same independent reviewer `1578dfd8-f239-4eba-989b-3c4bde3e5792`; no implementation
or merge-resolution ownership, no nested agents. This covers the original integrated
P10 content plus the exact released repair below, not subsequent unreviewed fan-in.
F01-F06/B01 and the accepted component report remain preserved at their actual sources.

## Selection and authority

| Item | Exact identity |
| --- | --- |
| Original integration | `3397311f59b74f05c732f44a6386b724b60a0b6c` |
| Original integration tree | `82d9cfdec7eed8601fc7b32af3986f10f4242c8a` |
| Integration merge | `68d322403a31a4b2eadff3281f358928929d8c3b` |
| Accepted component review | `f460eb9fdeb0e665c6a84c72b32233124e599977` |
| Initial review authority | `7b87b46045a12090ee4482b1b4cb974c39da165b` |
| Repair authority and sole product parent | `da14da230f927b4622c898159173d14d2fe7fd10` |
| Additional F-INT-4 authority | `199ddc91860b22426a7fc0894b4358b85f72226e` |
| Repaired product | `0caba6fe50be52c82763cf4c3e326ad629b1b3b1` |
| Product tree | `4bdca8735b07ea4dacdd721e318aa401142b7b45` |
| Report-only child | `d4b902594998dfa09026c1893932a10d96bbd108` |
| Child tree | `eae35722feff16dcafb4f02f9053be39516db94d` |

The reviewer checkout started at exact `f460eb9f`, detached and clean. Immutable
Git objects were exported to a separately owned 1,125-file source tree; no owner
worktree or retained shared MSYS mount root was inspected. The report-only child
changes only the owner report, whose 143,340 Git bytes have SHA-256
`4775e69b2c9ab62e7abe9a9a858621f40b504376c9c6a47782f6d15591c1c986`.
Its new section and complete report diff were read against the previously read report.

The repair changes exactly seven paths, +338/-53:

| Changed path | Reviewed change |
| --- | --- |
| `bin/li-copilot.py` | Joined-resource source preflight before planning observations. |
| `lib/managed_transaction.py` | Exact owned-journal unstable-read handling within the existing retry bound. |
| `docs/lifecycle.md` | Journal-read behavior and its limits. |
| `docs/native-installation.md` | Honest Windows Bash/PowerShell fixture coverage. |
| `tests/integration/copilot-kit.py` | One new installed-helper refusal method; all previous methods unchanged. |
| `tests/integration/universal-lifecycle.py` | Shared fixture construction and labelled Windows Bash variants. |
| `tests/unit/managed-transaction.py` | Four discriminating methods and their private sampling helper. |

Original integration evidence is sealed separately: 808 files, index SHA-256
`9fe6f941aca0dd4867d4fb2ac11ae5f62b7d91a1dfd14cbf494c96e33bfe1b48`.
The repaired export manifest SHA-256 is
`daa8a94dd3b6d6a4daf9dd347b6ffbc93e64c923d8b1c4ed55fd7315d7efa0e0`.

## Stage 1: specification

**PASS for all ten original A12 subleaves and four parents, within this selection.**

### Original integration preservation

All 1,124 initial merge paths were compared. Relative to the recorded comparison
base, 740 match both parents, 301 carry recovery-only changes, 42 carry P10-only
changes and 41 are jointly changed. No unambiguous same/single-parent content is lost.
Two merge bases exist; the retained single-base text-merge diagnostic is not a
recursive-merge conflict oracle. The coordinator's twelve textual conflicts and
the 41 joint-content paths are different measurements.

All 49 original P10 surfaces remain, with Git modes preserved. The final repair
leaves 41 identical to accepted `a2df2021`; the eight differing surfaces are the
seven paths above plus the additive `docs/client-adapters.md` union. Only `main`
and `_save_journal` change among production functions in this repair.
`context_safety`, lifecycle producers/readers, native performers, schemas and
`ADAPTER_RESOURCES`, `SOURCE_METADATA`, `JOINED_RUNTIME_RESOURCES` remain unchanged.

The five initial union files preserve their intended content. Welcome and the
runner-contract test retain recovery's catalog/footer and literal diagnostics;
pack-source-target retains P10's real lifecycle/policy controls. The adapter retains
all resource additions and its F05 observation binding, with only the released
source-preflight ordering change. All 49 initial integrated kit tests remain
unchanged; one new F-INT-2 test makes 50. The catalog is byte-identical to the tested
regeneration, with 127 skills and only the ten P10 description changes from recovery.
All 81 required source resources exist; alias and upstream-provenance payloads remain.

The seven initial shared-state choices equal recovery: evolution, MEMORY, lessons,
working-state, handoff, P10 card and plan. They drop no P10-owned file.
The earlier FAIL report `2685bd57` and accepted `f460eb9f` report remain preserved.
The specification itself is unchanged. Subsequent coordinator shared-state updates
are distinguished from product authorship.

### Released defects

**F-INT-2.** `main` now checks the existing joined adapter resources before registry
loading or target observation used for planning. Target/home validation and the
missing-transaction argument error retain their precedence. `generate` still checks
its full source closure; no inventory resource is silently optional. Independent
execution of the original removal case and new check/init/Universal-init case
produced exact clean refusals, empty stdout and preserved target/store state.
No F05 planning observation is recaptured.

**IC-F01.** The diagnosed difference is named: five captured journal reads among
222,786 disagree only on mtime within their identity samples; creation time also
changes, while device/inode/size/mode/attributes agree. Four captures match an older
same-path timestamp pair. No mismatch is recorded among 78,416 other-path reads.
The periodic external-actor interpretation is plausible, not identification of a
process or service. The review relies on the observed metadata inconsistency, not
on an unproven actor name or historical WinError5 cause.

Only `_save_journal` handles the exact unstable-read error, within the same four
retries and 0.05/0.1/0.2/0.4-second backoff shared with B01. Every accepted read is
internally stable; a stable changed state after the baseline refuses. Post-denial
instability must pass the next stable comparison before replacement. Other errors,
final-attempt failure and non-journal writes retain their behavior. The first stable
entry read defines this save's before-state; this is not protection against a change
before that baseline. `read_owned`, atomic publication and receipt validation are
not relaxed. Independent persistent-disturbance tests remain incomplete and recover
exactly through the existing explicit recovery operation.

**Checkout reconciliation.** Coordinator `756835f6` adds only
`install/directories.txt text eol=lf`. Native Git `check-attr --source` independently
confirms text/LF on the repaired candidate, versus unspecified on the original
integration. The Git directory-contract bytes remain 273 bytes, 21 LF, zero CR.
This removes the checkout-induced `audit\r` refusal without weakening path checks.

**F-INT-4.** Retained measurements show full-source Windows Bash install/check/
unchanged-reinstall at 2,366.566/436.507/1,157.003 seconds; the same full source uses
49.243/7.949 seconds for PowerShell install/check. These are host measurements under
reported load, not a whole-CI performance certification. The authorized correction
uses a labelled small source for the three Windows Bash variants, while preserving
full-source default PowerShell variants and full-source selection on other systems.
The helper extracts existing fixture construction; no assertion is skipped and
the 600-second subprocess limit is unchanged. Independent default-form execution
verified six labels and six actual installations: Bash 23 mutations, PowerShell 533
mutations, for each method. All 18 F06 refusal rows remained effective.

### Original A12 leaf matrix

| Leaf | Result and evidence |
| --- | --- |
| A12.1.a | PASS: original source/target, scaffold/doctor/health and required caller-policy controls retained; exact source refusals independently checked. |
| A12.1.b | PASS: structured profile, copied validation and pin/switch semantics unchanged; accepted evidence retained. |
| A12.1.c | PASS: roles/personas/private-source boundaries unchanged; no real-home or host-activation claim. |
| A12.1.d | PASS: F01-F04 migration/producer/reader closures unchanged; exact owned recovery remains. |
| A12.2.a | PASS: original fresh/repeated/default/classic/canonical/Git cases retained and included in the complete repaired kit. |
| A12.2.b | PASS: F05 observed-state admission retained; all 28 repaired-kit intervention rows refuse with preservation. |
| A12.3.a | PASS: initial failures remain failed; bounded journal instability and error propagation independently exercised. |
| A12.3.b | PASS: persistent-disturbance recovery, later-edit refusal, root/store binding and consumed permission independently exercised. |
| A12.4.a | PASS: bare path remains Python-free; F06 retains actual Bash and full default PowerShell coverage with honest fixture/host limits. |
| A12.4.b | PASS: alias/provenance source closure, historical aliases and truthful migration visibility retained. |

### Actual verification

Reviewer runs used the immutable repair export, a new 79-character temp parent,
allowlisted synthetic HOME/USERPROFILE/AppData/XDG/Lintel paths, PATHEXT, Git ceilings
and the explicit approved PowerShell 7 selector. Source Git identity was checked
separately. Both retry prefixes were captured. No full repository or full kit suite
was rerun by this reviewer.

| Run and actor | Outcome |
| --- | --- |
| Independent transaction unit | 19/19 PASS; 53.289 s unittest, process exit 0; source/outer equality and exact named-fixture cleanup. |
| Independent original/new F-INT-2 methods | 2/2 PASS; 426.908 s, exit 0, 51 audited/completed subprocesses; four exact context-safety refusals, source/outer equality and cleanup. |
| Independent three changed native methods, default form | 3/3 PASS; 999.024 s, exit 0; 43 audited/completed subprocesses: 21 exit 0 and 22 expected refusals; source/outer equality and cleanup. |
| Builder complete repaired kit on `0caba6fe` | 50/50 PASS, 7,744.336 s; no skips; 488 recorded invocations / 493 completed subprocesses; source seal and exact cleanup. |
| Builder F05 regression | 8/8 PASS; all 28 interventions refuse, not-ready/store-absent, only intervention changed. |
| Builder final native default-form selection | 3/3 PASS; 18 F06 rows, six labels: Windows Bash small / PowerShell full. |
| Builder final native small aggregate | 13/13 PASS, explicitly `--native-small`; not full-payload evidence. |
| Builder transaction regression | 19/19 PASS, including every unchanged B01 method and new IC-F01 controls. |
| Coordinator initial kit | FAILED: 48 pass / one F-INT-2 failure, 49 tests, outer exit 1. |
| Coordinator original light / lifecycle rerun | FAILED: original 97 failures across 14 methods; separate rerun 65 pass / three native failures. |
| Coordinator two LF native attempts | Each outer exit 1, one pass / three 600-second errors. Final `p10n1` root deliberately retained for MSYS; not inspected or removed here. |

Independent transaction output includes all 24 transient B01 combinations, three
persistent B01 recovery cases, four changed-journal refusals, eight nonretryable
cases and seven other-write controls. IC-F01 adds eight transient read cases,
bounded exhaustion, changed-content refusal, post-denial checks and real
complete/incomplete/recovered `apply_files` outcomes. These disturbances are injected
regressions, not a reproduction of the unknown external actor.

The coordinator's generated catalog/wiki receipts are verified at their original
candidate. The light run has two explicit jq skips (JSON extraction and version
parity); its exit-0 entries do not erase them. The catalog is unchanged by this
repair. No hosted Windows CI execution, whole-suite budget or live dependency
advisory result is inferred.

## Stage 2: quality

**PASS, recorded after specification PASS. P1 0 / P2 0 / P3 0.**

The complete selected integration and repair were considered for correctness,
preservation/security boundaries, performance, maintainability, coverage and
cross-artifact consistency. Source admission no longer depends on the missing
observation helper. Journal retry is limited to one owned path and a stable-state
comparison, with unchanged non-journal primitives and explicit failure/recovery.
The fixture split is the authorized measured alternative, not a silent skip,
timeout expansion or second native implementation. Original ownership, source
closure, recovery, protected prose, client and EOL contracts remain intact.

This is the same independent reviewer's repair continuation, not builder
self-acceptance and not a new claim that the initial failed integration passed.

## Limits and delivery boundary

Compliance remains **UNVERIFIED**, with clearance blocked by unresolved required-policy
source/version/applicability and live advisory freshness. It is not a product finding
or a neutral-policy waiver.

Windows PowerShell 5.1 remains denied. Actual host observations are limited to
PowerShell 7.6.6, Git Bash 5.3.15 and Python 3.11.9 where recorded. Python 3.9,
stock Bash 3.2/POSIX execution, other OSs and the unsupported long linked-Git positive
remain unverified. The earlier F06 reviewer run explicitly used `--native-small`;
that limit was already recorded, not substituted for full-source proof.

The initial WinError5, original 120/128 FAILED, stopped aggregates and older
SPEC/QUALITY failures retain their status. Four real B01 retries are recorded in
the new probe stderr, but their cause remains unestablished. The builder observer
counts only B01 notices; its zero count does not prove zero IC-F01 notices.
Independent source/native rechecks captured zero notices of either kind.

Diagnostic probes used an instrumented reader that continued after mismatch;
they are mechanism evidence, not unmodified production success runs. Their JSON
captures do not contain contemporaneous launch-source hashes or full launch
environments; those attributions remain owner-provided. The current independent
regressions have separately recorded source and process-isolation evidence.

The builder's `fint2-red-1` cleanup failed on a held synthetic home directory and
remains retained. The earlier native-unit product exit 0 / private cache-wrapper
exit 1 distinction remains. This review retains one private receipt-parser
failure caused by a tuple/list comparison; correction reused unchanged copies
and did not rerun product work. The new empty reviewer temp parent is retained
intentionally; no shared mount probe or broad cleanup was performed.

The repair parent predates later `da5a599b` P09 test-only extraction. That join and
SAME447's accepted two-caller evidence are preserved separately, not claimed to be
present in `0caba6fe`. Subsequent test/shared-state reconciliation and P13 consumer
fan-in remain coordinator-owned. This review changes no A12 checkbox, A13,
shared ledger, product file, policy or external system.

## Evidence

Current private evidence:
`C:\Users\jokerman\.copilot\session-state\1578dfd8-f239-4eba-989b-3c4bde3e5792\files\p10-integration-0caba6fe-independent`.

Key records: `repair-intake.json`, `repair-scope.json`,
`repair-original-surface-map.json`, `repair-union-preservation.json`,
`builder-evidence-join.json`, `repair-diagnostic-assessment.json`,
the three independent assessment/invocation/result sets, and sequential
`integration-spec-stage.json`, `integration-quality-stage.json`,
`integration-compliance-stage.json`. The final evidence index and delivery
receipt bind this report's Git bytes and its single report-only commit.
