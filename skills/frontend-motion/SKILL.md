---
name: frontend-motion
layer: foundation
description: Use when a frontend brief needs an animation, scrolling or reduced-motion strategy, including no-animation and CSS-only choices.
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
  - cli: copilot
    level: full
---

You are the `frontend-motion` sub-skill — motion-director for the frontend-design family.

## What this skill does

Reads operator brief → MotionDirector chooses none, CSS or a justified
project-compatible motion library, then maps scrolling, key animations and
reduced-motion behavior → writes `motion.json` (schema_version: 1) with setup
instructions only for the actual selected mode.

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
- Optional `--customer-share` — selects the customer-share control boundary; no automatic license validator
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

The verified active design profile's actual motion tokens are the default.
The brief's energy-level justifies deviation from the tokens — never
from the reduced-motion floor.

Use `agents/frontend/MotionDirector.md` as the decision method with corpus hits
and verified profile tokens. Follow [axis ownership](../frontend-design/references/axis-ownership.md);
delegate only when a separate context is useful and actually available. The role
returns a draft; this caller owns Step 3's single publication. Decide in this order:

- **None:** native scrolling and no animation when movement adds no necessary information.
- **CSS:** use supported native transitions/scroll timelines when they meet the
  brief and reduced-motion requirements without a JS dependency.
- **Library:** only for an evidenced interaction need beyond those branches;
  compare the existing project runtime, framework/browser support, measured or
  explicitly unverified performance budget and maintenance/setup cost.

For a selected library, verify exact package/release/source/license and distinguish
runtime, plugin, editor and asset terms. Native scrolling is not a missing feature,
and a familiar vendor name is not evidence of fit or licensing.

Use actual supplied/verified license evidence or request an authorized lookup.
A role name does not prove current terms were checked.

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
      "name": "<selected project-compatible motion runtime>",
      "purpose": "scroll-choreography",
      "version": "<exact project-compatible release>",
      "license": {"type": "<verified terms>", "source": "<primary source for that release>"},
      "npm": "<verified selected package name, if applicable>"
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
      "library": "<selected runtime>"
    },
    {
      "name": "section-fade-up",
      "trigger": "section enters viewport 20%",
      "spec": "translateY(40px) → 0, opacity 0 → 1, duration 600ms ease-out-quart",
      "library": "<selected runtime>"
    },
    {
      "name": "image-parallax",
      "trigger": "scrub-tied",
      "spec": "background translateY(0) → translateY(-20%) over section",
      "library": "<selected runtime>"
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
from design_contract import emit_fragment

try:
    emit_fragment(fragment, "motion", repo=repo, out=out,
                  original_output_state=None if out is None else original_output_state)
except (ValueError, OSError, UnicodeError) as error:
    print(f"ERROR [lintel/design]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

This emits only the validated fragment, including none/CSS choices, not a
success-shaped receipt. Invalid data emits no stdout or named file; publication
errors have a nonzero exit. Never pass stdout/special/absolute paths to the rooted
reader. For `--customer-share`, use the [customer-share control boundary](../frontend-design/SKILL.md#customer-share-control-boundary)
on the same data or an owned relative staging file. Missing mandatory licensing
or policy observations remain unverified; stdout does not exempt them.
Use its named `motion-licensing` procedure for selected runtimes, plugins,
editors and assets. Required brief/profile obligations apply without this flag too.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
Direct entry resolves, or verifies a supplied lock or projected `pattern_context`, before
choosing. Mandatory clauses bound the motion, scroll-smoothing and page-transition decision;
defaults apply only where the brief did not decide; unconstrained choices follow the usual
Design DNA brief > profile > corpus rules. Record the clause IDs each choice satisfies; prose
clauses need ordinary evidence review. Pattern text is not evidence of licensing or
accessibility.

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
- Explicitly selected and authorized motion assets or verified profile references;
  no personal-home discovery or lazy-created asset folder

**Writes:**
- `motion.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `.claude/runtime/audit/frontend-motion-runs.jsonl`

**Calls into:**
- `agents/frontend/MotionDirector.md` (primary)
- The `motion-licensing` source-inspection procedure in the customer-share control
  boundary; `/li:compliance-gate` evaluates its recorded outcomes, not dependency licenses

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
- Customer-share: obtain the required `motion-licensing` evidence, then evaluate
  the actual controls through `/li:compliance-gate`; unresolved permission blocks sharing
- Future: propose a reviewed pattern at an explicitly selected authorized destination;
  no automatic personal write or activation follows from a motion decision
