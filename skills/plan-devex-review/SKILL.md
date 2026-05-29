---
name: plan-devex-review
layer: foundation
description: Developer experience gaps review. Slow CI, painful deploys, bad local dev, attrition signals.
color: orange
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /plan-devex-review

Reviews a plan's impact on developer experience (DX). DX is a leading indicator of code quality — slow CI, bad local dev, painful deploys → worse software, higher attrition. Optional review tier.

Lintel version inspired-by gstack equivalent. Scores against DX pillars. Surfaces time-to-hello-world (TTHW) as the headline metric.

## When to use

- Plan introduces new tooling that engineers will touch daily (CI step, local dev script, deploy pipeline)
- Plan changes a contributor onboarding flow (new repo setup, new test command)
- A "two-week smell test" failure recently happened (competent engineer couldn't ship a small feature in two weeks → onboarding problem)
- Existing devex-review predates significant tooling changes

## When NOT to use

- Plans that don't touch tools engineers interact with daily
- Customer-facing features without contributor-facing impact

## Inputs

- Optional path to plan/design doc.
- Optional `--product-type <cli|library|service|sdk|harness>` — informs DX baseline expectations.

## Workflow

Measure / score 6 dimensions:

1. **Time-to-hello-world (TTHW)** — clone → working state. Stretch targets:
   - CLI: <5 min cold
   - Library: <2 min
   - Service: <15 min
   - SDK: <10 min
   - Harness (like Lintel): <10 min cold
2. **Test loop latency** — change → test result. <30s warm, <2min full suite is target.
3. **Deploy pain** — number of manual steps to ship a fix. >3 steps is bad.
4. **Local dev fidelity** — local matches prod? mocks where real services would be better?
5. **Error message quality** — does the error tell the engineer what to do, or just "something failed"?
6. **Documentation freshness** — last commit on README vs last code commit on touched areas?

Each dimension: measure (where possible) + 1-3 specific findings + AskUserQuestion per finding.

## Report format

```markdown
## DX Review — <plan title>

| Dimension | Initial | After fixes | TTHW measured |
|---|---|---|---|
| TTHW | (current) <8 min | (target) <5 min | bash install.sh + verify.sh, 4m 32s on op machine |
| Test loop | warm: 18s, full: 4m | warm: 18s, full: 90s | reduced full by parallelizing |
| Deploy pain | 5 steps | 2 steps | scripted GitHub Actions trigger |
| Local fidelity | 6/10 | 7/10 | added Docker compose for upstream sources |
| Error msg quality | 5/10 | 8/10 | rewrote install.sh failure paths |
| Docs freshness | README 47 days old | README current | added to /release-ev2 checklist |

**Overall:** 6.0/10 → 7.7/10 (after 9 decisions)
**Competitive tier:** mid-pack (target: top-quartile for harness category)
**Persona:** CAIP SE — primary, intrapreneur secondary
```

Persist via first-party `bin/li-review-log` (legacy alias: gstack-review-log):
```bash
bin/li-review-log '{"skill":"plan-devex-review","timestamp":"...","status":"...","initial_score":N,"overall_score":N,"product_type":"...","tthw_current":"...","tthw_target":"...","mode":"...","persona":"...","competitive_tier":"...","unresolved":N,"commit":"..."}'
```

## Compliance integration

None directly. DX is engineering-internal.

## Voice tier note

`voice: internal`. Reviewers and the team are the audience.

## Failure modes

- **No measurable TTHW:** estimate from clone → first useful output. Annotate as estimate.
- **Operator pushes back on every finding:** that's a signal — log it and proceed. The dimension scores still surface for future reference.
- **Plan doesn't change DX-relevant code:** report "no DX scope detected. Skipping."

## Two-week smell test

Specifically called out: if a competent engineer can't ship a small feature in this codebase in two weeks, the plan should address THAT first. Otherwise scope is wrong.

When invoked: ask operator "has anyone (incl. yourself) failed the two-week smell test in this codebase recently?" If yes → recommend deferring feature work + prioritizing DX work in current plan.

## Examples

**Harness plan:**
```
> /plan-devex-review --product-type harness
[6 dimensions measured]
✓ Overall: 6.0 → 7.7/10
  TTHW reduced 8m → 4m 32s
  9 decisions, 0 unresolved
```

**Backend service plan, no DX scope:**
```
> /plan-devex-review --product-type service
[Step 0: no DX-touching changes]
✗ No DX scope detected. Skipping.
  /plan-eng-review covers backend arch.
```

## See also

- `/devex-review` — diff-scoped lighter variant
- `/plan-eng-review` — required arch review (DX often surfaces issues for eng to fix)
- `/plan-design-review` — UX review (some DX issues are actually UX issues for engineers)
