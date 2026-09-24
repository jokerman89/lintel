# P10 final independent review: a2df202

**Date:** 2026-09-24. **Reviewer:** the same independent session
`1578dfd8-f239-4eba-989b-3c4bde3e5792`; not the implementer, no nested agents.
**SPEC: PASS. QUALITY: PASS. COMPLIANCE: UNVERIFIED, clearance blocked.**
F05 and F06 are closed; F01-F04 and B01 retain their independently established
closures. Current product findings: **P1 0, P2 0, P3 0**. This completes the
same-reviewer continuation of the first whole-P10 quality review; it does not
rewrite the failed quality attempt at `2685bd57`.

The compliance evaluator passed nine observed scoped controls but returned
`unverified`, `blocked: true`: required-policy source/version/applicability has
not been established within this no-private-profile authority. A live dependency
advisory check is also unverified. The supplied review authority and neutral test
fixtures are not substitutes for an active organization policy. This report
does not clear A13, final integration, deployment, or human approval.

## Immutable scope and attribution

| Item | Identity |
|---|---|
| Repair authority | `13eda0854095ecf45ec501fe5de25a9b614403ba` |
| Product | `a2df202108e25702b96f95e7f5b39286355e6095` |
| Product tree | `6eb50f94febeb2e8fa42eb1c504f1ffec372b170` |
| Sole product parent | `72cf78a5dd294228127b864f9c5705ffa855dd9f` |
| Reviewed report-only child / required parent of this report | `56346ad39b6c8e0a60bb6b01a070f099d03150dd` |
| Builder report Git-byte SHA-256 | `c95590ba0928170aaaf7b3d8ab804b1c5607c395901a31c36ba68c8be2d5f4aa` |
| Previous independent report commit | `2685bd570c04002b46f15f1c467e79d28b73d8c2` |
| Previous independent report Git-byte SHA-256 | `46dc734e17e5cbf6f7b328b1b6552a919f761d2a5e97643adb6a532793cf375f` |

The worktree was pinned clean at the report-only child, without reset, amend or
discard. The previous report ref `review-p10-dea-frozen-2685bd5` is retained.
The sole new repository output is this report. Product, tests, shared plan,
memory, reducers, earlier reports and original failed fixtures were not repaired.

The selection remains the original 48 P10 paths from `a73cf9ee38977501c201225d8269dac3668c1080`
relative to `fb96f71342f7994c42bdfc7cd61e6d452e6acb54`, plus the separately
authorized `acf97f1c` profile-context fixture: **49 surfaces, 12,959 current lines**.
The accepted coordinator/core/Git/provider dependencies remain separately
attributed, not counted as original P10 authorship. Original A12 parents and
all ten subleaves govern, with the mapped spec/plan, ADR-0030, CP-02/04/12/16,
RU-06/07/08/11 and relevant lifecycle inventory.

The present repair changes eight selected files, +402/-69. The other 41 selected
surfaces and applicable previous evidence were rebound rather than rerun.
All 967 raw Git source blobs were exported and verified; other than the eight
product files and builder report, 958 entries remain unchanged. Prior 42 kit and
65 lifecycle method ASTs are unchanged. The shared transaction/B01, context-safety,
F02 producer, dispatcher, ownership schemas and P07/provider contracts are unchanged.

| Current changed path | Git-byte SHA-256 |
|---|---|
| `bin\li-copilot.py` | `b64a03f2a86bf95ceda8a5d6e882a623efe0af54cf2802d5eba09b4f6a373278` |
| `docs\copilot.md` | `808e3f979d53de6f6e658c450763718036ef9d3e57c6a1e5a844e98ef660e0fb` |
| `docs\native-installation.md` | `951a66f80faafe089cd1d7754bd9a4a71a0547d161275cd5fe3a947fc65091d8` |
| `install\native.ps1` | `a9e8e110a40621091fbe425f2a53b9ba6fdc25cbb8bab51e6a122fb7c19175e5` |
| `install\native.sh` | `11a44b51e8dae656763726e9c4f9ca2f7d125a7ae01221db19ba724eb9e9ae09` |
| `tests\integration\copilot-kit.py` | `610188aaa80203aba495cdf7136c464113960f65655d630ad0bf73e31f518846` |
| `tests\integration\universal-lifecycle.py` | `4b58676cfcc568762928d045a2142451731b49a0528e205454f9f066582285ee` |
| `tests\unit\native-receipt.ps1` | `89624b0ead1aca149e549b098b73ccf1f29a0a7d0c61c35f439ee9f34a6a6cbd` |

Builder RED/GREEN, full-kit and stopped attempts are preserved as builder
observations, not substituted for independent acceptance.

## Original specification matrix

| Original leaf | Verdict | Bound evidence and coverage |
|---|---|---|
| A12.1.a - scaffold and diagnostics | PASS | Retained installed-source/working-target, missing-source, required caller-policy and diagnostic controls; current real canonical parent-to-child caller. |
| A12.1.b - pack and profile | PASS | Unchanged structured profile/pin/switch controls and real copied validation skill, including malformed required policy, effective result, no activation and exact cleanup. |
| A12.1.c - roles and personas | PASS | Retained actual role/persona operations, private source boundaries and required caller/target policy separation; no global installation or private-pack copy. |
| A12.1.d - migration and recovery | PASS | F01 malformed inventory, F02 producer ownership, F03 native observations and F04 finite canonical destination mapping closures; explicit owned migration/recovery controls. |
| A12.2.a - fresh and repeated installation | PASS | Retained native/classic/Git controls; current default target113/store128, publication218->260 and canonical history304 controls. No shortened replacements. |
| A12.2.b - preservation and conflicts | PASS | F05 original real-CLI refusal and 28 intervention refusals; current project prose/update; retained unowned collisions, old managed ownership, config/roles/packs/hooks/brand, EOL and link controls. |
| A12.3.a - interruption diagnosis | PASS | Actual incomplete and failed publication histories retained; bounded journal-only B01 evidence and truthful nonzero failure, not success from a label change. |
| A12.3.b - verified owned recovery | PASS | Current default explicit recovery; retained interrupted operations, root/store binding, foreign/corrupt states, later user edits and consumed replay permission. No automatic rollback or lock theft. |
| A12.4.a - host and uninstall limits | PASS | F06 both-performer strict inventory controls; native unit; retained real no-Python installation, host/Git refusal, data-only shared TSV, exact cleanup and truthful uninstall limits. |
| A12.4.b - historical migrations and aliases | PASS | Actual aliases registry payload; retained opt-in aliases and truthful missing/malformed/overdue/unknown migration and F01/F03/F04 reader observations. |

**A12.1, A12.2, A12.3 and A12.4: PASS. No original selected acceptance control
remains missing.** Platform and compliance limits below are not silently converted
to execution claims. The original failure/recovery contract is supported by actual
failed incomplete states and explicit recovery evidence, not merely later positive
non-reproductions.

## Newly executed independent checks

These are separate observations, not a synthetic combined aggregate or a new
full-suite result. Every product import/call used the verified allowlisted
synthetic environment, fixed interpreter binding, captured output and stable
exact-source export.

| Selection | Actual result | Capture / preservation |
|---|---|---|
| Four added F05 adapter methods | 4/4, exit0, 503.530s; 32 real subprocesses | 28 exit17 refusal rows, 3 exit0 and 1 exit1; exact named-fixture cleanup, outer equality, source967. |
| Original F05 real-CLI counterexample | CLI exit1; private verifier exit0 | Original expected state retained, late edit preserved, no store and no ready output. Exact current target retained. |
| Native PowerShell receipt unit | Product exit0, 6.906s | Empty stderr, named fixture cleaned, source967; outer wrapper is separately FAILED below. |
| Three added F06/payload methods | 3/3, exit0, 772.162s; 40 real subprocesses | 18 exit0, 22 exit1; both actual performers, exact cleanup, outer equality, source967. |
| Three original adapter preservation methods | 3/3, exit0, 615.536s; 12 real subprocesses | 10 exit0, 2 exit1; original dimensions, cleanup, outer equality, source967. |
| Pure shared compliance evaluator | Process exit0; result `unverified`, `blocked: true` | Nine scoped controls pass, one unresolved required-policy blocker, one advisory unverified; source and synthetic maps unchanged. |

F05 selectors:

```text
CopilotKit.test_f05_fresh_late_creations_refuse_before_publication
CopilotKit.test_f05_consumer_late_input_changes_refuse
CopilotKit.test_f05_installed_late_changes_and_guards_refuse
CopilotKit.test_f05_post_admission_guard_is_a_labelled_limitation
```

Native and original-preservation selectors:

```text
NativeInstallLifecycle.test_native_inventory_refuses_every_malformed_record
NativeInstallLifecycle.test_native_unterminated_final_record_is_still_verified
NativeInstallLifecycle.test_native_payload_installs_and_verifies_alias_registry
CopilotKit.test_original_default_113_128_paths_init_check_and_owned_recovery
CopilotKit.test_canonical_default_caller_child_keeps_verified_parent_and_unbound_child
CopilotKit.test_full_protocol_is_portable_and_project_prose_survives_update
```

Native selected execution used `--native-small`, the frozen real aliases and
metadata bytes, forced actual Bash and explicit approved PowerShell. It is not
advertised as a new full-payload/no-Python aggregate. The independent retained
full native/no-Python observations remain at their original sources.

### Native unit outer-wrapper failure

The private unit wrapper remains **exit1 / FAILED**, despite product unit exit0.
Its strict outer-map equality found only the new synthetic PowerShell startup
cache and its four ancestor directories under
`synthetic-home\AppData\Local\Microsoft\PowerShell`.
`StartupProfileData-NonInteractive` is 87,524 bytes, mode0666, readonlyfalse,
SHA-256 `5aad336474e8a298c8a988ab0bb5353735fcbb47e3b3c13557df795c6e8f9cfb`;
the directories are mode0777. No existing outer entry or source blob changed.

This is an owned synthetic USERPROFILE addition, not evidence of an operator-home
write or a product receipt failure. The wrapper was not relabelled, retried,
weakened or cleaned up. The cache remains preserved, including through subsequent
exact before/after maps and final sealing.

## F05 closure: bind publication to the original observation

`bin\li-copilot.py:181-219,819-880,987-1117` pairs native presence/type inspection
and `context_safety.read_owned` bytes/state once per planning input. Managed writes,
protocol merges, create-only seeds (`None`), stale deletions, ignore/attributes
appends and the inventory use that original observation. Missing/nonregular
write observations refuse. Read-only guards are re-observed at final consumer
admission; actual mutations retain the unchanged engine's expected-state checks.
There is no later reconstruction of write ownership.

The original exact CLI counterexample was repeated using a profiling intervention
at real `admitted_expectations` entry and observation of actual `apply_files`,
without replacing a product function:

| Image | Bytes | SHA-256 |
|---|---:|---|
| Original operator instructions | 56 | `166fc64e863123220e2ee89e48e54b7d0b7e001093ed5d39bf220e371ea5bee1` |
| Late operator release-freeze edit | 111 | `b86072a9ac7eafd4842612634c59a5a1ecfe74f6affdcca1db4bf3f2a0f65bd2` |
| Stale generated publication | 12,850 | `294b824dd996e0e75cee591f66197d5cefc721f1b0d968c9d1cbde645a3ca1c8` |

The candidate refuses that same stale publication with
`ERROR: Caller expected state does not match current bytes: AGENTS.md`.
Expected ownership remains the 56-byte original; current/after remains the
111-byte late edit, mode0666, readonlyfalse. CLI exit1, no recovery store, no
`Lintel kit ready` and no mutation besides the intentional late edit.

The four-method selection adds 23 planned refusals (including four guards) and
five writer-entry refusals across absent/existing/merge/deletion/inventory classes.
All 28 report exit17, not ready, store absent and only the intervention changed.
The distinct post-admission unchanged-guard case exits0, leaves the edit untouched
and is detected by later check. It is the explicit non-atomic guard limitation
from `5d4651b`, **not a refusal**. A path actually written still receives full
original-state write protection.

The old failed target/store remain unchanged and unrecovered. Their capture and
trace hashes remain respectively
`ce1d20b2a96f6ba78e6d95ba9a89b357c26244dcf80bbda6cac584210d2606e7`
and `5b9c94142734ba3b84f631ee671e67f4f1c33dfc54c7efd5321d7a9546bc1bf6`.

## F06 and metadata payload closure

`install\native.sh:164-185,362-440,550-565` validates one compared inventory
copy, refuses NUL, requires exactly one first-line header, validates every body
row including an unterminated final record, and makes all consumers use the
validated records. Inventory identity is checked again at planning/publication.
`install\native.ps1:207-223,270-337,515-526` parses the observed state's bytes
instead of rereading a different live inventory.

On both real performers, all 16 malformed-record install/check cases refuse with
exit1 and preserved target/store maps: duplicate trailing/interior headers,
unterminated malformed final rows and unterminated foreign final rows.
A valid unterminated last record is accepted and its later file drift refuses
on both performers; neither drift case prints success. The actual PowerShell
unit also exercises inventory rewrite after its parsed observation and refuses
with `Inventory changed after ownership preflight.`

Only `config\aliases.yaml` is added to the fixed metadata payload/allowlist.
Its installed bytes, inventory SHA-256 and size match the real frozen source on
both performers. Check passes before drift; drift and conflicting reinstall
refuse while preserving the changed file. No general config, profile, role,
pack, hook or brand ownership was added.

## Whole-P10 quality and retained evidence

The review covers all 49 selected surfaces, not only F05/F06 or tests. Unchanged
evidence was rebound at its actual source: 1,317 B01, 572 original036 and 102
final6e bindings, **1,991 retained bindings**, not a unique-file or new-test count.

| Retained source | Independent observation reused |
|---|---|
| `00a0bef` | F01: complete malformed/valid migration catalogs, 40 candidate and two baseline cases, seven tests. |
| `c1a38a03` | Lifecycle53 and runtime9; actual F02 preservation counterexample remains historical. |
| `c1f6bad1` | F02 installed3/long lifecycle4 and completed classic/default/canonical controls. |
| `131d3db4` | F03 exact short/long contrast, six reader controls and completed dependency case. |
| `8c3afbbe` | F04 four tests/223 calls with no-write maps; original036 17-selector aggregate remains 15 pass/2 fail; copied validation separately 1/1; final6e pair remains 1 pass/1 fail. |
| `2685bd57` on `dea408ef` / `72cf78a5` | B01 unit15/15, 39.616s; real Git/inventory pair2/2, 986.196s, 70 subprocesses. Seventy-three injected retry notices, zero real notices. Its F05/F06 findings and final SPEC/QUALITY FAIL remain historical. |

Original classic outer109/source116/target182 and atomic256->263, default
target113/store128 and publication218->260, canonical history304, real required
policy/Git refusals and copied-validation cleanup are not replaced by shorter
or relocated positive cases. Current default/canonical/prose checks independently
confirm the relevant changed adapter path.

Quality conclusions: original observation ownership is retained across the full
producer class; inventory/blocks/clients/EOL/protected-file semantics still belong
to the adapter, not a second transaction ownership engine. Native performers keep
the shared data-only TSV, path/type/link boundaries, before/after byte and supported
mode checks, locks and explicit verified recovery. Source closure, installed
controls, policy separation and inert activation remain intact. Caching the
planning observation and using one validated inventory copy introduce no new
dependency or general retry. Tests distinguish positive operation, refusal,
interruption, recovery, guard limits and outer cleanup. Documentation describes
the narrowed guarantees and metadata scope consistently.

B01 remains journal-only: held lock, original journal state, actual Windows
5/32/33 same-directory replacement failures, four bounded backoffs and repeated
state checks. No target/source/stage/snapshot/restore write is generically retried.
No new high-confidence correctness, safety-boundary, maintainability, performance
or coverage defect was established in this continuation.

## Compliance and limits

After SPEC and QUALITY PASS, the frozen shared `review_contract.evaluate_controls`
was actually invoked under verified synthetic roots. Nine scoped mandatory
controls passed: authorized scope, isolation, preservation/recovery, required
caller-policy behavior, truthful host/activation claims, static license/dependency
scope and the three actual selected test runs.

The aggregate nevertheless remains **UNVERIFIED / blocked**. No active
organization/profile policy source, version or applicability was established.
Global/private inspection is prohibited, so required-policy resolution is
conservatively unresolved rather than waived. The evaluator's explicit blocker is
`required-policy: load/source/version/applicability is unresolved`.
The authority card establishes review permission, not that missing policy.
The shipped neutral pack is not proof of an active global pack. This is a
compliance evidence limit, not a newly demonstrated P10 implementation defect.

No new third-party dependency or bundled upstream tool was added; the repository
license is unchanged. Network/CVE freshness remains a separate unverified advisory;
no clean-CVE claim, live pack hook, voice gate or organization enforcement claim
is made. No shared clearance record, generated reducer or A13 artifact was written.

Actual hosts are Python3.11.9, Git Bash5.3.15 and explicitly selected existing
PowerShell7.6.6 through `LINTEL_POWERSHELL`, without policy override.
WinPS5.1 remains denied/unverified; Python3.9, stock Bash3.2/POSIX, other OSs and
unsupported long linked-Git positive execution remain unverified. Bare-install
Python independence is retained; Python-based runtime helpers keep their prerequisite.

Every execution used synthetic HOME/USERPROFILE/LINTEL_HOME and explicit effective
state/pack/profile/registry/audit/cache/temp paths, cleared inherited selectors,
preserved PATHEXT/interpreter binding, isolated Git discovery/config and separate
source checkout versus raw-export EOL behavior. No real-home/profile inspection,
global setting, hook activation, generic retry, platform probe, remote operation,
source repair or full repository suite was performed.

Historical WinError5, 120/128 FAILED and all failed/stopped aggregates remain
failed at their actual sources. Zero real retry notices in current selected runs
and retained B01 positives are non-reproductions, not an explanation or fix claim
for the historical denial. Frozen-copy assessment did not establish an owned
handle/readonly/expected-state defect or external sharing cause. Required
positive Git cases were actually observed at B01; the earlier failures remain.

## Evidence seal and handoff

Private evidence root, relative to this reviewer's session `files` directory:
`p10-f0506-a2df202-independent`. Exact absolute paths are in the private
`delivery.json` handoff, not copied into the repository. The final index binds
360 current evidence/helper entries; the 967-file source manifest and the three
retained indexes are separately bound. These are identity counts, not test counts.

| Artifact | SHA-256 |
|---|---|
| `final-evidence-index.json` | `7cf042da9371f5b1cd45eaf61eeb02a9e6ab798bbf060226d5243c0b8967f8ad` |
| `source-manifest.json` | `d22657666b11144faa482421e48d2ac5e6e72f5020dc2c92082e257604740101` |
| `retained-and-full-selection.json` | `5df2b543b00d964ae3a43e455e2b60fe6a316dd6a68c28ef55b7b231df254bb1` |
| `f05-independent-assessment.json` | `5b9836f44afb8ac285d32e0f7374dedccf2f11134912534bf5faa61adfed6ac2` |
| `remaining-independent-assessment.json` | `b20c35c2025582815a1d6fda68b49ed41d8d3ac2cd857287a994fb7fc961c59d` |
| `native-unit-cache-assessment.json` | `f2369cf144391a836a06facf2943c42284f8e40c428027b3ce4d7d35c600f5c0` |
| `spec-stage.json` | `196b8ab0dcfe8a1d11b36a00853f1e8c576d896db4ad3926f02ce09c42f42442` |
| `quality-stage.json` | `971c59c1c36b7850bb6deef9b9fcace4901de22ad97695a15758179aba6dd6dd` |
| `compliance-stage.json` | `377032f13cedddc74597a8a1a099e2b25d415952d11f062f608fd10ffb100a43` |
| `compliance-evaluator.stdout.txt` | `b3f8d472487698ce4c9ece7146ba4fe044b5bf87dee1736f45e2d631d45c4255` |

Final preservation checks verified source967, the original failed F05 target/store,
and the current retained late-edit target and synthetic startup cache unchanged.
No recovery or cleanup of that evidence was performed. The report-only commit
must have sole parent `56346ad39b6c8e0a60bb6b01a070f099d03150dd`, this sole changed
path and the required trailer; its actual identity, Git-byte report hash and
clean status are returned separately after commit verification.

No P10 product repair is identified. Coordinator retains required-policy,
A13/final integration and human acceptance gates; this review supplies the
original SPEC and whole-P10 QUALITY verdicts without silently clearing those gates.
