---
name: jstack-perf-mode
description: Activate 1M context-budget mode for the session — "tuffa faser" preset.
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
---

# /perf-mode

Activates Performance Mode for the current session. Raises context budget ceiling from default (200k) to perf-mode level (800k default; configurable to 1M ceiling). Use for hard CAIP-SE phases that genuinely need 800k+ tokens of loaded context.

Outcome-based, not token-saving. Spend tokens where outcome density justifies it.

## When to use

- Multi-week customer engagement consolidation — load all prior session checkpoints + design docs + brand
- Parallel decomposed task — multiple sub-tasks need shared deep context
- Warmup-heavy integration moment — preload entire engagement state before authoring
- Critical demo prep — context window must hold script + handout + follow-up + brand assets

## When NOT to use

- Routine work — default 200k is more than enough
- Cost-sensitive sessions — perf-mode token spend is ~5x default ($15-30/session)
- Light edits, single-file changes — perf-mode is overkill
- Tests + CI runs — predictable budget needed

## Inputs

- `--budget <N>` — explicit budget override (default: from config `perf_mode_budget`)
- `--ceiling <N>` — raise/lower the max ceiling for this session (default: from `max_budget`)
- `--decay-policy <prompt-operator|aggressive|conservative|retain-all>` — set default decay for this session
- `--cost-estimate` — show projected token spend + USD estimate without activating
- `--off` — deactivate perf-mode, return to default budget

## Workflow

1. **Preflight check.** Verify context engine is enabled (`context.enabled: true` in config). If not: warn + offer to enable.
2. **Cost estimate (if `--cost-estimate`).** Compute projected spend based on budget + average session token-velocity history. Show estimate + skip activation.
3. **Activate.** Write to `~/.jstack/sessions/$SESSION_ID/perf-mode-active`:
   ```yaml
   active: true
   activated_at: 2026-05-27T21:30:00Z
   budget: 800000
   ceiling: 1000000
   decay_policy: prompt-operator
   activated_by: operator-explicit
   ```
4. **Surface to operator.** Print activation banner. Subsequent watcher warnings use perf-mode thresholds.
5. **Subsequent skill invocations** check perf-mode-active file and apply perf-mode budget if no explicit `context_phases` declared.
6. **Cost tracking.** Audit log entry recording activation. Monthly cost summary report picks this up.

## Report format

```
⚡ Perf-mode ACTIVE for session 47821-1716926400

Budget:        800,000 tokens (vs default 200,000)
Ceiling:       1,000,000 tokens (max)
Decay policy:  prompt-operator
Estimated spend:
  At average velocity (50k tokens/hour): ~16 hours runway
  USD estimate (Claude Sonnet pricing):  ~$24-48 for full perf-mode session

Active phases will use perf-mode budget unless explicitly declared otherwise.

Deactivate: /perf-mode --off
View state: /context-budget
Monitor:    /context-budgetwatch
```

## Compliance integration

- Activation logged: `~/.jstack/audit/perf-mode-activations.jsonl`
- Cost tracking aggregates perf-mode sessions to monthly summary
- No production-mutation gate — perf-mode is local resource allocation

## Voice tier note

`voice: internal`.

## Failure modes

- **Context engine disabled in config** — warn + offer to enable, then retry
- **Already active in this session** — show current state, no-op
- **Budget request exceeds max_budget ceiling** — refuse + show ceiling. Operator edits config to permanently raise ceiling.
- **`--off` when not active** — no-op + confirmation

## Examples

**Standard activation:**
```
> /perf-mode
⚡ Perf-mode active. 800k budget, ~16 hour runway.
```

**Cost estimate before committing:**
```
> /perf-mode --cost-estimate
At average velocity: 16 hours runway. Estimated $24-48 cost.
[Skill exits without activating]
```

**Custom budget:**
```
> /perf-mode --budget 600000 --decay-policy aggressive
⚡ Perf-mode active. 600k budget, aggressive decay default.
```

**Deactivate:**
```
> /perf-mode --off
✓ Perf-mode deactivated. Returning to default 200k budget for remaining session.
```

## See also

- `CONTEXT-ENGINE.md` — engine semantics
- `/context-budget` — view + modify state
- `/context-warmup` — explicit preload
- `/context-budgetwatch` — passive monitoring
- `ContextBudgetAdvisor` — Layer 4 agent suggests perf-mode for unstructured tasks
