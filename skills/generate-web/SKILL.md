---
name: generate-web
layer: foundation
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

Uses native HTML / Next.js templates from `~/.lintel/brand/web-templates/` or in-repo defaults.

## When to use

- Customer-demo landing page (single-file for quick iteration; Next.js for deployable demo)
- Engagement-internal microsite (technical wiki, runbook viewer)
- Pitch artifact that needs to look modern + carry the active pack's brand

## When NOT to use

- Static markdown — direct edit is faster
- Complex web app — Next.js scaffold is starter, not full product
- Slide artifact — use `/generate-ppt`

## Inputs

- Required `--brief <path|inline>` — content brief **OR** `--from-pipeline <dir>` (Phase 2: shared pipeline mode) **OR** `--from-frontend-design <dir>` (v3.7 Phase B: frontend-design family integration)
- Required `--variant <single-file|nextjs-scaffold>` — output shape
- Optional `--audience <text>` — primary audience
- Optional `--use-defaults` — force in-repo default templates
- Optional `--preview` — after generation, open in `/open-managed-browser`
- Optional `--theme <name>` — apply a pack-provided theme palette (default: neutral)

## From-pipeline mode (v3.5 Phase 2 — generate-pipeline integration)

If invoked with `--from-pipeline <run-dir>` instead of `--brief`:

1. **Read shared pipeline-output:**
   - `<run-dir>/content.md` — hero + sections + body with HTML-comment annotations
   - `<run-dir>/design-spec.json` — read `per_format.web.sections` for layout-mappings

2. **Replace brief-parsing logic** with direct-read of content.md sections + design-spec web-block-types (hero / sections / features / FAQ).

3. **Apply format-specific design-pass via design_pass_hook:**
   - Reads `per_format.web.sections[N].design_pass_hook` (canonical: WebExperienceCritic)
   - Invokes agent for a web-specific fidelity-pass (information-hierarchy, accessibility, motion-language)
   - Per Reviewer Concern #7: WebExperienceCritic stays web-specific, not lifted

4. **CLI stays backward-compat:** existing `--brief`-flag invocations work unchanged. `--from-pipeline` is additive.

5. **4-gate pipeline runs as usual** after generation.

## From-frontend-design mode (v3.7 Phase B — frontend-* family integration, M-1 resolution)

If invoked with `--from-frontend-design <run-dir>` instead of `--brief` or `--from-pipeline`:

1. **Read frontend-design output:**
   - `<run-dir>/frontend-design-spec.json` — **distinct filename** from pipeline's `design-spec.json` (M-1 resolution per /plan-eng-review — avoids schema collision). Verify `"source": "frontend-design"` + `"schema_version": 1` before consuming.
   - Embedded blocks: `typography` (font-stacks + variable-axes + size-scale) + `motion` (libraries + scroll-trigger-config + key-animations + perf-budget) + `shader` (om present; nullable) + `component_libraries` (shadcn + Aceternity etc) + `layout_grammar` (max-width + grid + breakpoints) + `interaction_signature` (scroll-smoothing + hover-intent + page-transitions) + `visual_thesis` (one-paragraph)

2. **Schema-version handshake:**
   ```bash
   spec="<run-dir>/frontend-design-spec.json"
   sv=$(jq -r '.schema_version' "$spec")
   source=$(jq -r '.source' "$spec")
   [ "$sv" = "1" ] || { echo "Unsupported schema_version: $sv (this skill reads v1)"; exit 1; }
   [ "$source" = "frontend-design" ] || { echo "Wrong source: $source (expected frontend-design)"; exit 1; }
   ```

3. **Replace brief-parsing logic** with direct-read of spec:
   - Hero copy: synthesize from `visual_thesis` + brand-context
   - Typography: emit `<link>` tags from `typography.font_stacks[].loading_strategy` + apply via Tailwind config
   - Motion: emit GSAP/Lenis import snippets from `motion.libraries[]` + scroll-trigger setup from `motion.scroll_trigger_config` + key-animations from `motion.key_animations[]`
   - Shader: if `shader != null` → emit Paper Shaders component or OGL canvas-mount
   - Component-libraries: emit shadcn-init command + Aceternity copy-paste-references in operator-instructions
   - Layout: apply `layout_grammar.max_width` + grid-config to root layout
   - Interaction: emit Lenis init if `interaction_signature.scroll_smoothing`

4. **Design-pass hook integration:**
   - WebExperienceCritic agent runs on produced HTML/JSX (existing pattern)
   - DesignSystemAuditor agent (Phase A2) optional post-gen audit if `--review` flag set

5. **CLI stays backward-compat:** existing `--brief` + `--from-pipeline`-flag invocations work unchanged. `--from-frontend-design` is an additive third mode.

6. **prefers-reduced-motion handling** — always emit fallback per `motion.perf_budget.fallback_for_prefers_reduced_motion` field. Non-negotiable.

7. **Mobile-strategy emission** — read `motion.perf_budget.mobile_strategy` + apply via `gsap.matchMedia()` conditional logic in generated code.

8. **4-gate pipeline runs as usual** after generation.

**Boundary with frontend-* family (L-002):** generate-web is the **rendering-engine** — file-output. frontend-design is the **design-director** — decisions. generate-web does NOT make design-decisions; it READS them from frontend-design-spec.json + renders accordingly.

## Workflow

1. **Preflight gates** — brand templates check, staleness, the active pack's compliance gates if customer-bound

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
   - **single-file:** populate `~/.lintel/brand/web-templates/landing-single-file.html` (or default)
   - **nextjs-scaffold:** copy `~/.lintel/brand/web-templates/demo-site/` skeleton, write src/app/page.tsx + components, generate package.json

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
Template: landing-single-file.html (~/.lintel/brand/web-templates/, brand 2026-Q2)
Theme: pack-default
Voice tier: internal (pack-resolved)

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
  Brand: pack palette applied ✓

## Generation
  Produced ~/.lintel/draft/copilot-for-legal-demo.html (87 KB)
  6 SVGs embedded from the active pack's asset library

## 4-Gate pipeline
  Gate 1 (voice):   ✓ PASS — score 86/100
  Gate 2 (brand):   ✓ PASS — pack palette + assets from brand 2026-Q2
  Gate 3 (honest):  N/A — no AI-disclosure section in this variant
  Gate 4 (proven):  ✓ PASS — PROV-c4d5 recorded

## Status
ALL GATES PASS. Moving from draft → ./copilot-for-legal-demo.html.

Preview: /open-managed-browser file://~/.lintel/draft/copilot-for-legal-demo.html
```

## Compliance integration

- 4-gate pipeline is the customer-bound enforcement path; the specific gates are pack-configurable (`resolve_pack_field compliance.hooks`; none by default)
- HTML/JS output sanitized — no inline scripts that fetch external resources without disclosure
- nextjs-scaffold pre-wires the active pack's deploy gate (if any)

## Voice tier note

`voice: mixed`.

## Failure modes

- **nextjs-scaffold template incomplete** — fall back to single-file variant + warn
- **Voice gate fails on customer-facing content** — surface flagged paragraphs, allow regen
- **Accessibility audit fails** (contrast issue, missing alt text) — surface findings; require fixes before gate-2 passes
- **Customer-data in brief** — BLOCK

## Examples

**Single-file customer demo:**
```
> /generate-web --brief demo-brief.md --variant single-file --theme pack-default --preview
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
- `/open-managed-browser` — open the generated file
- The active pack's deploy gate — wire Next.js deployment (pack-configurable)
