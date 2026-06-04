---
name: generate-word
layer: foundation
description: Produce brand-compliant Word doc via docx-templater — technical / customer-summary / transparency-note variants.
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
license_note: produces customer-bound output; honors the active pack's compliance gates for customer-facing variants
---

# /generate-word

Brand-compliant Word document generation. Three target variants:

- **`technical`** — engineering-internal deliverable (technical spec, runbook, ADR-style doc) — voice: internal
- **`customer-summary`** — customer-bound engagement summary — voice: pack-resolved (customer-facing tier), gated
- **`transparency-note`** — AI-feature transparency note — voice: pack-resolved (customer-facing tier), gated, includes honest-limitations check

Uses docx-templater under the hood. Phase F of v2 build.

## When to use

- Customer engagement summary deliverable
- Technical spec / architecture doc with the active pack's brand identity
- AI-feature transparency note (compliance artifact, if the active pack requires one)

## When NOT to use

- Quick markdown note — use direct editing
- Slide content — use `/generate-ppt`
- Multi-page wiki/site — use `/generate-web`

## Inputs

- Required `--brief <path|inline>` — content brief or source markdown **OR** `--from-pipeline <dir>` (Fas 2: shared pipeline mode)
- Required `--target <technical|customer-summary|transparency-note>` — variant
- Optional `--template <name>` — explicit template (default: `<target>.docx` from brand)
- Optional `--audience <text>` — primary audience
- Optional `--voice` — voice tier override (default per target)
- Optional `--use-defaults` — force in-repo default templates
- Optional `--ignore-stale-brand <reason>` — bypass staleness-warn

## From-pipeline mode (v3.5 Fas 2 — generate-pipeline integration)

If invoked med `--from-pipeline <run-dir>` istället för `--brief`:

1. **Read shared pipeline-output:**
   - `<run-dir>/content.md` — sections med H1/H2/H3 hierarchy + bodies + voice-annotations
   - `<run-dir>/design-spec.json` — read `per_format.word.sections` för heading-levels + slot-mappings

2. **Replace brief-parsing logic** med direct-read av content.md (per target-variant):
   - `technical`: headings + paragraphs + code blocks + tables
   - `customer-summary`: narrative paragraphs + key findings + next steps
   - `transparency-note`: capabilities + limitations + data + decisions + appeals

3. **Apply format-specific design-pass via design_pass_hook:**
   - Reads `per_format.word.sections[N].design_pass_hook` (canonical: WordTechnicalEditor)
   - Invokes agent på Word-specific fidelity-pass (heading-style consistency, technical-tone, tables-formatting)
   - Per Reviewer Concern #7: WordTechnicalEditor stays word-specific

4. **CLI bevaras backward-compat:** befintliga `--brief`-flag invocations fungerar oförändrat. `--from-pipeline` är additive.

5. **4-gate pipeline körs som vanligt** (voice + brand + honest-limitations om transparency-note + provenance).

## Workflow

1. **Preflight gates** (same as /generate-ppt) — brand template present, staleness check, the active pack's compliance gates for customer-facing variants

2. **Read brief + parse into target-shape:**
   - **technical:** headings + paragraphs + code blocks + tables → matched to technical template
   - **customer-summary:** narrative paragraphs + key findings + next steps → matched to customer template
   - **transparency-note:** capabilities + limitations + data + decisions + appeals → matched to transparency template

3. **Invoke target-specific agent:**
   - technical → `WordTechnicalEditor` agent for structure + accuracy review
   - customer-summary → `WordTechnicalEditor` for structure; voice gate Gate 1 handles voice
   - transparency-note → both `WordTechnicalEditor` and explicit honest-limitations check

4. **Generate via docx-templater:**
   - Load template
   - Substitute placeholders with brief-derived content
   - Insert formatted blocks (tables, code, lists)
   - Embed asset references where appropriate

5. **4-gate quality pipeline** (per /generate-ppt):
   - Gate 1: voice gate (per voice-tier)
   - Gate 2: brand-conformance
   - Gate 3: honest-limitations (active only for transparency-note variant)
   - Gate 4: provenance record

6. **On all 4 PASS:** move from `~/.lintel/draft/` → `--out` path.

## Report format

```
Generate Word: case-analysis-ai-transparency-note

Target: transparency-note
Template: transparency-note.docx (~/.lintel/brand/word-templates/, brand version 2026-Q2)
Voice tier: internal (pack-resolved)

## Structure (from brief)
- Overview: 1 paragraph
- Capabilities: 6 items
- Limitations: 7 items (ratio 7/6 — honest ✓)
- Data inventory: 4 categories
- Decision impact: medium (informational with human-in-loop)
- Appeals + feedback: documented

## Generation (docx-templater)
  Produced ~/.lintel/draft/case-analysis-ai-transparency-note.docx (47 KB)

## 4-Gate pipeline
  Gate 1 (voice):   ✓ PASS — score 88/100
  Gate 2 (brand):   ✓ PASS — template + heading styles + footer per brand 2026-Q2
  Gate 3 (honest):  ✓ PASS — limitations ratio 7/6 ≥ capabilities−2
  Gate 4 (proven):  ✓ PASS — PROV-8b2c4 recorded

## Status
ALL GATES PASS. Moving from draft → ./case-analysis-ai-transparency-note.docx.

For customer distribution: confirm the recorded provenance reference PROV-8b2c4.
```

## Compliance integration

- 4-gate pipeline is the customer-bound enforcement path; the specific gates are pack-configurable (`resolve_pack_field compliance.hooks`; none by default)
- transparency-note variant invokes the honest-limitations gate (mandatory)
- Customer-data in brief → BLOCK
- Distribution gated by the active pack's deploy/release gate (if any) reading provenance + voice status

## Voice tier note

`voice: mixed`. The skill is internal; output voice depends on `--target`.

## Failure modes

- **docx-templater placeholder mismatch** (template + brief don't align) — surface diff, allow operator to align brief or pick different template
- **Honest-limitations fails** (limitations < capabilities − 2) — REJECT for transparency-note; force operator to expand limitations
- **Voice gate fails after regen** — same as /generate-ppt
- **Brand template absent** — fall back to default-word-template.json OR refuse if `--use-defaults` not set

## Examples

**Technical spec:**
```
> /generate-word --brief docs/spec/auth-rewrite.md --target technical
[Uses technical voice tier; no voice gate; brand gate active]
✓ ./auth-rewrite.docx
```

**Customer summary:**
```
> /generate-word --brief engagement-notes.md --target customer-summary --audience "Customer A finserv CISO"
[Customer-facing voice tier; full 4-gate]
✓ ./engagement-summary.docx — PROV-9a3.
```

**Transparency note:**
```
> /generate-word --brief case-analysis-design.md --target transparency-note
[Honest-limitations gate active; cross-references the active pack's impact-assessment gates if present]
✓ ./case-analysis-ai-transparency-note.docx — PROV-8b2c4.
```

## See also

- `BRAND-INTEGRATION.md`
- `WordTechnicalEditor` agent
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)
- `/generate-ppt`, `/generate-web`
