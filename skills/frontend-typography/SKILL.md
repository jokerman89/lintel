---
name: frontend-typography
layer: foundation
description: Frontend design-director sub-skill — picks font-family-stacks + variable-axes-config + size-scale + line-heights + font-loading-strategy from brief. Solo-invokable.
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

You are the `frontend-typography` sub-skill — typography-curator for the frontend-design family.

## What this skill does

Reads operator brief → TypographyCurator agent picks font-stack from the font-recommendation-tree (Google Fonts | Pangram | Velvetyne | Recursive | Fraunces | Future Fonts) + maps variable-axes + size-scale + line-heights + font-loading-strategy → writes `typography.json` (schema_version: 1) with licensing-context.

Solo-invokable for component-mode ("just typography please") or auto-invoked by the `/li:frontend-design` orchestrator in parallel-dispatch (Workflow Step 2).

L-001-discipline: skill body is the contract. Agent at invocation produces specific font choices and licensing-instructions. Don't pre-bake recommendations in the SKILL.md body.

## When to use

- Solo: "ai-app for legal professionals — give me a typography stack"
- Orchestrator-parallel: dispatched from `/li:frontend-design` Step 2
- Brand-update: "customer-deck just landed, what should our heading-stack be?"

## When NOT to use

- Already have a typography.json — invoke `/li:frontend-design` directly with `--pattern <name>`
- Pure palette extraction — `/li:generate-style-learn` is right tool (palette ≠ typography)
- Font-rendering troubleshooting — that's CSS-debugging, not design-direction

## Inputs

- Required `--brief <text>` OR `--target-audience <description>` (one or other minimum)
- Optional `--mood <serif-display|tight-mono|variable-experimental|editorial|techy>` — override default mood-inference
- Optional `--out <path>` — output path (default: stdout if solo, `$run_dir/typography.json` if orchestrator-parallel)
- Optional `--customer-share` — triggers license-validation strict-mode

## Workflow

### Step 1 — Parse + warm context

```bash
brief="${BRIEF:-${1:-}}"
audience="${TARGET_AUDIENCE:-}"
mood="${MOOD:-auto}"
out="${OUT:-/dev/stdout}"
[ -z "$brief$audience" ] && { echo "Need --brief OR --target-audience"; exit 2; }
```

### Step 2 — Corpus query + TypographyCurator agent dispatch

Query the design corpus first (ADR-0015 — retrieval before generation):

```bash
python3 skills/design-dna/scripts/search.py "<mood + audience keywords>" --domain typography -n 3
```

The active design profile's font roles are the starting point (default anthropic-default:
Poppins display / Lora body / JetBrains Mono). Corpus pairings + the brief justify deviation;
no deviation needed → the profile stack IS the answer. python3 absent → Read
`skills/design-dna/data/typography.csv` directly (73 pairings, greppable).

Hand off to `agents/frontend/TypographyCurator.md` with the corpus hits + profile in context. Agent reads brief + (optionally) audience + mood. Picks font-stack from the recommendation-tree:

- **Google Fonts (free, no-license-friction):** Inter, IBM Plex, Space Grotesk, JetBrains Mono, Fraunces (variable), Recursive (variable)
- **Pangram Pangram (commercial license required):** PP Editorial New, PP Neue Montreal, PP Mori, PP Right Grotesk
- **Velvetyne (free, open-source experimental):** Cirrus, Compagnon, Reross
- **Future Fonts (early-access licensing):** various variable-axes-heavy choices
- **System stack (zero-license):** SF Pro / Segoe UI / system-ui fallback

Agent verifies current licensing terms at invocation (L-003: don't trust stale claims about font-licensing).

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
      "family": "PP Editorial New",
      "fallback_stack": ["Fraunces", "Georgia", "serif"],
      "variable_axes": {"weight": [400, 700], "optical_size": [14, 96]},
      "loading_strategy": "self-hosted via @font-face",
      "license": {
        "type": "commercial",
        "source": "pangrampangram.com",
        "operator_instruction": "License at pangrampangram.com → drop .woff2 in ~/.lintel/brand/fonts/ → frontend-design will reference by relative path"
      }
    },
    {
      "role": "body",
      "family": "Inter",
      "fallback_stack": ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      "variable_axes": {"weight": [400, 600], "slant": [-10, 0]},
      "loading_strategy": "Google Fonts CDN",
      "license": {"type": "free", "source": "Google Fonts", "operator_instruction": "Include via <link> tag or @import"}
    },
    {
      "role": "mono",
      "family": "JetBrains Mono",
      "fallback_stack": ["Cascadia Code", "Menlo", "Consolas", "monospace"],
      "variable_axes": {"weight": [400, 700]},
      "loading_strategy": "Google Fonts CDN",
      "license": {"type": "free", "source": "Google Fonts", "operator_instruction": "Include via <link> tag"}
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
  "operator_instructions_md": "# Typography setup\n\n## Pangram (heading font)\n1. License at pangrampangram.com\n2. Drop .woff2 in ~/.lintel/brand/fonts/PP-Editorial-New.woff2\n3. frontend-design will reference\n\n## Inter + JetBrains Mono\nAlready free via Google Fonts.\n```html\n<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;700&display=swap\" rel=\"stylesheet\">\n```"
}
```

Agent fills in specific choices based on the brief. Don't pre-bake.

### Step 4 — Schema-validate + emit

```bash
# Sanity: schema_version present, font_stacks non-empty
jq -e '.schema_version == 1 and (.font_stacks | length > 0)' "$out" || { echo "Schema invalid"; exit 1; }

# Customer-share mode: validate licensing claims
if [ -n "${CUSTOMER_SHARE:-}" ]; then
  /li:compliance-gate --check font-licensing "$out"
fi
```

## Status protocol

- **DONE** — typography.json written, schema valid
- **DONE_WITH_CONCERNS** — font-license-check borderline (e.g., Pangram referenced without operator-confirmation of the license)
- **BLOCKED** — brief unparsable, OR customer-share license-check failed
- **NEEDS_CONTEXT** — brief lacks audience-direction

## Pause-points

- Customer-share + commercial-license font: surface licensing-instruction explicit + ask for confirm before proceeding
- Brief mentions specific font operator doesn't know about: agent verifies at invocation, surface if unclear

## Integration

**Reads:**
- `--brief` argument
- `~/.lintel/brand/fonts/` (for operator-licensed fonts; lazy-created)

**Writes:**
- `typography.json` (stdout default, $OUT-path if orchestrator)
- Audit-log: `.claude/runtime/audit/frontend-typography-runs.jsonl`

**Calls into:**
- `agents/frontend/TypographyCurator.md` (primary)
- `/li:compliance-gate --check font-licensing` (if --customer-share)

**Consumed by:**
- `/li:frontend-design` Workflow Step 5 (synthesis input)
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
- Orchestrator: parallel-dispatch returns to `/li:frontend-design` Step 5 synthesis
- Customer-share: pair with `/li:compliance-gate` for final license-audit
