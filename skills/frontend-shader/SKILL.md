---
name: frontend-shader
layer: ms-team
description: Frontend design-director sub-skill — picks shader library (Paper Shaders / OGL / react-three-fiber / Lygia) + visual thesis + GLSL snippet references + perf-budget. Solo-invokable.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
---

You are the `frontend-shader` sub-skill — shader-engineer for v3.7 frontend-* family (Fas A2).

## What this skill does

Reads operator brief → ShaderEngineer agent picks shader-library (Paper Shaders deklarativ | OGL+glslify | react-three-fiber+postprocessing | Lygia-snippets | CSS-houdini-paint-worklet) + visual-thesis + GLSL-snippet-references + GPU-fallback-strategy + perf-budget → writes `shader.json` (schema_version: 1).

Solo-invokable för delar-mode eller auto-invoked by `/li:frontend-design` orchestrator i parallel-dispatch (Workflow Step 4) som tredje parallel sub-skill (efter typography + motion).

L-001-discipline: skill body är contract. Agent at invocation produces specific library picks + GLSL recommendations. Don't pre-bake shader-snippets i SKILL.md body.

## When to use

- Solo: "hero-bakgrund för enterprise SaaS landing — want a subtle mesh-gradient"
- Orchestrator-parallel: dispatched from `/li:frontend-design` Step 4
- Audit existing site: "extract shader-thesis from this site"

## When NOT to use

- Static site, no hero-visual ambition → shader overkill
- 3D scene-graph needed → use react-three-fiber direct (shader sub-skill picks libs but doesn't build scenes)
- CSS-gradient is enough → agent surfaces "no shader needed" and short-circuits

## Inputs

- Required `--brief <text>` (one minimum)
- Optional `--visual-thesis <mesh-gradient|noise-field|fluid-sim|particle-system|displacement-warp|none>` — default: inferred from brief
- Optional `--perf-budget <low-end|mid-tier|high-end-only>` — affects GPU-fallback-strategy
- Optional `--out <path>` — output path (default: stdout solo, `$run_dir/shader.json` orchestrator)
- Optional `--customer-share` — triggers compliance-gate license-check

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
thesis="${VISUAL_THESIS:-auto}"
perf="${PERF_BUDGET:-mid-tier}"
out="${OUT:-/dev/stdout}"
[ -z "$brief" ] && { echo "Need --brief"; exit 2; }
```

### Step 2 — ShaderEngineer agent dispatch

Hand off to `agents/frontend/ShaderEngineer.md`. Agent picks shader-library:

- **Paper Shaders** (MIT, declarative React/Vue/Vanilla): mesh-gradients + animated bg. Best for non-3D hero-visuals. Lowest implementation-cost.
- **OGL** (MIT, lightweight 3D + raw WebGL): direct GLSL with full control. Best för custom thesis + performance-critical.
- **react-three-fiber + drei + postprocessing** (MIT, React 3D + effects): production 3D scenes + post-FX. Best för immersive contexts.
- **Lygia** (MIT, GLSL function library): drop-in functions för noise/SDF/lighting. Pairs with OGL eller r3f. Don't ship alone.
- **CSS Houdini Paint Worklet** (W3C, browser-paint API): GPU-accelerated CSS paint. Best för super-lightweight backgrounds where shader-lib is overkill.
- **shadcn + CSS conic-gradient + filter blur** (zero-lib): no-shader fallback. Often sufficient.

Agent verifies current licensing at invocation (L-003).

### Step 3 — Produce `shader.json`

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_summary": "<one-line>",
  "visual_thesis": "<mesh-gradient | noise-field | fluid-sim | particle-system | displacement-warp | none>",
  "library": {
    "name": "paper-design/shaders",
    "version_min": "0.x",
    "license": {"type": "free", "source": "MIT"},
    "npm": "@paper-design/shaders-react",
    "operator_instruction": "npm i @paper-design/shaders-react"
  },
  "glsl_snippets": [
    {
      "name": "mesh-gradient-3color",
      "purpose": "hero background",
      "source": "Paper Shaders built-in <MeshGradient> component",
      "notes": "configurable colors[0..2], speed, distortion, swirl"
    }
  ],
  "lygia_imports": [],
  "perf_budget": {
    "fps_target": 60,
    "max_draw_calls": 4,
    "fallback_strategy_low_end": "swap to CSS conic-gradient",
    "fallback_strategy_no_webgl": "static CSS gradient + noise SVG",
    "respect_prefers_reduced_motion": true,
    "intersection_observer_pause": true
  },
  "gpu_thesis": {
    "complexity": "low | medium | high",
    "mobile_strategy": "downscale-resolution-50% | disable | full",
    "explanation": "Paper Shaders runs on fragment-shader-only with 1 fullscreen quad — safe for mid-tier mobile"
  },
  "operator_instructions_md": "# Shader setup\n\n```bash\nnpm i @paper-design/shaders-react\n```\n\n```tsx\nimport { MeshGradient } from '@paper-design/shaders-react'\n\n<MeshGradient\n  colors={['#0078D4', '#50E6FF', '#0d1b2a']}\n  speed={0.3}\n  distortion={0.8}\n  className=\"absolute inset-0 -z-10\"\n/>\n```\n\nFallback for `prefers-reduced-motion`:\n```css\n@media (prefers-reduced-motion: reduce) {\n  .shader-bg { animation: none; }\n}\n```"
}
```

Agent fyller specific picks. Don't hardcode.

### Step 4 — Schema-validate + emit

```bash
jq -e '.schema_version == 1 and .library.name != null' "$out" || { echo "Schema invalid"; exit 1; }

# perf_budget required
jq -e '.perf_budget.fallback_strategy_low_end != null and .perf_budget.respect_prefers_reduced_motion == true' "$out" || {
  echo "perf_budget incomplete"; exit 1
}

if [ -n "${CUSTOMER_SHARE:-}" ]; then
  /li:compliance-gate --check shader-licensing "$out"
fi
```

### Step 5 — Visual-thesis === "none" short-circuit

Agent kan returnera visual_thesis="none" om brief doesn't warrant shader. Skill body STILL emits valid JSON så orchestrator-Step-5 synthesis kan handle `shader: null` gracefully.

## Voice tier behavior

`voice: internal`. Default. `--customer-share` triggers `/li:compliance-gate --check shader-licensing`.

## Status protocol

- **DONE** — shader.json written, schema valid, library + perf-budget non-empty (OR visual_thesis="none")
- **DONE_WITH_CONCERNS** — picked library has commercial-tier requirements (rare)
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks visual-direction (cant determine if shader needed)

## Pause-points

- Customer-share + library has obscure license → flag explicit
- Brief mentions specific shader-lib agent doesn't know → may need NEEDS_CONTEXT
- visual_thesis="none" — short-circuit confirmation to operator (no shader is fine)

## Hop-in support

YES — solo-invocable.

## Integration

**Reads:**
- `--brief` argument
- `~/.lintel/brand/shader-snippets/` (om operator-curated; lazy-created)

**Writes:**
- `shader.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `~/.lintel/audit/frontend-shader-runs.jsonl`

**Calls into:**
- `agents/frontend/ShaderEngineer.md` (primary)
- `/li:compliance-gate --check shader-licensing` (om --customer-share)

**Consumed by:**
- `/li:frontend-design` Workflow Step 5 (synthesis input — `shader` field)
- Operator direct (solo delar-mode)

## Anti-patterns

- **Hardcoding "always Paper Shaders"** — L-001 violation. Agent picks based on brief.
- **Skipping perf_budget.respect_prefers_reduced_motion** — accessibility-fail. Required field.
- **No fallback_strategy_low_end** — mobile-users will see broken page. Required.
- **No fallback_strategy_no_webgl** — WebGL-disabled browsers (rare but real) see broken page. Required.
- **Producing shader.json without `schema_version`** — M-5 compliance.

## Failure recovery

- Brief too vague → NEEDS_CONTEXT with question ("subtle mesh-gradient or full 3D scene?")
- Library-version-recommendation outdated → agent re-picks at invocation
- Schema validation fails: BLOCKED + diff
- visual_thesis="none" but operator wanted shader: surface "consider CSS-gradient instead"

## Recommended next steps after invocation

- Solo: review shader.json + apply till target project
- Orchestrator: parallel-dispatch returns to `/li:frontend-design` Step 5
- Customer-share: pair med `/li:compliance-gate` för final license-audit
- Future: extract proven shader-snippets till `~/.lintel/brand/shader-snippets/` (via frontend-style-extract)
