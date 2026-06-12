---
name: tq-test-pyramid-review
layer: foundation
description: TQ sub-skill — unit/integration/e2e ratio audit + test-distribution health. Dispatches to Architect + TestRunner.
color: green
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-TEST-PYRAMID-REVIEW — the workflow that audits the test-pyramid health.

## What this skill does

Enumerates tests across the repo by kind (unit / integration / e2e / contract / perf). Spawns `TestRunner` to count + measure execution profile per kind and `Architect` to assess the distribution against the test-pyramid principle (more unit, fewer e2e). Produces test-pyramid report with ratio, execution-time distribution, recommendations for rebalancing.

## When to use

- TQ full pass (any time, informs all other checkpoints)
- Single action `/li:tq single --action test-pyramid-review`
- After noticing slow CI (often inverted pyramid)
- Pre-release confidence check

## When NOT to use

- Single test classification (write inline)
- Routine CI tuning (use CI tool)

## Workflow

### Step 1 — Spawn TestRunner for test enumeration + execution profile

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate tests by kind + measure execution profile
context_pointers:
  - test directories (per language convention)
constraints:
  - classify: unit | integration | e2e | contract | perf
  - per kind: count, total execution time, average execution time, flake rate
  - total CI time per kind
acceptance:
  - structured per-kind report
EOF

/li:brief-forge subagent_spawn tq-test-pyramid-review TestRunner brief "$brief_file"
```

### Step 2 — Spawn Architect for distribution assessment

```bash
arch_brief=$(mktemp)
cat > "$arch_brief" <<EOF
task: Assess test distribution against test-pyramid principle
context_pointers:
  - .claude/runtime/state/tq/test-enumeration.md
constraints:
  - ideal pyramid: many unit, fewer integration, fewest e2e
  - flag inverted pyramid (more e2e than unit)
  - flag missing layer (no integration tests, etc.)
  - recommend rebalancing: which kind to add, which to convert
acceptance:
  - distribution verdict + rebalancing recommendations
EOF

/li:brief-forge subagent_spawn tq-test-pyramid-review Architect brief "$arch_brief"
```

### Step 3 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/tq/test-pyramid-$ts.md"
{
  echo "# Test pyramid — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-kind enumeration"
  cat .claude/runtime/state/tq/test-enumeration.md
  echo ""
  echo "## Distribution assessment"
  cat .claude/runtime/state/tq/distribution-assessment.md
} > "$out"

printf '{"ts":"%s","kind":"tq_test_pyramid","unit":%d,"integration":%d,"e2e":%d,"contract":%d,"perf":%d,"verdict":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$unit_count" "$integration_count" "$e2e_count" "$contract_count" "$perf_count" "$verdict" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — pyramid healthy
- **DONE_WITH_CONCERNS** — inverted or missing layer; rebalancing recommended
- **BLOCKED** — TestRunner couldn't enumerate (unfamiliar test framework)

## Integration

**Reads:** test directories, CI execution data
**Writes:** `.claude/runtime/state/tq/test-pyramid-<ts>.md`, audit JSONL
**Dispatches to:** TestRunner (enumeration), Architect (distribution assessment)

## Anti-patterns

- **Inverted pyramid (more e2e than unit)** — slow CI, brittle, hard to debug
- **No integration tests** — unit gaps appear at boundaries
- **Single distribution number** — per-kind matters more than aggregate
- **Curating ideal ratios** — Architect reasons from repo state (L-001)
