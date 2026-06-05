---
name: hooks-status
layer: foundation
description: Reader for hooks.jsonl — surface active-vs-dead hooks + override patterns + trigger counts. Closes the hooks-observation loop.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `hooks-status` skill — reader for `~/.lintel/audit/hooks.jsonl`. Closes backlog 1.2 (consume hooks.jsonl) + 1.7 (hook usage status) as one skill.

## What this skill does

Lintel has 15 hooks installed. Hooks.jsonl is written on override attempts + trigger events, but nothing reads it. This skill:

1. Aggregates trigger counts per hook (last N days)
2. Identifies override patterns ("customer-data-block overridden 6× this week" → flag-worthy)
3. Surfaces dead hooks (zero triggers > 30 days — candidate for cleanup)
4. Correlates override trends with skills (via run_id cross-reference to usage-log)

Closes the self-observation-spine loop per Cohort 2 goal: data written → data read → operator sees pattern.

## When to use

- "Which hooks actually fire?" → `/li:hooks-status --triggers --days 30`
- "Have I overridden too much?" → `/li:hooks-status --overrides`
- "Which hooks are dead?" → `/li:hooks-status --dead --days 90` (no trigger past 90 days)
- Maintenance pre-flight: combine with `/li:usage-log --report` for a full observation pass

## When NOT to use

- Real-time hook-firing detection — this is retroactive, reads the jsonl after the event
- Hook design or install — `bin/li-doctor` has a hook-install-state check

## Workflow

### Step 1 — Read hooks.jsonl

```bash
HOOKS_LOG="$HOME/.lintel/audit/hooks.jsonl"
if [ ! -f "$HOOKS_LOG" ]; then
  echo "No hooks.jsonl yet. Hooks log at first override or trigger event."
  exit 0
fi
```

### Step 2 — Aggregate per requested view

**`--triggers --days N`:**
- Parse jsonl, filter by `ts` within last N days
- Group by `hook_name`, count triggers
- Surface table: hook_name | trigger_count | last_trigger_ts

**`--overrides`:**
- Filter lines with `override: true`
- Group by `hook_name` + `override_reason`
- Surface: "hook X overridden N× (reasons: ...)"
- Flag if N > 5 for any hook in past 7 days (signals friction)

**`--dead --days N`:**
- For each registered hook (from `hooks/`-dir scan), check last trigger
- If no trigger past N days → flag as candidate cleanup
- Surface: hook_name | days_since_last_trigger | install_state

### Step 3 — Cross-reference with usage-log (optional via `--correlate`)

If `--correlate` flag:
- Read `usage-*.jsonl` (usage-log writer output)
- Match override events to invoked skills via `run_id`
- Surface: "when hook X overrides, skill Y is invoked N% of the time" → causal-link hint

### Step 4 — Render report

Markdown table output to stdout. Operator pipes to less or redirects to a file.

## Voice tier behavior

`voice: internal`. Operator observability. No voice gate.

## Status protocol

- **DONE** — report rendered
- **DONE_WITH_CONCERNS** — report rendered but hooks.jsonl is malformed on some lines (skip + count in report)
- **BLOCKED** — `~/.lintel/audit/hooks.jsonl` permissions deny read
- **NEEDS_CONTEXT** — invocation without a view flag (`--triggers` / `--overrides` / `--dead`)

## Hop-in support

YES — pure-reader skill, solo-invocable any time.

## Integration

**Reads:**
- `~/.lintel/audit/hooks.jsonl` (canonical hooks-audit log)
- `~/.lintel/audit/usage-*.jsonl` (optional cross-reference via `--correlate`)
- `hooks/`-dir scan (for dead-hook detection — which hooks are installed)

**Writes:**
- stdout (markdown report)

**Consumed by:**
- Operator (solo-invocation pattern)
- `/li:maintenance` (5.3 — feed observation-data)

## Anti-patterns

- **Modifying hooks.jsonl** — this is reader-only. The audit log is immutable.
- **Streaming live triggers** — this processes batches. Real-time hook-watching is an `inotify`/`fswatch` job, not this.

## Failure recovery

- Malformed JSON lines: skip + count + report at end ("3 malformed lines skipped").
- Empty hooks.jsonl: surface "No hook events recorded yet."
- usage-log not present for `--correlate`: warn + proceed without correlation.

## Recommended next steps after invocation

- For the full picture: pair with `/li:usage-log --report` (sibling skill)
- On an override spike: surface to operator decision on whether hook-tuning is needed
- On a dead hook: `/li:doctor --hooks` validates installed-state before a cleanup decision
