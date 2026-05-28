---
name: make-pdf
layer: foundation
description: Convert URL, markdown file, or HTML to PDF via managed Chromium.
color: yellow
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code]
---

# /make-pdf

PDF generation via the same managed Chromium that powers `/browse`. Accepts URLs, local HTML, or markdown (converted to HTML first via a deterministic toolchain). Use for deliverables: rendered design docs, customer-facing one-pagers (after `/rais-customer-voice-check`), printable runbooks.

## When to use

- Operator wants a PDF copy of a `/office-hours` design doc for distribution
- Customer-facing deliverable that's been voice-checked and needs to leave the chat as a static artifact
- Print-friendly version of a runbook or onboarding doc
- Snapshot of a rendered page for archival (combine with `/scrape --diff` for monitoring)

## When NOT to use

- Live preview during authoring — use the IDE's markdown preview
- Multi-page report assembly with TOC + cross-refs — out of scope. Use a dedicated typesetting tool.
- Customer-bearing data not yet voice-checked — STOP. Run `/rais-customer-voice-check` first (Phase 3 skill).

## Inputs

- Required `--input <path-or-url>` — `.md`, `.html`, or `http(s)://...`
- Optional `--out <path>` — output PDF path (default: `<input-stem>.pdf` in cwd)
- Optional `--format <a4|letter|custom>` — paper size (default: a4)
- Optional `--orientation <portrait|landscape>` — default portrait
- Optional `--header-footer <yaml>` — declarative header/footer (page number, title, date)
- Optional `--print-css <path>` — override print stylesheet
- Optional `--no-background` — skip CSS backgrounds (smaller, B&W-friendly)

## Workflow

1. **Resolve input.** URL → fetch via Playwright. Local file → check extension.
2. **Markdown path.** If `.md`: convert to HTML using a deterministic pipeline (pandoc if available, else markdown-it). Apply default print CSS unless overridden.
3. **Compliance gate.** If input is a URL matching Layer 2 prod-host list: BLOCK unless overridden.
4. **Render.** Launch headless Chromium, navigate to file:// or http(s)://, wait for `networkidle`, render PDF with the requested format.
5. **Verify.** PDF written + readable + non-zero bytes. If less than 5KB: warn (likely blank).
6. **Report.** Path, file size, page count.

## Report format

```
Make-PDF: design-doc-v2.md → design-doc-v2.pdf

Input: 14KB markdown, 1 image embedded
Render: 2.3s (chromium headless, A4 portrait)
Output: 142KB PDF, 8 pages
Path: ./design-doc-v2.pdf
```

## Compliance integration

- Layer 2 customer-data gate on the input (markdown content scanned for customer-data patterns; URL hostname checked against prod list).
- Output PDFs land where operator specified — they are NOT auto-uploaded anywhere. Distribution is the operator's responsibility.
- If `voice: trailblazer` content detected in input markdown: surface reminder to run `/rais-customer-voice-check` if not already done.

## Voice tier note

`voice: internal`. The skill itself is internal-voice; the PDF *contents* may be trailblazer or internal — the skill does not transform voice.

## Failure modes

- **Markdown converter not installed (no pandoc, no markdown-it):** report missing toolchain + bail. Do not silently degrade to a worse converter.
- **Page render timeout (60s default):** capture whatever's there, warn about partial render.
- **Output PDF < 5KB:** warn explicitly — almost certainly an empty or broken render.
- **Print CSS reference broken:** fall back to default print stylesheet, log warning.
- **Headless Chromium crash mid-render:** retry once. Second crash: report + bail.

## Examples

**Markdown to PDF:**
```
> /make-pdf --input design-doc.md
✓ 142KB PDF, 8 pages → ./design-doc.pdf
```

**URL to PDF with header/footer:**
```
> /make-pdf --input https://docs.example.com/runbook --header-footer hf.yaml
hf.yaml:
  header: "Runbook — confidential — {{date}}"
  footer: "Page {{page}} of {{total}}"
✓ 312KB PDF, 24 pages → ./runbook.pdf
```

**Letter landscape:**
```
> /make-pdf --input report.html --format letter --orientation landscape
✓ 87KB PDF, 4 pages → ./report.pdf
```

## See also

- `/browse` — page rendering without PDF output
- `/scrape` — extracting structured data instead of producing PDF
- `/rais-customer-voice-check` (Phase 3) — voice gate before customer-facing PDF leaves
- `/design-html` (batch 7) — generate the HTML that feeds this skill
