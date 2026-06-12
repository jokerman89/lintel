---
name: sc-incident-runbook
layer: foundation
description: SC sub-skill — response runbook for the new surface. Dispatches to SecurityAuditor + ReleaseEngineer agents.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are SC-INCIDENT-RUNBOOK — the workflow that produces a security-incident response runbook.

## What this skill does

Reads threat model + auth flow + secret inventory + audit path. Spawns `SecurityAuditor` to produce per-threat-class incident response steps (detection signals → containment → eradication → recovery → post-mortem) and `ReleaseEngineer` to specify rollback + hotfix mechanics. Produces a runbook the on-call operator can follow cold.

## When to use

- SC full pass (produced after threat_model_complete + audit_path_verified)
- Single action `/li:sc single --action incident-runbook`
- New production surface introduction
- Post-incident review wants a generalized runbook
- Pre-launch checklist

## When NOT to use

- General SRE runbook for non-security incidents (use SRE-specific tooling)
- Single-incident post-mortem (write inline)

## Workflow

### Step 1 — Read prior SC artifacts

```bash
threat_model=$(find .claude/runtime/state/sc -name "threat-model-*.md" -mtime -7 2>/dev/null | sort | tail -1)
auth_flow=$(find .claude/runtime/state/sc -name "auth-flow-*.md" -mtime -7 2>/dev/null | sort | tail -1)
secret_inv=$(find .claude/runtime/state/sc -name "secret-inventory-*.md" -mtime -7 2>/dev/null | sort | tail -1)
audit_path=$(find .claude/runtime/state/sc -name "audit-path-*.md" -mtime -7 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn SecurityAuditor for per-threat-class response

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Produce per-threat-class incident response steps
context_pointers:
  - $threat_model
  - $auth_flow
  - $secret_inv
  - $audit_path
constraints:
  - per threat class: detection signals (what triggers the runbook), containment steps,
    eradication steps, recovery steps, post-mortem template
  - distinguish on-call action (within minutes) vs operator action (within hours)
  - reference audit-log queries for detection
acceptance:
  - per-threat-class runbook section
EOF

/li:brief-forge subagent_spawn sc-incident-runbook SecurityAuditor brief "$brief_file"
```

### Step 3 — Spawn ReleaseEngineer for rollback + hotfix mechanics

```bash
release_brief=$(mktemp)
cat > "$release_brief" <<EOF
task: Specify rollback + hotfix mechanics referenced by incident runbook
context_pointers:
  - .claude/runtime/state/sc/incident-response.md
  - existing deploy / rollback runbooks
constraints:
  - per-deploy-target: rollback command + estimated rollback time
  - hotfix path: feature-flag toggle, infra-level circuit-break, traffic-cutover
  - communication protocol: who notifies, channels, status-page
acceptance:
  - rollback + hotfix mechanics per deploy target
EOF

/li:brief-forge subagent_spawn sc-incident-runbook ReleaseEngineer brief "$release_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/sc/incident-runbook-$ts.md"
{
  echo "# Incident runbook — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-threat-class response"
  cat .claude/runtime/state/sc/incident-response.md
  echo ""
  echo "## Rollback + hotfix mechanics"
  cat .claude/runtime/state/sc/rollback-hotfix.md
} > "$out"

printf '{"ts":"%s","kind":"sc_incident_runbook","threat_classes":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$threat_class_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — runbook emitted covering every threat class with rollback mechanics
- **DONE_WITH_CONCERNS** — emitted but 1-2 threat classes lack rollback path
- **BLOCKED** — no threat model present (must run /li:sc-threat-model first)

## Integration

**Reads:** prior SC outputs (threat-model, auth-flow, secret-inventory, audit-path)
**Writes:** `.claude/runtime/state/sc/incident-runbook-<ts>.md`, audit JSONL
**Dispatches to:** SecurityAuditor (response steps), ReleaseEngineer (rollback + hotfix)

## Anti-patterns

- **Runbook without detection signals** — on-call needs the trigger pattern, not just the response
- **Single-response runbook for all incidents** — per-threat-class because containment differs
- **No post-mortem template** — every incident produces a post-mortem; provide the skeleton
- **Skipping communication protocol** — incident response is technical AND organizational
