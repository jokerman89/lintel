# P03 joined native-path core independent review

**Date:** 2026-09-21.
**Reviewer:** Same independent P03 reviewer, session
`d2f01e82-f00a-40fd-96e9-9294a8b01513`; no product implementation by reviewer.

**Scoped CORE specification:** PASS, before quality began.
**Scoped CORE quality:** PASS. **New findings:** P1 0 / P2 0 / P3 0.
**Integration readiness:** eligible to hand the exact core dependency to its downstream
owners, not full installed/default-consumer acceptance. The original classic-adapter
long-template installed/removal boundary remains **BLOCKED**. P10 A23.4.p2,
A13/P08, complete joined acceptance and final CI remain open.

## Immutable identity and authority

| Item | Exact identity |
|---|---|
| Authorized base | `417edacd0c6e3187cc3f8867eb2ff475111cabf2` |
| Sixteen-path core commit | `ce7415f6342220e49746880dd7338a6e7d9294ed` |
| One-file P01 fixture follow-up / tested product | `5fc657f14123daca9ec126cadc1e9d64ee60691c` |
| Report-only candidate / parent of this review | `8170c8e86d6d830c6b194ca48879504e3826d425` |
| Fixture extension authority | `67d39f10f10ef35014128a0c6ca15292668b8b23` |
| Preserved investigation | `990b0daa752fc36b1612e9c897f128bb1ca4cf88` |
| Accepted P07 implementation baseline | `4d0014639204e5b5ad84838272a840c5283e28d0` |
| Accepted P07 long-path review | `a745059786933c049a9fa52b74c0d2f5a9d19da1` |
| New review branch | `jokerman-microsoft-p03-joined-path-review` |

Verified a clean checkout before creating the new branch directly at `8170c8e`.
The earlier reviewer branches and reports remain at `d0f4552`, `98515a1` and
`2840012`; no reset, amend, discard or other-worktree edit occurred. Earlier bounded
P03 acceptance and the investigation remain historical evidence, not erased or
reinterpreted as proof of these later joined failures.

Read the complete 315-line repair report, complete investigation report, ADR-0031,
the appended P03 card at the base, and the narrow extension through local Git.
Read the accepted P07 long-path report, adapter/bootstrap instructions and current
memory/lessons, including L-037. The extension is authority, not an unreviewed product
overlay. Its commit is not silently substituted for the supplied candidate.

Full tracked-tree comparison found exactly the 16 core paths below plus the new
implementation report. Every other tracked blob and mode is unchanged from the base,
including protected review/provider/profile-schema/state/audit/memory/promote surfaces.
The follow-up changes only `tests\unit\universal-trusted-tools.py`; `8170c8e` adds only
`reports\P03-joined-path-repair.md` over `5fc657f`.

## Complete reviewed change

| Owned seam | Files and review conclusion |
|---|---|
| Pure representation | `lib\native_paths.py`: exactly `path_identity(PurePath) -> tuple[str, ...]` and `native_io_path(Path) -> Path`; accepted P07 representation logic, no I/O or authority. |
| P03 I/O and recovery | `lib\context_safety.py`, `bin\li-snapshot.py`: native operands at the filesystem boundary while logical roots and records stay separate; existing ownership, bounds and journal decisions retained. |
| P07 extraction | `lib\profile_context.py`: trusted sibling loading and exactly the two compatibility wrapper bodies changed. No profile/containment/schema/history/generation/digest algorithm changed. |
| Owned Git operations | `agents\engineering\RegressionDetective.md`: Windows-only per-invocation option on owned worktree/bisect/reset operations; caller operations and persistent configuration remain separate. |
| Direct documentation | `skills\context-save\SKILL.md`, `skills\safe-install\SKILL.md`: same-location I/O and explicit non-guarantees, not a shorter store, policy change or blanket installer claim. |
| Retained and added core tests | `tests\unit\context-safety.py`, `tests\unit\snapshot-ownership.py`, `tests\unit\profile-path-identity.py`: old assertions retained; exact-length/native/purity/compatibility regressions added. |
| P07 copied fixture | `tests\integration\universal-profile-context.py`: required resource plus exact-root cleanup only; scenario bodies and validation method unchanged. |
| P01 copied fixture | `tests\unit\universal-trusted-tools.py`: required resource plus authorized exact-created-root cleanup registration; test bodies/assertions/depth unchanged. |
| Other copied resources | `tests\integration\pack-source-target-resolution.sh`, `tests\unit\wiki-gen-idempotency.sh`: native helper added to their copied resources; no scenario rewrite. |
| Mandatory inventory entries | `bin\li-copilot.py::ADAPTER_RESOURCES`, `tests\integration\copilot-kit.py::JOINED_RUNTIME_RESOURCES`: one required-source entry each; no classic installer engine fix. |

AST comparison established that all prior P07 function/class definitions except
`_path_identity` and `_native_io_path` are identical to the base. That base's entire
`profile_context.py` is byte-identical to accepted `4d001463`. P07 test changes are
limited to `setUp` resource/cleanup plumbing and the added cleanup method; P01 changes
are limited to `Fixture.setUp`. Runtime producer/consumer tests below supplement, not
replace, those structural comparisons.

## Isolation, source fidelity and evidence

Every test invocation used a newly constructed allowlisted environment, not a copy of
the ambient environment. HOME/USERPROFILE, HOMEDRIVE/HOMEPATH, application directories,
XDG config/data/state/cache, TEMP/TMP/TMPDIR, Claude/Copilot/Gstack locations, LINTEL_HOME,
packs/pointer, audits, jobs/registries and Git configuration were explicit synthetic paths.
Inherited redirects were absent; `BASH_ENV`, `ENV`, `CDPATH` and `PYTHONPATH` were empty.
The hostile-PYTHONPATH case deliberately substitutes only its own disposable target.

Before each invocation, startup-free Bash sourced the trusted frozen path/resolver/jobs
readers with `LINTEL_JOBS_NO_INIT=1`; the collector checked 18 actual effective locations:
homes, Lintel home, packs/pointer/profile, global/hook/resolver audits, jobs, both registry
locations, state, sessions, repo, source, temp and cache. All resolved inside that exact
fixture. Python separately confirmed its actual home and temporary directory. Preflight
audit-directory creation was inside the same fixture. Test-created child environments
were inspected in the unchanged fixtures and remained descendants of these locations.
Unset values were not treated as isolation.

Tests ran from disposable exports of the exact candidate's Git blobs. Every exported
file was checked against its Git object, with modes recorded separately; bytes were
sealed again after execution. No test changed an exported source file. The real reviewer
checkout was not a runtime fixture. Archive operations explicitly selected raw LF Git
bytes; source checkout verification separately used checkout-equivalent Git/EOL settings.
No source file was normalized or reset.

The approved jq executable was read only from the supplied coordinator location and
SHA-256 verified as
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`.
Its directory was added only to the child PATH. Python observed **3.11.9** on Windows;
Git for Windows/Git Bash and the existing PowerShell 7 executable were used. No installation,
credential, network, global setting, host-hook activation or paid-model operation occurred.

Session artifacts are under `files\p03-joined-review\`: per-run expanded command,
allowlisted environment, resolved paths, Git-byte manifest, stdout/stderr, actual result
and exact-root cleanup records. The collector, compatibility and threshold probes are
session-only files, not new repository tooling. Successfully completed fixtures were
cleaned only through their recorded exact created roots, with errors unsuppressed.
Existing failed owner/investigation fixtures and real-home effects were not inspected
or cleaned.
The final 18-run evidence index, including the failed exact-dimension classic run, is
`evidence-index-final.json`, SHA-256
`3075f49961ee5c89c43b6e5f952d6495a12815445920628027521387bf71509e`.

## Stage 1: discriminating core evidence

### Exact original Python failures and same-path repair

An independent probe loaded the actual old helper from a verified export of `417edac`
and then the candidate helper. It exercised the same destination, not a shorter control.

| Required logical length/boundary | Actual old result | Actual candidate result |
|---|---|---|
| 259-character first reservation, then collision suffix | First succeeds; second raises `FileNotFoundError`, errno 2 | Existing first checkpoint preserved; `copy0002` reservation/read/write succeeds at 268 characters |
| 260, 268, 278, 277, 290 first reservations | Each raises `FileNotFoundError`, errno 2 | Exact logical destination retained; reservation, write and read succeed |
| Snapshot blob publication, temporary 218 -> destination 260 | Actual `os.replace` raises `FileNotFoundError`, errno 2 / WinError 3 | Both operands use same-location native spelling, original logical lengths remain 218/260, bytes verify and own temporary is removed |

The probe exits 0 after checking expected old RED and candidate GREEN; this does not
relabel the old product exceptions as success. Independent execution also covers the
long parents, selection/cooling, same-file comparison, explicit extended roots and
native ancestor/link/refusal tests in the complete 28-case context suite.

### Real deep checkpoint consumers

The unchanged shell scripts ran with their real repository keys, labels, defaults,
history and assertions. Actual paths were extracted from retained Bash traces.

| Script | Observed generated checkpoint lengths | Exit |
|---|---|---|
| `context-repository-ownership.sh` | 270, 278, 281, 283, 289, 292, **301** | 0 |
| `context-checkpoint-roundtrip.sh` | 279, 280 | 0 |
| `memory-v2.sh` | 292 | 0 |

These runs used synthetic TEMP lengths 142/142/143. The reviewer's initial independent
deep runs at TEMP 137/137/138 also passed but returned paths five characters shorter
than the published cases; they remain separate controls. The targeted later runs added
five characters to the outer fixture and established the exact published returned-path
dimensions. No product name/hash, script body, argument, assertion or default was
shortened. This is not a claim that every outer P08 path matched its historical run.

### Actual old producers, not invented records

The accepted base's real snapshot CLI created and bound ordinary and explicitly
extended-root records in separate processes. Candidate CLI verify/restore preserved
the exact manifest/result bytes and owner strings, restored the original CRLF payload,
removed only its owned newly created file and preserved unrelated user bytes.
Snapshot/result schema 1 and new restore schema 2 remained unchanged.

The accepted P07 CLI actually bootstrapped required `_default` profiles at ordinary
and explicitly extended selections. Candidate cold bootstraps returned exactly the
same references, canonical profile/digest/generation and current/selected/history
bytes, without rebinding. Actual retained history filenames were **425 characters**.
The old and new code operated on the same logical source/target/data for each comparison.

The complete snapshot suite additionally exercises long-store create/read/bind,
interruption/resume, per-file consumed authority, stale/tampered/foreign records,
late edits, locks, retention and exact pruning. Relative CLI root arguments remain
supported. No old record was hand-authored as a substitute for producer compatibility.

### Pure seam, policy separation and Git

The pure helper's two exported functions retain case and accepted drive/UNC identity,
reject unsupported namespace/ADS/reserved/traversal ambiguity, and perform no filesystem
lookup, resolution, root selection, permission/configuration decision or mutation.
Both exact-sibling loaders refuse missing, symlinked and target/PYTHONPATH substitutes
before product operations. P03 imports no profile internals and uses the shared identity
for its private logical projection/containment instead of a second namespace parser.

P03 still rejects all links/reparse paths and non-regular owned files. P07 still allows
its previously accepted in-root links and rejects escapes. The **full 20-method P07 path
run passed, zero skips**, including the existing native case-sensitive-sibling test.
That test enabled the attribute only on its own empty disposable directory under current
permissions, verified distinct objects and cleaned that fixture. No elevation or global
policy change was attempted. Injected alias/case/interruption cases remain separately
identified tests, not replacements for the native observation.

The actual bisect success/error recipe ran at its asserted **283-character ref-lock**
dimension. Caller HEAD, raw index/config, staged/unstaged/untracked content and modes
were unchanged. Owned worktree creation, bisect start/run/log and trap reset use the
Windows-only `-c core.longpaths=true` array. Read-only caller resolution is outside that
array; no local/global persistent setting or session-wide override was introduced.
Git is not represented as inheriting Python's path adapter.

## Per-leaf decision and integration readiness

| Leaf | CORE spec | CORE quality | Evidence and remaining boundary |
|---|---|---|---|
| A01.2.w1 | PASS | PASS | Two pure exports, exact trusted loading, unchanged P07 algorithms/error mapping and actual old ordinary/extended profile identity compatibility |
| A01.2.w2 | PASS | PASS | Full native snapshot I/O and exact 218->260 repair; long locks/journals/retention/prune and inherited ownership/interruption/replay negatives |
| A01.2.w3 | PASS for assigned core source/fixture seam | PASS for same seam | Resource inventories, copied P01/P07/pack/wiki consumers, refusal before writes, exact-root cleanup and unchanged scenario bodies verified; original deep classic installed/removal case remains BLOCKED outside the core engine scope |
| A01.4.w1 | PASS | PASS | Real 283-character owned bisect success/error and caller byte/mode/config preservation |
| A11.1.w1 | PASS | PASS | Exact direct threshold probes plus real unchanged ownership/roundtrip/memory consumers through 301-character paths |
| A23.4.p1 | PASS for scoped core/extraction/dependency handoff | PASS | Same independent reviewer, frozen source and actual compatibility/refusal evidence; coordinator integration still required |
| A23.4.p2 | NOT REVIEWED / OPEN | NOT REVIEWED / OPEN | Later P10 direct-I/O and original-path default init/check/recovery/caller-child acceptance, not implied by p1 |

The w3/p1 result is grounded independently in the shared-core and required-source/copy
checks, not a waiver of the failing classic writer. No missing core requirement is
counted as green through the shallow installed control described below.

## Stage 2: whole-core quality

Quality began only after the scoped specification results above. It covered all 16
paths and the exact one-file follow-up, including unchanged policy context around the
extraction, not only the new module.

| Area | Code and conclusion |
|---|---|
| Representation/loader | `native_paths.py:16-58`, `context_safety.py:23-36`, `profile_context.py:28-38`: pure, two-function shared seam; trusted sibling binding and explicit loader failure; no fallback to target code |
| Logical versus native operations | `context_safety.py:40-295`: native ancestry/stat/read/open/mkdir/temp/chmod/replace/iteration/samefile operations; temporary and iterated names projected onto retained logical roots |
| P03 recovery | `li-snapshot.py:35-183,197-435`: root/owner checks, both publication operands, locks, observations, journals, iteration and exact cleanup retain schemas/bounds/retry classes and consumed permission |
| P07 policy | `profile_context.py:667-695`: wrappers translate only representation `ValueError` to `PROFILE_IO`; all other functions/classes match accepted base, with runtime and actual producer evidence |
| Git separation | `RegressionDetective.md:91-109`: process-scoped Windows option throughout owned trial/admin/reset flow, no persistent configuration; real retained failure/success assertions |
| Fixture integrity | P01 `Fixture.setUp` captures/rechecks the exact created root and retains `TemporaryDirectory` readonly/error handling; P07 copy/cleanup plumbing does not change scenario logic; all selected consumers complete teardown |
| Bounds/error truth | Existing bounded selector DP, byte/candidate bounds, regular-file checks, URL pre-request validation, stale/replay refusal and no-success-on-failure tests remain and pass |
| Portability | Stdlib only, no new install prerequisite; Python 3.9 grammar/deferred-annotation checks pass, not actual 3.9 runtime; pure UNC/POSIX behavior is not native share/OS execution |

**Quality findings:** P1 0 / P2 0 / P3 0 within the authorized core.
There is no claim of whole-tree transactional atomicity, hostile concurrent-writer
containment, hard-crash durability or generic long-path support for unchanged callers.

## Commands and actual outcomes

Each command below ran through the session-only allowlisted driver with a separately
recorded preflight, source manifest and exit; expanded argv is retained per run.
Paths are relative to that verified export.

| Command/scenario | Actual reviewer outcome |
|---|---|
| `bash --noprofile --norc tests\unit\context-safety.sh` | 28/28 PASS, exit 0, including real native path and Git recipe assertions |
| `bash --noprofile --norc tests\unit\snapshot-ownership.sh` | 27/27 PASS, exit 0 |
| `bash --noprofile --norc tests\unit\url-policy.sh` | 5/5 PASS, exit 0, no network |
| `python -B tests\unit\profile-path-identity.py --root <source>` | 20/20 PASS, exit 0, zero skips including native case-sensitive fixture |
| Three unchanged shell commands in the deep table, `bash --noprofile --norc -x ...` | All exit 0; published path dimensions recorded; initial shorter controls separate |
| `bash --noprofile --norc tests\integration\universal-profile-context.sh <six selectors below>` | 6/6 PASS, exit 0, complete fixture cleanup |
| `bash --noprofile --norc tests\unit\universal-trusted-tools.sh <four selectors below>` | 4/4 PASS, exit 0, complete exact-root cleanup; no broad wrapper run |
| `bash --noprofile --norc tests\integration\pack-source-target-resolution.sh` | PASS, exit 0; actual copied resolver/source/default/target policy |
| `bash --noprofile --norc tests\unit\wiki-gen-idempotency.sh` | PASS, exit 0; copied parser and failure-before-output/idempotence |
| Classic adapter three selectors below, `python -B tests\integration\copilot-kit.py ...`, shallow TEMP 55 control | 3/3 PASS; not acceptance of the original blocked dimension |
| Same unchanged three selectors, exact original R74/TEMP79 dimensions, final frozen source | First two PASS; third FAIL in initial setup, process/aggregate exit 1, before the intended assertion; inner unittest fixture teardown completes |
| `python -I -S -B <session>\p03_joined_thresholds.py` | Expected original REDs and same-path candidate GREEN, collector exit 0 |
| `python -I -S -B <session>\p03_joined_compatibility.py` | Actual old snapshot/profile producers -> candidate readers PASS; ordinary/extended identities and record bytes preserved |
| Read-only AST/Git-object inspections | Two wrapper bodies only; scenario bodies retained; pure API and Python 3.9 grammar; exact all-tree scope and source hashes verified |

Six exact P07 selectors:

```text
ProfileLifecycle.test_neutral_first_use_and_unbound_boundary
ProfileLifecycle.test_producer_fresh_process_delegated_handoff_and_cold_resume
ProfileLifecycle.test_documented_bootstrap_without_injected_host_id_pins_two_fresh_shells
ProfileLifecycle.test_default_home_long_runtime_keeps_fresh_shells_history_rebind_and_drift
ProfileLifecycle.test_validation_skill_executes_shared_contract_without_activation
ProfileLifecycle.test_explicit_roots_and_target_data_are_preserved
```

Four exact P01 selectors:

```text
TrustedHooks.test_hostile_target_is_never_executed_by_any_resolver_caller
TrustedHooks.test_target_policy_is_data_and_changes_each_domain_decision
TrustedHooks.test_trusted_home_fallback_keeps_installed_pack_precedence
Vault.test_hostile_target_dry_run_uses_pack_data_without_destination_writes
```

Classic adapter selectors:

```text
CopilotKit.test_swarm_wrapper_and_complete_source_resource_inventory
CopilotKit.test_joined_runtime_dependencies_refuse_incomplete_source_before_writes
CopilotKit.test_joined_installed_dependencies_cannot_be_hidden_by_inventory_removal
```

A preliminary read-only protected-file inspection stopped with Git exit 128 because
the reviewer supplied a nonexistent bridge filename. It was replaced with a complete
tracked-tree comparison, which passed and verifies every unchanged file without guessed
names. This was not a product test failure or missing product dependency.

## Known blocked and unrun boundaries

**Classic long-template installed/removal remains BLOCKED, now independently reproduced
on the final tree at the original dimensions.** The core changed only the required-source
tuple, not the private writer at `bin\li-copilot.py:840-849`.

The coordinator relayed retained dimensions and corrected the earlier owner's provenance:
`resource1` was a **pre-commit working-source run over `417edac`**, from
12:20:05 to 12:20:56 UTC; core commit time was 12:36:29 UTC. Its relevant engine and
test content match the later final code, but its complete source manifest differs in
the later snapshot correction. It is not retroactively a `ce7415f`/`5fc657f`/`8170c8e`
execution. The retained owner stderr SHA-256 is
`e2160aa469965c5c888a8a0ae2d3ae5e129c47488ac4f4baf72135f040cd1066`.
This is relayed provenance, separate from the reviewer execution below.

The reviewer first ran the unchanged three selectors with synthetic TEMP length 55;
all three passed. That result is retained only as a shallow control. After receiving
the original dimensions, the reviewer ran the exact top argv once more using verified
`8170c8e` source, outer fixture length 74 and its `temp` child length 79:

| Actual final-tree path | Characters |
|---|---:|
| Outer fixture / TEMP | 74 / 79 |
| Copilot TemporaryDirectory / copied source | 109 / 116 |
| Failing method's unchanged target / installed bundle | 182 / 197 |
| Publication parent | 239 |
| `os.replace` temporary / `agent-brief.template.md` destination | **256 / 263** |

The first two selectors pass at these original lengths. The third fails during its
initial `run_cli()` with process 1 / WinError 3 in the ordinary classic atomic writer;
its intended inventory-removal assertion is not reached. The aggregate is
`FAILED (failures=1)`, exit 1, not a passing core aggregate. The inner unittest-owned
directory is removed by its actual teardown; the outer failed fixture is retained.
Paths were decoded from the exception with `ast.literal_eval` and lexical
`ntpath.normpath`, not measured as escaped repr text or resolved through the filesystem.
Reviewer stderr SHA-256:
`921d7ed829766d4359abbc28abd56dd0640e09af96a5ef488f80c43a11dedda8`.

This is a **classic adapter 256->263** boundary, not the repaired **snapshot
218->260** boundary or P10's 113/128 target/store dimensions. No engine/test/target-name
edit, shortening after failure or waiver occurred. The source/copy criteria of this
core unit are independently evidenced; the deeper installed/removal and full default
consumer checks remain blocked for their actual owner.

**P10 composition is not final evidence.** The retained diagnostic used frozen
`c1de05c7` plus four core overlays before the final snapshot relative-root correction.
Its snapshot overlay hash starts `071767...`, not the final
`7d5aaaca1a18777d7503b05d7900053c95ec41b0df378dc5b7b778694b564ebd`.
Its 427-file default init at 94/113/128 dimensions is not a final-four-file composition
run and proves no check/recover/caller-child acceptance. No P10 composition was run
or silently adopted here.

The historical P01 300-second broad-wrapper timeout remains INCOMPLETE and its four
pre-extension cleanup ERRORs remain failures. This reviewer's later four-method pass
does not relabel those runs. Likewise the owner's P07 selected 19/19 and later native
1/1 remain separate observations; the independent 20/20 above is this new run.

P08 shell27 remains invalid with unknown real-home effects; no inspection or rollback
of those effects occurred. A13, P08 routing/consumers, P10 direct I/O, full default
installation, final joined consumers, CI and enterprise/human gates are not approved.
No full repository suite, network/GitHub, credentials, private/global state, OS/global
Git setting, nested agent or actual customer/production operation was used.

Native evidence is the observed Windows/Python 3.11.9 host with current permissions.
Python 3.9 grammar is not a runtime run, UNC data is not a network-share test, and pure
POSIX behavior is not Linux/macOS execution. Hard-crash durability, concurrent-writer
atomicity and actual browser/model behavior remain unverified.

## Disposition

Accept the scoped native-path **CORE** range `417edac..5fc657f` for coordinator
integration and explicit downstream handoff. The whole authorized extraction/I/O/
fixture unit has independent spec and quality evidence. Preserve all prior reports,
rejected/blocked observations and the separate installed/default-consumer gates.

Only this review report belongs in the local commit. Shared leaf status, integration,
remaining dependencies and final delivery decisions remain with MasterSession.

**Cycle position:** REVIEW (scoped CORE spec PASS, quality PASS) -> coordinator
integration and separately owned P10/direct-consumer acceptance; no SHIP clearance.
