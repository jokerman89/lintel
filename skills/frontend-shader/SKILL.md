---
name: frontend-shader
layer: foundation
description: Use when a frontend visual brief needs a shader or no-shader decision, source-backed library choices, performance limits and GPU fallbacks.
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

You are the `frontend-shader` sub-skill — shader-engineer for the v3.7 frontend-* family (Phase A2).

## What this skill does

Reads operator brief → ShaderEngineer chooses no shader or an evidenced,
project-compatible renderer, with visual thesis, source-backed snippet references,
GPU fallbacks and performance budget → writes `shader.json` (schema_version: 1).

Solo-invokable for component-mode or auto-invoked by the `/li:frontend-design` orchestrator in parallel-dispatch (Workflow Step 4) as the third parallel sub-skill (after typography + motion).

L-001-discipline: skill body is the contract. Agent at invocation produces specific library picks + GLSL recommendations. Don't pre-bake shader-snippets in the SKILL.md body.

Use the shader definition in the [shared design contract](../design-dna/references/design-contract.md).
Validate `visual_thesis: none` with `library: null` before GPU-only requirements.

## When to use

- Solo: "hero-background for enterprise SaaS landing — want a subtle mesh-gradient"
- Orchestrator-parallel: dispatched from `/li:frontend-design` Step 4
- Audit existing site: "extract shader-thesis from this site"

## When NOT to use

- Static site, no hero-visual ambition → shader overkill
- 3D scene-graph implementation needed → use the project's supported scene tooling (this method chooses, not builds, scenes)
- CSS-gradient is enough → agent surfaces "no shader needed" and short-circuits

## Inputs

- Required `--brief <text>` (one minimum)
- Optional `--visual-thesis <mesh-gradient|noise-field|fluid-sim|particle-system|displacement-warp|none>` — default: inferred from brief
- Optional `--perf-budget <low-end|mid-tier|high-end-only>` — affects GPU-fallback-strategy
- Optional `--out <path>` — output path (default: stdout solo, `$run_dir/shader.json` orchestrator)
- Optional `--customer-share` — selects the customer-share control boundary; no automatic license validator

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
thesis="${VISUAL_THESIS:-auto}"
perf="${PERF_BUDGET:-mid-tier}"
out="${OUT:-}"  # absent --out means stdout, not a path to validate
[ -z "$brief" ] && { echo "Need --brief"; exit 2; }
```

### Step 2 — ShaderEngineer agent dispatch

Use `agents/frontend/ShaderEngineer.md` as the decision method and follow
[axis ownership](../frontend-design/references/axis-ownership.md). Delegate only
when a separate context is useful and actually available; the role returns a
draft and this caller owns Step 3's single publication. First test whether static
artwork or a supported CSS treatment meets the brief: `visual_thesis: none`
and `library: null` are successful results. For an actual GPU need, compare
existing project tooling, required effect, framework/browser/device support,
measured or explicitly unverified cost, and fallback behavior. Choose a renderer
only on that evidence. A snippet/function library is not a renderer, and a
vendor name cannot establish device safety.

Retain exact selected-release/file terms and attribution for the renderer,
snippets, imports and artwork. Keep the existing `lygia_imports` field when
applicable; the field name does not require selecting that library.

Use actual supplied/verified license evidence or request an authorized lookup.
A role name does not prove current terms were checked.

### Step 3 — Produce `shader.json`

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_summary": "<one-line>",
  "visual_thesis": "<mesh-gradient | noise-field | fluid-sim | particle-system | displacement-warp | none>",
  "library": {
    "name": "<selected project-compatible renderer>",
    "version": "<exact selected release>",
    "license": {"type": "<verified selected terms>", "source": "<primary release/file source>"},
    "npm": "<selected package, if applicable>",
    "operator_instruction": "<authorized project-local setup; no automatic install>"
  },
  "glsl_snippets": [
    {
      "name": "mesh-gradient-3color",
      "purpose": "hero background",
      "source": "<actual selected file/release reference>",
      "notes": "<supported parameters and source/profile token mapping>"
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
    "explanation": "<selected device/browser/resolution and actual measured frame/GPU evidence, or explicitly unverified>"
  },
  "operator_instructions_md": "<setup for the actual selected renderer only; use verified profile/brief colors, real reduced-motion and no-WebGL fallbacks, and cleanup instructions; no automatic install>"
}
```

Agent fills in specific picks. Don't hardcode.

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
    emit_fragment(fragment, "shader", repo=repo, out=out,
                  original_output_state=None if out is None else original_output_state)
except (ValueError, OSError, UnicodeError) as error:
    print(f"ERROR [lintel/design]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

This emits only the validated fragment, including the no-shader branch, not a
success-shaped receipt. Invalid data emits no stdout or named file; publication
errors have a nonzero exit. Never pass stdout/special/absolute paths to the rooted
reader. For `--customer-share`, use the [customer-share control boundary](../frontend-design/SKILL.md#customer-share-control-boundary)
on the same data or an owned relative staging file. Missing mandatory licensing
or policy observations remain unverified; stdout does not exempt them.
Use its named `shader-licensing` procedure for selected renderers, snippets,
imports and assets. Required brief/profile obligations apply without this flag too.

### Step 5 — Visual-thesis === "none" short-circuit

Agent can return visual_thesis="none" if the brief doesn't warrant a shader. Skill body STILL emits valid JSON so orchestrator-Step-5 synthesis can handle `shader: null` gracefully.
This branch is validated before active-shader library/performance checks, not after
a failing mandatory-library check. Emit no canvas, GPU import or install instruction.
For an active shader, retain the real fallback/reduced-motion budget and selected
release/source/license evidence. A CSS media query alone does not stop a JS GPU loop.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
Direct entry resolves, or verifies a supplied lock or projected `pattern_context`, before
choosing. Mandatory clauses bound the shader decision; defaults apply only where the brief did
not decide; unconstrained choices follow the usual Design DNA brief > profile > corpus rules.
Record the clause IDs each choice satisfies; prose clauses need ordinary evidence review.
Pattern text is not evidence of licensing or accessibility.

## Status protocol

- **DONE** — shader.json written, schema valid, library + perf-budget non-empty (OR visual_thesis="none")
- **DONE_WITH_CONCERNS** — picked library has commercial-tier requirements (rare)
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks visual-direction (cant determine if shader needed)

## Pause-points

- Customer-share + library has obscure license → flag explicit
- Brief mentions specific shader-lib agent doesn't know → may need NEEDS_CONTEXT
- visual_thesis="none" — short-circuit confirmation to operator (no shader is fine)

## Integration

**Reads:**
- `--brief` argument
- Explicitly selected and authorized shader assets or verified profile references;
  no personal-home discovery or lazy-created asset folder

**Writes:**
- `shader.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `.claude/runtime/audit/frontend-shader-runs.jsonl`

**Calls into:**
- `agents/frontend/ShaderEngineer.md` (primary)
- The `shader-licensing` source-inspection procedure in the customer-share control
  boundary; `/li:compliance-gate` evaluates its recorded outcomes, not shader licenses

**Consumed by:**
- `/li:frontend-design` Workflow Step 5 (synthesis input — `shader` field)
- Operator direct (solo component-mode)

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

- Solo: review shader.json + apply to target project
- Orchestrator: parallel-dispatch returns to `/li:frontend-design` Step 5
- Customer-share: obtain the required `shader-licensing` evidence, then evaluate
  the actual controls through `/li:compliance-gate`; unresolved permission blocks sharing
- Future: propose a reviewed pattern at an explicitly selected authorized destination;
  no automatic personal write or activation follows from a shader decision
