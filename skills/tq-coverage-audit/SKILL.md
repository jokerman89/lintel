---
name: tq-coverage-audit
layer: foundation
description: TQ sub-skill — critical-path coverage + branch coverage + mutation testing report. Dispatches to TestRunner + Architect agents.
color: green
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-COVERAGE-AUDIT — the workflow that produces a coverage audit.

## What this skill does

Reads critical paths (from TA boundary-review if present, else operator-declared). Spawns `TestRunner` to run coverage tools per language and `Architect` to map gaps against critical paths. Produces coverage-audit with per-component line + branch coverage, critical-path verdict, and mutation-testing report (when supported).

## When to use

- TQ full pass coverage_targets_met checkpoint
- Single action `/li:tq single --action coverage-audit`
- Pre-release coverage gate
- After critical-path discovery to verify coverage

## When NOT to use

- Single-file coverage check (use language tool directly)
- Quick "did my new code get covered" check (use CI report)

## Workflow

### Step 1 — Read preferences + critical paths

```bash
target="${target:-${coverage_target:-80}}"
critical_path="${critical_path:-${critical_path_coverage:-100}}"
boundary_review=$(find .claude/runtime/state/ta -name "boundary-review-*.md" -mtime -30 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn TestRunner per language

```bash
language=$(detect_language)  # shared helper
case "$language" in
  go)     coverage_tool="go test -coverprofile" ;;
  python) coverage_tool="pytest --cov" ;;
  node)   coverage_tool="jest --coverage" ;;
  rust)   coverage_tool="cargo tarpaulin" ;;
  *)      coverage_tool="lcov / language-specific" ;;
esac

brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Run coverage tools for ${language}; report per-component line + branch + mutation
context_pointers:
  - $boundary_review
constraints:
  - per component: line %, branch %, mutation score (when tool supports)
  - flag critical paths separately from regular paths
acceptance:
  - structured report per component + per critical path
EOF

/li:brief-forge subagent_spawn tq-coverage-audit TestRunner brief "$brief_file"
```

### Step 3 — Spawn Architect for gap analysis

```bash
gap_brief=$(mktemp)
cat > "$gap_brief" <<EOF
task: Map coverage gaps against critical paths + recommend backfill priority
context_pointers:
  - .claude/runtime/state/tq/coverage-raw.md
  - $boundary_review
constraints:
  - per gap: line vs branch vs mutation; critical-path or regular; impact estimate
  - rank by criticality + ease of test
acceptance:
  - per-gap recommendation with priority
EOF

/li:brief-forge subagent_spawn tq-coverage-audit Architect brief "$gap_brief"
```

### Step 4 — Raise-help on critical-path below threshold

```bash
critical_below_threshold=$(jq -r '.critical_paths[] | select(.coverage_pct < '"$critical_path"') | .name' .claude/runtime/state/tq/coverage-summary.json 2>/dev/null | wc -l)
if [ "$critical_below_threshold" -gt 0 ]; then
  echo "RAISE_HELP: $critical_below_threshold critical path(s) below threshold ${critical_path}%"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/tq/coverage-audit-$ts.md"
{
  echo "# Coverage audit — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Targets: ${target}% overall, ${critical_path}% critical"
  echo ""
  echo "## Per-component"
  cat .claude/runtime/state/tq/coverage-raw.md
  echo ""
  echo "## Gap analysis + backfill priority"
  cat .claude/runtime/state/tq/coverage-gaps.md
} > "$out"

printf '{"ts":"%s","kind":"tq_coverage_audit","language":"%s","target":%d,"critical_below_threshold":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$language" "$target" "$critical_below_threshold" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — coverage at target; all critical paths ≥ threshold
- **DONE_WITH_CONCERNS** — overall at target, 1-2 critical paths just below threshold
- **BLOCKED** — raise-help triggered (critical paths below)

## Integration

**Reads:** profile preferences, TA boundary-review (for critical paths)
**Writes:** `.claude/runtime/state/tq/coverage-audit-<ts>.md`, audit JSONL
**Dispatches to:** TestRunner (per language), Architect (gap analysis)
**Hook integration:** `tq-coverage-drop-warn` hook fires pre-commit on coverage drops

## Anti-patterns

- **Single coverage number** — critical-path coverage is the metric that matters
- **Skipping mutation testing when tool supports** — line coverage with weak assertions = false-confidence
- **Hardcoding target** — read profile
