# P12 automatic test-entry source review - e7e97d4

Date: 2026-09-23. Independent reviewer runtime
`31c39265-13e5-4057-9e78-49bf658749a5` (SAME31), not the product builder.
Coordinator: `88aecc43-40f9-41d4-8947-6c2fb0a55481`.
Original product owner: `09666ec2-ff03-4517-9169-8793149ea8cd`,
runtime `0a75211f-455c-4318-864f-bc8023ce9142`.

**Selected ENTRY / ISOLATION / FAILURE-PROPAGATION SOURCE SPEC: PASS.
Subsequent complete eligible two-path SOURCE QUALITY: PASS.
Owned findings: P1 0 / P2 0 / P3 0.**

This accepts the bounded test-entry correction, not the whole caller/provider
join. The original default and explicit full runs remain **33 executed,
30 PASS / 3 FAIL, zero errors/skips, exit 1**. My separately owned default run
passed 33 methods; that different-root result does not clear either original
failure. Full-suite/provider acceptance remains **BLOCKED**.

## Immutable authority and ownership

Read the complete **Automatic integration-test entry** section of P12 at
`5e1d21a38f2747b614f8c3d9707e595298ef25eb`, plus its original input-binding/B01
boundaries, startup/adapters and prior accepted review. No moving coordinator
tree or pending P05 repair was imported.

| Identity | Exact value |
|---|---|
| Accepted source/review base | `c75eabce70c117cb363076093a91a91158d81e33` |
| Selected product; sole parent is that base | `e7e97d463e7960305b1249fbf97f8dbb5e20fe7d` |
| Selected report-only commit; sole parent is product | `67a6e82b4f1e85139532373852f224981802cc40` |
| Full builder report | `reports/P12-pipeline-auto-entry.md`: 202 LF lines, 12,125 Git bytes |
| Builder report SHA-256 | `b82ce58f134de43a4c050589e985d8072d95b913ab03cdec2a083335a2cd7443` |
| Prior accepted report SHA-256 | `ce9f35ae4aba80244eb0148e672f3aa38f4907d06abc6b66e269bf827ae20299` |

Exactly two product paths changed. Their complete delta was reviewed, not just
the new helper. All 33 `test_` method ASTs are identical to the accepted base.
The earlier forty-file dependency closure has two authorized changes and
38 byte-identical files; the runner, `.gitattributes` and `.gitignore` were also
pinned, making 43 immutable exported source files. Production helper, six
callers, schemas and provider bytes are unchanged. Source Git/EOL checks were
separate from fixture Git isolation; checkout CRLF is not a product mutation.

| Owned path and source citations | SPEC | Eligible QUALITY | Ownership conclusion |
|---|---|---|---|
| `tests/integration/document-pipeline-binding.sh:9-13` | PASS | PASS | Retains interpreter selection/refusal and flags; `exec` preserves child status. |
| `tests/integration/document-pipeline-binding.py:52-102,817-953` | PASS | PASS | Test-only bootstrap, parser/preflight ordering and strict-parent ceiling correction; no assertion weakening or provider repair. |

This report is the only repository write and is committed as a report-only child
of `67a6e82`. Exact resulting commit, parent and Git-byte report digest accompany
the handoff. Previously accepted PPT, workbook, PDF, common-source and input-
admission review refs remain separate and preserved; no general ancestry approval.

## SPEC, completed before QUALITY

Scoped SPEC completed **2026-09-23T01:55:54.352577Z**. QUALITY began
**2026-09-23T01:56:56.6242922Z**, only after those controls passed, and completed
**2026-09-23T01:58:22.897051Z**. Supplemental QUALITY probe limits are below.

| Control | SPEC verdict | Evidence and exact boundary |
|---|---|---|
| E01 - Exact scope and preservation | PASS | Two-path diff; 33 identical assertion-method ASTs; 38 unchanged prior closure files and 43 pinned files retained. Accepted `c75eabc` input semantics were not re-reviewed or expanded. |
| E02 - Actual zero-argument runner seam | PASS | Existing `tests/runner/run-all.sh:90` supplies no test arguments. Exact old entry reproduced argparse exit 2, zero tests. Candidate Bash entry, with closed stdin and no test arguments, actually executed all 33 once. The whole repository runner was not run. |
| E03 - Existing interpreter/Git selection | PASS | Existing Python 3.11.9 selected through retained `LINTEL_PYTHON`; default Git discovered by actual Git Bash. No installer, dependency restoration, skip or synthetic interpreter. Explicit Git selection separately retained. |
| E04 - Fresh owned default and explicit runs | PASS | Automatic run beneath the copied repository's `.claude/runtime/p12-pipeline-binding`; separate fresh explicit parent/run. Source inspection of `mkdtemp` and actual preflights agree; file parent refused during SPEC. Filesystem-root/junction contrasts additionally confirmed source guards during QUALITY. |
| E05 - Isolation before product imports/artifacts | PASS | `bootstrap` reconstructs and clears the environment before `main` writes its environment artifact or imports product modules. Actual initial/case/command records exclude declared synthetic credential/profile/cache/config markers. All reviewer execution had its own verified outer allowlist. |
| E06 - Derived paths and trusted tool environment | PASS | 378 independent records checked: HOME/USERPROFILE/AppData/temp/XDG/Lintel/source/target/config paths, Windows home components, PATH/PATHEXT and selected executables. Owned empty Git config and disabled prompts retained; removed redirects cannot leak through inheritance. |
| E07 - Strict Git ancestor ceilings | PASS | Owned copied source was a real Git ancestor. All 35 executed cases actually refused ancestor discovery before fixture initialization. Case ceiling is its strict parent, not the starting case directory; the existing assertion is unchanged. |
| E08 - Explicit argument/selector compatibility | PASS | Actual `--fixture-root` and `--git` plus two repeated `--test` options executed exactly those two methods, exit 0, no errors/skips. Source-reviewed invalid-selector refusal was additionally executed during QUALITY. |
| E09 - Required refusal contract | PASS | Actual missing Python 127; missing explicit/default Git, file fixture parent and unknown option each 2. All five have empty stdout and truthful stderr, no new test preflight, no skip/install or false success. |
| E10 - Truthful status propagation | PASS, entry only | Own child exits 0/2/127 preserved; shell `exec` and Python success/source-retention conjunction retain exit 1 for failed suites. Original recorded full-entry exit 1 and `success:false` remain independently read and preserved, not reclassified or attributed as my rerun. |
| E11 - Historical/source retention | PASS | 43 selected source files unchanged after execution; all 397 older artifact/QA entries and six exact stopped owner result files rehashed read-only before/after. No original fixture or pin relocation, normalization, cleanup or replay. |
| E12 - Non-clearance and authority | PASS, boundary only | No new provider candidate, native action, structured P05 decision/corroboration, denied route or parent closure. Required full caller/provider, shared-runtime and native/format controls remain outside this acceptance. |

Python 3.9 grammar was checked, not execution on Python 3.9. POSIX bootstrap
behavior was reviewed in source, not claimed as an actual POSIX host run.
These inspected process environments are not an OS sandbox or enterprise policy.

## Actual independent execution and private evidence

`Q`:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

`D`:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.

The private `auto-entry-run.ps1` creates an exact source export copy and clears
the child process environment. `auto-entry-checks.py` verifies that allowlist,
tools, paths, source hashes and Git ceiling before any product call. Each command
has its exact argv/cwd/environment, preopened stdout/stderr, timestamps and actual
exit. Run-local script snapshots and output seals retain the executed harness
versions, including unsuccessful private inspectors. No original artifact was
used as a writable test target.

| Execution/evidence | Actual observation |
|---|---|
| `ae-spec02\commands\baseline-noargs` | Exact accepted old entry: exit 2, empty stdout, missing required arguments; zero tests. |
| `ae-spec02\commands\candidate-noargs` | Existing Git Bash `--noprofile --norc <entry.sh>`, DEVNULL stdin, **no test arguments**; 33 PASS, zero failures/errors/skips, exit 0. Started 01:49:42.033703Z; ended 01:52:35.434950Z. |
| Default retained run | `Q\ae-spec02\source\.claude\runtime\p12-pipeline-binding\pipeline-tests-_qzfuvqj`; 356 inspected environment records, 33 real ancestor refusals. |
| `ae-spec03\commands\explicit-selector` | `--fixture-root <owned parent> --git C:\Program Files\Git\cmd\git.exe --test test_cli_reads_exact_files_and_refuses_unknown_options_without_writes --test test_crlf_and_optional_source_fields_are_preserved_not_normalized`; exactly 2 PASS, exit 0. |
| Explicit retained run | `Q\ae-spec03\explicit-fixtures\pipeline-tests-k5yixlrq`; 22 inspected environment records, two real ancestor refusals. This is selector compatibility, not a second full-suite acceptance. |
| `ae-spec03\commands\missing-python` | Actual Bash refusal 127; no product/test execution. |
| `ae-spec03\commands\missing-explicit-git` / `missing-default-git` | Each 2. Default absence used the same Python bootstrap directly with an inspected PATH excluding Git; other required refusal cases used Bash. |
| `ae-spec03\commands\file-root` / `unknown-option` | Each 2; empty stdout, explicit stderr, no new run/preflight. |
| `ae-quality01\commands\filesystem-root` / `invalid-selector` | Each 2; no test preflight or false zero-test PASS. Retained, not rerun. |
| `ae-quality02\commands\linked-fixture-root` | Actual Windows junction between two owned private locations refused with 2; target remained empty. No alternate route or external target. |
| `ae-quality02\commands\shell-syntax` | Actual existing Bash `-n`, exit 0. |

Default Git Bash selected its installed
`C:\Program Files\Git\mingw64\bin\git.exe`, not the outer command wrapper at
`C:\Program Files\Git\cmd\git.exe`. Both are existing selected-installation tools;
the explicit route selected the latter as requested. Default binary SHA-256:
`1a0043555d254618f2d56c936c3d9a1fbfb878bc878416a133c346bc7835eda9`.
Each resulting PATH was checked against the actual selected Git directory,
existing Python directory and required Windows directories, not an ambient PATH.

### Preserved unsuccessful reviewer probes

`ae-spec01` exited 1 before its first Git/product process: my audit hook treated
Windows' string-form subprocess event as a list. Only the private guard was
corrected; no product run from that attempt is counted.

`ae-spec02` really completed the default 33-method run with exit 0, then my
inspector exited 1 because it expected the outer Git wrapper rather than Git
Bash's installed `mingw64` executable. `ae-spec03` inspected those same immutable
outputs and actual executable, without rerunning, relocating or shortening the
default fixture. The original failed inspector, logs and seal remain.

`ae-quality01`'s additional absent-SystemRoot probe returned **1**, not the
private expected bootstrap refusal 2. The pre-existing `unittest.mock` import
loads `asyncio`/`_overlapped`; this host raises explicit WinError 10106 before
bootstrap or product imports when that Windows prerequisite is missing.
Stdout is empty and no test/preflight is created. This does not demonstrate
execution of the bootstrap's SystemRoot validation branch. The original
commission specifies 2 for the five stated admission cases, not this unsupported-
host extension. `ae-quality02` retained/re-inspected the actual early refusal;
it did not rerun it, repair product, install anything or reinterpret it as
test success. Required refusal expectations were not relaxed.

All five private seals were subsequently rechecked: 56 / 2,010 / 202 / 74 / 71
files respectively unchanged. Successful inspector exits mean completed scoped
checks, not reversal of any retained failed command or external acceptance gate.

## First eligible complete entry QUALITY

The whole two-path change was assessed after scoped SPEC: setup/main/import
ordering, stdlib-only ownership checks, exception and process-status handling,
explicit-route compatibility, assertions/oracles and evidence preservation.

| Quality area | Verdict | Reasoning |
|---|---|---|
| Correctness and scope | PASS | Default arguments are resolved in test bootstrap, not production helpers. No business/content semantics or original assertions changed. |
| Isolation and ordering | PASS | Explicit executable/path reconstruction, clear-and-replace environment and strict-parent ceiling are coherent; actual initial/case/child evidence agrees. Source checks reject links before fixture creation. |
| Failure transparency | PASS | Missing-tool/argument failures remain nonzero with explicit diagnostics. Normal test failure is not converted to skip, success or an unexecuted result. Early unsupported-host failure is stated honestly above. |
| Maintainability and compatibility | PASS | Small named test-only helper; existing argparse/unittest/import mechanisms reused; no dependency, alternative parser/provider, installer or runtime API. Shell uses direct `exec`. |
| Verification discrimination | PASS | Exact old-entry RED retained; actual default and repeated selectors, strict ancestor refusals, required errors and physical junction contrast. All 33 assertion ASTs preserved. Builder full failures are not replaced with reviewer-root successes. |

**No actionable owned P1/P2/P3 finding.** No repair is requested in these two
files. Confidence is high for the observed Windows/source entry contract; it
does not extend to unexecuted minimum-runtime/POSIX/native behavior.

## Original provider block and preservation

The builder's full default root remains
`C:\Users\jokerman\reference-repos\copilot-worktrees\jokerman-session-setup\jokerman-microsoft-literate-adventure\.claude\runtime\p12-pipeline-binding\pipeline-tests-vmybtbfp`;
its explicit root remains
`D\pipeline-auto-entry\working-explicit\explicit-fixtures\pipeline-tests-rwzmmb4m`.
Both exact result files still hash to
`63d0695244ca853cad8a5ca8c30bef7b5963705ab2f7778c85774025529289ca`.
The builder reports 704 inspected environment records; that count is attributed,
not a new independent inspection of all 704. My actual 378-record inspection is
separately identified.

The unchanged upstream partial-profile, unselected/stale-result and own-context
methods stop at P05 `prepare`: selected
`.claude/runtime/state/domains/pipeline-fixture/i0001/ta/01-result.json`
has no tracked/working content in that snapshot. All six previously identified
1,605-byte files at logical lengths 263/260 retain their exact hashes from
`working-observations-scoped.json`. Same-location native filesystem spelling was
used only to rehash those exact read-only files, never for a caller rerun or
namespace workaround. No root/pin/provider was changed to make those tests pass.

The owner wrapper exit-1 records were independently read:
`D\logs\pipeline-auto-noargs-isolation.result.json` SHA-256
`25c806d94849fcb3138b7685097b8681d55f2f89565632b7650a9d747ffa9c43`,
and `pipeline-auto-explicit-isolation.result.json` SHA-256
`2522b44da5cf0b4b8ea3bb230c14489426681da18828d9c7c61014af5f5f658d`.
These observations and the source `exec`/return paths support truthful failure
propagation; they are not a newly passing joined provider execution.

All 397 original entries remain unchanged: Word/PPT 135, workbook 135,
selected PPT 60 and PDF 67. Prior RED/ceiling/inspection failures are retained.
No pending P05 `78e4381`/`a75`/`fb08` candidate was imported or executed.

## Evidence digests and next actual gate

| Evidence | SHA-256 |
|---|---|
| `Q\auto-entry-source-pin\source-pin.json` | `7c6732c43c76aa04f2c699ec593a1325969d5b82ececacc702aa4262ae031fd8` |
| `Q\ae-spec01\seal.json` | `1108b474ea6b66bc94b7d4d67c2af4c1a518e461327d36ea4288490d5b14e4f2` |
| `Q\ae-spec02\seal.json` | `24d351084172125081cc234a811068160fd92a59c2b52ea7093be3e104161f73` |
| `Q\ae-spec03\results.json` | `0c686dba7be795ce4f2ae14c0d94a2fe987f6960ea8ed2e14d694f0b493c6362` |
| `Q\ae-spec03\seal.json` | `d860931bd16a6703fb589853cca67350a8ccf7b7fda0a16b1db63d89448baf6f` |
| `Q\ae-quality01\seal.json` | `daa59637d9feead9a9740fb7e48ccf19649ff881b8bd588ca527bcf454cfa8b5` |
| `Q\ae-quality02\results.json` | `455630fe3ebd76042745537c0c07d165de1006f78b228536e3fd14ca9944b476` |
| `Q\ae-quality02\seal.json` | `3176f2e64d875aa7944ebfe15a67876c6b4f3afaaf77942798e8c0a77d8b1f39` |
| `D\pipeline-auto-entry\source-freeze.json` | `e4aa818f4134d8841d558301994172796c38b7f22e8fc26edbf8ab14cd542fa4` |
| `D\pipeline-auto-entry\working-observations-scoped.json` | `af6e7945fd642be0d0e6548c178171a4d59247ceeea77ccd3a3e8f9de74d482a` |

The next full-caller gate is a separately authorized, accepted P05 provider join
and recheck of the preserved original failure identity, coordinated with its
original owner. It is **not performed or commissioned by this review**. No
shortened fixture, substituted namespace or passing different-root run clears it.

Word layout remains permission-blocked; workbook saved caches/layout and PDF
origins/complete visual gates remain open. Selected PPT `5858268`, workbook
`21e5228`, PDF `ae793d3`, common source `f2c1d09` and input-admission `c75eabc`
retain only their previously accepted scopes. Shared pipeline/runtime/theme/work
serialization, full A15 and P12, publication/SHIP and main integration are not
accepted here. Structured P05 decision/corroboration persistence remains closed.
No Office/UI/COM/browser/server/raster/network/dependency or denied-route action,
product repair, nested reviewer, merge, remote operation or parent completion
was performed. Final integration/publication remains the coordinator's authority.
