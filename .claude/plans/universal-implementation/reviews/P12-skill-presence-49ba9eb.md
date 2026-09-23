# P12 generation-skill presence correction: independent source review

## Decision and ownership

**Selected SPEC PASS, followed by eligible one-file SOURCE QUALITY PASS.**
Findings: **P1 0 / P2 0 / P3 0**. No product repair is requested.
This accepts only the released legacy presence-test expectation correction, not
PDF/XLSX execution, format maturity, native acceptance, A15 or P12 completion.

Reviewer: distinct session `31c39265-13e5-4057-9e78-49bf658749a5`.
Product owner: original P12 builder `0a75211f-455c-4318-864f-bc8023ce9142`.
Coordinator: `88aecc43-40f9-41d4-8947-6c2fb0a55481`; integration/publication remains
the coordinator's responsibility. Authority is the supplied bounded handoff citing
the coordinator's 2026-09-23 21:08 release. No broader review was inferred.

## Immutable subject

| Item | Verified identity |
|---|---|
| Base | `84e63a4e2bf3a0109b09abb4c5332b30b51276cf` |
| Product, sole parent base | `49ba9eb5175a1e689babb6a76420fe7a1ca1e2f8` |
| Builder report-only child, sole parent product | `61c3afdba7986a91168e5494a89b99a2c1275889` |
| Sole changed product path, called `T` below | `tests/unit/generate-skills-present.sh` |
| Product `T` SHA-256, 6,131 raw Git bytes | `761c9f7cd58ae8c14644d3ca6246c3a9fc7f3fc8dc069a24d2aaa17ecbb166a4` |
| Base `T` SHA-256 | `ce7b0bfddbcf5b452e8d28b6690eb6174a4dfa08370f318c209f7560721d525d` |
| Builder report | `.claude/plans/universal-implementation/reports/P12.md`, 345 LF lines, 22,009 raw Git bytes |
| Full builder report SHA-256 | `c53ac5feda2157c306cb295b7010afa333bb2a2054bcafd119001d011fbfaedb` |
| Appendix SHA-256 | `cd7961e8c2b76c45bff4656359ce7fd566438275f5bd658e74e09277c7890892` |

The full builder report, complete test and exact delta were read. The original
295-line, 18,872-byte report is an unchanged byte prefix; only lines 296-345
were appended. Twenty-two test inputs were exported from exact Git objects.
The other 21 inputs are byte-identical between base and product. No skill,
helper, integration test, CATALOG, provider or other product path changed.
Raw Git identities and normal source-Git/EOL checks were kept separate from
fixture execution and from the builder's working-copy hashes.

## SPEC: complete selected controls

All line references below address product `T`, unless another path is named.
The selected SPEC completed at `2026-09-23T19:52:07.4733123Z`, before QUALITY.

| Control | Verdict | Source and actual evidence |
|---|---|---|
| Exact released ownership and historical evidence | PASS | Verified both sole parents and sole changed paths. Original report prefix and 21 other inputs unchanged; pin manifest records raw hashes. |
| Keep Visio's original template/L-001 assertion | PASS | `T:69-75` retains case-sensitive marker lookup and original pass/failure diagnostics. Exact candidate passes; deleting the marker in only the Visio copy gives exit 1 and its one expected L-001 failure (`s05`). |
| Reject PDF template declarations | PASS | `T:76-79` uses case-insensitive rejection. Adding `TEMPLATE ONLY` to only the PDF description gives exit 1 and exactly its named failure (`s03`). |
| Reject XLSX template declarations | PASS | The same branch covers XLSX, without changing its name/layer checks. Lowercase `template only` in only the XLSX description gives exit 1 and exactly its named failure (`s04`). |
| Require existing concrete helpers | PASS | `T:87-91,98-104` names PDF `prepare_html.py`, `print_pdf.mjs`, `check_pdf.py`, and XLSX `check_xlsx.py`. Four separate missing-file copies each give exit 1 and only the matching support failure (`s06-s09`). |
| Require existing integration support/entries | PASS | `T:92-96,98-104` requires `document-pdf.py`, `.sh`, `.test.mjs` and `document-workbook.py`, `.sh` under `tests/integration`. Five separate missing-file copies each give exit 1 and only the matching support failure (`s10-s14`). Presence does not execute these files. |
| Preserve original metadata assertions | PASS | Original setup/orchestrator/shared checks and format frontmatter block are byte-identical; `T:22-67,106-117` retains names, foundation layers and required fields. No accepted assertion was replaced by the new helper loop. |
| Preserve color, mapping, overlays, voice ownership and legacy builders | PASS | Everything from original section 4 through the final exit block is byte-identical (`T:106-177`), including color, all mapping entries, `role_overlays`, `voice_gate_owner`, and PPT/web/Word presence checks. |
| Correct baseline and truthful failure propagation | PASS | Same other inputs: base gives exit 1, 24 PASS lines and exactly the two obsolete PDF/XLSX marker failures (`s01`); product gives exit 0, 35 PASS lines, no failure or stderr (`s02`). Each of the twelve negative SPEC cases gives exit 1, 34 PASS lines and exactly one expected failure. |
| Source-only claim and no product execution/writes | PASS | Header `T:4-7` expressly excludes native/runtime verification. New logic is only `grep`, file predicates and existing `fail`/`pass`; `T:171-177` retains the exit contract. Actual copies stayed unchanged, with no added source or synthetic-environment files. No helper or integration entry was executed. |

## SOURCE QUALITY: eligible after SPEC

The complete one-file QUALITY pass began at `2026-09-23T19:53:22.8568296Z`
and completed at `2026-09-23T19:54:32.7445532Z`.
No separate product implementation or child reviewer was used.

| Dimension | Verdict | Review and additional checks |
|---|---|---|
| Correctness and fail visibility | PASS | Explicit Visio/concrete branches implement the two distinct states, rather than weakening every slot. Named missing-file diagnostics feed the existing failure accumulator. All negative cases actually exit 1. |
| Completeness and preservation | PASS | All four required helpers and all five existing integration files are enumerated. Original frontmatter, color, mapping/overlay/voice-owner, legacy-builder and exit blocks remain intact, verified as byte-preserved regions. |
| Simplicity and scope | PASS | One conditional change, one fixed support array/loop, and a truthful header; no new parser, dependency, schema, provider, capability claim or execution path. Existing quoting and helper conventions are retained. |
| Shell/source behavior | PASS | `q01`: actual Bash syntax check exits 0; this is explicitly syntax-only, not a zero-test execution success. `q02`: a directory at required `check_pdf.py` is not accepted as a file, exit 1 with the one support failure. |
| Retained regression sentinels | PASS | `q03` wrong orchestrator name, `q04` wrong design color, `q05` missing QA mapping entry and `q06` absent legacy PPT skill each cause exactly their existing failure and exit 1. The color case still prints the unchanged aggregate PASS line, but does not falsely return success. |
| Evidence attribution and side effects | PASS | Each negative fixture differs in exactly one named input. Before/after hashes, complete copied-file inventories, empty owned environment directories and 175 original builder-evidence hashes were checked. No product change or original-fixture rerun occurred. |

There are no actionable P1/P2/P3 source findings in this released delta.
Confidence is high for this small source-presence contract, not for the behavior
or rendering of any file whose existence the test checks.

## Actual execution and retained failures

Reviewer evidence root `S` is
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\sp49`.
Builder evidence root `E` is
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-skill-presence`.

The reviewer executed 14 SPEC cases and six QUALITY cases: **19 executions of
the presence test plus one syntax-only check**. This is not 20 format tests.
Every successful preflight used fresh owned copies, a cleared process environment,
owned HOME/USERPROFILE/AppData/temp/XDG and derived Lintel locations, empty Git
config, strict-parent Git ceilings, fixed PATH/PATHEXT, closed stdin and
**zero `LINTEL_*` exports**. Bash startup/profile files were disabled. Effective
environment and installed-tool bindings were inspected before the exact test.
Preopened stdout/stderr, exact argv/cwd, real exits, mutations and input hashes
are retained per case. No jq, Python/Node product import, helper execution,
provider, full suite, native action, network or installation was used.

The first private preflight (`S\spec\s01`) refused with exit **92**, before
the test ran: the installed Git Bash launcher had prepended the fresh owned
HOME's `bin` directory to PATH. This refusal and its outer exit 1 are retained.
Only the private wrapper was corrected to record the incoming path and set the
fixed installed-tool PATH before inspection. Fresh `spec-02` cases then ran.
No product source, builder fixture, global path or policy was changed.

**Builder warning distinction is preserved, not waived or misreported.**
`E\committed\committed-source.result.json` and its raw output show the test
itself exited **0**, with **35 PASS** lines and no test failure. Its stderr
contains two `bash.exe: warning: could not find /tmp, please create!` lines.
`E\logs\driver-committed.result.json` records the separate inspector's **exit 1**;
its traceback identifies the extra `assert not stderr`. The later builder seal
confirms exact executed test-source identity with GREEN. That test was not
nonzero, but its execution was not stderr-clean either. The reviewer did not
repair `/tmp`, suppress the warning, rerun the builder's committed route or
replace that evidence with the reviewer's clean-stderr observations.

## Reusable evidence identities

Paths in this table are relative to `S`; all hashes are SHA-256.

| Record | Hash |
|---|---|
| `pin\results.json` | `29d03cc76965531538d5f7121332b60b10f0f11ae97ee9714c7051e141df2dc6` |
| `pin\owner-manifest.json`, 175 builder evidence files | `ceee7178752f80350110ecbf178154aac061878cdd6bd917d1ef4eb2d10125df` |
| `spec\failure.json`, retained private preflight refusal | `7b9bad388613068be3eaac847cfa3b84e26c2cccccfc56c4648801ea960811da` |
| `spec-02\results.json`, 14 cases | `41c22fd27a2fcb5879052022d0d2120d14e2869f9f5cb548d8e245d735d37ffc` |
| `quality-02\results.json`, six cases | `ac742dc18488a7794c75e1eaa01558b003f0d3f484757d00872bda1ade42d6cb` |
| `audit\results.json`, ordered-stage/input/evidence inspection | `0e1ee5558fa4ba0fbc83ce3178a8ce97645311e74c0d3235b3df1c6e9f3b6cd8` |

The pin also verified the supplied builder GREEN, mutations, seal and audit
digests. Those observations remain attributed to the builder, separate from
the reviewer's actual runs. The final inspection rehashed all 175 scoped
builder evidence files and both completed execution seals without changes.
Normal source `git diff --check` passed for the exact product delta.

## Limits and next gate

This is a human-readable source-review checkpoint only. It creates no P05
structured decision/corroboration and clears no denied persistence route.
No Office/UI/COM/browser/raster/renderer or alternate application route was
used or reopened. Existing maturity remains unknown; prior selected source
acceptances remain separate, not extended by this presence check.

Word pagination/layout permission, workbook persisted calculation caches/layout,
PDF origins/complete visual inspection, other native gates and P12/A15 parent
acceptance remain unchanged. Existing provider/full-caller observations are
neither rerun nor cleared here. The next action is coordinator intake of this
one-file correction and report within its existing integration authority;
format/native or parent clearance still requires separately released evidence.
