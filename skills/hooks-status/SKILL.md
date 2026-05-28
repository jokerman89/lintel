---
name: hooks-status
layer: foundation
description: Reader för hooks.jsonl — surface aktiva-vs-döda hooks + override-pattern + trigger-counts. Stänger hooks-observation-loopen.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `hooks-status` skill — reader för `~/.lintel/audit/hooks.jsonl`. Stänger backlog 1.2 (consume hooks.jsonl) + 1.7 (hook usage status) som en skill.

## What this skill does

Lintel har 15 hooks installerade. Hooks.jsonl skrivs på override-attempts + trigger-events, men ingenting läser den. Denna skill:

1. Aggregerar trigger-counts per hook (senaste N dagar)
2. Identifierar override-pattern ("customer-data-block overridad 6× denna vecka" → flag-worthy)
3. Surface:ar döda hooks (zero triggers > 30 dagar — candidate för cleanup)
4. Korrelerar override-trender med skills (via run_id cross-reference till usage-log)

Closes self-observation-spine loop per Cohort 2 mål: data skriven → data läst → operatör ser pattern.

## When to use

- "Vilka hooks fires faktiskt?" → `/li:hooks-status --triggers --days 30`
- "Har jag overridat för mycket?" → `/li:hooks-status --overrides`
- "Vilka hooks är döda?" → `/li:hooks-status --dead --days 90` (no trigger past 90 days)
- Maintenance-pre-flight: kombineras med `/li:usage-log --report` för full observation-pass

## When NOT to use

- Real-time hook-firing detection — denna är retroactive, läser jsonl efter event
- Hook design eller install — `bin/li-doctor` har hook-install-state check

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
- Filter lines med `override: true`
- Group by `hook_name` + `override_reason`
- Surface: "hook X overridad N× (reasons: ...)"
- Flag if N > 5 for any hook in past 7 days (signals friction)

**`--dead --days N`:**
- For each registered hook (from `hooks/`-dir scan), check last trigger
- If no trigger past N days → flag as candidate cleanup
- Surface: hook_name | days_since_last_trigger | install_state

### Step 3 — Cross-reference with usage-log (optional via `--correlate`)

Om `--correlate` flag:
- Read `usage-*.jsonl` (usage-log writer output)
- Match override-events to invoked skills via `run_id`
- Surface: "när hook X overrides, skill Y invokeras N% av tiden" → causal-link hint

### Step 4 — Render report

Markdown table-output till stdout. Operatör pipear till less eller redirectar till fil.

## Voice tier behavior

`voice: internal`. Operatör-observability. Ingen voice-gate.

## Status protocol

- **DONE** — report rendered
- **DONE_WITH_CONCERNS** — report rendered men hooks.jsonl är malformed på rader (skip + count i report)
- **BLOCKED** — `~/.lintel/audit/hooks.jsonl` permissions deny read
- **NEEDS_CONTEXT** — invocation utan view-flag (`--triggers` / `--overrides` / `--dead`)

## Hop-in support

YES — pure-reader skill, solo-invocable any time.

## Integration

**Reads:**
- `~/.lintel/audit/hooks.jsonl` (canonical hooks-audit log)
- `~/.lintel/audit/usage-*.jsonl` (optional cross-reference via `--correlate`)
- `hooks/`-dir scan (för dead-hook detection — vilka hooks är installerade)

**Writes:**
- stdout (markdown report)

**Consumed by:**
- Operator (solo-invocation pattern)
- `/li:maintenance` (5.3 — feed observation-data)

## Anti-patterns

- **Modifying hooks.jsonl** — denna är reader-only. Audit-log är immutable.
- **Streaming live triggers** — denna processar batches. Real-time hook-watching är `inotify`/`fswatch`-jobb, ej denna.

## Failure recovery

- Malformed JSON lines: skip + count + report at end ("3 malformed lines skipped").
- Empty hooks.jsonl: surface "No hook events recorded yet."
- usage-log not present for `--correlate`: warn + proceed without correlation.

## Recommended next steps after invocation

- För full picture: pair med `/li:usage-log --report` (sibling skill)
- Vid override-spike: surface till operator-decision om hook-tuning behövs
- Vid dead-hook: `/li:doctor --hooks` validerar installed-state innan cleanup-decision
