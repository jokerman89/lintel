---
name: "{{name}}"
layer: foundation
description: "{{description}}"
color: green
tools: Read, Bash
voice: internal
cli_support: []
---

# {{name}}

> DRAFT template. Instantiate only at an explicitly owned new target path. Replace the
> placeholders with valid YAML-quoted values and reviewed method text. Use a bare canonical
> kebab-case name; native wrapper/plugin spelling belongs to the actual adapter. An empty
> cli_support list is unknown declaration coverage, not universal support or activation.
> Validate the actual draft with the trusted `lib/frontmatter.sh` function
> `validate_lintel_frontmatter <file> skill`; it checks opening-block required-field
> presence only, not semantic validity or observed host execution.

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

- {{Output 1 — format, explicitly authorized target path or response channel}}
- {{Output 2}}

## Workflow

1. {{Validate literal inputs and applicable authority. Name the existing method/helper.}}
2. {{Perform the useful work using actual permitted host operations or an explicit fallback.}}
3. {{Verify the result; preserve errors, incomplete work and evidence limitations.}}

## Report format

{{Actual result, selected inputs, owned output, checks run, failures and next action.
Do not claim a hook, tool, independent reviewer or host execution from a declaration.}}

## Sub-skill: voice tier behavior

This skill's output voice resolves from the active pack (`resolve_pack_field voice.default_tier`; neutral default: `internal`). A pack may map a tier to a voice corpus (`resolve_pack_field voice.corpus`; none by default) and a voice-critic check that surfaces non-conforming output to the operator before it lands.

If `voice: internal`: direct, builder-talking-to-builder. No voice-corpus overhead.

If `voice: mixed`: this skill produces both internal and customer-facing output. The skill body explicitly tags which sections are which.

If `voice: custom`: the active pack defines the tier and any corpus/critic behavior.

## Compliance integration

If this skill touches any of the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default), state which here and which actual control supplies evidence. Preserve required-policy errors. A declared hook is not proof that it ran; do not claim enforcement from this template.

Preserve actual source attribution and required notices for adaptations. Add an optional
`license_note` only for real bundled material; do not infer originality or license
clearance from rewritten wording.

## Failure modes

- {{Failure 1: what can go wrong, how skill handles it (warn/block/fail), what operator sees}}
- {{Failure 2}}

## Examples

{{At least two concrete examples: valid inputs and expected output, plus a negative case
with its diagnostic and preserved state. Label illustrations separately from executed evidence.}}

## See also

- {{Related skill 1}}
- {{Related agent 1}}
- {{Relevant ADR}}
