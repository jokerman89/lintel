---
name: jstack-clean
description: Manual self-maintenance trigger. Suggests /context-save + restart when session feels heavy.
color: yellow
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code]
---

# /clean

Manual companion to the Layer 4 context-bloat watchers. Operator runs this when a session feels heavy (or when a watcher fired and you want to act). Outputs a short readout + offers the cleanup path: `/context-save` → restart fresh session → `/context-restore`.

**JStack does NOT make Claude's context infinite. This skill surfaces the cleanup ritual.**

## When to use

- A watcher hook fired and surfaced "consider /clean"
- You FEEL the session got heavy — output quality dropped, you're repeating context, tool-call rate accelerated, agent forgets earlier decisions
- Before stepping away for >2 hours (so resume is clean)
- After a long multi-skill chain (office-hours → plan-eng-review → implementation) where the chain itself ate context

## When NOT to use

- Pure short Q&A — nothing to clean
- Mid-tool-call sequences — let the current sequence finish first
- Before a `/release-ev2` — let ship complete, THEN clean

## Inputs

- **No required arguments.** Skill computes:
  - Estimated token count (best-effort — count tool-result sizes + recent turn lengths)
  - Tool-call count for this session
  - Skills invoked this session
  - Whether a checkpoint exists for current slug + branch (and how recent)

## Workflow

1. **Compute session weight signals:**
   - Approximate token count (`conversation length` from harness if available, else operator-estimated)
   - Tool-call count
   - Skills invoked count
   - Time elapsed since session start
2. **Read recent checkpoint:**
   - `ls -t ~/.gstack/projects/<slug>/checkpoints/<branch>-*.md | head -1`
   - If exists: timestamp, age in minutes
3. **Read watcher thresholds** from `~/.jstack/config.yaml`:
   - `watchers.token_watcher.warn_threshold` (default 50000)
   - `watchers.toolcall_watcher.warn_threshold` (default 80)
4. **Decision tree:**
   - If session is BELOW both thresholds: report green status, no action needed.
   - If session is ABOVE warn threshold(s): recommend `/context-save` + restart.
   - If checkpoint is RECENT (<5 min): suggest using that one — `/context-restore` after restart.
5. **Print readout + offer next step.**

## Report format

**Green (no action needed):**
```
Session health: ✓ within thresholds
  Estimated tokens: ~24,000 (warn at 50,000)
  Tool calls: 42 (warn at 80)
  Skills invoked: office-hours, plan-eng-review
  Time elapsed: 1h 47m
  Latest checkpoint: 2h ago (~/.gstack/projects/jstack/checkpoints/main-20260527-...)

No cleanup needed yet. Run /clean again if session grows heavier.
```

**Yellow (over warn, not escalation):**
```
Session health: ⚠ over warn threshold
  Estimated tokens: ~62,000 (warn at 50,000 — exceeded)
  Tool calls: 73 (warn at 80 — close)
  Skills invoked: office-hours, plan-eng-review, plan-eng-review, /clean
  Time elapsed: 3h 12m
  Latest checkpoint: 45m ago

Recommended:
  1. /context-save phase-2-batch-1 (write a checkpoint)
  2. Close this session
  3. Open fresh Claude session, run /context-restore

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

- **No `~/.jstack/config.yaml` exists:** use defaults (50k/80k tokens, 80/130 tool calls).
- **No checkpoint history:** skip the "latest checkpoint" line.
- **Operator overrides default thresholds:** read them from config and apply.
- **Token count unavailable:** skip token line, only report tool-call count + qualitative signal ("you've invoked 5 skills, session feels heavy").

## Honest framing

JStack can't compact your conversation. Only Claude can. This skill:

- Surfaces the right thresholds
- Suggests the right ritual (`/context-save` + restart + `/context-restore`)
- Doesn't perform any auto-action — operator owns the call

That's the design per office-hours D5 (hybrid soft-warning + manual /clean) and reframed per eng-review A5 (watchers, not "self-maintenance").

## Compliance integration

None directly. /clean reads + reports; doesn't touch code or external systems.

## Failure modes

- **Token count estimation off:** report it's an estimate, not authoritative.
- **`~/.gstack/projects/<slug>/checkpoints/` doesn't exist:** treat as no-checkpoint-history.
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
- Layer 4 `jstack-token-watcher` + `jstack-toolcall-watcher` hooks — fire warnings that lead operator here
- `~/.jstack/config.yaml` — threshold overrides
