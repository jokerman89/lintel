# The skill protocol — stated once

> ADR-0009. This document is the SINGLE statement of the conventions every Lintel skill
> follows. Before v5.1 these were restated as boilerplate sections in 110-166 SKILL.md files
> (~20-30% of the entire skill surface); now a skill carries a section ONLY when it deviates
> from the defaults below. The cycle spine (the 9 phases + cycle/resume/jobs/status/welcome/
> brief-forge/analyze) keeps its protocol sections inline — there they ARE the contract.

## Status protocol (default)

Every skill reports one of:

- **DONE** — completed, output delivered.
- **DONE_WITH_CONCERNS** — completed, but findings/caveats the operator should see.
- **BLOCKED** — cannot proceed; report the blocker and stop. Never silently continue.
- **NEEDS_CONTEXT** — missing input only the operator can provide; ask, then resume.

A skill documents statuses inline only when a status carries skill-specific meaning
(e.g. BUILD's per-task statuses, REVIEW's ship verdicts).

## Hop-in (default: yes)

Skills are solo-invokable unless they state otherwise. A skill documents hop-in inline only
when it has REAL entry dependencies (e.g. BUILD requires a plan; SHIP requires REVIEW PASS).

## Voice (default: frontmatter)

The `voice:` frontmatter field is authoritative; resolution goes through the active pack
(`resolve_pack_field voice.default_tier`). No prose section needed unless the skill mixes
tiers or raises them for customer-facing output.

## Pause-points (default: none)

Skills run to completion. Inline pause-gates exist only where a decision is genuinely the
operator's (cost gates, design approval, destructive actions) — and are documented inline
at the gate, not in a trailing section.

## Failure recovery (default)

On error: report what failed (file:line / command output), set BLOCKED, propose the next
action. Retry only idempotent steps. Never silently skip a failed step. Skills document
recovery inline only when they own a non-default protocol (e.g. CYCLE's retry/skip/loop-back).

## Compliance (default: pack-resolved)

Compliance gates resolve through the active pack (`compliance.hooks`, `compliance.mode`).
The neutral `_default` pack enforces nothing. Skills document compliance inline only when
they invoke gates regardless of pack (e.g. customer-data handling in context-warm-customer).

## State ledger (default)

Cycle-participating skills close with one `state_append <PHASE> <STATUS> [next=X] [k=v...]`
(lib/state.sh) and render the cycle footer (lib/cycle-footer.sh). See ADR-0008.

## Frontmatter contract (unchanged)

Required: `name`, `layer`, `description`, `color`, `tools`, `voice`, `cli_support`.
Optional since v5.1: `hop_in: no` (only when not solo-invokable). Everything else in this
document is convention, not frontmatter.
