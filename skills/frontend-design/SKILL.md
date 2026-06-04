---
name: frontend-design
layer: foundation
description: Frontend design-director orchestrator. Chains typography + motion (+ shader in Fas A2) → frontend-design-spec.json → calls generate-web/generate-app for rendering. Design-director-layer per v3.7 family-separation.
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
license_note: produces customer-bound output if --customer-share flag set
---

You are the `frontend-design` orchestrator skill — entrypoint för production-ready frontend design e2e per v3.7 frontend-* family.

## What this skill does

Orchestrates **design-director-decisions** (typography + motion + shader thesis + component-library-pick) → produces `frontend-design-spec.json` → calls **rendering-engine** (`generate-web` single-file/Next.js eller `generate-app` full-vite/svelte/next-monorepo — Fas B) för fil-output.

Skillen ÄGER design-decisions. ÄGER INTE HTML/Next.js-file-generation (det är generate-* family per v3.7 design-doc-boundary).

Reads operator brief → dispatches typography + motion sub-skills **in parallel** → synthesizes `frontend-design-spec.json` → calls rendering-engine.

## When to use

- "Lex Sweden gets a copilot landing page" — full helhet-mode för production-ready design
- Customer demo som måste se Awwwards-grade ut
- Internal microsite där visual quality påverkar adoption
- Multi-format engagement där /li:cycle BUILD-phase producerar app + design måste matcha pitch

## When NOT to use

- Wireframe-only sketch → `/li:design-html` (existing skill)
- Single design-decision-axis (just typography eller just motion) → solo sub-skill `/li:frontend-typography` eller `/li:frontend-motion`
- Pure file-gen utan design-direction → `/li:generate-web` direkt med `--brief`
- Re-render existing run → `/li:generate-web --from-frontend-design <existing-run-dir>`

## Inputs

- Required `<brief>` — design brief text eller path till brief.md
- Optional `--pattern <vault-name>` — välj från `~/.lintel/brand/design-patterns/<name>/` (Fas A2 enables canonical pattern)
- Optional `--target-format <single-file|nextjs|app>` — default: `single-file`. `app` triggar generate-app (Fas B)
- Optional `--customer-share` — sets CUSTOMER_SHARE=1, triggers compliance-gate + voice-gate
- Optional `--out <path>` — output path (default: `~/.lintel/frontend-runs/<run-id>/`)
- Optional `--skip-shader` — Fas A1 default (frontend-shader skill ships i A2)

## Workflow

### Step 1 — Parse invocation + warm context

```bash
brief="${1:-}"
pattern="${PATTERN:-}"
target_format="${TARGET_FORMAT:-single-file}"
customer_share="${CUSTOMER_SHARE:-}"
out_dir="${OUT:-$HOME/.lintel/frontend-runs/$(date +%Y%m%d-%H%M%S)-${RANDOM}}"

[ -z "$brief" ] && { echo "Usage: /li:frontend-design <brief> [--pattern <name>] [--target-format <single-file|nextjs|app>]"; exit 2; }
mkdir -p "$out_dir"
```

Voice-tier resolution: default `internal`. If `--customer-share` → run the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default) first. Per L-001-discipline: skill body bevarar contract, agent at invocation produces actual content.

### Step 2-4 — Parallel sub-skill dispatch (M-4 resolution)

**Run typography + motion sub-skills CONCURRENTLY** (single-batch Agent-tool dispatch). They are independent — both take the brief as input, neither depends on the other.

```
Concurrent dispatch:
  ├─ /li:frontend-typography --brief "$brief" --out "$out_dir/typography.json"
  └─ /li:frontend-motion --brief "$brief" --out "$out_dir/motion.json"

(Fas A2 adds parallel /li:frontend-shader → $out_dir/shader.json)
```

Wallclock budget: ~60s concurrent (vs ~180s sequential). Wait för båda att slutföra before Step 5.

### Step 5 — Synthesize `frontend-design-spec.json`

Read typography.json + motion.json (+ shader.json om A2). Synthesizes till `frontend-design-spec.json`:

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_hash": "<sha256 of brief>",
  "source": "frontend-design",
  "target_format": "single-file | nextjs | app",
  "typography": { /* embedded från typography.json */ },
  "motion": { /* embedded från motion.json */ },
  "shader": null,
  "component_libraries": [
    {"name": "shadcn", "kind": "primitive"},
    {"name": "<aceternity|magic-ui|park-ui>", "kind": "motion-enhanced"}
  ],
  "layout_grammar": {
    "max_width": "1200px",
    "section_spacing": "var(--space-section)",
    "grid": "12-col"
  },
  "interaction_signature": {
    "scroll_smoothing": true,
    "hover_intent": "subtle",
    "page_transitions": "fade-or-slide"
  },
  "visual_thesis": "<one-paragraph synthesis>",
  "voice_tier": "internal | customer-share"
}
```

**Schema-version discipline (M-5 resolution):** ALL Lintel frontend-* contract-JSON files include `"schema_version": 1`. generate-web/generate-app readers log+reject on unknown major version. Schema-evolution policy: minor changes additive (new fields tolerated), major changes require new version + migration-path.

**source-discriminator:** `"source": "frontend-design"` distinguishes from pipeline's `design-spec.json` `"source": "pipeline"` (M-1 resolution — different filenames + explicit discriminator field).

### Step 6 — Call rendering-engine (Fas B integration)

```bash
case "$target_format" in
  single-file|nextjs)
    /li:generate-web --from-frontend-design "$out_dir"
    ;;
  app)
    /li:generate-app --from-frontend-design "$out_dir"   # Fas B skill
    ;;
esac
```

Fas A1 NOTE: `--from-frontend-design` mode i generate-web ships i Fas B PR. Fas A1 stops at frontend-design-spec.json emission + the minimum-viable roundtrip test verifies the contract is consumable.

### Step 7 — Quality gate (Fas A2)

`/li:frontend-design-review <out_dir>` (Fas A2 skill) — 6-dimension audit. Fas A1 stub: emit "skip" log entry tills A2 ships.

### Step 8 — Output paths + recommendation

```
FRONTEND-DESIGN RUN COMPLETE
══════════════════════════════════════════════════════════════════

Run dir:                $out_dir
Typography spec:        $out_dir/typography.json
Motion spec:            $out_dir/motion.json
Frontend design spec:   $out_dir/frontend-design-spec.json

Voice tier:             $voice_tier
Target format:          $target_format

Next:
  Render:               /li:generate-web --from-frontend-design $out_dir   (Fas B)
  Review:               /li:frontend-design-review $out_dir                 (Fas A2)
  Extract som pattern:  /li:frontend-style-extract $out_dir/*               (Fas A2)
```

## Voice tier behavior

`voice: mixed`. Default `internal`. `--customer-share` triggers the active pack's compliance-gate + voice-gate (`resolve_pack_field compliance.hooks`; none by default).

## Status protocol

- **DONE** — both sub-skills returned, frontend-design-spec.json written, schema-validation passed
- **DONE_WITH_CONCERNS** — sub-skill returned with warnings (e.g., font-license unclear)
- **BLOCKED** — sub-skill failed, OR brief unparsable, OR customer-share check failed
- **NEEDS_CONTEXT** — brief too vague (no audience, no purpose, no aesthetic-direction)

## Pause-points

- Customer-share flag set + voice-check fails → BLOCKED för operator-review
- Brief lacks "for whom" eller "what aesthetic" → NEEDS_CONTEXT
- Sub-skill returns with critical-warning → DONE_WITH_CONCERNS surface till operator

## Hop-in support

YES — solo-invocable. Designed för auto-invocation från `/li:cycle` BUILD-phase i Fas D (when cycle-integration ships).

## Integration

**Reads:**
- `<brief>` argument (path eller inline text)
- `~/.lintel/brand/design-patterns/<name>/` (om `--pattern` flag set; Fas A2 enables)
- `~/.lintel/profile.yaml` (mode → voice-tier)

**Writes:**
- `~/.lintel/frontend-runs/<run-id>/typography.json` (via frontend-typography sub-skill)
- `~/.lintel/frontend-runs/<run-id>/motion.json` (via frontend-motion sub-skill)
- `~/.lintel/frontend-runs/<run-id>/frontend-design-spec.json` (Step 5 synthesis)
- Audit-log: `~/.lintel/audit/frontend-design-runs.jsonl`

**Calls into:**
- `/li:frontend-typography` (sub-skill, parallel)
- `/li:frontend-motion` (sub-skill, parallel)
- `/li:generate-web --from-frontend-design <run-dir>` (Fas B)
- the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default — om customer-share)
- `/li:compliance-gate` (existing, om customer-share)

**Boundary med generate-* family:**

frontend-design är DESIGN-DIRECTOR-LAYER (decisions). generate-web/generate-app är RENDERING-ENGINE-LAYER (file-output). Frontend-design CALLS into generate-* för rendering. Inte vice versa. Skarp boundary per v3.7 design-doc per family-separation-table.

**Brand-asset-slots (Fas A1 documents paths; folders lazy-created):**
- `~/.lintel/brand/design-patterns/` — Fas A2 ships canonical `ultra-modern-lovable-style/`
- `~/.lintel/brand/motion-libraries/` — operator-tested GSAP/Lenis-combos
- `~/.lintel/brand/shader-snippets/` — operator-curated GLSL (Fas A2 + frontend-shader)

## Anti-patterns

- **Generating HTML inside frontend-design** — that's generate-web's job (boundary-violation per L-002). Use `--from-frontend-design` chain.
- **Sequential sub-skill dispatch** — Workflow Step 2-4 explicitly PARALLEL per M-4. Sequential breaks 10-min budget.
- **Pre-baking canonical patterns** — Fas A1 ships slot-bootstrapping only. Canonical hand-curation deferred till A2 after schema validates against operator-real briefs.
- **Bundling commercial fonts/libraries** — Lintel ships scaffolding. Operator licenserar Pangram + installer GSAP/OGL/Aceternity via npm.

## Failure recovery

- Sub-skill timeout (>120s): mark sub-skill output as STUB + continue with partial synthesis; surface to operator with "partial-spec" warning
- Brief unparsable: BLOCKED, return to operator with prompt-improvement-suggestions
- Schema-validation failure on frontend-design-spec.json: BLOCKED, log diff between produced + expected schema
- Voice-gate fail (customer-share): BLOCKED, surface voice-check output verbatim

## Recommended next steps after invocation

- Fas A1: hand off `$out_dir/frontend-design-spec.json` till generate-web manually for now (Fas B automatisk chain)
- Fas A2: pair med `/li:frontend-design-review` för 6-dimension audit
- Fas A2+: extract successful design via `/li:frontend-style-extract $out_dir/*` → adds till vault
- Cycle-integration: defer till Fas D after operator dogfood validates real-engagement flow

## L-001/L-002/L-003 application

- **L-001 (scaffolding-not-content):** skill body är contract. Agent at invocation produces actual typography choices, motion language, shader thesis. Canonical pattern deferred till A2. Operator-extracted patterns dominate vault long-term.
- **L-002 (grep-first):** generate-* family bevaras. Frontend-* family = identity-anchor + design-director layer, EJ replacement. Boundary-table-row added till design-doc.
- **L-003 (verify-claims):** schema_version field on every contract JSON. generate-web reader verifies before consuming. Don't trust stale schemas.
