# P03 joined native-path core handoff

**Status:** frozen implementer candidate; independent SPEC then QUALITY pending.
**Date:** 2026-09-21. **Review mode:** self-review only; no nested agents.
The classic adapter long-template selector remains **BLOCKED**, not waived.
This report does not close shared leaves, grant P10 acceptance or authorize SHIP.

## Authority and immutable identity

| Item | Exact reference |
|---|---|
| Authorized coordinator/base | `417edacd0c6e3187cc3f8867eb2ff475111cabf2` |
| Decision/card | ADR-0031; packages/P03.md, coordinated joined-path repair |
| Core product commit | `ce7415f6342220e49746880dd7338a6e7d9294ed` |
| Narrow fixture extension authority | `67d39f10f10ef35014128a0c6ca15292668b8b23` and MasterSession's explicit message |
| Separate fixture follow-up / final tested tree | `5fc657f14123daca9ec126cadc1e9d64ee60691c` |
| Full attributable review range | `417edac..5fc657f` |
| Preserved accepted P03 branch | `jokerman-microsoft-universal-context-safety` at `399a2e6b03a9ca3b3dfaddc4f38498f9f88115f4` |
| Preserved investigation branch | `jokerman-microsoft-p03-joined-path-investigation` at `990b0daa752fc36b1612e9c897f128bb1ca4cf88` |
| Current continuation | `jokerman-microsoft-p03-native-path-core` |

The continuation started clean at the authorized base. No reset, amendment, previous
ref movement, WIP import, other-worktree edit or remote operation occurred. The fixture
extension arrived after the core commit; it is a separate one-file commit, not an amendment.
This report is a later documentation-only commit and does not change tested product bytes.

Only these 16 product/test paths changed:

| Group | Exact paths |
|---|---|
| Representation and core I/O | `lib\native_paths.py`, `lib\context_safety.py`, `bin\li-snapshot.py`, `lib\profile_context.py` |
| Isolated Git recipe | `agents\engineering\RegressionDetective.md` |
| Direct support documentation | `skills\context-save\SKILL.md`, `skills\safe-install\SKILL.md` |
| Existing core/path tests | `tests\unit\context-safety.py`, `tests\unit\snapshot-ownership.py`, `tests\unit\profile-path-identity.py` |
| Authorized fixture/copy plumbing | `tests\integration\universal-profile-context.py`, `tests\unit\universal-trusted-tools.py`, `tests\integration\pack-source-target-resolution.sh`, `tests\unit\wiki-gen-idempotency.sh` |
| Mandatory-entry additions only | `bin\li-copilot.py::ADAPTER_RESOURCES`, `tests\integration\copilot-kit.py::JOINED_RUNTIME_RESOURCES` |

P07 scenario bodies/validation, P10 engine/navigation/transaction/parser code, P08
routing/private-import fixtures, A13, shared plans/memory/ADRs and generated outputs
were not edited. In universal-profile-context.py, only the source resource list and
exact-root cleanup registration/method changed. In universal-trusted-tools.py, only
RESOLVER_RESOURCES and Fixture's cleanup registration changed.

## Implementation boundaries

`lib\native_paths.py` has exactly two public exports:

```python
path_identity(path: PurePath) -> tuple[str, ...]
native_io_path(path: Path) -> Path
```

The accepted P07 representation code was extracted, not independently reinvented.
It preserves case and recognized ordinary/extended drive and UNC identities, rejects
device/ambiguous/ADS/reserved/traversal forms, and performs no filesystem I/O,
resolution, root selection, permission decision or mutation. POSIX I/O spelling remains
a passthrough. Representation errors are `ValueError`.

P07 retains `_path_identity` and `_native_io_path` compatibility wrappers with
`ProfileError("PROFILE_IO", ...)` translation. Its profile selection, containment,
allowed in-root links, schemas, canonicalization, generations, history and digest
functions are unchanged. Actual AST comparison against the base found only the two
wrapper function bodies changed; the additional module-loading block requires the
trusted sibling before any operation.

Both P03 and P07 load the module by the exact executable-sibling file, refusing a
missing or linked/reparse substitute. They do not fall through to target or
`PYTHONPATH` code. P03 does not import P07 internals. The shared representation never
replaces P03's stricter link/regular-file/ownership policy or P07's runtime policy.

P03 uses native operands for relevant ancestry/link/type/stat/resolution, open/read,
mkdir, temporary creation, chmod, both replace/rename operands, traversal, samefile,
locks, journal access, retention and exact owned cleanup. Internal P03 logical-path
projection uses the shared identity; it is not a third public path primitive.
Native iteration/temp names are projected back onto the caller's retained logical
root. Ordinary inputs do not acquire serialized I/O aliases, while explicitly selected
extended roots retain their spelling. Existing snapshot/result v1 and restore v2
formats, digests, filenames, key lengths, byte bounds, retry classes and consumed
restore permission remain intact.

The Windows bisect recipe uses a local option array for only its owned worktree
creation, trial bisect start/run/log and reset. Non-Windows commands remain unchanged.
No persistent local/global `core.longpaths` setting or session-wide environment
override is written. Read-only caller ref resolution is outside that option array.

## RED and preservation evidence

All runs used recorded synthetic isolation. Earlier investigation failures and
artifacts remain separate; a later successful run does not relabel them.

| RED observation | Repair verification |
|---|---|
| `red-context`: 3 methods, 1 failure and 7 errors. At 259 the first reservation worked but its collision suffix failed; 260/268/278/277/290 exclusive opens failed. Long-parent mkdir and missing-native-dependency requirement also failed. | Exact-length reservation/read/atomic write/collision tests now pass, with unchanged logical path strings. Long-root select/cool/case-alias behavior and missing/hostile-PYTHONPATH/linked sibling refusal pass. |
| `red-snapshot`: long existing store was treated as missing by ordinary directory I/O. | Actual create/read/bind/interrupted restore/resume/retention/prune uses long parents, blobs, locks and journals. Recorded explicit-root owners and unchanged manifest/result bytes are asserted. |
| Investigation's actual 218 -> 260 blob replacement failure on unchanged dependency code | `test_native_snapshot_atomic_publication_uses_218_to_260_without_shortening` asserts the exact logical source/destination lengths, captures both native replace operands, verifies bytes, and preserves existing bytes/removes only its temporary after injected replacement failure. |
| `red-bisect`: real 283-character good-ref lock creation failed with `Filename too long`. | The unchanged success/error reproducer executes the modified real recipe at the same 283-character ref dimension. Caller HEAD, raw index/config, staged/unstaged/untracked bytes and modes are unchanged; trial HEAD and bisect-state cleanup are checked. |
| `relative-red`: initial native adoption rejected previously supported relative CLI root arguments. | Before freezing, `_locations` was corrected to use existing checked-root resolution before its duplicate link check. The dedicated regression and inherited overlap/link refusals pass. No root-inference behavior was added to native_paths. |

The selector's bounded dynamic-programming implementation is retained. Existing literal,
glob, unmatched/error, ADR, capacity, URL, historical checkpoint, stale/tampered record,
late user edit, interrupted recovery and replay tests remain; no oracle was deleted
or weakened. Namespace/ADS/reserved/outside/link/junction negatives precede mutation.

### Real shell consumers at long defaults

The original ownership, roundtrip and memory-v2 scripts were run unchanged, not replaced
by direct syscalls. Their outer owned fixtures were 137/137/138 characters. The
post-commit run used Bash tracing to retain actual returned path strings without changing
their arguments or assertions:

| Script | Observed native checkpoint lengths | Result |
|---|---|---|
| `tests\unit\context-repository-ownership.sh` | 270, 278, 281, 283, 289, 292, 301 across its retained branch/history/collision cases | Exit 0 |
| `tests\unit\context-checkpoint-roundtrip.sh` | 280 (`mywork`), 279 (`later`) | Exit 0 |
| `tests\unit\memory-v2.sh` | 292 | Exit 0, including its synthetic warn-hook cases |

These are actual consumer paths, not a claim that all 16 P08 outer paths were identical
to that owner's prior fixture. The direct core regression separately asserts all six
required 259/260/268/278/277/290 lengths. No default path, hash, label or store was shortened.

## Actual old-record and extraction compatibility

A session-only fixture exported the accepted base's unmodified profile and snapshot
producers from local Git objects. Their actual outputs, not hand-authored stand-ins,
were then read by the candidate:

- Accepted P07 bootstrap created ordinary and explicitly extended selections with long
  homes/history. Candidate bootstrap returned identical references, canonical profiles,
  digests, generations and selected/current/history bytes, without rebinding.
- Accepted snapshot `create` and `bind` ran in separate real processes for ordinary and
  explicitly extended owner roots. Candidate CLI `verify` and `restore` retained exact
  old manifest/result bytes and owner strings and restored the original CRLF payload.
  This is compatibility of previously supported records, not a shorter-default acceptance test.
- AST comparison confirmed all existing P07 function/class definitions except the two
  compatibility wrappers were identical. This does not substitute for runtime tests.

`compat2` reran this evidence after the core commit. Raw references and before/after
hashes are retained in its artifact. No schema migration or old-record rewrite occurred.

## Commands and outcomes

The reproducible invocation form was the session-only isolation driver, followed by the
existing command/selector, for example:

```text
python -I -S -B <session-files>\p03_native_path_build.py
  --run <unique-run-id> [--depth <unchanged-fixture-depth>]
  test bash tests\unit\context-safety.sh
```

The driver records exact expanded argv, allowlisted environment, actual resolved paths,
exit status, stdout/stderr and pre/post source hashes. Table entries identify the real
commands executed; no full repository suite is claimed.

| Command / selected methods | Outcome and revision |
|---|---|
| `bash tests\unit\context-safety.sh` | Post-`ce7415f`: **28/28 PASS** |
| `bash tests\unit\snapshot-ownership.sh` | Post-`ce7415f`: **27/27 PASS** |
| `bash tests\unit\url-policy.sh` | Post-`ce7415f`: **5/5 PASS**, no network |
| Three original deep shell scripts listed above | Post-`ce7415f`: all exit 0 |
| `python tests\unit\profile-path-identity.py --root . <selected methods>` | Post-`ce7415f`: **selected 19/19 PASS**, not initially the full retained 20-method inventory |
| `ProfilePathIdentity.test_native_case_sensitive_sibling_root_is_rejected` | Initially excluded due to its directory-metadata mutation; after explicit `67d39f1` allowance, separately **1/1 PASS** under current permissions, verified native distinct siblings, exact fixture cleanup, no elevation |
| `bash tests\integration\universal-profile-context.sh` with the six methods below | **6/6 PASS**; tested source is unchanged in the committed extraction/fixture plumbing |
| `bash tests\integration\pack-source-target-resolution.sh` | `copy-pack2`: exit 0, actual copied installed resolver and data policy |
| `bash tests\unit\wiki-gen-idempotency.sh` | Exit 0, including the minimal copied parser and failure-before-output cases |
| `CopilotKit.test_swarm_wrapper_and_complete_source_resource_inventory` | PASS |
| `CopilotKit.test_joined_runtime_dependencies_refuse_incomplete_source_before_writes` | PASS, including mandatory native_paths dependency |
| `CopilotKit.test_joined_installed_dependencies_cannot_be_hidden_by_inventory_removal` | **BLOCKED/FAIL in initial setup**, described below; no shortened retry |
| `bash tests\unit\universal-trusted-tools.sh` without selectors | **INCOMPLETE, 300-second timeout**; not passing aggregate evidence |
| Four exact P01 dependency methods below, before cleanup extension | **4 ERRORs** in unchanged long-history cleanup; not 4 passes |
| Same four methods after separately authorized exact-root cleanup | **4/4 PASS**, then **4/4 PASS after `5fc657f`** at identical effective-path lengths |
| Actual accepted-record compatibility fixture | Post-`ce7415f`: PASS |

The six unchanged P07 consumer methods were:

```text
ProfileLifecycle.test_neutral_first_use_and_unbound_boundary
ProfileLifecycle.test_producer_fresh_process_delegated_handoff_and_cold_resume
ProfileLifecycle.test_documented_bootstrap_without_injected_host_id_pins_two_fresh_shells
ProfileLifecycle.test_default_home_long_runtime_keeps_fresh_shells_history_rebind_and_drift
ProfileLifecycle.test_validation_skill_executes_shared_contract_without_activation
ProfileLifecycle.test_explicit_roots_and_target_data_are_preserved
```

The four actual P01 dependency methods were:

```text
TrustedHooks.test_hostile_target_is_never_executed_by_any_resolver_caller
TrustedHooks.test_target_policy_is_data_and_changes_each_domain_decision
TrustedHooks.test_trusted_home_fallback_keeps_installed_pack_precedence
Vault.test_hostile_target_dry_run_uses_pack_data_without_destination_writes
```

The native P07 case method is a separate later observation, not retroactive evidence
for the earlier selected 19. Its fixture-only metadata allowance is not permission to
alter host/global policy or another directory. Injected case-distinct cases and native
link/junction tests remain separate evidence categories.

### Failure histories retained

The original P01 broad run timed out at 300 seconds; the driver had no completed test
result or final source-after record. A scoped process check found no running test
descendant (only the read-only query process itself matched). No name-based kill,
full-suite loop or shorter-root retry followed.

The four narrower methods then reached `TemporaryDirectory.cleanup` with four
`WinError 145` errors under their synthetic profile histories. Their bodies had no
reported assertion failure, but the aggregate was **FAILED**. Only after explicit
extension `67d39f1` did `5fc657f` change Fixture's cleanup registration. It captures and
rechecks the exact created name/resolved root, keeps the original paths and invokes
TemporaryDirectory's own readonly/error handling using the same-location native name.
Errors still propagate; no broad cleanup implementation or test-body change was added.
`copy-p01-targeted`, `copy-p01-followup` and `copy-p01-frozenxx` have equal-length run
names and all 18 effective preflight path lengths match. Earlier failed remnants stay retained.

`copy-pack1`'s test exited 0, but the scratch driver failed while printing a checkmark
through cp1252. Its raw output/result were already recorded; no aggregate pass is
claimed. Only scratch output encoding was corrected, and `copy-pack2` completed in a
new equal-purpose synthetic fixture. No product change was made to fix log rendering.

The classic adapter's three-selector run exited 1: two tests passed, then the third
failed at its initial `bin\li-copilot.py` private atomic writer, before its intended
inventory-removal assertion. `WinError 3` occurred publishing a long installed
`scaffolding\01-foundation\templates\swarm\agent-brief.template.md`.
That adapter I/O is **outside this core unit**. It remains blocked in the original
test; its engine, target depth and assertion were not changed. This report does not
claim installed inventory-removal acceptance or complete default-consumer closure.

## Optional P10 composition: diagnostic only

The authorized disposable composition used frozen
`c1de05c7f18770f34f950a8c4d4e194892da3291`, verified raw Git export, plus only:
`lib\native_paths.py`, `lib\context_safety.py`, `lib\profile_context.py`,
`bin\li-snapshot.py`. No P10 source function, migration parser, native installer,
resource list or transaction algorithm was repaired.

Actual `li-adapter.py init --source <source> --target <installed consumer>
--client copilot-cli`, **without `--store`**, exited 0 at the original dimensions:
fixture 94, target 113, default store 128. It reported a complete file transaction
and 427 managed files. Source bytes were unchanged; the resulting target/store
and exact overlay manifest are retained. No `check`, `recover`, caller/child bridge
or independent P10 acceptance follows from that diagnostic.

The diagnostic preceded the final relative-root correction. Three overlay hashes
match the final core's tested working bytes; its snapshot overlay was
`071767282347458e2e4d926ed5ee6c8e9ccf8fed0d8a876e07764206a3419163`,
whereas final snapshot bytes are
`7d5aaaca1a18777d7503b05d7900053c95ec41b0df378dc5b7b778694b564ebd`.
The difference moves the redundant link check after existing root resolution.
This observation is explicitly **not** a run of the final four-file composition,
nor a reason to avoid P10's later exact-dependency default init/check/recovery gate.

## Producer/resource identity seal

These SHA-256 values are over committed LF Git blobs, not CRLF checkout bytes:

| File | SHA-256 at final tested tree |
|---|---|
| `lib\native_paths.py` | `b4b8f541c91c40563f9cabfab433d3216e3d58e1167b357141b008e4769a90ed` |
| `lib\context_safety.py` | `e80cf6ac5b8edd0e97f865c05486da3c8a39ddb56c83e42eed09c04dd7d7176e` |
| `bin\li-snapshot.py` | `7d5aaaca1a18777d7503b05d7900053c95ec41b0df378dc5b7b778694b564ebd` |
| `lib\profile_context.py` | `353ba79537736ab8d2acb8da06fbb7bd731c19d697b02fbdd5702a73712291a1` |
| `bin\li-copilot.py` | `e39425fa78d66aeedd2f4163116989ab2e876cc09515f8b3ce157e66286df494` |
| `tests\unit\universal-trusted-tools.py` | `9c6aa481fd0f49802534bcf58161a9ba08126202c38537cdf856c9b1aafece3f` |

`product-commit.json`, `fixture-commit.json` and `final-source-seal.json` record all
16 paths, Git modes and separate working-byte hashes. The two bin Python entries
retain mode 100755; the new library is 100644. Source Git operations explicitly use
checkout-equivalent `core.autocrlf=true` / `core.eol=crlf`; fixture Git configuration
is isolated separately. Nothing was manually normalized, reset or amended.
The final seal verified the fixture follow-up changed no core product blob.

## Per-leaf handoff and limits

| Leaf | Evidence supplied; completion remains coordinator/reviewer-owned |
|---|---|
| A01.2.w1 | Two-export pure seam, exact trusted-sibling refusal, unchanged P07 policy/function AST and actual old ordinary/extended record/ref/digest compatibility |
| A01.2.w2 | Full long-path snapshot lifecycle, both publication operands, long parents/locks/observations, retention and existing corruption/interruption/late-edit/replay negatives |
| A01.2.w3 | Exact-root native fixture cleanup, authorized copied-resource lists and mandatory-entry additions; passing source-refusal cases, explicitly blocked installed-removal case |
| A01.4.w1 | Actual Windows owned bisect success/error at 283 characters; unchanged caller HEAD/index/config/content/modes; no persistent option |
| A11.1.w1 | Direct exact threshold cases plus real deep shell ownership/roundtrip/memory paths, full labels/keys/history retained |
| A23.4.p1 | Frozen implementation/evidence ready for original reviewer's complete scoped SPEC then QUALITY; no self-clearance |
| A23.4.p2 | Remains later P10 owner/integration work. The pre-final default-init diagnostic is not acceptance. |

No unresolved owned-product defect was identified in this self-pass; that is not
independent assurance. The blocked classic-adapter selector, historical timeout/error
runs and unrun downstream checks are explicit, not averaged away by the green counts.
Source/copy plumbing and P07 extraction must be included in independent review.

Every test/hook command had a non-inherited allowlisted environment with synthetic
HOME/USERPROFILE, Lintel home/packs/pointer/profile/audits/jobs/registries/state/sessions,
temp/cache, Git global config and hooks path. Actual resolver locations were checked
before the command. Scripts/fixtures that derive child homes stayed under those roots.
No unset-HOME isolation assumption, real-home inspection/rollback, private sync,
network, credentials, hook activation, global OS/Git setting, Python installation or
source edit during tests occurred. The existing memory/P01 hooks ran only as fixture
commands, not as registered host hooks.

Actual execution used Windows, Python 3.11.9, Git Bash 5.3.15 and Git for Windows
2.55.0 for fixture Git; source-object/commit operations used the existing app Git
2.53.0. Junction fixtures used explicitly selected installed PowerShell 7.
Python 3.9 grammar/deferred-annotation checks are not a Python 3.9 runtime run.
UNC identities are data-only cases, not network I/O. Other OS/runtime/host/model
acceptance, hard-crash durability and concurrent-writer atomicity are not claimed.
Native bare installation remains Python-free and untouched.

Raw evidence is in session `files\p03-native-path-build\`: per-run preflight,
resolved-path, source-before/after, result and stdout/stderr files; compatibility and
P10 overlay records; product/fixture commit manifests; final source/evidence seals.
The isolation/compatibility/composition drivers are session-only artifacts, not new
product tooling. Existing failed investigation and owner artifacts were not cleaned up.

**Next:** freeze this report-only head over `5fc657f`, give the original P03 reviewer
`417edac..5fc657f` for complete scoped SPEC then QUALITY, and let the coordinator
release exact dependencies to the later P08/P10 owners only after that review.
