---
name: dh-on-call-playbook
layer: foundation
description: DH sub-skill — per-failure-mode runbook + escalation matrix. Dispatches to ReleaseEngineer + SecurityAuditor agents.
color: purple
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are DH-ON-CALL-PLAYBOOK — the workflow that produces the on-call playbook.

## What this skill does

Reads observability spec + rollback strategy + SLI/SLO spec. Spawns `ReleaseEngineer` for per-failure-mode response steps and `SecurityAuditor` for the security-incident response overlap (cross-reference with `/li:sc-incident-runbook` if SC ran). Produces on-call-playbook with detection signal per failure mode + first-5-minute actions + escalation matrix.

## When to use

- DH full pass on_call_ready checkpoint
- Single action `/li:dh single --action on-call-playbook`
- Pre-launch checklist
- After incident review wants generalized playbook

## When NOT to use

- General SRE handbook (use SRE-specific tooling)
- Single-incident retrospective (write inline)

## Workflow

### Step 1 — Read context

```bash
observability_spec=$(find .lintel/state/dh -name "observability-spec-*.md" -mtime -7 2>/dev/null | sort | tail -1)
rollback_strategy=$(find .lintel/state/dh -name "rollback-strategy-*.md" -mtime -7 2>/dev/null | sort | tail -1)
slo_spec=$(find .lintel/state/dh -name "sli-slo-spec-*.md" -mtime -7 2>/dev/null | sort | tail -1)
sc_runbook=$(find .lintel/state/sc -name "incident-runbook-*.md" -mtime -30 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn ReleaseEngineer for per-failure-mode response

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Per-failure-mode response playbook
context_pointers:
  - $observability_spec
  - $rollback_strategy
  - $slo_spec
constraints:
  - per failure mode: detection signal (which alert/SLI burn), first-5-minute actions, decision tree
  - escalation matrix: severity → who pages → when escalate
  - reference rollback paths from $rollback_strategy
acceptance:
  - per-failure-mode section + escalation matrix
EOF

/li:brief-forge subagent_spawn dh-on-call-playbook ReleaseEngineer brief "$brief_file"
```

### Step 3 — Spawn SecurityAuditor for security-incident overlap

```bash
sec_brief=$(mktemp)
cat > "$sec_brief" <<EOF
task: Cross-reference operational + security incident response
context_pointers:
  - .lintel/state/dh/operational-runbook.md
  - $sc_runbook (if present)
constraints:
  - identify failure modes that are ALSO security incidents (auth outage, secret leak, etc.)
  - merge response paths where they overlap
  - clarify when to escalate to security on-call vs operational on-call
acceptance:
  - failure-mode → response-team mapping + escalation triggers
EOF

/li:brief-forge subagent_spawn dh-on-call-playbook SecurityAuditor brief "$sec_brief"
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/dh/on-call-playbook-$ts.md"
{
  echo "# On-call playbook — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-failure-mode response"
  cat .lintel/state/dh/operational-runbook.md
  echo ""
  echo "## Escalation matrix"
  cat .lintel/state/dh/escalation-matrix.md
  echo ""
  echo "## Security-incident cross-reference"
  cat .lintel/state/dh/security-overlap.md
} > "$out"

printf '{"ts":"%s","kind":"dh_on_call_playbook","failure_modes":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$failure_mode_count" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/dh-decisions.jsonl"
```

## Status protocol

- **DONE** — playbook emitted per failure mode + escalation matrix
- **DONE_WITH_CONCERNS** — emitted but 1-2 failure modes lack first-5-minute actions
- **BLOCKED** — observability spec missing (must run /li:dh-observability-spec first)

## Integration

**Reads:** DH observability + rollback + SLO; SC incident runbook (if present)
**Writes:** `.lintel/state/dh/on-call-playbook-<ts>.md`, audit JSONL
**Dispatches to:** ReleaseEngineer (response steps), SecurityAuditor (security overlap)

## Anti-patterns

- **Playbook without detection signals** — on-call needs trigger pattern, not just response
- **First-5-minute actions without decision tree** — early actions are about gathering data, not fixing
- **No escalation triggers** — escalation matrix needs when-to-escalate, not just who
- **Skipping security overlap** — auth/secret incidents need both on-call teams
