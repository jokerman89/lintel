# ADR-0023: turn-start continuity injection (UserPromptSubmit) — completing the trifecta

- **Status:** Accepted
- **Date:** 2026-06-17
- **Deciders:** operator
- **Extends:** ADR-0022 (self-healing harness continuity)
- **Supersedes:** —

## Context

ADR-0022 made cycle continuity self-healing at two points: a turn-**end** `Stop` hook
(`cycle-incomplete-warn`) that surfaces the footer so a turn never silently ends mid-cycle, and a
`SessionStart` digest that re-injects "Current cycle: phase X · next Y" on a fresh/resumed/compacted
session. Both fire at session/turn **edges**.

The operator reported — and this session reproduced — that after ~2–3 phases the model stops
rendering the footer, stops the structured per-phase report, and loses the phase. Diagnosis: nothing
re-asserts position at the **start of a turn within a live session**. The Stop hook fires *after* the
model already produced the footer-less turn; the digest fires once per session; the rest is SKILL.md
prose, which decays under momentum (L-016, L-018). The one Claude Code hook that can inject context
*before* the model generates — `UserPromptSubmit` — was **not registered at all** in `hooks.json`.
(ADR-0022 did not evaluate it; its "taxes every turn" note referred to the Stop hook. So this extends
0022, it does not reverse it.) A compounding cause: operators run stale installed plugins, so even the
0022 backstops don't fire — deployment is part of the fix.

## Decision

Add one `UserPromptSubmit` hook, `cycle-position-inject`, as the **turn-start** continuity surface,
completing the trifecta (turn-start drive + turn-end Stop backstop + SessionStart recovery):

1. **Inject-only, never block.** Always `exit 0`; never `exit 2` / `{"decision":"block"}` — on
   `UserPromptSubmit` that would drop the operator's prompt. Fully fail-open.
2. **Silent + near-zero cost outside a cycle.** A state-file + `phase: CYCLE` marker pre-check runs
   before any lib is sourced; the footer lib loads only when a cycle marker is present.
3. **Single source of truth.** When a cycle is active it injects the compact
   `render_cycle_footer --compact` position + "render the footer, give the per-phase report, advance
   when this phase is done." No second ledger parser (the cross-cycle footer bug came from two parsers).
4. **Gap-A nudge, same hook.** If the prompt invokes a cycle (`/li:cycle`, `/li:fix`, `/li:autoplan`,
   `/li:plan-and-build`) and no ledger marker exists, it nudges the model to write `CYCLE STARTING`
   first (the model owns the write — no auto-write, so cycle_id/mode/branch/commit stay correct).
5. **Pack-ready seam.** Built cycle-source-agnostic; a commented seam lets a future revision probe an
   active pack's `continuity.probe` so pack cycles (e.g. `/s4l:forge`) get the same treatment — no rework.
6. **Deployment.** Version bump 5.6.0 → 5.7.0 (both manifests) so the plugin actually updates;
   `/li:doctor` gains a firing check + a version-staleness warning. Also co-registered the orphaned
   `no-customer-data-in-message` UserPromptSubmit hook (it shipped but was never registered).

## Alternatives considered

- **Stronger SKILL.md prose only.** Rejected — prose is exactly what decays (proven repeatedly).
- **Extend the Stop hook / digest instead of a new hook.** Rejected — neither can inject *before* a
  turn; turn-start is structurally the missing moment.
- **Auto-write a provisional `CYCLE STARTING` from the hook (A2).** Rejected as default — it mutates
  state on a hot path and can write spurious markers; the A1 nudge keeps the hook read-only and is
  enough. (Left as a possible env-gated opt-in, not built.)
- **PreCompact hook.** Rejected — the event does not exist in Claude Code (verified).
- **Blocking the prompt until the cycle advances.** Rejected — drops/forces operator input; fights pause-points.

## Consequences

- **Positive:** position is re-armed every turn a cycle is active (killing the 2–3-phase decay), the
  footer always surfaces (turn-start + turn-end), and recovery survives compaction (the next
  UserPromptSubmit re-injects). Deployment is made loud so the fix actually reaches sessions.
- **Negative / residual:** hooks can inject + warn but cannot *force* model output — the model could
  still ignore a reminder. This residual is irreducible on Claude Code's substrate and is strictly
  smaller than edges-only continuity. Claude-Code-only; other CLIs keep the prose footer fallback.
- **Neutral:** one more hook fires per turn, but it self-exits cheaply when no cycle is active.

## References

- `hooks/shared/cycle-position-inject/{run.sh,HOOK.md}`, `hooks/hooks.json` (UserPromptSubmit block).
- Reuses `lib/cycle-footer.sh::render_cycle_footer`, `lib/state.sh::state_cycle_segment`,
  `hooks/shared/_input.sh::hook_input`. Tested in `tests/unit/cycle-continuity.sh` (sections 5–7).
- ADR-0022; lessons L-016, L-018.
