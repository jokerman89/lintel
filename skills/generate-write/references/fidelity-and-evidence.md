# Content fidelity and artifact evidence

Use the existing brief -> outline.md -> content.md -> speaker-notes.md chain.
This procedure does not introduce a domain envelope, design schema or task ledger.
The shared pipeline/theme binding remains a separately released integration.

## Source before presentation

Retain the exact supplied brief and explicit source files in an owned run directory.
Inline input becomes a retained file before hashing. Keep the existing
`source_brief_hash`, `source_outline_hash` and `source_content_hash` meanings:
SHA-256 of the actual input bytes, not a regenerated summary. Preserve `language`,
`target_formats`, `voice_tier`, `section_ref`, `§N`, `{#sec-N}`, Title, Subtitle,
Body, Bullets and Data-viz. A section may contain multiple paragraphs, tables,
code, citations and subordinate headings. It is not constrained to one slide/page.

Trace the source's claims, evidence, assumptions, reasoning, table cells/units,
citations and material limitations to output locations. Unsupported synthesis is
labelled, never represented as measured evidence. Do not equate limitation counts,
word counts, voice scores or file sizes with honesty or coverage.

Word retains the complete argument in its editable body/tables. PowerPoint has a
separate visible presentation view; put all supporting detail into actual speaker
notes, an appendix or a delivered linked long-form artifact. Put any limitation
that changes a visible claim's meaning on the visible slide too. Retain the
long-form source in all cases. Confirm notes survived serialization and reopening.
Splitting a section records multiple output locations without changing its ID.

## Actual policy, not neutral proxies

Resolve the selected profile through P07's `ProfileConfig`,
`bootstrap_profile_context`, `profile_reference`, `verify_profile_reference` and
`required_policy`, or their accepted shell accessors. Supply explicit trusted source,
target, synthetic/authorized home, pack store, active pointer and stable context.
Do not parse a personal profile or the resolver's cache directly. Carry the full
v1 reference unchanged. Verify the reference again before evidence consumption.
Required load errors or drift block the affected action; a checksum is not policy
enforcement or independent review.

Use P05's [content-bound evidence contract](../../review/references/evidence.md),
not a second interpretation of control fields. Declare `qa_requirements` before
observations for mapped work, including the requested fidelity, editability and
rendered inspections and any actual policy obligations. Preserve their immutable
id, kind, requirement, applicability and policy through QA. A native Office
operation is a generic `check` with its actual tool/action evidence, not a fabricated
browser observation. Add measured contrast or executable tests using P05's typed
controls only when those checks actually occurred.

Select the original brief/sources, full content, notes, explicit template/config,
profile reference and produced artifacts in the snapshot. Keep observations and
context/QA records outside the selected product inputs to avoid self-hashing.
Include an existing selected work map and original leaf IDs when provided.
Standalone unmapped inspection uses P05 `snapshot` then `inspect` with the current
required-policy bridge; it explicitly has `release_clearance: false`. No invented
map or independent reviewer is needed just to prepare and inspect a document.

`qa-report.json` remains the human-facing v1 format report. It references the P05
evidence; it cannot replace the v2 prepared context, decision or QA receipt.
Reprepare affected evidence after any source/artifact edit, including auto-fixes.
Keep required independent review open until an actual separate review is obtained.

## Inspect the right layer

Record the actual tool/provider, instance, action, input/output paths, versions or
hashes, result and limitations for each observation:

| Layer | Evidence it can provide | What it cannot establish |
|---|---|---|
| Source/documentary checks | Required procedures and retained source fields | Any executed native operation |
| ZIP/XML or model extraction | Text, tables, notes, relationships and package structure | Rendered clipping, page breaks or visual fidelity |
| Native reopen and edit/readback | Editability through that particular API/application | Editability in every Office client |
| Actual page/slide rendering | Visible output in the named renderer | Unrendered pages, hidden notes, other renderers or full application equivalence |

Inspect every requested output, not a convenience sample labelled complete.
For slides, inspect visible text wrapping, overflow, overlap, legibility, table
content and any assets; separately inspect the actual notes. For Word, inspect
page breaks, headings, table continuation, references, margins and headers/footers
in a real page renderer. If the available API only returns a Word model, page-layout
inspection is **unverified**, even if document creation and edit/readback succeed.

Missing renderer, zero observations, a broken reference or an unavailable mandatory
control never becomes PASS through a score or absence of reported errors. Record
`unverified` or `error` as appropriate and keep the affected acceptance open.
An optional style preference may remain advisory. Genuine N/A needs source,
version, scope rationale and evidence; missing tooling is not an N/A rationale.

## Ownership and tools

Discover native schemas before calling actions. Prefer native operations or an
already declared, available library. Record a real missing-tool failure before
considering a task-local dependency restore. No automatic/global install, template
scan, macros, credential transfer, external upload or security bypass.

Use only explicit local source/output/template paths. Refuse an existing output
unless its replacement is authorized. A native host API is not an OS sandbox and
does not inherit a shell's synthetic HOME. Describe that boundary honestly.
Neutral mode can use an explicitly chosen blank native document; it has no invented
company palette, logo, voice threshold or required brand template.
