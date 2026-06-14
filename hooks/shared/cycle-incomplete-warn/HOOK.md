---
name: cycle-incomplete-warn
tier: warn-only
event: Stop
fires_on: turn end while an active cycle is open mid-flight (a phase started, cycle not complete)
override: none needed — say `go` / `pause` / `/li:capture`, or it stays silent once the cycle closes
necessity: RECOMMENDED
gap_if_skipped: "The session can silently end mid-cycle with no position footer — the recurring 'did lots of work, then total silence, no next step' symptom (L-008, L-016). The footer convention reverts to 100% model-discipline."
audit: .claude/runtime/audit/hooks.jsonl
---

# cycle-incomplete-warn

The mechanical backstop for the cycle-position footer (ADR-0003). Until this hook, the
footer was rendered ONLY when the model chose to run `render_cycle_footer` — invisible
discipline, which ADR-0003 itself warns "is indistinguishable from no discipline." Across
long BUILDs, subagent returns, and context compaction the model's adherence decays and the
turn ends with no footer; the operator sees silence and the thread looks lost.

## What it does

On every `Stop` event it sources `lib/cycle-footer.sh` and renders the auto-tier footer —
the single source of truth for "is a cycle active." If the footer is the thin "no active
cycle" line (no cycle, or `cycle_complete: true`), the hook stays **silent**. If a cycle is
genuinely open mid-flight, it prints the position footer + the one next action, so the
operator always sees where the session is, even when the model forgot to.

## Why warn-only, never block

A `Stop` hook fires on EVERY turn end. A *blocking* Stop hook (`decision: block` / exit 2)
forces the model to continue and can re-trigger itself → infinite loop, and it would block
legitimate stops. This hook is stdout + `exit 0`: it surfaces the canary, it does not coerce
the model. The reliable re-injection half (telling a fresh/resumed/compacted session where it
was) is the SessionStart digest's `Current cycle:` line, not this hook.

## Failure mode

Fully fail-open: any error sourcing the footer or reading state → `exit 0`, silent. It can
never break turn-end. Claude-Code-only (Stop hooks are a Claude Code feature); other CLIs
keep the prose footer convention as the fallback.
