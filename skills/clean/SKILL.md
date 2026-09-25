---
name: clean
layer: foundation
description: Manual self-maintenance trigger. Suggests /context-save + restart when session feels heavy.
color: yellow
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code]
---

# /clean

Manual companion to the Layer 4 context-bloat watchers. Operator runs this when a session feels heavy (or when a watcher fired and you want to act). Outputs a short readout + offers the cleanup path: `/context-save` → restart fresh session → `/context-restore`.

**Lintel cannot expand or erase a host's active model context.** This is a
compatibility entry into P03 context-budget/save/restore guidance, not a second
context policy or compaction engine.

## When to use

- A watcher hook fired and surfaced "consider /clean"
- You FEEL the session got heavy — output quality dropped, you're repeating context, tool-call rate accelerated, agent forgets earlier decisions
- Before stepping away for >2 hours (so resume is clean)
- After a long multi-skill chain (office-hours → plan-eng-review → implementation) where the chain itself ate context

## When NOT to use

- Pure short Q&A — nothing to clean
- Mid-tool-call sequences — let the current sequence finish first
- Before a `/ship` — let ship complete, THEN clean

## Inputs

- **No required arguments.** Skill computes:
  - Estimated token count (best-effort — count tool-result sizes + recent turn lengths)
  - Tool-call count for this session
  - Skills invoked this session
  - Whether a checkpoint exists for current slug + branch (and how recent)

## Workflow

1. **Read available session weight signals through `/li:context-budget`:**
   - P03 `context_budget` carries observed/estimated usage and its source, or unknown
   - Tool-call count
   - Skills invoked count
   - Time elapsed since session start
2. **Read recent checkpoint:**
   - `source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_context.sh"; context_latest` (checkpoints live at `.claude/runtime/sessions/<branch>/`)
   - If exists: timestamp, age in minutes
3. **Optional watcher advice:** inspect only explicitly configured and authorized
   thresholds. They are advisory warning points, not host capacity or proof that a
   watcher is installed/running. Do not create another threshold store here.
4. **Decision tree:**
   - If relevant signals are unknown, report unknown; absent telemetry is not green.
   - Supplied observations below configured advice thresholds do not certify session health.
   - If session is ABOVE warn threshold(s): recommend `/context-save` + restart.
   - Reuse a checkpoint only after verifying its selected work/profile and contents,
     not simply because it is younger than five minutes.
5. **Print readout + offer next step.**

## Report format

**Illustrative observed signals (not an actual run):**
```
Session observations: within configured advisory thresholds; host headroom still requires evidence
  Estimated tokens: ~24,000 (warn at 50,000)
  Tool calls: 42 (warn at 80)
  Skills invoked: office-hours, plan-eng-review
  Time elapsed: 1h 47m
  Latest checkpoint: 2h ago (.claude/runtime/sessions/main/20260527-...-context-save.md)

No cleanup needed yet. Run /clean again if session grows heavier.
```

**Illustrative warning:**
```
Session observations: over a configured advisory warning
  Estimated tokens: ~62,000 (warn at 50,000 — exceeded)
  Tool calls: 73 (warn at 80 — close)
  Skills invoked: office-hours, plan-eng-review, plan-eng-review, /clean
  Time elapsed: 3h 12m
  Latest checkpoint: 45m ago

Recommended:
  1. /context-save phase-2-batch-1 (write a checkpoint)
  2. Close this session
  3. Open a fresh session in the actual host, restore the owned checkpoint

This is a soft warning. You can keep going if you have <30 min of focused work left.
```

**Red (over escalation, or both watchers tripped):**
```
Session health: ✗ context bloat likely
  Estimated tokens: ~85,000 (escalation at 80,000 — exceeded)
  Tool calls: 142 (escalation at 130 — exceeded)
  Skills invoked: [list]
  Time elapsed: 5h 22m

STRONG recommendation:
  1. /context-save (now — before more work fights heavier context)
  2. Close session
  3. Fresh session → /context-restore

If you push past this, expect:
  - Slower tool calls
  - Forgotten decisions from earlier in the session
  - Repeated context summaries (wasted tokens)
```

## Edge cases

- **No configured watcher thresholds:** use shared context advice; do not invent
  a 1M window or a new default warning policy.
- **No checkpoint history:** skip the "latest checkpoint" line.
- **Operator overrides default thresholds:** read them from config and apply.
- **Token/tool counts unavailable:** explicitly report unknown, not zero or healthy.

## Honest framing

Only a real supported host operation can compact a conversation. This skill:

- Surfaces the right thresholds
- Suggests the right ritual (`/context-save` + restart + `/context-restore`)
- Doesn't perform any auto-action — operator owns the call
- Keeps selected-map/P07 references in the checkpoint through the shared lifecycle.
  Disk archiving and future read exclusions cannot reclaim already-sent context.

That's the design per office-hours D5 (hybrid soft-warning + manual /clean) and reframed per eng-review A5 (watchers, not "self-maintenance").

## Failure modes

- **Token count estimation off:** report it's an estimate, not authoritative.
- **`context_latest` returns nothing (no `.claude/runtime/sessions/<branch>/` checkpoints):** treat as no-checkpoint-history.
- **Operator runs /clean during a sub-skill chain:** report current state but warn that the chain hasn't completed yet — clean AFTER chain finishes.

## Examples

**Healthy session:**
```
> /clean
Session health: ✓ within thresholds
  ...
No cleanup needed yet.
```

**Bloated session:**
```
> /clean
Session health: ✗ context bloat likely
  ...
STRONG recommendation: /context-save then restart.
```

## See also

- `/context-save` — paired write step
- `/context-restore` — paired read step
- Optional watcher hooks — registration and observation must be separately verified
- `~/.lintel/config.yaml` — threshold overrides
