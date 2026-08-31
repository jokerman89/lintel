# {{Skill name}}

> Template for new Lintel skills. Copy this file to `~/.claude/skills/li:<name>/SKILL.md` and fill the placeholders. `verify.sh --frontmatter` will reject any skill missing required fields.

```yaml
---
name: li-<name>                       # REQUIRED: kebab-case, must start with `li-`
description: <one-line summary of what the skill does — appears in slash-command picker>  # REQUIRED
color: <blue|purple|green|red|orange|yellow>   # REQUIRED: color tag for the picker
tools: <comma-separated list — only what the skill needs>  # REQUIRED
voice: <internal | mixed | custom>        # REQUIRED: resolves to the active pack's voice tier (default: internal)
cli_support: [claude-code, codex, copilot] # REQUIRED: list of CLIs where this skill is supported
                                            #   - claude-code: full support
                                            #   - codex: degraded — operator sequentializes manually
                                            #   - copilot: degraded — no slash-command mechanism
                                            #   omit any CLI where the skill genuinely won't work
license_note: <empty>                       # OPTIONAL: only if this skill bundles third-party content
---
```

## What this skill does

{{One paragraph. Concrete. What problem does it solve, what's the output?}}

## When to use it

- {{Bullet 1: trigger pattern}}
- {{Bullet 2: trigger pattern}}

## When NOT to use it

- {{Bullet 1: case where another skill fits better}}
- {{Bullet 2: case where the operator should handle manually}}

## Inputs

- {{Input 1 — type, source, validation rules}}
- {{Input 2}}

## Outputs

- {{Output 1 — format, where it lands (file path, stdout, AskUserQuestion, etc.)}}
- {{Output 2}}

## Sub-skill: voice tier behavior

This skill's output voice resolves from the active pack (`resolve_pack_field voice.default_tier`; neutral default: `internal`). A pack may map a tier to a voice corpus (`resolve_pack_field voice.corpus`; none by default) and a voice-critic check that surfaces non-conforming output to the operator before it lands.

If `voice: internal`: direct, builder-talking-to-builder. No voice-corpus overhead.

If `voice: mixed`: this skill produces both internal and customer-facing output. The skill body explicitly tags which sections are which.

If `voice: custom`: the active pack defines the tier and any corpus/critic behavior.

## Compliance integration

If this skill touches any of the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default), state which here and how the skill enforces (or surfaces) the rule.

## Failure modes

- {{Failure 1: what can go wrong, how skill handles it (warn/block/fail), what operator sees}}
- {{Failure 2}}

## Examples

{{Concrete example invocations + expected outputs. At least 2.}}

## See also

- {{Related skill 1}}
- {{Related agent 1}}
- {{Relevant ADR}}
