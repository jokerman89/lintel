# P10 combined independent specification review

**Date:** 2026-09-22. **Candidate:** `4c0519e3ba3ba610d4db3f7f19e18a85531546d9`.
**Product:** `a559c9f5aefc62b3a2e6094e8c899d5f3ed55f70`.
**SPEC:** FAIL. **First whole-P10 QUALITY:** NOT STARTED.
**New findings:** P1 1 / P2 0 / P3 0. **F01:** remains CLOSED.

F02 reproduces replacement of eight existing consumer-owned files/fields through
the actual installed caller-to-child scaffold path. The operation returns exit 0
and a complete receipt. Specification testing stopped on this counterexample;
passing targeted suites do not establish complete P10 acceptance.

## Authority, immutable identities and attribution

Read the complete current reports/P10.md, including native-consumer and Git-refusal
evidence, the complete MasterSession card at `34b84a8`, ADR-0030/0031, and the retained
original authority/review context. Original A12.1-.4 and their ten subleaves remain
selected. This is the same independent reviewer, not the builder or a nested reviewer.

| Identity | Exact value |
|---|---|
| Required parent of this sole report commit | `4c0519e3ba3ba610d4db3f7f19e18a85531546d9` |
| Candidate parent / reviewed product | `a559c9f5aefc62b3a2e6094e8c899d5f3ed55f70` |
| Product parent | `f7d2151d9596377e1023c01ed99269b3cb0a999f` |
| Original owned dependency base | `fb96f71342f7994c42bdfc7cd61e6d452e6acb54` |
| Original 48-path product | `a73cf9ee38977501c201225d8269dac3668c1080` |
| Authorized copied validation fixture | `acf97f1ca47d115501613ca29e91d902300b9bf6` |
| F01 product / independent closure report | `4407827f563fecac2ac6bf04a6bd0fc9cdd05641` / `00a0bef938a4da3f09064b6be88b8bad89ec897d` |
| Original rejection, preserved | `1d871338dcdd1b6a535e4b546c2b2d0a7aea031b` |
| Current authority | `34b84a880875870e4f9b4c4ffdb01acc3f9c1e42` and the explicit combined-review instruction |
| Reviewer | App context `cb36a715-df4e-4c7a-8588-37115c8df3c8`; CLI context `1578dfd8-f239-4eba-989b-3c4bde3e5792` |

A new detached worktree was created clean at exact `4c0519e3`. Prior review branches,
reports and worktrees remained unchanged and clean. No reset, amend, product repair,
test repair, shared-plan/memory/reducer edit, master product import or remote operation
occurred. The only repository output is this report.

The current report-only candidate differs from its product parent only in
reports/P10.md, whose exact Git-byte SHA-256 is
`9c2aec3ec5c6df0a3d4d7bdb079868f72e5aa4e4f3b0b3097d5ca71b238bbca2`.
All 967 candidate files were exported from Git objects, verified against their blob
IDs and SHA-256, and rechecked unchanged after the verification runs and final seal.

| Separately attributed change | Scope retained |
|---|---|
| Coordinator imports `dcf0448`, `7a89277`, `a400c03` | P05 CLI Git mode, literal runner diagnostics, welcome footer/parity; not P10 authorship |
| Accepted core `ce7415f` -> `bc0863a8c4d16bc07f2389ccc8599c583c004834` | Native path representation, P03/P07 wrappers and assigned resource/fixture closure |
| Accepted fixture `5fc657f` -> `8097ba2c7d45cdc09715abf57593512ea28d8199` | P01 same-root cleanup follow-up; not a new P10 core implementation |
| P10 `a31c5eb9fe5a910f2f3d27b6079c144313f80b6c` | Five-path direct-consumer unit: adapter, transaction primitive and three owned test files |
| P10 `a559c9f` | Only adapter Git preflight/refusal, its focused Copilot tests and docs/lifecycle.md |

Independent AST comparison confirmed all 29 original `a73` Copilot test methods
unchanged. The entire real Git subprocess-call AST remains identical to `f7d2151`;
the approved correction does not add flags, aliases, redirects or retries.
Original ownership is still 48 paths plus the authorized copied fixture, with the
F01/native-consumer/refusal deltas and accepted dependencies attributed separately.
The earlier original-surface inspection is retained; this continuation inspected
the combined deltas, current callers and the relevant complete runtime functions.

### Producer and accepted-core hashes

| Artifact | Exact candidate SHA-256 |
|---|---|
| `docs/native-installation.md` | `e2cf6bf3417e10ad12112002e0719a581f1632b0db2881459cfaad20208e1ae0` |
| `docs/lifecycle.md` | `4f6771383b8ed17c663d95a473d76e29928223212ebf9db745516318767bfe13` |
| `install/directories.txt` | `c8e0e825586f309c43bbcb5dc6644eb270a233ee638c7244696193db8f52d7c3` |
| `install/native.sh` | `1425c05888b24b413a45ec33f70a98fe432f73774634197cae4cbdc9d1c9e187` |
| `install/native.ps1` | `57173b99e0c809d3fe45a6c9b894ddab0c07b3961a2d73b6fd61af25047483f7` |
| `lib/managed_transaction.py` | `acbf84ef94a9fc4afdb8f66766d376653549ee82f4cf063c6a5721b1fdc08cae` |
| `bin/li-lifecycle.py` | `465db503bd518c8f453916aed961ff6e290e415ffb3e561b770578d09cd09b60` |
| `lib/native_paths.py` | `b4b8f541c91c40563f9cabfab433d3216e3d58e1167b357141b008e4769a90ed` |
| `lib/context_safety.py` | `e80cf6ac5b8edd0e97f865c05486da3c8a39ddb56c83e42eed09c04dd7d7176e` |
| `bin/li-snapshot.py` | `7d5aaaca1a18777d7503b05d7900053c95ec41b0df378dc5b7b778694b564ebd` |
| `lib/profile_context.py` | `353ba79537736ab8d2acb8da06fbb7bd731c19d697b02fbdd5702a73712291a1` |

The last four runtime blobs were independently compared with accepted `5fc657f`.
The Markdown provider remains blob `0b3da55046358864fcd3075ba5bfb6c2348b1fec`.
No native TSV, snapshot/result/restore, P05 evidence or P07 reference format changes
are authorized or made by this review.

## F02 - Existing long-path foundation content is overwritten

**Severity:** P1, blocks acceptance. **Confidence:** 10/10.
**Primary location:** `bin/li-lifecycle.py:911-917`.
**Coupled locations:** `733-736`, `779-800`, `810-818`, `918-924`.
**Requirement:** A12.1.a/.1.d and A12.2.b; original CP-12, RU-06/07/08 and the
consumer-owned preservation contract. See `skills/scaffold/SKILL.md:41-47` and
`docs/lifecycle.md:55-61`.

After the shared authority check returns a logical path, `scaffold` still uses
ordinary `path.exists()` / `path.is_file()` to decide whether a file is consumer-owned.
At the observed native Windows lengths those calls return false for existing files.
The helper consequently adds template replacements to its plan. `migration_changes`
has the same gap for the layout marker, memory index, ignore file and local settings.
The accepted native writer can access those files: `runtime_publication` captures
their real current states at line 810 and publishes the incorrectly authorized plan.

**Expected:** existing project prose, durable knowledge, ignore policy, marker comments
and unrelated settings remain owned by the consumer. Update only the explicitly
documented memory-pointer field. If required metadata cannot be established, refuse
before publication rather than infer that files are absent.

**Actual:** the same real scaffold command preserves the seeded short control but
replaces eight existing files/fields at the long plain-folder target, returns exit 0,
reports `"state": "complete"` and `"preserved": []`, and records all paths applied.
The approved external-Git limitation is irrelevant: this target has no `.git`
metadata and the reproduction does not run or vary any Git compatibility command.
No universal numeric path-support requirement is invented here; overwriting
consumer-owned content instead of preserving/refusing violates the original scope.

### Real installed-path reproduction

An independent source export installed an actual repository bundle using:

```text
python -B <sealed-source>\bin\li-adapter.py init
  --source <sealed-source> --target "<fixture>\installed consumer"
  --client copilot-cli
```

No `--store` or recovery-store override was supplied. Fixture length was 94, caller
target length 113 and default sibling-store length 128. This initialization returned
0 in 86.563 seconds. The bundled shell/runtime helpers used by the probe were
compared byte-for-byte with the sealed source before either scaffold invocation.

The two new target folders were seeded with identical relative content. The
short target was 116 characters; the long target was 256. No previous fixture was
shortened or moved. Both were plain folders, with no `.git`, symlink or reparse entry.
The consumer seeds were:

```text
AGENTS.md: "Consumer-owned AGENTS prose.\r\n"
CLAUDE.md: "Consumer-owned CLAUDE prose.\r\n"
.claude/memory/lessons.md: "Consumer-owned durable lessons.\r\n"
.claude/memory/MEMORY.md: "Consumer-owned memory index.\r\n"
.claude/rules/README.md: "Consumer-owned rules.\r\n"
.claude/settings.local.json: {"custom":"consumer-owned","autoMemoryDirectory":"preserve-or-update-only-this"}\r\n
.claude/lintel-layout.yaml: "layout_version: 5\n# Preserve this consumer comment.\n"
.gitignore: "# Consumer ignore policy\r\n.claude/runtime/\r\n.claude/settings.local.json\r\n"
unrelated.txt: "Unrelated consumer file.\r\n"
```

For each target the real Git Bash invocation, from the installed caller, cleared
ambient Lintel/profile selectors only after synthetic HOME/USERPROFILE had been
established, then executed:

```bash
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
# Read-only observer records the actual exported reference and before states.
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$REVIEW_CHILD"
```

This is the canonical shell route, not a direct Python method or mock. The actual
bundled bootstrap established the caller's default runtime home and carried its
verified reference into the real bundled scaffold. No custom home, missing helper,
removed inherited pin, alternate store or host-policy workaround was used.

The short control returned 0, preserved all protected seed bytes and retained the
settings `custom` field while updating only `autoMemoryDirectory`.
The long case returned 0 in 8.625 seconds with these observed changes:

| Existing file | Path characters | Bytes before -> after | Actual result |
|---|---:|---:|---|
| `AGENTS.md` | 266 | 30 -> 14611 | Consumer prose replaced by generated template |
| `CLAUDE.md` | 266 | 30 -> 17216 | Consumer prose replaced by generated template |
| `.claude/memory/lessons.md` | 282 | 33 -> 784 | Durable lessons replaced by seed |
| `.claude/memory/MEMORY.md` | 281 | 30 -> 364 | User memory index replaced |
| `.claude/rules/README.md` | 280 | 23 -> 213 | User rules replaced |
| `.claude/settings.local.json` | 284 | 82 -> 309 | `custom` key lost; only the new memory pointer remains |
| `.claude/lintel-layout.yaml` | 283 | 52 -> 18 | Existing marker comment lost |
| `.gitignore` | 267 | 73 -> 66 | Existing user comment/bytes replaced |
| `unrelated.txt` | 270 | 26 -> 26 | Preserved negative control |

All listed files retained mode 0666 and read-only false. For each long file,
ordinary `Path.exists()` was false while native same-location observation was true.
This distinguishes absent-file inference from a caller-authorized update. Full
before/after SHA-256, sizes, modes, directory inventories and literal outputs are
retained in the sealed probe records. Representative exact identities:

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| `AGENTS.md` | `a55d0d50654029123d629b331a3985f20aa9a052980cf37464dd27e4976c3c89` | `1c6937530e46a343028f037a3c239d2368dc7df331c5f43203f84b9fc6c5d622` |
| `.claude/settings.local.json` | `ec2c2cd6748fe48f2465ad7485d58512910e2eecf4b500acaef40643caa60a8b` | `c121b18f71fe358fab23066e15eb14acd66f59eba4268dd6f30c9af61fe0e7e3` |
| `unrelated.txt` | `57769f1535f11858c7643b99633327331e3b1bc47e6bb7b2484345a0f805f015` | Same |

Caller bytes/modes, its default home/pin/history, source and synthetic personal home
were unchanged. The retained caller history was 304 characters. The child result
contained the exact caller generation-1 operation reference and
`target_profile_reference: null`; no child generation was introduced.

The actual receipt is `transaction-f859752264f44a3aa79d678ac29703ed`, snapshot
`snapshot-dec2ead17d8444cdab471695834e2d2f`. Read-only inspection confirmed a complete
journal, every phase applied, logical owner/source and no remaining lock.
All overwritten files' snapshot/plan before hashes match the original seeds.
Recoverable backups do not authorize overwriting consumer-owned content.
No recovery, rollback, relabeling or cleanup was attempted; the altered synthetic
target and receipt remain evidence. The reviewer probe returned 3 for SPEC FAIL,
distinct from the actual scaffold's exit 0.

**Repair direction, not implemented:** correct the lifecycle consumer's own
existence/read/ownership decisions at these sites using the already accepted
same-location I/O boundary after its existing authority checks, or refuse safely.
Retain logical roots, settings/prose semantics, explicit caller constraints and
receipt formats. Add the real installed-path seeded preservation regression.
This finding does not authorize a P03/P07 rewrite, Git compatibility experiment,
new infrastructure or reviewer's repair; scope remains MasterSession's decision.

## Actual independent execution and harness failures

All commands below used sealed raw candidate bytes and a session-only observer,
not substituted subprocess results. The observer records effective environments,
rejects out-of-fixture roots and invokes unchanged shipped tests. Injected failures
inside those existing tests are labelled synthetic and occur after their real writes.

```text
python -I -B <files>\p10_combined_test_runner.py managed-runtime-nine
  <sealed-source>\tests\unit\managed-transaction.py --root <sealed-source> -v -f

python -I -B <files>\p10_combined_test_runner.py owned-lifecycle-matrix-pathext
  <sealed-source>\tests\integration\universal-lifecycle.py
  --root <sealed-source> --bash <git-bash> -v -f

python -I <files>\p10_scaffold_preservation_probe.py probe
```

| Actual run | Result and cleanup |
|---|---|
| `managed-runtime-nine` | **9/9**, 15.385 seconds, exit 0; original seven plus deep native transaction/recovery; exact temp cleanup and source seal verified |
| Initial `owned-lifecycle-matrix` | **FAILED**, 8 tests / 1 failure, 30.754 seconds, 47 subprocesses, exit 1; first seven migration methods passed, native interruption was not reached because Git discovery failed |
| Native prerequisite diagnostics | Same approved PS7: omitted PATHEXT -> Git unavailable/exit 2; explicit process PATHEXT -> actual Git found/exit 0. Diagnostic driver itself remained **FAILED** on its separate broad cache-state assertion |
| `owned-lifecycle-matrix-pathext` | **53/53**, 623.146 seconds, 192 real subprocesses, exit 0; no skips, cleanup errors or source changes |
| Real default installed-consumer setup | Exit 0, actual target113/store128, no alternate store; setup for independent scaffold probe, not full D01 closure |
| Seeded short installed caller-to-child scaffold | Exit 0; protected contents and caller/home preserved; settings custom field retained |
| Seeded long installed caller-to-child scaffold | **Exit 0 but SPEC FAIL F02**, eight consumer files/fields replaced; probe exit 3; evidence deliberately retained |

The full owned lifecycle matrix covered real native no-Python install/check,
Bash and PowerShell Windows entry points, repeat/update/obsolete ownership,
seed/custom role/pack/config/hook/brand preservation, invalid candidates,
interruption/recovery/corrupt/foreign/consumed replay, profile/role/persona helpers,
migration/collision/pointer repair, F01, diagnostics and required-policy helper cases.
It did not contain F02's existing long-path foundation case.

### Reviewer environment correction, not a product repair

The first allowlist omitted `PATHEXT`. Approved PowerShell 7.6.6 consequently
reported `git is required` before reaching the injected publication failure.
The same executable/PATH with explicit per-process `.COM;.EXE;.BAT;.CMD` resolved
`C:\Program Files\Git\bin\git.exe`. MasterSession confirmed this fixture-only
correction was within scope. No runtime installation, host switch after denial,
ExecutionPolicy setting or product assertion changed.

The diagnostic's own whole-synthetic-host-state equality assertion also failed.
Its raw exit/output is retained, not called green. Its before-map was not persisted,
so the exact differing field cannot be retrospectively proven. Read-only inspection
recorded these expected tool-owned startup artifacts under the synthetic home:
`AppData\Local\Microsoft\PowerShell\StartupProfileData-NonInteractive` and
`AppData\Local\Microsoft\PowerShell\telemetry.uuid`. No blanket cache exclusion was
added to turn that assertion into a pass. Subsequent runs retain their own exact
source/temp checks; the F02 probe separately compares the entire caller/home/source/
target state. PowerShell telemetry opt-out was explicitly set for the later tests.

The corrected 53-test result is a new run on unchanged product bytes; it does not
rewrite the failed eight-test aggregate or the diagnostic failure.

## Original parent/subleaf specification verdicts

The required complete specification gate fails. A passing named scenario is not a
blanket original-leaf pass while required combined evidence remains absent. Quality
is NOT STARTED for every row; there was no interleaved quality pass.

| Original control | SPEC verdict | Completed evidence / remaining condition |
|---|---|---|
| A12 | **FAIL** | F02; first whole quality ineligible |
| A12.1 | **FAIL** | F02 violates lifecycle's consumer-owned content boundary |
| A12.1.a | **FAIL** | Real installed scaffold replaces existing foundation bytes; ordinary dispatch/diagnostics cases passed |
| A12.1.b | UNVERIFIED | Profile API switch/required/drift cases passed; actual copied validation/default cleanup selector not rerun before stop |
| A12.1.c | UNVERIFIED for complete gate | Role/persona tests passed; no defect claimed here, remaining complete surface acceptance not certified |
| A12.1.d | **FAIL** | `migration_changes` loses marker/ignore/settings content in F02; ordinary migration/collision/recovery cases passed |
| A12.2 | **FAIL** | Preservation counterexample cannot be averaged away |
| A12.2.a | UNVERIFIED | Native fresh/repeat cases and real default init passed; full classic/default installed checks/recovery selectors unrun |
| A12.2.b | **FAIL** | Seven protected seed files and unrelated settings field overwritten |
| A12.3 | UNVERIFIED for complete gate | Runtime/native interruption and explicit recovery passed; required combined adapter scenarios unrun |
| A12.3.a | UNVERIFIED for complete gate | Correct incomplete-state/no-success behavior observed in injected runtime/native/migration tests |
| A12.3.b | UNVERIFIED for complete gate | Ordinary/deep verified recovery, foreign stores, edits, locks and consumed replay passed; full combined adapter proof outstanding |
| A12.4 | UNVERIFIED for complete gate | F01 retained; actual approved Git-refusal matrix not run before F02 stop |
| A12.4.a | UNVERIFIED | Truthful unsupported host/native boundaries inspected and tested where noted; external-Git correction execution outstanding |
| A12.4.b | F01 CLOSED; complete leaf UNVERIFIED | All seven current migration methods passed; no reopening of prior F01 closure |

## Isolation, historical evidence and unrun limits

Before execution a startup-free shell sourced the frozen path/resolver/jobs readers
and reported 21 effective paths; each resolved into an owned synthetic fixture.
Python's actual home/temp were checked too. The per-process allowlist explicitly
sets HOME/USERPROFILE, application/XDG/cache/temp roots and Lintel source/target/home/
pack/pointer/audit/jobs/private-role roots and derived profile/history/registry/state.
Inherited Lintel/Claude/Gstack/Git selectors, BASH_ENV/ENV and redirects were not
adopted. Synthetic Git config and an empty per-command hook directory prevented
personal configuration/hook use.

The test temp parent was newly allocated at the required length 79, without moving
prior state. Existing fixtures performed their own verified exact-root cleanup.
For both completed suites the synthetic temp map was empty before and after;
all 967 source identities matched. Probe targets/receipts and the diagnostic
artifacts remain intentionally retained. No old incident state, real home or
private profile was inspected, recovered or cleaned.

Actual Python was 3.11.9; native Windows verification used the expressly approved
already-installed PowerShell 7.6.6 without policy overrides. Git Bash was the
available Windows shell, not stock Bash 3.2/POSIX acceptance. Python 3.9, other OSs,
denied PowerShell 5.1, live host enforcement and real private company data remain
unrun. No remote/GitHub/authentication, paid model, release/push/PR or hook activation
operation was performed.

The operator-approved Git contract was assessed as pre-write refusal, not a demand
for successful root256 Git setup. The current code and unchanged argv were inspected;
the two real Git methods were not executed before F02 stopped this review.
No stopped option/native-C/cwd/setup experiment was retried. Long linked positive
support remains UNVERIFIED. F02's no-Git plain folder is a different defect.

The required classic base109/source116/target182 and atomic256->263 selectors,
complete default snapshot218->260/check/repeat/recovery/replay selector, D03 actual
validation fixture with cleanup, combined installed required-policy/audit controls,
remaining adapter-preservation selectors and check-install.ps1 were not independently
executed in this continuation. The setup and neutral bridge observations above are
partial evidence only. D01/D03 are not declared closed.

Historical **120/128, 8 failures, 0 skips, 0 partial** remains FAILED. Earlier seven-
and fifteen-case failures, REDs, Git/setup failures, D01 normalized260 correction and
D03 cleanup ERROR remain unchanged history. Builder 2-method/34-operation and
22-selector results, older evidence index `3386d3c...`, new index `e555e589...` and
manifest `9b29bb4...` are not this reviewer's runs or a whole-package pass.
No repository-wide suite ran, concurrently or otherwise.

### Durable evidence

Raw artifacts are in this reviewer's session
`files\p10-combined-a559c9f-independent\`. The retained execution fixtures are
separate from the immutable source/worktree. Session-only drivers are
`p10_combined_review.py`, `p10_combined_test_runner.py` and
`p10_scaffold_preservation_probe.py`. Personal path prefixes are omitted here;
invocation records retain exact local paths, argv, exits and root checks.

| Artifact | SHA-256 |
|---|---|
| `candidate-identity.json` | `5bb86e7c39e6a25fc773937e8de475bdc5d90beb0adbd5ee9b3e30c9716dde14` |
| `source-manifest.json` | `87ea7724ccf6e9c63252150b00d7f6f3ca602258fa254da762eeaf176d35bdc7` |
| `scope-proof.json` | `afe062ffe77060f14a980485e7f17a434f2819403f23905ecd9d5d4285e58f0b` |
| `owned-lifecycle-matrix.stderr.txt` (failed) | `1155319515c5f429be198abadd137aa394e5342d7e7876bc544b665dc8bb375f` |
| `native-prerequisite-diagnosis.json` | `3dfcda19fdce21f44aac9f66842f8cb2881404803c1314d24106a77b5eec806e` |
| `owned-lifecycle-matrix-pathext.stderr.txt` | `7c7533f84bd8ba46e1a7db84907d454702735126658b51cee7771d89ae8f0bed` |
| `managed-runtime-nine.stderr.txt` | `3cec80de3852e8050294c1a2da7bebd3a7e786132e51dcf37b6ccdd1eab250b6` |
| `scaffold-short-preservation-evidence.json` | `4a9ddc3127b0d96c67aea6a494a8d9f55af89f36400ece55dc1a4697b5cf26c7` |
| `scaffold-long-preservation-evidence.json` | `dd07d03acce562c7350b09790b46f3e034b519757e9337fa3d478f6c2f4617b7` |
| `scaffold-preservation-verdict.json` | `fb820ecc2bb2ef30f95b4e24dbf953b511f9f8154f182c46cb7cf588bf0e6b11` |

`combined-finding-seal.json` also records every seed hash/size/mode, unchanged
caller/history, exact logical receipt identity and verified recoverable before-images.
Hashes identify content, not authenticated independence or policy enforcement.

**Next gate:** MasterSession returns F02 to its original owner under explicit scope,
then supplies a new frozen combined checkpoint for remaining complete specification
and only subsequently the first whole-P10 quality review. No reviewer repair,
infrastructure expansion, A13 release or product import is authorized by this report.
