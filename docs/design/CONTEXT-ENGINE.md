# Lintel Context Engine (1M Budget Engine)

Context as a **budgeted resource**, not as "what fits before compaction." Outcome-based — spend tokens where outcome density is high, save where it doesn't.

v2.0 ships engine as **declarative + soft-enforcement only** (per P1 fix T1 from eng-review). Hard enforcement (block on budget exceeded) deferred to v2.0.5 patch after usage data confirms warnings get acted on.

---

## Why this engine exists

**The problem in v1:** Long sessions hit the context wall. The operator either waits for auto-compaction (which loses structure) or runs `/context-save` and restarts (which loses momentum). Neither serves "tuffa faser" — multi-week customer-engagement work that genuinely needs 800k+ tokens of loaded context.

**The v2 approach:** Phase declarations + budget tracking + warmup patterns + outcome scoring. The operator declares phases ("preload all engagement docs", "build the demo", "voice-check the deliverable") and the engine tracks budget consumption per phase. The operator gets visibility + tools, not magic.

**What it explicitly does NOT do:** auto-compact mid-session. Claude can't compact. Pretending it can produces silent failure. The engine surfaces the state honestly; the operator decides what to drop, summarize, or checkpoint.

---

## Phase declaration grammar

Skills + multi-step orchestrators declare context budget per phase in frontmatter:

```yaml
---
name: li-engagement-deepdive
context_phases:
  - phase: preload
    budget: 200000              # tokens
    warmup_tasks:
      - "read all engagement docs from current branch"
      - "summarize prior sessions for this customer"
    decay_on_exit: prompt-operator
  - phase: build
    budget: 500000
    reserve_for_eval: 100000    # tokens reserved for downstream eval phase
    decay_on_exit: aggressive    # auto-drop most of build context on phase end
  - phase: voice_check
    budget: 150000
    reserve_for_corpus_calibration: 50000
    decay_on_exit: conservative  # keep voice-check artifacts in context
---
```

### Required fields per phase

- `phase` (string) — phase name. Operator-readable.
- `budget` (number) — token budget for this phase. SUM of all phases ≤ `max_budget` from config.

### Optional fields per phase

- `warmup_tasks` (array of strings) — explicit preload tasks. Charged against this phase's budget. Emitted as system messages at phase entry.
- `reserve_for_<sub>` (number) — reserved tokens NOT spent in this phase but available for downstream phases. Engine tracks across phase transitions.
- `decay_on_exit` (string) — `prompt-operator | aggressive | conservative | retain-all`. Default: `prompt-operator`.

---

## Budget tracker semantics

The tracker maintains state in `~/.lintel/sessions/$SESSION_ID/context-state.json`:

```json
{
  "session_id": "47821-1716926400",
  "current_phase": "build",
  "phase_history": [
    {"phase": "preload", "budget": 200000, "spent": 187000, "outcome": "engagement docs loaded, 12 summaries generated"}
  ],
  "current_phase_state": {
    "phase": "build",
    "budget": 500000,
    "spent_so_far": 312000,
    "remaining": 188000,
    "watcher_warned_at_80pct": false,
    "watcher_warned_at_100pct": false
  },
  "reservations": {
    "voice_check.reserve_for_corpus_calibration": 50000
  },
  "warmup_tasks_completed": ["read all engagement docs from current branch"],
  "warmup_tasks_pending": ["summarize prior sessions for this customer"]
}
```

State updated on every tool call (tracked via Claude Code's token-usage telemetry where available; estimated via conversation length heuristic otherwise).

---

## Watchers (soft enforcement, v2.0)

At **80%** of phase budget consumed:

> ⚠ Context budget watcher: phase `build` at 80% (400k of 500k). Consider:
>   - `/context-budget --checkpoint` — save phase state, start next phase
>   - `/context-budget --compress` — collapse low-value context (operator confirms)
>   - Continue at your own risk; will warn again at 100%

At **100%** of phase budget consumed:

> ⚠⚠ Context budget watcher: phase `build` exhausted (500k of 500k spent).
>   Recommend:
>   1. `/context-save` + fresh session, OR
>   2. `/context-budget --next-phase` to transition + decay, OR
>   3. `/context-budget --override +N` to extend phase budget (logged)

**No hard block in v2.0.** Operator decides. Audit log records every watcher fire + operator decision. v2.0.5 patch may add hard block on second 100%-warning if data shows operators ignore the first.

---

## Warmup task pattern

Heavy phases EXPLICITLY preload context with high-leverage material at start. The engine charges this against phase budget; it's a deliberate investment, not waste.

Example warmup execution (Phase: preload, budget 200k):

```
[Engine] Entering phase: preload (budget 200000)
[Engine] Warmup task 1: "read all engagement docs from current branch"
[Engine]   Estimated cost: 45000 tokens
[Engine]   Proceed? (auto-yes if warmup_enabled: true in config)
[Engine]   ✓ Loaded 14 docs, 42k tokens consumed
[Engine] Warmup task 2: "summarize prior sessions for this customer"
[Engine]   Estimated cost: 25000 tokens
[Engine]   ✓ Loaded 3 prior sessions, 23k tokens consumed
[Engine] Warmup complete. Phase budget: 65k spent / 200k allocated.
```

If warmup cost would exceed phase budget: STOP at the warmup task that would cross, surface to operator: "warmup task N would exceed budget by X tokens — skip, extend budget, or cancel phase?"

---

## Decay policies (phase transition)

When a phase ends, the engine offers structured cleanup based on `decay_on_exit`:

### `prompt-operator` (default)

Engine surfaces:
> Phase `build` ending. 312k tokens consumed.
> Options for context decay:
>   (1) Keep all — next phase starts with full build-phase context loaded
>   (2) Summarize then drop — engine writes 1-2 paragraph summary, drops raw
>   (3) Drop verbatim — next phase starts fresh from preload-summary + reservations
> Recommended: (2) — preserves outcome without bloat.

Operator picks. Audit log records.

### `aggressive`

Auto-drops phase context on exit. Keeps only:
- Phase-summary auto-generated by engine (target: 5000 tokens or 10% of phase spent, whichever lower)
- Reservations for downstream phases

Suitable for phases that produce a discrete artifact (a built doc, a passing test, a completed migration).

### `conservative`

Retains most phase context on exit. Useful when downstream phases need the build state.

### `retain-all`

No decay. Phase context flows into next phase unchanged. Useful for tightly-coupled phase sequences (review → critique → revise where the diff context must be preserved across).

---

## Error semantics (P1 fix T10 from eng-review)

| Error | Engine behavior |
|-------|----------------|
| Phase transition error (invalid phase name, etc.) | Log + continue current phase. Don't crash session. |
| Budget exceeded mid-phase | Warn + offer compress/checkpoint/override. No silent compaction. |
| Operator cancels phase | Checkpoint current phase state to `~/.lintel/sessions/$SESSION_ID/checkpoint-<phase>.md`. Resumable. |
| Engine config read error | Fall back to safe defaults (`default_budget: 200000`, no warmup) + warn. |
| Warmup task fails | Mark task as failed in state, continue with remaining warmup. Phase budget not refunded. |
| Override request beyond `max_budget` ceiling | Refuse + surface ceiling. Operator can edit config to raise ceiling permanently. |
| Reservation overflow (sum of reservations > total remaining) | Engine refuses to enter the over-reserving phase. Operator adjusts. |

---

## Outcome scoring (P2 fix T11 from eng-review)

Each phase logs (in audit) tokens spent + outcome shipped:

```jsonl
{"phase":"preload","ts":"...","spent":187000,"outcome":"engagement docs loaded","outcome_density_estimate":"high"}
{"phase":"build","ts":"...","spent":312000,"outcome":"3 deliverables drafted","outcome_density_estimate":"medium"}
{"phase":"voice_check","ts":"...","spent":98000,"outcome":"all 3 deliverables PASS at ≥85","outcome_density_estimate":"high"}
```

`outcome_density_estimate` is operator-supplied OR engine-heuristic:
- **high** — concrete artifact produced (file written, decision made)
- **medium** — useful intermediate state (analysis, exploration)
- **low** — exploratory / dead-end (operator can mark when phase didn't pan out)

Periodic `/perfbench --context` report shows token-spend per outcome category. Operator sees where 1M perf-mode actually pays off.

---

## Cost tracking (P2 fix T11)

Monthly summary log at `~/.lintel/audit/context-cost-monthly.jsonl`:

```jsonl
{"month":"2026-05","perf_mode_sessions":7,"total_tokens":4200000,"estimated_cost_usd":63.0,"avg_outcome_density":"medium"}
```

Token cost estimated using Anthropic prompt-cache pricing (input $3/M, output $15/M for Sonnet; adjust per model). Operator sees rolling 30-day estimate.

---

## Config (`~/.lintel/config.yaml`)

```yaml
context:
  enabled: true                      # opt-in; off = use claude-code default no engine
  default_budget: 200000             # safe default for unmarked phases
  max_budget: 1000000                # 1M ceiling for perf-mode sessions
  perf_mode_budget: 800000           # /perf-mode default
  decay_policy_default: prompt-operator
  warmup_enabled: true
  outcome_logging: true
  cost_tracking: true
watchers:
  budget_soft_pct: 80
  budget_hard_pct: 100
  warning_cooldown_calls: 5          # don't re-warn for N tool calls after last warn
```

Operator tunes per project + per session via `/context-budget --config`.

---

## New skills introduced by this phase

| Skill | Purpose |
|-------|---------|
| `/context-budget` | View + modify current phase budget, declare new phase, checkpoint |
| `/context-warmup` | Explicit preload of high-leverage context per declared warmup pattern |
| `/perf-mode` | Activate 1M context-budget mode for the current session |
| `/context-budgetwatch` (renamed from `/context-tokenwatch`; consolidated into `/context-budget --watch` 2026-06-10) | Passive monitoring with budget-aware thresholds |

Plus agent: `ContextBudgetAdvisor` (Layer 4) — suggests phase declarations for unstructured tasks.

---

## Integration with other skills

- `/perf-mode` SETS context to perf-mode budget for session; other skills' `context_phases` declarations apply unchanged
- `/release-ev2` reads `outcome_density_estimate` audit to surface "low outcome density sessions" as advisory before ship
- `/onecs-check` is unaffected — compliance is orthogonal to context budgeting
- `/onebranch-validate` cross-CLI matrix runs do NOT use perf-mode (tests need predictable budget)

---

## See also

- `/context-budget` skill — view/modify mechanism
- `/context-warmup` skill — explicit preload
- `/perf-mode` skill — perf-mode activation
- `ContextBudgetAdvisor` agent — Layer 4 advice generator
- `verify.sh --context-engine` — schema + state validation
- Phase G — engine becomes part of v2.0.0 ship gate
