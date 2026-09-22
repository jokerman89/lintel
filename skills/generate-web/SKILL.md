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

The [shared design contract](../design-dna/references/design-contract.md) is the
only input/argument/profile boundary. Template paths must be explicitly authorized;
their historic home convention does not permit personal-directory discovery.

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
- Required explicit `--out <path>` for owned output; optional `--customer-share`
  is propagated from the director. Reject conflicting input modes, unknown or
  duplicate options; direct `--brief` remains an entry point into the same contract.

## From-pipeline mode (v3.5 Phase 2 — generate-pipeline integration)

If invoked with `--from-pipeline <run-dir>` instead of `--brief`:

1. **Read shared pipeline-output:**
   - `<run-dir>/content.md` — hero + sections + body with HTML-comment annotations
   - `<run-dir>/design-spec.json` — read `per_format.web.sections` for layout-mappings
   - Validate its existing envelope plus resolved `web_design`/`binding` through
     `design_contract.load_design`. Preserve legacy readability, not fabricated
     render readiness. Keep P12's document mappings intact.

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

2. **Shared handshake:** use `design_contract.load_design` with the external
   prepared P05 context and explicit P07 configuration, then `renderer_args`.
   Checking two JSON strings alone does not validate bindings, choices or policy.

3. **Replace brief-parsing logic** with direct-read of spec:
   - Hero copy: synthesize from `visual_thesis` + brand-context
   - Typography: emit `<link>` tags from `typography.font_stacks[].loading_strategy` + apply via Tailwind config
   - Motion: `none` emits no animation dependency; `css` emits only selected CSS;
     `library` imports only the selected, sourced library and justified configuration.
   - Shader: if `shader != null` → emit Paper Shaders component or OGL canvas-mount
   - Component libraries: preserve existing primitives; emit no setup/import when
     the selected list is empty. New library advice requires source/version/license evidence.
   - Layout: apply `layout_grammar.max_width` + grid-config to root layout
   - Interaction: emit Lenis init if `interaction_signature.scroll_smoothing`

4. **Design-pass hook integration:**
   - WebExperienceCritic agent runs on produced HTML/JSX (existing pattern)
   - DesignSystemAuditor agent (Phase A2) optional post-gen audit if `--review` flag set

5. **CLI stays backward-compat:** existing `--brief` + `--from-pipeline`-flag invocations work unchanged. `--from-frontend-design` is an additive third mode.

6. **prefers-reduced-motion handling** — always emit fallback per `motion.perf_budget.fallback_for_prefers_reduced_motion` field. Non-negotiable.

7. **Mobile-strategy emission** — apply the selected strategy through the actual
   CSS/library mechanism; do not introduce GSAP solely to handle a media query.

8. **4-gate pipeline runs as usual** after generation.

**Boundary with frontend-* family (L-002):** generate-web is the **rendering-engine** — file-output. frontend-design is the **design-director** — decisions. generate-web does NOT make design-decisions; it READS them from frontend-design-spec.json + renders accordingly.

## Workflow

1. **Preflight gates** — brand templates check, staleness, the active pack's compliance gates if customer-bound

2. **Read brief + parse structure:**
   - Hero (title + subtitle + CTA)
   - 2-4 substantive sections
   - Optional: features grid, FAQ, footer
   Resolve direct brief input into the same frontend contract, pinning the existing
   project/profile and retrieval evidence before rendering. No parallel private
   schema for this entry point.

3. **Invoke `WebExperienceCritic` agent** for layout review BEFORE generation:
   - Information hierarchy
   - Accessibility (WCAG AA via existing AccessibilityChecker)
   - Motion-language considerations
   - Brand alignment

3b. **Stack-guidance pass (ADR-0015 — retrieval before rendering):**
   ```bash
   python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/search.py" "<layout/feature keywords>" --stack html-tailwind   # or nextjs per variant
   ```
   Apply the returned Do/Don't/Severity rules during generation. python3 absent → Read
   `design-dna/data/stacks/<stack>.csv` (same root) directly.

4. **Generate per variant:**
   - **single-file:** populate `~/.lintel/brand/web-templates/landing-single-file.html` (or default)
   - **nextjs-scaffold:** copy `~/.lintel/brand/web-templates/demo-site/` skeleton, write src/app/page.tsx + components, generate package.json

5. **Gate 0 + 4-gate quality pipeline** (per /generate-ppt):
   - Gate 0 (mechanical, ADR-0015): `python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/validate_design.py" <out>.html --profile <active-profile>` — exit 1 BLOCKS (zoom-disable, killed focus, emoji icons, off-palette drift). Fix and re-run; never ship over a red gate.
   - Gate 1: voice (if customer-bound)
   - Gate 2: brand-conformance
   - Gate 3: honest-limitations (only if generating an AI-feature page with disclosure)
   - Gate 4: provenance

6. **On pass:** move from draft → `--out`

7. **Optional preview** through the shared browser operations on an authorized owned
   local server. Verify health and actual session ownership first; provider availability
   and URL admission are not established by this instruction.

## Report format

```
Generate Web: legal-assistant-demo

Variant: single-file
Template: landing-single-file.html (~/.lintel/brand/web-templates/, brand 2026-Q2)
Theme: pack-default
Voice tier: internal (pack-resolved)

## Structure (from brief)
  Hero: "Every contract, answered in seconds"
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
  Produced ~/.lintel/draft/legal-assistant-demo.html (87 KB)
  6 SVGs embedded from the active pack's asset library

## 4-Gate pipeline
  Gate 1 (voice):   ✓ PASS — score 86/100
  Gate 2 (brand):   ✓ PASS — pack palette + assets from brand 2026-Q2
  Gate 3 (honest):  N/A — no AI-disclosure section in this variant
  Gate 4 (proven):  ✓ PASS — PROV-c4d5 recorded

## Status
ALL GATES PASS. Moving from draft → ./legal-assistant-demo.html.

Preview: /open-managed-browser file://~/.lintel/draft/legal-assistant-demo.html
```

## Compliance integration

- 4-gate pipeline is the customer-bound enforcement path; the specific gates are pack-configurable (`resolve_pack_field compliance.hooks`; none by default)
- HTML/JS output sanitized — no inline scripts that fetch external resources without disclosure
- nextjs-scaffold pre-wires the active pack's deploy gate (if any)

## Failure modes

- **nextjs-scaffold template incomplete** — block that requested target with the
  concrete missing resource; do not silently change the requested artifact.
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
[Generates ./legal-assistant/ with package.json + src/]
Run: cd legal-assistant && npm install && npm run dev
```

## See also

- `BRAND-INTEGRATION.md`
- `WebExperienceCritic` agent
- `AccessibilityChecker` (Layer 4) for WCAG audit
- `/open-managed-browser` — open the generated file
- The active pack's deploy gate — wire Next.js deployment (pack-configurable)
