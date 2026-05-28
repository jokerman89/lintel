---
name: jstack-context-warmup
layer: foundation
description: Explicit preload of high-leverage context per declared warmup pattern.
color: blue
tools: Read, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
---

# /context-warmup

Executes warmup tasks declared in current phase's `warmup_tasks` array. Charges against phase budget; surfaces cost estimates per task before execution.

Use when you want explicit control over preload — vs the auto-warmup that happens on phase entry if `warmup_enabled: true` in config.

## When to use

- Auto-warmup is OFF (config) and operator wants explicit preload
- Re-preload after `--compress` removed warmup context
- Mid-phase add of additional warmup task
- Debugging warmup behavior (verbose output)

## When NOT to use

- Auto-warmup ran cleanly at phase entry — re-running burns budget
- No active phase has warmup_tasks declared — nothing to preload

## Inputs

- `--task <text>` — execute a specific warmup task (declared OR ad-hoc)
- `--all` — execute all pending warmup tasks for current phase
- `--estimate-only` — show cost estimate without executing
- `--verbose` — step-by-step execution log

## Workflow

1. Read current phase from context-state.json
2. Read warmup_tasks declared in originating skill's frontmatter
3. Filter to pending (not in `warmup_tasks_completed`)
4. For each pending task:
   - Estimate token cost (heuristic: file size for read tasks, ~500 tokens per summary)
   - Surface estimate to operator
   - If `--estimate-only`: stop here
   - Otherwise: execute task (read files, run analysis, etc.)
   - Charge actual cost against phase budget
   - Mark task complete
5. Report.

## Report format

```
Context warmup — phase: preload

Pending warmup tasks (2):
  1. "read all engagement docs from current branch"     [est. 45k tokens]
  2. "summarize prior sessions for this customer"        [est. 25k tokens]

Total estimate: 70,000 tokens
Phase budget: 200,000 — remaining 200,000
Operator: continue? (auto-yes if warmup_enabled: true)

[Execution]
Task 1: reading docs/engagement/*.md... 14 files, 42k tokens consumed
Task 2: reading ~/.jstack/projects/.../checkpoints/*.md... 3 sessions, 23k tokens
✓ Warmup complete. Phase spent: 65k / 200k.
```

## Compliance integration

- Layer 2 customer-data scan on every file loaded via warmup. BLOCK on hit.
- Audit log entry per task: `~/.jstack/audit/context-warmup.jsonl`
- Files matching frozen-zone patterns are loaded but flagged for read-only treatment downstream

## Voice tier note

`voice: internal`.

## Failure modes

- **Warmup task spec ambiguous** (e.g. "read engagement docs" with no path) — ask operator for clarification before estimating
- **Estimated cost would exceed remaining phase budget** — STOP. Surface options: skip task, extend budget, cancel phase
- **File read fails** (permission, missing, locked) — log error, continue with remaining warmup tasks, mark this task failed
- **Customer-data pattern in loaded file** — BLOCK (Layer 2 always-on)

## Examples

**Standard auto-warmup execution:**
```
> /context-warmup --all
[2 tasks executed, 65k tokens consumed]
```

**Just estimate:**
```
> /context-warmup --all --estimate-only
[Shows cost without executing]
```

**Ad-hoc warmup:**
```
> /context-warmup --task "load engagement risk register"
[Asks for specifics, estimates, executes]
```

## See also

- `CONTEXT-ENGINE.md` — warmup-task pattern semantics
- `/context-budget` — view + modify current phase
- `/perf-mode` — perf-mode activation
- ContextBudgetAdvisor agent — suggests warmup patterns
