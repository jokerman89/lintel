---
name: maintenance
layer: foundation
description: On-demand maintenance — force-compact + static-path monitoring + token-cost simulation. Operator-request 5.3. Bygger på usage-log (1.1) som data-source.
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `maintenance` skill — on-demand Lintel-maintenance pass.

## What this skill does

Operator-request 5.3 (post Cohort 2 dependency 1.1 usage-log landed): on-demand maintenance system med 3 modes:

1. **`--force-compact`** — clear excess context beyond what's already compacted. Operator allows heavy contexting för heavy tasks, then reclaims on demand.

2. **`--monitor-paths`** — watch canonical paths för drift/missing. Would have caught 0.4 (tasks/personas+memory missing per LAYERS.md). Static-path verification.

3. **`--simulate-tokens <workflow>`** — "what would `/li:cycle --mode customer-engagement` cost?" Depends på 1.1 (usage-log) för real numbers; otherwise heuristics.

Closes operator-request 5.3 + integrates med L-002 (grep-first-pattern adapted för paths).

## When to use

- "Min Lintel känns slö" → `/li:maintenance --force-compact`
- "Är allt på plats?" → `/li:maintenance --monitor-paths`
- "Vad skulle X kosta?" → `/li:maintenance --simulate-tokens customer-engagement`
- "Vad rostar?" → `/li:maintenance --rust-report` (skills with <2 invocations past 30 days, via usage-log)

## When NOT to use

- Mid-task work (denna pausar för diagnostic)
- Single-file-check — `/li:doctor --quick` is faster
- Pre-implementation cost estimate — `/li:cycle --dry-run` har inline cost

## Workflow per mode

### `--force-compact`

```bash
# Identify compactable state:
# 1. /context-save snapshots > N days old → archive
find ~/.lintel/state -name "*.md" -mtime +30 | xargs -r tar -czf ~/.lintel/archive/old-state-$(date +%Y%m%d).tar.gz

# 2. usage.jsonl > 90 days old → already auto-rotated by usage-log skill
# (verify via /li:usage-log --report)

# 3. Build/draft directories: clean up after successful PRs
find ~/.lintel/draft -mtime +7 -type d -empty -delete

# 4. .gstack/ session markers > 120 min → already cleaned by hook
# (no action)

# 5. Provenance records: keep latest per artifact, archive older
# (specific to /generate-* outputs)
```

Surface report: "Reclaimed <X> MB. Compaction summary: ..."

### `--monitor-paths`

Static-path manifest (loaded från config or hard-coded):

```yaml
load-bearing_paths:
  - tasks/lessons.md          # required per LAYERS.md
  - tasks/personas.md          # required per LAYERS.md (Cohort 1 0.4)
  - tasks/memory.md            # required per LAYERS.md (Cohort 1 0.4)
  - ~/.lintel/profile.yaml     # session-config
  - ~/.lintel/audit/           # observation spine writes here
  - skills/                    # canonical skill location
  - agents/                    # canonical agent location

deprecated_paths_check:
  - $HOME/.jstack/             # post Phase A: should be empty or migrated

required_files_in_paths:
  - skills/CATALOG.md          # auto-generated, should exist post-Cohort-2 merge
  - tasks/lessons.md           # canonical lessons
```

For each path:
- Check existence
- Check writeable (om relevant)
- Check non-empty (om expected)
- Check no-drift (deprecated paths should be empty)

Surface diff vs expected state. PASS / WARN / FAIL per path.

### `--simulate-tokens <workflow>`

Read mode-presets från `skills/cycle/SKILL.md` mode_envelopes:

```yaml
hotfix:           ~5k tokens
customer-engagement: ~40-80k tokens
internal-tool:    ~25-50k tokens
demo-prep:        ~15-25k tokens
research-dive:    ~10-20k tokens
```

Cross-reference med usage-log (post-1.1 land):
- Read `~/.lintel/audit/usage-*.jsonl` past 30 days
- Filter by skill-list för chosen workflow
- Compute median + p95 tokens-est
- Surface: "Estimated: median <X>k tokens (p95: <Y>k) baserat på N prior invocations"

If no usage-log data: fall back till mode-envelope hard-coded estimates.

### `--rust-report`

Read usage-log past 30 days:
- For each skill in `skills/`, count invocations
- Flag skills med < 2 invocations som rust candidates
- Group by category: never-invoked / rare / cold / active
- Surface table för operator-review

Pairs naturally med `/li:catalog --trends` (Cohort 2 1.6 output).

## Voice tier behavior

`voice: internal`. Operator-internal maintenance pass.

## Status protocol

- **DONE** — maintenance pass complete för selected mode
- **DONE_WITH_CONCERNS** — pass complete med warnings (e.g., deprecated paths still present)
- **BLOCKED** — `~/.lintel/` permissions deny read/write
- **NEEDS_CONTEXT** — `--simulate-tokens` utan workflow-arg

## Pause-points

- `--force-compact` skulle reclaim > 500MB: confirm via AskUserQuestion (avoid surprise)
- `--monitor-paths` FAIL på load-bearing path: surface med fix-recommendation

## Hop-in support

YES — designed för periodic operator-run + automation via cron-like trigger.

## Integration

**Reads:**
- `~/.lintel/audit/usage-*.jsonl` (Cohort 2 1.1 output)
- `~/.lintel/state/` (snapshot dir)
- `~/.lintel/draft/` (clean targets)
- `skills/cycle/SKILL.md` mode_envelopes
- Load-bearing path manifest (configurable)

**Writes:**
- `~/.lintel/archive/old-state-*.tar.gz` (compaction outputs)
- `~/.lintel/audit/maintenance-runs.jsonl` (audit-trail)
- stdout (report)

**Consumed by:**
- Operator (manual periodic runs)
- Future: scheduled-task wrapper for weekly auto-run

## Anti-patterns

- **Aggressive force-compact mid-engagement** — keep recent state för 30 days minimum. Operators behöver resume-from-context som inte är just-shipped.
- **Path-monitoring without write-safety** — denna skill READS paths. Modifications via separate ops.
- **Token-simulation utan usage-log data** — surface "estimated from defaults only — limited accuracy" warning.

## Failure recovery

- Compaction targets locked (open files): skip + log
- Path monitoring permission-deny: warn + continue (partial coverage)
- Token simulation: heuristic fallback om no usage-log data, flag i report

## Recommended next steps

- Post-monitor-paths FAIL: address each fail individually (most likely missing config or stale path)
- Post-rust-report: review rust candidates, archive what genuinely cold
- Post-force-compact: run `/li:doctor --quick` verify no inadvertent state loss
