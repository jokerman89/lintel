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
license_note: produces customer-bound output if --customer-share flag set
---

You are the `generate` orchestrator skill — multi-format document generation entrypoint.

## What this skill does

Orchestrates the v3.5 shared content pipeline + per-format builders to produce branded deliverables (PPTX deck, DOCX doc, HTML site, PDF, XLSX, Visio) from a single content brief.

Reads operator brief → outline → full written content → design → format-specific
builders → actual artifact QA. Retain all original sources and long-form content.
Use an explicitly owned run directory, not an implicit personal draft/profile scan.

The standalone `--brief` Word/PPT routes preserve content and use actual available
native/library operations. The existing pipeline now has a read-only
[input admission procedure](../generate-write/references/fidelity-and-evidence.md#existing-pipeline-input-admission);
that verifies original source/work/profile and document projections, not native
artifact acceptance. A15.3.shared and the full format gates still need their
joined outcomes; never fabricate a design-spec or report an unrun format ready.

Designed for "write the script once, deliver to N formats without duplicate work." Per v3.5 doc-gen plan, replaces the prior pattern where operator invoked each `/li:generate-X` separately with different briefs.

## When to use

- Customer-engagement deliverable that needs multiple formats from the same content (deck + handout + summary email)
- Internal report that should ship as both web (readable) and PDF (archivable)
- Workshop prep that needs deck (presenter) + Word handout (participants) + speaker notes (operator)
- Any time the same content surface is needed across more than one format

## When NOT to use

- Single-format quick draft → invoke format-specific skill directly (`/li:generate-ppt`, `/li:generate-web`, `/li:generate-word`) with `--brief` — bypasses orchestrator overhead
- Re-rendering an existing run with new template → invoke the format-builder solo with `--from-pipeline <run-dir>`
- QA-only on existing artifact → invoke `/li:generate-qa <artifact>` solo
- Outline-only ideation → invoke `/li:generate-outline` solo

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

### Step 2 — Preflight gates

Per format in `--formats`:
- Discover actual writer, reopen/edit and renderer operations for the requested format
- Resolve only explicit or verified-profile template paths; `--use-defaults` cannot waive required brand policy
- Apply actual configured freshness/voice/compliance requirements and their applicability
- Declare required fidelity/format inspections using P05/P07 before observations; mandatory failure/error/unverified blocks the affected action

Planned PDF/XLSX/Visio routes keep concrete activation gates: PDF writer/export plus
page/text fidelity; XLSX writer plus actual recalculation, formula/cache integrity
and reopen; Visio writer plus connector/label/rendered-editability checks. Missing
adapters are not implemented by an operator confirming that content is generated
fresh. Keep the affected output open and continue independent supported formats.

### Step 3 — Generate outline (shared)

Invoke `generate-outline` sub-skill:
- Input: `--brief "${brief}" --target-formats "${formats}" --audience "${audience}" --arc "${arc}"`
- Output: `${run_dir}/outline.md`

Surface outline to operator via short summary (slide_count, sections, key messages). Offer to skip-ahead if outline is approved or rewind to S1 if not.

### Step 4 — Generate written content (shared)

Invoke `generate-write` sub-skill:
- Input: `--outline ${run_dir}/outline.md`
- Output: `${run_dir}/content.md` (plus `${run_dir}/speaker-notes.md` if `ppt` in formats)
- Voice tier: the active pack's voice tier (default: `internal`); upgraded per pack if `--customer-share`
- Retain multi-paragraph reasoning, tables, citations and material limitations; slide brevity is a separate presentation view with full detail in actual notes/appendix or delivered linked long-form content

### Step 5 — Generate design spec (shared)

Invoke `generate-design` sub-skill:
- Input: `--content ${run_dir}/content.md --target-formats "${formats}" --palette "${palette}"`
- Output: `${run_dir}/design-spec.json` (per-format layout-mappings)

Keep the existing v1.0 document projections; do not shrink canonical content to
fit a slot or invent a second design schema. Document-only inputs use P11
compatibility plus format-owned reference checks under the external P05/P07/P08
input context. Genuine mixed web/document input also needs full P11 `load_design`.
An unresolved web binding cannot become a document-only success.

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
- Read original prerequisites and actual acceptance evidence; source checkboxes
  from the work reader cannot authorize execution. Selected upstream P09 data
  retains its own request/context/profile, not the document's new QA inventory.
- Invoke format-builder with `--from-pipeline ${run_dir}` flag:
  - `ppt` → `/li:generate-ppt --from-pipeline ${run_dir} --template ${template}`
  - `web` → `/li:generate-web --from-pipeline ${run_dir} --variant single-file`
  - `word` → `/li:generate-word --from-pipeline ${run_dir} --target ${target}`
  - `pdf` / `xlsx` → pass admitted full source to their existing standalone
    production procedures; retain converter/print or formula/cache/reopen gates,
    without inventing document layout projections
  - `visio` → actual writer/editor seam still required; no image-as-VSDX substitution
- Each format-builder writes its output to `${run_dir}/<format>/<artifact>.<ext>`

Builders retain brand, honest-limitations and provenance categories with actual
applicability, plus source-retention, editable-reopen and rendered inspection.
Upstream controls are reusable only while their bound source/profile remains
unchanged; they cannot cover a later lossy format conversion.

### Step 8 — Aggregate QA

Invoke `generate-qa` sub-skill on all produced artifacts:
- Input: `--artifacts ${run_dir}/*/`
- Output: `${run_dir}/qa-report.json`

Compare each saved artifact with the full source and inspect its actual available
render/reopen layer. Auto-fixes must preserve meaning and invalidate affected
pre-edit evidence. A missing renderer or dropped qualification cannot be averaged
away by a score or an otherwise empty issue list.
Prepare the final external P05 context after changed artifacts exist. Input
admission is not final QA, and `qa-report.json` remains the existing presentation
report rather than a replacement evidence envelope.

### Step 9 — Output + telemetry

Print exact run/source/artifact/evidence paths and unfinished format gates.
The existing completion event below is appropriate only for a genuinely completed
run; a partial/unverified output must not emit successful completion telemetry:

```yaml
event: generate_run_complete
run_id: <id>
brief: <hash of brief>
formats: <list>
voice_tier: <pack-resolved; internal default>
qa_pass: <true|false>
ts: <iso-8601>
```

## Voice tier behavior

- **Default `internal`** — no invented customer voice rule; any applicable configured internal requirements still apply.
- **`--customer-share` flag** — content will be delivered to customer. The active pack's compliance gates apply (`resolve_pack_field compliance.hooks`; none by default). Voice tier upgraded per pack. Vocabulary-blocklist enforced if the pack defines one.

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
- `.claude/runtime/state/00-state.md` (telemetry)

**Writes:**
- Selected owned run directory (original brief, outline.md, full content.md, speaker-notes.md if PPT, actual design-spec.json where released, per-format artifacts, qa-report.json and bound evidence)
- `.claude/runtime/state/00-state.md` (run event)

**Triggers (sub-skills):**
- `/li:generate-outline`, `/li:generate-write`, `/li:generate-design`, `/li:generate-qa` (shared pipeline)
- `/li:generate-ppt`, `/li:generate-web`, `/li:generate-word` (canonical format-builders)
- `/li:generate-pdf`, `/li:generate-xlsx`, `/li:generate-visio` (planned adapters with the specific writer/inspection gates above)

**Compliance gates:**
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) at orchestrator level if `--customer-share`

## Anti-patterns

- **Confuse methods with customer content** — reusable format procedures belong in skills; real customer data does not. Planned adapters need working procedures and evidence, not an indefinite empty-slot promise.
- **Bypass the compliance gate when `--customer-share` is set** — if the active pack defines gates, they are non-negotiable. A failing gate blocks.
- **Run format-builders in parallel before content/design steps complete** — design-spec.json is a dependency. Builders fail loudly if missing.
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
5. **compliance-gate aggregator** optionally invokes broader customer-share gates at end-of-pipeline — `/li:compliance-gate --scope customer-share` runs all the active pack's configured gates

The customer-share flag selects customer-facing applicability; it does not disable
mandatory internal policy or source fidelity when absent. Neutral style advice
does not become a hard vocabulary rule.

Use the flag with the verified current profile, not instead of it.

## Deferred flags (YAGNI)

These flags appeared in earlier design-doc drafts but are **not implemented** as of v3.6 closeout. Documented here so future readers don't expect them:

- **`--keep-runs <N>`** — purge run-dirs after N retained. Not implemented (PR #7 concern #3, deferred). If operator's `~/.lintel/generate-runs/` grows unwieldy, manual cleanup or future `--keep-runs` add. Don't pre-build until dogfood shows the friction.

## Failure recovery

- **Sub-skill fails mid-chain**: stop, surface error, write partial run-state to `${run_dir}/RUN-STATE.md`. Operator can resume with `--resume ${run_id}`.
- **One format fails**: preserve successful independent outputs and report the blocked requested format; do not claim the whole run complete.
- **Pack compliance gate fails on `--customer-share`**: block, surface the failing gate, exit BLOCKED.
- **Adapter/renderer unavailable**: report the exact remaining gate; alternatives require an explicit format choice and their own inspection.

## Recommended next steps after invocation

- For one-format follow-up after shared binding is available: use the format-builder's `--from-pipeline ${run_dir}` flag, preserving the full source.
- For voice-tier upgrade (internal → customer-share): re-invoke `/li:generate --customer-share --from-pipeline ${run_id}`.
- For multi-format-cohort comparison: invoke `/li:qa-only` on the aggregated qa-report.
- For sharing externally: pipe `${run_dir}/web/index.html` via `/li:generate-web --customer-share` after the compliance gate passes.
