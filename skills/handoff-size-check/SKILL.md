---
name: handoff-size-check
layer: foundation
description: Use for the retained handoff-budget entry point; delegates selected artifacts and supplied observations to context-budget.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: full
---

# Handoff-size check compatibility

Use `/li:context-budget --handoff` with the supplied selection and observation
arguments. The [context-budget owner](../context-budget/SKILL.md#handoff---handoff)
owns artifact admission, interpretation, policy boundaries and recovery.
PLAN/CAPTURE invoke that owner directly; this name remains compatible.

Retain explicit `--map`, the verified lifecycle's `LINTEL_WORK_MAP`, literal
`--warm-path`, observation/reserve flags and original work/profile/task identities.
Advisory unknown headroom remains unknown. Caller skip flags mean not run, never
a pass or a waiver of a required bound. Do not add another routing selector.

For mapped work, the compatibility recipe calls the same owned reference:

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
bash "$source_root/skills/context-budget/references/route.sh" --handoff "$@"
```

Legacy positional plans and `--plan <path>` keep the owner's
[explicit selected-plan/manual join](../context-budget/SKILL.md#legacy-selected-plan).
They are not passed to the mapped reader, dropped or converted into an invented map.
