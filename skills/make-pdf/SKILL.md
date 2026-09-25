---
name: make-pdf
layer: foundation
description: Convert an authorized URL, Markdown file or HTML through actual browser print, preserving source and separating text/page checks from complete visual inspection.
color: yellow
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code]
---

# /make-pdf

PDF generation through the accepted [browser operations](../browse/references/browser-operations.md).
Use the [standalone PDF procedure](../generate-pdf/SKILL.md) for explicit local
HTML, Markdown through an available declared converter, or an authorized URL.
No personal browser/profile, assumed daemon or Office export is required.

## When to use

- Operator wants a PDF copy of a `/office-hours` design doc for distribution
- Customer-facing deliverable that's been voice-checked and needs to leave the chat as a static artifact
- Print-friendly version of a runbook or onboarding doc
- Snapshot of a rendered page for archival (combine with `/scrape --diff` for monitoring)

## When NOT to use

- Live preview during authoring — use the IDE's markdown preview
- Multi-page report assembly with TOC + cross-refs — out of scope. Use a dedicated typesetting tool.
- Customer-bearing data not yet voice-checked — STOP. Run the active pack's compliance gates first (if any are configured).

## Inputs

- Required `--input <path-or-url>` — `.md`, `.html`, or `http(s)://...`
- Optional `--out <path>` — output PDF path (default: `<input-stem>.pdf` in cwd)
- Optional `--format <a4|letter|custom>` — paper size (default: a4)
- Optional `--orientation <portrait|landscape>` — default portrait
- Optional `--header-footer <yaml>` — declarative header/footer (page number, title, date)
- Optional `--print-css <path>` — override print stylesheet
- Optional `--no-background` — skip CSS backgrounds (smaller, B&W-friendly)

## Workflow

1. **Resolve exact source and output.** Retain complete Markdown/HTML, tables,
   code, citations, units and limitations. Refuse unapproved replacement.
2. **Select converter explicitly.** Use available Pandoc/Markdown-it, not a new
   parser/plain-text fallback. Missing conversion blocks Markdown mode. Explicit
   HTML is independent. Only after a real missing-tool failure may an authorized,
   manifest-declared task-local restore occur; no global install or TLS bypass.
3. **Prepare existing print choices.** Preserve paper/orientation/CSS/header-footer/
   background flags. The local helper uses print CSS and CSS page-margin content;
   actual PDF inspection establishes their effect.
4. **Verify policy and navigation.** Use P07's live reference and actual controls,
   then P03 admission on an explicit authorized origin. Serve local HTML/assets
   through an owned loopback server and verify health. The accepted provider
   refuses file:// and checks requests/redirects before following them. Remote
   inputs remain a guarded documented route, not exercised by the synthetic unit
   and not authorization for production data or credential transfer.
5. **Print through the actual provider.** Use the accepted BrowserSession or an
   available permitted native print API. Create a fresh owned context, apply print
   media, call print, record output and verify exact process/profile/server cleanup.
   Missing API, timeout or partial output is failure, not a successful export.
6. **Inspect actual PDF content.** Use an explicit existing reader for searchable
   full text, page-specific material and physical paper dimensions using its
   finite positive UserUnit. Preserve raw boxes/origins and check the nonempty
   MediaBox/CropBox intersection, not an oversized crop alone.
   File size/page count alone is not QA. Complete page rendering remains separate;
   unavailable/denied inspection stays unverified, not replaced with text origins
   or an HTML screenshot.
7. **Report and bind evidence.** Retain exact source/config/tool/artifact identity,
   failures and P05 outcomes. QA is not an independent decision or SHIP clearance.

## Report format

Report exact source/output paths and hashes, converter/provider/reader and observed
versions, actual print/read/cleanup actions, retained source, page observations
and missing visual coverage. Do not fill the report with illustrative passing
durations, page counts or invented renderer results.

## Compliance integration

- Resolve actual profile/data/navigation requirements, not an invented neutral prod-host list or count of passing controls.
- Output PDFs land where operator specified — they are NOT auto-uploaded anywhere. Distribution is the operator's responsibility.
- If customer-facing voice content detected in input markdown: surface reminder to run the active pack's compliance gates if not already done.

## Voice tier note

`voice: internal`. The skill itself is internal-voice; the PDF *contents* may use a customer-facing voice tier or internal — the skill does not transform voice.

## Failure modes

- **Selected converter missing:** retain source and report exact failure. Explicit HTML is not a claimed Markdown conversion.
- **Print timeout/crash/partial output:** preserve failure evidence; no completion claim or blind launch-variant retry.
- **Unreadable/blank/truncated output:** fail the actual reader/content check, not a file-size proxy.
- **Explicit CSS/header-footer missing or malformed:** stop before print rather than silently replacing a requirement.
- **Required page renderer unavailable/denied:** retain useful writer/text observations but leave visual inspection unverified; no workaround to a denied route.

## Examples

**Markdown to PDF:**
```
> /make-pdf --input design-doc.md
[Requires the selected converter; inspect actual output and report missing observations.]
```

**URL to PDF with header/footer:**
```
> /make-pdf --input https://docs.example.com/runbook --header-footer hf.yaml
hf.yaml:
  header: "Runbook — confidential — {{date}}"
  footer: "Page {{page}} of {{total}}"
[Use an authorized guarded origin; no cookie or credential transfer.]
```

**Letter landscape:**
```
> /make-pdf --input report.html --format letter --orientation landscape
[Verify printed dimensions and content; file size is not acceptance.]
```

## See also

- `/browse` — page rendering without PDF output
- `/scrape` — extracting structured data instead of producing PDF
- The active pack's compliance gates — voice gate before customer-facing PDF leaves
- `/design-html` (batch 7) — generate the HTML that feeds this skill
