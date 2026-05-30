---
name: ta-dependency-graph
layer: foundation
description: TA sub-skill — module dependency map, circular-detection, layering audit. Dispatches to Architect + Explorer agents. Per L-001 a workflow-and-dispatch contract.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-DEPENDENCY-GRAPH — the workflow that maps module dependencies and surfaces structural issues.

## What this skill does

Reads the repo's module structure (per detected language: imports, requires, includes, mod files). Spawns `Explorer` for the enumeration + `Architect` for the layering analysis. Produces dependency graph (DOT format + summary), circular-dependency report, layering audit. Writes to `.lintel/state/ta/dependency-graph-<ts>.md`.

## When to use

- TA full pass, discovery_complete checkpoint
- Single action: `/li:ta single --action dependency-graph`
- After a dependency PR to verify no new cycles introduced

## When NOT to use

- Build-time dependency analysis (use language tooling: `cargo tree`, `mvn dependency:tree`, etc.)
- Runtime dependency tracing (use observability stack)

## Workflow

### Step 1 — Detect language + dependency declaration style

```bash
# Heuristic: count common manifest files
[ -f "package.json" ] && language="node"
[ -f "go.mod" ] && language="go"
[ -f "Cargo.toml" ] && language="rust"
[ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && language="python"
[ -f "pom.xml" ] || [ -f "build.gradle" ] && language="jvm"
[ -f "*.csproj" ] || ls *.sln 2>/dev/null && language="dotnet"
```

### Step 2 — Spawn Explorer for module enumeration

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate all modules in this $language repo, capture per-module dependencies
constraints:
  - exclude vendored / third-party trees
  - include only first-party modules
acceptance:
  - structured list of (module, [dependencies]) tuples
EOF

/li:brief-forge subagent_spawn ta-dependency-graph Explorer brief "$brief_file"
```

### Step 3 — Spawn Architect for layering analysis

```bash
analysis_brief=$(mktemp)
cat > "$analysis_brief" <<EOF
task: Analyze module dependency graph for layering violations + cycles
context_pointers:
  - .lintel/state/ta/explorer-output.json
constraints:
  - flag any cyclic dependency
  - flag any cross-layer reverse-dependency (e.g. lower-layer importing higher-layer)
acceptance:
  - structured report with cycles + violations + suggested refactors
EOF

/li:brief-forge subagent_spawn ta-dependency-graph Architect brief "$analysis_brief"
```

### Step 4 — Emit DOT graph + summary

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/ta/dependency-graph-$ts.md"
{
  echo "# Dependency graph — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Summary"
  echo "- Modules: $module_count"
  echo "- Edges: $edge_count"
  echo "- Cycles: $cycle_count"
  echo "- Layering violations: $violation_count"
  echo ""
  echo "## DOT graph"
  echo '```dot'
  cat .lintel/state/ta/graph.dot
  echo '```'
  echo ""
  echo "## Cycles + violations"
  cat .lintel/state/ta/architect-output.md
} > "$out"
```

### Step 5 — Audit

```bash
printf '{"ts":"%s","kind":"ta_dependency_graph","language":"%s","modules":%d,"cycles":%d,"violations":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$language" "$module_count" "$cycle_count" "$violation_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — graph emitted, 0 cycles + 0 violations
- **DONE_WITH_CONCERNS** — graph emitted with cycles or violations surfaced
- **BLOCKED** — Explorer couldn't enumerate (unsupported language, missing manifests)

## Integration

**Reads:** repo manifests (package.json / go.mod / etc.)
**Writes:** `.lintel/state/ta/dependency-graph-<ts>.md`, `.lintel/state/ta/graph.dot`, audit JSONL
**Dispatches to:** Explorer (enumeration), Architect (analysis)

## Anti-patterns

- **Hardcoding language detection** — use heuristic + manifest presence
- **Including vendored deps** — first-party only; third-party surfaces in separate audit
- **Curating layering rules** — Architect infers from the graph (L-001)
