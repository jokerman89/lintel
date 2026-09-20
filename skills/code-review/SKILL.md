---
name: code-review
layer: foundation
description: Use before landing a change to review just the diff — focused on the changed code only, lighter than a full engineering review. Reach for it when you have uncommitted or unmerged changes and want a correctness and quality pass before they land.
color: red
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /code-review

Reviews the current branch's diff before landing. Lighter than `/plan-eng-review` (which reviews a plan/design doc). Use when there's no plan but you want a code review pass before `/ship`.

Auto-scales by aggregate risk: mechanical diffs may use explicitly labeled inline
review; substantive changes need a separately attributable reviewer. An optional
outside-review tool does not substitute for missing independence.

## When to use

- Branch is feature-complete, no design doc exists
- Quick correctness pass before `/ship`
- Small fixes / refactors that don't warrant `/plan-eng-review`
- `/ship` blocked by "Eng Review NOT CLEARED" and the work is too small for full plan-eng-review

## When NOT to use

- Plan exists — use `/plan-eng-review` against the plan instead
- Trivial mechanical diff — inline review is proportionate; record the actual mode
- Tests fail — fix first, review after

## Inputs

- Optional `--base <branch>` — compare against this base instead of default branch (default: `main`)
- Optional `--codex` — force Codex structured review even on small diffs
- Optional `--no-codex` — skip Codex even on large diffs

## Workflow

For ad-hoc work with no initiative map, keep this lightweight: capture an explicit
snapshot, review it and return useful read-only findings. Do not create a duplicate
plan/backlog merely to get review feedback. The shared `snapshot` + `inspect`
commands can bind observations without a map; they explicitly report
`release_clearance: false`. Mapped authority and full evidence are needed only to
enter the strict SHIP path. See [inspection mode](../review/references/evidence.md#unmapped-inspection).

1. **Bind scope** — follow [the shared evidence procedure](../review/references/evidence.md).
   Include explicitly selected tracked, staged, unstaged, new and deleted files,
   documentation/config inputs and the selected package/leaf acceptance. Use the
   snapshot manifest for scope; `git diff <base>...HEAD --stat` covers only committed
   changes. Preserve useful SMALL/MEDIUM/LARGE reporting without using line count
   to downgrade substantive risk.
2. **Read selected content** — inspect every selected changed state and relevant
   surrounding functions/tests. A commit-only diff cannot clear dirty/new files.
3. **4-dimension review** (lighter than `/plan-eng-review`'s 4 sections — no per-issue AskUserQuestion overhead):
   - Architecture impact (does the diff respect existing boundaries?)
   - Code quality (DRY violations, error handling, edge cases)
   - Test coverage (does the diff add tests for new code paths? regression risk?)
   - Performance (N+1, memory, slow paths introduced)
4. **Independent pass** — use an actual available independent reviewer for substantive
   scope. `--codex` requests an outside review when available; `--no-codex` does not
   waive required independence. Keep findings read-only and route fixes to the builder.
5. **Persist via `bin/li-review-log`** with `skill: code-review` (distinct from Phase-6 `/review` and `plan-eng-review`).
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
- P2 count: 1 — should fix before /ship
- P3 count: 2 — recommended fixes

Run /ship when P2+ resolved.
```

Persist the full version-1 decision with `skill: code-review` through the shared
writer, then consume the shared reader with the same expected context and actual
host/human corroboration. The [procedure](../review/references/evidence.md) defines
the executable commands. Missing/unverified mandatory controls block independently
of advisory findings. Empty or placeholder commits and loose clearance strings
are not valid evidence.

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

## Failure modes

- **Diff empty:** implementation clearance is blocked. An approved verification-only
  task may use its actual acceptance evidence without inventing changes.
- **Diff too large to fully analyze:** spot-check + warn operator that some files weren't deeply reviewed.
- **Outside reviewer unavailable:** use an available separate reviewer or manual
  handoff. A main-agent self-review remains declared, not independently corroborated.
- **`bin/li-review-log` unavailable:** print findings; strict clearance remains blocked.

## Examples

**Small clean diff:**
```
> /code-review
Diff scope: 23 lines, 2 files (SMALL)
No findings. Ready for the shared evidence gate, not clearance from this sentence.
```

**Medium diff with findings:**
```
> /code-review
[3 findings reported]
P1: 0, P2: 1, P3: 2
Action: fix P2 before /ship.
```

**Large diff with Codex P1 gate:**
```
> /code-review
Diff: 412 lines, 18 files (LARGE)
Codex pass: P1 found — race condition in payment-handler.ts:108
✗ /ship BLOCKED until P1 resolved
```

## See also

- `/plan-eng-review` — heavier plan-stage review (use when design doc exists)
- `/investigate` — debugging when /code-review finds something broken
- `/ship` — consumes the latest applicable content-bound decision and same-context read-only QA
