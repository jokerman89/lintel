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

Use the motion definition in the [shared design contract](../design-dna/references/design-contract.md).
No animation and CSS-only are first-class successful decisions, not missing work.

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
- Optional `--mode <none|css|library>` — explicit decision when known; otherwise
  decide from the brief and existing project before producing the shared contract.

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
energy="${ENERGY_LEVEL:-moderate}"
target_device="${TARGET_DEVICE:-both}"
out="${OUT:-}"  # absent --out means stdout, not a path to validate
[ -z "$brief" ] && { echo "Need --brief"; exit 2; }
```

### Step 2 — Corpus query + MotionDirector agent dispatch

Query the design corpus first (ADR-0015 — retrieval before generation):

```bash
python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/search.py" "<animation/interaction keywords>" --domain ux -n 3
```

The active design profile's motion tokens are the default (anthropic-default: 150/220/320ms,
ease-out enter / shorter ease-in exit, one orchestrated moment per view, transform/opacity only,
reduced-motion respected). The brief's energy-level justifies deviation from the tokens — never
from the reduced-motion floor.

Hand off to `agents/frontend/MotionDirector.md` with the corpus hits + profile tokens in context. Agent picks motion-language from:

- **GSAP + ScrollTrigger:** scroll-choreographed reveals, scrub-tied keyframes and
  hero-act sequences when justified. Check the selected release's actual terms;
  do not repeat an obsolete blanket Club-plugin purchase requirement.
- **Lenis:** smooth scrolling only when justified over native behavior; verify the
  selected maintained package, release and license.
- **Theatre.js:** timeline-based animation/editor; distinguish selected runtime,
  editor and asset terms when storyboard control is needed.
- **Rive:** state-driven vector interaction; verify runtime and authoring/asset terms separately.
- **Motion/WAAPI candidates:** lightweight component transitions when needed; use
  the current project-compatible package API, version and license.
- **React motion candidates:** choose only for compatible React projects and
  UI-bound motion; do not impose them on another framework.
- **CSS-only** (zero-license): native transitions + `@scroll-timeline` (where supported). Best subtle-energy + perf-critical.

Agent verifies current licensing at invocation (L-003).

### Step 3 — Produce `motion.json`

```json
{
  "schema_version": 1,
  "mode": "none | css | library",
  "generated_at": "<iso-8601>",
  "brief_summary": "<one-line>",
  "energy_level": "subtle | moderate | kinetic",
  "target_device": "desktop-only | mobile-first | both",
  "libraries": [
    {
      "name": "gsap",
      "purpose": "scroll-choreography",
      "version": "<exact project-compatible release>",
      "license": {"type": "<verified terms>", "source": "<primary source for that release>"},
      "npm": "gsap"
    },
    {
      "name": "<selected maintained smooth-scroll package, only if needed>",
      "purpose": "smooth-scroll",
      "version": "<exact project-compatible release>",
      "license": {"type": "<verified terms>", "source": "<primary source for that release>"},
      "npm": "<verified selected package name>"
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
  "operator_instructions_md": "<only the selected mode's setup, reduced-motion and cleanup instructions; no automatic install>"
}
```

Agent fills in specific picks based on the brief. Don't hardcode.
The example above illustrates the library branch. `mode: none` instead has
`libraries: []`, `key_animations: []`, native scrolling and no page transition.
`mode: css` has no JS libraries and marks each selected animation `library: css`.
Both retain an explicit reduced-motion decision. Source/license/rationale evidence
for every actual selected library is carried in the common binding at synthesis.

### Step 4 — Schema-validate + emit

Keep Step 3's actual parsed JSON object as `fragment` until validation and any
required licensing checks finish. In the trusted source Python scope, `repo` is
the explicit target root and `out` is `None` when `--out` was omitted, otherwise
the literal repository-relative output path. For named output, the authorized
caller captures `original_output_state` through P03 before generation (`None`
means originally absent, not overwrite permission). Then execute:

```python
import sys
import context_safety as safety
from design_contract import validate_spec
from review_contract import canonical_json

try:
    checked = validate_spec(fragment, "motion")
    payload = (canonical_json(checked["fragment"]) + "\n").encode("utf-8")
    if out is None:
        sys.stdout.buffer.write(payload)
    else:
        root = safety.checked_root(repo)
        relative = safety.selector_path(out)
        safety.atomic_write(
            root, relative, payload,
            mode=original_output_state["mode"] if original_output_state is not None else 0o600,
            expected=original_output_state, check_expected=True,
        )
        if safety.read_owned(root, relative, len(payload))[0] != payload:
            raise ValueError("Fragment output failed readback")
except (ValueError, OSError, UnicodeError) as error:
    print(f"ERROR [lintel/design]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

This emits only the validated fragment, including none/CSS choices, not a
success-shaped receipt. Invalid data emits no stdout or named file; publication
errors have a nonzero exit. Never pass stdout/special/absolute paths to the rooted
reader. For `--customer-share`, apply `/li:compliance-gate --check motion-licensing`
to the same data or an owned relative staging file before release; stdout does
not exempt the required check.

## Status protocol

- **DONE** — motion.json written and shared validation passed, including none/CSS branches
- **DONE_WITH_CONCERNS** — an optional candidate has unresolved terms; do not treat it
  as an approved dependency in renderable output
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks energy-direction (cant determine subtle vs kinetic)

## Pause-points

- Customer-share + unresolved dependency terms: retain the missing source/license
  decision and use the actual approval boundary; no blanket historical license assumption
- Brief mentions specific motion-library agent doesn't know: agent verifies + may need NEEDS_CONTEXT

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
