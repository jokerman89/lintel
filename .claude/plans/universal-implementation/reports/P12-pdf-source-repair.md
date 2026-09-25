# P12 PDF D01-D03 source correction

Date: 2026-09-22. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`,
runtime `0a75211f-455c-4318-864f-bc8023ce9142`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Status: bounded source repair frozen for SAME reviewer.** The seven reproduced
discrepancies now match their expected outcomes. Builder self-review reports no
remaining owned-code P1/P2/P3 finding; this is not independent SPEC or QUALITY.
The actual PDF's sixteen unresolved origins and required visual inspection remain
non-clearing. A15.4.pdf, P12 and parent acceptance are still open.

## Exact authority, ancestry and scope

Read the complete P12 card from Git release
`a9476b25660579ad542619c7d9a7eaf3ea27edd5`, including **PDF D01-D03 source
correction**. This release was not merged. The selected map remains
`.claude\plans\universal-implementation\work.json`; no new plan or backlog was made.

Independent review `0ea284cd73c66584216d6ccc785afd6ec96b509c`, sole parent
`9b4a8a1dc58d2f15e02376390169aa6ce30b5d0e`, was read in full: 210 lines,
Git-byte SHA-256 `6197da20821420272034354c560726a8f23ad24979a1b154cb9a928c456de009`.
Its verdict is source SPEC FAIL, P1=0/P2=3/P3=0, QUALITY not started.

Product **`1ba9f9b2b71bb470595e66adbbfb715d92d0c9ba`** has sole parent
**`5d82498aa6019298b045ca2c5583d4d0df5a92c4`**. That parent is the report-only
child of workbook repair `839e6df90193eaf7099e9f8d87fd2287d7bb195e`.
This report is a separate report-only child; its exact commit and Git-byte digest
are supplied in the immutable handoff.

Exactly five product files changed:

- `skills\generate-pdf\scripts\check_pdf.py`
- `skills\generate-pdf\scripts\prepare_html.py`
- `tests\integration\document-pdf.py`
- `skills\generate-pdf\SKILL.md`
- `skills\make-pdf\SKILL.md`

The accepted A16 dependency remains inherited through `51b6f301` and `3049811`;
no coordinator ancestry or pending provider source entered this repair. Frozen
PDF `5978def`/`9b4a8a1`, Word/PPT/F01 and workbook history are preserved.
The print adapter, browser provider, workbook sources/reports, agents, shared
schemas, installer, generated files, master ledgers and other worktrees were not
changed. Local Conventional Commits include the required Copilot trailer.

## Implemented corrections

**D01:** read the existing pypdf `PageObject.user_unit` metadata, resolve a returned
PDF object if necessary, and require numeric finite positive scale. The reader's
PDF-defined default still supports an omitted UserUnit; absent API support or
invalid metadata is an error, not a silent unit-1 fallback. Physical MediaBox and
effective-box width/height multiply raw differences by the actual scale. Existing
`paper_points` now compares those physical MediaBox dimensions with the retained
2-point tolerance. Raw boxes, origins and font-size observations are not scaled.

**D02:** require finite ordered MediaBox/CropBox coordinates and a nonempty
intersection. Origin checks use both boxes. An oversized crop cannot conceal
out-of-media origins; a smaller crop still restricts the region. Raw observations
and original `within_crop_box` meaning remain intact. Additive diagnostics expose
`effective_box`, `user_unit`, `physical_media_points`,
`physical_effective_points`, `within_media_box` and `within_effective_box`.
Invalid/empty regions refuse; no text origin is clamped or discarded.

**D03:** extend the existing HTMLParser text-content contexts for `title` and
`textarea`, retaining script/style handling. A literal `</head>` there is data,
not a document boundary. Collected title character references decode exactly
once for margin text; complete supplied HTML remains untouched apart from the
existing CSS insertion. Real duplicate-head refusal, LF-based offsets, comments,
source ownership/publication checks and missing-converter refusal are retained.
No new HTML/Markdown/PDF parser, dependency or renderer was introduced.

Existing arguments, source expectations and result fields remain compatible;
new fields are format-local observations, not a shared schema or domain envelope.
Reader exit 0 still means only requested reader checks, exit 3 failed/unverified
observations, and exit 2 input/reader error. Complete visual inspection remains
unverified and `release_clearance` false even for a reader PASS.

## Exact saved-input reproduction

`Q` is the reviewer-owned root:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.
Verified `Q\p-c03\cases.json` SHA-256
`a31c385fa9de9cac543e73c7b2d63560d120cc7ddfa2b267c1e7f140b736b4ff`
and `Q\pdf-final-repro-manifest.json` SHA-256
`79d424af0e177f5f890256d4d483df7f88a6db1cf7c201965e2950b42b29eed2`.

The builder replay copies exact saved PDF/oracle/HTML bytes from `Q\p-c03\r`
after per-file hash/size checks and adds owned YAML for the two named header
controls; it does not execute reviewer helper code. All 29 final PDF-1.7/HTML
cases run through the actual helper CLIs. Before repair, the same seven
discrepancies reproduce. After repair and again on committed product,
**29/29 expected status/exit pairs match**, with unchanged input hashes.

| Saved discrepancy | Before status / exit | Repaired status / exit |
|---|---|---|
| `userunit-two-wrong-paper` | pass / 0 | fail / 3 |
| `userunit-two-physical-paper` | fail / 3 | pass / 0 |
| `invalid-userunit-zero` | pass / 0 | error / 2 |
| `invalid-userunit-negative` | pass / 0 | error / 2 |
| `crop-outside-media-hides-origin` | pass / 0 | fail / 3, all 41 origins retained |
| `literal-head-marker-in-title` | error / 2 | prepared / 0 |
| `literal-head-marker-in-textarea` | error / 2 | prepared / 0 |

The other 22 saved cases retain their expected results, including unit-1, rotated,
source/paper mismatch, partial/encrypted PDF, narrowed crop, escaped text, header/
CSS and comment/non-LF controls. The reviewer's earlier inherited-PDF-1.4 cases
remain distinct diagnostic history; they were not used as the UserUnit oracle.

## Actual verification and evidence

`D` is the builder-owned root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
The existing `p12-pdf-run.ps1` is beside D. Each log label below has separately
preopened stdout/stderr, recorded argv/environment and actual exit JSON under
`D\logs`; no pipeline masks a child exit.

| Check / log label | Actual result |
|---|---|
| `d01-d03-reproduce-before` | Exit 1: exact seven discrepancies among 29 saved cases. |
| `d01-d03-regressions-red` | Exit 1: new geometry/RCDATA regressions fail before product edits; original tests retained. |
| `d01-d03-regressions-green1`, `d01-d03-request-tests` | Exit 0 each: 30 Python methods and six unchanged Node tests pass. |
| `d01-d03-reproduce-after` | Exit 0: all 29 saved status/exit pairs match. |
| `d01-d03-committed-python-tests`, `d01-d03-committed-node-tests` | Exit 0 each at `1ba9f9b`: 30 + 6 pass, no failures/errors/skips. |
| `d01-d03-reproduce-committed` | Exit 0: all 29 exact saved cases match on the frozen source. |
| `d01-d03-native-reader-cli` | Exit 3: unchanged actual PDF still fails the sixteen origin observations. |
| `d01-d03-preservation-exact-bytes`, `d01-d03-preservation-committed` | Exit 0 each: 397 prior evidence files unchanged, original 18 methods AST-identical, four local links valid, exact HTML identity. |
| `d01-d03-check-whitespace`, `d01-d03-staged-check` | Exit 0: unstaged/staged whitespace checks. |
| `d01-d03-whole-scope`, `d01-d03-product-status` | Exit 0: only five owned product paths differ from `5d82498`; clean worktree after product commit. |

New tests are eight geometry methods and four text-context methods. They use
actual pypdf-created searchable PDF 1.7 fixtures and six real reader CLI cases,
not a stubbed native renderer. Coverage includes omitted/explicit unit 1, unit 2
with wrong/correct dimensions, fractional scale/nonzero box origin, zero/negative/
invalid-type/overflow scale, normal/narrow/oversized/disjoint/empty/inverted boxes,
translated origins, raw/escaped RCDATA, one-time entities and source preservation.
The original 18 test method ASTs and six Node definitions are unchanged. Node
executes pure request validation, not Admission or BrowserSession operations.

One private preservation attempt, `d01-d03-preservation-working`, exited 1:
the verifier used universal-newline `read_text` on CRLF source/CSS and therefore
did not reproduce the exact original bytes. Reading bytes and explicitly decoding,
as the production CLI already does, fixed that harness comparison. The failure
is retained; no product or original artifact was changed to make it pass.

The existing runtime is Python 3.11.9, pypdf 6.13.2 and Node 24.16.0. Python 3.9
grammar was checked, not executed; no full-suite, other CLI, alternate reader or
minimum-Node-runtime verification is claimed. Sources are sealed before imports.
Allowlisted synthetic HOME/USERPROFILE/AppData/temp/Lintel/source/target roots,
PATH/PATHEXT and actual Git ceilings are recorded. Source Git uses its separate
source-root configuration, not a fixture's Git configuration. No inherited token,
personal profile, policy redirect, network/install or application action was used.
These are process-environment controls, not an OS sandbox. Temporary test cases
use scoped cleanup; exact replay inputs and logs remain owned review evidence.

| Evidence relative to D | SHA-256 |
|---|---|
| `d01-d03\before\results.json` | `5e493d0f58e32a39d6bf977d105e5673be8448c12cb1474e1b44f8eda7b031a9` |
| `d01-d03\committed\results.json` | `40489ed512662520eee71b38de096f6e0cce1e04fa48432d86292322f4a06b3c` |
| `d01-d03\verification-committed\results.json` | `f3e13c14e4defade6c17be19291a2c3d8aa50cbb07a7924405884d58fa26a3d6` |
| `d01-d03\verification-committed\actual-reader.json` | `21375e62c42bb4012d2794537fba99554b82850d371cfe316e7fddcfe483b669` |
| `d01-d03\verification-committed\prepared-identical.html` | `417d084825b3465a06b55609803c6e5da2ab6d1b41c08f0783dc82810200f342` |

The verification result includes working-byte SHA-256 seals for all five changed
files and ten retained dependencies, the four original inventories and all native
observations. Git product identity separately pins the committed source.

## Preserved native specimen and remaining gates

All **397** prior inventory entries match: first unit 135, workbook 135, separate
presentation 60 and PDF 67. Old QA, source/provenance and artifact evidence were
not rewritten. Original PDF SHA-256 remains
`89e209ed5e2b9f5500b6d827068b7a723e809197a8ea9a7d97a1498fcce9d246`.
Repreparing original HTML/CSS/header data reproduces byte-identical `417d0848...`
HTML without printing. All original page text, boxes and raw origins match.

The four native pages have UserUnit **1**. Complete source-text and page checks
pass for this existing specimen, but all **16** page-3 origin failures remain,
including approximately `[50.999997875, 2271.4199204375]`. Aggregate reader status
is fail. D01/D02 do not explain, repair or waive those coordinates; origins are
not full glyph bounds or proof of clipping. Complete PDF page inspection remains
unverified. No print, browser/server, raster, experimental-layout, alternative
reader, Word/Excel/COM or UI retry occurred.

The missing Markdown converter, original TLS download failure and failed
experimental reader diagnostic are retained, not rerun or replaced. Workbook
cache/layout, Word rendering, shared A14/pipeline serialization and an actual
Visio writer/editor remain separate gates. No source repair closes A15 parents.

Return this exact product/report to SAME reviewer
`31c39265-13e5-4057-9e78-49bf658749a5` for affected source SPEC, then eligible
QUALITY. No extra worker or reviewer was created. P05 structured decision and
corroboration persistence remains explicitly denied; these are build/check
observations, not review records. No alternate writer, SHIP, authenticated GitHub
operation, push, PR or remote merge was attempted. Remote delivery remains solely
with MasterSession.
