# ADR-0003 — cycle-position footer on every official report

- Status: Accepted
- Date: 2026-06-09
- Deciders: operator + Claude (meta-infra cycle)
- Supersedes: —
- Related: ADR-0002 (session-digest auto-load), `skills/cycle/SKILL.md` (phase-progress)

## Context

An operator can enter the 9-step Lintel cycle (`SENSE → SCOPE → DEFINE → DISCOVER → PLAN →
BUILD → REVIEW → SHIP → CAPTURE`) at the start, middle, or end — via `/li:cycle`, a standalone
phase skill, `/li:resume`, or a mode preset that skips phases. Reports came back with no
positional anchor: the operator finished reading and did not know *where they were* in the cycle
or *what the single logical next action was*. This surfaced concretely during the 2026-06-09
research-dive run, which delivered a large report but never said "you are here → next is this →
say `go`."

Two external harnesses independently validate the need. superpowers #446 ("How do I know if
superpowers is even running?", 22 comments) was fixed by making activation *visibly announce
itself* — invisible discipline is indistinguishable from no discipline. spec-kit's value comes
from explicit phase artifacts the user can see. The lesson: **the harness must always tell the
operator their position and the next move.**

A second need emerged mid-build: the same affordance, much lighter, for *normal* messages
outside the cycle — a thin ambient line, not a heavy block.

## Decision

Add a single shared helper, `lib/cycle-footer.sh::render_cycle_footer`, that every official-skill
report calls at its close. One entry point, three tiers, auto-selected:

- **full** (default, in a cycle) — legend + a 9-step stepper (`✅ done · ⊘ skipped · 📍 here ·
  ▢ pending`) + a "you are here / next / say-this" block with the literal next command.
- **compact** (`--compact`, in a cycle) — a one-line variant for short single-answer replies.
- **thin** (no active cycle) — an ambient one-liner (`` `li` · no active cycle — `/li:cycle` … ``)
  for normal Q&A outside the curated cycle.

Design decisions:

- **D1 — three tiers, one helper.** Subtraction bias: the thin/compact/full split is a tier
  argument, not three code paths to maintain.
- **D2 — emoji primary, ASCII fallback.** `LINTEL_ASCII=1` / `--ascii` renders
  `[x]/[~]/[>]/[ ]` and keeps *all* labels emoji-free, for terminals that mangle glyphs — a
  convergent cross-platform lesson (superpowers #275, spec-kit #1946).
- **D3 — close of a user-facing report**, not every micro-message. Phase skills + the cycle
  orchestrator always; other official skills (welcome/jobs/resume/status) in a later phase.
- **D4 — question-mode.** `--awaiting "<hint>"` flips the next block to "Awaiting your answer"
  and suppresses the next-command table, so a phase that needs operator input says so as the
  *last line*.
- **Shared schema.** The mode→skipped-phases map lives once in `lib/cycle-modes.sh`, consumed by
  both the footer and (going forward) the cycle presets — the skip-map can never disagree with
  what a mode actually runs.
- **Tolerant + fail-open.** The state parser is CRLF-safe, jq/yq-free, reads the append-log
  `.lintel/state/00-state.md` (last `phase:` = here, its `next_recommended:` = next, mode from
  `cycle_mode:`); unknown mode → skip nothing; no state → thin ambient. It never errors a report.

## Consequences

**Positive.** Every report ends with an unambiguous position + next action; entry at any phase is
self-locating; the thin tier gives ambient orientation outside the cycle at near-zero cost;
`cycle-modes.sh` removes a latent duplication; the helper is unit-tested (41 assertions,
`tests/unit/cycle-footer.sh`) — including the fail-open paths an independent REVIEW pass flagged
(trailing value-flag must not hang, unknown/lowercase phase, garbage state file), so the
"never errors a report" guarantee is tested, not just asserted.

**Negative / cost.** A new output convention ~30 cycle surfaces must adopt (phased: orchestrator
first, then the 9 phase skills, then the rest). A few lines of footer per report — mitigated by
the compact/thin tiers. The mode→skip map now has a second consumer to keep honest (covered by
the unit test).

**Follow-ups — all shipped (Phases 2–3).** Phase 2 wired the 9 phase skills + a presence shape test.
Phase 3 extended the footer to the high-traffic non-phase entry points (welcome/jobs/resume/status)
and had the cycle orchestrator write `cycle_mode:` into `00-state.md`, so the footer resolves the
skipped-phase glyphs from state alone without an explicit `--mode`. The footer now closes every
official entry point — inside a cycle (full/compact) or outside one (thin ambient).
