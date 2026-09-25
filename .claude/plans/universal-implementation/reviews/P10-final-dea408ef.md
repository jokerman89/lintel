# P10 independent B01 and first whole-package quality review

**Final SPEC: FAIL. First whole-P10 QUALITY: STARTED, FAIL. Compliance: NOT STARTED.**
**Open findings: P1=1 (F05), P2=1 (F06), P3=0. B01 is independently closed within
its authorized scope; F01-F04 retain their scoped closures. P10/A13/integration
are not cleared.** No product, test, shared plan, memory or generated file was repaired.

The last two missing original selectors passed on this candidate. An initial
component SPEC PASS was recorded before opening QUALITY, not inferred from the
builder's results. QUALITY then demonstrated a separate adapter preservation
defect and identified a native inventory contract defect. Those findings supersede
the initial PASS; passing selectors do not average away failed requirements.

## Immutable selection and authority

| Identity | Value |
|---|---|
| Authority | `5123ca877979d6f38972b286aeb91e66f46b9387` |
| Product | `dea408ef4051219c75eb4bebd7a678f3a85bcc80` |
| Product parent | `4be5e0966937755ad19d7a2f6560c8fdbb27d479` |
| Reviewed report-only HEAD / this report's required parent | `72cf78a5dd294228127b864f9c5705ffa855dd9f` |
| Builder report Git-byte SHA-256 | `88a784c5b3a34e0c46ddaefc91467f3187cbc70ce6da5e65666c610e700b4394` |
| Continuing independent reviewer | `1578dfd8-f239-4eba-989b-3c4bde3e5792` |
| Prior independent final | `8c3afbbe269e2b289ee8c20e2d5fd2cf87eecc9d` |
| Preserved prior ref | `refs/heads/review-p10-6e1-frozen-8c3afbb` |

Authority, the complete current builder report, mapped work/spec/plan, original
A12/CP-02/04/12/16/RU-06/07/08/11 and lifecycle inventory, ADR-0030/0031 and relevant
retained decisions/reviews were reconciled. The selected work map validated.
Clean detached ancestry was verified before pinning and before report creation.
The previous review remains reachable; no reset, amendment or discarded state.

The B01 delta is exactly three product paths, +299/-1:
`lib/managed_transaction.py` changes only `_save_journal`; its unit file adds six
methods/helpers; `docs/lifecycle.md` adds eight lines. All nine prior transaction
methods, all 42 kit methods and the other 963 Git entries remain unchanged.
The raw-Git export has 967 files, verified again after execution and evidence sealing.

The review selection remains the original 48 paths from `fb96f713` to `a73cf9ee`,
plus the separately authorized copied-validation fixture: 49 files, 12,626 lines,
with exact blobs, Git modes, sizes, hashes and diffs in `selected-inputs.json`.
This is not a three-file-only quality verdict.

| Selected surface | Files |
|---|---|
| Executable entry/helper family | Eight: Copilot adapter, doctor, lifecycle shell/Python, managed-transaction dispatcher, migration, pack scaffold, scaffold |
| Documentation | Five: client adapters, Copilot, lifecycle, migration index, native installation |
| Native installation | Six: directories contract, both entry points, both performers, source verifier |
| Runtime transaction | One shared producer-supplied file mutation primitive |
| Lifecycle skill fronts | Sixteen: doctor/health/migrations, four pack skills, personas/profile, three role skills, three scaffold skills, v4 alias |
| Tests | Thirteen: behavior/shape/unit/integration surfaces, including the separately authorized profile fixture |

Accepted-core imports `bc0863a`/`8097ba2`, coordinator CLI-mode/runner/footer changes,
native-consumer `a31c5eb`, Git refusal `a559c9f`, F02 `a797b2d`, F03 `036e903`,
F04 `6e1b1e0`, and B01 remain separately attributed. Unchanged P03/P07/provider
dependencies are not relabeled as original P10 authorship or independently
reimplemented. The quality findings below are outside the B01 three-file repair.

## F05 - adapter adopts late current state as overwrite permission

**P1 / blocks acceptance / confidence 10/10.**
Location: `bin/li-copilot.py:1048-1052`; originating read/merge at `806-839`,
other preflight/planning at `957-1003` and `1016-1047`.
Requirement: A12.2.b and the package's explicit rule that a current-state scan
alone never confers ownership. This is not a new atomicity requirement.

`protocol_updates` reads original project bytes and constructs merged bytes.
Later, after the complete changes dictionary exists, the adapter builds every
expected state from another current read. A user edit between those steps becomes
the accepted before-image even though the planned bytes were constructed without
it. The unchanged transaction correctly checks the supplied, but wrong, expectation.

The deterministic private probe used the frozen source CLI via `runpy`, with its
actual `init --target <owned plain folder> --source <immutable export> --store
<owned separate store>` arguments. It inserted one synthetic user edit immediately
before the adapter's expected-state read, and otherwise called the original
`file_state` and `apply_files`. It changed no product file, expected-state result,
transaction behavior or Git argument. This was a source-entry probe, not a claim
of another independently run installed-child scenario.

| Actual observation | Result |
|---|---|
| Seeded `AGENTS.md` | 56 bytes, mode 0666, readonly false |
| Late edited file before transaction admission | 111 bytes, same mode; added `Late operator instruction: retain the release freeze.` |
| Adapter-supplied expected state | Exactly the late 111-byte state |
| Planned and published file | Same 12,850 bytes, mode 0666, readonly false; late instruction absent |
| Actual product exit/output | Exit 0, 115.906s; reported `Lintel kit ready:` |
| Transaction | `transaction-303c1c23792345e3a83fd9e859630d27`, `complete`, all 441 paths `applied` |
| Final publication | `.github/lintel/manifest.json` |
| Source / outer synthetic roots / temp | 967 source files unchanged; exact outer/temp equality |

| Byte image | SHA-256 |
|---|---|
| Seed | `166fc64e863123220e2ee89e48e54b7d0b7e001093ed5d39bf220e371ea5bee1` |
| Late edit / wrong accepted expectation | `b86072a9ac7eafd4842612634c59a5a1ecfe74f6affdcca1db4bf3f2a0f65bd2` |
| Staged and published result | `294b824dd996e0e75cee591f66197d5cefc721f1b0d968c9d1cbde645a3ca1c8` |

The plan's before-image and snapshot contain the late edit. Plan/journal/snapshot
digests and current target/store maps agree. This is coherent publication of stale
planned content, not journal corruption. The recoverable before-image does not
make silent successful loss acceptable. No recovery, cleanup or further product
execution was performed after freezing the finding.

The demonstrated write-set edit is **before consumer admission**, not an unchanged
guard edited after its final read. The F02 guard-only clarification therefore does
not waive it. F02's repaired lifecycle producer remains closed; this is the other
producer, `li-copilot.py`, retaining the same ownership mistake.

Static class trace also reaches generated managed updates, protocol merges,
`.gitignore`/`.gitattributes` merges, absent/create-only outputs, obsolete deletions
and final inventory publication: all use the same late comprehension. Only the
`AGENTS.md` instance was dynamically demonstrated here; the class trace is not
misreported as seven additional executed tests.

**Required correction:** bind each planned mutation to the original bytes/state
that justified its ownership and content; retain `None` for create-only paths.
Refuse intervening changes instead of substituting a late observed expectation.
Reuse the existing shared seam and adapter inventory/blocks/clients/EOL semantics.
Cover the producer class, not one filename/string; no core guard API expansion.
Guard-only rechecks remain at final consumer admission, without new post-admission
atomicity for unchanged guards. The reviewer made no correction.

## F06 - Bash accepts a body record that is invalid in the shared TSV contract

**P2 / must fix / confidence 9/10; source-grounded, not a new runtime test.**
Location: `install/native.sh:167-175`, consumed again at `543-551`.
Contrast: `install/native.ps1:207-220`.
Contract: `docs/native-installation.md:32-34,69-77` and the approved single
versioned native contract.

The Bash parser validates the first header but then skips **every** row whose
first field is `LINTEL-INSTALL`. For these bytes (backslash escapes denote tabs
and newlines):

```text
LINTEL-INSTALL\t1\nLINTEL-INSTALL\t1\n
```

both rows bypass record validation. The duplicate-path check sees only one body
row and accepts it. The check loop skips it again and reaches
`Installed managed bytes verified.` The PowerShell reader skips only the first
line, then rejects the second line because it is not a three-field hash/size/path
record. Thus malformed metadata is accepted by one performer and refused by the
other; even check-only verification can be success-shaped.

**Required correction:** consume exactly one header and strictly validate every
subsequent record under the shared grammar; apply the same rule to consumers of
that inventory and add a narrow negative parity case. No inventory data should be
silently omitted. This source trace does not establish execution on stock
Bash3.2/POSIX or a new PowerShell run. No such runtime claim or additional native
matrix is made.

## B01 independent closure and current commands

The bounded `_save_journal` implementation retains the operation lock, captures
the original absent/existing journal state, and allows at most four reported
retries at 0.05/0.1/0.2/0.4s only for Windows 5/32/33 two-path replacements of this
journal from its same-directory `.lintel-write-*`. It rechecks state after failure
and before retry, with the unchanged atomic expected-state seam still guarding
publication. Fifth, unrelated and non-Windows errors propagate. No generic target,
stage, source, snapshot, plan, binding or restore retry was added.

For these recorded commands, `PY` is the explicit Python 3.11.9 executable,
`FILES` is this reviewer's private session files directory, `E` is
`FILES\p10-b01-dea408e-independent`, and `S=E\exact-source`. Full absolute argv,
environments, streams and subprocess completions are retained privately.

```text
PY -I -B FILES\p10_b01_process_runner.py b01-journal-unit
  S\tests\unit\managed-transaction.py --root S -v

PY -I -B FILES\p10_b01_process_runner.py b01-original-pair
  S\tests\integration\copilot-kit.py -v
  CopilotKit.test_git_verification_directory_linked_and_plain_folder_controls
  CopilotKit.test_inventory_traversal_and_windows_paths_refused

PY -I -B FILES\p10_quality_producer_probe.py product
  [dispatches frozen li-copilot.py with the exact captured init argv]
```

| New independent execution | Exit and outcome | Preservation |
|---|---|---|
| Transaction suite | 0; 15/15, 39.616s; 46 scenario records, held-lock refusal separately | Completed cleanup, exact outer equality, 967 source files |
| Original Git/inventory pair | 0; 2/2, 986.196s; 70 completed subprocesses, 29 JSON events, no skips | Completed exact cleanup including temp/outer equality, 967 source files |
| F05 producer observation | 0; actual preservation expectation violated despite ready/complete | Full target/store and four byte images frozen; cleanup deliberately not attempted |

The unit scenarios contain 24 transient cases, 3 persistent exhaustions with real
explicit recoveries, 8 nonretryable/non-Windows/nonreplacement cases, 4 changed-state
refusals and 7 unrelated-publication propagation controls. Exactly 73 retry notices
were injected. The real selector pair emitted **zero** retry notices, including
normally captured successful stderr.

Supported directory and linked init/check, linked negative cases, plain-folder
operation and original malicious-inventory assertions completed at the unchanged
original dimensions. B01's missing positive is now observed independently.
This is a **non-reproduction**, not proof of the historical denial's cause.
Injected exhaustion/recovery verifies the bounded error mechanism separately.

The builder's 15/15, 71-subprocess pair and 317-subprocess complete 42/42 kit remain
builder evidence. The independent reviewer did not run another complete kit or
full repository suite and does not substitute the builder's counts for 70 here.

## Original acceptance matrix and retained evidence

`PASS` below is a scoped component observation, not host/platform, integration or
release approval. Required deviations cannot be averaged away. A12.4.a retains
passing host/uninstall subcontrols but fails truthful native check through F06.

| Original control | Final SPEC | Actual basis |
|---|---|---|
| A12 | **FAIL** | F05 preservation and F06 native verification |
| A12.1 | PASS | Owned helper and configured-root families below |
| A12.1.a | PASS | Retained actual installed/default caller-child bridge and required-policy selector |
| A12.1.b | PASS | Structured profile/pin/switch evidence and actual copied validation with complete cleanup |
| A12.1.c | PASS | Retained role/persona/private-boundary cases and source review; no real private profile |
| A12.1.d | PASS | F02 lifecycle original-state binding, migration and actual producer/reader consistency |
| A12.2 | **FAIL** | Original positive observations complete, but adapter preservation fails |
| A12.2.a | PASS | Retained native/classic/default positives plus current real directory/linked/plain controls |
| A12.2.b | **FAIL F05** | Existing conflict/prose/EOL/link controls pass; late adapter write ownership does not |
| A12.3 | PASS | Actual interruption/owned recovery and bounded journal failure controls |
| A12.3.a | PASS | Nonzero/no-success and coherent incomplete evidence; current exhaustion controls |
| A12.3.b | PASS | Real explicit recovery, later-edit refusal, consumed replay and default-store evidence |
| A12.4 | **FAIL** | Historical/host boundaries retained; malformed native inventory can verify |
| A12.4.a | **FAIL F06** | Static native check counterexample; actual Git refusals and unsupported host/uninstall controls remain valid |
| A12.4.b | PASS | Independent F01/F03/F04 closures and preserved historical aliases |

The complete original 18-selector listing and actual mixed-source outcomes remain
in `P10-final-6e1b1e0.md` at `8c3afbbe`, SHA-256
`d7eeae1dfe8508a4c2ee96998c2923b37b4d652ab408a49a4c5213b2ec400fde`.
Its 036 run was 17 methods, 15 pass/2 fail, exit 1; copied validation separately 1/1.
Its 6e F04 class was 4/4 and 223 actual calls with no-write maps; final pair was
1 pass/1 fail, exit 1. Those aggregates remain failed. The two methods now passed
on `dea408ef` are distinct new observations, not a retroactive combined pass.

Retained passing selectors cover required/missing/drifted/conflicting caller
policy, actual long Git refusal, missing-rule repair, interruption and explicit
recovery, prose/conflict/collision, CRLF/EOL, deterministic source update, symlink,
long metadata/generated links/public index, malformed protocol/inventory and
actual copied validation/nonactivation/cleanup.

Other retained independent sources remain `00a0bef` (F01: 40 candidate+2 baseline
cases and 7 tests), `c1a38a03` (lifecycle 53/runtime 9), `c1f6bad1` (F02 installed 3,
long lifecycle 4 and individual completed classic/default/canonical controls),
and `131d3db4` (F03 exact contrast, 6 reader methods and completed dependency case).
The F04 exact three-call contrast distinguishes observed incomplete canonical
destinations from the producer's actual stranded-redirect refusal.

Original classic 109/source 116/target 182 and atomic 256->263, default 113/store 128
and 218->260, and the actual installed/default canonical caller with 304-history
remain their original evidence, not shortened substitutes or current reruns.
674 old indexed bindings were reverified against their sizes/hashes. Repeated
bindings are not counted as unique files or new test executions.

## Quality dimensions, isolation and limits

Correctness/preservation and test adequacy fail on F05; fail-closed contract parity
and truthful output fail on F06. Existing adapter ownership must remain the sole
engine, with original-state evidence passed into the shared primitive. Source
closure, required policy, role privacy, inert hooks, migration/readers, bounded
retry, root/store binding, explicit recovery and skill/helper consistency were
reviewed using the full selection and retained observations, not just B01.
No new high-confidence performance/style defect is asserted. This is a failed
first whole-package quality attempt, not a passing comprehensive certification.
Compliance gates were not started because QUALITY failed; neutral fixtures are
not a policy exemption.

Every product call/import and outer comparison used verified allowlisted
synthetic HOME/USERPROFILE/application/XDG/cache/temp/Lintel-derived roots,
PATHEXT/interpreter binding and Git discovery ceilings. Source Git identity was
kept separate from fixture config, including checkout-equivalent autocrlf for
source status. Outputs were redirected before commands; no shared runtime,
live-home read, ACL/AV/process inquiry, global setting or permission change.

Private verifier failures remain separate: the retained index initially rejected
explicit session-owned parent helper references; the producer launcher first
rejected its own mismatched ceiling assertion **before any product call**; final
indexing initially doubled an already-native path prefix after sealing the
finding. Only private verifiers were corrected. Raw failed logs are retained.
No shipped assertion/source or product environment/behavior was weakened.

Native no-Python installation evidence remains actual earlier execution through
the expressly approved installed PowerShell 7.6.6 without policy override.
Windows PowerShell 5.1 remains denied/unverified. Actual Python 3.11.9 and Git
Bash 5.3.15 do not prove Python 3.9, stock Bash 3.2, POSIX or other OSs.
Unsupported long linked-Git positive remains unverified. F06 is static evidence.

All 120/128 failures, REDs, guard/cleanup/cache diagnostic failures, repeated
WinError 5 and stopped aggregates remain historical failures. The captured
WinError 5 incident has coherent incomplete owner/plan/snapshot/file-phase
evidence; its pre-syscall temporary/handle/ACL facts and cause remain unavailable.
The owner's assessment did not establish an owned open-handle/readonly/state bug
or external sharing cause. That incident was not recovered or investigated anew.
Unrelated passing explicit recoveries do not claim recovery of that incident.

## Frozen evidence and delivery

Private root: `<session-files>\p10-b01-dea408e-independent`.
F05 capture: `quality-producer-ownership\capture.json`; exact target and store are
the sibling `target` and `store` directories there. Seeded, late-edited, planned
and published `AGENTS.md`, trace, complete maps, plan/journal/snapshot and raw
stdout/stderr remain preserved. No recovery or cleanup is authorized by this report.
The coordinator receives exact absolute paths privately, not personal prefixes
committed into the repository.

| Evidence | SHA-256 |
|---|---|
| New index, 1317 bindings; source separately manifest-bound | `31ce7c5b3a0422743ee65e76d649781c8729b40f86b70ff7e8b9ae85b195fe7f` |
| `quality-findings.json` | `35ff3ba1ad4221fe430a1785246f866af4a137bac10cee1288365796682787df` |
| `final-stage.json` superseding initial SPEC gate | `97c868a4464ef20739273949ef2b53494e37ec849ff0574a11c9c2cac243d177` |
| F05 `capture.json` | `ce1d20b2a96f6ba78e6d95ba9a89b357c26244dcf80bbda6cac584210d2606e7` |
| F05 `producer-trace.json` | `5b9c94142734ba3b84f631ee671e67f4f1c33dfc54c7efd5321d7a9546bc1bf6` |
| Current unit stdout / stderr | `6fea85a47a9b315663bc69ef2c309779f269717bfc3d301c1561485fcded6493` / `bf0e1701e4da9bd302e4a9578711fa1955a409ae6332d26c2d9a3cf10e40944e` |
| Current pair stdout / stderr | `c9749ac6b4b550184f93b977ea4e1e94c9314145edc3e2d74a91beadd3bd62ae` / `46f9a224b3c813852eb706293e912873cd6816cbdd2bdbd4dd4a255bcef4870e` |
| Retained 036 index, 572 bindings | `36121f71d86c2d7accbe8c870f5dbd5cd8c7a054db461c8809088aeddbcbc4cf` |
| Retained 6e index, 102 bindings | `5b352367c0687c47ad4edf41ef338d3f51f2683bb0f9936df78080d47d24533d` |

This is the sole repository output. Report-only parent, raw Git report hash and
clean-state receipt accompany delivery; no merge, push, PR or product import.
**Next permitted decision belongs to the coordinator/original owner: address F05
and F06 within the existing contracts, then recheck affected controls while
retaining valid unchanged evidence. No reviewer repair or further execution is
implied. A13 and integration remain gated.**
