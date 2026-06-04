---
name: sc-compliance-evidence
layer: foundation
description: SC sub-skill — per-framework (SOC2/GDPR/HIPAA/etc.) evidence collection. Dispatches to ComplianceOfficer (NEW) + Architect agents. Raises help on framework gap.
color: red
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are SC-COMPLIANCE-EVIDENCE — the workflow that produces per-framework evidence.

## What this skill does

For each compliance framework declared in `pack.compliance.hooks` or `engineering.security_compliance.compliance_frameworks`, spawn `ComplianceOfficer` to collect evidence (control mappings, screenshot pointers, policy doc references, audit-log queries). Spawn `Architect` to map architectural decisions to control requirements. Produces per-framework evidence document. Raises help on framework gap.

## When to use

- SC full pass compliance_evidence_present checkpoint
- Single action `/li:sc single --action compliance-evidence`
- Pre-audit prep (customer audit, internal audit, regulatory)
- An engagement or release requires an evidence package

## When NOT to use

- Single control verification (operator can run control-specific check directly)
- Operational SOC reporting (use ops tools, not this scaffold)

## Workflow

### Step 1 — Read frameworks

```bash
frameworks_csv="${frameworks:-${compliance_frameworks:-soc2,gdpr}}"
IFS=',' read -ra frameworks <<< "$frameworks_csv"
```

### Step 2 — Per framework: spawn ComplianceOfficer

```bash
for fw in "${frameworks[@]}"; do
  fw=$(printf '%s' "$fw" | tr -d '[:space:]')
  brief_file=$(mktemp)
  cat > "$brief_file" <<EOF
task: Collect evidence per ${fw} control mapping
context_pointers:
  - .lintel/state/sc/threat-model-*.md (latest, if present)
  - .lintel/state/sc/auth-flow-*.md (latest, if present)
  - .lintel/state/sc/secret-inventory-*.md (latest, if present)
  - .lintel/state/sc/audit-path-*.md (latest, if present)
constraints:
  - per ${fw} control: evidence pointer (file path or audit-log query) or flagged-gap
  - distinguish: technical-control evidence vs procedural-control evidence
acceptance:
  - per-control verdict (covered | partial | gap) with evidence pointer
EOF
  /li:brief-forge subagent_spawn sc-compliance-evidence ComplianceOfficer brief "$brief_file"
  mv .lintel/state/sc/evidence.md ".lintel/state/sc/compliance-evidence-${fw}.md"
done
```

### Step 3 — Spawn Architect for control mapping

```bash
arch_brief=$(mktemp)
cat > "$arch_brief" <<EOF
task: Map architectural decisions (from /li:ta if present) to compliance controls
context_pointers:
  - .lintel/state/ta/system-arch.md (if present)
  - .lintel/state/sc/compliance-evidence-*.md
constraints:
  - per architectural decision: which controls satisfied or threatened
acceptance:
  - cross-reference table: decision → controls
EOF

/li:brief-forge subagent_spawn sc-compliance-evidence Architect brief "$arch_brief"
```

### Step 4 — Raise-help on framework gap

```bash
total_gaps=0
for fw in "${frameworks[@]}"; do
  fw=$(printf '%s' "$fw" | tr -d '[:space:]')
  gap=$(jq -r '.controls[] | select(.verdict == "gap") | .id' ".lintel/state/sc/compliance-evidence-${fw}.json" 2>/dev/null | wc -l)
  total_gaps=$((total_gaps + gap))
done

if [ "$total_gaps" -gt 0 ]; then
  echo "RAISE_HELP: $total_gaps control(s) flagged as gap across $frameworks_csv"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/sc/compliance-evidence-$ts.md"
{
  echo "# Compliance evidence — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Frameworks: $frameworks_csv"
  echo ""
  for fw in "${frameworks[@]}"; do
    fw=$(printf '%s' "$fw" | tr -d '[:space:]')
    echo "## $fw"
    cat ".lintel/state/sc/compliance-evidence-${fw}.md"
    echo ""
  done
  echo "## Architectural decisions → control cross-reference"
  cat .lintel/state/sc/decision-control-xref.md
} > "$out"

printf '{"ts":"%s","kind":"sc_compliance_evidence","frameworks":"%s","gaps":%d,"raise_help":%s,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$frameworks_csv" "$total_gaps" \
  "$([ "$total_gaps" -gt 0 ] && echo true || echo false)" \
  "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — every framework covered (no gaps)
- **DONE_WITH_CONCERNS** — partial evidence accepted with note
- **BLOCKED** — raise-help triggered (framework gap)

## Integration

**Reads:** pack policy, profile preferences, prior SC outputs, TA system-arch
**Writes:** `.lintel/state/sc/compliance-evidence-<framework>.md`, audit JSONL
**Dispatches to:** ComplianceOfficer (NEW, per-framework evidence), Architect (control mapping)

## Anti-patterns

- **Single framework when pack requires multiple** — collect per framework, separately
- **Evidence without pointers** — every claim has a file path or audit-log query
- **Conflating technical + procedural** — distinguish; procedural needs operator-owned doc
- **Curating control mappings** — ComplianceOfficer reasons; this skill orchestrates (L-001)
