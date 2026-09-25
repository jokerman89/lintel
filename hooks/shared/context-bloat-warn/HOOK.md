---
name: context-bloat-warn
tier: warn-only
event: PreToolUse (any)
fires_on: token estimate or tool-call count exceeds soft threshold
override: not applicable (informational only)
audit: not logged (high-volume; would generate noise)
---

# context-bloat-warn

Surfaces context-bloat warning at the 50k token / 80 tool-call soft threshold (configurable). Hooks the periodic check so the operator doesn't have to manually run `/li:context-budget --watch`.

## Behavior

- At soft threshold: prints one-line warning. Repeats no more than once per 5 tool-calls (don't spam).
- At hard threshold (80k / 130 calls): recommends `/li:pause`, then `/li:resume --from` in a fresh session.
- Reads thresholds from `~/.lintel/config.yaml` `watcher` section.

## Why warn-only

This optional warning cannot compact the host's active context. It surfaces recorded
observations against local thresholds; the operator decides. Blocking tool calls would
not reclaim context.

## Audit

Not logged. `/li:context-budget --watch` reports its actual observations separately;
neither a threshold file nor this hook's presence proves that telemetry was collected.
