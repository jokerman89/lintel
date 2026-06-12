---
name: ta-api-design
layer: foundation
description: TA sub-skill — REST/GraphQL/gRPC interface design with versioning + breaking-change analysis. Dispatches to APIDesigner agent. Called by /li:ta or standalone via /li:ta single --action api-design.
color: amber
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are TA-API-DESIGN — the workflow that produces an interface specification.

## What this skill does

Reads operator's interface intent + existing API conventions + profile preferences (api_style, versioning). Spawns `APIDesigner` agent to produce the spec. Validates the output against checklist. Writes audit + emits structured spec under `.claude/runtime/state/ta/api-design-<ts>.md`.

Per L-001: this skill is the workflow + dispatch contract. The actual API design content is produced by APIDesigner at invocation, not curated in this skill.

## When to use

- Invoked by `/li:ta full` during decision_documented checkpoint
- Standalone via `/li:ta single --action api-design`
- Direct: `/li:ta-api-design --pref api_style=rest --pref versioning=semver-major-uri`

## When NOT to use

- Pure schema work without interface concern → `/li:da` (v4.2)
- Cross-system contract collision analysis → `/li:ta-contract-collision`
- Quality-attribute spec (latency, throughput) → `/li:ta-quality-attributes`

## Workflow

### Step 1 — Read preferences

```bash
api_style="${api_style:-rest}"           # rest | graphql | grpc | mixed
versioning="${versioning:-semver-major-uri}"  # semver-major-uri | accept-header | none
```

### Step 2 — Spawn APIDesigner agent through Brief Forge

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Design ${api_style} interface for [operator's description]
constraints:
  - versioning: ${versioning}
  - backward-compat: required for v1.x
  - operator-stated requirements: [list]
acceptance:
  - interface spec written to .claude/runtime/state/ta/api-design-<ts>.md
  - breaking-change analysis present if v2.x
  - example request/response per endpoint
EOF

/li:brief-forge subagent_spawn ta-api-design APIDesigner brief "$brief_file"
```

### Step 3 — APIDesigner agent runs

Agent reads brief + existing API conventions + repository state. Produces structured spec.

### Step 4 — Validate against checklist

```
[ ] Each endpoint has method, path, request schema, response schema, error responses
[ ] Versioning strategy applied consistently
[ ] Breaking-change analysis present (if v2.x or higher)
[ ] Authentication/authorization noted
[ ] Rate-limit / quota notes per endpoint
[ ] Example payload(s)
[ ] OpenAPI/Protobuf/SDL artifact if applicable
```

Failing checklist items surface as gaps. Operator decides re-spawn vs accept.

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
audit="$LINTEL_HOME/audit/ta-decisions.jsonl"
printf '{"ts":"%s","kind":"ta_api_design","api_style":"%s","versioning":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$api_style" "$versioning" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$audit"
```

Spec emitted at `.claude/runtime/state/ta/api-design-<ts>.md`.

## Status protocol

- **DONE** — spec written, checklist all-pass
- **DONE_WITH_CONCERNS** — spec written, 1-2 checklist gaps surfaced
- **BLOCKED** — APIDesigner could not produce spec (insufficient context)
- **NEEDS_CONTEXT** — operator's interface intent unclear

## Integration

**Reads:** profile preferences, existing API conventions, Brief Forge gate
**Writes:** `.claude/runtime/state/ta/api-design-<ts>.md`, audit JSONL
**Dispatches to:** `APIDesigner` agent
**Called by:** `skills/ta/SKILL.md`, operator-direct

## Anti-patterns

- **Hardcoding REST when profile says graphql** — read preferences first
- **Curating API patterns in this skill** — that's APIDesigner's job at invocation (L-001)
- **Skipping the breaking-change analysis** — required for v2.x+ per acceptance criteria
