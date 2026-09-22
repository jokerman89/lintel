# P04 shared-evidence consumer review at f02e994

**Date:** 2026-09-22. **Reviewer:** independent session
`ed672f58-2e85-42e2-b1b2-0635ba5b2325`; no implementation by this reviewer.
**Coordinator:** recovery session `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Released-unit specification: FAIL. Quality: NOT STARTED. Unit verdict: REJECT.**
New findings: **P1: 1; P2: 1; P3: 0**. Both findings are in the owned consumer
delta, not requests to repair accepted P05/P07/P09 providers. No product fix was made.
Earlier `aa73651` / `279dfc9` component acceptance and historical merge acceptance
remain separate; this report does not retrospectively rewrite either.

## Exact scope and refs

| Role | Immutable ref |
|---|---|
| Reviewed product | `f02e994a5a8c131bac862c3c866289f49c05a212` |
| Product parent / delta base | `0516a4a05708e06f86cd51ae1d642399737e58b3` |
| Product tree | `1c96075421b97f35bf6c8d1a428c7d51c0d4bb13` |
| Released card/dependency tree | `bdfd1274b47fb54687076ef89082fddf2ceda3b5` |
| Builder report-only tip / review checkout | `c2a9455a0c87db5900f93d73afa62e2e5f635ac4` |

The checkout was clean and detached at `c2a9455` before review; its only difference
from the product is the appended P04 implementation-report checkpoint. This review
covers exactly the 17 paths in `0516a4a..f02e994`, under the released
`packages/P04.md` **Shared-evidence consumer unit**, its accepted interfaces and
P05 evidence reference. It is not an audit of the incoming dependency history.
The dependency merge's tree equals `bdfd127`; its two parents and the prior
reviewer worktrees were verified without resetting or changing them.

Changed paths: `bin/li-swarm.py`; `lib/swarm_contract.py`, `lib/swarm_evidence.py`,
`lib/swarm-schema.json`; `skills/swarm/SKILL.md`; `docs/concepts/swarming-work.md`;
the five Swarm brief/report/review/charter/coordination templates;
`tests/integration/swarm-shared-binding.py` and `.sh`;
`tests/integration/swarm-workflow.py`; `tests/shape/swarm-contract.sh`;
`tests/unit/swarm-contract.py`; and
`.claude/plans/universal-implementation/reports/P04.md`.

## New findings

### F06 - P1: shared review pointer can acquire coordinator runtime ownership

**Location:** `lib/swarm_contract.py:699-703`, with lexical admission at
`:405-408` and reviewer authorization at `:852-855`. **Confidence: 10/10.**

The new exception skips the entire protected `.claude/runtime` tree for every
`shared_evidence.*` artifact. The canonical-review pathname check does not
establish physical ownership. A permitted
`.claude/runtime/reviews/swarm-BC1.json` can therefore be a real hardlink or
symlink to an unrelated coordinator runtime file.

Independent actual-CLI reproduction used both link types against each of:

- `.claude/runtime/state/operation.json`
- `.claude/runtime/audit/reviews.jsonl`
- `.claude/runtime/jobs/current.json`

For all six cases, `os.path.samefile` confirmed the alias.
`li-swarm.py validate` and
`li-swarm.py check-scope --task BC1 --actor reviewer --changed <review-pointer>`
both returned **exit 0, `ok: true`, no diagnostics**. No extra coordinator path
declaration was needed. These were synthetic files, not live ledgers.

The gate consequently reports an edit of coordinator state or the review log as
a reviewer-owned edit. A later shared-evidence parse failure does not prevent
that earlier ownership mistake or restore overwritten state. This contradicts
the released alias/link/hardlink protection and the new template/skill claims.
The original plan/reducer hardlink negatives still pass; their old closure does
not cover this new runtime exception.

**Required repair:** keep the ordinary assigned review JSON usable, but narrowly
admit its physical ownership instead of exempting every runtime object reachable
through that name. Reject runtime-ledger aliases, including parent-directory
aliases and hardlinks, before accepting the reviewer change set. Retain positive
ordinary-review and coordinator-provider-slot cases. Repair belongs to the P04
owner, not to a shared provider.

### F07 - P2: a valid containing P05 selection is rejected

**Location:** `lib/swarm_evidence.py:103-104`. **Confidence: 9/10.**

The consumer checks exact set membership of each lane scope in
`snapshot.selection`, rather than whether the accepted selection covers that
scope. P05 explicitly accepts directory selection including descendants and
future new files (`lib/review_contract.py:312-313,340-396`).

Independent reproduction first passed all four shared commands with lane
`write_scope: ["src/core"]`. A fresh actual P05 context then selected `src`
instead of `src/core`, retaining the report, review and evidence selections,
base, work, actors and obligations. Real preparation, decision logging,
corroboration and QA were regenerated. The actual P05 **read-only** `ship`
verifier returned **`ok: true`**; it performed no publication.

`status`, `wave`, `resume` and `verify` nevertheless all returned **`ok: false`**
with `shared.blocked: Shared snapshot must select every complete declared
product scope`; close left the lane `awaiting_shared_evidence`. The selected
parent fully covered the declared product scope. This is a consumer-only false
negative on a valid caller-selected P05 context, not a provider incompatibility.

**Required repair:** honor accepted complete directory-selection coverage while
continuing to reject missing/partial scope and retaining future-file coverage.
Do not replace P05 hashing, relax raw identity, or require callers to fabricate
a second context merely to repeat a redundant child selector.

## Released-unit specification controls

The labels below are review navigation, not new task IDs or a second backlog.
The selected unit has **10 passing controls and 2 failures**; passes do not
average away either failure.

| Control | Verdict | Actual evidence |
|---|---|---|
| C01 Accepted providers, original map/package APIs, no replacement hash/parser/latest selector/scheduler or P08 import | PASS | Complete owned-delta inspection; actual P05/P07/P09 calls; provider/source identities unchanged. |
| C02 Work/package/leaves/attempt/purpose/actors and raw report/result identity | PASS | Shared identity negatives; all 57 retained local cases; independent CRLF/LF-only changes leave local inspection complete but revoke raw shared evidence for both product and report. |
| C03 Complete caller-selected P05 product coverage | FAIL | F07; actual P05 positive contrasted with all four consumer rejections. Missing-scope/noncircular negatives remain passing. |
| C04 Coordinator/reviewer ownership and all alias protections for new pointers | FAIL | F06 six physical aliases. Ordinary ownership, authority/reducer/cross-actor negatives and prior local protections still pass. |
| C05 One gate for status/wave/resume/verify; missing evidence and later rejection revoke | PASS | All four positive/missing-corroboration/later-rejection paths; malformed-log revocation and newer valid recovery; independent missing-explicit-profile cases. |
| C06 Immutable mandatory QA inventory, not result-selected obligations | PASS | Missing/retyped/downgraded/N-A/zero-test negatives; independent two-obligation case cannot omit the second requirement in any shared command. Restoring exact QA recovers. |
| C07 Explicit target-specific live P07 reference and policy before/after consumption | PASS | Lost pin, generation, required-policy/target drift and no-rebind cases; deterministic drift injected after the real successful QA verifier is caught by the final P07 check, then restoration recovers. |
| C08 Fresh non-clearing P09 results; ordinary P05 QA when no domain is selected | PASS | Actual provider production/verification; missing start/result and failed checkpoint after reprepare block; fresh QA equality and `release_clearance: false` / `review: not_evaluated` retained. |
| C09 Genuine verification-only result; explicit mechanical versus substantive/manual corroboration | PASS | No invented product edit; changed verification-only result blocks; mechanical opt-out and separate host/human fixture attestations exercised. Strings are not authenticated people. |
| C10 Old local/v1/v2 artifacts remain observations/history, never automatically upgraded | PASS | Local-only complete fixture cannot gain shared clearance; inspect/check-complete remain non-clearing; an independently supplied valid historical P05 v1 record/context/QA stays rejected and byte-unchanged. |
| C11 Git attribution, fan-in/conflict/interruption and native/sequenced/manual local capabilities retained | PASS | Original genuine-Git workflow; shared two-worktree fan-in and reprepare; unrelated-commit reuse; retained mode/type/link/dependency controls. Capability flags remain caller declarations. |
| C12 Owned scope, historical records, provider/role preservation and meaningful entrypoints | PASS | Exact 17-path delta; 968 baseline paths unchanged; 76 retained destinations; 17 historical Swarm artifacts / 23 historical plan paths and all 69 roles unchanged. Rich brief/template behavior and shape checks retained. |

The earlier A21 and A22.1-A22.6 evidence is reused only for its unchanged scope;
this is not a fresh historical merge audit. F06 affects the newly released
ownership extension, and F07 the new shared-context bridge. The selected A22.7
unit fails. **The A22.7 parent, newer P08 selected-work/resume join, other package
parents and final integrated acceptance remain OPEN.**

## Checks actually executed by this reviewer

All runs used the frozen source tree. Python test modules were loaded by the
private runner without changing their source or assertions. The outer command
was `python -B -S review_driver.py <mode>` through `invoke-isolated.ps1`, with
`local`, `workflow`, `shared`, `shape`, `probes` and `extra-probes` as the modes.

| Check | Result |
|---|---|
| `tests/unit/swarm-contract.py` | 57 tests PASS, 163.864 s, no unittest skips. All 56 previous test method names and their meaningful assertions remain; one local-only clearance negative is added. |
| `tests/integration/swarm-workflow.py` | PASS, 54.671 s: mapped/legacy local observations and actual Git worktrees, actor-scope rejection, interruption, conflicting merge and ancestry-preserving fan-in. |
| `tests/integration/swarm-shared-binding.py` | 18 tests PASS, 319.398 s, no skips; real accepted providers, synthetic actors. |
| `tests/shape/swarm-contract.sh` | PASS. Structural/prose wiring evidence only. |
| Three independent public-entrypoint probes | Two reproducible product failures F06/F07; missing explicit profile blocks as expected. Completed run: 44.090 s. |
| Four supplementary controls | 4 PASS, 75.501 s: multi-obligation QA, raw/local digest separation, valid v1 no-upgrade and post-QA live-profile drift. |
| Six changed Python files parsed with `feature_version=(3,9)` | PASS grammar only; actual interpreter was Python 3.11.9. Git was 2.55.0.windows.3. |
| Git scope, immutable blob/mode, report-prefix and whitespace checks | PASS. `c2a9455` differs from product only in the implementation report; no source or index changes remained after tests. |

The 15 Brief Forge checks reported by the builder were **not rerun here** or
counted as independent evidence. Brief Forge/provider files outside this delta
are byte/mode-identical to the released dependency. No full repository suite,
installed-client matrix, paid/model worker, actual Python 3.9 runtime or POSIX
executable-bit run was performed.

### Isolation, attempts and evidence

Every outer Python invocation, diagnostic import/comparison and child launch used
an allowlisted environment: synthetic HOME/USERPROFILE/HOMEDRIVE/HOMEPATH,
AppData/XDG/temporary/Lintel and derived pack/pointer/audit/state/jobs paths,
explicit PATH/PATHEXT and Git discovery ceilings. User/system Git configuration,
prompts, signing and hooks were disabled; no target-supplied command was run.
The approved jq executable was rehashed before launches. No dependencies were
installed, and no real-home, remote/authentication, global-activation or production
operation was performed.

The private driver only enforced subprocess environments, Python `-S` and bounded
Windows long-path cleanup. Product code and test assertions were not patched.
The post-QA test wraps the real verifier solely to introduce deterministic
synthetic profile drift after it returns; it does not replace a verdict and is
not evidence of a live concurrency race.

Excluded attempts are retained honestly: the first driver preflight incorrectly
required a zero-byte rather than comment-only empty Git config; a private
`MSYS_NO_PATHCONV` setting then broke shell-to-native path arguments; and the
first supplementary-probe load had a private syntax error. Corrected runs above
completed on unchanged product. These setup errors are not product findings or
passing tests. F06 also reproduced before the path-conversion correction.
All individual test fixtures were cleaned; private evidence and the synthetic
process roots are retained for reproducibility.

Reviewer-local reproducer source, command/environment logs, exact observations,
provider hashes and preservation results are indexed under
`.claude/runtime/p04-shared-private/evidence-index.json`, outside this report
commit. Index SHA-256:
`7f5b8e6c37cb484753d13bd7a699d1c166c6402b3108b1b4a229978205bfe1b9`.
The index records 51 private evidence files and includes both failing and final
executions. It is not a P05 decision or independent actor corroboration.

## Decision and next owner

Return **F06/F07 to the original P04 owner through the recovery coordinator**.
Retain this frozen rejection, the existing passing controls and previous reports.
Recheck the repaired owned consumer before the shared unit's first eligible
quality stage. No P05/P07/P09 implementation change or P08 WIP import is requested.

Synthetic records do not grant host/human, client, global or release clearance.
Final selected-work/resume integration, applicable module joins, coordinator
reducers and independent integrated review remain separate requirements.
This report-only child names the reviewed product explicitly; its own commit
must not be confused with a new product checkpoint.
