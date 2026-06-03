---
name: sc-threat-model
layer: foundation
description: SC sub-skill — STRIDE / attack-tree threat enumeration with mitigations. Dispatches to ThreatModelDrafter + SecurityAuditor agents.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are SC-THREAT-MODEL — the workflow that produces a threat model with mitigations.

## What this skill does

Reads operator's surface description + existing data-flow / auth-flow diagrams (if present). Spawns `ThreatModelDrafter` to enumerate threats using STRIDE (Spoofing, Tampering, Repudiation, Info-disclosure, DoS, Elevation-of-privilege) and `SecurityAuditor` to validate mitigations. Raises help when high-severity threats lack mitigation.

Per L-001: workflow + dispatch contract. Content from agents at invocation.

## When to use

- SC full pass threat_model_complete checkpoint
- Single action `/li:sc single --action threat-model`
- New external surface or auth path introduction
- Pre-release threat surface review

## When NOT to use

- Pure refactor with no surface change
- Threat surface revision only — use `/li:sc loop`

## Workflow

### Step 1 — Read surface context

```bash
surface_file="${1:-.lintel/state/sc/surface-description.md}"
auth_flow=$(find .lintel/state -name "auth-flow*.md" -mtime -7 2>/dev/null | sort | tail -1)
data_flow=$(find .lintel/state -name "data-flow*.md" -mtime -7 2>/dev/null | sort | tail -1)
```

### Step 2 — Spawn ThreatModelDrafter for STRIDE enumeration

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate threats using STRIDE per declared surface
context_pointers:
  - $surface_file
  - $auth_flow
  - $data_flow
constraints:
  - one entry per (threat-category, attack-vector, target)
  - severity: high | medium | low
  - skip threats already mitigated by platform (document them as "platform-covered")
acceptance:
  - structured threat list with severity + attack vector + target
EOF

/li:brief-forge subagent_spawn sc-threat-model ThreatModelDrafter brief "$brief_file"
```

### Step 3 — Spawn SecurityAuditor for mitigation validation

```bash
mitigation_brief=$(mktemp)
cat > "$mitigation_brief" <<EOF
task: Validate mitigations per enumerated threat
context_pointers:
  - .lintel/state/sc/threats.json
constraints:
  - per threat: existing mitigation OR proposed mitigation OR flagged-unmitigated
  - flagged-unmitigated requires explicit operator accept-risk
acceptance:
  - per-threat mitigation verdict with implementation pointer
EOF

/li:brief-forge subagent_spawn sc-threat-model SecurityAuditor brief "$mitigation_brief"
```

### Step 4 — Raise-help if high-severity unmitigated

```bash
high_unmitigated=$(jq -r '.threats[] | select(.severity == "high" and .mitigation == "unmitigated") | .id' .lintel/state/sc/threat-model.json 2>/dev/null | wc -l)
if [ "$high_unmitigated" -gt 0 ]; then
  echo "RAISE_HELP: $high_unmitigated high-severity threat(s) unmitigated"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/sc/threat-model-$ts.md"
{
  echo "# Threat model — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Enumeration (STRIDE)"
  cat .lintel/state/sc/threats.md
  echo ""
  echo "## Mitigations"
  cat .lintel/state/sc/mitigations.md
} > "$out"

printf '{"ts":"%s","kind":"sc_threat_model","threats":%d,"high_unmitigated":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$threat_count" "$high_unmitigated" \
  "$([ "$high_unmitigated" -gt 0 ] && echo true || echo false)" \
  "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — threat model emitted, 0 high-severity unmitigated
- **DONE_WITH_CONCERNS** — 1-2 medium-severity unmitigated with operator accept-with-concern
- **BLOCKED** — raise-help triggered (high-severity unmitigated)
- **NEEDS_CONTEXT** — surface description missing

## Integration

**Reads:** surface description, auth-flow + data-flow if present
**Writes:** `.lintel/state/sc/threat-model-<ts>.md`, audit JSONL
**Dispatches to:** ThreatModelDrafter (enumeration), SecurityAuditor (mitigation validation)

## Anti-patterns

- **Skipping platform-covered threats** — document them; future operators need to know they were considered
- **Single-severity threats** — high/medium/low ranking informs acceptance decisions
- **Curating threats in this skill** — ThreatModelDrafter enumerates (L-001)
- **Silent unmitigated high-severity** — raise-help is required
