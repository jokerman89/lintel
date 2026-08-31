---
name: design-consultation
layer: foundation
description: Conversational design-system advisor — answer systems-level questions with grounded recommendations.
color: purple
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /design-consultation

The advisor variant of design work. Operator asks a systems-level question ("should we add motion to the case card?", "what should the spacing scale look like?", "is our type ramp too aggressive at mobile?") and the skill returns a grounded recommendation with three alternatives + trade-offs.

Distinct from `/design-review`: that one critiques what's built. This one shapes what hasn't been built yet.

## When to use

- Designing the next feature's UI and want a systems-level second opinion before sketching
- Considering a design-token change that ripples across the app
- New surface that doesn't fit existing patterns — need a fresh-eyes recommendation
- Resolving a design disagreement between two operators with a structured comparison

## When NOT to use

- Reviewing a specific built page — use `/design-review`
- Generating actual HTML/mockup — use `/design-html`
- Plan-doc-level review — use `/plan-design-review`
- Customer-facing copy decisions — use the active pack's compliance gates + voice corpus

## Inputs

- Required: the question or proposal (inline prose or path to a markdown file)
- Optional `--scope <area>` — narrow consultation to a specific area (e.g. "portal", "landing", "case-tabs")
- Optional `--with-codex` — invoke `/codex` mid-consultation for an outside opinion
- Optional `--read-design-system <dir>` — point at the project's design-system docs (default: `.lovable/memory/style/` if present, else `.claude/engineering/design-archive/`)

## Workflow

1. **Read the question.** Extract the actual design decision being made. Restate it precisely.
2. **Read context.** Load the design-system docs from `--read-design-system`. Read closest analog patterns in the codebase via Grep.
3. **Generate three alternatives.** Concrete, named options. Not "do nothing" + "do it" — three real design moves with distinct trade-offs.
4. **Trade-off matrix.** For each alternative: cost (implementation), risk (regression surface), upside (what improves), downside (what gets worse). Mark which existing tokens/utilities apply.
5. **Recommend one.** With a one-line reason. Operator decides — recommendation is a starting point, not a verdict.
6. **Optional Codex pass.** If `--with-codex`: feed the question + three alternatives to Codex, surface its take separately.
7. **Output.** Markdown report. No code generated — that's `/design-html` territory.

## Report format

```
Design Consultation

## Question
Should /portal/cases use a card-grid or a list-table layout at desktop?

## Context read
- .lovable/memory/style/portal-design-v2.md (loaded)
- src/components/portal/Cases.tsx (current: card-grid 3-col)
- src/components/case/CaseProjectView.tsx (current: list-table for sub-items)
- 12 existing card-using components, 4 list-table-using components

## Alternatives

### A) Keep card-grid, refine spacing
- Cost: low (tweak existing tokens)
- Risk: low (no migration)
- Upside: visual rhythm consistent with Dashboard
- Downside: dense data still hard to scan; horizontal padding eats real estate
- Tokens: existing portal-card + Tailwind 3-col grid

### B) Switch to list-table
- Cost: medium (rewrite Cases.tsx, new table primitive)
- Risk: medium (table semantics, sort/filter UX expansion)
- Upside: scannability for users with 20+ cases
- Downside: breaks visual rhythm with Dashboard; mobile layout becomes a separate component
- Tokens: would need new `data-table` primitive

### C) Hybrid: card-grid at < 20 cases, list-table at ≥ 20
- Cost: high (two implementations + threshold logic)
- Risk: high (state-dependent UI is fragile)
- Upside: best of both for both user segments
- Downside: cognitive load — UI shifts under the user
- Tokens: both, plus a switch component

## Recommendation
**A) Keep card-grid, refine spacing.** Reason: data shows median user has 4 cases; the scannability problem is theoretical at current scale. Migrate to B later if median crosses ~15.

## Codex pass (optional, requested)
Codex agrees with A but pushed back on the threshold — argues ~10 not 15. Worth noting.
```

## Compliance integration

- If question references customer data (e.g. "how should we lay out a case from <real customer>"): STOP, ask operator to sanitize the question.

## Failure modes

- **No design-system docs found:** report + ask operator to point at the right path, OR offer to proceed with reduced context (mark recommendation confidence lower).
- **Question is too vague to recommend on:** restate what was asked, surface ambiguity, ask one targeted clarifying question.
- **Three alternatives can't be generated honestly:** name that — sometimes the right answer is "there are only two real options". Don't manufacture filler.
- **Codex unavailable when `--with-codex`:** continue without Codex, note the gap.

## Examples

**Spacing scale question:**
```
> /design-consultation "Should we move from 4px base to 8px base for spacing tokens?"
[Reads design-system, finds 47 components using 4px-based tokens]
Three alternatives with cost/risk/upside/downside. Recommendation: defer (cost of migration too high vs marginal rhythm gain).
```

**With Codex:**
```
> /design-consultation "Add motion to case-card hover?" --with-codex
Three options scored. Local recommendation: A (subtle 100ms ease-out).
Codex: agrees, but flags accessibility risk — recommends gating on prefers-reduced-motion.
Combined recommendation: A with motion gate.
```

## See also

- `/design-review` — review what's already built
- `/design-html` — produce a concrete mockup of the recommended option
- `/plan-design-review` — design-doc-level review
- `/codex` — outside-voice second opinion
