---
name: generate-pdf
layer: foundation
description: Produce a PDF through an available converter and accepted browser print operation, preserving source content and separating text/page evidence from incomplete visual inspection.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# /generate-pdf

Produce a searchable PDF from an explicit source while preserving its full
argument, tables, citations, code, units and material limitations. Standalone
production does not require an unaccepted shared design schema. Retain editable
source even though PDF editing is not promised.

## Inputs and compatibility

- `--brief <path|inline>` or `--input <path|url>` selects the complete source.
  Retain inline input as an owned file. HTML and Markdown paths use the procedure
  below; URL input uses an actually authorized guarded browser route.
- `--from-pipeline <run-dir>` is retained. Consume released content/design/profile/
  work contracts only; do not fabricate design-spec.json or assume another
  format's presence establishes its export capability.
- Preserve `--out`, `--format <a4|letter|custom>`, `--orientation`,
  `--header-footer <yaml>`, `--print-css` and `--no-background` from
  [make-pdf](../make-pdf/SKILL.md).
- `--customer-share` applies the actual profile's customer-facing controls.
  `--accessible` requires actual PDF structure/reading-order/link/accessibility
  evidence, not merely searchable text or a structure-tree flag.

## Select a real writer and reader

Inspect actual converter, browser and PDF-reader APIs before calling them.
Use available declared Pandoc or Markdown-it, including the explicitly selected
`markdown-it-py` API. The format-local helper imports Markdown-it only for Markdown
input; it does not implement a replacement parser. Missing conversion blocks that
input mode, rather than flattening tables or treating plain text as conversion.

In the released environment, Node/Python Markdown-it imports and the allowlisted
Pandoc lookup failed. One manifest-declared task-local converter download failed
TLS negotiation; no installation or verification bypass followed. The independent
**explicit HTML** route remains usable. AI-authored HTML from a brief is retained
and compared with the complete source; it is not an executed Markdown conversion.

Use the accepted [A16 browser provider](../browse/references/browser-operations.md)
for real print, with P03 URL guards and caller-verified P07 work/profile context.
The helper consumes public `Admission`, `BrowserSession.start`, `open`, `media`,
`read`, `print` and `close` operations, not a daemon or private CDP extension.
It never attaches to a personal browser/profile.

The selected reader here is the existing `pypdf` API. No PDF renderer/parser is
implemented by this skill. Another existing reader is an explicit choice needing
its own observations, never a silent fallback after denied inspection.
Word/PPT export remains a possible independently authorized source strategy, not
an automatic fallback. Denied Word/Excel/UI/PDF-raster operations cannot be retried
through COM, another launcher, provider or export tool.

## Local production procedure

1. Read the whole brief and source ledger. Preserve evidence, qualifications,
   tables/units, code and material limitations. Retain the editable source and
   explain transformations; do not shorten it to meet a page-count target.
2. Resolve explicit owned input/output/CSS/header-footer paths. Verify current
   P07 reference/policy and selected work identity. Declare P05 fidelity, print,
   text/page and complete visual requirements before observing them. Neutral
   defaults do not invent brand, disclosure or score gates.
3. Prepare print HTML with `scripts/prepare_html.py`, an explicitly selected
   available converter, or a supplied complete HTML document. The helper preserves
   supplied HTML and inserts print CSS into its actual head; Markdown mode needs
   the declared library. It writes a new owned HTML path using P03 expected-state
   checks. Literal `</head>` text inside title/textarea is not a head boundary;
   real duplicate closing heads still refuse. Source, CSS and prepared HTML
   remain separate artifacts.
4. Start an invocation-owned loopback server serving only the selected document
   and explicitly authorized local assets. Bind 127.0.0.1, observe a real health
   response, and retain the actual origin/server handle. The accepted provider
   checks that exact scheme/host/port and every request/redirect. This is not
   OS-wide network isolation.
5. Invoke `scripts/print_pdf.mjs` with the actual preview URL/origin, absolute
   browser/Python executables, owned output root and unchanged verified
   session/work-map/profile context. It creates a fresh context, enables print/
   reduced-motion media, reads the page, calls actual print and closes the
   context/process/profile in `finally`. Stop the exact server and verify cleanup,
   including failures. Missing APIs or provider errors do not become success.
6. Read the actual PDF with `scripts/check_pdf.py` and an explicit source oracle.
   Check searchable complete content, page-specific material, physical paper
   dimensions, page/crop boxes and transformed text origins against their
   effective intersection. File size is not QA.
7. Obtain complete rendered-page inspection through an actually permitted route:
   clipping, glyphs, table continuation, heading orphans, code, references, images
   and headers/footers. Text/origins or HTML print-media screenshots are not
   images of every PDF page. Missing/denied rendering remains unverified.
8. Bind exact source/config/tool/output observations with existing P05/P07. Retain
   the owned PDF with its partial evidence when a required inspection is unavailable.
   Writing it does not authorize distribution, independent clearance or SHIP.

## Helper interfaces and limits

Use the host's native path spelling and line-continuation syntax:

```text
python <trusted-source>\skills\generate-pdf\scripts\prepare_html.py --root <owned-root> --input brief.html --out prepared.html --format a4 --orientation portrait --header-footer header-footer.yaml --print-css print.css
node <trusted-source>\skills\generate-pdf\scripts\print_pdf.mjs <owned-print-request.json>
python <trusted-source>\skills\generate-pdf\scripts\check_pdf.py --root <owned-root> --input output.pdf --expect pdf-expectations.json
```

Preparation accepts `.md`/`.markdown` only with its available converter.
Header/footer YAML uses the existing data-only P07 parser and only `header`/
`footer` strings with `{{title}}`, `{{date}}`, `{{page}}`, `{{total}}`.
These become CSS page-margin content, not an invented native header/footer API.
Custom paper needs explicit `@page` CSS and observed PDF dimensions.
`--no-background` clears CSS backgrounds, not content images; it does not
pretend to change the accepted provider's fixed print options.

The print request has exactly `url`, `origin`, `python`, `executable`, `outputRoot`,
`name` (new simple `.pdf` filename) and `context` (unchanged verified
`session_id`, `work_map`, `profile_ref`, and source identity when supplied).
The caller resolves policy and permission. The PDF initially lives in the owned
browser run; publish to `--out` only with explicit ownership/expected-state
checks, preserving unverified QA status when applicable. No overwrite, URL
refusal, incomplete cleanup or timeout is converted to successful completion.
The provider's real DOM read bounds cause explicit refusal, never source truncation.

Reader expectations use `required_text` (nonempty complete source segments),
optional `min_pages`, `paper_points` (physical width/height in 1/72-inch points),
and `page_text` (page number to expected text). The existing reader's `user_unit`
must be finite and positive; physical dimensions multiply raw box differences
by that scale. Missing reader support or invalid scale is an error, not a
unit-1 fallback. An omitted PDF UserUnit uses the reader's PDF-defined default.
Results retain raw `media_box`, `crop_box`, `effective_box` and text origins
separately from `physical_media_points` and `physical_effective_points`.

Both boxes must have finite ordered coordinates and a nonempty intersection.
An oversized crop cannot hide origins outside the media box; a narrower crop
still restricts the effective region. Original crop membership remains reported
alongside media/effective membership. No origin is clamped or discarded.
Matching normalizes whitespace only, not numbers, punctuation or facts. These
are **not full glyph bounds or complete visual inspection**. Blank/truncated/
encrypted/malformed, missing-content or wrong-paper output cannot pass.
Exit 0 means only requested reader checks; exit 3 means failed/unverified checks
and exit 2 is an input/reader error. Release clearance is always false.

Keep source-text, page-dimension and text-origin outcomes separate, without
changing the aggregate failure. The four-page synthetic print retained complete
source text and A4 page boxes, but pypdf 6.13.2 reported sixteen table-column text
origins outside page 3. All four pages have UserUnit 1; physical-unit and effective
box checks do not explain or clear those observations. A single documented
experimental-layout diagnostic failed
inside that same reader before producing coordinates. Both observations remain
non-clearing: neither a proven visual clipping defect nor permission to clamp
coordinates, discard table cells or assert successful geometry. Full page visual
inspection remains separately unverified; no denied raster route was retried.

## Roles, status and evidence

Retain WordTechnicalEditor as the read-only document-structure/accuracy method,
with the accepted accessibility/security methods when required by content/policy.
Use actual available delegation only; do not invent a role or independent review.
Apply configured brand references from explicit verified paths, never a personal
template scan. A PDF visual reference is not itself a writer or required template.

- **DONE:** all requested writer/fidelity/reader/visual and policy controls met.
- **DONE_WITH_CONCERNS:** mandatory observations complete, advisory concerns only.
- **BLOCKED:** missing selected converter, writer/reader error, partial content,
  failed required check or unverified required visual inspection.
- **NEEDS_CONTEXT:** missing source/output authority or unresolved applicability.

Record exact input/output hashes, converter/library/browser versions, actual
URL/origin/process/context/cleanup evidence, reader results and the precise visual
gap. QA observations are not structured independent decisions/corroboration;
an explicit denial of those writes stays binding. Shared pipeline, accessible
PDF certification and other formats retain their own actual acceptance.
