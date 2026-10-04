---
name: li-generate-qa
description: Use to inspect generated or supplied artifacts against source, brand, readability and structure requirements without modifying them; explicitly requested repairs use a separate owned copy.
---

> **Lintel on GitHub Copilot.** Generated from `skills/generate-qa/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/generate-qa/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/generate-qa/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `generate-qa` skill — final stage of the v3.5 shared content pipeline. Validates produced artifacts against brand, voice, readability, and structural standards.

## What this skill does

Inspects selected artifacts (PPTX, DOCX, HTML, PDF, XLSX or Visio) only through
actually available format operations, with their source, optional design spec and
configured voice requirements. Produces qa-report.json with issues, coverage and
unavailable checks. A recognized extension is not proof of inspection support.
Inspection is report-only by default; repairs require explicit authorization and
a separate output.
For standalone Word/PPT, a design-spec is optional: inspect the exact original
brief/content and saved artifact. Follow the
[source-fidelity and P05/P07 evidence procedure](../../../skills/generate-write/references/fidelity-and-evidence.md).
Do not invent a shared design input or treat package extraction as rendered inspection.

Crucially: **invocable solo on any artifact**, including those not produced by the `generate` pipeline. Operator can run QA on a deck a teammate sent them, on an existing .docx from a prior engagement, on a web page exported from another tool.

Used by `generate` orchestrator as Step 8 (aggregate QA on all produced formats), or solo at any time.

## When to use

- Last step of `/li-generate` orchestrator chain (after format-builders complete)
- Operator received a deck/doc from a teammate and wants brand/voice check before forwarding
- Pre-customer-share gate — run QA before voice-gate to catch issues that voice-gate doesn't (layout, font sizes, contrast)
- Post-edit verification — operator hand-edited a deck, wants confirmation that constraints still hold

## When NOT to use

- Voice-gate execution — use the active pack's `voice.gates_active` and its actual
  configured corpus. Compliance hooks are a separate source of controls; an empty
  `compliance.hooks` list is not a passed or absent required voice check.
- Brand-asset audit (template freshness across the brand directory) — that's a separate operator workflow
- Pre-implementation design review — use `/li-inspect --target plan --lens design`

## Inputs

- Required `--artifacts <path|paths>` — single artifact or list (glob: `${run_dir}/*/*` works)
- Optional `--design-spec <path>` — generating design-spec.json for cross-reference checks (if available)
- Optional `--source <path>` — exact source brief or content.md for standalone retention checks
- Optional `--palette <name>` — palette for brand-color validation (default: inferred from design-spec or the active pack's default palette)
- Optional `--vocabulary-blocklist <path>` — voice blocklist for content-text checks
- Optional `--auto-fix <safe|aggressive|none>` — auto-fix mode (default: none)
- Optional `--fixed-out <path>` — new owned artifact path; required for `safe` or `aggressive`. Repair one artifact per invocation; inspect multiple artifacts together in report-only mode.
- Optional `--out <path>` — qa-report.json output path (default: alongside artifacts)

The report destination must also be an authorized new output. Refuse a report
path that aliases an input, a repaired artifact or an existing unrelated file;
report-only does not authorize overwriting an artifact with the JSON report.

## Check categories

Determine applicability and mandatory/advisory status from the brief, selected
acceptance and verified profile **before** observing results. For mapped evidence,
use P05's immutable `qa_requirements`; standalone inspection uses its existing
snapshot/inspect path. The tables below describe checks, not invented neutral hard
gates. Required errors, missing tools, unknown applicability and unperformed
inspections stay unresolved regardless of an advisory score.

### Source fidelity and actual inspection

Trace all material claims, reasoning paragraphs, table cells/units, citations and
limitations from the full source to output locations. A long Word section is not
a malformed slide. For PPT, inspect visible claims plus actual saved notes/appendix
and delivered linked long-form content. Missing detail in a sidecar that never
reaches the delivered package is a fidelity finding.

In report-only `none` mode, do not perform mutating native edit/readback probes.
Use non-mutating inspection and any applicable attributable existing editability
evidence. A required editability check with no such evidence remains unverified,
not waived because the file is normally editable. A new mutating probe is a
separately authorized verification on a distinct owned copy, with its own
path/content-bound evidence; it is not implicit QA or permission to edit the
supplied artifact. Repairs still require their explicit mode and `--fixed-out`.

Render every required page/slide through an authorized non-mutating operation
and inspect wrapping, clipping, overlap,
legibility, table continuation and assets at that renderer's layer. Word model/ZIP
checks cannot prove pagination; a PowerPoint SVG render does not establish every
Office application's behavior. Record the tool, instance, actions, paths/hashes,
coverage and unsupported features. Missing rendering is unverified, not N/A or PASS.

### Brand (palette/font/logo)

| Check | Rule | Severity |
|-------|------|----------|
| Colors/fonts | Match explicit or configured requirements | severity from applicable requirement |
| Logo | Required only by actual brief/profile, with an authorized asset | severity from applicable requirement |
| Logo placement | Inspect only where a logo is required/present | warning unless required |

### Readability

| Check | Rule | Severity |
|-------|------|----------|
| Titles/bullets | Concise visible slides, complete source detail elsewhere; no universal section cap | advisory unless explicitly required |
| Font size | Legible in the actual format and viewing context; inspect rendering after resizing | severity from applicable requirement |
| Contrast | When WCAG AA applies, measured normal text >= 4.5:1 and large text >= 3:1 | mandatory when required, otherwise advice |
| Slide/page count | Serves material and duration; count targets cannot authorize content loss | info unless an explicit delivery constraint |

### Voice

| Check | Rule | Severity |
|-------|------|----------|
| Blocklist | Actual configured tiers, scope and exceptions; no neutral stock blocklist | mandatory/advisory as configured |
| Passive voice | Flag excessive passive constructions | info |
| Sentence length | Readability advice appropriate to language and technical precision | info |

### Structure

| Check | Rule | Severity |
|-------|------|----------|
| Empty content | No slide/section without content | error |
| Duplicate titles | No two slides/sections same title | warning |
| Speaker notes | Supporting source detail required by the presentation view survives in actual notes/appendix or linked deliverable | error when required detail is missing |
| Heading hierarchy | No skipped levels (H1 → H3 with no H2) | warning |

## Auto-fix modes

**`none` (default):**
- Report-only mode. No artifact modification, including files produced by this pipeline.
- Report findings and proposed fixes without creating a repaired copy.

**`safe` (explicit):**
- Normalize decorative formatting only when semantics and source coverage are unchanged
- Remove a genuinely empty unused placeholder, not a source slot awaiting content
- Copy the source to the explicit `--fixed-out`, preserve the original bytes and record every edit to the copy
- Reopen and repeat affected retention/render checks after any edit; font resizing or wording changes are not automatically safe

**`aggressive` (explicit):**
- All `safe` actions
- With explicit approval, reflow/split slides, add continuation pages, or move detail to actual notes/appendix while preserving every fact and citation
- Propose order, wording or contrast changes with a source-preserving diff
- Never truncate bullets or delete qualifiers to meet a count or font target

Neither repair mode authorizes overwriting the source or an existing destination.
Reject the same path, a symlink/hard-link alias, an unowned output or an unavailable
destination before writing. Never fall back to the input path or current directory.
`--out` is the report destination, not permission to use it for a repaired artifact.

## Qa-report.json schema

```json
{
  "version": "1.0",
  "generated_at": "<iso-8601>",
  "artifacts_checked": ["<path1>", "<path2>"],
  "design_spec_used": "<path or null>",
  "auto_fix_mode": "safe|aggressive|none",
  "summary": {
    "total_checks": <int>,
    "passed": <int>,
    "warnings": <int>,
    "errors": <int>,
    "auto_fixes_applied": <int>,
    "qa_pass": <true|false>
  },
  "issues": [
    {
      "artifact": "<path>",
      "location": "slide-4 / section-§2 / page-3",
      "check": "voice/blocklist-tier-1",
      "severity": "error|warning|info",
      "detail": "'comprehensive' found in bullet 2",
      "auto_fixed": <true|false>,
      "fix_applied": "replaced with 'complete'"
    }
  ]
}
```

## Workflow

### Step 1 — Resolve artifact list

Parse `--artifacts` (single path or glob). Validate each exists + is in supported format (PPTX, DOCX, PDF, HTML, XLSX, Visio source files).

### Step 2 — Load context

- `--design-spec <path>` if provided (for cross-reference checks: does artifact match what was specified?)
- `--palette <name>` (or infer from design-spec, or default to the active pack's default palette)
- `--vocabulary-blocklist <path>` (or default from the active pack's voice corpus; none by default)
- Full source and claim ledger; verify hashes rather than checking a generated summary against itself
- Current P07 profile reference/required-policy bridge and P05 accepted check inventory

For a pipeline-produced document, repeat the
[existing input admission](../../../skills/generate-write/references/fidelity-and-evidence.md#existing-pipeline-input-admission)
against its current external context before comparing source/design with the
artifact. Use original package/leaves and selected templates/config; never
substitute a same-bytes sibling path or a cached admission result. This is
read-only source verification, not QA of an uncreated artifact. Retain the
standalone `--source` route without requiring pipeline files.

### Step 3 — Per-artifact checks

Discover actual available inspection tools and schemas first; prefer native
operations or already declared libraries. Word/PPT canvas model operations,
python-docx/python-pptx and ZIP/XML extraction provide different coverage from a
page/slide renderer. Name the layer and do not count an extractor as rendering.
Check all selected applicable categories and retain missing observations.

For PPTX, use the shipped [`check_pptx.py` retention procedure](../../../skills/generate-ppt/references/retention-check.md)
with the actual artifact and explicit source inventory. It refuses malformed or
aliased notes and reports missing paragraphs/cells; it is read-only ZIP/XML
inspection, not native rendering, reopen/editability or full layout verification.

PDF has an existing converter/browser-print writer but no shipped PDF reader:
produced text, pages and visual rendering stay unverified without an actually
available authorized inspection operation. XLSX uses its existing production
method, actual recalculation and shipped formula/cache checker; persisted caches
and application reopen remain separate observations. Visio has no shipped writer;
connector/label/rendered editable-reopen checks require actual host operations.
Do not install a reader/renderer or invent shared projections to hide these gaps.

### Step 4 — Apply auto-fixes per `--auto-fix` mode

With `none`, skip repairs. A check request or a suggested fix is not explicit
repair authorization. For `safe` or `aggressive`, validate the single selected
artifact and distinct owned `--fixed-out` before creating a copy. If authorization
or the output is missing, report that repair is blocked; keep the original
inspection results, and do not choose an output on the operator's behalf.

Record source/output paths and hashes, `auto_fixed` and `fix_applied`. Apply edits
only to the copy and verify the original bytes remain unchanged. Re-read the
changed copy, compare it to the full source and rerun affected checks. Prepare
P05 evidence for the copy's actual path and content; identical initial bytes do
not transfer a source artifact's PASS to another path. An edit cannot retain a
pre-edit PASS.

### Step 5 — Compose qa-report.json

Keep the existing report fields. Counts describe actual checks, not assumed passes.
Set `summary.qa_pass` true only when the applicable required validation was actually
performed and P05's evaluation has no mandatory blocker, with requested format
coverage complete. Otherwise set false and record the missing/failed requirement
in `issues`, referring to its P05 evidence. No applicable checks is not a verified
QA pass. Persist the bound P05 receipt separately; qa-report.json is not clearance.
Input admission does not supply missing artifact observations. Keep the original
mandatory inventory, reprepare the final context after source/artifact edits,
and respect any explicit decision/corroboration persistence denial.

### Step 6 — Surface summary to operator

Print: total checks, pass/warn/err counts, qa_pass status, auto-fix count, top 3 unresolved errors.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
When a design spec carries `pattern_context`, verify it first; then check each mandatory clause
against the produced artifacts and report it by clause ID as passed, failed or unverified in
qa-report.json. A missing required section is failed. These results feed the clause review
evidence; QA never clears review, and an unverified clause is not passed.

## Status protocol

- **DONE** — report written, required inspection complete and qa_pass=true
- **DONE_WITH_CONCERNS** — required checks satisfied with advisory concerns explicitly retained
- **BLOCKED** — required inspection/control failed or remains unverified, including missing/unreadable artifacts or unavailable extraction/rendering; report useful partial observations
- **NEEDS_CONTEXT** — `--artifacts` empty or glob matched nothing

## Pause-points

- A proposed repair changes intent or exceeds the explicitly authorized scope: resolve that decision before editing the copy
- Vocabulary-blocklist match in customer-share context but operator hasn't run the active pack's compliance gates: surface recommendation to run the voice-gate

## Integration

**Reads:**
- Artifact files (PPTX, DOCX, HTML, PDF, XLSX, Visio)
- `design-spec.json` (optional, for cross-reference)
- Explicit palette/source paths selected through the verified profile; no personal-directory scan
- The active pack's vocabulary blocklist (`resolve_pack_field voice.corpus`; none by default)

**Writes:**
- `qa-report.json` to `--out`
- A new artifact at explicit `--fixed-out` only when `safe` or `aggressive` repair is authorized; the original is never edited

**Consumed by:**
- `/li-generate` orchestrator (Step 8 — aggregate QA across all produced formats)
- Operator (solo-invocation for arbitrary artifact validation)

## Anti-patterns

- **Auto-fix `aggressive` without operator confirmation** — reflow/reorder can change intent. No mode permits silent content loss.
- **Treat QA-pass as sharing permission** — applicable policy, independent review and delivery authority still govern; neutral voice advice is not an invented hard gate.
- **Modify artifact when `--auto-fix none`** — none means report-only. Hard rule.
- **Repair the original or silently choose a destination** — repair authority requires an explicit distinct owned output, including for teammate-supplied files.
- **Skip cross-reference check when design-spec available** — if operator provided design-spec, validate artifact matches spec (catches drift).

## Failure recovery

- Tool missing: use another actually available authorized operation, or record incomplete text/render/edit coverage; never convert missing required coverage to pass
- Artifact corrupted: report unreadable + skip, continue with other artifacts in batch
- Required palette/profile resolution fails: block the affected action; optional neutral defaults remain explicitly advisory

## Recommended next steps after invocation

- If `qa_pass=true`: the reported required inspection is satisfied for the bound artifact; obtain any outstanding independent review and delivery authorization
- If `qa_pass=false` with errors: operator addresses errors manually, re-runs QA
- If many warnings: consider re-invoking `/li-generate-design` with different palette or template
- For customer-share: chain the active pack's compliance gates after QA-pass
