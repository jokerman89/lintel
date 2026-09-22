# P10 preservation recheck and specification stop

**Verdict: SPEC FAIL; first whole-P10 QUALITY NOT STARTED.**
**Open actionable findings: P1 0, P2 1, P3 0.**
F02's bounded producer-ownership repair passes the recheck described below.
F01 remains CLOSED. New **F03** is an independently reproduced false
`not_applicable` migration observation for an existing, incomplete plain target.
Product testing stopped on that counterexample. Neither the passing ownership
cases nor the partial remaining-spec execution establish whole-P10 acceptance.

This is the same independent reviewer who did not implement P10. No nested
reviewer, product repair, P03/P07 change, compatibility project, shared-plan edit,
A13 release, integration, remote operation or recovery of retained evidence
occurred. This report is the sole repository output.

## Immutable target, authority and attribution

| Identity | Value |
|---|---|
| Reviewed report HEAD / required parent of this report | `7bf5a31526cc39951978945df86dea85796fd01b` |
| Reviewed product | `a797b2d8e357d319e549015f591bc85421535cf7` |
| Direct product parent | `4c0519e3ba3ba610d4db3f7f19e18a85531546d9` |
| Original owned dependency base | `fb96f71342f7994c42bdfc7cd61e6d452e6acb54` |
| Original P10 product | `a73cf9ee38977501c201225d8269dac3668c1080` |
| Original independent review | `1d871338dcdd1b6a535e4b546c2b2d0a7aea031b` |
| Independent F01 closure | `00a0bef938a4da3f09064b6be88b8bad89ec897d` |
| Independent F02 finding | `c1a38a03e0efb54454e14bddee7cd07b4af6e1e3` |
| Current builder report Git blob | `963b13666e777052a5efd518a0724ce691b7c28e` |
| Current builder report SHA-256 / size | `2d0740563abd9c2629e52a944c1531702bb6bb1e36b7f35a9b411875c3473de5` / 76,849 bytes |

The initial worktree was already clean at exact `7bf5a315`; no reset, discard,
amendment or replacement of an old report was necessary. A post-stop read
reconfirmed clean detached HEAD `7bf5a315` before adding this report. The sealed
source contains **967 files**, exported from immutable Git blobs, with Git mode,
blob, size and SHA-256 recorded. Every source file was reverified after execution
and at the stop; no extra source files appeared.

Authority includes AGENTS.md, AGENT-INSTRUCTIONS.md, the Copilot adapter, relevant
memory/architecture, the selected work.json/spec/plan, original A12 and
CP-02/04/12/16 and RU-06/07/08/11, lifecycle inventory, ADR-0030/0031, the complete
current P10 report, master card `34b84a8`, F02 authority `79a36cc`, and guard-only
clarification `5d4651b`. Immutable authority absent from this branch was read
through Git artifacts, not imported or rewritten.

The original 48 paths plus the authorized copied-validation fixture remain the
review scope, not merely the most recent four files:

| Original group | Scope |
|---|---|
| Runtime entries, 8 | `bin\li-copilot.py`, `li-doctor`, `li-lifecycle`, `li-lifecycle.py`, `li-managed-transaction.py`, `li-migrate-claude-home`, `li-pack-scaffold`, `li-scaffold` |
| Native installation, 6 | `install\directories.txt`, `install.ps1`, `install.sh`, `native.ps1`, `native.sh`, `verify.sh` |
| Shared runtime primitive, 1 | `lib\managed_transaction.py` |
| Direct documentation, 5 | `docs\client-adapters.md`, `copilot.md`, `lifecycle.md`, `migrations\_INDEX.md`, `native-installation.md` |
| Skills, 16 | doctor, health, migrations, pack-create/list/switch/validate, personas-rotate, profile-switch, role-new, role, roles-list, scaffold-internal-tool, scaffold-mvp, scaffold, v4-migrate |
| Original tests, 12 | `tests\behavior\{install-fail-closed,install-target-boundaries}.sh`; `tests\integration\{copilot-kit.py,enterprise-workflow-snippets.sh,pack-source-target-resolution.sh,universal-lifecycle.py,universal-lifecycle.sh}`; `tests\shape\extension-pack-contract.sh`; `tests\unit\{managed-transaction.py,managed-transaction.sh,native-receipt.ps1,v37-closeout-additions-present.sh}` |
| Authorized fixture, 1 | `tests\integration\universal-profile-context.py`, its authorized copied-source list and validation method |

Keep separate: fixture `acf97f1`, F01 `4407827`, coordinator mode/diagnostic/footer
dependencies, accepted-core imports `bc0863a`/`8097ba2`, owned five-path `a31c5eb`,
approved Git-refusal `a559c9f`, and current F02 repair `a797b2d`. Accepted core is
not P10 authorship. Original producer hashes were not silently substituted for
later accepted-core hashes.

The current product diff has exactly four authorized paths:

| Path | Current immutable SHA-256 |
|---|---|
| `bin\li-lifecycle.py` | `a4148ba69f4c2b752486d44b299a00449311af62b3de2f71404279c5a8d72203` |
| `docs\lifecycle.md` | `c723ea622f370237797712d316be67626a70ce41e292a40927d08bdfa136525e` |
| `tests\integration\copilot-kit.py` | `21cef63b23c7ffe81d6a30f3154e01f96f748367974f425c2cfcfb1d02f93e42` |
| `tests\integration\universal-lifecycle.py` | `e63ce62bab65b6d03417d951b9fbab1ba8d239de170fe36f3d4e97531c07f296` |

Independent AST comparison preserves all **39 prior Copilot and 53 prior lifecycle
test methods**. Changed production functions are `destination`, `migration_changes`,
`runtime_publication`, `scaffold`, `extension_pack`, and the migrate call in `main`.
The F01 `migration_inventory` parser and F03's `layout_observation` are unchanged
from `4c0519e3`. F03 is an outstanding original requirement, not a claim that the
F02 patch introduced the detector.

Fourteen dependency/contract identities were compared against `4c0519e3`.
Key current identities are:

| Unchanged contract | SHA-256 |
|---|---|
| `docs\native-installation.md` | `e2cf6bf3417e10ad12112002e0719a581f1632b0db2881459cfaad20208e1ae0` |
| `install\directories.txt` | `c8e0e825586f309c43bbcb5dc6644eb270a233ee638c7244696193db8f52d7c3` |
| `install\native.sh` | `1425c05888b24b413a45ec33f70a98fe432f73774634197cae4cbdc9d1c9e187` |
| `install\native.ps1` | `57173b99e0c809d3fe45a6c9b894ddab0c07b3961a2d73b6fd61af25047483f7` |
| Accepted `lib\managed_transaction.py` | `acbf84ef94a9fc4afdb8f66766d376653549ee82f4cf063c6a5721b1fdc08cae` |
| `lib\profile_context.py` | `353ba79537736ab8d2acb8da06fbb7bd731c19d697b02fbdd5702a73712291a1` |
| `lib\profile-context-schema.json` | `dbcd40408fa066e423093312b86f3278e15613a04b310bcc43d832f7bef1e79c` |
| `lib\markdown_source.py` | `331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf` |
| `bin\li-copilot.py` | `f43ac1d9ebe1a4f961754014d33fae2738d240d78bf35a02947597f7ef3e18fc` |
| `lib\copilot-env.sh` | `5600e0a77d0b18cdad35605f4744c0145a7f6ce016346f1491869781345ba764` |
| Copied validation fixture | `d13bc5e93cbf23d03df9f093af761dd0d6f46aaa7badbf8a18d9f99558d0fee5` |

The shared Markdown provider remains blob
`0b3da55046358864fcd3075ba5bfb6c2348b1fec`. `context_safety.py`, `native_paths.py`
and `li-snapshot.py` complete the fourteen comparisons. No shared schema,
transaction, P07 reference, Git invocation or adapter ownership engine changed.

## F02 recheck: bounded ownership repair passes

The repair addresses the class rather than enumerating eight exceptions:
native presence/type/enumeration determines existing versus absent inputs;
`read_owned` captures original bytes and state together; absent outputs retain
create-only `None`; merges, moves and deletions carry their original expectations;
fresh publication observations can refuse but cannot manufacture ownership.
The existing shared `apply_files` contract remains the writer.

The independent three-method installed run uses the real copied source, caller
bootstrap and bundled `li-scaffold`, inherited verified caller reference, default
runtime home and retained 304-character history. It exercises short116 and
plain256 targets, mixed existing/absent seeds, the original protected contents,
settings surroundings/custom key, pointer-only changes, repeated/check/dry-run
behavior, late consumer-admission changes and write-entry changes. All three
methods passed: **41 recorded subprocess invocations**, no skips or cleanup error.
This is this reviewer's execution of the committed regressions, not the builder's
27-method aggregate.

The uninterrupted seeded/check/repeat positives invoke the actual bundled shell
helper. The race and guard tests use explicit interception of the actual Python
consumer/writer after the same real caller bootstrap; they are controlled
interceptions, not 21 uninterrupted shell executions. The race method proves
**21 refusals: 11 at consumer admission and 10 at writer entry**, with exact
post-intervention target preservation and no store creation.

The four long lifecycle methods independently passed with **25 recorded subprocess
invocations**: hidden/nested legacy moves and redirects; collisions, nonfiles and
malformed inputs; pointer repair and no-pointer preservation; and the four
create-only extension outputs. Their successful assertions do not establish
correctness of every diagnostic reader, as F03 demonstrates.

The admitted guard limitation was evaluated as specified. Unchanged observed
inputs are rechecked at final consumer admission. Real write paths keep the
original engine's expected-state checks. The deterministic guard-only marker edit
after its final admission read remains untouched and is **not** called a refusal,
atomicity guarantee or defect. A marker actually in the write set receives write
protection. No new guard API or no-op write was demanded.

**F02 CLOSED for this bounded producer contract.** F01's existing independent
40-candidate + 2-baseline cases and seven tests remain its closure evidence; the
parser/provider are unchanged. Neither closure opens whole quality or A13.

## F03: real incomplete layout reported not applicable

**Severity: P2, must fix. Confidence: 10/10 for the reproduced case.**
**Primary location:** `bin\li-lifecycle.py:473-505`, specifically ordinary marker
presence at 476, legacy presence at 483 and the absence-to-status mapping at
503-505. The same detector also uses ordinary directory/file enumeration at
491-499; that broader reader class was inspected, not separately exhaustively run.

**Requirement trace:** original A12.4.b / A12.4 and CP-16's truthful migration
visibility; `skills\migrations\SKILL.md:35-43` requires actual marker, legacy and
stub observations and keeps unknown distinct from completion. The defect affects
an explicitly selected plain target in the already required length256 class.
It is not the operator-approved external Git limitation, a demand for an unlimited
path guarantee, or permission for a P03/path project.

### Exact input and actual call

The two targets contain identical bytes, seeded and verified through native I/O:

```python
# .claude\lintel-layout.yaml: 66 bytes, LF
b"# Consumer marker; legacy content still exists.\nlayout_version: 5\n"

# tasks\lessons.md: 63 bytes, CRLF
b"# Consumer lessons\r\nUnmigrated knowledge must remain visible.\r\n"
```

Both are ordinary writable files: mode `0666`, readonly false. Their before/after
identities are respectively:

| File | SHA-256 before and after |
|---|---|
| `.claude\lintel-layout.yaml` | `b6ff0ad8776fa67e263c5c694a9f44c3f41f1a62399863862fa20c4c117e99ee` |
| `tasks\lessons.md` | `34c67a8e8ed5b15d967750f15c1b5a628bd0f714501a1ce85b1f1144f0dad7c3` |

The private fixture is `<evidence>\layout-observation-fixture`. Personal prefixes
are redacted here, not removed or shortened during execution. The short child is
`short`; the long child is `long-` plus 103 `x` characters.

| Actual normalized path | Short control | Long counterexample |
|---|---:|---:|
| Plain target root | 153 | 256 |
| `.claude\lintel-layout.yaml` | 180 | 283 |
| `tasks\lessons.md` | 170 | 273 |
| Ordinary presence of both seeded files | true | false |
| Native presence and exact seeded bytes | true | true |

Neither target has Git metadata. The real immutable source catalog was used
unmodified: `docs\migrations\_INDEX.md`, SHA-256
`8c7cf772687d272b1bd9ab8dbc3b6ab088a1ce6ce81c402bbc9f11660af1f273`.
No custom catalog/parser, mock helper, removed pin, alternate recovery store,
shortened default home or OS change was substituted.

The probe extracted the single Bash block from the unchanged actual skill,
SHA-256 `736eae4f2e30154be86a55223ff7f9133b013a0c7f7ab8483fc94d70b015adba`,
and executed it with the startup-free installed Git Bash:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" migrations
```

Actual outer argv was `C:\Program Files\Git\bin\bash.exe --noprofile --norc -c`
followed by that exact block; cwd was the owned common fixture, not either target.
The unchanged copied shell dispatcher, SHA-256
`8075bb67aad321701235b44f570521b96d1aa6b086a7f981b159f63b18beeb7f`,
executes the actual Python helper with the explicit source/repo/home/pack/pointer
arguments. The PATH binds the approved existing Python 3.11 interpreter.
No helper method was substituted for the skill/dispatcher route.

### Expected versus observed

Both targets have a version5 marker and unmigrated lessons; both should report
`incomplete`, version `5`, and `legacy: ["tasks/lessons.md"]`. An actual inability
to inspect the target must remain explicit uncertainty/error, not a definitive
non-applicability observation.

| Case | Product exit / elapsed | Actual layout row |
|---|---|---|
| Short true-positive | 0 / 0.891s | `observation: "incomplete"`, `layout_version: 5`, `legacy: ["tasks/lessons.md"]`, `stubs: []` |
| Long counterexample | **0 / 1.391s** | **`observation: "not_applicable"`, `layout_version: null`, `legacy: []`, `stubs: []`** |

Both stderr streams are empty. The current catalog's schedule remains `overdue`
in both outputs, with date `2026-09-22`; that schedule does not repair the false
target observation. Other unknown catalog rows are still present. This is not
F01's malformed-row disappearance.

The private discriminating probe exits **2 / SPEC_COUNTEREXAMPLE**, while both
product calls exit **0**. The long product result is successful JSON with a
definitive but false non-applicability classification. It does not literally
claim a completed installation, transaction or migration; those must not be
conflated with this read-only diagnostic defect.

The causal path is exact: skill lines24-25 -> shell dispatcher lines25-31 ->
`main` lines1163-1164 -> `migration_inventory` lines547-548 ->
`layout_observation` ordinary `exists()` gates -> null version/empty legacy ->
`not_applicable` at lines503-505 -> JSON/return0 at lines1192-1193.
The native-aware `read_owned` calls never run when those ordinary gates say false.
`doctor` also calls this detector at lines610-612; no additional doctor execution
or separate finding is claimed.

### Preservation and stop

Full before/after fixture maps match: exact bytes, file sizes/modes/readonly,
directories and both synthetic environment roots. All 967 source identities
match. No profile, pin, selected reference, audit, registry, receipt, lock,
snapshot, recovery store or transaction was created. The default runtime home
and derived roots remained the configured, absent target-local paths. No
completion receipt or ownership claim was generated.

The short and long targets, exact seeds, raw JSON/stderr, argv/environment records
and before/after maps are retained. **No cleanup or product recovery was attempted.**
The short positive is a detector control, not replacement acceptance for the
long case, D01's default scenario, or D03.

After confirming F03, the existing remaining-spec continuation was terminated
through its known attached tool session. The first two methods had reported
`ok`; the required-caller-policy method was in progress. No later product tests
were started. There is no terminal aggregate exit/result or cleanup success.
Post-stop read-only sealing retained 1,782 fixture entries, including 1,398 files,
under its exact owned Temp root; two snapshots agreed and the unrelated outer
fixture remained unchanged. This deliberate stop is not a passing aggregate
or a new product interruption/recovery test.

## Independently executed evidence

The selected-test commands use explicit installed Python, `-I -B`, the retained
private `p10_combined_test_runner.py` and exact sealed test source. Copilot
selections use `-v -f`; the four-method lifecycle selection uses `-v`.
Full argv, environment and subprocess records are retained by the labels below.
No candidate test/assertion was modified.

```text
<Python311>\python.exe -I -B <files>\p10_combined_test_runner.py <label>
  <sealed-source>\tests\integration\copilot-kit.py -v -f <selected methods>

<Python311>\python.exe -I -B <files>\p10_combined_test_runner.py
  f02-independent-long-lifecycle
  <sealed-source>\tests\integration\universal-lifecycle.py
  --root <sealed-source> --bash <approved Git Bash> -v <selected methods>

<Python311>\python.exe -I -B <files>\p10_layout_observation_probe.py
```

| Actual label | Result / actual outer exit | Preservation and limitation |
|---|---|---|
| `f02-independent-installed` | **FAILED**, 1 test, 3.563s; exit1 | Unchanged fixture HOME-ancestry assertion failed before a product subprocess; exact cleanup, outer fixture and 967 source identities verified |
| `f02-independent-installed-temp-home` | **3/3**, 583.684s; exit0; 41 subprocesses | Corrected private HOME placement under the owned Temp parent; exact cleanup, outer/source unchanged |
| `f02-independent-long-lifecycle` | **4/4**, 22.150s; exit0; 25 subprocesses | Exact cleanup, outer/source unchanged |
| `remaining-original-adapter-spec` | **FAILED**, 5 tests / 1 failure, 297.787s; exit1; 11 subprocesses | First four pass; fifth fails at init; exact fixture cleanup and outer/source equality do not make the failed run green |
| `remaining-original-adapter-continuation` | **STOPPED**, 2 `ok`, third in progress; aggregate exit unavailable; 9 recorded subprocess starts | No full-run preservation/cleanup record; retained fixture, final source and unrelated outer state independently sealed |
| Actual migrations skill short/long | Product0/product0; discriminating probe2 | Short correct; long F03; complete read-only preservation and retained fixtures |

The first installed failure was specifically
`copilot-kit.py:148` in `default_consumer`: the initial synthetic HOME was not
under the test's unchanged Temp-parent requirement. The replacement run changed
only private environment roots to `<Temp79>\observer-roots\synthetic-home`.
It did not shorten the actual caller, default store, child or retained history.
The failed original run and its exact output remain separate.

The passing installed selectors were:

```text
CopilotKit.test_installed_scaffold_preserves_seeded_short_and_long_plain_targets
CopilotKit.test_installed_scaffold_refuses_late_long_target_changes
CopilotKit.test_post_admission_guard_change_is_preserved_without_atomicity_claim
```

The passing long lifecycle selectors were:

```text
ScaffoldMigrationLifecycle.test_long_plain_migration_keeps_hidden_files_stubs_and_user_bytes
ScaffoldMigrationLifecycle.test_long_plain_migration_collisions_and_invalid_inputs_refuse_before_writes
ScaffoldMigrationLifecycle.test_long_plain_pointer_repair_preserves_surroundings_and_no_pointer_opt_out
ScaffoldMigrationLifecycle.test_long_extension_outputs_keep_create_only_expectations
```

The first four methods of the failed remaining-spec aggregate passed:

```text
CopilotKit.test_native_publication_keeps_the_original_263_character_destination
CopilotKit.test_missing_native_helper_cannot_fall_back_to_target_pythonpath
CopilotKit.test_swarm_wrapper_and_complete_source_resource_inventory
CopilotKit.test_joined_runtime_dependencies_refuse_incomplete_source_before_writes
```

`CopilotKit.test_joined_installed_dependencies_cannot_be_hidden_by_inventory_removal`
then failed during initial `self.run_cli()` (`copilot-kit.py:1153`, assertion at71),
before its dependency-removal assertion. Actual error:

```text
ERROR: [WinError 5] Access is denied:
'\\?\<Temp79>\lintel-copilot-tests-5x4_pwt0\
.lintel-recovery-5a8c54c4c6702945\transactions\
transaction-6fe9c97be57c4429b3dea835aa7d861e\.lintel-write-m5zbz9ap'
->
'\\?\<same transaction>\journal.json'
```

The operation returned1. Its cause is **unresolved**, not attributed to a fixed
product defect, cleanup or policy. A separate later run cannot erase it. The
builder's own historical WinError5 is also not claimed repaired.

Before the F03 stop the continuation completed:

```text
CopilotKit.test_original_default_113_128_paths_init_check_and_owned_recovery
CopilotKit.test_canonical_default_caller_child_keeps_verified_parent_and_unbound_child
```

These add actual default113/store128, original218->260/check/recovery and real
installed caller/child evidence. The earlier atomic selector preserves
classic109/source116/target182 and destination256->263. Neither a short-root nor
an explicit-store substitute was used. The continuation stopped during
`test_canonical_required_caller_policy_refuses_missing_drifted_and_conflicting_context`;
its remaining 14 selections did not run. They included the two approved Git
methods, missing-rule repair, adapter interruption, prose/conflict/EOL/source
update/link checks, long metadata/index controls and the failed dependency
selector's proposed rerun. No completion claim is made for those selections.

## Original parent and subleaf verdicts

`BLOCKED` means the complete required evidence was not obtained before the
mandatory specification stop; it is not a pass manufactured from selected cases.
Passing unchanged prior behavior is retained at its actual source revision.

| Original control | SPEC verdict | Evidence / remaining condition | QUALITY |
|---|---|---|---|
| A12 | **FAIL** | F03; complete acceptance blocked | NOT STARTED |
| A12.1 | BLOCKED | F02 producer closure; remaining diagnostic/profile/caller obligations incomplete | NOT STARTED |
| A12.1.a | BLOCKED | Installed source/target bridge and class preservation pass; complete doctor/health and remaining canonical policy proof not certified | NOT STARTED |
| A12.1.b | BLOCKED | Retained profile contract/switch evidence; actual validation cleanup and complete required caller selector outstanding | NOT STARTED |
| A12.1.c | BLOCKED for complete gate | Prior independent role/persona/private-boundary tests and unchanged APIs retained; extension create-only recheck passes, not whole-surface certification | NOT STARTED |
| A12.1.d | BLOCKED for complete gate | F02 paired migration/guards/write-set behavior passes; full combined lifecycle acceptance not established | NOT STARTED |
| A12.2 | BLOCKED | F02 overwrite closed, not a blanket install/update/conflict pass | NOT STARTED |
| A12.2.a | BLOCKED | Retained genuine no-Python native cases plus classic/default methods pass; aggregate failure/stop remains | NOT STARTED |
| A12.2.b | BLOCKED for complete gate | F02 seeded/mixed/late-change and long collision class passes; remaining full adapter/config/customization selections stopped | NOT STARTED |
| A12.3 | BLOCKED | Retained core/native recovery plus current default method; combined adapter interruption selector unrun | NOT STARTED |
| A12.3.a | BLOCKED | Prior explicit failure/interruption evidence retained; current access-denial failure unresolved | NOT STARTED |
| A12.3.b | BLOCKED | Existing owned/deep recovery and replay evidence retained; full combined adapter proof outstanding | NOT STARTED |
| A12.4 | **FAIL** | F03 gives a false target observation | NOT STARTED |
| A12.4.a | BLOCKED | Honest host/uninstall boundaries inspected; actual approved Git-refusal selectors not reached | NOT STARTED |
| A12.4.b | **FAIL** | F01 stays CLOSED; F03 hides actual incomplete layout behind non-applicability | NOT STARTED |

There was no whole-quality start followed by an undisclosed stop. Static work and
executions above belong to the required specification pass. No quality verdict
is supplied for unexamined whole-package correctness or maintainability.

## Retained evidence, isolation and limits

Do not rerun unchanged suites to manufacture a new aggregate: the prior independent
`c1a38a03` review already records **53/53** lifecycle methods on the corrected
process environment and **9/9** managed-runtime methods. Native no-Python
install/check, genuine Bash/PowerShell entry points, repeat/update/obsolete
ownership, config/roles/packs/hooks/brand, required policy, migrations, interruption,
explicit recovery, foreign/corrupt stores and consumed replay were exercised
there. Those are prior-source observations, not 62 fresh tests on `a797b2d`.
Current changes/unchanged contracts and focused rechecks are separately recorded.

The old native aggregate **8 tests / 1 failure**, PATHEXT-related Git discovery
failure and separate broad cache diagnostic failure remain FAILED. The latter
did not retain its before-map; its exact difference cannot be retrospectively
proven. Expected synthetic PowerShell startup/telemetry files are documented,
not a blanket cache exception. Current outer-map comparisons have no ignored
cache differences.

Every execution reconstructed an allowlisted process environment before both
tests and outer comparisons: synthetic HOME/USERPROFILE, drive/path, application,
XDG/cache/temp, source/repo/home/packs/pointer/audit/jobs/private roles and derived
profile/history/registry/state roots. BASH_ENV/ENV and inherited Lintel/Claude/
Gstack/Git selectors were not adopted. Explicit PATHEXT, interpreter binding,
Git system/global `NUL`, empty hooks, fsmonitor off, and discovery ceilings were
recorded. Source-fixture Git settings were kept separate from checkout-equivalent
`core.autocrlf=true` used for actual worktree status; no false CRLF dirt was repaired.
Each test invocation was logged with effective roots before execution; stdout and
stderr destinations were opened before commands. The F03 probe used separate
owned roots outside the running continuation's Temp/outer fixture, avoiding
shared runtime or source mutation.

Actual Python is **3.11.9**, Git Bash **5.3.15**, and the approved existing
PowerShell is **7.6.6**. No policy override, denied5.1 retry, installation or
automatic host switch occurred. Python3.9, stock Bash3.2/POSIX, other OSs and
actual host registration/enforcement remain unverified. Existing Python-dependent
runtime helpers were not used to redefine bare installation's no-Python contract.

The operator's Git decision remains accurate pre-write refusal with unchanged
argv, not successful root256 Git setup. No stopped compatibility/setup variant
was repeated. The actual Git-refusal methods were selected but not reached
before the F03 stop. Supported shorter linked controls cannot close the
unsupported long linked positive, which remains UNVERIFIED.

Original D01 failed default setup, corrected normalized260 length and original
overcount/log remain preserved. The current default method's `ok` adds evidence;
it does not rewrite that failure or establish the stopped aggregate's cleanup.
The explicit-store bridge stays control-only. Original D03 cleanup **ERROR**
remains: the actual copied validation fixture was not independently rerun in this
continuation before the stop. No D01/D03 or complete preservation waiver is made.

Historical strict **120/128, 8 failures, 0 skips, 0 partial** remains FAILED.
Earlier 15-case/7-case failures, REDs, guard probe, Git/setup errors and failed
aggregates remain retained. Builder-only current **27/27**, **25/25**, **9/9** and
validation **1/1**, manifest `fa1d4000...`, and older builder 22-selector/34-operation
records are not this reviewer's runs or a synthesized full suite. No full
repository suite ran here. Catalog/reducers, final P04/P08/P10/P14/CI, human/host
acceptance and A13 remain separate and unaccepted.

### Durable evidence and handoff

Raw evidence remains under this reviewer's session
`files\p10-preservation-a797b2d-independent\`. Its immutable source, F03 short/long
fixtures and stopped continuation fixture are retained. Older roots/reports/refs
are not cleaned, rewritten or normalized. Read-only post-stop sealing executes
no product command.

| Artifact | SHA-256 |
|---|---|
| `identity.json` | `acecc385f84f59a33e812a986dc4a1025d9a9d00e4e289a6d046f5fe7a312839` |
| `source-manifest.json` | `4b1c113d0e1fd31d66eccee75dce07c0cf32dc545b8c82bd330a647171b0c516` |
| `scope-proof.json` | `450dae282562badea7463055c424efb361f856b5358240c0a547e411cb94ca08` |
| `migration-observation-short-evidence.json` | `fb94f2d9890f8a317f023083f526936a084304013926d0c802859b26d11d12c9` |
| `migration-observation-long-evidence.json` | `1b0960831ba4994fa11b101154c8304c38d2b8ba32e8566ac39653266d68208e` |
| `post-stop-seal.json` | `d22cbd0a1b58ef6d0dbae5c8d2358c053945b3a3f34f34daf0219fda92249699` |
| `post-stop-evidence-index.json` | `badf087a98ca06ce76ed3c5cbe9a2ccaaab5e6dc216e9f69ca763aee2984d3da` |

The index also binds invocation, isolation, preservation, failed/stopped raw logs,
exact source excerpts and the private drivers. Hashes establish content identity,
not authenticated independence or host enforcement.

**Return to MasterSession:** F02 scoped closure, F01 retained closure, new P2 F03
and complete SPEC FAIL. The original owner needs separately bounded authority for
the real detector/preservation class; the reviewer supplies no repair or scope
expansion. First whole-P10 QUALITY stays NOT STARTED. This sole report is committed
on exact `7bf5a315`; the delivery message supplies its commit, parent, file hash
and verified clean status. Preserve all fixtures and remain read-only pending a
new immutable checkpoint.
