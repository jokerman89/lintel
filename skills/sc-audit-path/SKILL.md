---
name: sc-audit-path
layer: foundation
description: SC sub-skill — audit log design with retention + integrity. Dispatches to SecurityAuditor + Architect agents.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are SC-AUDIT-PATH — the workflow that produces an audit log design.

## What this skill does

Reads required-events list (from compliance frameworks + threat model). Spawns `SecurityAuditor` to specify event schema + integrity controls (append-only, tamper-evident, signing) and `Architect` to map the audit pipeline (emission point, transport, durable sink, retention storage). Produces audit-path document.

## When to use

- SC full pass audit_path_verified checkpoint
- Single action `/li:sc single --action audit-path`
- New regulated feature requires evidentiary audit
- Compliance audit prep (audit log is the auditor's primary artifact)

## When NOT to use

- Operational/observability logs (use `/li:dh` v4.4 — those are not audit logs)
- Single audit event spec (write inline; module is for the full path)

## Workflow

### Step 1 — Read retention + required events

```bash
retention="${retention:-${audit_retention:-2555}}"   # default 7 years

# Required events: aggregate from compliance frameworks + threat model
required_events=$(aggregate_required_events)
```

### Step 2 — Spawn SecurityAuditor for event schema + integrity

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Specify audit event schema + integrity controls
context_pointers:
  - required events: $required_events
  - .claude/runtime/state/sc/threat-model-*.md (latest, for tampering threats)
constraints:
  - per event: timestamp (UTC, monotonic), actor, action, target, outcome, context-id
  - integrity: append-only sink + tamper-evident (hash chain or signed)
  - PII handling per event (minimize, hash, or exclude)
acceptance:
  - event schema + per-event capture mechanism + integrity strategy
EOF

/li:brief-forge subagent_spawn sc-audit-path SecurityAuditor brief "$brief_file"
```

### Step 3 — Spawn Architect for pipeline + retention

```bash
pipeline_brief=$(mktemp)
cat > "$pipeline_brief" <<EOF
task: Map audit pipeline (emission → transport → sink → retention)
context_pointers:
  - .claude/runtime/state/sc/audit-event-schema.md
constraints:
  - emission point: where in code each event is written
  - transport: durable (not best-effort) — queue, write-ahead-log, or sync write
  - sink: append-only or WORM (write-once-read-many)
  - retention: ${retention} days; cold-tier transition strategy
  - access control: who reads, how
acceptance:
  - per-event: emission point → transport → sink path
  - retention policy + cold-tier transitions
  - access-control matrix
EOF

/li:brief-forge subagent_spawn sc-audit-path Architect brief "$pipeline_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/sc/audit-path-$ts.md"
{
  echo "# Audit path — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Retention: ${retention} days"
  echo ""
  echo "## Event schema + integrity"
  cat .claude/runtime/state/sc/audit-event-schema.md
  echo ""
  echo "## Pipeline"
  cat .claude/runtime/state/sc/audit-pipeline.md
} > "$out"

printf '{"ts":"%s","kind":"sc_audit_path","retention_days":%d,"events":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$retention" "$event_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — audit path emitted with integrity strategy + retention
- **DONE_WITH_CONCERNS** — emitted but 1-2 events lack emission point
- **BLOCKED** — SecurityAuditor couldn't infer integrity model

## Integration

**Reads:** required-events from compliance + threat model, retention pref
**Writes:** `.claude/runtime/state/sc/audit-path-<ts>.md`, audit JSONL
**Dispatches to:** SecurityAuditor (event schema + integrity), Architect (pipeline + retention)

## Anti-patterns

- **Best-effort audit transport** — durable transport is non-negotiable for audit
- **PII in audit events without minimization** — hash or exclude; raw PII in audit = compliance violation
- **Single retention for all event kinds** — some events need longer retention than others
- **Skipping access-control matrix** — read access to audit log is itself an audit event
