---
name: li-frontend-typography
description: Use when a frontend brief needs font stacks, a type scale, variable-font axes or a loading strategy with source and licensing evidence.
---

> **Lintel on GitHub Copilot.** Generated from `skills/frontend-typography/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/frontend-typography/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/frontend-typography/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `frontend-typography` sub-skill — typography-curator for the frontend-design family.

## What this skill does

Reads operator brief → TypographyCurator selects font roles from the verified profile,
retained corpus evidence and actual project constraints, then maps variable axes,
size scale, line heights and loading strategy → writes `typography.json`
(schema_version: 1) with licensing context.

Solo-invokable for component-mode ("just typography please") or auto-invoked by the `/li-frontend-design` orchestrator in parallel-dispatch (Workflow Step 2).

L-001-discipline: skill body is the contract. Agent at invocation produces specific font choices and licensing-instructions. Don't pre-bake recommendations in the SKILL.md body.

Use the typography definition in the [shared design contract](../../../skills/design-dna/references/design-contract.md).
Retain actual profile/brief precedence and source/version/license/rationale evidence
for chosen fonts; licensed availability is not established by this example.

## When to use

- Solo: "ai-app for legal professionals — give me a typography stack"
- Orchestrator-parallel: dispatched from `/li-frontend-design` Step 2
- Brand-update: "customer-deck just landed, what should our heading-stack be?"

## When NOT to use

- Already have a typography.json — invoke `/li-frontend-design` directly with `--pattern <name>`
- Pure palette extraction — `/li-generate-style-learn` is right tool (palette ≠ typography)
- Font-rendering troubleshooting — that's CSS-debugging, not design-direction

## Inputs

- Required `--brief <text>` OR `--target-audience <description>` (one or other minimum)
- Optional `--mood <serif-display|tight-mono|variable-experimental|editorial|techy>` — override default mood-inference
- Optional `--out <path>` — output path (default: stdout if solo, `$run_dir/typography.json` if orchestrator-parallel)
- Optional `--customer-share` — selects the customer-share control boundary; no automatic license validator

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
audience="${TARGET_AUDIENCE:-}"
mood="${MOOD:-auto}"
out="${OUT:-}"  # absent --out means stdout, not a path to validate
[ -z "$brief$audience" ] && { echo "Need --brief OR --target-audience"; exit 2; }
```

### Step 2 — Corpus query + TypographyCurator agent dispatch

Query the design corpus first (ADR-0015 — retrieval before generation):

```bash
python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/search.py" "<mood + audience keywords>" --domain typography -n 3
```

The verified active design profile's actual font roles are the starting point.
Corpus pairings + the brief justify deviation;
no deviation needed → the profile stack IS the answer. python3 absent → Read
`skills/design-dna/data/typography.csv` directly (73 pairings, greppable).

Use `agents/frontend/TypographyCurator.md` as the decision method with the corpus
hits + verified profile. Follow [axis ownership](../../../skills/frontend-design/references/axis-ownership.md);
delegate only when a separate context is useful and actually available. The role
returns a draft; this caller owns Step 3's single publication. Compare candidates
against the actual audience, language/glyph coverage,
heading/body/mono roles, density, available weights/axes, fallback metrics and
project loading constraints. Prefer an already suitable selected font or system
fallback over an unnecessary dependency. A vendor label, installed font or
corpus hit is not a license grant; retain exact source/release evidence.

Use actual supplied/verified license evidence or request an authorized lookup.
Neither a role name nor a font recommendation proves current terms were checked.

### Step 3 — Produce `typography.json`

```json
{
  "schema_version": 1,
  "generated_at": "<iso-8601>",
  "brief_summary": "<one-line>",
  "mood": "<inferred-or-specified>",
  "font_stacks": [
    {
      "role": "heading",
      "family": "<selected heading family>",
      "fallback_stack": ["<observed compatible fallback>", "serif"],
      "variable_axes": {"weight": [400, 700], "optical_size": [14, 96]},
      "loading_strategy": "self-hosted via @font-face",
      "license": {
        "type": "<verified terms for the selected release>",
        "source": "<actual release/file source>",
        "operator_instruction": "Verify the selected font release and license, then use an explicitly authorized project asset path and record its source; do not create or scan a personal asset folder"
      }
    },
    {
      "role": "body",
      "family": "<selected body family>",
      "fallback_stack": ["<observed compatible fallback>", "sans-serif"],
      "variable_axes": {"weight": [400, 600], "slant": [-10, 0]},
      "loading_strategy": "<project-supported, authorized delivery strategy>",
      "license": {"type": "<verified terms>", "source": "<actual source>", "operator_instruction": "<required setup and notices; no automatic fetch>"}
    },
    {
      "role": "mono",
      "family": "<selected mono family, if needed>",
      "fallback_stack": ["monospace"],
      "variable_axes": {"weight": [400, 700]},
      "loading_strategy": "<project-supported, authorized delivery strategy>",
      "license": {"type": "<verified terms>", "source": "<actual source>", "operator_instruction": "<required setup and notices; no automatic fetch>"}
    }
  ],
  "size_scale": {
    "ratio": 1.25,
    "base_px": 16,
    "scale": ["xs:0.75rem", "sm:0.875rem", "base:1rem", "lg:1.125rem", "xl:1.25rem", "2xl:1.5rem", "3xl:1.875rem", "4xl:2.25rem", "5xl:3rem", "6xl:3.75rem", "7xl:4.5rem"]
  },
  "line_heights": {
    "tight": 1.1,
    "snug": 1.25,
    "normal": 1.5,
    "relaxed": 1.625,
    "loose": 2
  },
  "letter_spacing": {
    "tight": "-0.02em",
    "normal": "0",
    "wide": "0.05em",
    "wider": "0.1em"
  },
  "operator_instructions_md": "# Typography setup\n\nVerify the actual release/source/license for each selected font. Use an explicitly selected authorized project asset path or approved delivery source; record the reference and required evidence before customer sharing. Do not install, fetch, publish or create personal asset directories from this example."
}
```

Agent fills in specific choices based on the brief. Don't pre-bake.

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
    emit_fragment(fragment, "typography", repo=repo, out=out,
                  original_output_state=None if out is None else original_output_state)
except (ValueError, OSError, UnicodeError) as error:
    print(f"ERROR [lintel/design]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

This emits only the validated fragment, not a success-shaped validation receipt.
Invalid data emits no stdout or named file; publication errors have a nonzero exit.
Never pass stdout/special/absolute paths to the rooted-file reader. Its existing
CLI remains valid for an already written, explicitly owned relative file.
For `--customer-share`, use the [customer-share control boundary](../../../skills/frontend-design/SKILL.md#customer-share-control-boundary)
on the same data or an owned relative staging file before release. Missing
mandatory licensing/policy evidence remains unverified; stdout is no exemption.
Use its named `font-licensing` procedure for the exact font releases and intended
use. Required obligations from the brief/profile apply even without this flag.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
Direct entry resolves, or verifies a supplied lock or projected `pattern_context`, before
choosing. Mandatory clauses bound the typography decision; defaults apply only where the brief
did not decide; unconstrained choices follow the usual Design DNA brief > profile > corpus
rules. Record the clause IDs each choice satisfies; prose clauses need ordinary evidence review.
Pattern text is not evidence of licensing or accessibility.

## Status protocol

- **DONE** — typography.json written, schema valid
- **DONE_WITH_CONCERNS** — an optional font's terms are unresolved; not permission to use it where licensing is mandatory
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks audience-direction

## Pause-points

- Customer-share + commercial-license font: surface licensing-instruction explicit + ask for confirm before proceeding
- Brief mentions specific font operator doesn't know about: agent verifies at invocation, surface if unclear

## Integration

**Reads:**
- `--brief` argument
- Explicitly selected and authorized licensed-font assets or verified profile
  references; no personal-home discovery or lazy-created asset folder

**Writes:**
- `typography.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `.claude/runtime/audit/frontend-typography-runs.jsonl`

**Calls into:**
- `agents/frontend/TypographyCurator.md` (primary)
- The `font-licensing` source-inspection procedure in the customer-share control
  boundary; `/li-compliance-gate` evaluates its recorded outcomes, not the font license

**Consumed by:**
- `/li-frontend-design` Workflow Step 5 (synthesis input)
- Operator direct (solo component-mode)

## Anti-patterns

- **Pre-baking specific font recommendations in SKILL.md body** — L-001 violation. Skill body = contract; agent at invocation picks from current font landscape.
- **Hardcoding licensing claims** — L-003: font licenses change. Agent verifies at invocation.
- **Producing typography.json without `schema_version`** — M-5 compliance.

## Failure recovery

- Agent fails to pick (brief too vague): NEEDS_CONTEXT with a specific clarification-question
- Font-recommendation references unavailable font: agent re-picks; logs the attempt
- Schema validation fails: BLOCKED, return diff

## Recommended next steps after invocation

- Solo: review typography.json + drop in target project
- Orchestrator: parallel-dispatch returns to `/li-frontend-design` Step 5 synthesis
- Customer-share: obtain the required `font-licensing` evidence, then evaluate
  the actual controls through `/li-compliance-gate`; unresolved permission blocks sharing
