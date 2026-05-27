---
name: jstack-generate-web
description: Produce brand-compliant static HTML or Next.js scaffold for demo/landing page.
color: green
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
      - capability: Browser
        strategy: degraded-output
license_note: produces customer-bound output if --variant=customer-demo
---

# /generate-web

Brand-compliant web artifact generation. Two variants:

- **`single-file`** — self-contained HTML (Lovable-style aesthetic; one file, inline CSS, optional inline JS)
- **`nextjs-scaffold`** — multi-file Next.js project (real demo with routes, components, deploy-ready)

Uses native HTML / Next.js templates from `~/.jstack/brand/web-templates/` or in-repo defaults.

## When to use

- Customer-demo landing page (single-file for quick iteration; Next.js for deployable demo)
- Engagement-internal microsite (technical wiki, runbook viewer)
- Pitch artifact that needs to look modern + carry MS brand

## When NOT to use

- Static markdown — direct edit is faster
- Complex web app — Next.js scaffold is starter, not full product
- Slide artifact — use `/generate-ppt`

## Inputs

- Required `--brief <path|inline>` — content brief
- Required `--variant <single-file|nextjs-scaffold>` — output shape
- Optional `--audience <text>` — primary audience
- Optional `--use-defaults` — force in-repo default templates
- Optional `--preview` — after generation, open in `/open-managed-browser`
- Optional `--azure-theme` — apply Azure-specific palette (vs neutral defaults)

## Workflow

1. **Preflight gates** — brand templates check, staleness, voice/T0 if customer-bound

2. **Read brief + parse structure:**
   - Hero (title + subtitle + CTA)
   - 2-4 substantive sections
   - Optional: features grid, FAQ, footer

3. **Invoke `WebExperienceCritic` agent** for layout review BEFORE generation:
   - Information hierarchy
   - Accessibility (WCAG AA via existing AccessibilityChecker)
   - Motion-language considerations
   - Brand alignment

4. **Generate per variant:**
   - **single-file:** populate `~/.jstack/brand/web-templates/landing-single-file.html` (or default)
   - **nextjs-scaffold:** copy `~/.jstack/brand/web-templates/demo-site/` skeleton, write src/app/page.tsx + components, generate package.json

5. **4-gate quality pipeline** (per /generate-ppt):
   - Gate 1: voice (if customer-bound)
   - Gate 2: brand-conformance
   - Gate 3: honest-limitations (only if generating an AI-feature page with disclosure)
   - Gate 4: provenance

6. **On pass:** move from draft → `--out`

7. **Optional preview** via `/open-managed-browser file://...` (single-file) or instructions to `npm run dev` (Next.js)

## Report format

```
Generate Web: copilot-for-legal-demo

Variant: single-file
Template: landing-single-file.html (~/.jstack/brand/web-templates/, brand 2026-Q2)
Azure theme: enabled
Voice tier: trailblazer-draft

## Structure (from brief)
  Hero: "Lex Sweden gets a copilot"
    CTA: "Book the demo"
  Section 1: What changes for the lawyer
  Section 2: Where the AI helps + where it stops
  Section 3: How we got here (engagement timeline)

## Pre-gen review (WebExperienceCritic)
  Information hierarchy: clear ✓
  Accessibility: WCAG AA (contrast verified) ✓
  Motion: prefers-reduced-motion respected ✓
  Brand: Azure palette applied ✓

## Generation
  Produced ~/.jstack/draft/copilot-for-legal-demo.html (87 KB)
  6 Azure SVGs embedded via /asset-search

## 4-Gate pipeline
  Gate 1 (voice):   ✓ PASS — score 86/100
  Gate 2 (brand):   ✓ PASS — Azure palette + assets from brand 2026-Q2
  Gate 3 (honest):  N/A — no AI-disclosure section in this variant
  Gate 4 (proven):  ✓ PASS — PROV-c4d5 recorded

## Status
ALL GATES PASS. Moving from draft → ./copilot-for-legal-demo.html.

Preview: /open-managed-browser file:///c/Users/jokerman/.jstack/draft/copilot-for-legal-demo.html
```

## Compliance integration

- 4-gate pipeline IS Layer 2 SDL enforcement for customer-bound output
- HTML/JS output sanitized — no inline scripts that fetch external resources without disclosure
- nextjs-scaffold pre-wires deploy gate via `/setup-ev2-targets` reference

## Voice tier note

`voice: mixed`.

## Failure modes

- **nextjs-scaffold template incomplete** — fall back to single-file variant + warn
- **Voice gate fails on trailblazer-draft content** — surface flagged paragraphs, allow regen
- **Accessibility audit fails** (contrast issue, missing alt text) — surface findings; require fixes before gate-2 passes
- **Customer-data in brief** — BLOCK

## Examples

**Single-file customer demo:**
```
> /generate-web --brief demo-brief.md --variant single-file --azure-theme --preview
[Generates HTML, opens in /open-managed-browser]
```

**Next.js scaffold:**
```
> /generate-web --brief microsite-brief.md --variant nextjs-scaffold --use-defaults
[Generates ./copilot-for-legal/ with package.json + src/]
Run: cd copilot-for-legal && npm install && npm run dev
```

## See also

- `BRAND-INTEGRATION.md`
- `WebExperienceCritic` agent
- `AccessibilityChecker` (Layer 4) for WCAG audit
- `/asset-search`, `/open-managed-browser`, `/provenance-track`
- `/setup-ev2-targets` — wire Next.js deploy gate
