---
name: li-generate-ppt
layer: ms-team
description: Produce brand-compliant PowerPoint deck via pptx-genjs, 4-gate quality pipeline.
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
      - capability: Browser
        strategy: degraded-output
license_note: produces customer-bound output; requires T0 CALIBRATED status for trailblazer voice tier
---

# /generate-ppt

Produces a brand-compliant PowerPoint deck (.pptx) for customer engagements. Uses pptx-genjs under the hood. Pulls templates from `~/.lintel/brand/ppt-templates/` (or falls back to in-repo defaults if brand not pulled). Voice-gated before distribution.

Phase F of v2 build.

## When to use

- Customer-engagement deliverable (pitch deck, workshop deck, summary deck)
- Internal presentation that needs MS brand identity
- Reusing engagement-specific content across multiple PPT outputs
- Replacing manual PPT authoring with a workflow that has voice + brand + provenance gates

## When NOT to use

- One-slide quick mockup — `/design-html` is faster
- Non-PPT artifact — use `/generate-word` or `/generate-web`
- T0 not calibrated AND output is customer-bound — calibration first (see T0-CALIBRATION-WORKFLOW.md)

## Inputs

- Required `--brief <path|inline>` — content brief describing the deck purpose
- Required `--template <name>` — PPT template name from `~/.lintel/brand/ppt-templates/` (e.g. `pitch-deck`, `workshop`)
- Optional `--audience <text>` — primary audience (affects voice tier output)
- Optional `--slide-count <N>` — target slide count (default: 20-30 based on duration)
- Optional `--duration <minutes>` — presentation duration (informs slide pacing)
- Optional `--voice <internal|trailblazer-draft>` — voice tier for slide content (default: trailblazer-draft)
- Optional `--use-defaults` — force use of in-repo default templates instead of brand pull
- Optional `--ignore-stale-brand <reason>` — bypass brand-staleness-warn

## Workflow

1. **Preflight gates:**
   - `~/.lintel/brand/ppt-templates/<template>.pptx` exists OR `--use-defaults` flag present
   - brand-staleness-warn check (90-day rule) — surface warning if stale
   - T0 calibration status if `--voice trailblazer-draft` (UNCALIBRATED → output marked unverified)

2. **Read brief + extract structure:**
   - Goal / key message (one sentence)
   - Audience profile
   - 3-5 substantive sections
   - Opening hook + closing CTA

3. **Invoke `PPTNarrativeArchitect` agent** to design slide arc:
   - Slide-by-slide content goals
   - Mode tags per slide (Reveal / Inspire / Provoke / Neutral)
   - Layout suggestions per slide
   - Asset suggestions (Azure icons via `/asset-search` if Azure-relevant)

4. **Generate slides via pptx-genjs:**
   - Apply template
   - Add slides per architect's arc
   - Populate text with brief-derived content
   - Insert assets via `/asset-search` matches
   - Mode-tag in slide notes for voice-check downstream

5. **4-gate quality pipeline** (output stays in `~/.lintel/draft/` until ALL 4 PASS):

   **Gate 1 — Voice (`/rais-customer-voice-check`):**
   - Apply 12-cell Trailblazer rubric to slide text
   - Require ≥85 score, 0 P1 violations
   - PASS → continue; FAIL → surface + regenerate flagged slides (up to 2 retries)

   **Gate 2 — Brand-conformance:**
   - Template matches latest brand version (or default-fallback marker present)
   - Assets are from `~/.lintel/brand/azure-assets/` (or operator-confirmed)
   - No unauthorized branding (third-party logos)
   - Color/typography matches template tokens

   **Gate 3 — Honest-limitations:**
   - Applies to transparency-note slides ONLY
   - Limitations section ≥ capabilities − 2 (per RAIS rule)
   - Skipped for pitch/workshop decks (no transparency-note section)

   **Gate 4 — Provenance:**
   - `/provenance-track` generates record with source chain + voice score + brand version
   - Record landed in `~/.lintel/provenance/`

6. **On all 4 PASS:** move from `~/.lintel/draft/` → operator-specified `--out` path (or `<brief-stem>.pptx` in cwd).

7. **On any gate FAIL:** keep in draft, surface specific failures, allow operator iteration.

## Report format

```
Generate PPT: customer-A-arc-pitch

Template: pitch-deck.pptx (~/.lintel/brand/ppt-templates/, brand version 2026-Q2)
Brand staleness: ok (32 days)
Voice tier: trailblazer-draft
Audience: mid-market public sector IT leadership

## Slide architecture (PPTNarrativeArchitect)
  1. Opening: Reveal/Curtain — "What does Friday 2 AM actually cost?"
  2. Stakes: Provoke/Unflinching — current cost in incidents + hours
  3. Setup: Reveal/Dream — picture the unified-Arc world
  4-8. Substantive: feature surface mapped to operational pain
  9. Close: Inspire/Marvel — what becomes possible

## Generation (pptx-genjs)
  9 slides generated. 6 Azure service icons resolved via /asset-search.
  142 KB output → ~/.lintel/draft/customer-A-arc-pitch.pptx

## 4-Gate pipeline
  Gate 1 (voice):   ✓ PASS — score 87/100, 0 P1 violations
  Gate 2 (brand):   ✓ PASS — template + 6/6 assets from brand-version 2026-Q2
  Gate 3 (honest):  N/A — no transparency-note slides
  Gate 4 (proven):  ✓ PASS — PROV-7f8a2 recorded

## Status
ALL GATES PASS. Moving from draft → ./customer-A-arc-pitch.pptx.

Distribution: operator-driven. Run /provenance-track --query PROV-7f8a2 to verify chain before sending.
```

## Compliance integration

- 4-gate pipeline IS Layer 2 SDL enforcement for customer-bound output
- `/release-ev2` reads provenance + voice-check status before customer-bearing distribution
- Customer-data patterns in brief → BLOCK (Layer 2 always-on)
- Stale brand (>90d) surfaces warn but doesn't block (operator decides)

## Voice tier note

`voice: mixed`. Skill itself is engineering-internal; the SLIDE CONTENT may be trailblazer-draft (gated by Gate 1).

## Failure modes

- **pptx-genjs runtime error** (lib bug, malformed template) — surface error, keep work-in-progress in `~/.lintel/draft/.work/`, allow operator manual debug
- **Brand template missing AND --use-defaults not set** — surface options: pull brand, use defaults, abort
- **Voice gate fails after 2 regen attempts** — keep draft, surface specific slide failures with fix recommendations
- **Asset search returns 0 results for slide concept** — surface to operator, allow them to provide path manually OR skip the asset for that slide
- **Customer-data in brief** — BLOCK before generation. Sanitize first.

## Examples

**Standard pitch deck:**
```
> /generate-ppt --brief docs/engagement/customer-A-pitch-brief.md --template pitch-deck --audience "Nordic public sector CIO"
[Architect designs, pptx-genjs generates, 4 gates pass]
✓ Deck at ./customer-A-arc-pitch.pptx. Provenance PROV-7f8a2.
```

**Workshop deck with defaults:**
```
> /generate-ppt --brief workshop-brief.md --template workshop --use-defaults --voice internal
[Uses in-repo default-ppt-template; voice tier internal so Gate 1 is no-op]
✓ Deck at ./workshop.pptx (default-fallback marker present).
```

**Stale brand override:**
```
> /generate-ppt --brief archive-pitch.md --template pitch-deck --ignore-stale-brand "archival deliverable, brand version pinned"
[Bypasses brand-staleness-warn, logs reason]
```

## See also

- `BRAND-INTEGRATION.md` — brand architecture + cache
- `PPTNarrativeArchitect` agent — slide arc design
- `/asset-search` — Azure asset lookup
- `/rais-customer-voice-check` — Gate 1
- `/provenance-track` — Gate 4
- `/generate-word`, `/generate-web` — sibling doc-gen skills
- `brand-staleness-warn` hook — Phase E
