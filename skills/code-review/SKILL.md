---
name: code-review
layer: foundation
description: Use before landing a change to review just the diff — focused on the changed code only, lighter than a full engineering review. Reach for it when you have uncommitted or unmerged changes and want a correctness and quality pass before they land.
color: red
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /code-review

Reviews the selected changed result before landing. Use `/inspect` for plan-stage
engineering/design/devex assessment; use this workflow for the implemented diff.
An existing plan supplies acceptance, not a reason to skip reviewing the code.

Auto-scales by aggregate risk: mechanical diffs may use explicitly labeled inline
review; substantive changes need a separately attributable reviewer. An optional
outside-review tool does not substitute for missing independence.

## When to use

- Branch is feature-complete, no design doc exists
- Quick correctness pass before `/ship`
- Small fixes / refactors needing focused correctness and quality feedback
- `/ship` needs the latest applicable content-bound review, not a clearance heading

## When NOT to use

- Only a plan exists, with no implementation to inspect — use `/inspect` on that plan
- Trivial mechanical diff — inline review is proportionate; record the actual mode
- Tests fail — fix first, review after

## Inputs

- Optional `--base <ref>` — compare against this explicit local base rather than the
  repository's known default branch; resolve an unknown base instead of guessing.
- Optional `--cross-check` — request an additional independent pass through `/cross-check`.
- Optional `--no-cross-check` — skip that optional additional pass; this does not waive
  required independent review of substantive work.
- Optional `--reviewer <name>` — select an actual reviewer/client for `--cross-check`;
  requires that flag. Codex remains a valid explicitly authorized client.

Invocation: `/code-review [--base <ref>] [--cross-check [--reviewer <name>] | --no-cross-check]`.
Conflicting cross-check flags are an input error, not a reason to choose silently.

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
3. **4-dimension review** (focused on implementation; no routine per-issue approval interview):
   - Architecture impact (does the diff respect existing boundaries?)
   - Code quality (DRY violations, error handling, edge cases)
   - Test coverage (does the diff add tests for new code paths? regression risk?)
   - Performance (N+1, memory, slow paths introduced)
4. **Independent pass** — use an actual available independent reviewer for substantive
   scope. `--cross-check` requests an additional separate opinion; skipping it does not
   waive required independence. Keep findings read-only and route fixes to the builder.
   Forward the exact selected snapshot to `/cross-check --diff`, including any
   explicit reviewer choice; do not substitute the current committed diff for it.
   A selected unavailable reviewer leaves that pass unverified, never silently replaced.
5. **Persist via `bin/li-review-log`** with `skill: code-review` (distinct from Phase-6
   `/review`, plan/repository `/inspect` and an additional `cross-check` decision).
6. **Output: findings list + severity + suggested fixes.**

## Report format

```
Review Status: <branch> vs <base>

Diff scope: 173 lines changed across 8 files (MEDIUM)
Additional cross-check: optional, not requested

## Findings (3)

[P2] (confidence: 8/10) src/services/billing.ts:47 — N+1 query in refund flow
   Loop calls payment.fetch() per refund; batch via .fetchMany()
   Suggested: ~5 line refactor

[P3] (confidence: 7/10) src/utils/format.ts:12 — DRY violation
   formatDate duplicated in format.ts and date-helpers.ts; consolidate

[P2] (confidence: 9/10) tests/billing.test.ts:NEW — Missing required edge case
   Selected acceptance requires refundPayment with 0 amount; no test covers it.
   Add the regression check and report its actual result.

## Verdict
- P1 count: 0 — no block
- P2 count: 2 — must resolve before /ship
- P3 count: 1 — advisory improvement

Resolve P1/P2 findings, then recheck the exact result through the shared evidence gate.
An empty finding count alone is not release clearance.
```

Persist the full version-2 decision with `skill: code-review` through the shared
writer, then consume the shared reader with the same expected context and actual
host/human corroboration. The [procedure](../review/references/evidence.md) defines
the executable commands. Preserve work/package/leaf IDs, attempt, profile context/
generation/digest and required policy; verify the current reference before consumption.
Missing/unverified mandatory controls block independently of advisory findings.
Empty or placeholder commits and loose clearance strings
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
- **Diff too large to fully analyze:** report unreviewed files/controls explicitly;
  partial findings cannot clear their mandatory acceptance.
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

**Large diff with a corroborated independent P1 finding:**
```
> /code-review
Diff: 412 lines, 18 files (LARGE)
Independent reviewer: P1 found — race condition in payment-handler.ts:108
✗ /ship BLOCKED until P1 resolved
```

## See also

- `/inspect` — engineering/design/devex lenses over a selected plan or repository
- `/diagnose` — debugging when /code-review finds something broken
- `/cross-check` — an additional separate opinion using an available authorized reviewer
- `/verify` — read-only validation of the reviewed result; repair requires explicit authority
- `/ship` — consumes the latest applicable content-bound decision and same-context read-only QA
