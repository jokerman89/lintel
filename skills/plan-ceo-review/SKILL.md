---
name: plan-ceo-review
layer: foundation
description: Use before architecture lands to review a plan's strategy and scope — surfaces the product and business assumptions baked into it. Reach for it when you want the why and the scope challenged before committing engineering effort to the how.
color: purple
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
hop_in: no
---

# /plan-ceo-review

Optional strategy/venture review of the selected plan/design. Invoke it for an
explicit strategy request, `--lens venture`, or an applicable operator-selected
pack lens. A large migration, maintenance task, research request or ordinary
user-facing feature does not automatically need a founder interview.
Follow [task-relevant intake](../define/references/intake.md).

Operator-to-operator strategic challenge before architecture locks: demand reality, wedge specificity, 3-year fit. Voice stays internal (this is a builder-to-builder challenge, not customer-facing).

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

- Explicit design path or the selected [work map](../spec-kit/references/work-map.md),
  validated with `bin/li-work-artifacts.py`; no timestamp/global-store selection.
- Verify the P07 reference and required-policy bridge before using pack criteria.

## Workflow

1. **Read design context.** Use the original mapped design/spec/task IDs and
   explicitly linked evidence. Prior answers and approval remain valid within scope.
2. **Three forcing questions** — one AskUserQuestion per question. Skip if answer is already in the design doc.
   - **Q1 Demand reality:** strongest evidence someone actually wants this — not interest, not signups, behavior + money + panic-when-it-breaks?
   - **Q2 Wedge specificity:** smallest version someone would pay real money for this week, not after the platform ships?
   - **Q3 3-year fit:** if the world looks meaningfully different in 3 years (and it will), does this become MORE essential or less?
3. **Premise challenge** — list 3-5 load-bearing premises the design assumes. Ask operator to confirm each. If any rejected → revise design before continuing.
4. **Scope deltas** — propose 1-2 scope EXPANSIONS (10-star versions) and 1-2 scope REDUCTIONS (minimum viable wedge). Operator picks.
5. **Decision-evidence synthesis** — record relevant stated priorities, observed
   user behavior and remaining uncertainty. Do not infer personality or founder
   traits from phrasing; optional pack framing does not replace factual evidence.

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

**Decision evidence and uncertainty:**
- <source-grounded priority or observation>
- <unverified premise and next evidence needed>

**Verdict:** SCOPE LOCKED — proceed to /plan-eng-review
        OR  REVISE — design doc needs <specific change> before eng review
```

Preserve the strategy report, scope deltas and original IDs. Use
[P05 evidence](../review/references/evidence.md) for a bound result:
prepare -> actual review -> `bash "$LINTEL_SOURCE_ROOT/bin/li-review-log" --file
"$review_record"` -> latest reader with expected context/corroboration.
Immutable QA obligations and required policy are not inferred from this lens's
score. For an unmapped/draft inspection use shared `snapshot`/`inspect`; it
declares `release_clearance:false`. A strategy heading or old SCOPE LOCKED/CLEAR
string never grants implementation or SHIP clearance.

## Failure modes

- **No design doc found:** suggest `/office-hours` first to produce one.
- **Operator declines optional questions:** stop that interview; retain genuinely
  unresolved material decisions without forcing two more questions.
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
- `/plan-tune` — dormant preference history; no runtime auto-decision consumer
