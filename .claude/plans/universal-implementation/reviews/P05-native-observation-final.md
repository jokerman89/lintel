# P05 native-observation independent review

**Date:** 2026-09-23.
**Stage 1, complete scoped native-observation specification: PASS.**
**Stage 2, whole eligible native-observation unit quality: PASS.**
**Current product findings: 0 P1 / 0 P2 / 0 P3 in each stage.**

This accepts the bounded P05 provider correction, not its stopped callers or an
entire Windows compatibility layer. **A03.2.n3 and whole A03.2 remain OPEN**
until the coordinator completes the actual required joined-caller acceptance.
The original P14/P12/native/installer and final CI gates are not closed here.
The separate focused-gate wrapper ended with **cleanup ERROR / exit 1**;
its passing command bodies are not a passing aggregate.

The same independent reviewer performed this continuation. The earlier complete
Q01 SPEC and first whole P05 QUALITY PASS in
`33eac071a26f5eb931c8ca7ed220fee91ea4469b` remains accepted history, integrated
in `c5c8f8638f4ae7a93331c4b615f3b9f275ab18ca`. It was not broadly re-audited
or reopened. This new specification pass was completed before the eligible
native-unit quality pass began. No nested reviewer, source fix or shared-state
write was used.

## Exact reviewed scope and authority

| Role | Immutable identity |
|---|---|
| Accepted base | `8adb8a1ebeae367141bde2df9ebd7dbeea9f5b0b` |
| Implementation, sole parent is that base | `78e4381eab48d4182f2e3554bd96e3d7e44861d4` |
| Test-only child, sole parent is implementation | `a75ec0ef2d78dac4bbd80381e1d872ee28a0031a` |
| Effective report-only child, sole parent is test tip | `fb08cb8409de4025513626a50790b7e76e17b3b1` |
| Native release authority | `18787a598ddde04fb1fb1ff3d3c3729859b6c6c7` |
| Unchanged helper | `lib\native_paths.py`, Git blob `835098264c9228f74caae5c63f1ded1430dbd94d` |
| Helper immutable bytes / SHA-256 | 2,387 / `b4b8f541c91c40563f9cabfab433d3216e3d58e1167b357141b008e4769a90ed` |
| Builder report at effective candidate | `.claude\plans\universal-implementation\reports\P05.md` |
| Builder report Git bytes / lines / SHA-256 | 67,513 / 847 / `df295a111b694dd0cf89cba604d80eb6226f1cd047846d5cf15ee4136a965e75` |

The original `work.json` selects the existing spec/plan/tasks/prompt. The complete
P05 release, **Native policy and evidence observation join**, and the n1-n3
refinement/reopening were read at exact `18787a5` through Git objects. This matters:
the isolated base's older plan does not itself contain the later reopening.
The selected original specification, original P05 card, ADR-0028, ADR-0031 and
P03's accepted shared-path contract remain authority. No task map was rewritten.
Recovery coordinator is `88aecc43-40f9-41d4-8947-6c2fb0a55481`, not the parked
MasterSession.

The whole eligible delta is exactly four product/test paths. The fifth changed
path is the builder's report. The implementation and test-only child boundaries,
including the report's non-append-only status corrections, were checked:

| Product/test path | Git blob at effective candidate | Immutable bytes / SHA-256 |
|---|---|---|
| `lib\review_contract.py` | `f3320a90c2728bc129debaf3802e943b48a84c5b` | 42,517 / `d4e05e6f14709c97c1dae0bc5e48c60527631830b8bbbeb129ab63c39dea9461` |
| `bin\li-review-evidence.py` | `954eebf552953ba153be9966cf33790206d395af` | 15,451 / `25972a78300d9f9a8dc813242073d43c768303887c230e37a9640e4118c24490` |
| `tests\unit\review_evidence.py` | `4bbe8443b531989022679f878ccf3cc4041f03ca` | 99,047 / `62868b432ea91d4ff74f9b2697656042240f2003f99d0ecca6ddb5071e0fef4d` |
| `tests\unit\review-source-target.sh` | `2ca92d53cff2f29b5d7a1724e25b01ac9e81f6dc` | 4,518 / `0937b3bef30b2047640ebbd08b3e46410b8d87279a6adbf50690009666f4dbb6` |

The test-only child adds one explicit ignored domain-shaped input case, changing
no production code or existing test method. No P03/P07 helper, schema, record
version, profile, domain/Swarm/design implementation, installer, generated output,
P14/P12 fixture, policy/actor/QA semantics or production Git strategy changed.

## Stage 1: native leaves and retained acceptance

| Leaf or preserved contract | Scoped SPEC | Scoped QUALITY | Evidence and remaining boundary |
|---|---|---|---|
| A03.2.n1, original P14 input | PASS | PASS | Independent read-only replay at the exact stopped root216/file262; old guard rejects, new guard returns the same logical path; 848 bytes/hash/file identity/size/mtime unchanged. No caller activation. |
| A03.2.n2, consistent native observations | PASS | PASS | Metadata, ancestry, regular-file admission, reads, directory iteration, current records, policy and snapshots; direct old/new omission probe, real gate negatives/positives and unchanged short receipts. |
| A03.2.n3, provider-review portion | PASS | PASS | This independent review, 102 retained/native methods, nine independent methods, controls/source-target/hook bodies, and current domain/Swarm seams. **Whole leaf OPEN** for original stopped caller joins. |
| A03.2, compound parent | Provider unit PASS; parent OPEN | Provider unit PASS; parent OPEN | No self-closure of the task checkbox or substitution of synthetic provider checks for the required joined P14/P12 outcome. |
| A02.1-A02.4 | Retained | Retained | Shared schema, statuses, mandatory/advisory, applicability and policy are unchanged. Twelve control methods pass, including mandatory unknown/error/zero-run/missing-browser and contrast behavior. This is not a new legal review. |
| A03.1 and A03.4 | Retained | Retained | Actual latest-decision/audit validation, later rejection, malformed history, current content/acceptance and evidence drift remain blocking. Native long-audit test passes. |
| A03.3 | Retained | Retained | Exact v2 QA inventory and supplied corroboration semantics unchanged. Independent omission/retype/downgrade/reclassification/policy mutations reject. Old review/QA do not clear changed evidence. |
| A03.5 and prior s/e refinements | Retained | Retained | All 91 prior evidence methods run again; useful unchanged-result reuse, Q01 interpretation identity, selected progress, raw product/criteria/literal binding, docs/advisory and unmapped history behavior remain. Prior `33eac071` is not relabeled. |

No new actionable product finding needs a P1/P2/P3 file:line/expected/actual
entry. The following source-specific observations explain the positive verdict,
rather than relying only on the aggregate test count:

| Source | Expected / independently observed |
|---|---|
| `lib\review_contract.py:26-39` | Trusted sibling helper only; ordinary source import passes, missing and actual symlink helper each exit 1 with explicit diagnostics; hostile target/PYTHONPATH helper never executes. |
| `lib\review_contract.py:284-327` | Only `FileNotFoundError` maps to absent metadata. Native lstat and resolved containment retain P05's existing authority rules; injected permission/I/O/resolution failures propagate. |
| `lib\review_contract.py:329-345` | Production `_git` AST/arguments/options unchanged. Root comparisons use recognized identities, not a newly authorized destination. |
| `lib\review_contract.py:370-477` | Existing record validation and selected snapshot observations use native operands; directory children are reconstructed from logical parent/name. New/dirty/staged/tracked/deleted/ignored inputs stay bound without native prefixes in manifests. |
| `lib\review_contract.py:496-587,729-761` | Work/acceptance/policy/evidence reads and current-context checks see real files at depth; approved hash recipes and task-progress semantics remain unchanged. |
| `bin\li-review-evidence.py:30-31,61-92,119-139,268-310` | Explicit CLI objects, audit reads/readback/history/imports and SHIP root handling use the same I/O spelling. Missing audit is distinct from permission/I/O failure; the real CLI read gate returns error/false/3 for injected audit errors. |
| `tests\unit\review_evidence.py:72-180,1506-1845` | Native fixtures preserve root216 and fixture-only command configuration, include real long positive/negative consumers and inherited cleanup accounting. Injected failures and real Windows links are not conflated. |
| `tests\unit\review-source-target.sh:15-22` | Only the required accepted helper was added to the copied source closure; all three actual installed-source/target/history assertions pass. |

Confidence is high for this bounded provider contract: actual old/new behaviors,
real consumers, immutable source comparisons and independent adversarial probes
agree. This is not an assertion of authentication, arbitrary path/platform
support, or unexecuted caller acceptance.

## Discriminating independent observations

### Exact stopped P14 input, read-only

The coordinator supplied the one explicitly authorized file in session
`8fa44739-f562-4213-a6c4-fb7719fc8c9e`:

```text
files\p14-prep-shell-06\temp\p14-profile-prep.nrprcPzf\cases\
test_c04_resolved_fields_and_consumed_policy_sources\rapid-development\target\
packs\rapid-development\policies\inventory.md
```

The actual literal absolute path, not this wrapped display, is retained in the
private executable `probes.py`. The repository root ending in `target` is 216
logical characters; the file is 262. P14 correction/report remains
`175a03df10428eb211d9f5bd73af01bd9af079e1` /
`9120bb263f6169125e3dd61c6cd12cbf9ff6fc60`, with E02 attributed to the
pre-repair P05 consumer.

The independent probe reads exactly 848 bytes with SHA-256
`226d954634ea3f0728d8dfdffcbfc1eca29f6316440af5cef854d4ce7611545e`.
Ordinary `is_file()` is false; native `is_file()` is true. A private immutable
export of the accepted-base P05 `_path(..., regular=True)` raises
`Evidence/authority must be a regular local file`; the candidate returns the
identical ordinary logical path. Before/after byte comparison and
`st_ino`/size/mtime comparison are equal.

No original policy content was executed or rewritten. No stopped fixture, profile
pin, P14 harness, business decision or P12 route was activated, moved or rerun.
This closes the provider reproduction, not the default-entry caller.

### Fresh same-dimension and selection probes

Fresh reviewer-owned roots retain 216 characters. A separate synthetic policy at
the same relative path is 848 bytes and file262. It is an actual acceptance source
and the policy source of the immutable mandatory test requirement. Actual
prepare/writer/latest-reader/QA/SHIP initially clear; changing or removing it
blocks; restoring exact bytes reuses the existing evidence.

For a selected directory `selected/` plus 24 `d` characters, the fresh input path
is 266 characters. An actual accepted-base snapshot silently omits the new
untracked input and marks the existing dirty tracked file absent. The candidate
includes the tracked, deleted and fresh inputs with their correct base/index/
worktree states. It also includes an actually Git-ignored, explicitly selected
opaque JSON file at:

```text
.claude/runtime/state/domains/reviewer-fixture/i0001/ta/01-result.json
```

That input is new reviewer data, not a P12 decision. No ignored-status bypass,
directory shortening or loss of selected metadata was needed.

Exit triples are **actual latest reader / QA producer / SHIP**:

| Independent transition | Actual exits |
|---|---|
| Fresh policy current / exact restoration | `0/0/0` |
| Policy criterion changed / missing | `3/1/3` |
| Complete selected tracked/deleted/new/ignored inputs current | `0/0/0` |
| Later selected directory addition / changed staged content | `3/1/3` |
| Explicit ignored input changed / removed | `3/1/3` |
| Exact selected bytes and index restored | `0/0/0` |
| Unselected evidence bytes change, fresh observation requested | `3/0/3` |
| Original evidence bytes restored | `0/0/0` |

The old valid QA bytes were restored before SHIP in these stale-content probes.
A fresh QA observation of changed, unselected evidence may legitimately succeed;
the immutable obligations and context have not changed. Direct `verify_qa` of
the old evidence rejects with `QA evidence files changed`, and the stale review/
restored old QA cannot ship. No test was weakened to demand that every fresh
observation fail or to permit an old review to clear.

The independent probe also submits missing QA IDs, tests-to-check retyping,
mandatory-to-advisory downgrade, applicability reclassification and changed
policy version. Every producer invocation rejects with exit 1 and the specific
inventory/immutable-field diagnostic. The retained suite additionally exercises
forged QA at the SHIP consumer and mandatory negative controls.

### Errors, authority and source trust

Injected `PermissionError` and `OSError(EIO)` at selected-file metadata are raised,
not represented as absent snapshots. Injected iteration and resolution errors
also propagate. Only the explicit `FileNotFoundError` case returns absent.
At the actual CLI `main` read-gate boundary, injected audit permission and I/O
errors each return exit 3, `ok:false`, `status:"error"` and the original error.
These injections verify error handling; they are not actual ACL-change evidence.

Actual ordinary and native spellings produce identical work/evidence identities.
A filesystem-only authority root of 306 characters includes the required-profile
declaration and its raw hash. It is not proof that Git initializes at root306.
Traversal, Git metadata and ADS-like relative inputs are refused.

Real Windows link probes preserve P05's policy rather than importing P03's
stricter policy: an explicit file through an in-root junction is permitted;
recursive junction/alias selection is rejected; an outside-root junction is
rejected. A long selected symlink binds its target-string bytes without following
the target, but cannot be admitted as a regular evidence file. The long allowed
junction-file observation is 300 characters. The outside sentinel bytes remain
unchanged. Stored junction targets are logical; native spellings are only I/O
operands. No unsupported long-junction-constructor claim is made.

The source-trust probe uses a copied, known source and a hostile target
`native_paths.py` marker. Ordinary helper loading succeeds. Missing and actual
symlink helper cases fail before marker execution, even with target PYTHONPATH.
This is a source-selection refusal, not authenticated code provenance or a new
enterprise security boundary.

### Actual old-source receipt compatibility

The reviewer exported the bounded old source from exact `8adb8a1` as data and
executed that old producer in a fresh synthetic short-path fixture. It created
context, review, QA, corroboration and actual audit bytes before invoking the
candidate consumers. This is a new independent old-code/new-code comparison,
not a claim that these reviewer files predate the original implementation edit.

The repaired actual latest reader and SHIP both return 0 with true gates using
those unchanged old receipts. All five files remain byte-identical; a later
candidate `prepare` emits the exact same serialized context without rewriting
the saved file:

| Old-source artifact | Before/after SHA-256 |
|---|---|
| Context | `b2b08ce4f2c39c50d9417cf311d1de16d788dc9159caed95904d00d46ddb0eac` |
| Review | `f9fadb8ac5cf83d0ccbb995474f39019ffb9c34334eff0f583ce5fd0d0ca4710` |
| QA | `cc14a8a62efc62cc2f9a8ab9e566b330c6ec4a398089f703e5e4c74f40442f0e` |
| Corroboration | `971bd865ce02f8b07052856cd1b6a083da0059d8b4eea1c79b46383137df6832` |
| Audit | `8bf138511eca4c351dc5bfb0e30b8521734f2cd3ab698e0cc90c800aa71e022b` |

The native correction introduces no new receipt migration. Q01's prior byte-only
excerpt migration rule remains unchanged. Native aliases do not enter persisted
relative names or digests.

## Stage 2: whole eligible unit quality

After confirming complete scoped SPEC, quality covered the entire four-path
`8adb8a1..a75ec0e` native unit, the full effective report changes, the accepted
native helper's two-export contract and relevant unchanged consumer seams.
It did not treat an earlier Q01 approval as approval of this correction, or
expand into a new review of unrelated P03/P07/domain/Swarm/installer code.

| Dimension | Verdict and basis |
|---|---|
| Correctness and complete observation boundary | PASS. The change covers lstat/ancestry/resolution/regular-file checks, iteration, link/file bytes, acceptance/policy/control evidence and explicit CLI/audit reads, not just the first failing `is_file`. Logical children are rebuilt after enumeration. |
| Authority and error handling | PASS. Native spelling is not authority; P05-specific links and containment remain. Observation errors are explicit and non-clearing, not missing-data success. Trusted helper errors have no target fallback. |
| Compatibility and producer/consumer agreement | PASS. Existing public signatures, schemas, versions, status/QA/actor policy and hash recipes remain. Actual old producer bytes clear the new real consumers unchanged. Fresh QA and stale evidence are correctly distinguished. |
| Scope, simplicity and maintainability | PASS. Three small private path-observation helpers reuse the accepted provider; no generic filesystem framework, alternate root, fallback Git strategy or platform-setting change. The CLI shares the same spelling/resolution rather than duplicating policy. |
| Performance and determinism | PASS within the bounded inspection. No new dispatch/network operation or extra Git strategy; Git blob caching and deterministic manifest ordering remain. No performance benchmark or universal path-depth claim is inferred. |
| Tests and evidence meaning | PASS. All prior method names remain, native cases exercise actual consumers and source closure, the later ignored-input case is correctly attributed to the test-only child, and actual/injected/fixture-error evidence levels are distinguished. |

AST comparison finds no changed existing function signatures. `_git`,
`_snapshot_digest`, control evaluation, status validation and QA/actor semantics
are unchanged. Schema, Markdown/native providers and writer/reader shell source
bytes are unchanged. Current `domain_result._current_context` and
`swarm_evidence._latest_review` run in the retained native test with a fresh owned
neutral pin: current evidence passes, changed acceptance and later rejection
fail. These two seams do not establish complete domain/Swarm business outcomes.

## Actual commands, environment and limitations

Before product imports, inline product calls or subprocesses, the private
launcher inspected synthetic HOME/USERPROFILE/AppData/temp/XDG/Lintel roots,
source hashes, fixed PATH/PATHEXT, executable resolution and Git ceilings.
Parent collection/export code imports no product modules. Every product process
inherits only that inspected environment. The exact original P14 file is the one
separately authorized read-only exception to newly owned fixture data.

Runtime was Python **3.11.9**, fixture Git **2.55.0.windows.3** and Git Bash
**5.3.15**. Approved jq 1.8.2 was reverified against
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`
and supplied only through the fixture process PATH. No installation occurred.
Native root216 cases alone use the authorized command-scope environment:
`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=core.longpaths`,
`GIT_CONFIG_VALUE_0=true`. Tests assert command scope, no local setting and
unchanged fixture config bytes. Production Git source/arguments are unchanged.

Ordinary source Git uses its normal existing configuration and controls, not
synthetic global-disabled settings, an EOL projection, a hook override or a
new longpaths option. Its status and immutable diff check are clean. No source
or index normalization was performed.

| Reviewer execution | Actual result |
|---|---|
| Private `launch.py run retained-01 --mode evidence`, invoking `bash tests\unit\review-evidence.sh` | **PASS**, one actual **102-method** run: all 91 retained plus all 11 native, 1181.856 s unittest; 1182.513 s command / 1182.634 s wrapper. Zero failures/errors/skips; child 0, aggregate 0, cleanup null. |
| Private `launch.py run probes-01 --mode independent`, invoking private `probes.py` | **PASS**, 9 methods, 132.128 s unittest / 132.729 s wrapper; zero failures/errors/skips, child/aggregate 0, cleanup null. Includes exact original n1, independent baseline omission, real gates, trust/errors/links and old receipts. |
| `bash tests\unit\mandatory-controls.sh` | Body PASS: 12 methods, 44.399 s unittest / 44.851 s command, exit 0, no skips. |
| `bash tests\unit\review-source-target.sh` | Body PASS: all 3 assertions, 13.650 s, exit 0. |
| `bash tests\integration\no-merge-without-review.sh` | Body PASS: 2 methods, 21.296 s unittest / 22.111 s command, exit 0, no skips. No hook activation. |
| Four shape scripts: audit-writes-via-helper, skill-descriptions-trigger, agents-categorized, claude-home-paths | Bodies PASS, exit 0 each; 17.256 / 14.948 / 21.134 / 4.203 s. Includes 74 inspected shell files and all 69 agent categories. |
| Combined focused-gate wrapper `gates-01` | **ERROR / aggregate exit 1**, 138.434 s, despite child/body exit 0: synthetic cleanup `PermissionError(13, 'The process cannot access the file because it is being used by another process')`. Not rerun or relabeled. |
| Python 3.9 grammar, AST/API/scope comparisons | PASS on the four selected Python files; all 105 prior evidence/control/hook method names retained, 11 native added. **Not live Python 3.9 execution.** |
| Normal source `git diff --check 8adb8a1ebeae367141bde2df9ebd7dbeea9f5b0b fb08cb8409de4025513626a50790b7e76e17b3b1`, ancestry/blob/status checks | PASS without configuration/hook overrides or normalization. |

Builder evidence stays separately attributed: 101 methods in 1254.708 s plus
one later method in 16.055 s was **not** a builder 102-method aggregate. The
builder's six-method RED, incorrect fresh-QA oracle, junction-constructor errors
and synthetic-EOL source check remain failed historical runs as recorded in
the full builder report. This reviewer neither repeats their timings as its
own nor converts them into passes. The independent run above genuinely included
all 102 methods at the test-only tip.

### Focused-gate cleanup: exact bounded facts

The failed-cleanup root was created by this reviewer's launcher:

```text
C:\Users\jokerman\.copilot\session-state\6ed9c7df-4845-4d70-88c7-f0746ab28059\files\p05-native\gates-01\sandbox
```

The already-completed read-only inspection found exactly these remaining child
directories, each with attributes 16 (ordinary directory) and zero entries:
`home`, `legacy`, `localappdata`, `temp`, `workspace`, `xdg-cache`,
`xdg-config`, `xdg-data`, `xdg-runtime`, `xdg-state`. Thus their exact paths are
the displayed root plus each named child. The wrapper process exited. The
lock holder and any other remaining-process state are **unknown**; neither
processes nor ACLs were queried.

Recovery subsequently reported a separate exact-root re-inspection, one
nonrecursive `.NET Directory.Delete(path, false)` attempt on `sandbox\home`
that failed "being used by another process" (coordinator shell311 exit 1),
then read-only confirmation that all ten directories remain empty/ordinary
(shell312). Those are **coordinator observations**, not reviewer reruns.
The execution stopped there. No process/ACL query, force/recursive deletion,
retry or source/evidence change is inferred.

The original wrapper ERROR remains exactly ERROR; the later cleanup refusal
does not alter any test-body result or this provider review. No cleanup retry
or further investigation was performed by this reviewer. The coordinator owns
any separately authorized future cleanup.

### Persistent private evidence

Private evidence is under session
`6ed9c7df-4845-4d70-88c7-f0746ab28059\files\p05-native\`.
The private executable fixtures, inspected environment JSON, source/API intake,
structured summaries and original result JSON accompany these logs:

| Log | SHA-256 |
|---|---|
| `retained-01\stdout.log` | `edc65fc0c5506276caa3033086d2ba1b64b8cb9b6546778b1ef560544fdcb39d` |
| `probes-01\stdout.log` | `7c11a1428cf86477e06939a301fe35dd85dd9127ea16a76c9cce30032648aaba` |
| `gates-01\stdout.log` | `74bead6a1e617cead0bdc00c85f7709db4d16eb08a48f3b6f482909142c749cd` |

The reviewer did not access the original P12 structured-record file. Its reported
263-character/1,605-byte observation and SHA
`d5623a4dbf14056b34a740cd31e3a0196ccc5a490ab789cf15450ed98a3154f9`
were read as attributed evidence in the P05 report only. The fresh opaque
ignored-input tests do not reopen the denied P12 decision route.

## Preservation and final gate

The new review worktree/branch is
`jokerman-microsoft-p05-native-observation-review`, created clean at exact `fb08`.
The only authored repository output is this file. The five earlier reviewer
heads remain preserved:

| Branch | Exact head |
|---|---|
| `jokerman-microsoft-universal-evidence-review` | `aef81d425a2ca36588a8b8ab01bc1a8321d9bc3d` |
| `jokerman-microsoft-universal-evidence-recheck` | `d83ed02e46171d3ef2c87395dd0d7721f94651ef` |
| `jokerman-microsoft-universal-evidence-final` | `85e8d908329bae18203dc2fa855436e982270afd` |
| `jokerman-microsoft-universal-evidence-shared-boundary` | `0cdbf5962d52a0d8d5e82ac3316209140a5a597d` |
| `jokerman-microsoft-p05-excerpt-review` | `33eac071a26f5eb931c8ca7ed220fee91ea4469b` |

The report-only commit and its direct `fb08` parent, single-file scope, unchanged
product/helper identities, preserved heads and ordinary clean status are verified
in the final handoff. No reset/discard/amend, source fix, shared plan/memory write,
new reviewer, network/private/global action, UI/native-client run, installation,
ACL/policy change or P10 probe was performed.

Synthetic actors and receipts remain caller-trusted observations, not
authenticated independent/human testimony. Real Windows filesystem cases are
distinguished from injected I/O errors. There is no live Python 3.9, Linux/macOS,
UNC deployment, general Git long-root compatibility, full native client/model,
legal/enterprise enforcement or release/CI claim.

**Bounded P05 provider SPEC and QUALITY pass; the coordinator may consider the
provider for integration.** A03.2.n3 and whole A03.2, original stopped P14/P12
caller joins, native/profile business acceptance, installer/source preflight and
the remaining integrated/CI boundaries stay open. Only their owning coordinator
can release those next operations. This reviewer stops at the report-only
checkpoint; the original P05 owner retains responsibility for any later repair.
