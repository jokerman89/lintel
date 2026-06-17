---
name: cycle-position-inject
tier: inject-only
event: UserPromptSubmit
fires_on: every user prompt; injects context only when a cycle is active (or being invoked without a ledger)
override: none — it is silent + zero-cost outside a cycle; no operator action needed
necessity: RECOMMENDED
gap_if_skipped: "Cycle position is re-asserted only at session edges (SessionStart digest) and turn end (Stop hook). Nothing re-anchors the model at the START of a turn within a live session, so the footer + structured per-phase reports decay after ~2-3 phases — the operator's recurring 'we lose the thread mid-cycle' symptom (L-016, L-018)."
audit: .claude/runtime/audit/hooks.jsonl
---

# cycle-position-inject

The turn-START surface the continuity trifecta was missing (ADR-0023, extends ADR-0022).
SessionStart re-injects position once per session; the `Stop` hook surfaces the footer at turn
*end* — both are session/turn EDGES. Neither re-anchors the model *before* it generates a turn,
which is the only moment that can prevent a footer-less, off-thread turn. This hook is that moment.

## What it does

On every `UserPromptSubmit`, after a cheap state-file + `phase: CYCLE` marker pre-check (so it does
nothing when no cycle exists), it uses `render_cycle_footer --compact` — the single source of truth
for "is a cycle active" — and, if a cycle is genuinely mid-flight, injects via the
`UserPromptSubmit` `additionalContext` envelope: the compact position line + "render the footer, give
the per-phase report, and advance when this phase is done." If the prompt INVOKES a cycle
(`/li:cycle`, `/li:fix`, `/li:autoplan`, `/li:plan-and-build`) but no ledger marker exists yet, it
injects a one-line nudge to write `CYCLE STARTING` first (gap-A: the marker everything keys off).

## Why inject-only, never block

`UserPromptSubmit` fires on EVERY prompt and a hook that `exit 2` / `{"decision":"block"}` would DROP
the operator's prompt entirely. This hook is `exit 0` on every path — it adds context, it never
blocks and never coerces output (hooks can inject + warn, not force the model's reply; that residual
is irreducible). It re-arms adherence every turn instead of letting it decay monotonically.

## Cost

Silent path (the common case — no active cycle, prompt not a cycle invocation): one bounded stdin
read + a state-file existence check + a `grep` + a `case` glob, then `exit 0`. The footer lib is
sourced only when a cycle marker is present. No network, no writes, no git fork on the silent path.

## Failure mode

Fully fail-open: any error reading the prompt, sourcing the footer, or resolving state → `exit 0`,
silent. Claude-Code-only (UserPromptSubmit is a Claude Code hook); other CLIs keep the prose footer
convention as fallback.

## Pack cycles

Built cycle-source-agnostic: a commented seam (step 3 in `run.sh`) lets a future revision probe the
active pack's `continuity.probe` so pack-provided cycles (e.g. `/s4l:forge`) get the same treatment —
no rework needed.
