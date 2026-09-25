---
name: frontend-design-review
layer: foundation
description: Use to review built UI or produced frontend designs with actual route/viewport evidence, six canonical advisory dimensions and the existing required-control contract.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

You are the `frontend-design-review` skill for produced designs and built UI.

For `--url`, routes, viewports and changed-file context, follow the
[built review procedure](references/built-review.md). It retains visual polish,
accessibility, motion, copy, layout/density and brand critique while using this
same `design-review.json` contract. No retired review entrypoint is required.

## What this skill does

Reads a produced frontend artifact (HTML file, Next.js project, screenshots, or live URL) → DesignSystemAuditor agent runs **6-dimension audit** with explicit scoring rubric → writes `design-review.json` with per-dimension scores (0-100) + verdict (green/yellow/red) per dimension + overall verdict.

Solo-invokable for audit or chained from `/li:frontend-design` Workflow Step 7 (if enabled).

**Retained advisory scoring rubric:**
- Per dimension: **≥80 = green**, **60-79 = yellow**, **<60 = red**
- Overall verdict: ALL dimensions green → GREEN. Any red → RED. Otherwise YELLOW.
- Scores are advisory; applicable mandatory P05 fail/error/unverified results
  block regardless of score. A requested aesthetic threshold is an explicit
  requirement, not a substitute for observed controls.

Use the [shared design contract](../design-dna/references/design-contract.md) for
the six canonical keys, aliases, profile verification and P05 review input. Do not
copy its parser or use a separate score-only clearance path.

L-001-discipline: skill body is the contract (the 6 dimensions). Agent at invocation does the actual scoring against the produced artifact. Don't pre-bake what "good" looks like.

## When to use

- Pre-customer-share artifact-validation
- Auto-invoked by `/li:frontend-design` Workflow Step 7 (if not skipped)
- Standalone audit of operator-built site
- Diff-mode: compare produced output vs vault baseline

## When NOT to use

- Pre-implementation review (no artifact to score yet) — use `/inspect --target plan --lens design` instead
- A/B test scoring (different bar) — out of scope for this skill
- Purely typographic-only review — use `/li:frontend-typography` direct

## Inputs

- Required `<artifact>` or `--url <url>` — HTML file, project directory, screenshot or live URL; reject conflicting selections
- Optional `--baseline <pattern>` — compare against an explicitly selected project/pack pattern
- Optional `--dimensions <comma-list>` — subset audit (default: all 6)
- Optional `--out <path>` — output path (default: `<artifact-dir>/design-review.json`)
- Optional `--customer-share` — strict-mode: yellow → BLOCKED
- Optional `--include-screenshots` — capture through an actual authorized `web-session` provider
- Built-UI inputs: `--url`, `--routes`, `--viewport`, `--baseline-ref` and
  `--include-copy-pillar`; see the linked procedure. A Git baseline reference
  and a design-pattern baseline are distinct inputs, never guessed from one flag.

## Workflow

### Step 1 — Parse + validate artifact

```bash
artifact="${URL:-${1:-}}"
baseline="${BASELINE:-}"
dimensions="${DIMENSIONS:-all}"
customer_share="${CUSTOMER_SHARE:-}"

[ -z "$artifact" ] && { echo "Usage: /li:frontend-design-review <artifact>"; exit 2; }

# Detect artifact type
if [[ "$artifact" =~ ^https?:// ]]; then
  artifact_type="url"
elif [ -d "$artifact" ]; then
  artifact_type="project-dir"
elif [[ "$artifact" =~ \.(html|htm)$ ]]; then
  artifact_type="single-html"
elif [[ "$artifact" =~ \.(png|jpg|jpeg|webp)$ ]]; then
  artifact_type="screenshot"
else
  echo "Unknown artifact type: $artifact"; exit 2
fi
```

### Step 1.5 — Mechanical validator pre-pass (ADR-0015)

Before any agent judgment, run the cheap hard gate on HTML artifacts:

When the artifact has a selected design, reload it through `design_contract.load_design`. Feed its
resolved palette (including explicit brief overrides) to the existing
`validate_design.check(content, path, profile_hexes)` API, or use the standalone
CLI with the explicit verified profile asset path. Do not reconstruct a bundled
profile path by name when P07 selected a pack-owned asset. Static validation
retains its actual error/warning scope and is not browser evidence.
For a standalone built surface without a design spec, use the explicitly verified
project/profile tokens and actual artifact as the review inputs. Do not invent a
design envelope merely to review an operator-built page. The same canonical
advisory dimension keys remain available through `validate_review`.

Exit 1 → the run is **RED** regardless of dimension scores (hard findings include
zoom-disable, killed focus and emoji icons; off-palette/token checks are warnings). Surface the validator output as
findings; the 6-dimension audit still runs so the operator gets the full picture. python3 absent
→ the agent checks the design-dna non-negotiables list manually as part of dimension 4.

### Step 2 — DesignSystemAuditor agent dispatch

Use the `agents/frontend/DesignSystemAuditor.md` method with the artifact, selected
baseline, dimension list and verified design profile. Delegate only through an
available authorized native operation. Otherwise label the pass as self-review;
the independent review requirement remains open. A role file is not a tool call.

### Step 3 — Run 6-dimension audit

**Dimension 1: Typography hierarchy (0-100)**
- Heading scale-ratio applied consistently (1.25/1.333/1.618)
- Line-height bands: tight for display, normal for body, relaxed for long-form
- Letter-spacing applied at scale (tight for large, wide for small uppercase)
- Font-loading: preload critical, swap-strategy declared
- Variable-axes used (if font supports)
- **Red flags (subtract):** heading-soup (>4 size-levels in fold), font-loading FOIT >100ms, no fallback-stack

**Dimension 2: Motion coherence (0-100)**
- Single motion-language thesis (not GSAP-here, Framer-Motion-there for same role)
- Scroll-trigger animations respect viewport budgets (no >5 concurrent scroll-tracked anims)
- prefers-reduced-motion fallback present + tested
- Mobile-strategy declared + visibly differentiated
- **Red flags:** scroll-jank >16ms, no prefers-reduced-motion fallback, mixed-library overlap

**Dimension 3: Shader perf-budget (0-100)**
- WebGL initialization gated by viewport-intersection
- Fragment-shader complexity within mid-tier-mobile budget
- Fallback for no-WebGL contexts
- IntersectionObserver pause for off-screen
- **Red flags:** fps drops below 30 on mid-tier mobile, no fallback, WebGL crashes leak

**Dimension 4: Accessibility WCAG AA (0-100)**
- Color-contrast ≥4.5:1 for normal text, ≥3:1 for large text
- All interactive elements keyboard-reachable
- Focus-rings visible + meet contrast
- Aria-labels on icon-buttons
- prefers-reduced-motion + prefers-color-scheme respected
- **Red flags:** normal-text contrast <4.5:1 or large-text contrast <3:1, no keyboard nav, focus-rings stripped without replacement

**Dimension 5: Brand conformance (0-100)**
- Palette tokens match the verified profile and selected brief overrides
- Logo placement matches brand guidelines
- Typography family matches brand spec (if operator-licensed)
- Voice-tier compliance (internal vs customer-share copy)
- **Red flags:** off-palette colors >20% of accents, logo missing or misused, voice-tier mismatch

**Dimension 6: Responsive fidelity (0-100)**
- Breakpoints: mobile (<640px), tablet (640-1024px), desktop (>1024px) all valid
- Container queries used where component-context varies
- Touch-targets ≥44px on mobile
- Hero scales appropriately (no horizontal scroll, no clipped content)
- Mobile-motion-strategy applied
- **Red flags:** horizontal scroll on mobile, touch-targets <32px, hero broken on iPhone-SE

### Step 4 — Compute scores + verdict

Call `design_contract.validate_review` for advisory feedback. The only emitted keys
are `typography_hierarchy`, `motion_coherence`, `shader_perf_budget`,
`accessibility_wcag`, `brand_conformance`, `responsive_fidelity`. Map short CLI
aliases once through `normalize_dimensions`; reject unknown/duplicate keys and
missing members of the selected subset. Never read different short keys from the
JSON output. A null score retains unverified/unscored advice, not a synthetic 100.

### Step 5 — Customer-share strict gate

For a design-bound artifact, run the shared helper's `review` operation with the selected design, external P05
context/QA and the same explicit P07 configuration as rendering. It verifies
current input bytes/profile and every original required observation. A dimension
subset or none/CSS/no-shader choice cannot drop keyboard, contrast or other controls.
Ground N/A applicability through P05; never award an artificial score to clear it.
Actual browser absence remains unverified for keyboard/focus, responsive behavior,
reduced-motion and performance measurements. Independent review still follows the
existing P05 protocol; this advisory helper reports `release_clearance: false`.
For standalone built UI without a selected design, retain its actual source,
captures, profile and obligations through P05's existing standalone snapshot/
inspect route (or the already selected mapped context). Do not call the
design-bound helper with an invented spec or claim independent clearance from
standalone inspection. Required observations remain mandatory in either route.

### Step 6 — Output report

```
FRONTEND DESIGN REVIEW — <artifact>
══════════════════════════════════════════════════════════════════

Overall verdict:    <GREEN | YELLOW | RED>

Per-dimension:
  Typography hierarchy:   <score>/100  <verdict>
  Motion coherence:       <score>/100  <verdict>
  Shader perf-budget:     <score>/100  <verdict>
  Accessibility (WCAG):   <score>/100  <verdict>
  Brand conformance:      <score>/100  <verdict>
  Responsive fidelity:    <score>/100  <verdict>

Top findings (yellow + red):
  • <dimension>: <finding>
  • <dimension>: <finding>

Recommendation:
  GREEN  → advisory only; mandatory controls and independent review still apply
  YELLOW → address findings before customer-share
  RED    → BLOCKED for customer-share; must fix before re-review

Full report: $out
```

## Schema

`design-review.json`:

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "artifact": "<path or URL>",
  "artifact_type": "url | project-dir | single-html | screenshot",
  "baseline_compared": "<vault-name or null>",
  "overall_verdict": "green | yellow | red",
  "dimensions": {
    "typography_hierarchy": {
      "name": "Typography hierarchy",
      "score": 85,
      "verdict": "green",
      "findings": ["heading-scale 1.25 applied consistently", "preload tag missing for Fraunces"]
    },
    "motion_coherence": { "name": "Motion coherence", "score": 70, "verdict": "yellow", "findings": [...] },
    "shader_perf_budget": { ... },
    "accessibility_wcag": { ... },
    "brand_conformance": { ... },
    "responsive_fidelity": { ... }
  },
  "customer_share_strict": false
}
```

## Status protocol

- **DONE** — selected feedback and required observations are complete; report
  their actual result separately from independent delivery acceptance
- **DONE_WITH_CONCERNS** — review complete, overall yellow (non-customer-share)
- **BLOCKED** — review red, OR customer-share strict-mode with yellow/red
- **NEEDS_CONTEXT** — artifact unreadable, OR dimension-list invalid

## Pause-points

- Applicable mandatory failure/error/unverified: BLOCKED; a style-score override
  cannot waive the underlying control.
- Red dimension: hard-block for customer-share regardless of overall

## Integration

**Reads:**
- `<artifact>` (URL, file, dir, screenshot)
- Explicit selected design-pattern baseline (if --baseline)
- Current resolved palette/profile asset (for brand-conformance dimension)

**Writes:**
- `<artifact-dir>/design-review.json` (or $OUT-path)
- Audit-log: `.claude/runtime/audit/frontend-design-review-runs.jsonl`

**Calls into:**
- `agents/frontend/DesignSystemAuditor.md` (primary)
- `/li:compliance-gate` (if --customer-share + red dimension)

**Consumed by:**
- `/li:frontend-design` Workflow Step 7 (Phase A2-onwards integration)
- Operator standalone audit
- Pre-customer-share gate-check

## Anti-patterns

- **Scoring without rubric** — pre-A2 design-doc concern #3. Skill body documents rubric explicitly.
- **Treating all dimensions equal-weight** — accessibility + brand-conformance are gating for customer-share. Don't average them in.
- **Ignoring an explicitly selected baseline** — retain that comparison or
  report the missing input; do not discover personal patterns automatically.
- **Producing review.json without `schema_version`** — M-5 compliance.

## Failure recovery

- Artifact unreadable: BLOCKED with diagnostic ("file not found", "URL 404", "directory not a project")
- Headless-browser screenshot fails: degrade to static-audit + flag in review
- Explicit baseline missing: block that comparison and report the missing input

## Recommended next steps after invocation

- GREEN → inspect mandatory controls and obtain actual independent clearance
- YELLOW → address findings + re-run review
- RED → hard-block + investigate per-dimension findings
- Use design-review.json as input to `/li:pause` for session-handoff
