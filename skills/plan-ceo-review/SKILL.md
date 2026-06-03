---
name: plan-ceo-review
layer: foundation
description: Strategy + scope review. Surface product/business assumptions before architecture lands.
color: purple
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /plan-ceo-review

Strategy-level review of a plan or design doc. Asks the hard product/business questions BEFORE `/plan-eng-review` locks architecture. Optional but recommended for any plan that changes user-facing behavior, expands scope, or introduces a new market position.

Lintel's CEO review is **inspired-by gstack's** equivalent but written fresh per the inspiration-not-plagiarism constraint. Voice stays internal (this is operator-to-operator strategic challenge, not customer-facing).

## When to use

- Plan introduces new user-facing features
- Plan changes product direction
- Scope feels ambitious — challenge the wedge
- Before deciding to build vs. partner vs. defer

## When NOT to use

- Pure bug fix, refactor, infra cleanup — no product surface change
- Internal-tool work with no external impact
- Plan is already approved + scope is stable

## Inputs

- Optional path to a design doc (auto-discovers latest from `~/.gstack/projects/<slug>/*-design-*.md`).
- No-args: reviews the currently active design context (operator pastes plan or skill reads recent design from `~/.gstack/projects/`).

## Workflow

1. **Read design context.** Authoritative source is whichever design doc is freshest in `~/.gstack/projects/<slug>/`.
2. **Three forcing questions** — one AskUserQuestion per question. Skip if answer is already in the design doc.
   - **Q1 Demand reality:** strongest evidence someone actually wants this — not interest, not signups, behavior + money + panic-when-it-breaks?
   - **Q2 Wedge specificity:** smallest version someone would pay real money for this week, not after the platform ships?
   - **Q3 3-year fit:** if the world looks meaningfully different in 3 years (and it will), does this become MORE essential or less?
3. **Premise challenge** — list 3-5 load-bearing premises the design assumes. Ask operator to confirm each. If any rejected → revise design before continuing.
4. **Scope deltas** — propose 1-2 scope EXPANSIONS (10-star versions) and 1-2 scope REDUCTIONS (minimum viable wedge). Operator picks.
5. **Founder signal synthesis** — observe what the operator said + how they said it. Surface what their answers reveal about conviction, taste, agency.

## Report format

```markdown
## CEO Review — <design doc title>

**Demand evidence (Q1):** <quote operator's answer>
**Wedge (Q2):** <quote>
**3-year fit (Q3):** <quote>

**Agreed premises:**
1. <premise> ✓
2. <premise> ✓

**Scope deltas considered:**
- Expansion A: <one-line> — operator: <accepted|rejected|deferred>
- Expansion B: <one-line> — operator: <decision>
- Reduction C: <one-line> — operator: <decision>

**Founder signals observed:**
- <signal 1>
- <signal 2>

**Verdict:** SCOPE LOCKED — proceed to /plan-eng-review
        OR  REVISE — design doc needs <specific change> before eng review
```

Persist via first-party `bin/li-review-log` (legacy alias: gstack-review-log):
```bash
bin/li-review-log '{"skill":"plan-ceo-review","timestamp":"...","status":"...","scope_proposed":N,"scope_accepted":N,"scope_deferred":N,"mode":"...","commit":"..."}'
```

## Compliance integration

The 5 always-on rules apply during the review (don't surface customer data in the review prose). Otherwise no specific compliance hooks.

## Voice tier note

This skill's output uses `voice: internal` — direct, operator-to-operator. Even when reviewing a customer-facing product, the review itself is for the internal team. No elevated voice tier applies regardless of the active pack.

## Failure modes

- **No design doc found:** suggest `/office-hours` first to produce one.
- **Operator unwilling to engage with hard questions:** offer escape hatch ("ask 2 more, then proceed"). Don't gatekeep beyond that.
- **Premise rejected mid-review:** loop back. Don't proceed with a known-false premise.

## Examples

**Healthy scope-locked outcome:**
```
> /plan-ceo-review
[3 forcing questions answered, 5 premises agreed]
✓ Verdict: SCOPE LOCKED — proceed to /plan-eng-review
  Design doc updated: jokerman-main-design-20260527-152200.md
```

**Revise outcome:**
```
> /plan-ceo-review
[Q2 wedge: operator can't name a specific user/payer]
✗ Verdict: REVISE — design doc lacks demand evidence
  Recommend: /office-hours to surface specific demand signals
  Status: blocked, no /plan-eng-review yet
```

## See also

- `/office-hours` — design doc generator (run before this skill if no doc exists)
- `/plan-eng-review` — runs after this (architecture & tests)
- `/autoplan` — chains office-hours → ceo-review → eng-review → design-review
- `/plan-tune` — auto-decide question preferences over time
