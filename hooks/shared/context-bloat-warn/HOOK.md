---
name: context-bloat-warn
tier: warn-only
event: PreToolUse (any)
fires_on: token estimate or tool-call count exceeds soft threshold
override: not applicable (informational only)
audit: not logged (high-volume; would generate noise)
---

# context-bloat-warn

Surfaces context-bloat warning at the 50k token / 80 tool-call soft threshold (configurable). Hooks the periodic check so the operator doesn't have to manually run `/context-budgetwatch`.

## Behavior

- At soft threshold: prints one-line warning. Repeats no more than once per 5 tool-calls (don't spam).
- At hard threshold (80k / 130 calls): prints stronger warning recommending `/context-save` immediately.
- Reads thresholds from `~/.jstack/config.yaml` `watcher` section.

## Why warn-only

Claude cannot mid-session compact context. The skill is honest about this — it surfaces, operator decides. Blocking tool calls past the threshold would just frustrate without solving the problem.

## Audit

Skipped — would generate too much noise. The `/context-budgetwatch` skill writes explicit audit events when operator invokes it.
