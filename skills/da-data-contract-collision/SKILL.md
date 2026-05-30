---
name: da-data-contract-collision
layer: foundation
description: DA sub-skill — schema change impact analysis across consumers. Dispatches to DatabaseDesigner + Architect. Raises help on ≥3 breaking consumers.
color: blue
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DA-DATA-CONTRACT-COLLISION — the workflow that surfaces consumer impact of schema changes.

## What this skill does

Given a proposed schema delta + a target schema. Scans the repo (and optionally a configured registry) for consumers — services reading the schema, analytics pipelines depending on column shapes, exported reports referencing columns. Spawns `DatabaseDesigner` for breakage assessment + `Architect` for migration-path proposal. Raises help when ≥3 consumers break.

## When to use

- Before merging schema change with declared consumers
- Operator: `/li:da single --action data-contract-collision --delta <file>`
- Triggered by `da-schema-drift-warn` hook (warn-only at pre-edit)
- DA full pass schema_locked checkpoint when consumer count > 0

## When NOT to use

- Internal-only schema refactor (no external consumers)
- Pure additive change (new nullable column) — backward-compat by definition

## Workflow

### Step 1 — Read delta

```bash
delta_file="${1:?usage: --delta <path>}"
[ -f "$delta_file" ] || { echo "ERROR: $delta_file not found"; exit 1; }

# Extract affected tables + columns
affected_tables=$(parse_delta_tables "$delta_file")
affected_columns=$(parse_delta_columns "$delta_file")
```

### Step 2 — Discover consumers

```bash
# Heuristic: grep for table + column names across repo
declare -a consumers
for tbl in $affected_tables; do
  while IFS= read -r f; do
    consumers+=("$f")
  done < <(grep -rln "$tbl" --include='*' "$REPO_ROOT" 2>/dev/null | grep -v "$delta_file" | sort -u)
done

# Pack-author can declare external registries (analytics warehouse, BI tools)
source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
external_registries=$(resolve_pack_field data_architecture.external_consumer_registries 2>/dev/null || true)

consumer_count=$(printf '%s\n' "${consumers[@]}" | sort -u | wc -l)
```

### Step 3 — Spawn DatabaseDesigner for breakage assessment

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Assess breakage risk per consumer for schema delta
context_pointers:
  - $delta_file
  - .lintel/state/da/consumers-list.txt
constraints:
  - per-consumer: backward-compat (additive / nullable) OR breaking (column drop / type narrowing / null→not-null)
  - flag analytics pipelines separately (silent breakage risk in dashboards)
acceptance:
  - structured per-consumer assessment
EOF

/li:brief-forge subagent_spawn da-data-contract-collision DatabaseDesigner brief "$brief_file"
```

### Step 4 — Spawn Architect for migration path (if any breaking)

```bash
breaking_count=$(jq -r '.consumers[] | select(.breaking == true) | .name' .lintel/state/da/breakage-assessment.json | wc -l)

if [ "$breaking_count" -gt 0 ]; then
  migration_brief=$(mktemp)
  cat > "$migration_brief" <<EOF
task: Propose migration path for $breaking_count breaking consumer(s)
context_pointers:
  - .lintel/state/da/breakage-assessment.json
constraints:
  - prefer expand-and-contract pattern (add new column → backfill → switch reads → drop old)
  - declare grace window per consumer
acceptance:
  - migration plan with phases + grace windows + rollback
EOF
  /li:brief-forge subagent_spawn da-data-contract-collision Architect brief "$migration_brief"
fi
```

### Step 5 — Raise-help trigger (≥3 breaking consumers per DA module raise_help)

```bash
if [ "$breaking_count" -ge 3 ]; then
  echo "RAISE_HELP: schema change breaks $breaking_count consumers"
  # DA module surfaces AskUserQuestion
fi
```

### Step 6 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/da/data-contract-collision-$ts.md"
{
  echo "# Data contract collision — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Affected tables/columns"
  echo "$affected_tables"
  echo "$affected_columns"
  echo ""
  echo "## Consumers"
  echo "Total: $consumer_count"
  echo "Breaking: $breaking_count"
  echo ""
  cat .lintel/state/da/breakage-assessment.md
  [ -f .lintel/state/da/migration-plan.md ] && cat .lintel/state/da/migration-plan.md
} > "$out"

printf '{"ts":"%s","kind":"da_data_contract_collision","delta_file":"%s","consumers":%d,"breaking":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$delta_file" "$consumer_count" "$breaking_count" \
  "$([ "$breaking_count" -ge 3 ] && echo true || echo false)" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/da-decisions.jsonl"
```

## Status protocol

- **DONE** — no breaking consumers; safe to proceed
- **DONE_WITH_CONCERNS** — 1-2 breaking with migration plan
- **BLOCKED** — raise_help triggered (≥3 breaking)

## Integration

**Reads:** delta file, repo source for grep, pack external_consumer_registries
**Writes:** `.lintel/state/da/data-contract-collision-<ts>.md`, audit JSONL
**Dispatches to:** DatabaseDesigner (assessment), Architect (migration)
**Hook integration:** `da-schema-drift-warn` hook fires pre-edit on schema-ADR-claimed files

## Anti-patterns

- **Treating analytics breakage as low priority** — silent dashboard breakage costs more than service-level
- **Hardcoding grace window** — read from pack `data_architecture.deprecation_window_days`
- **Skipping external registries** — pack-author opt-in; honor pack policy
