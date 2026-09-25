---
name: generate-web
layer: foundation
description: Use to render a static HTML mockup, a profile-aware single-file page or a Next.js scaffold from a brief or the existing design/content contracts.
color: green
tools: Read, Write, Bash, Glob
voice: mixed
cli_support: [claude-code, codex, copilot]
license_note: produces customer-bound output when explicitly requested
---

# /generate-web

Web artifact generation with `--mode artifact|mockup`; default `artifact`
preserves the existing brief/pipeline/frontend-design routes below.

- **Mockup mode:** follow the [mockup procedure](references/mockup.md) for
  `--brief`, `--reference`, `--tokens`, `--inherit-project`, `--copy-tier`,
  `--out` and optional `--preview`. It implies `single-file`: actual static HTML,
  inline CSS/minimal JS, no framework or build step.
- **Artifact variants:** `single-file` is self-contained HTML; `nextjs-scaffold`
  is a multi-file project with routes and components, not a deployment.

Use only explicitly selected or verified-profile templates and available project
resources. A named template is not proof a bundled skeleton exists.

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
- Required `--variant <single-file|nextjs-scaffold>` in artifact mode; mockup implies single-file
- Optional `--audience <text>` — primary audience
- Optional `--use-defaults` — force in-repo default templates
- Optional `--preview` — after generation, use `/web-session --mode open` on an owned admitted preview
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
   - `<run-dir>/frontend-design-spec.json` — **distinct filename** from pipeline's `design-spec.json`, avoiding a schema collision. Verify `"source": "frontend-design"` + `"schema_version": 1` before consuming.
   - Embedded blocks: `typography`, `motion`, nullable `shader`, `component_libraries`, `layout_grammar`, `interaction_signature` and `visual_thesis`.

2. **Shared handshake:** use `design_contract.load_design` with the external
   prepared P05 context and explicit P07 configuration, then `renderer_args`.
   Checking two JSON strings alone does not validate bindings, choices or policy.

3. **Replace brief-parsing logic** with direct-read of spec:
   - Copy: preserve the bound brief/content; a visual thesis is design direction,
     not a replacement for substantive source text, tables or limitations
   - Typography: honor `typography.font_stacks[].loading_strategy` through the
     existing target's CSS/config; fetch or link external assets only when authorized
   - Motion: `none` emits no animation dependency; `css` emits only selected CSS;
     `library` imports only the selected, sourced library and justified configuration.
   - Shader: emit a selected GPU component only when
     `shader != null && shader.visual_thesis != "none" && shader.library != null`.
     Both null and the accepted non-null `visual_thesis: none, library: null`
     representation emit no GPU canvas, import or dependency. Apply the same
     predicate to pipeline `web_design.shader`; do not substitute an artificial score.
   - Component libraries: preserve existing primitives; emit no setup/import when
     the selected list is empty. New library advice requires source/version/license evidence.
   - Layout: apply `layout_grammar.max_width` + grid-config to root layout
   - Interaction: apply selected smoothing only through its explicitly chosen
     library/stack; native scrolling emits no smoothing dependency

4. **Design-pass hook integration:**
   - WebExperienceCritic agent runs on produced HTML/JSX (existing pattern)
   - `frontend-design-review` consumes actual output and the original required
     observations; an optional review request cannot waive a mandatory control

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
   - All substantive sections, preserving source detail rather than a fixed section cap
   - Optional: features grid, FAQ, footer
   Resolve direct brief input into the same frontend contract, pinning the existing
   project/profile and retrieval evidence before rendering. No parallel private
   schema for this entry point.

3. **Apply the `WebExperienceCritic` method** for layout review BEFORE generation:
   - Information hierarchy
   - Accessibility (WCAG AA via existing AccessibilityChecker)
   - Motion-language considerations
   - Brand alignment

   Use actual native delegation when available and authorized; otherwise label
   the builder's pass as self-review. No actor or model is implied by this recipe.

3b. **Stack-guidance pass (ADR-0015 — retrieval before rendering):**
   ```bash
   python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/search.py" "<layout/feature keywords>" --stack html-tailwind   # or nextjs per variant
   ```
   Apply the returned Do/Don't/Severity rules during generation. python3 absent → Read
   `design-dna/data/stacks/<stack>.csv` (same root) directly.

4. **Generate per variant:**
   - **single-file:** render the selected design as one HTML file with inline
     CSS and only necessary authorized interactions
   - **nextjs-scaffold:** use a selected compatible skeleton or the established
     project structure; write routes/components and only justified manifest changes

5. **Gate 0 + 4-gate quality pipeline** (per /generate-ppt):
   - Gate 0 (mechanical, ADR-0015): use the
     [design validator](../design-dna/scripts/validate_design.py),
     `validate_design.check(content, path,
     profile_hexes)` on actual HTML with the loaded design's resolved palette.
     Hard errors such as zoom-disable, killed focus and emoji icons block;
     off-palette/token findings retain their warning severity. Do not reconstruct
     a bundled profile path that ignores a selected pack asset or brief override.
   - Gate 1: voice (if customer-bound)
   - Gate 2: brand-conformance
   - Gate 3: honest-limitations (only if generating an AI-feature page with disclosure)
   - Gate 4: provenance

6. **Publish within scope:** atomically write/read back the selected `--out`,
   preserving an authorized replacement's preimage. Report actual checks and
   blocked/unverified obligations; no draft move confers release clearance.

7. **Optional preview** through the shared browser operations on an authorized owned
   local server. Verify health and actual session ownership first; provider availability
   and URL admission are not established by this instruction.

## Report format

Report mode/variant, exact source/design/output paths, selected profile/template,
retained content, actual rendering operations and mechanical/voice/brand/
limitations/provenance outcomes. State whether preview, keyboard, responsive,
reduced-motion and other required observations ran, with their actual evidence.
Missing browser or renderer coverage remains unverified, not a fabricated pass.

## Compliance integration

- 4-gate pipeline is the customer-bound enforcement path; the specific gates are pack-configurable (`resolve_pack_field compliance.hooks`; none by default)
- HTML/JS output sanitized — no inline scripts that fetch external resources without disclosure
- nextjs-scaffold retains applicable deployment requirements but triggers no deployment

## Failure modes

- **nextjs-scaffold template incomplete** — block that requested target with the
  concrete missing resource; do not silently change the requested artifact.
- **Voice gate fails on customer-facing content** — surface flagged paragraphs, allow regen
- **Accessibility audit fails** (contrast issue, missing alt text) — surface findings; require fixes before gate-2 passes
- **Customer-data in brief** — BLOCK

## Examples

**Single-file customer demo:**
```
> /generate-web --brief demo-brief.md --variant single-file --out demo.html --preview
[Render; preview only through a verified owned server and authorized provider.]
```

**Next.js scaffold:**
```
> /generate-web --brief microsite-brief.md --variant nextjs-scaffold --use-defaults --out microsite
[Render a compatible scaffold; use existing tooling and authorized dependency restoration only.]
```

## See also

- `BRAND-INTEGRATION.md`
- `WebExperienceCritic` agent
- `AccessibilityChecker` (Layer 4) for WCAG audit
- `/web-session --mode open` — preview the generated file through owned loopback
- `/frontend-design --mode variants` — compare directions around a mockup
- `/generate-docs` — produce source-grounded Markdown before a format handoff
- The active pack's deploy gate — wire Next.js deployment (pack-configurable)
