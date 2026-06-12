---
name: tq-flaky-quarantine
layer: foundation
description: TQ sub-skill — flaky test detection + quarantine + remediation plan. Dispatches to TestRunner + RegressionDetective.
color: green
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-FLAKY-QUARANTINE — the workflow that surfaces + quarantines flaky tests.

## What this skill does

Reads recent test-run history (CI logs, junit XML, etc.). Spawns `TestRunner` to identify tests with inconsistent pass/fail across runs and `RegressionDetective` to classify root cause (timing race, external dependency, order-dependent, environment) + propose remediation. Produces flaky-quarantine list with per-test remediation plan + quarantine duration cap.

## When to use

- TQ full pass (typically after coverage_targets_met, runs alongside other checkpoints)
- Single action `/li:tq single --action flaky-quarantine`
- After CI flake-rate exceeds tolerance
- Quarterly flake-rate review

## When NOT to use

- Single flaky test (analyze inline)
- New test failures (those are regressions, not flakes)

## Workflow

### Step 1 — Read context

```bash
flaky_threshold="${threshold:-${flaky_quarantine_threshold:-3}}"   # consecutive runs failing before quarantine
test_history=".claude/runtime/state/tq/test-history.json"
```

### Step 2 — Spawn TestRunner for flake detection

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Identify flaky tests from recent run history
context_pointers:
  - $test_history (if present)
  - CI logs (last 30 runs, if available)
constraints:
  - flake definition: pass/fail inconsistent across ≥${flaky_threshold} runs on same code
  - per flaky test: failure count, failure rate, first-flake date
  - distinguish: flake vs. legitimate intermittent regression
acceptance:
  - structured flake list with run history
EOF

/li:brief-forge subagent_spawn tq-flaky-quarantine TestRunner brief "$brief_file"
```

### Step 3 — Spawn RegressionDetective for root-cause + remediation

```bash
remediation_brief=$(mktemp)
cat > "$remediation_brief" <<EOF
task: Classify flake root cause + propose remediation
context_pointers:
  - .claude/runtime/state/tq/flake-list.md
constraints:
  - per test: root cause (timing-race | external-dep | order-dependent | env-specific | unknown)
  - per test: remediation (deflake | rewrite | delete | accept-flake)
  - quarantine duration cap (default 14 days; longer = remediation work needed)
acceptance:
  - per-flake remediation plan + quarantine duration
EOF

/li:brief-forge subagent_spawn tq-flaky-quarantine RegressionDetective brief "$remediation_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/tq/flaky-quarantine-$ts.md"
{
  echo "# Flaky quarantine — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Threshold: $flaky_threshold consecutive failures"
  echo ""
  echo "## Flake list + remediation"
  cat .claude/runtime/state/tq/flake-remediation.md
} > "$out"

printf '{"ts":"%s","kind":"tq_flaky_quarantine","threshold":%d,"flaky":%d,"quarantined":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$flaky_threshold" "$flaky_count" "$quarantined_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — flake list emitted with per-test remediation
- **DONE_WITH_CONCERNS** — quarantines > 5 tests (signals systemic flake issue)
- **BLOCKED** — no test history available (need CI integration first)

## Integration

**Reads:** test history / CI logs
**Writes:** `.claude/runtime/state/tq/flaky-quarantine-<ts>.md`, audit JSONL
**Dispatches to:** TestRunner (detection), RegressionDetective (root-cause + remediation)

## Anti-patterns

- **Quarantine without remediation plan** — quarantine is temporary; the work is to remove flakes, not hide them
- **Treating all flakes as same root cause** — timing vs env vs order all need different remediation
- **Accept-flake without explicit justification** — flake hides regressions; accept only with documented reason
- **Hardcoding threshold** — read profile
