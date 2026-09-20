# P07 joined Windows long-path independent review

**Date:** 2026-09-20

**Reviewer:** Same independent P07 reviewer, session
`a7d78944-c02c-4909-a060-2c4f2a754b00`. No product implementation or repair by reviewer.

**Verdict:** **PASS for this scoped long-path repair, specification then quality.**
No actionable findings: **P1 0 / P2 0 / P3 0**. This does not grant final
P07/Universal, P05/P08/P10, A22.7/A24/P14, CI or enterprise/host-enforcement acceptance.

| Gate | Actual disposition |
|---|---|
| Stage 1: A07.3.l1-l3 / A07.4.l1 scoped specification | PASS before Stage 2 began |
| Stage 2: whole four-file repair and relevant shared-profile context | PASS; no specification counterexample found during quality |
| A07.4.l2: same-reviewer repair review and actual installed consumer | PASS within this immutable checkpoint; coordinator integration remains separate |
| Real company policy, other host/runtime/platform and final integrated review | NOT RUN / OPEN, not inferred from local results |

The earlier `a8de574` component acceptance and `3d8e715` report remain accepted
within their original bounds. The newly reproduced joined default-home failure
was not part of that earlier evidence. Neither the earlier acceptance nor the
historical method-OK/teardown-ERROR run is rewritten by this report.

## Exact candidate, baseline and isolation

| Identity | Exact value |
|---|---|
| Joined baseline and appended repair-card authority | `0ecdb520ddbfc628cc049860608484866986e3b9` |
| Baseline tree | `83c7ea084ea4e26acbeb1132c09298aaf1a71c3b` |
| Coordinator-owned cleanup dependency source | `0eab731c381985e21ef5b5520d7f93f49d3a8216` |
| Writer's separate cleanup dependency / direct product parent | `28b49add9b40e13d01a49ea9135b98f419be3ef3` |
| Frozen product under review | `4d0014639204e5b5ad84838272a840c5283e28d0` |
| Frozen product tree | `d23ae250107cf867cf285ec87abbe3b302357db0` |
| Report-only candidate / parent of this review commit | `da614cad615a06c52d2aefd32818c082f9557c0e` |
| Report-only candidate tree | `10852d3e7a548a60ffd288d119a6c4de452cf4d5` |
| New local review branch | `jokerman-microsoft-universal-profile-long-path-review` |

Clean status was verified in the original reviewer checkout and all three prior
review worktrees before creating a new worktree at exact `da614cad`. The new
checkout is `.claude/runtime/review-worktrees/p07-long-path-4d00146` under this
reviewer's workspace. No reset, amend, discard, builder/master edit or remote
operation occurred.

The earlier review refs/artifacts were preserved at:

```text
9edf8c1e44c33a0530772eefd2d6537182d7fdda  P07-component.md
ce386bad173c85d2628a89f26542d5608026f5c7  P07-recheck.md
e4285fd199969112e042b0dfa5b03994b321a81b  P07-final.md
3d8e715a033083df67651a21578a2153422385cb  P07-windows-final.md
```

Authority was resolved from current `work.json` to `spec.md` and `plan.md`,
`packages/P07.md`, ADR-0029 and the complete appended **Joined installed-source
long-path repair** section of `packages/P07-windows-repair.md` at `0ecdb520`.
The complete current `reports/P07.md` was read, including its retained history.
Current adapter/bootstrap instructions, changed repository guidance and relevant
memory were read; no private operator configuration was inspected.

### Attributable delta

The owned product delta from `28b49add` to `4d001463` is exactly four files,
**+357/-46**:

| File | Delta | Reviewed purpose |
|---|---:|---|
| `lib/profile_context.py` | +71/-42 | Native same-location I/O; guarded runtime stat/read/list/write/cleanup/lock operations |
| `docs/concepts/pack-resolver.md` | +33/-1 | Long-path contract and limits, without identity/store migration |
| `tests/integration/universal-profile-context.py` | +86/-0 | Actual long default-home lifecycle |
| `tests/unit/profile-path-identity.py` | +167/-3 | Six added long-path cases and retained/extended boundary cases |

The separate cleanup dependency adds exactly seven lines to
`tests/integration/copilot-kit.py:42-52`. Its source and cherry-picked file were
compared and match. It uses the same resolved, owned sandbox's native spelling
while retaining `TemporaryDirectory` cleanup and readonly/error handling. The
installed test body and default-home scenario are unchanged from `0ecdb520`
(diff and AST equality verified). This dependency is **not P07 product work** and
must not be duplicated during integration.

`da614cad` differs from `4d001463` only in `reports/P07.md`. This reviewer writes
and commits only this new review report. Shared plan/state, earlier reports,
product source, tests, installer and other packages remain untouched.

## Stage 1: exact failure and repaired behavior

The baseline was independently materialized with
`git archive --format=zip 0ecdb520ddbfc628cc049860608484866986e3b9` in a disposable
synthetic root. The **unchanged** installed method was executed there:

```powershell
$env:LINTEL_TEST_BASH = 'C:\Program Files\Git\bin\bash.exe'
python -B -s tests\integration\copilot-kit.py CopilotKit.test_joined_installed_profile_is_pinned_across_fresh_shells_and_detects_drift
```

Actual baseline output:

```text
Ran 1 test in 10.953s
FAILED (failures=1)
AssertionError: 2 != 0
{"code":"PROFILE_IO","message":"local profile I/O failed: The system cannot find the path specified","schema_version":1,"status":"error"}
```

The test process exited **1**; the bootstrap returned **2**. The reproduction
wrapper exited 0 only after checking that exact expected RED. This is not a passing
baseline. The archived snapshot and its owned test fixtures were cleaned.

On the frozen candidate, that same command returned **0**, with **1/1 PASS,
17.762s, zero skips**, including complete `tearDownClass`. It used the real
installed source bundle, `profile-consumer` target, repository-required `_default`,
and documented default target-local `LINTEL_HOME`; no short-home or durable-name
workaround was supplied. Fresh shells reuse the exact reference, same-mtime
manifest drift rejects without success output, restoring bytes resumes the
original pin, and the unused synthetic operator home remains empty.

The builder's direct installed-Python RED trace of temporary length 220/history
destination length 274 and WinError 3 is accurately retained in its report. That
specific trace was **not independently replayed here**; the unchanged real installed
baseline failure above was. Separate reviewer Python probes then exercised the
repaired API without Bash as described below.

### Per-leaf specification and quality

| Leaf | Stage 1 | Stage 2 | Evidence / preserved behavior |
|---|---|---|---|
| A07.3.l1 | PASS | PASS | Exact unchanged installed baseline RED independently reproduced. Current actual method plus teardown is GREEN; no shorter fixture/home/store substitution. |
| A07.3.l2 | PASS | PASS | Same-location native paths cover final names, long parents/temp/locks, stat/read/list and writes. Independent resolved profile and digest equal the baseline computation at the same logical roots. Durable filenames and ordinary persisted keys remain unchanged. |
| A07.3.l3 | PASS | PASS | Fresh-shell pin reuse, long cold history, explicit rebind, same-time drift and missing-current refusal verified. Independent required-policy recovery advances generation rather than recreating generation 1. |
| A07.4.l1 | PASS | PASS | Actual case-distinct siblings, symlinks/junctions/deep ancestors, outside-root/no-write, namespace/ADS/traversal, busy/incomplete state and injected-interruption controls retain refusals. UNC and injection evidence are labeled below. |
| A07.4.l2 | PASS in scoped checkpoint | PASS in scoped checkpoint | Same independent reviewer completed specification before quality and executed the actual installed consumer. Coordinator must still integrate the exact owned change and verify its resulting tree. |

### Independent identity, history and boundary probes

An additional synthetic required `_default` consumer used the documented default
home and a deliberately long target. Observed native logical lengths were:
**current parent 284, history filename 364, lock 310 characters**.

The reviewer loaded the baseline helper from its exact Git object in memory
(read-only) to compute the expected profile against the same source/target/data,
then compared the repaired helper's profile and digest exactly. Native I/O aliases
did not appear in stored roots, manifest provenance or input-hash keys. The
history filename remained `1-<unchanged-64-hex-digest>.json`; generation, schema,
context key and storage location were unchanged.

Repeated cold bootstrap retained current, selected and history bytes without
rebind. After deleting only the synthetic current file, `create=True` refused
recreation. An incomplete history entry then blocked reason-bearing recovery
without changing that entry or the older record. Removing that fixture-only
incomplete entry allowed explicit history-backed recovery to generation 2, with
the same required policy, profile/digest and older bytes. The stale generation-1
reference remained rejected.

A real directory symlink beyond the legacy path length pointed outside both
approved roots. Both the guarded runtime **read** and write were rejected;
the outside file's existing bytes were unchanged and no outside write appeared.
This supplements, rather than substitutes for, the retained path suite.

## Stage 2: bounded repair quality

Quality began only after the scoped specification results above were established.
It reviewed the **entire repair**, the shared configuration/input/selection/storage
context, relevant unchanged shell callers and direct docs/tests. This was not a
repeat broad audit or a replacement of the previous whole-component review.

| Area | Source and conclusion |
|---|---|
| I/O identity and containment | `profile_context.py:689-719`: one recognized native alias operation, a guarded runtime wrapper, actual native resolution of long ancestors and exact-component comparison against approved roots. No prefix stripping, case folding, storage relocation or system-setting change. |
| Input reads and pack discovery | `:332-380`: native access is separate from logical input/provenance bookkeeping. Required error semantics and source precedence remain. Direct shared consumers passed the preservation scripts. |
| Record/history reads | `:722-808`: configuration is carried into runtime reads; native listing entry names are mapped back to logical history paths; corruption/conflict/incomplete and latest-generation checks remain. No independent history parser or silent first-use fallback. |
| Locks and atomic publication | `:811-854`: guarded parent/temp/lock/replacement/cleanup calls, same durable destinations, individual atomic replacement, no lock stealing. Selected-before-context transaction order remains at `:942-984`. No claim of a hostile-concurrency sandbox or tamper-proof evidence. |
| Failure propagation and cleanup | Injected replacement denial propagated through both direct write and CLI. Existing target bytes and an unrelated `.profile-*` sibling were preserved; only the operation's actual temporary and lock were cleaned. A later explicit write succeeded. CLI returned status 2, structured `PROFILE_IO`, no success stdout or pin. |
| Dependency and portability | No new helper imports or third-party/runtime dependency; helper imports are stdlib. Python 3.9 grammar and 3.11 compilation passed, not actual 3.9 execution. The non-Windows adapter branch returns its input unchanged; a pure branch probe is not a POSIX OS test. |
| Tests and documentation | `pack-resolver.md:208-236` describes native I/O separately from identity and labels limits. All 44 earlier lifecycle method names and 13 earlier path methods remain; inventories are now 45/19. Assertions were strengthened rather than discarded. |

**Stage 2 findings: P1 0 / P2 0 / P3 0.** No specification counterexample was found
after quality started, and no product repairs were made. There is no online
dependency/security certification or claim of unobserved host enforcement.

## Exact checks and results

All executions were tied to the clean `da614cad` checkout whose product is
`4d001463`, except the explicitly identified archived baseline RED. Tests were not
piped through `head`/`tail`, and their exit statuses were checked.

Windows Python **3.11.9** and Git Bash were used. Per-process settings included
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONNOUSERSITE=1`, cleared `BASH_ENV`/`ENV`, and
synthetic profile roots. Relevant inherited LINTEL/CLAUDE selectors were cleared
before the test batches. Bash runners used `--noprofile --norc`; the installed
method's actual child invocation was left unchanged.

The authorized jq binary was SHA-256 verified before execution:

```text
C:\Users\jokerman\reference-repos\copilot-worktrees\jokerman-session-setup\jokerman-microsoft-fictional-broccoli\.claude\runtime\tools\jq-1.8.2\jq.exe
SHA-256 a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627
jq-1.8.2
```

Its directory was prefixed on PATH only in test/probe processes. No installation
or global environment/configuration change occurred.

| Command/scenario | Actual outcome |
|---|---|
| Exact installed method shown above, archived `0ecdb520` | Expected RED: process 1 / bootstrap 2, `PROFILE_IO`, 10.953s |
| Same installed method, candidate | PASS: process 0, 1 method, complete teardown, 17.762s, zero skips |
| `bash --noprofile --norc tests\unit\profile-path-identity.sh` | PASS: 19/19, 10.068s, zero skips |
| `bash --noprofile --norc tests\integration\universal-profile-context.sh` with the 19 exact selectors below | PASS: 19/19, 245.591s, zero skips |
| Nine preservation scripts below, sequential with status check after each | PASS: 9/9, zero skips, actual jq assertions executed; 30 unique ADRs |
| Independent inline `python -B -s -` identity/history/deep-link probe | PASS: parent284/history364/lock310, unchanged baseline profile/digest and cold bytes, required recovery and read/write refusals |
| Independent inline `python -B -s -` interruption/CLI/pure-POSIX-branch probe | PASS with explicitly injected failure and pure branch limits; unrelated sibling preserved, no own temp/lock leakage |
| `python -B -s bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS: explicit approved map |
| `ast.parse(..., feature_version=(3, 9))` and `compile(...)` | PASS for helper, lifecycle/path tests and CopilotKit; grammar/3.11 compile only |
| `git diff --check 0ecdb520ddbfc628cc049860608484866986e3b9 HEAD` before report creation | PASS |
| Installed-method AST equality / test-name preservation / dependency diff | PASS: unchanged method; 44->45 and 13->19 retained; same seven-line cleanup dependency |

Exact focused lifecycle selector arguments (one runner invocation):

```text
ProfileLifecycle.test_default_home_long_runtime_keeps_fresh_shells_history_rebind_and_drift
ProfileLifecycle.test_neutral_first_use_and_unbound_boundary
ProfileLifecycle.test_missing_invalid_and_incompatible_required_pack_never_become_neutral
ProfileLifecycle.test_all_selection_entrypoints_reject_missing_and_replaced_pin_in_parent_and_child
ProfileLifecycle.test_all_selection_entrypoints_reject_child_rebind_until_explicit_verify
ProfileLifecycle.test_explicit_recovery_requires_unambiguous_untampered_history
ProfileLifecycle.test_retained_latest_generation_rejects_current_rollback_without_expected_reference
ProfileLifecycle.test_id_only_create_cannot_reset_missing_context_with_retained_history
ProfileLifecycle.test_python_create_true_distinguishes_initial_binding_from_lost_history
ProfileLifecycle.test_bootstrap_rebind_explicitly_recovers_latest_required_pin_and_updates_children
ProfileLifecycle.test_concurrent_rebinds_publish_current_and_selected_as_one_transaction
ProfileLifecycle.test_rebind_recovers_history_backed_stale_selected_reference
ProfileLifecycle.test_rebind_preserves_other_selection_and_rejects_unbacked_recovery
ProfileLifecycle.test_reference_only_resume_controls_accessors_and_inherited_process_with_new_host_id
ProfileLifecycle.test_documented_bootstrap_without_injected_host_id_pins_two_fresh_shells
ProfileLifecycle.test_concurrent_no_id_bootstraps_share_one_binding
ProfileLifecycle.test_same_mtime_manifest_parent_pointer_and_deleted_parent_are_drift
ProfileLifecycle.test_explicit_roots_and_target_data_are_preserved
ProfileLifecycle.test_structured_values_whole_block_inheritance_and_provenance
```

Each preservation path was invoked as
`bash --noprofile --norc <path>` from the candidate:

```text
tests\unit\enterprise-pack-resolution.sh
tests\unit\pack-inheritance-depth-3.sh
tests\shape\pack-resolver-fallbacks.sh
tests\integration\pack-source-target-resolution.sh
tests\integration\enterprise-pack-impact.sh
tests\shape\extension-pack-contract.sh
tests\unit\capture-vault-sink.sh
tests\unit\brief-forge-evaluator-runs.sh
tests\shape\adr-numbers-unique.sh
```

The shape fallback entry executes its retained unit scenarios. The independent
selection deliberately targets changed persistence and affected readers; **the
builder's complete 45/45 run was not rerun or claimed as this reviewer's execution**.
The complete method inventory was checked, meaningful shared-reader preservation
cases were executed, and the earlier accepted component evidence remains separate.

## Evidence levels and remaining boundaries

Native Windows evidence includes actual installed bootstrap, long parent/temp/
lock/destination I/O, stat/list/read/history, real processes, real case-sensitive
distinct sibling directories, symlinks/junctions and deep ancestors. Fixture-only
case attributes and temporary roots were disposable and cleaned.

Pure drive/UNC namespace comparisons are not live-share access. Alias-injection
tests substitute spelling only; interruption probes deliberately inject a
replacement failure. Neither is labeled an observed production outage. The
non-Windows pass-through probe is pure; actual Linux/macOS and Python 3.9 runtime
were not executed. No `LongPathsEnabled` setting or network share was changed.

The repair preserves F01-F04 protections in the affected executed cases; it does
not claim a newly run real delegated model session, automatic different-target
transfer, or a new whole-component/platform acceptance beyond this narrow join.
Existing short-home overrides are not evidence for this repaired default-home path.

No private/global profiles, credentials, accounts, network/publication, paid models,
release, hooks, nested agents, shared plan/state or other-source edits occurred.
Only specifically owned synthetic snapshots/fixtures were cleaned, never a broad
temporary root. ADR-0030's no-Python **installation** decision is separate from this
already-Python runtime; no installer dependency decision was changed.

**Handoff:** integrate only the owned `4d001463` repair into the coordinator's
chosen sequence, accounting for the already separate cleanup dependency, then
verify resulting product blobs and the actual joined consumer. P05/P08/P10 and
final A22.7/A24/P14, cross-platform/runtime, CI and human/company acceptance remain
separate. This sole report is a local report-only child of exact `da614cad`.

**Cycle position:** REVIEW (scoped joined long-path spec and quality PASS) ->
coordinator integration and remaining acceptance gates; no SHIP clearance.
