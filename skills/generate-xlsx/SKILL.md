---
name: generate-xlsx
layer: foundation
description: ⚠ TEMPLATE ONLY — Slot for Excel spreadsheet generation (data + estimates + tables). Content not curated. AI generates fresh at invocation per L-001.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

## ⚠ TEMPLATE ONLY — Slot for XLSX generation

This skill is a **scaffolding slot** per L-001 (Lintel = scaffolding, not curated content). The frontmatter + agent-mapping entry exist; the workflow body does not. When an operator invokes this skill, the AI generates the appropriate workflow content at invocation time using the design-spec.json + content.md from the shared pipeline.

## Why a slot exists

XLSX is the natural artifact for tabular data: cost-estimates, capacity-forecasts, comparison-matrices, customer-question-trackers. The shared pipeline's outline → write produces text content; XLSX-generation requires identifying which sections are tabular candidates + structuring them as worksheets with formulas. This decision is content-specific and benefits from AI-at-invocation rather than pre-baked workflow.

## At-invocation contract

When invoked (via `/li:generate-xlsx --from-pipeline <run-dir>` or directly):

1. **Tabular extraction:** AI reads content.md + identifies sections that are inherently tabular (estimates, comparisons, schedules, options-matrices). Non-tabular sections (narrative, vision) are excluded.
2. **Worksheet structure:** One worksheet per tabular section + one summary worksheet linking them. Use design-spec.json's palette for header colors + font for consistency with sibling artifacts.
3. **Formula insertion:** Where estimates appear, AI inserts SUM/PRODUCT/AVERAGE formulas instead of hardcoded totals. Where comparisons appear, AI uses conditional-format rules for red/green status.
4. **Build:** Use openpyxl or equivalent Node-based xlsx library to produce `*.xlsx`. Brand-template from `~/.lintel/brand/xlsx-templates/` if present.
5. **QA hand-off:** Pass produced `*.xlsx` to `/li:generate-qa` for validation.

## Brand template

`~/.lintel/brand/xlsx-templates/` slot exists. Templates might include: `customer-estimate-template.xlsx`, `engagement-tracker-template.xlsx`, `comparison-matrix-template.xlsx`. If template present, AI uses it as starting structure. If empty, AI creates fresh workbook from design-spec.

## Agent dispatch

Per `skills/generate/agent-mapping.yaml`:
- Primary: CostAnalyzer (XLSX use cases skew cost/estimate)
- Conditional: CapacityPlanner if capacity/sizing content
- Conditional: SecurityAuditor if content references customer-sensitive data

## Voice tier

`voice: internal` default. XLSX content typically internal-only; even when shared with customer, voice is data-driven (numbers + labels), not prose.

If invoked with `--customer-share`, requires an upstream PASS from the active pack's voice gate (none by default) on any prose labels/headers (orchestrator-level gate).

## Status protocol

- **DONE** — `*.xlsx` produced + qa-handoff successful + formulas validated
- **DONE_WITH_CONCERNS** — produced but qa flagged formula errors or layout issues
- **BLOCKED** — content.md has no tabular sections + no fresh-data strategy declared
- **NEEDS_CONTEXT** — `--from-pipeline` directory missing or design-spec absent

## When to promote from slot to curated

If a recurring estimate-pattern emerges (e.g., always the same cost-estimate with same worksheet structure), promote that pattern into the SKILL.md body — that becomes a canonical XLSX-builder for that scenario.

Until then: AI generates fresh per invocation. Repo stays clean.

## Recommended next steps

After invocation:
- For QA: `/li:generate-qa --artifacts <xlsx-path>`
- For multi-format consistency: invoke parent `/li:generate` instead of solo-invocation
- For data-fresh: re-invoke with `--update-data <source>` to refresh estimates against current pricing/inventory
