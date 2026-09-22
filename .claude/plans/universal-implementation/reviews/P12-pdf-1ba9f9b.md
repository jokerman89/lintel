# P12 PDF source correction review

Date: 2026-09-22. **D01-D03 bounded writer/source SPEC PASS, then source QUALITY
PASS. All three prior findings closed; new P1=0/P2=0/P3=0.** This accepts the
released source correction, not the original PDF specimen or full A15.4.pdf/P12
acceptance. The original sixteen failing text origins, unverified complete visual
inspection and unavailable Markdown conversion remain explicitly non-clearing.

Same independent reviewer: project `f42bff7a-1c88-4784-80c9-60c37f683785`,
runtime `31c39265-13e5-4057-9e78-49bf658749a5`. Builder: project
`09666ec2-ff03-4517-9169-8793149ea8cd`, runtime
`0a75211f-455c-4318-864f-bc8023ce9142`. Coordinator:
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. No product fix, new reviewer, native
action, decision or corroboration was performed by this review.

## Exact reviewed scope

| Item | Identity |
|---|---|
| Complete D01-D03 release card | `a9476b25660579ad542619c7d9a7eaf3ea27edd5` |
| Prior source findings | `0ea284cd73c66584216d6ccc785afd6ec96b509c`, `reviews\P12-pdf-5978def.md`, unchanged |
| Repair product | `1ba9f9b2b71bb470595e66adbbfb715d92d0c9ba` |
| Sole product parent | `5d82498aa6019298b045ca2c5583d4d0df5a92c4` |
| Report-only child / pinned review parent | `124780e24d459162bb6cf024342465babba8eab2` |
| Complete builder report | `reports\P12-pdf-source-repair.md`: 195 LF lines, 12,024 Git bytes; SHA-256 `9d1fd5cdb63277e98f8436a0a6f1066fd6f1d2ca96144f8c167666aa710ce775` |
| Builder committed replay, verified as input | SHA-256 `40489ed512662520eee71b38de096f6e0cce1e04fa48432d86292322f4a06b3c` |
| Builder committed preservation, verified as input | SHA-256 `f3e13c14e4defade6c17be19291a2c3d8aa50cbb07a7924405884d58fa26a3d6` |

The clean checkout was detached at exact `124780e`, not a moving source branch.
Earlier workbook repair `21e5228`, PDF `0ea284c`, workbook `0c1a711`, PPT
`5858268` and earlier review refs remain preserved.

All five changed files and their complete delta were reviewed:
`skills\generate-pdf\scripts\check_pdf.py`,
`skills\generate-pdf\scripts\prepare_html.py`,
`tests\integration\document-pdf.py`,
`skills\generate-pdf\SKILL.md` and `skills\make-pdf\SKILL.md`.
Twenty-four selected dependencies remain unchanged, including the print adapter,
accepted browser provider, six Node tests, shell entry and workbook sources.
The original PDF writer/source review and its unchanged evidence remain applicable
outside the repaired areas. No common eleven-file Word/PPT closure, shared
pipeline, workbook-format acceptance or blanket ancestry approval is implied.

## Source SPEC, before QUALITY

Source SPEC completed at **2026-09-22T21:36:33.4960621Z**. QUALITY began later at
**21:38:09.3410668Z**. References below name exact product `1ba9f9b`.

| Finding | Verdict | Source and actual recheck |
|---|---|---|
| D01 UserUnit/physical dimensions | **CLOSED / PASS** | `check_pdf.py:49-72,96-100` reads the existing reader's actual metadata, rejects nonnumeric/nonfinite/nonpositive scale, and compares physical MediaBox dimensions. Exact unit-2 wrong-paper input now fails/exit 3; correct doubled paper passes/0; zero/negative units error/2. Raw coordinates remain unchanged. |
| D02 effective page boundary | **CLOSED / PASS** | `check_pdf.py:61-72,84-100` validates ordered finite boxes and their nonempty intersection. The saved oversized-crop/translated-content case now fails/3 with all 41 origins retained; ordinary and narrowed controls remain correct. Raw crop membership is retained separately from media/effective membership. |
| D03 HTML text contexts | **CLOSED / PASS** | `prepare_html.py:32-63` uses existing parser text contexts for title/textarea, retains script/style handling and decodes collected title references once. Both saved raw `</head>` text cases now prepare/exit 0; escaped counterparts, comments/LF offsets and real duplicate-head refusal remain correct. |

All **29 exact saved PDF-1.7/HTML cases** were independently replayed from
manifest-verified byte copies through the actual CLIs. Every original status/exit
oracle now matches, including the seven previously discrepant cases and the
22 positive/refusal controls. No saved input, expected outcome or old failure
was rewritten.

All **30 Python methods plus six unchanged Node tests pass**, zero
failures/errors/skips. The geometry suite includes six actual reader CLI
contrasts, not mock rendering. Independent AST comparison confirms all **18
original Python test methods unchanged**; all six Node definitions remain exact
apart from checkout EOL. This is source behavior evidence, not general model or
cross-client verification.

## Eligible bounded source QUALITY

QUALITY checks completed at **2026-09-22T21:38:15.3687639Z**; final bounded source
assessment recorded at **21:38:59.3655538Z**. **PASS; no new P1/P2/P3 findings.**

| Dimension | Assessment |
|---|---|
| Correctness/error handling | Invalid page metadata and physical overflow fail explicitly. Effective geometry retains raw values and all observed origins; no clamping, source omission or success-shaped fallback. |
| Compatibility | Original input/output/paper/orientation/CSS/header/background arguments remain. Raw result fields retain their meanings; physical/effective diagnostics are additive and format-local. Omitted UserUnit uses the reader's PDF default, not a fallback for missing API or invalid data. |
| Text fidelity | RCDATA handling changes only boundary interpretation, not supplied content. Removing the inserted style block reconstructs the original input; title references decode once, and textarea text cannot replace the document title. |
| Trusted source and ownership | Existing P03 owned-path/expected-state I/O and P07 header parser remain. The unchanged thin print adapter consumes accepted A16 public operations and closes its owned session; no new engine, parser, daemon or publication shortcut. |
| Tests and simplicity | Exact historical replays, unchanged assertions, actual reader CLI cases and eight additional independent quality contrasts cover the correction. No dependency expansion or unmeasured performance/visual claims. |

The **eight additional QUALITY cases** pass with expected CLI exits and unchanged
inputs: fractional scale with shifted media; a wrong physical dimension outside
the existing tolerance; empty effective boundary; finite scale causing physical
overflow; mixed-case title with once-decoded entities; textarea false-title text;
script/style literal-head controls; and a genuine duplicate head after RCDATA.
Prepared HTML remains explicitly unrendered. Non-error reader diagnostics retain
`complete_visual_inspection:unverified`; all reader outcomes deny release clearance.

## Native specimen and policy gates stay open

Original PDF SHA-256 remains
`89e209ed5e2b9f5500b6d827068b7a723e809197a8ea9a7d97a1498fcce9d246`.
All four pages have UserUnit **1**. Independent comparison preserves every original
page's text, MediaBox, CropBox, text-origin coordinates, font-size values and crop
membership. New media/effective diagnostics do not replace those observations.

Repreparation from the exact original HTML/CSS/header bytes still yields
`417d084825b3465a06b55609803c6e5da2ab6d1b41c08f0783dc82810200f342`,
the HTML used for the prior actual print. No new print or conversion is claimed.

| Original control / scope | Current result |
|---|---|
| D01-D03 released source correction | **SPEC PASS / source QUALITY PASS** at this exact source. |
| Existing native print/cleanup | Prior builder's actual output and cleanup evidence retained; not re-executed. |
| Existing PDF source text and page checks | **PASS for the unchanged unit-1 four-page specimen**. |
| Existing native text-origin check | **FAIL**, exactly 16 page-3 origins remain outside at approximately `[50.999997875, 2271.4199204375]`; actual reader CLI exits **3**. |
| Complete PDF visual inspection | **unverified/denied**, not replaced with extraction, origins or HTML. |
| Markdown conversion | **unverified in the selected environment**; missing converter/TLS failure retained, no install/retry. |
| Original P05 QA | **blocked**, independent controls CLI exits **3** for origins and complete visual inspection. Old requirements, observations and receipt are unchanged. |
| Full A15.4.pdf / P12 / parents | **open/unverified**; source review is not specimen or format clearance. |

D01/D02 do not explain or fix the original sixteen coordinates. No reader
diagnostic retry, alternative reader, raster inspection or assumption about
actual clipping was introduced. The previous failed experimental-layout result
remains historical evidence, not a resolved gate.

## Commands, evidence and limitations

Read-only builder root `D`:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
Reviewer root `Q`:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

| Actual command | Outcome |
|---|---|
| `pdf-source-pin.ps1 -Stage repair` | Exit 0: five owned paths, 24 unchanged selected dependencies, exact authority/report/Git/CRLF identities. |
| `review-run.ps1 -Label pr-t01 -Mode pdf-repair-tests` | Exit 0: **30 Python + 6 Node pass**; native reader-copy CLI exit 3, sixteen original failures; raw observations and exact prepared HTML preserved. |
| `review-run.ps1 -Label pr-r02 -Mode pdf-repair-replay` | Exit 0: **29/29** exact saved CLI cases; 18 original ASTs and six Node definitions unchanged. |
| `review-run.ps1 -Label pr-e01 -Mode pdf-repair-evidence` | Exit 0: all **397** earlier artifact hashes unchanged, original work/QA identity verified, controls CLI exit 3; four links, Bash syntax and 3.9 grammar checked. |
| `review-run.ps1 -Label pr-q01 -Mode pdf-repair-quality` | Exit 0: **8/8** additional actual CLI compatibility/error cases and read-only checks. |

Initial private replay `pr-r01` was 28/29, exit 1: the reviewer supplied the known
header control as JSON object text to the declared YAML-only P07 parser. Its
explicit error was correct. Only that private control's serialization was changed
to plain YAML keys with quoted values; `pr-r02` is 29/29. Both runs are retained.
This was not a product defect, altered original HTML/oracle or relaxed parser.

| Reviewer result | SHA-256 |
|---|---|
| `Q\pdf-repair-source-pin\source-pin.json` | `e081b8a4a35d8f5a0c881a769468ba886c595817b882ad358b8fab821f9a5a28` |
| `Q\pr-t01\results.json` | `c6f983fb8017146021915ff9912e0e0f8cafd44d699b9b2f18d985ca9ad17a3d` |
| `Q\pr-r02\replay.json` | `63b2540a4b1e2195aa21f1c1bc79860fb25182cc639f204277197314f337e623` |
| `Q\pr-e01\evidence.json` | `e0e6b6fc0f0c69ef178c5239ecca77c18c8a6d033fc26ca81704f0713072eb1e` |
| `Q\pr-q01\quality.json` | `323e92ca1ce838da41b6ff4975a9674a3f3861de13ccc7b7a9bbccdce1ad9483` |

Original repro pins remain `Q\p-c03\cases.json`,
`a31c385fa9de9cac543e73c7b2d63560d120cc7ddfa2b267c1e7f140b736b4ff`,
and `Q\pdf-final-repro-manifest.json`,
`79d424af0e177f5f890256d4d483df7f88a6db1cf7c201965e2950b42b29eed2`.
Saved pairs and new CLI logs are retained under the reviewer-owned run roots.

All product imports/calls used inspected per-process synthetic HOME/USERPROFILE/
AppData/temp/Lintel/derived paths/PATHEXT, trusted source closure and verified
fixture Git ceilings. Source Git/EOL checks stayed separate. Logs were preopened;
actual argv, stdout/stderr, exits and source/env seals remain. Node ran only pure
request validation under process/network guards, recording zero attempted
subprocess/network actions; it did not construct Admission or BrowserSession.

Python 3.11.9, existing pypdf 6.13.2 and Node 24.16.0 were used. Grammar checks
are not minimum-runtime execution. Test main environment replacement was not used.
File-only PDF fixtures/copies came from the existing reader/writer, not native
printing or a new parser/engine. No full suite, browser/server/UI/COM, raster,
alternate reader/layout retry, network, dependency install, policy change,
P05 decision/corroboration or publication occurred.

## Handoff

Only the reviewed five-file correction and affected writer/source methods are
ready for scoped coordinator integration; no additional source repair is requested.
This does not approve every product in the ancestry or complete common Word/PPT
source review. Native format, shared-pipeline, other-format and parent gates remain
separate. This completed checkpoint closes D01-D03 source findings only.
