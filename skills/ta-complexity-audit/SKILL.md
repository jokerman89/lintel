---
name: ta-complexity-audit
layer: foundation
description: TA sub-skill — per-component cyclomatic + cognitive complexity scoring. Reads pack/profile thresholds. Dispatches to CodeReviewer + Architect agents.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-COMPLEXITY-AUDIT — the workflow that scores complexity against budget.

## What this skill does

Scans repo for complexity using language-appropriate tools (`gocyclo`, `radon`, `lizard`, `eslintcc`). Aggregates per-component scores. Compares against thresholds from profile (`engineering.tech_architecture.complexity_budget_*`). Spawns Architect for refactor recommendations on over-budget components.

## When to use

- TA full pass, complexity_within_budget checkpoint
- Single action: `/li:ta single --action complexity-audit`
- Pre-PR check on a feature branch
- After a refactor to verify budget improvement

## When NOT to use

- Single-function complexity check (operator can run their language's tool directly)
- Runtime complexity profiling (use perf tools, see `/li:tq` v4.5)

## Workflow

### Step 1 — Read thresholds

```bash
budget_cyclomatic="${1:-${cyclomatic_budget:-12}}"
budget_cognitive="${2:-${cognitive_budget:-18}}"
```

Args support `--budget-cyclomatic N --budget-cognitive M`. Defaults from profile preferences.

### Step 2 — Detect language + invoke appropriate tool

```bash
language=$(detect_language)  # shared helper, same as ta-dependency-graph
case "$language" in
  go)     gocyclo -over "$budget_cyclomatic" . > .claude/runtime/state/ta/complexity-raw.txt ;;
  python) radon cc -n B -s . > .claude/runtime/state/ta/complexity-raw.txt ;;
  rust)   cargo-complexity > .claude/runtime/state/ta/complexity-raw.txt 2>/dev/null || echo "skip" ;;
  node)   npx eslintcc 'src/**/*.{js,ts}' --rule complexity > .claude/runtime/state/ta/complexity-raw.txt ;;
  *)      lizard . > .claude/runtime/state/ta/complexity-raw.txt ;;
esac
```

If detected tool missing: surface install hint, fall back to `lizard` (multi-language).

### Step 3 — Parse + aggregate

```bash
# Per-component (file or class) cyclomatic max + cognitive avg
parse_complexity_output > .claude/runtime/state/ta/complexity-summary.json

over_cyclo=$(jq -r '.components[] | select(.cyclomatic_max > '"$budget_cyclomatic"') | .name' .claude/runtime/state/ta/complexity-summary.json | wc -l)
over_cognitive=$(jq -r '.components[] | select(.cognitive_avg > '"$budget_cognitive"') | .name' .claude/runtime/state/ta/complexity-summary.json | wc -l)
```

### Step 4 — Spawn Architect for refactor recommendations (if over budget)

```bash
if [ "$over_cyclo" -gt 0 ] || [ "$over_cognitive" -gt 0 ]; then
  brief_file=$(mktemp)
  cat > "$brief_file" <<EOF
task: Recommend refactor approach for $over_cyclo cyclomatic + $over_cognitive cognitive over-budget components
context_pointers:
  - .claude/runtime/state/ta/complexity-summary.json
constraints:
  - prefer extraction over abstraction (Subtraction Bias)
  - identify specific refactor pattern per component
acceptance:
  - structured recommendation per over-budget component
EOF
  /li:brief-forge subagent_spawn ta-complexity-audit Architect brief "$brief_file"
fi
```

### Step 5 — Emit report + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/ta/complexity-audit-$ts.md"
{
  echo "# Complexity audit — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Budgets"
  echo "- Cyclomatic: $budget_cyclomatic"
  echo "- Cognitive: $budget_cognitive"
  echo ""
  echo "## Results"
  echo "- Over cyclomatic budget: $over_cyclo components"
  echo "- Over cognitive budget: $over_cognitive components"
  echo ""
  echo "## Per-component"
  jq -r '.components[] | "- \(.name): cyclomatic=\(.cyclomatic_max) cognitive=\(.cognitive_avg)"' .claude/runtime/state/ta/complexity-summary.json
  [ -f .claude/runtime/state/ta/architect-refactor.md ] && cat .claude/runtime/state/ta/architect-refactor.md
} > "$out"

verdict="GREEN"
[ "$over_cyclo" -gt 0 ] || [ "$over_cognitive" -gt 0 ] && verdict="YELLOW"
[ "$over_cyclo" -gt 5 ] || [ "$over_cognitive" -gt 5 ] && verdict="RED"

printf '{"ts":"%s","kind":"ta_complexity_audit","language":"%s","over_cyclomatic":%d,"over_cognitive":%d,"verdict":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$language" "$over_cyclo" "$over_cognitive" "$verdict" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — audit emitted, 0 components over budget (verdict GREEN)
- **DONE_WITH_CONCERNS** — verdict YELLOW (1-5 over) or RED (>5 over)
- **BLOCKED** — no complexity tool available for detected language

## Integration

**Reads:** profile preferences, language manifest, complexity tool output
**Writes:** `.claude/runtime/state/ta/complexity-audit-<ts>.md`, audit JSONL
**Dispatches to:** Architect (refactor recommendations when over budget)
**Hook integration:** `complexity-budget-warn` hook fires pre-commit using same thresholds

## Anti-patterns

- **Hardcoding thresholds** — read from profile (engineering.tech_architecture.complexity_budget_*)
- **Failing the audit silently** — verdict surfaces; operator decides accept-with-concern or refactor
- **Inventing complexity rules** — use established tools per language (gocyclo, radon, lizard)
