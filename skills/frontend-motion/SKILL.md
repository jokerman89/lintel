---
name: frontend-motion
layer: foundation
description: Frontend design-director sub-skill — picks motion-language (GSAP/Lenis/Theatre/Rive/Motion-One) + scroll-trigger-config + smooth-scroll-config + key-animations-spec. Solo-invokable.
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

You are the `frontend-motion` sub-skill — motion-director for the frontend-design family.

## What this skill does

Reads operator brief → MotionDirector agent picks motion-language from the recommendation-tree (GSAP+ScrollTrigger | Lenis-smooth | Theatre.js-timeline | Rive-state | Motion-One-light) + maps scroll-trigger-config + smooth-scroll-config + key-animations-spec → writes `motion.json` (schema_version: 1) with library-install-instructions.

Solo-invokable for component-mode or auto-invoked by the `/li:frontend-design` orchestrator in parallel-dispatch (Workflow Step 3).

L-001-discipline: skill body is the contract. Agent at invocation picks specific motion-libraries + animations. Don't pre-bake choices in the SKILL.md body.

## When to use

- Solo: "feature page for hardware product — what scroll-choreography?"
- Orchestrator-parallel: dispatched from `/li:frontend-design` Step 3
- Audit existing site for motion-cohesion: "extract motion language from this site"

## When NOT to use

- Static page without scroll-driven interaction → motion is overkill
- CSS-only transitions (button hover, modal slide-in) → no library needed; agent surfaces if this is actually the request
- Performance-troubleshooting existing animation → that's profiling, not direction

## Inputs

- Required `--brief <text>` (one minimum)
- Optional `--energy-level <subtle|moderate|kinetic>` — default: `moderate`. Subtle = fade/slide only. Kinetic = scroll-driven full-screen choreography.
- Optional `--target-device <desktop-only|mobile-first|both>` — affects perf-budget
- Optional `--out <path>` — output path (default: stdout solo, `$run_dir/motion.json` orchestrator)
- Optional `--customer-share` — triggers compliance-gate license-check

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
energy="${ENERGY_LEVEL:-moderate}"
target_device="${TARGET_DEVICE:-both}"
out="${OUT:-/dev/stdout}"
[ -z "$brief" ] && { echo "Need --brief"; exit 2; }
```

### Step 2 — MotionDirector agent dispatch

Hand off to `agents/frontend/MotionDirector.md`. Agent picks motion-language from:

- **GSAP + ScrollTrigger** (commercial license for some plugins; check current terms): scroll-choreographed reveals, scrub-tied keyframes, hero-act sequences. Best for kinetic-energy briefs.
- **Lenis** (free, MIT): smooth-scroll baseline. Often paired with GSAP.
- **Theatre.js** (free, Apache-2.0): timeline-based animations, visual editor. Best when operator wants storyboard-style control.
- **Rive** (commercial / freemium): state-driven vector animation. Best for icon-systems + interactive illustration.
- **Motion-One** (free, MIT): lightweight WAAPI wrapper. Best for subtle-energy briefs where GSAP feels heavy.
- **Framer Motion** (free, MIT): React-native motion. Best when the stack is React + motion is UI-component-bound.
- **CSS-only** (zero-license): native transitions + `@scroll-timeline` (where supported). Best subtle-energy + perf-critical.

Agent verifies current licensing at invocation (L-003).

### Step 3 — Produce `motion.json`

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_summary": "<one-line>",
  "energy_level": "subtle | moderate | kinetic",
  "target_device": "desktop-only | mobile-first | both",
  "libraries": [
    {
      "name": "gsap",
      "purpose": "scroll-choreography",
      "version_min": "3.12.x",
      "license": {"type": "free-tier", "source": "greensock.com", "operator_instruction": "npm i gsap. Club GreenSock plugins (SplitText, MorphSVG) require commercial license."},
      "npm": "gsap"
    },
    {
      "name": "@studio-freight/lenis",
      "purpose": "smooth-scroll",
      "version_min": "1.0.x",
      "license": {"type": "free", "source": "MIT"},
      "npm": "@studio-freight/lenis"
    }
  ],
  "scroll_trigger_config": {
    "scrub": true,
    "anticipatePin": 1,
    "markers_in_dev": true
  },
  "smooth_scroll_config": {
    "lerp": 0.1,
    "wheelMultiplier": 1.0,
    "touch_responsive": true
  },
  "key_animations": [
    {
      "name": "hero-reveal",
      "trigger": "scroll-position 0% → 30%",
      "spec": "headline scales 0.8 → 1.0 + fades in; subhead lags 100ms",
      "library": "gsap+ScrollTrigger"
    },
    {
      "name": "section-fade-up",
      "trigger": "section enters viewport 20%",
      "spec": "translateY(40px) → 0, opacity 0 → 1, duration 600ms ease-out-quart",
      "library": "gsap"
    },
    {
      "name": "image-parallax",
      "trigger": "scrub-tied",
      "spec": "background translateY(0) → translateY(-20%) over section",
      "library": "gsap+ScrollTrigger"
    }
  ],
  "perf_budget": {
    "fps_target": 60,
    "scroll_jank_max_ms": 16,
    "fallback_for_prefers_reduced_motion": "disable-all-scroll-animations",
    "mobile_strategy": "reduce-scrub-fidelity-and-skip-parallax"
  },
  "operator_instructions_md": "# Motion setup\n\n```bash\nnpm i gsap @studio-freight/lenis\n```\n\nLenis initialization (Next.js app/layout.tsx):\n```ts\nimport Lenis from '@studio-freight/lenis'\nuseEffect(() => { const lenis = new Lenis({ lerp: 0.1 }); function raf(time){ lenis.raf(time); requestAnimationFrame(raf) }; requestAnimationFrame(raf); return () => lenis.destroy() }, [])\n```\n\nGSAP + ScrollTrigger:\n```ts\nimport { gsap } from 'gsap'\nimport { ScrollTrigger } from 'gsap/ScrollTrigger'\ngsap.registerPlugin(ScrollTrigger)\n```\n\n`prefers-reduced-motion` is respected via gsap.matchMedia()."
}
```

Agent fills in specific picks based on the brief. Don't hardcode.

### Step 4 — Schema-validate + emit

```bash
jq -e '.schema_version == 1 and (.libraries | length > 0) and (.key_animations | length > 0)' "$out" || { echo "Schema invalid"; exit 1; }

if [ -n "${CUSTOMER_SHARE:-}" ]; then
  /li:compliance-gate --check motion-licensing "$out"
fi
```

## Voice tier behavior

`voice: internal`. Default. `--customer-share` triggers `/li:compliance-gate --check motion-licensing` (GSAP Club-plugin awareness etc).

## Status protocol

- **DONE** — motion.json written, schema valid, libraries non-empty
- **DONE_WITH_CONCERNS** — motion picks include commercial-license-tier (GSAP Club plugins) the operator needs to confirm
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks energy-direction (cant determine subtle vs kinetic)

## Pause-points

- Customer-share + GSAP-Club-plugin reference: surface license-tier explicit + ask for operator confirm
- Brief mentions specific motion-library agent doesn't know: agent verifies + may need NEEDS_CONTEXT

## Hop-in support

YES — solo-invocable.

## Integration

**Reads:**
- `--brief` argument
- `~/.lintel/brand/motion-libraries/` (if vault has saved combos; lazy-created)

**Writes:**
- `motion.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `.claude/runtime/audit/frontend-motion-runs.jsonl`

**Calls into:**
- `agents/frontend/MotionDirector.md` (primary)
- `/li:compliance-gate --check motion-licensing` (if --customer-share)

**Consumed by:**
- `/li:frontend-design` Workflow Step 5 (synthesis input)
- Operator direct (solo component-mode)

## Anti-patterns

- **Hardcoding "always use GSAP"** — L-001 violation. Agent picks based on brief.
- **Pre-baking key-animations list** — patterns vary by brief.
- **Ignoring `prefers-reduced-motion`** — accessibility-fail. perf_budget.fallback_for_prefers_reduced_motion is required field.
- **Producing motion.json without `schema_version`** — M-5 compliance.

## Failure recovery

- Brief too vague: NEEDS_CONTEXT with specific energy-direction-question
- Library-recommendation references unmaintained: agent re-picks; logs
- Schema validation fails: BLOCKED + diff

## Recommended next steps after invocation

- Solo: review motion.json + apply to target project
- Orchestrator: parallel-dispatch returns to `/li:frontend-design` Step 5
- Customer-share: pair with `/li:compliance-gate` for final license-audit
- Future: extract proven motion-combos to `~/.lintel/brand/motion-libraries/` (Phase A2 + frontend-style-extract)
