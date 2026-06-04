---
name: generate-pdf
layer: foundation
description: ⚠ TEMPLATE ONLY — Slot for PDF document generation. Content not curated. AI generates fresh at invocation per L-001.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

## ⚠ TEMPLATE ONLY — Slot for PDF generation

This skill is a **scaffolding slot** per L-001 (Lintel = scaffolding, not curated content). The frontmatter + agent-mapping entry exist; the workflow body does not. When an operator invokes this skill, the AI generates the appropriate workflow content at invocation time using the design-spec.json + content.md from the shared pipeline.

## Why a slot exists

PDF is a common terminal artifact (kund-leverans, archival), but typically generated FROM another format (PPT export → PDF, DOCX export → PDF, web print → PDF). Having a slot here is signal that operator-AI may be asked to handle this case; pre-baking content would violate L-001 because PDF-generation strategy depends on the source format chosen at invocation time.

## At-invocation contract

When invoked (via `/li:generate-pdf --from-pipeline <run-dir>` or directly):

1. **Source-format decision:** Operator-AI inspects design-spec.json's `per_format` field. If `ppt` is present, default strategy is "render via PPTX → export PDF." If `word` is present, default is "render via DOCX → export PDF." If `web` is present, default is "render via HTML → print to PDF." If only `pdf` is requested, operator-AI generates fresh content using design-spec as scaffold.
2. **Strategy declaration:** Operator-AI declares chosen strategy in run state, e.g.: `pdf_strategy: source=ppt, exporter=libreoffice-headless`.
3. **Build:** Apply chosen strategy. Use design-spec.json's palette + fonts + per-format layout-mapping to ensure visual consistency with sibling format artifacts.
4. **QA hand-off:** Pass produced `*.pdf` to `/li:generate-qa` for validation.

## Brand template

`~/.lintel/brand/pdf-templates/` slot exists. If template present (e.g., `customer-deliverable.pdf` as visual reference), AI uses it as design-baseline. If empty, AI uses design-spec.json's palette + fonts only.

## Agent dispatch

Per `skills/generate/agent-mapping.yaml`:
- Primary: WordTechnicalEditor (fallback for document-shaped content)
- Conditional: SecurityAuditor if content references customer-data or compliance
- Conditional: AccessibilityChecker if `--accessible` flag

## Voice tier

`voice: internal` default. If invoked with `--customer-share`, requires an upstream PASS from the active pack's voice gate (none by default) (orchestrator-level gate).

## Status protocol

- **DONE** — `*.pdf` produced + qa-handoff successful
- **DONE_WITH_CONCERNS** — produced but qa flagged issues
- **BLOCKED** — no source format available + no fresh-content strategy declared
- **NEEDS_CONTEXT** — `--from-pipeline` directory missing or design-spec absent

## When to promote from slot to curated

If a PDF-specific generation strategy emerges from repeated invocations (e.g., always libreoffice-headless from DOCX for customer-deliverables), promote that pattern into the SKILL.md body — that becomes the canonical workflow.

Until then: AI generates fresh per invocation. Repo stays clean.

## Recommended next steps

After invocation:
- For QA: `/li:generate-qa --artifacts <pdf-path>`
- For voice-gate (if customer-share): run the active pack's voice gate (none by default) on source content before PDF-export
- For multi-format consistency: invoke parent `/li:generate` instead of solo-invocation
