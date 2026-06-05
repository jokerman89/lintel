---
name: maintenance
layer: foundation
description: On-demand maintenance — force-compact + static-path monitoring + token-cost simulation. Operator-request 5.3. Builds on usage-log (1.1) as its data source.
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

Operator-request 5.3 (post Cohort 2 dependency 1.1 usage-log landed): an on-demand maintenance system with 3 modes:

1. **`--force-compact`** — clear excess context beyond what's already compacted. The operator allows heavy contexting for heavy tasks, then reclaims on demand.

2. **`--monitor-paths`** — watch canonical paths for drift/missing. Would have caught 0.4 (tasks/personas+memory missing per LAYERS.md). Static-path verification.

3. **`--simulate-tokens <workflow>`** — "what would `/li:cycle --mode customer-engagement` cost?" Depends on 1.1 (usage-log) for real numbers; otherwise heuristics.

Closes operator-request 5.3 + integrates with L-002 (grep-first-pattern adapted for paths).

## When to use

- "My Lintel feels sluggish" → `/li:maintenance --force-compact`
- "Is everything in place?" → `/li:maintenance --monitor-paths`
- "What would X cost?" → `/li:maintenance --simulate-tokens customer-engagement`
- "What's rusting?" → `/li:maintenance --rust-report` (skills with <2 invocations past 30 days, via usage-log)

## When NOT to use

- Mid-task work (this pauses for diagnostics)
- Single-file check — `/li:doctor --quick` is faster
- Pre-implementation cost estimate — `/li:cycle --dry-run` has inline cost

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

Static-path manifest (loaded from config or hard-coded):

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
- Check writeable (if relevant)
- Check non-empty (if expected)
- Check no-drift (deprecated paths should be empty)

Surface the diff vs expected state. PASS / WARN / FAIL per path.

### `--simulate-tokens <workflow>`

Read mode-presets from `skills/cycle/SKILL.md` mode_envelopes:

```yaml
hotfix:           ~5k tokens
customer-engagement: ~40-80k tokens
internal-tool:    ~25-50k tokens
demo-prep:        ~15-25k tokens
research-dive:    ~10-20k tokens
```

Cross-reference with usage-log (post-1.1 land):
- Read `~/.lintel/audit/usage-*.jsonl` past 30 days
- Filter by skill-list for the chosen workflow
- Compute median + p95 tokens-est
- Surface: "Estimated: median <X>k tokens (p95: <Y>k) based on N prior invocations"

If no usage-log data: fall back to mode-envelope hard-coded estimates.

### `--rust-report`

Read usage-log past 30 days:
- For each skill in `skills/`, count invocations
- Flag skills with < 2 invocations as rust candidates
- Group by category: never-invoked / rare / cold / active
- Surface a table for operator review

Pairs naturally with `/li:catalog --trends` (Cohort 2 1.6 output).

## Voice tier behavior

`voice: internal`. An operator-internal maintenance pass.

## Status protocol

- **DONE** — maintenance pass complete for the selected mode
- **DONE_WITH_CONCERNS** — pass complete with warnings (e.g., deprecated paths still present)
- **BLOCKED** — `~/.lintel/` permissions deny read/write
- **NEEDS_CONTEXT** — `--simulate-tokens` without a workflow arg

## Pause-points

- `--force-compact` would reclaim > 500MB: confirm via AskUserQuestion (avoid surprise)
- `--monitor-paths` FAIL on a load-bearing path: surface with a fix recommendation

## Hop-in support

YES — designed for periodic operator runs + automation via a cron-like trigger.

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

- **Aggressive force-compact mid-engagement** — keep recent state for 30 days minimum. Operators need to resume from context that isn't just-shipped.
- **Path-monitoring without write-safety** — this skill READS paths. Modifications go through separate ops.
- **Token-simulation without usage-log data** — surface an "estimated from defaults only — limited accuracy" warning.

## Failure recovery

- Compaction targets locked (open files): skip + log
- Path monitoring permission-deny: warn + continue (partial coverage)
- Token simulation: heuristic fallback if no usage-log data, flag it in the report

## Recommended next steps

- Post-monitor-paths FAIL: address each fail individually (most likely missing config or a stale path)
- Post-rust-report: review rust candidates, archive what is genuinely cold
- Post-force-compact: run `/li:doctor --quick` to verify no inadvertent state loss
