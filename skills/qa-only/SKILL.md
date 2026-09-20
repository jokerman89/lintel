---
name: qa-only
layer: foundation
description: Read-only test run — reports failures, never edits. For ship-gate verification.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /qa-only

The verification-only sibling of `/qa`. Runs the test suite, parses results, surfaces failures with full context — but **never edits anything**. Use as the pre-ship verification step or when you explicitly do not want auto-fixes muddying the diff.

## When to use

- Final pre-`/li:ship` verification — want to know tests pass without any drive-by changes
- CI parity check — reproduce remote CI failure locally without polluting the branch
- Sanity check after `/qa` to confirm the auto-fixes didn't introduce regressions
- Anywhere a "fresh eyes" report is needed without skill-level mutation

## When NOT to use

- You want failures auto-fixed — use `/qa` instead
- You're debugging a single failure deeply — use `/investigate`
- Tests aren't set up yet — use repo-specific bootstrap first

## Inputs

- Optional `--scope <path>` — restrict to a path subset
- Optional `--json` — emit machine-readable JSON report (for piping into `/li:ship` gate)
- Optional `--verbose` — include full stack traces for each failure (default: first 10 lines)

## Workflow

Without an initiative map, run read-only QA normally and preserve its useful
failure report. Do not create a redundant plan/backlog. Bind the observed controls
to an explicit snapshot with the shared
[inspection mode](../review/references/evidence.md#unmapped-inspection); that result
is explicitly NON-release-clearance. The full expected-context/SHIP path below is
for mapped authorized work, not a prerequisite for getting test feedback.

1. **Resolve applicable validation** — use approved acceptance. Detect the test
   runner as in `/qa` when tests apply. A docs-only package can instead require a
   real document/link/example check with source-grounded tests N/A; do not invent
   a universal software-test obligation.
   The prepared v2 context's `qa_requirements` is the immutable inventory. Results
   cannot omit IDs, change tests to generic checks, downgrade mandatory failures,
   declare new N/A scope or change policy references. A scope change needs a new
   prepared context and independent review, not revised observation labels.
2. **Single run** — use the reviewed expected context from the
   [shared evidence procedure](../review/references/evidence.md). Execute the real
   test command, capture stdout/stderr, command/environment inputs, actual
   executed/failed/skipped counts and exit code. No retry-on-flake or auto-fixes.
3. **Parse + classify** — same buckets as `/qa` (snapshot / lint / type / assertion / flaky), but no fix attempt. Classification informs the report's recommendation column.
4. **Report** — structured failure list with file:line, category, and a one-line cause hypothesis.
5. **Evidence and exit code** — emit the shared v2 QA record with `context_digest`,
   observed test controls and hashed evidence files via `li-review-evidence.py qa`.
   The helper validates observations; it does not run tests or document checks.
   Exit 0 requires an observed applicable mandatory validation, not N/A-only or
   advisory-only output. When tests apply, zero/failed/skipped required tests
   remain blocked even alongside a passing document check. Exit 3 means unresolved acceptance.
   Runner failures remain visible in the test control's actual exit code.
6. **Recheck identity** — SHIP consumes this exact context and the latest applicable
   independent review through `li-review-evidence.py ship`. Relevant source,
   config, dependency, document or acceptance changes require new affected checks.
   A run ten minutes ago is neither automatically valid nor automatically stale.

## Report format

```
QA-Only Status: <branch>

Runner: pytest
Exit: 1 (3 failures, 87 passes, 2 skipped)

## Failures

[1] tests/billing/test_refund.py:42 — assertion failure
   Expected: 100
   Got: 200
   Category: product logic
   Recommendation: /investigate

[2] tests/snapshots/test_landing.py:18 — snapshot mismatch
   Diff: 4 lines (whitespace + 1 attr)
   Category: snapshot drift
   Recommendation: /qa --scope tests/snapshots/

[3] tests/e2e/test_auth.py:91 — timeout 30s
   Category: possibly flaky
   Recommendation: re-run; if persistent, /investigate
```

## Compliance integration

- No mutations means no sanity-scan needed on edits (there are none).
- Reads test fixtures — if a fixture contains customer-data patterns, surface as a Layer 2 hint (read-only WARN, not BLOCK).

## Failure modes

- **No tests found in scope:** report "0 tests matched scope", record `unverified`
  and exit 3 for required acceptance. Never turn an empty error count into a pass.
- **Required tests skipped or browser/renderer unavailable:** record what was not
  observed and block the affected requirement; static checks may continue but do
  not prove runtime behavior.
- **Runner crashes:** report stderr + exit 2 (distinct from test-failure exit 1).
- **Network/db dependency unavailable:** report dependency missing + exit 3. Do not retry.

## Examples

**Clean:**
```
> /qa-only
pytest: 87 pass / 0 fail / 2 skip. Required skipped coverage remains unverified;
only explicitly grounded out-of-scope checks can be not applicable.
```

**Failures, JSON output:**
```
> /qa-only --json
{"runner":"pytest","passes":85,"failures":2,"skipped":2,"exit":1,"failures_list":[...]}
```

**Scope-limited:**
```
> /qa-only --scope tests/billing/
✓ 12 pass / 0 fail (scope: tests/billing/)
```

## See also

- `/qa` — active variant that auto-fixes
- `/li:ship` — calls `/qa-only --json` as a gate
- `/investigate` — when a failure is product-logic
- `/careful` — wraps `/qa-only` in extra confirmation when stakes are high
