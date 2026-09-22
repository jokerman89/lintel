# P12 standalone PDF writer checkpoint

Date: 2026-09-22. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Status: writer/source candidate frozen; complete A15.4.pdf acceptance remains
BLOCKED.** A real four-page PDF exists with complete searchable source. Reported
text-origin geometry is non-clearing and complete PDF visual inspection remains
unverified. Missing Markdown conversion is not disguised as successful conversion.

## Authority, dependency and exact product

Read complete PDF release card at
`c6462b4639f3a3ce79663d8db5df1392159ec87a`. It authorizes this standalone writer
against accepted A16/P03/P05/P07, not unaccepted A14, shared schema changes,
Office/COM/UI access, PDF-raster workarounds or structured P12 review decisions.

Ancestry-preserving dependency merge:
`51b6f30126f9a53131c69a469ad9b8664dd3b3e5`, parents
`7c130a22250345b2a22d0f06bb183112f7cbf823` and
`3049811386916686edc728ac9a3914970e228173`.
The accepted browser product is `d3b5569c92ce2b0b6f3d2eaf189070f226460513`.
Its inherited accepted P09 data-core ancestry is retained; no A14 WIP was imported.

The sole merge conflict was P11's old versus accepted report. The coordinator
explicitly authorized the exact accepted descendant bytes. Its staged Git
SHA-256 is `cabe3a0e6319178ad7b01fd20301248f106faa1a31ab5e86d3e33976e3daaf10`,
852 LF lines. The old report remains in preserved ancestry. Only the twenty
accepted dependency paths entered the merge; no P12 file was taken over.

Initial PDF product `e5eca8fd2a4d1b742a43eb9905903942b5109499`, sole parent `51b6f301`.
Exactly eight owned paths:

- `skills/generate-pdf/SKILL.md`
- `skills/make-pdf/SKILL.md`
- `skills/generate-pdf/scripts/prepare_html.py`
- `skills/generate-pdf/scripts/print_pdf.mjs`
- `skills/generate-pdf/scripts/check_pdf.py`
- `tests/integration/document-pdf.py`
- `tests/integration/document-pdf.sh`
- `tests/integration/document-pdf.test.mjs`

Final source is `5978def3a3ab0f310ece121d4649fa5798a0842b`, sole parent
`22e8530c7ad9ec8f9b544aedbd66f7a6c4480806` (the initial report-only child of
`e5eca8f`). That small source follow-up changes only HTML head-boundary handling
and its focused tests, as described below. This final report is a separate
report-only child. Exact report commit/hash is supplied in the handoff.
Earlier Word/PPT/F01/workbook/presentation source and reports
remain unchanged. Generated catalog/adapter/wiki/README and master ledgers were
not edited; the two changed source descriptions need coordinator regeneration.

## Implemented and retained behavior

The standalone PDF skill is a concrete writer/inspection method, not an empty
slot. Existing source/output/paper/orientation/header-footer/print-CSS/background
arguments remain. Explicit HTML uses standard-library head insertion plus print
CSS; Markdown requires an actual declared converter and never falls back to a
new parser or flattened plain text. The helpers use P03 owned-path/expected-state
I/O and the existing P07 data-only header/footer parser.

The thin Node print adapter invokes only accepted A16 public operations. The
caller supplies verified work/profile/session identity and authorized origin;
the adapter creates a fresh owned browser, applies print media, prints, then
closes it. It does not create a daemon, reuse a personal profile or add a second
browser engine. Remote input remains a documented guarded path; this unit
exercises only synthetic owned loopback input.

The read-only PDF helper uses explicitly selected existing pypdf, preserving its
observed limits. It compares full source text with whitespace-only normalization,
page-specific content and paper dimensions, and records actual page/crop boxes
and transformed text origins. It does not calculate full glyph bounds or render
pages. Blank, truncated, malformed, encrypted and missing-source output cannot
become a file-size-based success.

## Exact evidence roots and artifacts

`D` means:

```text
C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf
```

| Artifact relative to D | SHA-256 |
|---|---|
| `target\long-technical-brief.pdf` | `89e209ed5e2b9f5500b6d827068b7a723e809197a8ea9a7d97a1498fcce9d246` |
| `target\brief.html` | `4c0288eceff9c21e30ae574688f2f7b1c27b47e50d81f32577b352c738cede69` |
| `target\prepared.html` | `417d084825b3465a06b55609803c6e5da2ab6d1b41c08f0783dc82810200f342` |
| `target\observations\qa-context.json` | `b250b49ba3104de799e4c5a261ee8cc69dd8627226d1f13bc4458efadf83f65f` |
| `target\observations\qa.json` | `cef01408c8b85c1b10863c18b6ebb8af7348f1f2f6b89798f53f16204d5c2855` |
| `logs\artifact-inventory.stdout.log` | `72fc22ba968f331b3488442eed0c68eb3d40de751eb4745be99a109d9c24e6a4` |

`target\technical-source` contains unchanged copies of the earlier full synthetic
brief/content/notes and two local source files. The semantic HTML retains all ten
long reasoning paragraphs, the capacity table, complete claim/evidence ledger,
citations, units and material limitation. It adds explicitly illustrative code
and header/footer content. This authored HTML is a retained, inspected input;
it is **not** claimed as a successful Markdown-it conversion.

## Real converter and reader preflight

Node Markdown-it import: exit 1, module missing. Python Markdown-it import:
exit 1, module missing. Pandoc lookup in the allowlisted PATH: exit 127; no claim
that every machine location was searched. A task-local manifest declared
`markdown-it-py==3.0.0` and `mdurl==0.1.2`. One normal TLS-verified wheel download
failed TLS negotiation on files.pythonhosted.org, exit 2. No wheel was installed,
no transport-search loop or TLS/certificate override followed; wheel directory
and temporary directory are empty at final checks.

Existing pypdf **6.13.2** was explicitly selected and its actual `PdfReader`,
`extract_text` visitor and `Transformation.apply_on` APIs inspected before use.
Runtime: Python **3.11.9**, Node **24.16.0**. No converter, PDF parser or renderer
was reinvented. Actual Python 3.9/Node 22 execution is not claimed.

## Actual browser print and cleanup

The runtime fixture used the accepted browser test's deny-only loopback proxy
discipline without changing the provider. Its forwarding count is zero; it is
not OS-wide network confinement. The server served only `/health` and the owned
`/document`; both actual requests carried no Authorization header.

Health responses were verified before launch. Real provider:
`Chrome/153.0.8010.53`, protocol 1.3, executable
`C:\Program Files\Google\Chrome\Application\chrome.exe`.
The exact instance evidence is:

```text
D\browser\browse-fv3nt1\evidence.json
D\browser\browse-fv3nt1\provider-api.json
D\browser\actual-launches.json
D\logs\server-lifecycle.json
```

Actual public actions were `BrowserSession.start`, `open`, `media`, `read`,
`print` and `close`. Print invoked Page.printToPDF and produced the real PDF.
The inner writer command exited 0. The browser context was disposed, attached
process exited 0, owned profile was removed, and both exact server threads/sockets
stopped. No personal browser, Word/Excel/Copilot UI or PDF-raster action occurred.

The native run used accepted merged source plus explicit working-byte seals for
the new helpers, not an assertion that the pending product was already committed.
Afterward, committed source tests reused the exact output; no rerender is claimed.

## Actual content, page and unresolved geometry observations

pypdf observed **four A4 portrait pages**, each with media box approximately
594.95996 by 841.91998 points. The declared comparison allows a 2-point variation
from requested dimensions and reports the actual values unchanged; wrong-paper
negative tests still fail. No physical-printer accuracy is inferred.
The header and page/total footer appear in extracted text. All complete reasoning
paragraphs, table/ledger values, citations, illustrative code and material
limitation match the source. This is exact text comparison, not word-count proof.

The first reader CLI nevertheless returned **exit 3**: sixteen page-3 table-column
text chunks report the identical transformed origin approximately
`[50.999997875, 2271.4199204375]`, outside its page/crop box. No coordinate was
clamped, discarded or called a pass. These observations do not prove either
actual clipping or a specific reader bug.

One bounded source/API diagnostic used the **same** pypdf public experimental
layout-debug option on the unchanged PDF. It failed internally before producing
coordinate files: `TypeError` in dataclasses/asdict for EncodedStreamObject,
exit 1. The original PDF, first failed reader result and diagnostic error remain.
No new parser, reader, launcher or denied raster provider was tried.

The final helper exposes separate source-text, page and text-origin outcomes:
source/page pass, origins fail, aggregate fail. Complete rendered-page inspection
remains **unverified**. HTML print-media or text extraction is not a substitute
for PDF page images, full glyph bounds, table visual inspection or physical print.
Letter/landscape/custom/background preparation is covered as source behavior;
only this A4 portrait case was actually printed.

## Real non-clearing P05/P07 QA

Fresh PDF P07 context: `p12-standalone-pdf`, generation 1, `_default` 1.0.0,
digest `sha256:8fc2c954f67f5e9975be6abb3907d695172883f87781b116753e876d661e67f6`.
It was verified before print and before evidence consumption. No other target's
pin was transplanted.

The actual approved map/card copies select A15.4.pdf. Synthetic Git ancestor
discovery refuses and the initialized target root matches. P05 QA binds the
source, prepared HTML, CSS/header-footer, expectation oracle, profile and PDF.
Actual CLI QA exits **3**, blocked on:

- `pdf-text-origins`: failed sixteen observed origins; cause unresolved.
- `pdf-complete-visual`: required complete page inspection unverified/denied.

`qa-report.json` remains false. QA observations are not review records:
`record_path` is null, no structured review decision/corroboration/audit review
was written, and no SHIP call occurred. The explicit persistence denial remains
binding. Independent spec/quality stays required.

## Checks, failure history and isolation

| Check | Actual result | Evidence under D\logs |
|---|---|---|
| Preparation/reader unit checks | 14/14, exit 0, no browser | `preparation-reader-tests.*` |
| Actual HTML print pipeline | outer exit 1 because reader failed; inner print exit 0, reader exit 3 | `native-html-print.*`, `live-25-actual-print.*`, `live-26-actual-reader.*` |
| Existing-reader layout diagnostic | exit 1; retained library failure | `reader-layout-diagnostic.*` |
| Final explicit reader | exit 3; source/page pass, origin fail | `reader-explicit-outcomes.*` |
| Full focused tests | 17 Python + 6 Node pass, zero skips/errors, exit 0 | `pdf-full-tests.*` |
| Initial committed product `e5eca8f` | 17 Python + 6 Node pass, zero skips/errors, exit 0 | `committed-product-tests.*` |
| **Final committed source `5978def`** | **18 Python + 6 Node pass, zero skips/errors, exit 0** | `hardened-committed-tests.*` |
| Actual bound QA | exit 3, two mandatory blockers | `bound-qa-observations.*` and `target\observations` |
| Source/ancestry/preservation | eight paths sealed; four local links; 330 earlier artifact hashes unchanged | `final-preservation-seals-eol.*`, `final-seals.json` |
| Staged whitespace and Node syntax | exit 0 | `staged-product-check.*`, `print-adapter-syntax.*` |

Tests explicitly preserve the aggregate geometry failure. Passing tests mean
the fail-closed behavior and supported source/text paths work, not that the PDF
or missing converter/raster gate passed. Blank/partial/missing-source/wrong-paper
negative cases use the existing reader; no fake native output was produced.

Final self-review corrected the directly coupled HTML head-offset routine:
`HTMLParser` counts LF, whereas `str.splitlines()` also counts non-LF separators.
The original routine could therefore place the insertion incorrectly for those
inputs and repeatedly split the whole document for ambiguous closing heads.
The final routine locates the single boundary with one LF-only scan and rejects
the second closing head immediately. Tests cover CRLF, lone CR, vertical tab,
Unicode line separator, comments and duplicate heads. It does not parse Markdown
or change valid source content.

`prepared-source-identity.*` and `hardened-input-identity.*` prove the final helper
still produces the **byte-identical** HTML used for the actual print, SHA-256
`417d084825b3465a06b55609803c6e5da2ab6d1b41c08f0783dc82810200f342`.
No second print or artifact/QA rewrite occurred. The old blocked QA retains its
actual 17+6 test evidence; the final 18+6 committed run is separately recorded,
not retroactively substituted. Exact final follow-up source bytes are retained
under `D\source-candidate-hardened`.

An initial private sealing attempt compared LF reconstruction with the actual
CRLF first-reader seal and failed. The corrected explicit LF/CRLF comparison
recovered the exact pre-execution bytes at SHA-256
`2b384d25cade1eedf25c7ecf1a8640e76e27ac79ccbb33686dcc8083d31c3508`.
Both exits are retained; product source was not normalized to make that check
pass. Final helper source copies/seals and the exact first reader are retained
under `D\source-candidate-final`.

All product/helper calls used recorded cleared per-process HOME/USERPROFILE/
AppData/temp/Lintel/derived roots, explicit source closure, PATH/PATHEXT and
separate source/fixture Git configuration. Logs opened before execution retain
actual exits. Runtime browser cleanup is observed, not inferred from file size.
This is not an OS sandbox or proof of every possible native background effect.

## Next gate

Return this exact writer/source candidate to SAME reviewer
`31c39265-13e5-4057-9e78-49bf658749a5`. Builder self-review is not independent
acceptance. No outstanding owned-code finding is asserted, but the original
format obligations remain non-clearing: Markdown conversion is unverified in
this environment, text-origin geometry unresolved, and complete page visual
inspection unavailable under the current denial.

No release/parent completion, push/PR/main merge, new reviewer, renderer/app
workaround or structured decision/corroboration write follows. Word, workbook,
shared design serialization and a real Visio writer/editor remain separate.
