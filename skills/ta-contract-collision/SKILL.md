---
name: ta-contract-collision
layer: foundation
description: TA sub-skill — change-impact analysis across consumers of an interface. Dispatches to APIDesigner + Architect.
color: amber
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are TA-CONTRACT-COLLISION — the workflow that surfaces consumer impact of an interface change.

## What this skill does

Given an interface file path + proposed change, scans the repo (and optionally external configured registries) for consumers. Spawns APIDesigner to assess each consumer's breakage risk. Spawns Architect to propose a migration path. Produces a contract-collision report.

## When to use

- Before merging an interface change with declared consumers
- Operator: `/li:ta single --action contract-collision --interface <path> --change <description>`
- Triggered by `contract-collision-warn` hook (warn-only at pre-edit)
- TA full pass when contract_locked checkpoint detects consumer count > 0

## When NOT to use

- Internal-only refactor (no consumers)
- Pure additive change (no breaking risk)

## Workflow

### Step 1 — Read interface + proposed change

```bash
interface_file="${1:?usage: --interface <path>}"
change_description="${2:?usage: --change <text>}"

[ -f "$interface_file" ] || { echo "ERROR: $interface_file not found"; exit 1; }
```

### Step 2 — Discover consumers

```bash
# Heuristic: grep for imports of the interface file's exported symbols
symbols=$(extract_exported_symbols "$interface_file")

declare -a consumers
for sym in $symbols; do
  while IFS= read -r f; do
    consumers+=("$f")
  done < <(grep -rln "$sym" --include='*' "$REPO_ROOT" 2>/dev/null | grep -v "$interface_file" | sort -u)
done

consumer_count=$(printf '%s\n' "${consumers[@]}" | sort -u | wc -l)
```

External consumers (configured via `pack.yaml.tech_architecture.external_consumer_registries`) are queried optionally — pack-author opt-in.

### Step 3 — Spawn APIDesigner for breakage assessment

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Assess breakage risk per consumer for change: $change_description
context_pointers:
  - $interface_file
  - .claude/runtime/state/ta/consumers-list.txt
constraints:
  - per-consumer: backward-compat OR breaking
  - if breaking: specify the breaking aspect
acceptance:
  - structured per-consumer assessment
EOF

/li:brief-forge subagent_spawn ta-contract-collision APIDesigner brief "$brief_file"
```

### Step 4 — Spawn Architect for migration path (if any breaking)

```bash
breaking_count=$(jq -r '.consumers[] | select(.breaking == true) | .name' .claude/runtime/state/ta/breakage-assessment.json | wc -l)

if [ "$breaking_count" -gt 0 ]; then
  migration_brief=$(mktemp)
  cat > "$migration_brief" <<EOF
task: Propose migration path for $breaking_count breaking consumer(s)
context_pointers:
  - .claude/runtime/state/ta/breakage-assessment.json
constraints:
  - deprecation window: read from pack.tech_architecture.deprecation_window_days (default 90)
  - prefer additive new-version path over in-place breaking
acceptance:
  - migration plan with phases + timeline + rollback
EOF
  /li:brief-forge subagent_spawn ta-contract-collision Architect brief "$migration_brief"
fi
```

### Step 5 — Raise-help trigger (≥3 breaking consumers per TA module raise_help)

```bash
if [ "$breaking_count" -ge 3 ]; then
  echo "RAISE_HELP: contract change breaks $breaking_count consumers"
  # SENSE / TA module surface AskUserQuestion: operator decides migration path
fi
```

### Step 6 — Emit + audit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/ta/contract-collision-$ts.md"
{
  echo "# Contract collision — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Interface"
  echo "$interface_file"
  echo ""
  echo "## Proposed change"
  echo "$change_description"
  echo ""
  echo "## Consumers"
  echo "Total: $consumer_count"
  echo "Breaking: $breaking_count"
  echo ""
  cat .claude/runtime/state/ta/breakage-assessment.md
  [ -f .claude/runtime/state/ta/migration-plan.md ] && cat .claude/runtime/state/ta/migration-plan.md
} > "$out"

printf '{"ts":"%s","kind":"ta_contract_collision","interface":"%s","consumers":%d,"breaking":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$interface_file" "$consumer_count" "$breaking_count" \
  "$([ "$breaking_count" -ge 3 ] && echo true || echo false)" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/ta-decisions.jsonl"
```

## Status protocol

- **DONE** — no breaking consumers; safe to proceed
- **DONE_WITH_CONCERNS** — 1-2 breaking consumers with migration plan
- **BLOCKED** — raise_help triggered (≥3 breaking consumers), awaiting operator decision

## Integration

**Reads:** interface file, repo source for grep, pack.yaml external_consumer_registries
**Writes:** `.claude/runtime/state/ta/contract-collision-<ts>.md`, audit JSONL
**Dispatches to:** APIDesigner (assessment), Architect (migration)
**Hook integration:** `contract-collision-warn` hook fires pre-edit on interface files with declared consumers

## Anti-patterns

- **Skipping external consumer registries** — pack-author opt-in; honor pack policy
- **Treating breaking as terminal** — surface, propose migration, operator decides
- **Hardcoding deprecation window** — read from pack policy
