# {{AgentName}}

> Template for new Lintel agents. Copy this file to `~/.claude/agents/<AgentName>.md` (or `<repo>/.claude/agents/<AgentName>.md` for repo-level) and fill the placeholders. `verify.sh --frontmatter` will reject any agent missing required fields.

```yaml
---
name: <AgentName>                          # REQUIRED: CamelCase or kebab-case per family convention
description: <one-line description shown when main-agent picks an agent>  # REQUIRED
color: <blue|purple|green|red|orange|yellow>   # REQUIRED
tools: <Read, Grep, Glob, Bash, Edit, Write — only what is needed>  # REQUIRED
voice: <internal | mixed | custom>         # REQUIRED: resolves to the active pack's voice tier (default: internal)
cli_support: [claude-code, codex, copilot] # REQUIRED: source/discovery hints, not runtime evidence
                                            #   Bind exact CLI/desktop/IDE/cloud surfaces through lib/cli-tiers.yaml
                                            #   Preserve documented native support; record actual host observations separately
                                            #   Copilot: generated custom agent; degraded when a required native facility is absent
tier: <permissive | restricted>             # REQUIRED FOR PROMOTED AGENTS ONLY: license tier of upstream this agent ports
                                            #   Legacy license hint, never a tool-permission grant or model tier
                                            #   Consult actual retained licenses/notices and unknowns; no blanket reuse permission
upstream_url: <retained source URL>         # OPTIONAL: known third-party source only; never invent for original work
last_verified: YYYY-MM-DD                   # OPTIONAL: actual upstream verification only, not an inferred import date
---
```

See [Legacy role metadata](../../shims/universal/ADAPTER.md#legacy-role-metadata)
for the evidence boundary. Optional native `memory` and `model` fields remain valid
where supported; they do not promise cross-host memory or force a model. Preserve
known derivative notices and distinguish an unknown import revision from a later
source-record check. Do not manufacture license permission from a metadata label.

You are a {{role}} for this repo.

## What this agent does

{{Concrete description of the agent's job. One paragraph.}}

## When to invoke

- {{Trigger 1: task pattern that fits this agent}}
- {{Trigger 2}}

## When NOT to invoke

- {{Bullet 1: case where another agent is better}}
- {{Bullet 2: case where main agent should handle directly without delegation}}

## Workflow

1. {{Step 1: what the agent does first}}
2. {{Step 2}}
3. {{Step 3}}

## Report format

Structured output. Main agent reads this as context, so structure > prose:

```
{{Define the exact output schema this agent produces — markdown headers,
yaml blocks, or json — make it parseable by the main agent.}}
```

## Edge cases / what to do when blocked

- {{Edge case 1: how the agent handles it}}
- {{Edge case 2}}

## Voice tier behavior

This agent's output voice resolves from the active pack (`resolve_pack_field voice.default_tier`; neutral default: `internal`). {{One sentence on how that affects this agent's prose.}}

## License note (only if tier: restricted)

{{Required field for restricted-tier agents. State the license + what operator must NOT do with this agent's content.}}

Example: "This agent ports content from `trailofbits/skills` (CC-BY-SA-4.0). Invoking this agent from its install path is unrestricted. Copy-pasting any content from this agent's output into a permissively-licensed (e.g. MIT) repo would require the derivative to be CC-BY-SA-4.0 — which is incompatible with MIT defaults. Use as an installed tool, never as code to inline."

## Temporary heads-ups

If the agent needs to know something temporary (migrating from X to Y, deprecating a flow, etc.):

```markdown
## TEMP — YYYY-MM-DD — <short summary>

<2-3 sentence heads-up>
Remove this block when no longer relevant.
```

Remove when no longer needed. Difference vs `tasks/lessons.md`: lessons are permanent rules from corrections; heads-ups are short-term context.
