---
name: ta-boundary-review
layer: foundation
description: TA sub-skill — bounded-context drift detection, leaking-abstraction flags. Dispatches to BackendArchitect + Architect.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-BOUNDARY-REVIEW — the workflow that surfaces bounded-context drift.

## What this skill does

Reads module structure (per `/li:ta-dependency-graph` output if present, else fresh enumeration). Identifies bounded contexts (modules + their data + their language). Surfaces leaks: shared mutable state across contexts, shared internal types exposed across boundaries, language drift (one context's term used in another with different meaning). Spawns BackendArchitect for the boundary analysis + Architect for refactor recommendations.

## When to use

- TA full pass, decision_documented checkpoint
- Single action: `/li:ta single --action boundary-review`
- Before merging a feature that touches multiple bounded contexts
- After a long iteration to spot accumulated drift

## When NOT to use

- Pure single-context refactor (no boundary concern)
- API design — use `/li:ta-api-design`

## Workflow

### Step 1 — Reuse or generate dependency graph

```bash
graph_file=$(find .lintel/state/ta -name "dependency-graph-*.md" -mtime -1 2>/dev/null | sort | tail -1)
if [ -z "$graph_file" ]; then
  /li:ta-dependency-graph
  graph_file=$(find .lintel/state/ta -name "dependency-graph-*.md" 2>/dev/null | sort | tail -1)
fi
```

### Step 2 — Identify bounded contexts

```bash
# Heuristic: top-level directories under src/ (or equivalent) often map to contexts
contexts=$(find src -maxdepth 1 -type d 2>/dev/null | xargs -n1 basename | grep -vE '^\.')
# Augment with module manifests for finer granularity
```

### Step 3 — Spawn BackendArchitect for boundary analysis

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Analyze bounded contexts for drift + leaking abstractions
context_pointers:
  - $graph_file
  - .lintel/state/ta/contexts-list.txt
constraints:
  - flag shared mutable state across contexts
  - flag internal types exposed across context boundary
  - flag language drift (term used inconsistently across contexts)
acceptance:
  - structured report per context: clean/concerns/leaks
EOF

/li:brief-forge subagent_spawn ta-boundary-review BackendArchitect brief "$brief_file"
```

### Step 4 — Refactor recommendations (if leaks found)

```bash
if [ "$leak_count" -gt 0 ]; then
  refactor_brief=$(mktemp)
  cat > "$refactor_brief" <<EOF
task: Recommend boundary-hardening refactors for $leak_count leak(s)
context_pointers:
  - .lintel/state/ta/boundary-analysis.md
constraints:
  - propose specific refactor per leak (extract interface / introduce adapter / move type)
acceptance:
  - per-leak recommendation with code-level pointers
EOF
  /li:brief-forge subagent_spawn ta-boundary-review Architect brief "$refactor_brief"
fi
```

### Step 5 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/ta/boundary-review-$ts.md"
{
  echo "# Boundary review — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Contexts"
  echo "$contexts"
  echo ""
  echo "## Findings"
  cat .lintel/state/ta/boundary-analysis.md
  [ -f .lintel/state/ta/architect-refactor.md ] && cat .lintel/state/ta/architect-refactor.md
} > "$out"

verdict="GREEN"
[ "$leak_count" -gt 0 ] && verdict="YELLOW"
[ "$leak_count" -gt 5 ] && verdict="RED"

printf '{"ts":"%s","kind":"ta_boundary_review","contexts":%d,"leaks":%d,"verdict":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$context_count" "$leak_count" "$verdict" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — 0 leaks, verdict GREEN
- **DONE_WITH_CONCERNS** — verdict YELLOW or RED
- **BLOCKED** — context detection failed

## Integration

**Reads:** `.lintel/state/ta/dependency-graph-*.md`, repo structure
**Writes:** `.lintel/state/ta/boundary-review-<ts>.md`, audit JSONL
**Dispatches to:** BackendArchitect (analysis), Architect (refactor)

## Anti-patterns

- **Skipping the dependency graph reuse** — generation is expensive; reuse recent if available
- **Curating context lists** — heuristic + manifests; operator overrides via flag
- **Treating leak count as failure** — leaks surface; operator decides accept-with-concern or refactor
