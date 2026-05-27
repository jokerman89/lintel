---
name: jstack-context-budget
description: View/modify current phase context budget, declare new phase, checkpoint.
color: blue
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
  - cli: copilot-cli
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: sequential-prompt
---

# /context-budget

Operator-facing interface for the 1M Context Budget Engine. View current phase state, modify budget, declare next phase, checkpoint, or override.

## When to use

- Watcher fired at 80%/100% — operator wants to see state + decide
- Pre-heavy-task — operator wants to set explicit phase budget before starting
- Mid-session re-planning — adjust budget after scope change
- Post-session retro — review where tokens went

## When NOT to use

- Light-touch session — engine defaults are fine
- No phase declarations exist — declare phases first via `/perf-mode` or skill that uses context_phases frontmatter

## Inputs

- `--view` — show current state + recent phase history (default)
- `--checkpoint` — save current phase state, ready to transition
- `--next-phase <name>` — explicit phase transition with decay
- `--override +N` — extend current phase budget by N tokens (logged)
- `--compress` — surface compress-options for current context (operator confirms)
- `--config` — open `~/.jstack/config.yaml` context section for editing

## Workflow (default --view)

1. Read `~/.jstack/sessions/$SESSION_ID/context-state.json`
2. Display current phase + spent + remaining + watcher state
3. List warmup tasks completed/pending
4. Show reservations
5. Show recent phase history (last 5)

## Report format

```
Context Budget — session 47821-1716926400

Current phase: build
  Budget:      500,000 tokens
  Spent:       312,000 (62%)
  Remaining:   188,000
  Watchers:    80% — not fired yet | 100% — not fired

Reservations:
  voice_check.reserve_for_corpus_calibration: 50,000

Warmup tasks:
  ✓ "read all engagement docs from current branch" (45k tokens)
  ✓ "summarize prior sessions for this customer" (23k tokens)

Phase history:
  preload: 187k / 200k (94%) — engagement docs loaded ✓
  build:   in progress
  voice_check: pending

Actions:
  /context-budget --checkpoint    save state, prepare transition
  /context-budget --next-phase    transition to voice_check
  /context-budget --override +N   extend build budget (logged)
  /context-budget --compress      collapse low-value context
```

## Compliance integration

- Audit log entry per state change: `~/.jstack/audit/context-budget.jsonl`
- Override events logged with operator-provided reason (prompted)
- Read-only `--view` mode not audit-logged (high frequency, low value)

## Voice tier note

`voice: internal`. Engine plumbing.

## Failure modes

- **State file missing or corrupt** — engine surfaces "no active phase declared". Suggests `/perf-mode` or skill with `context_phases` frontmatter.
- **`--override` would exceed `max_budget`** — refuse. Operator must edit config ceiling.
- **`--next-phase` to undefined phase name** — list available phase names from current declaration.
- **Compress without operator confirmation** — refuse. Compression is irreversible; always confirm.

## Examples

**View state:**
```
> /context-budget
[Current phase: build, 62% spent, no watchers fired yet]
```

**Override:**
```
> /context-budget --override +100000
[Prompts: reason for override?]
Operator: "scope expanded mid-build to include additional fixture set"
✓ Budget extended: 500k → 600k. Logged.
```

**Phase transition:**
```
> /context-budget --next-phase voice_check
[Engine: phase `build` ending at 312k spent, decay_on_exit: aggressive]
[Engine: keeping summary + reservation; dropping verbatim build context]
✓ Phase voice_check active. Budget: 150k.
```

## See also

- `CONTEXT-ENGINE.md` — full engine semantics
- `/context-warmup` — explicit preload pattern
- `/perf-mode` — activate 1M perf-mode for session
- `/context-budgetwatch` — passive monitoring
- `ContextBudgetAdvisor` agent — suggests phase declarations
