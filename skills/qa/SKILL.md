---
name: qa
layer: foundation
description: Use when you need to know whether the code works and to get the test suite green — runs the full suite, parses failures, fixes common ones, and re-runs until clean or genuinely stuck. Reach for it after making changes or when tests are failing and you want them resolved.
color: yellow
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /qa

The active-QA skill. Runs the repo's test suite, parses failures, applies targeted fixes for common patterns (snapshot drift, lint nits, type errors, missing imports), re-runs, and reports a clean pass or a structured stuck-state. Distinct from `/qa-only`, which never edits.

## When to use

- You just finished implementation and want a clean test pass before `/review` or `/ship`
- CI is red and you want to reproduce + fix locally before pushing
- After a refactor where snapshots and fixtures need to catch up

## When NOT to use

- Tests have never passed on this branch — first establish a green baseline manually
- Failures are clearly product-logic bugs — use `/investigate` instead (hypothesis-driven, no auto-fix)
- Production deploy gate — use `/qa-only` (read-only, no edits)

## Inputs

- Optional `--scope <path>` — run only tests matching the path (default: full suite)
- Optional `--no-fix` — report failures, do not attempt fixes (same shape as `/qa-only`)
- Optional `--max-iterations <N>` — stop after N fix+rerun cycles (default: 3)

## Workflow

1. **Detect test runner** — read `package.json` / `pyproject.toml` / `Cargo.toml` / equivalent. Pick the canonical script (`npm test`, `pytest`, `cargo test`). If multiple: ask via AskUserQuestion.
2. **Baseline run** — execute, capture stdout/stderr + exit code. If clean: report + exit.
3. **Failure classification** — group failures into buckets:
   - Snapshot drift (stable diff, no logic change) → auto-fix candidate
   - Lint / format nit → auto-fix candidate
   - Type error from new code → auto-fix candidate (add missing import, fix obvious typo)
   - Assertion failure (real product behavior) → DO NOT auto-fix, escalate
   - Flaky / timeout → retry once, then escalate
4. **Auto-fix cycle** — for each auto-fix candidate, apply the targeted Edit. Group fixes into one commit-able batch. NEVER touch product code without explicit operator confirmation.
5. **Re-run** — repeat steps 2-4 up to `--max-iterations`.
6. **Final state** — either CLEAN PASS or STUCK with structured report.

## Report format

```
QA Status: <branch>

Runner: npm test
Iterations: 2/3
Initial failures: 7
Auto-fixed: 5
  - 3× snapshot drift (src/components/case/__snapshots__/)
  - 1× lint (src/lib/dlxClient.ts: unused import)
  - 1× missing import (src/hooks/useCaseBrain.ts: useEffect)
Remaining: 2

## Stuck — escalating
[FAIL] tests/billing.test.ts:42 — expected 100, got 200
  Likely cause: real product logic — refund doubles amount
  Recommendation: /investigate

[FAIL] tests/e2e/auth.spec.ts:18 — timeout waiting for #login-btn
  Likely cause: flaky — but failed twice in a row, suspect real
  Recommendation: read playwright trace at .playwright/trace.zip
```

## Compliance integration

- Sanity-scan on every Edit before applying (no secrets/customer-data in fix payload).
- If auto-fix would touch a frozen-zone path (per project CLAUDE.md): block + escalate.
- Audit-log every auto-fix mechanically (Layer 2 traceability):
  `source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"; audit_log qa-fixes auto_fix file=<path> fix_kind=<lint|snapshot|import|assertion>` → `.claude/runtime/audit/qa-fixes.jsonl`.

## Failure modes

- **No test runner detected:** report + ask operator to declare via `package.json` scripts or `~/.lintel/qa.yaml`.
- **Runner crashes (not test failure, runner itself):** report + exit. Do not retry blindly.
- **Max iterations hit with failures remaining:** STUCK state — surface full failure list + recommendations. Operator chooses next move.
- **Auto-fix introduces a NEW failure:** revert the fix, mark that failure non-auto-fixable, continue with remaining.

## Examples

**Clean pass:**
```
> /qa
✓ All tests pass (npm test, 1 iteration, 142 tests / 0 failures)
Ready for /review.
```

**Auto-fix success:**
```
> /qa
Iteration 1: 7 failures
Iteration 2: 0 failures (auto-fixed 7)
✓ Clean after 2 iterations. Fixes batched.
```

**Stuck on real bug:**
```
> /qa
Iteration 3: 2 failures remaining (non-auto-fixable)
✗ STUCK — see report. Recommendation: /investigate
```

## See also

- `/qa-only` — read-only variant for ship-gate verification
- `/investigate` — when QA finds a real product-logic bug
- `/review` — runs after QA clean for diff-scoped review
- `/ship` — reads QA status as a pre-flight gate
