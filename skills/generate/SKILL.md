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

Reads operator brief → chains outline → write → design → qa → format-specific builders (`generate-ppt`, `generate-web`, `generate-word`, and ⚠ slots for `generate-pdf` / `generate-xlsx` / `generate-visio`) → writes artifacts to `~/.lintel/generate-runs/<run-id>/`.

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
run_dir="${HOME}/.lintel/generate-runs/${run_id}"
mkdir -p "${run_dir}"
```

If brief is empty: surface available recent runs from `~/.lintel/generate-runs/` and exit `NEEDS_CONTEXT`.

### Step 2 — Preflight gates

Per format in `--formats`:
- Verify `~/.lintel/brand/<format>-templates/` exists OR `--use-defaults` flag present
- Brand-staleness warn check (90-day rule) — surface warning, do not block
- If `--customer-share`: run the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) — block on any gate failure

If any format in list is a `⚠ template only` slot (pdf, xlsx, visio): surface that operator-AI must generate format-specific content per L-001 (no pre-curated content in repo). Proceed if operator confirms; offer to substitute with a curated format.

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

### Step 5 — Generate design spec (shared)

Invoke `generate-design` sub-skill:
- Input: `--content ${run_dir}/content.md --target-formats "${formats}" --palette "${palette}"`
- Output: `${run_dir}/design-spec.json` (per-format layout-mappings)

### Step 6 — Compliance gate (orchestrator-level if --customer-share)

If `--customer-share`:
- Run the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) on `${run_dir}/content.md`
- Block on any gate failure or vocabulary-blocklist hits
- Proceed on PASS

This is the orchestrator-level gate. Format-builders still apply their own brand/honest-limitations/provenance gates per format (see Anti-patterns for execution-order rule).

### Step 7 — Per-format build (chained)

For each format in `--formats`:
- Invoke format-builder with `--from-pipeline ${run_dir}` flag:
  - `ppt` → `/li:generate-ppt --from-pipeline ${run_dir} --template ${template}`
  - `web` → `/li:generate-web --from-pipeline ${run_dir} --variant single-file`
  - `word` → `/li:generate-word --from-pipeline ${run_dir} --target ${target}`
  - `pdf` / `xlsx` / `visio` → ⚠ slot path: operator-AI generates content at invocation per L-001
- Each format-builder writes its output to `${run_dir}/<format>/<artifact>.<ext>`

Format-builders apply remaining 3 gates (brand, honest-limitations, provenance) per their own SKILL.md. Compliance is already gated at orchestrator level.

### Step 8 — Aggregate QA

Invoke `generate-qa` sub-skill on all produced artifacts:
- Input: `--artifacts ${run_dir}/*/`
- Output: `${run_dir}/qa-report.json`

Surface qa-report summary to operator. Auto-fix applied where possible (recorded in report).

### Step 9 — Output + telemetry

Print run directory + artifact paths. Append run-event to `.claude/runtime/state/00-state.md`:

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

- **Default `internal`** — content is operator-facing intermediate artifact. No customer-bound gate required.
- **`--customer-share` flag** — content will be delivered to customer. The active pack's compliance gates apply (`resolve_pack_field compliance.hooks`; none by default). Voice tier upgraded per pack. Vocabulary-blocklist enforced if the pack defines one.

## Status protocol

- **DONE** — all formats produced + qa_pass=true + run_dir printed
- **DONE_WITH_CONCERNS** — formats produced + qa_pass=false; surface qa-report
- **BLOCKED** — preflight failed (missing template + no `--use-defaults`, pack compliance gate failed with `--customer-share`, slot-format invoked without confirmation)
- **NEEDS_CONTEXT** — brief missing or unparseable

## Pause-points

- Brief is ambiguous: surface back to operator + offer 3 interpretations
- Pack compliance gate fails + `--customer-share`: hard-block, surface the failing gate
- Slot-format requested: confirm with operator that AI will generate content fresh (no pre-curated content per L-001)

## Integration

**Reads:**
- Operator brief (path or inline)
- `~/.lintel/brand/<format>-templates/` per requested format
- `~/.lintel/profile.yaml` (role context if active)
- `.claude/runtime/state/00-state.md` (telemetry)

**Writes:**
- `~/.lintel/generate-runs/<run-id>/` (outline.md, content.md, speaker-notes.md if PPT, design-spec.json, per-format artifacts, qa-report.json)
- `.claude/runtime/state/00-state.md` (run event)

**Triggers (sub-skills):**
- `/li:generate-outline`, `/li:generate-write`, `/li:generate-design`, `/li:generate-qa` (shared pipeline)
- `/li:generate-ppt`, `/li:generate-web`, `/li:generate-word` (canonical format-builders)
- `/li:generate-pdf`, `/li:generate-xlsx`, `/li:generate-visio` (⚠ slots — AI generates at invocation)

**Compliance gates:**
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) at orchestrator level if `--customer-share`

## Anti-patterns

- **Pre-bake content into ⚠ slot SKILL.md files** — violates L-001. PDF/XLSX/Visio slots stay scaffolding; AI generates at invocation, content does not commit to repo.
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

## Vocabulary-blocklist ↔ customer-share-gate interaction (resolves PR #7 concern #4)

The vocabulary-blocklist enforcement chain is:

1. **Operator passes `--customer-share` to /li:generate orchestrator**
2. **Orchestrator propagates voice-tier:** sets the active pack's voice tier (`resolve_pack_field voice.default_tier`) on generate-write (Step 4)
3. **generate-write applies the vocabulary-blocklist** from the active pack's voice corpus (`resolve_pack_field voice.corpus`; none by default) — blocklisted words are never emitted
4. **generate-qa runs the compliance gate** (Step 6) via the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) — verifies blocklist compliance + any pack-defined match threshold
5. **compliance-gate aggregator** optionally invokes broader customer-share gates at end-of-pipeline — `/li:compliance-gate --scope customer-share` runs all the active pack's configured gates

The customer-share flag is **load-bearing for the entire chain**. Without it: voice-tier defaults to internal, blocklist not enforced, compliance gate doesn't fire, compliance-gate aggregator not auto-invoked.

Single source of truth: `--customer-share` on `/li:generate`. All downstream voice + compliance behavior derives from this flag and the active pack's configuration.

## Deferred flags (YAGNI)

These flags appeared in earlier design-doc drafts but are **not implemented** as of v3.6 closeout. Documented here so future readers don't expect them:

- **`--keep-runs <N>`** — purge run-dirs after N retained. Not implemented (PR #7 concern #3, deferred). If operator's `~/.lintel/generate-runs/` grows unwieldy, manual cleanup or future `--keep-runs` add. Don't pre-build until dogfood shows the friction.

## Failure recovery

- **Sub-skill fails mid-chain**: stop, surface error, write partial run-state to `${run_dir}/RUN-STATE.md`. Operator can resume with `--resume ${run_id}`.
- **Format-builder fails on one format but others pass**: produce qa-report flagging the failed format; complete-with-concerns status.
- **Pack compliance gate fails on `--customer-share`**: block, surface the failing gate, exit BLOCKED.
- **Slot-format requested but operator-AI cannot generate fresh content**: substitute with closest curated format (PDF → PPTX-then-export), surface substitution to operator.

## Recommended next steps after invocation

- For one-format follow-up tweak: invoke specific format-builder solo with `--from-pipeline ${run_id}` flag.
- For voice-tier upgrade (internal → customer-share): re-invoke `/li:generate --customer-share --from-pipeline ${run_id}`.
- For multi-format-cohort comparison: invoke `/li:qa-only` on the aggregated qa-report.
- For sharing externally: pipe `${run_dir}/web/index.html` via `/li:generate-web --customer-share` after the compliance gate passes.
