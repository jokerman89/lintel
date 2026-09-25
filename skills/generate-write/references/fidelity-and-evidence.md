# Content fidelity and artifact evidence

Use the existing brief -> outline.md -> content.md -> speaker-notes.md chain.
This procedure does not introduce a domain envelope, design schema or task ledger.
The shared source-input binding below is separate from native artifact acceptance.

## Existing pipeline input admission

For `--from-pipeline`, use the read-only
[`pipeline_inputs.py`](../../generate/scripts/pipeline_inputs.py) from the trusted
source before a document builder consumes the run. It returns the original complete
Markdown/notes and design object with current-input diagnostics; do not save that
result as a new interchange file or treat it as rendered output.

Prepare an external **input** P05 v2 context selecting the actual canonical
`<run>/brief.md`, `outline.md`, `content.md`, `design-spec.json`, and
`speaker-notes.md` for PPT. Include original claim/evidence sources and every
selected template, logo, print CSS or other configuration input. An identical
file at another path is not the file the builder will read. Hashes retain their
existing actual-byte meanings; neither newline normalization nor a regenerated
summary can replace them.

Use the original map/package/leaves and accepted sources in that context. The
helper calls the accepted P08 `work_context` and compares its P05 binding with
the external context. Recognized package membership must match. For an original
package grouped only by a linked handoff, `--linked-authority` must name that
explicit whole-file acceptance source; its existence is not inferred membership
or approval. The caller still reads the original assignment and verifies actual
prerequisite acceptance. Returned prerequisite checkboxes are **source-status-only**,
not execution authority or independent evidence.

Example argument shape, using actual selected values and the host's path syntax:

```text
python <trusted-source>\skills\generate\scripts\pipeline_inputs.py --repo <target> --from-pipeline <relative-run> --expected <external-input-context.json> --package <original-package> --leaf <original-leaf> --format word --format ppt --profile-home <owned-home> --profile-packs <owned-packs> --profile-pointer <owned-pointer>
```

Repeat `--leaf`, `--format` and `--selected-input <relative-path>` as needed.
`--profile-context-file` retains an explicitly selected P07 context file.
Other data paths are literal target-relative paths, with Windows separators
accepted at the input boundary. Single-valued options cannot repeat. There is no
`--out`, renderer command, installation or review-record writer.

The Python entry is `load_pipeline_inputs(repo, run_dir, *, expected,
profile_config, package_id, leaf_ids, formats, selected_inputs=(),
linked_authority=None, upstream_request=None, upstream_expected=None,
upstream_profile=None)`. It uses P03 rooted reads, P05 strict JSON/current
context, P07 live reference/policy and the shared Markdown source classifier.
It recognizes only the existing section/field markers in eligible source
positions; fenced/quoted/raw/comment examples do not become section definitions.
Anchor candidates also use their original classified spans: inline code, comments,
HTML attributes and escaped markers cannot supply or duplicate an anchor. Content
requires one eligible matching anchor; outline/notes anchors remain optional, but
any eligible anchor must still be unique and match its section.
Complete source, including those literal examples, remains in the returned inputs.
Each read is bounded to 2 MiB with explicit failure, never truncation.

Document-only `version: "1.0"` design files use P11 compatibility validation
plus the existing Word/PPT projection checks. Word retains `sections`,
`section_ref`, `heading_level` and `elements`; PPT retains `layouts`,
`layout_name`, `layout_index` and `elements`. References must name actual source
sections and present Title/Subtitle/Body/Bullets/Data-viz fields. Word's semantic
destinations are `heading`/`body`; PPT's are `title`/`subtitle`/`body` (bullets
and other body material can use `body`). Unknown/duplicate destinations, missing
section coverage and wrong format hooks refuse. Multiple continuation layouts
may reference the same original section. This does not prove that a selected
native template implements a slot, or permit dropping unmapped source detail.

A genuinely mixed web/document design also runs P11's full `load_design` with
the exact sibling `content.md` binding. Legacy unresolved web data is not
silently treated as document-only. Do not add a fake web design to a Word/PPT
run, widen the web renderer registry, or reinterpret its result as document
layout inspection. PDF/XLSX reuse the admitted full source and their existing
format methods without invented `per_format.pdf`/`.xlsx` projections.

Explicit template/config overrides must be selected in the new input context
and passed as `--selected-input`; any template/logo referenced by the selected
document projection must also be selected. Preserve the standalone template/
default decision and revalidate its actual slot mapping. An omitted design
template is not implicit `--use-defaults` or a required-brand waiver.

For a selected upstream domain operation, pass its original request, its own
external final P05 context and its explicit original live profile configuration.
The helper calls P09 `verify_result`, not a copied result flag. At the CLI these
are `--upstream-request`, `--upstream-expected`, `--upstream-profile-home`,
`--upstream-profile-packs`, `--upstream-profile-pointer` and optionally
`--upstream-profile-context-file`. Request/start/result/artifact/evidence bytes
must also be selected downstream. Never graft document QA onto the domain's
original request, create a document domain, or publish a checkpoint just to
generate a standalone document. Upstream `review: not_evaluated` and
`release_clearance: false` stay explicit.

Exit 0 verifies current **inputs only**; exit 2 reports invalid, missing,
unselected, drifted or blocked inputs. The result always has `executed: false`
and `release_clearance: false`. Input admission does not require a finished
artifact's QA: declare its obligations now, create the artifact through an
authorized format operation, then externally prepare its final context and
collect actual QA. Missing mandatory observations remain unverified in P05,
never cleared by input admission. Keep contexts/QA outside their selected files;
the explicit decision/corroboration persistence denial is not changed.

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
