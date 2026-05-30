---
name: review
layer: foundation
description: Diff-scoped pre-landing code review. Lighter than /plan-eng-review, focused on changed code only.
color: red
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /review

Reviews the current branch's diff before landing. Lighter than `/plan-eng-review` (which reviews a plan/design doc). Use when there's no plan but you want a code review pass before `/release-ev2`.

Auto-scales: small diffs get fast review; large diffs (200+ lines) additionally get Codex structured review with P1 gate.

## When to use

- Branch is feature-complete, no design doc exists
- Quick correctness pass before `/release-ev2`
- Small fixes / refactors that don't warrant `/plan-eng-review`
- `/release-ev2` blocked by "Eng Review NOT CLEARED" and the work is too small for full plan-eng-review

## When NOT to use

- Plan exists — use `/plan-eng-review` against the plan instead
- Diff too small to be reviewable (<5 lines, trivial fix) — skip review
- Tests fail — fix first, review after

## Inputs

- Optional `--base <branch>` — compare against this base instead of default branch (default: `main`)
- Optional `--codex` — force Codex structured review even on small diffs
- Optional `--no-codex` — skip Codex even on large diffs

## Workflow

1. **Diff stats** — `git diff <base>...HEAD --stat`. Auto-classify:
   - <50 lines changed: SMALL (Claude-only review)
   - 50-200: MEDIUM (Claude + optional Codex)
   - 200+: LARGE (Claude + mandatory Codex with P1 gate, unless --no-codex)
2. **Read diff content** — `git diff <base>...HEAD`. Identify changed files + functions + tests.
3. **4-dimension review** (lighter than `/plan-eng-review`'s 4 sections — no per-issue AskUserQuestion overhead):
   - Architecture impact (does the diff respect existing boundaries?)
   - Code quality (DRY violations, error handling, edge cases)
   - Test coverage (does the diff add tests for new code paths? regression risk?)
   - Performance (N+1, memory, slow paths introduced)
4. **Codex pass (if LARGE diff or --codex)** — invoke Codex with structured review prompt. P1 findings BLOCK ship.
5. **Persist via first-party `bin/li-review-log`** (legacy alias: gstack-review-log) with `skill: review` (distinct from `plan-eng-review`).
6. **Output: findings list + severity + suggested fixes.**

## Report format

```
Review Status: <branch> vs <base>

Diff scope: 173 lines changed across 8 files (MEDIUM)
Codex pass: optional, skipped this run

## Findings (3)

[P2] (confidence: 8/10) src/services/billing.ts:47 — N+1 query in refund flow
   Loop calls payment.fetch() per refund; batch via .fetchMany()
   Suggested: ~5 line refactor

[P3] (confidence: 7/10) src/utils/format.ts:12 — DRY violation
   formatDate duplicated in format.ts and date-helpers.ts; consolidate

[P3] (confidence: 9/10) tests/billing.test.ts:NEW — Missing edge case
   refundPayment with 0 amount: no test. Add test or document why allowed.

## Verdict
- P1 count: 0 — no block
- P2 count: 1 — should fix before /release-ev2
- P3 count: 2 — recommended fixes

Run /release-ev2 when P2+ resolved.
```

Persist via first-party `bin/li-review-log` (legacy alias: gstack-review-log):
```bash
bin/li-review-log '{"skill":"review","timestamp":"...","status":"...","findings":N,"findings_fixed":N,"gate":"P1_clean","commit":"..."}'
```

## Compliance integration

- Sanity scan on diff content (secrets, customer-data, PII) — fast pre-check. Blocks if hit.
- `cli_support` + `voice` frontmatter validation on any new/changed skill or agent files in the diff.

## Confidence scoring

Every finding gets a 1-10 confidence:
- 9-10: verified by reading specific code
- 7-8: high-confidence pattern match
- 5-6: medium — show with "verify this is actually an issue" caveat
- 3-4: suppressed from main report, appendix only
- 1-2: speculation only (rarely reported)

## Voice tier note

`voice: internal`. Code review prose is engineering-internal.

## Failure modes

- **Diff empty:** no changes to review. Report + exit.
- **Diff too large to fully analyze:** spot-check + warn operator that some files weren't deeply reviewed.
- **Codex unavailable:** fall back to Claude adversarial subagent. Note in report.
- **`bin/li-review-log` unavailable:** still print findings, but no dashboard update.

## Examples

**Small clean diff:**
```
> /review
Diff scope: 23 lines, 2 files (SMALL)
✓ No findings. Clean to /release-ev2.
```

**Medium diff with findings:**
```
> /review
[3 findings reported]
P1: 0, P2: 1, P3: 2
Action: fix P2 before /release-ev2.
```

**Large diff with Codex P1 gate:**
```
> /review
Diff: 412 lines, 18 files (LARGE)
Codex pass: P1 found — race condition in payment-handler.ts:108
✗ /release-ev2 BLOCKED until P1 resolved
```

## See also

- `/plan-eng-review` — heavier plan-stage review (use when design doc exists)
- `/investigate` — debugging when /review finds something broken
- `/release-ev2` — reads /review's dashboard entry as ship-gate signal (within 7 days, current commit)
