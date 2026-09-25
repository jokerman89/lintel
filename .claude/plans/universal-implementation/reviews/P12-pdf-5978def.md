# P12 PDF writer and source review

Date: 2026-09-22. **Independent source SPEC: FAIL. P1=0/P2=3/P3=0.
QUALITY: NOT STARTED.** Three source defects are demonstrated independently of
the original specimen's unresolved text origins and unverified complete visual
inspection. No full PDF/A15.4.pdf, P12 or parent acceptance is granted.

Reviewer project `f42bff7a-1c88-4784-80c9-60c37f683785`, runtime
`31c39265-13e5-4057-9e78-49bf658749a5`; original builder project
`09666ec2-ff03-4517-9169-8793149ea8cd`, runtime
`0a75211f-455c-4318-864f-bc8023ce9142`; coordinator
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. This reviewer implemented no product,
created no child reviewer and wrote no P05 decision/corroboration.

## Immutable selection

| Item | Exact identity |
|---|---|
| Released PDF writer/inspection authority | `c6462b4639f3a3ce79663d8db5df1392159ec87a`, complete P12 card |
| Authorized merge base | `51b6f30126f9a53131c69a469ad9b8664dd3b3e5`, parents `7c130a2` and accepted `3049811` |
| Initial product/report | `e5eca8fd2a4d1b742a43eb9905903942b5109499` -> `22e8530c7ad9ec8f9b544aedbd66f7a6c4480806` |
| Final product/report | `5978def3a3ab0f310ece121d4649fa5798a0842b` -> `9b4a8a1dc58d2f15e02376390169aa6ce30b5d0e` |
| Complete builder report | `reports\P12-pdf.md`: 254 LF lines, 14,471 Git bytes; SHA-256 `8048e21a8ea38863fcaa64218f50f53004efc203c526d4fcf3cf0e2244a70721` |
| Original actual PDF | `89e209ed5e2b9f5500b6d827068b7a723e809197a8ea9a7d97a1498fcce9d246` |

The clean checkout was detached at exact `9b4a8a1`. Previous PPT `5858268`,
workbook `0c1a711` and earlier review refs remain preserved. No current workbook
repair, P09/P11 A14 source or moving builder tip was selected.

All eight product files and their complete base-to-final delta were inspected:
`skills\generate-pdf\SKILL.md`, `skills\make-pdf\SKILL.md`,
`skills\generate-pdf\scripts\prepare_html.py`, `print_pdf.mjs`, `check_pdf.py`,
and `tests\integration\document-pdf.py`, `.sh`, `.test.mjs`.
Sixteen accepted provider/fidelity/fixture dependencies are unchanged from the
authorized merge base. The original map/spec/acceptance, full release card and
complete report were read; source Git/checkout-EOL identity is separately sealed.

## Findings

References name exact final source at `5978def`. These are source/checker
correctness findings, not a diagnosis or waiver of the native page-3 observation.

| ID | Severity | Location | Finding | Confidence |
|---|---|---|---|---|
| D01 | P2 | `skills\generate-pdf\scripts\check_pdf.py:49-51,72-73` | Paper comparison ignores PDF user-unit scale and accepts invalid scale | 10/10 |
| D02 | P2 | `skills\generate-pdf\scripts\check_pdf.py:49-51,64-67` | An oversized CropBox hides origins outside the MediaBox | 9/10 |
| D03 | P2 | `skills\generate-pdf\scripts\prepare_html.py:32-54,115-117` | Literal head text in RCDATA is mistaken for a real head boundary | 9/10 |

### D01 - Compare physical dimensions, not unscaled user coordinates

The selected pypdf 6.13.2 API exposes `PageObject.user_unit`: a positive multiplier
of 1/72 inch. The checker compares raw MediaBox differences directly with
`paper_points` and never reads that multiplier.

On a valid-version **PDF 1.7 synthetic copy** of page 1 with `/UserUnit 2`,
the actual physical dimensions are 1189.91992 by 1683.83996 points, while the raw
MediaBox remains 594.95996 by 841.91998. The checker nevertheless reports all
statuses PASS and CLI **exit 0** against the original A4-sized oracle. Supplying
the correct doubled dimensions instead yields a false paper failure, **exit 3**.
Explicit `/UserUnit 0` and `-1` also produce PASS/exit 0.

**Fix:** validate a finite positive user-unit value and account for it when
comparing/reporting physical paper dimensions, keeping raw coordinates distinct.
If non-unit scale is intentionally unsupported, report it unverified rather than
silently passing. Invalid scale must not clear. Add paired unit-1/unit-2 and
invalid-scale cases through the actual reader and CLI. No renderer is needed.

### D02 - Respect the effective page boundary

A second synthetic page retains the original MediaBox but translates content
upward by 1000 user units. With the ordinary CropBox it correctly fails. Enlarging
only CropBox height to 1841.91998 makes the same checker report source, page and
origins **PASS / exit 0**, even though all **41 observed text origins are outside
the 841.91998-high MediaBox**. Checking the raw CropBox alone does not bound
content to the page: its effective displayed region cannot extend beyond MediaBox.

**Fix:** validate the relationship between the boxes and check the effective
MediaBox/CropBox intersection, or explicitly refuse unsupported inconsistent
boxes. Reject empty/invalid effective regions. Preserve raw reader observations;
do not clamp or discard text, and do not turn this limited origin check into
full-glyph or visual acceptance. Add ordinary, narrowed and oversized-crop pairs.

### D03 - Recognize real head closures in their HTML text context

The callback treats every reported `</head>` token as a document boundary.
Standard-library `HTMLParser` does not by itself give `title` and `textarea`
the HTML RCDATA handling needed by this algorithm.

Complete HTML containing `<title>Source </head> notation</title>` or
`<textarea>Example </head> token</textarea>` has only one real document-head
closure, yet preparation reports "multiple closing heads" and the CLI exits
**2**. In those elements the token is literal text, not a head end tag.
The paired `&lt;/head&gt;` versions prepare successfully, as do script/comment
controls. Thus a valid supplied document is rejected before printing.

**Fix:** make boundary recognition respect these text contexts using the existing
parser/explicit context tracking. Preserve the complete source and retain the
real duplicate-head refusal. Extend the final LF-offset/comment regression with
raw/escaped RCDATA pairs; do not introduce a Markdown parser or another browser.

## Native specimen and preserved behavior

The declared writer retains input/output, paper/orientation, header/footer,
print-CSS and background arguments, `--from-pipeline`, customer-share and
accessible-output boundaries. `prepare_html` uses P03 expected-state writes and
the existing P07 data-only header parser. `print_pdf` imports the accepted A16
public provider and closes the owned session in `finally`; it does not introduce
another browser engine or silently publish to a different output.

The supplied actual writer evidence is distinct from this reviewer's file-only
checks. Builder print exits **0**, and its recorded context/process/profile/server
cleanup is complete. The outer pipeline exits **1** because its reader exits
**3**, not because print succeeded without a usable file.

All four actual A4 pages and the full required reasoning, table/ledger values,
code, units, citations, material limitation and header/footer text are retained.
The final preparer reproduces **exactly the HTML used for that print**:
`417d084825b3465a06b55609803c6e5da2ab6d1b41c08f0783dc82810200f342`.
No rerender or Markdown-conversion success is inferred. The converter is actually
missing; the previous normal TLS download failure and no-install boundary stand.

The same existing reader reproduces all **16** page-3 out-of-crop origins at
approximately `[50.999997875, 2271.4199204375]`. A bounded arithmetic comparison
confirms the helper's nested `Transformation.apply_on` matches the public API's
text-matrix then current-matrix composition. That verifies the calculation used,
**not the correctness of pypdf's supplied coordinates**. It does not establish
visual clipping or resolve the earlier failed experimental-layout diagnostic.
That diagnostic was not repeated. All four original pages have UserUnit 1.
D01/D02 use separate synthetic metadata cases; they do not explain or erase this
native result.

| Control / original acceptance | Result |
|---|---|
| Writer/source-method preservation | **PASS for retained behavior**, with D03's valid-HTML preparation defect outstanding. |
| Reader correctness | **FAIL**, D01/D02. No score can clear incorrect physical-page/origin results. |
| Frozen source tests | **PASS**, 18 Python + 6 Node, zero failures/errors/skips; coverage misses D01-D03. |
| Actual print | **PASS as reviewed builder evidence**, with attributable output and cleanup; not re-executed here. |
| Actual source-text/page checks | **PASS for this unit-scale A4 specimen**, not universal PDF-format support. |
| Actual text-origin control | **FAIL**, 16 observations remain unresolved and non-clearing. |
| Complete PDF visual inspection | **unverified**, unavailable/denied; no raster or alternative reader route authorized. |
| Markdown conversion | **unverified in this environment**, not claimed by the explicit-HTML route. |
| Source SPEC / QUALITY | **FAIL / NOT STARTED**; source defects and original format gates remain separate. |
| A15.4.pdf / P12 / parents | **unverified/open**; no full-format or initiative completion. |

## Verification and evidence

`D` is the read-only builder root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
`Q` is the reviewer root:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

| Command | Actual result |
|---|---|
| `pdf-source-pin.ps1` | Exit 0: eight product paths, sixteen unchanged dependencies, five original authority sources and exact report/Git/EOL identity. |
| `review-run.ps1 -Label p-api03 -Mode pdf-preflight` | Exit 0: existing pypdf 6.13.2 signatures and public user-unit/transformation/PDF-version APIs inspected; all four native pages have UserUnit 1. |
| `review-run.ps1 -Label p-t01 -Mode pdf-tests` | Exit 0: **18 Python + 6 Node pass**. Actual reader-copy CLI exits 3; final HTML identity matches. Node subprocess/network guard records zero attempts. |
| `review-run.ps1 -Label p-c03 -Mode pdf-cases` | Exit **1**: 29 file-only cases, 22 expected outcomes and **7 discrepancies** across D01-D03. Nine additional owned-publication/paired-HTML CLI observations retained. |
| `review-run.ps1 -Label p-e01 -Mode pdf-evidence` | Exit 0: all **67 PDF** and **330 earlier** inventory files unchanged, actual controls CLI **exit 3**, work/evidence identity matches; four local links, Bash syntax and 3.9 grammar checked. |

The seven discrepancies are four false reader PASS/exit-0 results, one false
paper failure/exit-3 and two valid-HTML refusals/exit-2. Positive controls cover
ordinary unit-scale pages, whitespace-only matching, rotation nonclearance,
source/page mismatch, encryption/truncation refusal, narrowed crop, CSS and
header data, comments and non-LF separators. Existing-output, root-escape,
renamed-PDF and missing-CSS publication attempts refuse; owned inputs are unchanged.

All synthetic PDF variants were written with the **existing pypdf** from an
owned one-page copy, not generated by a new engine, printed or rasterized.
The first private variants inherited PDF 1.4; they are retained as diagnostic
history. After inspecting the public `pdf_header` setter, final `p-c03` explicitly
uses PDF 1.7 so the UserUnit support finding is based on the correct format version.
The same seven discrepancies reproduce. No old result or source was rewritten.

| Reusable evidence | SHA-256 |
|---|---|
| `Q\pdf-source-pin\source-pin.json` | `9b4593d4fee7e914294090b24956599384b02275f02f82e4dc3997829e77b0a9` |
| `Q\p-api03\reader-api.json` | `897a77a8e3865326843364dd2353a117af6118d484aaca071e1f536425cd1142` |
| `Q\p-t01\results.json` | `8f8bfb1c535e863ea5172e94004371638cd71400039feab2df2178be487c840f` |
| `Q\p-c03\cases.json` | `a31c385fa9de9cac543e73c7b2d63560d120cc7ddfa2b267c1e7f140b736b4ff` |
| `Q\p-c03\actual-origin-composition.json` | `85d1481470c3e40e14ece45d7352e01c8672a7a2c03e72cd73eee201592d8005` |
| `Q\p-e01\evidence.json` | `e0e6b6fc0f0c69ef178c5239ecca77c18c8a6d033fc26ca81704f0713072eb1e` |
| `Q\pdf-final-repro-manifest.json` | `79d424af0e177f5f890256d4d483df7f88a6db1cf7c201965e2950b42b29eed2` |

Exact synthetic inputs/expectations are in `Q\p-c03\r`; preopened logs, actual
CLI exits, observed API metadata and per-run source/env seals are retained.
Every product import/call used inspected synthetic HOME/USERPROFILE/AppData/temp/
Lintel/derived paths/PATHEXT and Git ceilings. Source Git/EOL checks were separate.
Node ran only pure request tests, with process/network functions guarded before
product imports; it did not construct Admission or BrowserSession. Python used
the existing pypdf reader, not an alternate reader or the experimental layout mode.

Python 3.11.9 and Node 24.16.0 were observed; syntax/grammar are not minimum-runtime
execution claims. No browser/server/native UI, Word/Excel/COM, PDF rasterizer,
network, package install, private-home scan, policy change, full suite or product
repair occurred. Old QA retains its original 17+6 test observation; the final
18+6 run is separate evidence, not retroactively substituted.

## Exact next gate

The original owner repairs D01-D03 under a new bounded release/candidate and
returns to this reviewer. Preserve the native PDF, raw 16-origin failure,
converter/diagnostic failures and all original visual obligations. Source fixes
must not clamp origins or turn text/writer success into full visual acceptance.

The original P05 context remains A15.4.pdf, `record_path:null`, with unchanged
mandatory obligations. Actual and independently evaluated QA exits 3 for
`pdf-text-origins` and `pdf-complete-visual`. No structured decision,
corroboration, publication or alternative persistence route was attempted.
This completes the bounded writer/source review only; actual format acceptance
and all other P12 work remain separate.
