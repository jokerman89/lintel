---
name: frontend-design
layer: foundation
description: Use to direct frontend design, advise on a design-system choice or compare bounded variants while preserving the shared design contract and actual rendering/review evidence.
color: orange
tools: Read, Write, Bash, Glob
voice: mixed
cli_support: [claude-code, codex, copilot]
license_note: produces customer-bound output if --customer-share flag set
---

You are the `frontend-design` skill, the design-director layer over existing rendering tools.

## Modes

Select `--mode design|advice|variants`; default `design` preserves the ordinary
brief-to-design-to-render workflow below. Reject conflicting mode inputs before
writing. These are skill inputs, not an installed command parser.

| Mode | Inputs and output |
|---|---|
| `design` | `<brief>`, selected pattern/target/stack, explicit `--out`; bound `frontend-design-spec.json`, rendered artifact and review |
| `advice` | `<question>`, `--scope`, `--read-design-system`, `--cross-check`; grounded alternatives and a recommendation, no code |
| `variants` | `--seed`, `--axis`, `--count` (2-8, default 4), optional `--brief`/`--only`, explicit `--out`; per-variant designs, rendered HTML and comparison `index.html` |

For advice follow [the advice procedure](references/advice.md). For variants
follow [the variants procedure](references/variants.md). Neither mode invents
independent actors, installs tools, replaces project technology or waives policy.
Advice stops before rendering. Variants reuse this decision contract and the
existing `generate-web` renderer for each actual output.

## What this skill does

Orchestrates **design-director-decisions** (typography + motion + shader thesis + component-library-pick) → produces `frontend-design-spec.json` → calls **rendering-engine** (`generate-web` single-file/Next.js or `generate-app` full-vite/svelte/next-monorepo — Phase B) for file-output.

The skill OWNS design-decisions. It does NOT own HTML/Next.js-file-generation (that's the generate-* family per the v3.7 design-doc-boundary).

Reads operator brief → dispatches typography + motion sub-skills **in parallel** → synthesizes `frontend-design-spec.json` → calls rendering-engine.

The [direct design contract](../design-dna/references/design-contract.md) and its
single schema/helper govern all producers, renderer arguments and review. Use
actual available delegation or serial execution; a role name is not an invocation.

## When to use

- "A landing page for our legal-research assistant" — full end-to-end mode for production-ready design
- Customer demo that must look Awwwards-grade
- Internal microsite where visual quality affects adoption
- Multi-format engagement where /li:cycle BUILD-phase produces an app + design must match the pitch

## When NOT to use

- Wireframe-only sketch → `/li:generate-web --mode mockup`
- Single design-decision-axis (just typography or just motion) → solo sub-skill `/li:frontend-typography` or `/li:frontend-motion`
- Pure file-gen without design-direction → `/li:generate-web` directly with `--brief`
- Re-render existing run → `/li:generate-web --from-frontend-design <existing-run-dir>`

## Inputs

- Required `<brief>` — design brief text or path to brief.md
- Optional `--pattern <name>` — select an explicitly configured project/pack pattern; no personal-vault discovery
- Optional `--target-format <single-file|nextjs|app>` — default: `single-file`. `app` triggers generate-app (Phase B)
- Optional `--customer-share` — sets CUSTOMER_SHARE=1, triggers compliance-gate + voice-gate
- Required `--out <path>` for rendering — owned repository-relative run directory
- Optional `--skip-shader` — explicit no-shader choice, not an unfinished GPU feature
- `--stack <next-app|vite-react|svelte-kit>` for `--target-format app`, selected
  explicitly or confirmed from the existing project manifest; never infer React
  for an unknown stack.

## Design mode workflow

### Step 1 — Parse invocation + warm context

```bash
brief="${1:-}"
pattern="${PATTERN:-}"
target_format="${TARGET_FORMAT:-single-file}"
customer_share="${CUSTOMER_SHARE:-}"
out_dir="${OUT:?select an owned repository-relative output directory}"

[ -z "$brief" ] && { echo "Usage: /li:frontend-design <brief> [--pattern <name>] [--target-format <single-file|nextjs|app>]"; exit 2; }
```

Reject missing, unknown, duplicate or conflicting options before creating output.
Preserve the brief as literal data. `--skip-shader` records a no-shader decision.
The application stack and output path must reach the renderer unchanged.

Voice-tier resolution: default `internal`. If `--customer-share` → run the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default) first. Per L-001-discipline: skill body preserves contract, agent at invocation produces actual content.

### Step 1.5 — Design DNA pass (REQUIRED — ADR-0015/0016)

Retrieval before generation. Resolve the active design profile and search the corpus BEFORE any
design decision:

```bash
dna="${LINTEL_SOURCE_ROOT:?trusted source required}/skills/design-dna"
python3 "$dna/scripts/search.py" "<product> <industry> <tone keywords from brief>" \
  --design-system -f markdown -p "<project>" > "$out_dir/design-dna.md"
```

Use the already verified P07 `profile_ref` and `design_contract.profile_asset` to select
the pack-owned profile before the same named bundled asset. Retain its hash and
retrieval output in `binding`. Missing required policy or a selected asset blocks;
do not source a personal-home fallback or silently substitute a brand.

Precedence: **brief > verified profile > corpus hit** — the profile is the
selected baseline; the corpus recommendation fills what the
profile doesn't pin (style pattern, landing structure, product-specific palette when the brief
asks for one); the brief's own words always win. Both `design-dna.md` and the profile feed
Step 2-4 dispatch and Step 5 synthesis. No python3 → use the grep fallback documented in
`skills/design-dna/SKILL.md` (the corpus is plain CSV).

### Step 2-4 — Parallel sub-skill dispatch (M-4 resolution)

Typography and motion are independent decision tasks. Run concurrently only when
the actual host provides attributable disjoint output ownership; otherwise serialize.

```
Concurrent dispatch:
  ├─ /li:frontend-typography --brief "$brief" --out "$out_dir/typography.json"
  └─ /li:frontend-motion --brief "$brief" --out "$out_dir/motion.json"

(Phase A2 adds parallel /li:frontend-shader → $out_dir/shader.json)
```

Both sub-skills receive `$out_dir/design-dna.md` + the active profile as context (Step 1.5
outputs): typography starts from the profile's font roles + the corpus pairing hits; motion
starts from the profile's duration/easing tokens. They deviate only where the brief demands it.

Wait for both actual results before synthesis. No timing or parallel-execution
claim follows from this recipe. None/CSS motion is a complete result, not a stub.

### Step 5 — Synthesize `frontend-design-spec.json`

Read typography.json + motion.json (+ shader.json if A2). Synthesizes into `frontend-design-spec.json`:

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_hash": "<sha256 of brief>",
  "source": "frontend-design",
  "target_format": "single-file | nextjs | app",
  "typography": { /* embedded from typography.json */ },
  "motion": { /* embedded from motion.json */ },
  "shader": null,
  "component_libraries": [],
  "layout_grammar": {
    "max_width": "1200px",
    "section_spacing": "var(--space-section)",
    "grid": "12-col"
  },
  "interaction_signature": {
    "scroll_smoothing": false,
    "hover_intent": "subtle",
    "page_transitions": "none"
  },
  "palette": {
    "source_profile": "<selected-profile>",
    "tokens": { "<semantic-name>": "<hex>" }
  },
  "style": {
    "name": "<chosen style from design-dna search>",
    "anti_patterns": ["<from the corpus reasoning rule>"]
  },
  "design_dna": {
    "profile": "<selected-profile>",
    "search_query": "<the Step 1.5 query>",
    "search_ref": "design-dna.md"
  },
  "visual_thesis": "<one-paragraph synthesis>",
  "voice_tier": "internal | customer-share",
  "binding": { /* exact profile, brief, project, retrieval and provenance per shared schema */ }
}
```

`palette`, `style` and `design_dna` are additive optional fields (ADR-0015) — `schema_version`
stays 1; readers tolerate their absence (minor-additive per the schema-evolution policy below).
Legacy input remains readable, not automatically renderable. New resolved output
needs palette tokens, explicit motion mode and the shared binding. Libraries are
chosen only when justified by the existing stack and brief, with exact sourced
versions/licenses; empty lists are valid.

**Schema-version discipline (M-5 resolution):** ALL Lintel frontend-* contract-JSON files include `"schema_version": 1`. generate-web/generate-app readers log+reject on unknown major version. Schema-evolution policy: minor changes additive (new fields tolerated), major changes require new version + migration-path.

**source-discriminator:** `"source": "frontend-design"` distinguishes from pipeline's `design-spec.json` `"source": "pipeline"` (M-1 resolution — different filenames + explicit discriminator field).

### Step 6 — Call rendering-engine

Prepare the external P05 input context, then call the shared helper's
`renderer-args` operation with the explicit target/profile paths. It validates
current bytes and returns a literal argument array:

- `single-file` -> `generate-web --from-frontend-design <run> --variant single-file --out <out>`
- `nextjs` -> `generate-web --from-frontend-design <run> --variant nextjs-scaffold --out <out>`
- `app` -> `generate-app --from-frontend-design <run> --stack <selected-stack> --out <out>`

Propagate `--customer-share` when selected. Invoke through the actual host only
within authorization; mapping itself reports `executed: false`. Missing stack,
unresolved bindings or incompatible existing technology block before rendering.

### Step 7 — Quality gate (MANDATORY — ADR-0015)

The gate is no longer optional. Two parts, in order:

1. Run the existing mechanical validator on actual produced HTML/CSS. Use the
   **resolved** palette, including explicit brief overrides, rather than rebuilding
   a bundled `$dna/profiles/<name>` path that ignores a pack-owned asset.
   The existing `validate_design.check(content, path, profile_hexes)` API accepts
   the lowercase values of `loaded_design["design"]["palette"]["tokens"]`.
   Preserve its returned errors/warnings separately; errors block. The standalone
   validator CLI remains available when an explicit verified asset path is used.
2. Invoke `/li:frontend-design-review` on the actual output and the same selected
   design/context. That consumer rechecks P07 and the original P05 obligations.

Validator errors → **BLOCKED** (fix and re-render; never ship over a red gate). No rendered HTML
yet (spec-only run) → validator runs in generate-web/generate-app when output exists;
spec feedback does not count as built-UI review. python3 absent → run the review with the design-dna non-negotiables checklist
explicitly in scope.

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
  Render:               /li:generate-web --from-frontend-design $out_dir   (Phase B)
  Review:               /li:frontend-design-review $out_dir                 (Phase A2)
  Extract as pattern:   /li:frontend-style-extract $out_dir/*               (Phase A2)
```

## Voice tier behavior

`voice: mixed`. Default `internal`. `--customer-share` triggers the active pack's compliance-gate + voice-gate (`resolve_pack_field compliance.hooks`; none by default).

## Status protocol

- **DONE** — the requested mode produced its actual outputs and required
  observations; spec validation alone does not complete a requested render/review
- **DONE_WITH_CONCERNS** — sub-skill returned with warnings (e.g., font-license unclear)
- **BLOCKED** — sub-skill failed, OR brief unparsable, OR customer-share check failed
- **NEEDS_CONTEXT** — brief too vague (no audience, no purpose, no aesthetic-direction)

## Integration

**Reads:**
- `<brief>` argument (path or inline text)
- Explicitly selected project/pack pattern (if `--pattern` is set)
- Verified P07 reference, selected profile asset and actual voice requirements

**Writes:**
- `<out>/typography.json` and `<out>/motion.json` (validated sub-skill output)
- `<out>/frontend-design-spec.json` (Step 5 synthesis)
- Variants add separate bound runs, rendered files and comparison `index.html`
- Advice returns Markdown or the explicit owned `--out`; no rendered artifact

**Calls into:**
- `/li:design-dna` system search + profile resolution (Step 1.5, required) + validator (Step 7)
- `/li:frontend-typography` (sub-skill, parallel)
- `/li:frontend-motion` (sub-skill, parallel)
- `/li:generate-web --from-frontend-design <run-dir>` (Phase B)
- the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default — if customer-share)
- `/li:compliance-gate` (existing, if customer-share)

**Boundary with the generate-* family:**

frontend-design is the design-director layer; generate-web/generate-app own file
output. Direct brief/mockup rendering can use the director's decision method
without recursively invoking its render step. No second design schema is created.

**Brand-asset-slots (Phase A1 documents paths; folders lazy-created):**
- `~/.lintel/brand/design-patterns/` — Phase A2 ships canonical `ultra-modern-lovable-style/`
- `~/.lintel/brand/motion-libraries/` — operator-tested GSAP/Lenis-combos
- `~/.lintel/brand/shader-snippets/` — operator-curated GLSL (Phase A2 + frontend-shader)

## Anti-patterns

- **Generating HTML inside frontend-design** — that's generate-web's job (boundary-violation per L-002). Use `--from-frontend-design` chain.
- **Invented parallel dispatch** — serial/manual operation is valid when the host
  cannot provide attributable parallel ownership.
- **Pre-baking canonical patterns** — Phase A1 ships slot-bootstrapping only. Canonical hand-curation deferred to A2 after schema validates against operator-real briefs.
- **Bundling unlicensed fonts/libraries** — preserve actual source/license
  evidence and authorized tooling scope; no installation follows from advice.

## Failure recovery

- Sub-skill failure: retain partial artifacts and report the missing decision;
  do not turn a stub into a resolved renderable spec.
- Brief unparsable: BLOCKED, return to operator with prompt-improvement-suggestions
- Schema-validation failure on frontend-design-spec.json: BLOCKED, log diff between produced + expected schema
- Voice-gate fail (customer-share): BLOCKED, surface voice-check output verbatim

## Recommended next steps after invocation

- Phase A1: hand off `$out_dir/frontend-design-spec.json` to generate-web manually for now (Phase B automatic chain)
- Phase A2: pair with `/li:frontend-design-review` for 6-dimension audit
- Phase A2+: extract successful design via `/li:frontend-style-extract $out_dir/*` → adds to vault
- Cycle-integration: defer to Phase D after operator dogfood validates real-engagement flow

## L-001/L-002/L-003 application

- **L-001 (scaffolding-not-content):** skill body is contract. Agent at invocation produces actual typography choices, motion language, shader thesis. Canonical pattern deferred to A2. Operator-extracted patterns dominate vault long-term.
- **L-002 (grep-first):** the generate-* family is preserved. Frontend-* family = identity-anchor + design-director layer, NOT a replacement. Boundary-table-row added to the design-doc.
- **L-003 (verify-claims):** schema_version field on every contract JSON. generate-web reader verifies before consuming. Don't trust stale schemas.
