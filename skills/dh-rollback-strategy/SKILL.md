---
name: dh-rollback-strategy
layer: foundation
description: DH sub-skill — rollback mechanics + blast-radius limiting + hot-swap path. Dispatches to ReleaseEngineer + SecurityAuditor agents.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-ROLLBACK-STRATEGY — the workflow that produces a rollback playbook.

## What this skill does

Reads deployment plan (from `dh-deployment-plan` if present) + threat surface (from SC if present). Spawns `ReleaseEngineer` for rollback mechanics (revert vs rollback vs hot-swap) and `SecurityAuditor` to assess blast-radius + revoke paths for security-sensitive changes. Produces rollback-strategy with per-failure-mode rollback path, blast-radius estimate, estimated time-to-rollback.

## When to use

- DH full pass deployment_plan_locked checkpoint (deployment + rollback must lock together)
- Single action `/li:dh single --action rollback-strategy`
- Pre-production-deployment rollback rehearsal
- After near-miss incident requires rollback path improvement

## When NOT to use

- Single-PR revert (use git revert)
- Routine deploy (existing pipeline)

## Workflow

### Step 1 — Read context

```bash
deployment_pattern="${deployment_pattern:-blue-green}"
deployment_plan=$(find .claude/runtime/state/dh -name "deployment-plan-*.md" -mtime -7 2>/dev/null | sort | tail -1)
threat_model=$(find .claude/runtime/state/sc -name "threat-model-*.md" -mtime -30 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn ReleaseEngineer for rollback mechanics

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Specify rollback mechanics for ${deployment_pattern} deployment
context_pointers:
  - $deployment_plan
constraints:
  - per failure mode: revert | rollback | hot-swap | feature-flag-off
  - estimated time-to-rollback per option
  - data implications (schema changes, in-flight transactions)
acceptance:
  - per-failure-mode rollback path + time estimate
EOF

/li:brief-forge subagent_spawn dh-rollback-strategy ReleaseEngineer brief "$brief_file"
```

### Step 3 — Spawn SecurityAuditor for blast-radius

```bash
blast_brief=$(mktemp)
cat > "$blast_brief" <<EOF
task: Assess blast-radius + revoke paths for security-sensitive changes
context_pointers:
  - $deployment_plan
  - $threat_model
constraints:
  - per security-sensitive change (auth, secrets, access policy): revoke path
  - blast-radius: how many users, how much data, how much downtime if rollback fails
acceptance:
  - per-change blast-radius + revoke path
EOF

/li:brief-forge subagent_spawn dh-rollback-strategy SecurityAuditor brief "$blast_brief"
```

### Step 4 — Irreversibility detection

```bash
# If any failure mode has no rollback path → irreversibility flagged
irreversible_count=$(jq -r '.failure_modes[] | select(.rollback_path == "none" or .rollback_path == "irreversible") | .name' .claude/runtime/state/dh/rollback-mechanics.json 2>/dev/null | wc -l)

if [ "$irreversible_count" -gt 0 ]; then
  echo "RAISE_HELP: $irreversible_count failure mode(s) with irreversible rollback path"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/dh/rollback-strategy-$ts.md"
{
  echo "# Rollback strategy — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Pattern: $deployment_pattern"
  echo ""
  echo "## Rollback mechanics"
  cat .claude/runtime/state/dh/rollback-mechanics.md
  echo ""
  echo "## Blast-radius + revoke paths"
  cat .claude/runtime/state/dh/blast-radius.md
} > "$out"

printf '{"ts":"%s","kind":"dh_rollback_strategy","pattern":"%s","irreversible":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$deployment_pattern" "$irreversible_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> ".claude/runtime/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — strategy emitted with rollback path per failure mode
- **DONE_WITH_CONCERNS** — emitted with 1-2 long time-to-rollback paths
- **BLOCKED** — irreversible rollback flagged

## Integration

**Reads:** DH deployment plan, SC threat model
**Writes:** `.claude/runtime/state/dh/rollback-strategy-<ts>.md`, audit JSONL
**Dispatches to:** ReleaseEngineer (mechanics), SecurityAuditor (blast-radius)
**Hook integration:** `dh-deploy-without-rollback-warn` hook fires pre-commit on deploy/IaC w/o rollback declaration

## Anti-patterns

- **Rollback as afterthought** — locked together with deployment plan
- **Single rollback path for all failure modes** — different modes need different paths
- **Skipping blast-radius for security changes** — security rollback is harder than feature rollback
- **Curating rollback patterns** — agents produce, this skill orchestrates (L-001)
