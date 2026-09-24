# P10 F-INT-5 independent review

**Date:** 2026-09-24. **SPEC: PASS. QUALITY: PASS.**
**Findings: P1 0 / P2 0 / P3 0. COMPLIANCE: UNVERIFIED; clearance remains blocked.**

Same independent reviewer `1578dfd8-f239-4eba-989b-3c4bde3e5792`, distinct from
builder `5ea6c88c-68c1-4712-8f55-adecdfe0061f`. No implementation ownership or nested
agents. This accepts the bounded F-INT-5 test-only repair, not a new whole-P10,
P08 integration, hosted-CI or release verdict.

## Immutable selection

| Item | Verified identity |
| --- | --- |
| Authority and sole product parent | `1cc174cb9e8e7e0b7febf8d61469563858915b76` |
| Test-only product | `b7555ca347a11af83027c968df39310efd48c600` |
| Product tree | `199c2b8005e2f629e065a99d5e766123f787dfc1` |
| Report-only child | `b7cf10efd668f7400ecfa4eb65c055cce8a4c25c` |
| Child tree | `43a0c72be11fb1e481d4ff21fdcdd830c680c90a` |
| Changed test blob | `030a8ee22df58b2a544250533770d7fda5667c95` |
| Test Git-byte SHA-256 | `7b477cdf51722b763d7af464aa2fc1526b70e48418cb9e1e49fbefc74b96a69d` |
| Owner report Git-byte SHA-256 | `a58da17d32855a5c367a33e3b3202e472946288d07685cde03b80cbf46b1987c` |

The reviewer started at `9ca6402a095c48818ece2affad297324feeb31ca` on
`review-p10-integration-0caba6fe`, clean. The owner worktree was not inspected or
changed. Review used an independent export of 1,134 immutable Git blobs, with
manifest SHA-256
`7e24b38127fbf067368413d4e2d66022bd845783767d9daf7ccf119c6032bf81`.
Every executed selection verified that source before and after execution.

The product changes only `tests/unit/managed-transaction.py`, +208/-5,
53,658 Git bytes. The child changes only the owner report: 154,432 bytes,
2,227 lines. Both commit parents, exact scopes and required trailers match.
`lib/managed_transaction.py`, `lib/context_safety.py`, `lib/native_paths.py`,
`bin/li-snapshot.py` and the unit shell wrapper equal their accepted `f740141e`
blobs. No runtime, installer, dependency manifest, ownership contract or wrapper
is changed.

Authority is the complete P10 card section "Integration finding F-INT-5 and
test-only repair release." The mapped spec/plan, ADR-0030, prior review and
current isolation lessons remain binding. The affected preservation controls
are A12.2.b and A12.3.a/b; the other accepted A12 leaves are retained, not rerun
or relabeled. The earlier 19/19 evidence and `9ca6402a` keep their original scope.

## Stage 1: specification

**PASS**, recorded before QUALITY at 16:20:28 +02:00.

All 19 original test methods remain. Eighteen have identical function ASTs;
the remaining method gains the declared injection marker and shield-reread
exclusion. Existing assertion source bytes, exact product sleeps/notices,
failure identities and recovery expectations are retained. One new method
adds six explicitly simulated shield scenarios.

The shield's placement preserves fault attribution. Replacement injections
wrap it; their deliberate failures still reach the product unchanged. The
two helpers that deliberately change a file during a read increment every
active shield's injection counter. A marked read refusal is not absorbed.
Shield rereads do not consume the helpers' product-read counters.

The shield has a separate eight-retry budget and captured real sleep function,
with delays totaling 6.37 seconds per exhausted call. It filters replacement
WinError 5/32/33 by synthetic target root and read failures by the exact
unstable-read message, root and unchanged injection count. Unsupported failures
propagate. Exhaustion raises an explicit `AssertionError` subclass chained to
the host error, outside the product's retry handlers. Absorptions and final
counts are visible as JSON.

Independent evidence confirms both reported failure points, including both
possible branches behind Log A's first sleep. No product retry limit or
assertion was relaxed to obtain GREEN.

| Independent selection | Actual result |
| --- | --- |
| Baseline / candidate, journal denial in `other-result` | RED: exit 1, the exact unexpected-sleep assertion. GREEN: exit 0, one replacement absorption. |
| Baseline / candidate, journal read #2 identity shift in `other-result` | RED: exit 1, the same assertion. GREEN: exit 0, one read absorption. |
| Baseline / candidate, denial after four staging-check disturbances | RED: exit 1, WinError 5 at the stated subtest. GREEN: exit 0, one replacement absorption; all four product delays/notices remain. |
| Persistent host denial on the candidate | Expected exit 1: nine denials, eight absorptions, one unabsorbed event and `HostTransientExhausted`. No false pass. |
| In-memory mutation removing the injection-mark guard | Expected exit 1: four actual IC-F01 methods, eleven assertion failures. A shield that swallows deliberate faults is detected. |
| Complete unmodified candidate unit file | **20/20 OK**, no skips; 66.590 s unittest / 67.094 s process, exit 0. Real-host summary: absorbed 0, unabsorbed 0. |

The full run includes 24 B01 transient combinations, three persistent recovery
cases, eight nonretryable/non-Windows branch cases, four changed-journal
refusals and seven other-publication controls. It also retains eight IC-F01
transient cases, bounded exhaustion, changed-content refusal, both post-denial
cases and complete/incomplete/recovered apply behavior. All six new simulated
shield scenarios ran. These are injected controls, not proof of another OS or
the unidentified real actor.

Each Python test parent and child started with a cleared, recorded environment
before imports. HOME, USERPROFILE, AppData, TEMP/TMP, XDG, Lintel
pack/pointer/profile/registry/audit/state/recovery paths were synthetic.
Inherited selectors, Git redirects and shell startup variables were not used.
Git identity reads were separate from product execution, with command-local
settings and checkout-equivalent CRLF handling. No configuration write occurred.

All nine accepted independent selections preserved their outer fixtures and
cleaned their exact temporary consumers/stores, including expected failures.
The invalid first mutation attempt was also empty. Afterward, 106 verified
empty execution directories were removed individually; zero files were
deleted. Evidence and the immutable source remain retained.

### Owner evidence, separately attributed

The frozen index SHA-256
`52157bb37cea19a0dc34db8e4ec95c76498521d3f42c4bc4d260c9d21a02147f`
and 98 referenced run/harness files were verified and copied read-only.
All 26 recorded outcomes and launch environments were checked. Final test
checkout hash `e349763d...943f` is exactly the CRLF form of the reviewed Git
bytes; relevant recorded runtime hashes likewise match their immutable bytes.
The simulator was read and places faults beneath test imports and injections.

Five consecutive owner full-file runs and four additional concurrent runs
each report 20/20, with zero real absorptions. Their sequential/concurrent
attribution is preserved; they are not reviewer executions. Owner RED,
negative and mutation failures remain failed. The seven pre-freeze runs are
superseded only by the corresponding final-byte runs, not erased.
The owner's native-path module launch hash was not recorded, and its cleanup
claim is report-based; no owner live fixture was inspected. The independent
runs separately bind that dependency and their actual cleanup.

## Stage 2: quality

**PASS**, recorded after SPEC at 16:22:01 +02:00.
**P1 0 / P2 0 / P3 0.**

The complete one-file delta was reviewed for correctness, error propagation,
preservation, performance, maintainability and coverage. The shared shield and
single marker mechanism avoid divergent accounting patches per test. Cleanup
restores patches before deleting fixtures. The bounded failure path cannot
fall through to a success-shaped result, and the mutation control demonstrates
that unchanged assertions still discriminate the injection boundary.

The lexical root filter is a test-fixture filter, not a new production
ownership authority. It covers real reads/replacements throughout each owned
synthetic test root; it does not add retries to the shipped runtime. Existing
product path/reparse checks, journal lock/before-state guards, non-journal
failure propagation, incomplete-state visibility and consumed recovery
permission are unchanged. No general retry framework, runtime dependency or
installation prerequisite is introduced.

## Limitations and retained history

No real host transient occurred in the independent full run or nine owner full
runs. Simulated absorption does not identify or reproduce the real WinError 5
cause or IC-F01 actor. The historical IC-F01 probes and timing-parent run remain
nonconforming observations excluded from acceptance under `827fccfe`; this
review does not rehabilitate them.

The owner disclosed a concurrent shared-Git-config change. Its writer remains
unknown; this reviewer neither inspected that configuration nor attributed,
reverted or investigated the change.

Actual runtime here was Python 3.11.9, launched by explicitly approved PowerShell
7.6.6 without policy overrides. The shell wrapper, Bash/MSYS, native installers,
Python 3.9, POSIX/other OSs, full repository suite, kit and hosted CI were not
run for F-INT-5. Windows PowerShell 5.1 remains denied/unverified. No global/home
inspection, real installation, hook activation, private profile, network,
authentication, push, merge, PR or deployment occurred.

Two private reviewer-harness failures are retained. The initial in-memory
mutation used an unregistered main module and discovered zero tests; its parent
failed closed, and it is excluded. The corrected runner required four tests and
observed eleven expected failures. A first data-only assessment rejected CRLF
around `OK`; the corrected line reader reused unchanged logs without rerunning
product work. Neither failure is a candidate defect or a passing control.

Compliance remains UNVERIFIED because required-policy source/version/
applicability and advisory freshness are unresolved. No neutral-policy waiver
or release clearance is asserted. Prior accepted reports, A12 closure and all
historical failures retain their status. Integration remains coordinator-owned.

## Evidence and handoff

Private evidence root:
`C:\Users\jokerman\.copilot\session-state\1578dfd8-f239-4eba-989b-3c4bde3e5792\files\p10-fint5-b7555ca-independent`.

`intake.json`, `scope.json`, `builder-evidence-join.json`, per-selection
`launch.json` / `child-preflight.json` / raw output / `events.json` /
`result.json` / `cleanup.json`, sequential `spec-stage.json` and
`quality-stage.json`, `compliance-stage.json`, and
`reviewer-harness-dispositions.json` retain the assertions and limits above.
The evidence index and report-only delivery receipt bind their exact hashes.
This review changes no product, test, plan, memory, reducer or shared ledger.
