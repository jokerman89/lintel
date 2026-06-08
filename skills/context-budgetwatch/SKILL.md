---
name: context-budgetwatch
layer: foundation
v1_alias: [li-context-tokenwatch]
description: Thin alias for /li:context-budget --watch — manual context-bloat check (token + tool-call thresholds, recommendation to /clean or /context-save).
color: yellow
tools: Read, Bash
voice: internal
cli_support: [claude-code]
necessity: OPTIONAL
gap_if_skipped: "Operator loses the one-word /context-budgetwatch name; the identical threshold/continuous-watch check is still reachable via /li:context-budget --watch, so no capability is lost — only the shorter name."
---

You are the context-budgetwatch alias — a thin delegator to `/li:context-budget --watch`.

## What this skill does

Manual trigger for the context-bloat soft-warning system. Identical to:
```
/li:context-budget --watch
```
but preserves the `/li:context-budgetwatch` name (and the `li-context-tokenwatch` v1 alias). All behavior — token + tool-call thresholds, GREEN/YELLOW/RED verdict, `/clean` vs `/context-save` recommendation — lives in `/li:context-budget`'s **Watch mode** section.

## When to use

- Mid-session sense-check: "are we approaching context limits?"
- Long session has been running, want to know if a checkpoint is overdue
- Tool-call-heavy work (lots of file reads, lots of bash) — proactive check
- Pre-large-task: about to do something expensive, want to know runway first

## When NOT to use

- Fresh session — pointless
- Just ran `/context-save` — limits are about to reset on resume anyway
- Inside another skill's workflow — that's the wrong place to trigger this

## Inputs

Forwarded verbatim to `/li:context-budget --watch`:

- `--budget <yaml>` — override default thresholds (default: read from `~/.lintel/config.yaml` watcher section)
- `--quiet` — only emit if a threshold is crossed
- `--mode <soft|hard|both>` — which thresholds to check (default: both)

## Workflow

Delegate to `/li:context-budget --watch`, forwarding any `--budget` / `--quiet` / `--mode` flags unchanged:

```
/li:context-budget --watch [--budget <yaml>] [--quiet] [--mode <soft|hard|both>]
```

No behavior beyond that. See `/li:context-budget`'s "Watch mode" section for the threshold logic, report format, and failure modes.

## Status protocol

Inherits from `/li:context-budget`.

## Voice tier note

`voice: internal`. Operational meta-skill, engineering-internal.

## See also

- `/li:context-budget` — the underlying skill (`--watch` is this alias; default mode shows the budget breakdown)
- `/clean` — in-session lighter-weight clear
- `/context-save` — checkpoint + clean break for fresh session
- `/context-restore` — resume from checkpoint
- `~/.lintel/config.yaml` — watcher threshold config
