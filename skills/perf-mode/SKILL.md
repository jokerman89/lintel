---
name: perf-mode
layer: foundation
description: Use for the retained resource-advice entry point on heavy work; delegates to context-budget without changing model capacity.
color: orange
tools: Read, Write, Bash
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

# Perf mode compatibility

Use `/li:context-budget --advice` with the supplied arguments. The
[context-budget owner](../context-budget/SKILL.md#advice---advice) owns the method,
observations, interpretation and recovery. Do not maintain a second procedure here.

Retain numeric `--budget`, `--ceiling`, `--decay-policy`, `--cost-estimate`, `--off`
and the original observation flags. This route is advice only, not a larger model
window, host setting or paid service. Do not add another routing selector.

The executable compatibility route uses the same owned reference:

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
bash "$source_root/skills/context-budget/references/route.sh" --advice "$@"
```
