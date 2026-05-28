---
name: jstack-qa-only
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

- Final pre-`/release-ev2` verification — want to know tests pass without any drive-by changes
- CI parity check — reproduce remote CI failure locally without polluting the branch
- Sanity check after `/qa` to confirm the auto-fixes didn't introduce regressions
- Anywhere a "fresh eyes" report is needed without skill-level mutation

## When NOT to use

- You want failures auto-fixed — use `/qa` instead
- You're debugging a single failure deeply — use `/investigate`
- Tests aren't set up yet — use `/setup-ev2-targets` or repo-specific bootstrap first

## Inputs

- Optional `--scope <path>` — restrict to a path subset
- Optional `--json` — emit machine-readable JSON report (for piping into `/release-ev2` gate)
- Optional `--verbose` — include full stack traces for each failure (default: first 10 lines)

## Workflow

1. **Detect test runner** — same logic as `/qa`. If ambiguous: ask once via AskUserQuestion.
2. **Single run** — execute test command, capture stdout/stderr/exit code. No retry-on-flake (operator can run again if they suspect flake).
3. **Parse + classify** — same buckets as `/qa` (snapshot / lint / type / assertion / flaky), but no fix attempt. Classification informs the report's recommendation column.
4. **Report** — structured failure list with file:line, category, and a one-line cause hypothesis.
5. **Exit code** — 0 if clean, 1 if any failures. Suitable for shell-piping.

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

## Voice tier note

`voice: internal`. Test reports are engineering-internal.

## Failure modes

- **No tests found in scope:** report explicitly ("0 tests matched scope") + exit 0. Empty scope is not a failure.
- **Runner crashes:** report stderr + exit 2 (distinct from test-failure exit 1).
- **Network/db dependency unavailable:** report dependency missing + exit 3. Do not retry.

## Examples

**Clean:**
```
> /qa-only
✓ pytest: 87 pass / 0 fail / 2 skip (exit 0)
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
- `/release-ev2` — calls `/qa-only --json` as a gate
- `/investigate` — when a failure is product-logic
- `/careful` — wraps `/qa-only` in extra confirmation when stakes are high
