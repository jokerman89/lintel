---
name: generate
layer: foundation
description: Use to produce a finished document or deliverable from a brief — drives outline, writing, design, and QA through to a built artifact in a chosen format such as slides, Word, web, or PDF. Reach for it when the ask is to generate a polished document rather than write code.
color: orange
tools: Read, Write, Bash, Glob
voice: mixed
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
  - cli: copilot
    level: full
license_note: produces customer-bound output if --customer-share flag set
---

You are the `generate` orchestrator skill — multi-format document generation entrypoint.

## What this skill does

Coordinates shared source preparation and the available format-specific operations.
Word, PowerPoint and web consume existing design projections; PDF and XLSX keep
their own production procedures. Visio remains a template slot without a shipped
writer. Configured branding requires actual selected assets and evidence.

Reads operator brief → outline → full written content → design → format-specific
builders → actual artifact QA. Retain all original sources and long-form content.
Use an explicitly owned run directory, not an implicit personal draft/profile scan.

The standalone `--brief` Word/PPT routes preserve content and use actual available
native/library operations. The existing pipeline now has a read-only
[input admission procedure](../generate-write/references/fidelity-and-evidence.md#existing-pipeline-input-admission);
that verifies original source/work/profile and document projections, not native
artifact acceptance. The retired document-format acceptance in ADR-0033 is not a
live gate. Use the current required P05 inspections for the actual format; never
fabricate a design-spec or report an unrun format ready.

Reuse complete source where supported, not a universal write-once/render-anywhere
promise. Each output still needs its own composition, source-retention and
available inspection evidence.

## When to use

- Customer-engagement deliverable that needs multiple formats from the same content (deck + handout + summary email)
- Internal report that should ship as both web (readable) and PDF (archivable)
- Workshop prep that needs deck (presenter) + Word handout (participants) + speaker notes (operator)
- Any time the same content surface is needed across more than one format

## When NOT to use

- Single-format quick draft → invoke format-specific skill directly (`/li:generate-ppt`, `/li:generate-web`, `/li:generate-word`) with `--brief` — bypasses orchestrator overhead
- Re-rendering an existing run with new template → invoke the format-builder solo with `--from-pipeline <run-dir>`
- Verification of an existing artifact → invoke `/li:generate-qa <artifact>` solo
- Outline-only ideation → invoke `/li:generate-outline` solo
- Documentation from source code → `/li:generate-docs`; its complete Markdown
  output can be the explicit brief for this pipeline, not fabricated pipeline output

## Workflow

### Step 1 — Parse invocation

```bash
brief="${1:-}"                          # required: brief text or path to brief.md
formats="${2:-ppt}"                     # comma-separated: ppt,web,word,pdf,xlsx,visio
customer_share="${CUSTOMER_SHARE:-}"    # set by --customer-share flag
run_id="$(date +%Y%m%d-%H%M%S)-${RANDOM}"
run_dir="${GENERATE_RUN_DIR:?select an explicit owned output directory}"
mkdir -p "${run_dir}"
```

This is an illustrative shell binding, not an installed argument parser. Preserve
the familiar skill flags and select the run path before execution. If the brief
is empty, exit `NEEDS_CONTEXT`; do not scan personal recent-run directories.
Verify ownership and planned destinations before creating anything. An existing
directory is not replacement authority; a continued run follows the explicit
[continuation procedure](#continue-an-owned-run), not this new-run recipe.

### Step 2 — Preflight gates

Per format in `--formats`:
- Discover actual writer, reopen/edit and renderer operations for the requested format
- Resolve only explicit or verified-profile template paths; `--use-defaults` cannot waive required brand policy
- Apply actual configured freshness/voice/compliance requirements and their applicability
- Declare required fidelity/format inspections using P05/P07 before observations; mandatory failure/error/unverified blocks the affected action

Keep actual production and inspection boundaries separate:

| Format | Current operation and remaining limits |
|---|---|
| PPTX | Available native slide operations or declared `pptxgenjs`; actual saved notes/source checks, API reopen/edit and slide rendering are separate observations |
| DOCX | Available native document operations or declared library; model/package checks do not establish pagination or native page rendering |
| Web | Existing single-file/Next.js procedures and actual authorized browser observations; no browser execution inferred from source |
| PDF | Existing converter or prepared-HTML/browser-print writer; Lintel has no PDF reader, so produced text, pages and visual rendering remain unverified without separate authorized evidence |
| XLSX | Existing native/library workbook writer, real recalculation and shipped formula/cache checker; live formula results do not prove persisted caches or application reopen behavior |
| Visio | Template slot; actual writer/editor and connector/label/rendered-editability observations are unavailable unless an authorized host supplies them |

A missing required operation keeps that requested outcome open. Continue only
independent supported preparation; a format label or confirmation cannot supply
the absent writer, reader or measurement.

### Step 3 — Generate outline (shared)

Invoke `generate-outline` sub-skill:
- Input: `--brief "${brief}" --target-formats "${formats}" --audience "${audience}" --arc "${arc}" --out "${run_dir}/outline.md"`
- Output: `${run_dir}/outline.md`

Surface outline to operator via short summary (slide_count, sections, key messages). Offer to skip-ahead if outline is approved or rewind to S1 if not.

### Step 4 — Generate written content (shared)

Invoke `generate-write` sub-skill:
- Input: `--outline ${run_dir}/outline.md --out-dir ${run_dir}`
- Output: `${run_dir}/content.md` (plus `${run_dir}/speaker-notes.md` if `ppt` in formats)
- Voice tier: the active pack's voice tier (default: `internal`); upgraded per pack if `--customer-share`
- Retain multi-paragraph reasoning, tables, citations and material limitations; slide brevity is a separate presentation view with full detail in actual notes/appendix or delivered linked long-form content

### Step 5 — Generate design spec (shared)

Invoke `generate-design` sub-skill:
- Input: `--content ${run_dir}/content.md --target-formats "${projection_formats}" --palette "${palette}" --out ${run_dir}/design-spec.json`
- Output: `${run_dir}/design-spec.json` (per-format layout-mappings)

Keep the existing v1.0 document projections; do not shrink canonical content to
fit a slot or invent a second design schema. Document-only inputs use P11
compatibility plus format-owned reference checks under the external P05/P07/P08
input context. Genuine mixed web/document input also needs full P11 `load_design`.
An unresolved web binding cannot become a document-only success.
Select `projection_formats` from the requested Word/PPT/web consumers; PDF/XLSX
do not acquire invented layout projections. If only a standalone PDF/workbook is
needed, pass the full brief/source to that format's existing method instead of
fabricating a design file or claiming shared stages ran.

### Step 6 — Compliance gate (orchestrator-level if --customer-share)

If `--customer-share`:
- Run the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) on `${run_dir}/content.md`
- Evaluate actual mandatory/advisory controls and vocabulary tiers using P05
- Proceed only when applicable mandatory controls have observed satisfactory outcomes; missing policy or evidence never becomes neutral success

This is the orchestrator-level gate. Format-builders still apply their own brand/honest-limitations/provenance gates per format (see Anti-patterns for execution-order rule).

### Step 7 — Per-format build (chained)

For each format in `--formats`:
- Before a Word/PPT/PDF/XLSX consumer reads the run, call
  `scripts/pipeline_inputs.py` with the selected format, explicit original
  package/leaves, external **input** context and live profile configuration.
  Select canonical sibling files, source evidence and every template/config
  override. Preserve complete returned source and existing design projections;
  the helper neither invokes a builder nor requires a future artifact's QA.
  For a mixed web design whose `design-spec.json` carries a `pattern_context`,
  also pass `--pattern-lock <run lock>` and `--pattern-context <current context>`,
  and select both files plus `.claude/patterns`. A document-only design refuses
  these flags; each stage verifies its attachment instead.
- Read original prerequisites and actual acceptance evidence; source checkboxes
  from the work reader cannot authorize execution. Selected upstream P09 data
  retains its own request/context/profile, not the document's new QA inventory.
- Invoke the actual format operation with an explicit owned destination:
  - `ppt` → `/li:generate-ppt --from-pipeline ${run_dir} --template ${template} --out ${run_dir}/ppt/deck.pptx`
  - `web` → `/li:generate-web --from-pipeline ${run_dir} --variant single-file --out ${run_dir}/web/index.html`
  - `word` → `/li:generate-word --from-pipeline ${run_dir} --target ${target} --out ${run_dir}/word/document.docx`
  - `pdf` / `xlsx` → pass admitted full source to their existing standalone
    production procedures; retain converter/print or formula/cache/reopen gates,
    without inventing document layout projections
  - `visio` → actual writer/editor seam still required; no image-as-VSDX substitution
- Each format-builder writes its output to `${run_dir}/<format>/<artifact>.<ext>`

The displayed paths are selected-output examples, not overwrite permission.
Template/default choices retain each format's existing precedence and policy.

Builders retain brand, honest-limitations and provenance categories with actual
applicability, plus source-retention, editable-reopen and rendered inspection.
Upstream controls are reusable only while their bound source/profile remains
unchanged; they cannot cover a later lossy format conversion.

### Step 8 — Aggregate QA

Invoke `generate-qa` sub-skill on all produced artifacts:
- Input: `--artifacts <explicit produced artifact paths> --source ${run_dir}/content.md --out ${run_dir}/qa-report.json`
- Mode: `--auto-fix none`; aggregate inspection does not authorize artifact edits
- Output: `${run_dir}/qa-report.json`

If an inspected artifact needs repair, retain its report and original bytes.
An explicitly authorized repair uses `generate-qa --fixed-out <new-owned-path>`
for that artifact, then repeats its affected checks and the aggregate QA on the
selected final deliverables. A default or suggested fix is not repair consent.

Compare each saved artifact with the full source and inspect its actual available
render/reopen layer. Auto-fixes must preserve meaning and invalidate affected
pre-edit evidence. A missing renderer or dropped qualification cannot be averaged
away by a score or an otherwise empty issue list.
Prepare the final external P05 context after changed artifacts exist. Input
admission is not final QA, and `qa-report.json` remains the existing presentation
report rather than a replacement evidence envelope.

### Step 9 — Output and continuation evidence

Print exact run/source/artifact/evidence paths and unfinished format gates.
Report stages/operations actually performed, source hashes, selected profile,
requested versus produced formats, QA outcomes and the next supported operation.
Keep the note in an explicitly owned report path. This recipe supplies no
completion-event writer or resumable scheduler; do not claim an event was emitted
or update a shared cycle ledger merely because a document was produced.

## Continue an owned run

Continuation is an explicit selection of current inputs and supported operations,
not a new orchestrator flag or a cached success token.

1. Select the exact authorized run/source/output paths and original work/profile.
   Read any prior report as history. Inventory actual files, full content, notes,
   hashes, selected template/config and unfinished obligations. No recent-run
   search, implicit output replacement or copying another run's acceptance.
2. Verify the unchanged current P07 reference and original prerequisite evidence.
   Re-read source bytes; if a brief/outline/content changed, regenerate its
   dependent stages and their hash bindings from the complete source. Do not
   patch a hash to legitimize stale content or discard material to fit a format.
3. Choose only the needed supported stage:

   | Available current input | Existing operation |
   |---|---|
   | Retained brief, outline absent or stale | `generate-outline --brief <actual-brief> --target-formats <selected-formats> --out <owned-outline>` |
   | Current outline and full referenced sources | `generate-write --outline <actual-outline> --brief <actual-brief> --out-dir <owned-run>` |
   | Current content, design absent/stale for Word/PPT/web | `generate-design --content <actual-content> --target-formats <supported-projection-formats> --out <owned-design-spec>` |
   | Current complete pipeline input | Re-run `pipeline_inputs.py` input admission for Word/PPT (or admitted source reuse by PDF/XLSX); web uses `load_design`. Then call the actual format method from Step 7 |
   | Existing standalone brief/source for PDF/XLSX | Use that format's standalone converter/print or workbook/recalculation procedure, without claiming shared projections |
   | Saved artifacts needing inspection | `generate-qa --artifacts <actual-files> --source <actual-source> --auto-fix none --out <owned-report>` |

   These are skill input shapes; optional selections such as template, audience,
   palette and voice must match the actual source/profile. For every write choose
   a new owned output or retain explicit replacement authority and its preimage.
4. Before consuming a complete pipeline, prepare the external current input
   context selecting the exact canonical sibling files and actual overrides.
   Re-run admission, not a stored result. Missing sibling content/design/notes
   blocks that consumer; standalone Word/PPT `--brief` remains a distinct route.
5. Any source/design/artifact change invalidates affected final QA/review. Refresh
   the final P05 context and actual required checks. Report missing requested
   formats even when the inspected subset succeeds. Repairs still require
   explicit `--fixed-out` and leave original artifacts unchanged.

No automatic cleanup, new renderer or inferred completion. Preserve partial and
failed outputs/evidence; deletion requires separate explicit authority.

## Voice tier behavior

- **Default `internal`** — no invented customer voice rule; any applicable configured internal requirements still apply.
- **`--customer-share` flag** — content will be delivered to customer. The active pack's compliance gates apply (`resolve_pack_field compliance.hooks`; none by default). Voice tier upgraded per pack. Vocabulary-blocklist enforced if the pack defines one.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
When the runtime reports patterns, the pipeline resolves once for the brief's context before
OUTLINE, writes the lock in the repository under
`.claude/runtime/patterns/<run-id>/patterns.lock.json` (the run directory itself when the run
lives there; document outputs may be elsewhere) and attaches it to `design-spec.json` as
`pattern_context` (`$LINTEL_SOURCE_ROOT/lib/pattern_visual.py` `design_attachment`, `lock_ref`
relative to that pattern-state directory). Every stage verifies that attachment
(`verify_design_attachment` with the same pattern-state directory) before using clauses; a
missing, stale or mismatched attachment is `unavailable`, never a pass. Mandatory clauses reach
the format-builders and QA unchanged. When the runtime reports no patterns, nothing is attached
or asked; `unavailable` or `invalid` is never treated as no patterns.

## Status protocol

- **DONE** — all formats produced + qa_pass=true + run_dir printed
- **DONE_WITH_CONCERNS** — requested required checks complete, only advisory concerns remain
- **BLOCKED** — required format/control unavailable, failed or unverified; retain and report independent completed preparation/artifacts
- **NEEDS_CONTEXT** — brief missing or unparseable

## Pause-points

- Brief is ambiguous: surface back to operator + offer 3 interpretations
- Pack compliance gate fails + `--customer-share`: hard-block, surface the failing gate
- Unavailable format operation: identify the precise activation requirement; do not substitute a different output format silently

## Integration

**Reads:**
- Operator brief (path or inline)
- Explicit templates and current verified P07 profile context per requested format
- Prior explicitly selected run report, as history only

**Writes:**
- Selected owned run directory (original brief, outline.md, full content.md, speaker-notes.md if PPT, actual design-spec.json where released, per-format artifacts, qa-report.json and bound evidence)
- Explicit owned run report with actual checks and continuation inputs

**Triggers (sub-skills):**
- `/li:generate-outline`, `/li:generate-write`, `/li:generate-design`, `/li:generate-qa` (shared pipeline)
- `/li:generate-ppt`, `/li:generate-web`, `/li:generate-word` (canonical format-builders)
- `/li:generate-pdf`, `/li:generate-xlsx` (existing standalone production procedures with the limits above)
- `/li:generate-visio` (template slot; no shipped writer)

**Compliance gates:**
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) at orchestrator level if `--customer-share`

## Anti-patterns

- **Confuse methods with customer content** — reusable format procedures belong in skills; real customer data does not. Planned adapters need working procedures and evidence, not an indefinite empty-slot promise.
- **Bypass the compliance gate when `--customer-share` is set** — if the active pack defines gates, they are non-negotiable. A failing gate blocks.
- **Consume incomplete pipeline inputs** — the selected consumer's canonical source/design/notes are dependencies. Standalone PDF/XLSX do not need invented projections.
- **Re-render with different `--palette` without rebuilding design-spec** — palette is encoded in design-spec.json. Pull from cache only if palette match; rebuild design otherwise.
- **Skip qa-report on customer-share runs** — the compliance gate is necessary but not sufficient. Brand/honest-limitations/provenance gates run per format and aggregate to qa-report.

## Gate execution order (after compliance-lift)

Per design doc's MAJOR concern #2 + #8: explicit order across orchestrator + format-builder layers.

```
Step 6 (orchestrator):  pack compliance gates + vocab-blocklist ─── applied to content.md
                            │
                            └─ PASS ──> Step 7 (per format-builder):
                                          brand-template-match
                                            │
                                            └─ honest-limitations check (transparency-note variant)
                                                  │
                                                  └─ provenance-stamp (run_id + brief-hash in metadata)
                                                        │
                                                        └─ format-output to ${run_dir}/<format>/
```

Compliance gate is single-source (orchestrator only). Brand/honest/provenance gates remain per-format (format-builder owns).
This diagram shows category order, not a substitute for source-retention,
editable-reopen and rendered-inspection evidence at Step 8.

## Vocabulary-blocklist ↔ customer-share-gate interaction (resolves PR #7 concern #4)

The vocabulary-blocklist enforcement chain is:

1. **Operator passes `--customer-share` to /li:generate orchestrator**
2. **Orchestrator propagates voice-tier:** sets the active pack's voice tier (`resolve_pack_field voice.default_tier`) on generate-write (Step 4)
3. **generate-write applies configured vocabulary tiers** without erasing factual qualifications, quotations or citations
4. **The orchestrator evaluates applicable configured controls** (Step 6); generate-qa later verifies the actual converted artifact and its required inspections
5. **Separate voice and compliance controls:** resolve `voice.gates_active` for
   voice and the applicable compliance declarations separately. Hand their
   actual outcomes and the original customer-facing applicability to
   `/li:compliance-gate` through its existing declared-controls procedure
   (`li-review-evidence.py controls --input <controls-file>`), not an
   undocumented scope flag. Required missing observations remain blocked.

The customer-share flag selects customer-facing applicability; it does not disable
mandatory internal policy or source fidelity when absent. Neutral style advice
does not become a hard vocabulary rule.

Use the flag with the verified current profile, not instead of it.

## Failure recovery

- **Sub-skill fails mid-chain**: preserve the exact error and partial outputs in the
  owned run report. Follow [Continue an owned run](#continue-an-owned-run) with
  current source/profile and an actually supported stage, not a guessed flag.
- **One format fails**: preserve successful independent outputs and report the blocked requested format; do not claim the whole run complete.
- **Pack compliance gate fails on `--customer-share`**: block, surface the failing gate, exit BLOCKED.
- **Adapter/renderer unavailable**: report the exact remaining gate; alternatives require an explicit format choice and their own inspection.

## Recommended next steps after invocation

- For a Word/PPT/web follow-up after current binding is verified, use the format
  builder's existing `--from-pipeline` path and explicit owned output.
- For a voice-tier change, use the current `generate-write --voice-tier` input
  when rewriting is needed, regenerate affected dependent stages, and re-run
  applicable source/format/share controls. Prior internal QA is not customer-share clearance.
- For final checking, use read-only `/li:verify` on the actual selected scope and
  recorded checks; `qa-report.json` alone is not an executed format comparison.
- External distribution is separate authorization after actual required controls
  and review, not a pipe that uploads an artifact.
