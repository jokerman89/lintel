---
name: maintenance
layer: foundation
description: Use for on-demand storage/context guidance, scoped path diagnostics and labeled usage estimates without treating partial logs as health or claiming model compaction.
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

1. **`--force-compact`** — retained compatibility name for context/storage advice.
   It does not clear active context or invoke an unavailable host operation.

2. **`--monitor-paths`** — watch canonical paths for drift/missing. Would have caught 0.4 (tasks/personas+memory missing per docs/architecture.md). Static-path verification.

3. **`--simulate-tokens <workflow>`** — a labeled planning estimate from real,
   compatible observations when available, otherwise an uncalibrated prior.
   Optional manual usage-log entries are not a full invocation/billing census.

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

Use P03 `/li:context-budget` for observed/estimated/unknown headroom, and
`/li:context-save` -> restart -> `/li:context-restore` for owned checkpoint continuity.
Retain the same [work map](../spec-kit/references/work-map.md) and actual verified
profile reference/required policy. Context state is not selected by a newer basename.

Storage inspection can identify old checkpoints, manual usage logs, draft directories
and provenance archives as candidates. Age alone does not make them safe to remove.
Before an authorized archive/recovery operation, name exact owned paths and destination,
preserve unrelated files, and use P03's owned snapshot/recovery workflow; do not copy
whole trees, delete by wildcard or send data to an implicit global/private sink.

Report disk bytes only after actual verification, separately from model context:
"Storage archived: <observed bytes or not performed>; active context reclaimed: not
established." No force-compaction control, watcher or cleanup daemon is enabled.

### `--monitor-paths`

Static-path manifest (loaded from config or hard-coded):

```yaml
load-bearing_paths:
  - .claude/memory/lessons.md          # required per docs/architecture.md
  - .claude/memory/personas.md          # required per docs/architecture.md (Cohort 1 0.4)
  - .claude/memory/working-state.md            # required per docs/architecture.md (Cohort 1 0.4)
  - <explicit configured profile context>  # P07 verification, not file-presence clearance
  - .claude/runtime/audit/     # observation spine writes here (usage-* stays in ~/.lintel/audit/)
  - <trusted source>/skills/   # source, not an arbitrary inspected target
  - <trusted source>/agents/

deprecated_paths_check:
  - <explicitly selected legacy paths>  # no automatic personal-directory inspection

required_files_in_paths:
  - skills/CATALOG.md          # auto-generated, should exist post-Cohort-2 merge
  - .claude/memory/lessons.md           # canonical lessons
```

For each path:
- Check existence
- Check writeable (if relevant)
- Check non-empty (if expected)
- Check no-drift (deprecated paths should be empty)

Surface the diff vs expected state. PASS / WARN / FAIL per path.

### `--simulate-tokens <workflow>`

Use `lib/scale-estimator.sh::scale_token_estimate <size>` for a whole-cycle prior
and its actual sample count/basis. Do not multiply it by task count or confuse it
with current context usage. Historic mode examples remain illustrative estimates:

```yaml
hotfix:           ~5k tokens
customer-engagement: ~40-80k tokens
internal-tool:    ~25-50k tokens
demo-prep:        ~15-25k tokens
research-dive:    ~10-20k tokens
```

Cross-reference with usage records, if any exist (the usage-log writer is manual, operator-invoked):
- Read `~/.lintel/audit/usage-*.jsonl` past 30 days
- Filter by skill-list for the chosen workflow
- Compute median + p95 tokens-est
- Surface the source, sample count, missing/estimated fields and selection bias.
  Do not manufacture p95 precision from a few optional records.

If no compatible measured data exists: report an uncalibrated prior or unknown.
For the actual handoff, `bin/li-work-artifacts.py --view budget` measures the
selected original map artifacts and explicit P03 warming inputs. There is no cost
estimate without actual provider/billing inputs.

### `--rust-report`

Read usage records past 30 days, if any exist (writer is manual — without records, report "no usage data" instead of a rust table):
- Count only **recorded** invocations in the selected source/log scope
- Low recorded activity may prompt a review, not deletion or a dead-skill verdict
- Group observed samples separately from **unobserved/coverage unknown**
- Surface a table for operator review

Pairs naturally with `/li:catalog --trends` (Cohort 2 1.6 output).

## Pause-points

- A requested disk mutation needs exact scoped authority regardless of byte count;
  use the actual host question channel only when that authority is missing
- `--monitor-paths` FAIL on a load-bearing path: surface with a fix recommendation

## Integration

**Reads:**
- `~/.lintel/audit/usage-*.jsonl` (Cohort 2 1.1 output)
- `.claude/runtime/state/` (snapshot dir)
- `~/.lintel/draft/` (clean targets)
- `skills/cycle/SKILL.md` mode_envelopes
- Load-bearing path manifest (configurable)

**Writes:**
- Explicitly authorized owned storage artifacts only; no default global archive
- `.claude/runtime/audit/maintenance-runs.jsonl` (audit-trail)
- stdout (report)

**Consumed by:**
- Operator (manual periodic runs)
- Future: scheduled-task wrapper for weekly auto-run

## Anti-patterns

- **Aggressive force-compact mid-engagement** — keep recent state for 30 days minimum. Operators need to resume from context that isn't just-shipped.
- **Path-monitoring without write-safety** — this skill READS paths. Modifications go through separate ops.
- **Token-simulation without compatible measured data** — label uncalibrated/unknown.
- **Calling absent partial telemetry healthy, dead or complete** — preserve the gap.

## Failure recovery

- Compaction targets locked (open files): skip + log
- Path monitoring permission-deny: warn + continue (partial coverage)
- Token simulation: heuristic fallback if no usage-log data, flag it in the report

## Recommended next steps

- Post-monitor-paths FAIL: address each fail individually (most likely missing config or a stale path)
- Post-rust-report: review low-observation candidates; absence is not disuse evidence
- Post-force-compact: run `/li:doctor --quick` to verify no inadvertent state loss
