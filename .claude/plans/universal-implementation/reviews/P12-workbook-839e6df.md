# P12 workbook integrity repair review

Date: 2026-09-22. **W01-W04 bounded source SPEC PASS, then source QUALITY PASS.
All four prior findings closed; new P1=0/P2=0/P3=0.** This accepts the released
source/checker correction only. Native persisted caches and rendered workbook
inspection remain unverified; no full A15.4.xlsx, XLSX/P12 parent or strict
P05 clearance follows.

Same independent reviewer: project `f42bff7a-1c88-4784-80c9-60c37f683785`,
runtime `31c39265-13e5-4057-9e78-49bf658749a5`. Original builder: project
`09666ec2-ff03-4517-9169-8793149ea8cd`, runtime
`0a75211f-455c-4318-864f-bc8023ce9142`. Coordinator:
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. The reviewer made no product changes
and created no nested reviewer, engine, cache publisher or structured decision.

## Exact source and authority

| Item | Pinned identity |
|---|---|
| Complete bounded correction card | `764cf5328378a20140dc482fe7950af0a9c24a2a` |
| Original independent findings | `0c1a7115ef2a0c5e267f25ce04e9807eadf63936`, `reviews\P12-workbook-5b8818c.md` |
| Repair product | `839e6df90193eaf7099e9f8d87fd2287d7bb195e` |
| Sole product parent | `9b4a8a1dc58d2f15e02376390169aa6ce30b5d0e` |
| Report-only child / pinned review parent | `5d82498aa6019298b045ca2c5583d4d0df5a92c4` |
| Complete builder repair report | `reports\P12-workbook-integrity-repair.md`: 180 LF lines, 10,962 Git bytes; SHA-256 `0fffa82b26a3b19632f157a94145ccec492f1ea528fa0ceadd9b11985c895497` |
| Builder committed replay, verified as input | SHA-256 `6fa4513b8664d3246a7b0e358d8557f9f04c6462a18da7b713becb54fde10f13` |

The clean checkout was detached at exact `5d82498`, not a moving builder tip.
Prior PDF `0ea284c`, workbook `0c1a711`, PPT `5858268` and earlier reviews remain
preserved on separate refs. Their findings/history were not rewritten.

Only four product paths change from the product parent:
`skills\generate-xlsx\scripts\check_xlsx.py`,
`tests\integration\document-workbook.py`,
`skills\generate-xlsx\SKILL.md` and
`skills\generate-xlsx\references\native-xlsx.md`.
All were read completely, including the full delta. Twenty-two selected provider,
fixture, entry and PDF paths remain unchanged. No PDF D01-D03 repair, Word/PPT,
shared schema, P09/P11 A14 or generated output was selected or changed.

## Source SPEC and original finding closure

Source SPEC was recorded at **2026-09-22T20:19:02.9948388Z**, before the QUALITY
command began at **20:21:38.1482235Z**. References below are exact `839e6df`.
`checker` means `skills\generate-xlsx\scripts\check_xlsx.py`.

| Finding | Verdict | Source and independently verified behavior |
|---|---|---|
| W01 package metadata/relationships | **CLOSED / PASS** | `checker:94-185`: required content types, real parts/owners, every declared internal target, consistent known kinds and semantic forbidden mechanisms are checked before cells. All seven original W01 discrepancy packages now error/CLI 2; complete metadata and contained relative/absolute positives pass. |
| W02 ambiguous cell/string payloads | **CLOSED / PASS** | `checker:202-224,263-270,303-340`: SST namespace/root, allowed cell types and payload multiplicity are checked before decoding/empty branches. Wrong-root SST, duplicate inline payload and invalid empty type now error/CLI 2. Plain/rich/shared/inline/blank and literal values remain supported. |
| W03 encoded declarations | **CLOSED / PASS** | `checker:80-91`: the existing parser's declaration hook refuses the inert UTF-8/UTF-16LE/BE DTD cases; ordinary non-DTD UTF-16 and declaration-looking literal/CDATA text pass. No alternate parser, external entity or amplification case was used. |
| W04 explicit normal formula | **CLOSED / PASS** | `checker:412-419`: omitted and explicit `t="normal"` are equivalent; original normal-formula repro now passes/CLI 0. Stale values still fail and missing caches stay unverified. Genuine shared/array/data-table/unknown attributes do not clear. |

All **15 exact saved CLI cases** were replayed independently from manifest-
verified copies: the thirteen original discrepancies, complete-package positive
and UTF-8 refusal. Results are two legitimate integrity passes/exit 0 and thirteen
explicit errors/exit 2, exactly matching the original oracles. This is not merely
agreement with a new builder test.

The original independent **50-case matrix** also now has zero discrepancies.
All **50 product test methods** pass, zero failures/errors/skips. Independent AST
comparison proves the original **23 test methods unchanged**. Adding complete
positive package metadata fixes the fixture rather than weakening assertions.
Valid positives prevent an all-errors implementation from appearing successful.

The actual native shared-string `phoneticPr` formatting metadata is retained
without inventing phonetic text. Ten complete Methods paragraphs, citations,
capacity/claim cells and literal `=1+1` remain byte/meaning consistent in the
saved workbook. Unsupported phonetic text/payloads still refuse.

## Eligible bounded source QUALITY

QUALITY command completed at **2026-09-22T20:21:42.9857326Z**; completed source
assessment recorded at **20:23:34.5318457Z**. **PASS, no new P1/P2/P3.**
This is quality of the authorized reader/source repair, not a claim that missing
engine-persistence or visual-format acceptance has been supplied.

| Dimension | Assessment |
|---|---|
| Correctness and errors | Package/relationship checks precede decoding; payload type/cardinality precedes missing-value branches. Invalid data errors are explicit; missing caches/unsupported semantics remain non-clearing. Public CLI status/exit and read-only behavior match API results. |
| Compatibility and preservation | Equivalent content-type/extension casing, explicit Internal relationships, significant inline whitespace and empty shared strings pass. Legitimate native formatting survives; hidden formulas, typed errors, source loss and stale cache regressions remain. |
| Ownership and trust | P03 owned-root/read primitives and trusted-source imports are retained. Inputs and expectations stay data; no package content, formula, macro or relationship target is executed/fetched. No shared policy/schema fork or new dependency. |
| Bounds and simplicity | Existing 64 MiB input/expanded, 16 MiB part and 10,000-entry checks remain and are exercised at their actual thresholds. Helpers separate metadata, relationships and text; no spreadsheet engine or general malware/schema certification is implied. |
| Test strength and clarity | Exact historical replays, unchanged original assertions, complete positive fixtures, independent 50-case matrix and additional eight CLI/API quality contrasts establish the intended correction rather than counts alone. |

The **eight additional source QUALITY cases** all match expected API and CLI
results: five compatibility positives, two malformed nested/phonetic payload
errors and one uninterpreted normal-attribute unverified result. Every case
preserves its input and reports release clearance false; non-error diagnostics
also explicitly decline calculation-execution and rendered-layout verification.
No issue was found requiring a product change by this reviewer.

## Original native and policy gates remain

| Control / leaf | Current status |
|---|---|
| W01-W04 source correction | **SPEC PASS / source QUALITY PASS**, only this component. |
| Native source/cell retention | **PASS** at saved-data layer; full long Methods content, citations and tables retained. |
| Native calculation/editability | Previously supplied real observations retained, not re-executed: 37.5 -> 50, saved-copy edit 62.5 and semantic restore 50. |
| Persisted-cache | **unverified**: same native workbook still has exactly two `cache_missing`, at Calculation!B2 and Summary!B2; actual checker CLI exits **3**. |
| Rendered-workbook | **unverified**, renderer unavailable and application permission blocked; no alternative route. |
| Original full-scope P05 QA | **blocked**, independent controls CLI exits **3** for persisted-cache and rendered-workbook. Original context/QA remain unchanged. |
| A15.4.xlsx / P12 / parents | **open/unverified**; source repair does not satisfy full native-format acceptance. |

Native hash remains
`c0cd1608350b78052f4f78f74074d615ade33cb93e102fd50afc71fc89d5c5db`.
No calculated value was inserted into that workbook. Synthetic numeric caches
exist solely as test oracles; they are not engine execution evidence.
The old 23-method QA observation was not rewritten as a new 50-method receipt.

## Reproducible evidence and boundaries

`W` is the read-only builder root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-workbook`.
`Q` is the reviewer root:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

| Actual command | Result |
|---|---|
| `workbook-source-pin.ps1 -Stage repair` | Exit 0: four owned paths, 22 unchanged selected dependencies, original authority/report and Git/CRLF identity. |
| `review-run.ps1 -Label wr-t01 -Mode workbook-repair-tests` | **50/50**, zero failures/errors/skips, exit 0; separate native checker CLI exit 3 with two unchanged missing caches. |
| `review-run.ps1 -Label wr-r01 -Mode workbook-repair-replay` | **15/15** exact saved CLI cases, exit 0; original 23 method ASTs unchanged. |
| `review-run.ps1 -Label wr-c01 -Mode workbook-repair-cases` | **50/50** independent matrix outcomes, exit 0; original discrepancies closed and retained positives/refusals preserved. |
| `review-run.ps1 -Label wr-e01 -Mode workbook-repair-evidence` | Exit 0: **397** prior artifact hashes unchanged; complete native data and unchanged QA obligations verified; controls CLI exit 3; links, Bash syntax and Python 3.9 grammar checked. |
| `review-run.ps1 -Label wr-q01 -Mode workbook-repair-quality` | **8/8** additional compatibility/error cases, exit 0; each actual CLI exit/status and read-only input verified. |

Original repro authority remains `Q\workbook-repro-manifest.json`,
SHA-256 `cedd617ffa958e460bc0cde41184888c2f302faffdc415d7ba8d741c77778e38`,
and `Q\w-c02\cases.json`,
`61dfabaf3188e4898f5c0c17f0259f2d918b6006b877140f13a985d7fc61db5a`.
They and the earlier failed artifacts/reports remain unchanged.

| Reviewer result | SHA-256 |
|---|---|
| `Q\workbook-repair-source-pin\source-pin.json` | `5e8790be40f479397225e2c853e7c4f32f65bb0b6d070bfc42f2daf66a77b6ee` |
| `Q\wr-t01\results.json` | `05c0b6add50374624cfe412e2e101194813e65b155c54a917bceaf738565639d` |
| `Q\wr-r01\replay.json` | `3f1788c7a9dbfd273710417ff6d8c78a5f1a2c872e562a4df62040d06494e85a` |
| `Q\wr-c01\cases.json` | `50bf4702782bdd8b74e5f630f980568ee17386d231bc972922258524185cabf1` |
| `Q\wr-e01\evidence.json` | `53165496f1a8da3df14dbd7c2961c5b17fa203422ee99f7d302e6ada8190e19d` |
| `Q\wr-q01\quality.json` | `97f8bb2dd710273282280d5fa4765c714b043cfde0943d8e0aa08eb7d5fbbca7` |

Every product import/call used inspected per-process synthetic HOME/USERPROFILE/
AppData/temp/Lintel/derived paths/PATHEXT, explicit trusted source closure and
fixture Git ceilings/ancestor refusal. Source Git/CRLF checks were separate.
Actual stdout/stderr/exits were captured in preopened logs with source/env seals.
Unchanged test classes ran under the reviewer allowlist, not the test main's
environment replacement. All artifact/checker calls used owned copies or synthetic
in-memory packages; builder originals and reviewer historical repros stayed read-only.

Python 3.11.9 was observed; 3.9 grammar is not minimum-runtime execution.
No full suite, engine, native UI, Office/COM, renderer, network, dependency install,
DTD amplification/external entity, profile relocation or policy change occurred.
No denied P05 decision/corroboration or alternative writer route was attempted.

## Handoff

Only the reviewed four-file correction is ready for coordinator integration at
the exact identity, not blanket acceptance of its PDF-containing ancestry.
No additional source repair is requested by this report.
Only separately authorized real cache-persistence/render observations can advance
the remaining full XLSX gates. PDF D01-D03, other formats, strict persistence and
P12 parent work remain separate; this completed checkpoint closes W01-W04 source
findings, not the workbook initiative.
