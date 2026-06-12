---
name: tq-regression-suite
layer: foundation
description: TQ sub-skill — golden-path tests + recent-bug-fix tests curated. Dispatches to RegressionDetective + TestRunner agents.
color: green
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-REGRESSION-SUITE — the workflow that curates the regression suite.

## What this skill does

Scans recent bug-fix commits + identifies golden paths (most-used journeys). Spawns `RegressionDetective` to map each bug fix to a test that should have caught it (if no test exists, propose one) and `TestRunner` to validate the curated suite executes. Produces regression-suite covering golden-path tests + recent-bug-fix tests + execution health.

## When to use

- TQ full pass regression_suite_curated checkpoint
- Single action `/li:tq single --action regression-suite`
- Post-incident: ensure regression test added
- Quarterly suite curation (prune stale + add recent)

## When NOT to use

- Single regression test (add inline)
- Full test suite re-organization (use test-pyramid-review)

## Workflow

### Step 1 — Read context

```bash
# Recent bug-fix commits (last 90 days)
recent_fixes=$(git log --since='90 days ago' --grep='^fix\|bug\|regression' --format='%H|%s' 2>/dev/null | head -50)

# Golden paths from observability or operator declaration
golden_paths=$(find .claude/runtime/state -name "critical-journeys*.md" -o -name "golden-paths*.md" 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn RegressionDetective for fix-to-test mapping

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Map recent bug fixes to regression tests + flag uncovered fixes
context_pointers:
  - recent bug-fix commits: $recent_fixes
  - existing test files
constraints:
  - per fix: does a test exist that would have caught it before merge?
  - flag uncovered fixes for backfill
  - distinguish: caught-by-existing | needs-new-test | impossible-to-test
acceptance:
  - per-fix verdict + backfill recommendation for uncovered
EOF

/li:brief-forge subagent_spawn tq-regression-suite RegressionDetective brief "$brief_file"
```

### Step 3 — Spawn TestRunner for golden-path execution

```bash
golden_brief=$(mktemp)
cat > "$golden_brief" <<EOF
task: Curate + execute golden-path test suite
context_pointers:
  - $golden_paths
  - .claude/runtime/state/tq/fix-to-test-mapping.md
constraints:
  - per golden path: at least one happy-path test + one edge-case test
  - flag flaky / slow tests for separate quarantine
  - report current pass rate + average duration
acceptance:
  - golden-path test list + execution report
EOF

/li:brief-forge subagent_spawn tq-regression-suite TestRunner brief "$golden_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/tq/regression-suite-$ts.md"
{
  echo "# Regression suite — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Recent fix → test mapping"
  cat .claude/runtime/state/tq/fix-to-test-mapping.md
  echo ""
  echo "## Golden-path tests"
  cat .claude/runtime/state/tq/golden-path-suite.md
  echo ""
  echo "## Execution health"
  cat .claude/runtime/state/tq/execution-report.md
} > "$out"

printf '{"ts":"%s","kind":"tq_regression_suite","fixes_mapped":%d,"uncovered_fixes":%d,"golden_paths":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$fix_count" "$uncovered_count" "$golden_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — suite curated, 0 uncovered fixes, golden paths pass
- **DONE_WITH_CONCERNS** — 1-3 uncovered fixes with backfill plan
- **BLOCKED** — golden-path test failures (regression-suite is broken; fix before curating)

## Integration

**Reads:** git log for recent fixes, golden paths, existing tests
**Writes:** `.claude/runtime/state/tq/regression-suite-<ts>.md`, audit JSONL
**Dispatches to:** RegressionDetective (fix mapping), TestRunner (golden-path execution)

## Anti-patterns

- **Adding every bug fix to regression** — curate to actually-recurring + critical
- **No golden-path tests** — golden paths are the smoke detector; without them, broad failure goes unseen
- **Regression suite without execution health** — un-executed regression is no regression
- **Curating tests in this skill** — agents produce, this skill orchestrates (L-001)
