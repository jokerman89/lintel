---
name: sc
layer: foundation
workflow_root: true
description: Use for security and compliance depth — threat models, auth flows, secret management, dependency-security audits, compliance evidence, and incident runbooks. Reach for it when a change has a security or regulatory surface. Runs full, loop, or single-capability, dispatching to the security agents and scoring against a rubric.
color: red
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Security- or compliance-bearing work proceeds with no threat model, no secret inventory, no audit-path verification, no per-framework compliance evidence; vulnerabilities reach production undetected and regulated work cannot be defended in audit."
navigation:
  primary_intent: produce threat-grade artifacts and compliance evidence when work touches security or regulated paths
  triggers:
    - new external surface / customer-data path / regulated feature
    - operator types /li:sc {full|loop|single --action <name>}
    - BUILD phase detects auth or compliance intent (Phase 4 wiring)
  sibling_workflows:
    - /li:ta — tech-architecture module (v4.1)
    - /li:da — data-architecture module (v4.2)
    - /li:dh — devops-hosting module (v4.4)
    - /li:tq — testing-qa module (v4.5)
    - /li:full-engineering-pass — composes all 5 modules in DAG order
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  preferences_root: engineering.security_compliance.*
  granularities: [full, loop, single]
  checkpoints:
    - threat_model_complete: STRIDE coverage with mitigations per threat
    - secrets_inventoried: all secrets cataloged with rotation policy
    - auth_flow_locked: auth design plus security review verdict
    - compliance_evidence_present: per-framework evidence collected
    - audit_path_verified: audit log captures all required events with retention
  recovery:
    - on_failure: revert to last-locked checkpoint, surface gap, AskUserQuestion (Re-loop | Accept-with-concern | Raise-help)
  continuation:
    - after_fix: resume at failed checkpoint, job state preserves loop position
  raise_help:
    - high_severity_threat_without_mitigation: operator decides accept-risk or block
    - compliance_evidence_gap_in_required_framework: operator decides override or comply
    - secret_with_no_rotation_path: operator decides accept-toxic or rotate
---

You are the SC (security-compliance) module — Phase 4 v4.3 of Lintel.

## What this module does

Produces threat-grade artifacts and compliance evidence when work touches security or regulated paths. Three granularities — full pass for new external surfaces, loop iteration for revised threat surfaces, single action for targeted ops.

| Entry | When | Outputs |
|---|---|---|
| `/li:sc full` | new external surface / regulated feature | `threat-model.md` + `secret-management-plan.md` + `auth-flow.md` + `compliance-evidence.md` + `audit-path.md` + `incident-runbook.md` |
| `/li:sc loop` | mid-cycle threat surface revision | revised threat model + diff against prior + new mitigations |
| `/li:sc <capability>` · `/li:sc single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New external surface (API endpoint, OAuth integration, webhook receiver)
- Work touches customer data, PII, secrets, or regulated material
- Work requires SOC2/GDPR/HIPAA/PCI-DSS/FedRAMP evidence
- Pre-production for any feature with auth or authorization path
- BUILD phase detected auth or compliance intent (Phase 4 wiring auto-invokes)

## When NOT to use

- Internal-only refactor with no auth/data impact
- Pure UI work without backend security surface — `/li:cycle`
- Single dependency update — `Migrator` agent direct (unless it's a security-critical lib, then `/li:sc dependency-security`)

## Sub-capability dispatch

Per ADR-0009 the seven capabilities live here as dispatch rows — there are no per-capability
skill files. Invoke one directly as `/li:sc <capability>` (long form: `/li:sc single --action
<capability>`). Per L-001 each capability is a workflow + dispatch contract: content comes from
agents at invocation (spawned via `/li:brief-forge subagent_spawn`); each emits
`.claude/runtime/state/sc/<capability>-<ts>.md` and appends the module audit line (Step 6).

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `threat-model` | ThreatModelDrafter + SecurityAuditor | STRIDE threat enumeration with mitigations | RAISE_HELP when any high-severity threat unmitigated (BLOCKED); one entry per (threat-category, attack-vector, target); severity high\|medium\|low; platform-covered threats documented, not enumerated; 1-2 medium unmitigated = DONE_WITH_CONCERNS with operator accept |
| `secret-management` | SecurityAuditor + SBOMAuditor | secret inventory + rotation policy + dependency-shipped-secret scan | RAISE_HELP when any secret lacks a rotation cadence (BLOCKED); pref: `secret_management` (keyvault\|aws-secrets-manager\|hashicorp-vault\|local-encrypted); per secret: name, kind, scope, storage location, rotation_cadence_days; per dependency: clean\|suspect\|confirmed-default-credential |
| `auth-flow` | JWTSecurityReviewer (when auth kind = jwt) or SecurityAuditor (otherwise), + SecurityAuditor cross-check | auth design + security review verdict (PASS \| PASS_WITH_CONCERNS \| FAIL) | routes on detected auth kind: jwt\|oauth2\|oidc\|saml\|api-key\|mtls; BLOCKED on FAIL (must re-loop); constraints below |
| `compliance-evidence` | ComplianceOfficer (once per framework) + Architect | per-framework + aggregated evidence with per-control verdict (covered \| partial \| gap) + evidence pointer | RAISE_HELP when any control verdict = gap (BLOCKED); pref: `frameworks` (default soc2,gdpr); distinguish technical vs procedural control evidence; reads TA `system-arch.md` if present |
| `audit-path` | SecurityAuditor + Architect | audit log design: event schema + integrity + pipeline + retention | pref: `retention` (default 2555 days / 7 years); per event: timestamp (UTC, monotonic), actor, action, target, outcome, context-id; sink append-only/WORM + tamper-evident (hash chain or signed); durable transport; audit-log content stays factual + neutral regardless of pack voice |
| `dependency-security` | DependencyAuditor (per detected ecosystem) + SBOMAuditor | SCA report + SBOM (SPDX or CycloneDX) | RED = high-severity exploitable CVE OR license-incompatible (BLOCKED — remediate or explicit override); YELLOW = medium CVE OR abandoned maintainer; auto-detects ecosystems npm/go/cargo/python/jvm/dotnet; runs anytime (no checkpoint ordering) |
| `incident-runbook` | SecurityAuditor + ReleaseEngineer | per-threat-class response runbook: detection signals, containment, eradication, recovery, post-mortem template | BLOCKED without a threat model (run `/li:sc threat-model` first); collects the prior SC artifacts <7 days old; distinguish on-call action (minutes) vs operator action (hours); hotfix paths: feature-flag toggle, circuit-break, traffic-cutover; communication protocol incl. status-page |

L-002 win: 6 of 7 capabilities dispatch to existing security agents. Only 1 new agent (ComplianceOfficer) for genuinely new capability (cross-framework evidence orchestration).

### auth-flow — design constraints

- sequence diagram per flow (login / refresh / revoke / step-up MFA)
- token lifetimes documented + justified
- refresh strategy + revocation path
- MFA posture per role
- per-step security check (rate limit, replay protection, session fixation)

## Workflow

### Step 1 — Parse invocation

```bash
granularity="${1:?usage: /li:sc {full|loop|<capability>|single --action <capability>}}"
capabilities="threat-model|secret-management|auth-flow|compliance-evidence|audit-path|dependency-security|incident-runbook"
case "$granularity" in
  full|loop) action="" ;;
  single)
    [ "$2" = "--action" ] || { echo "ERROR: --action required for single"; exit 1; }
    action="$3" ;;
  *) action="$granularity"; granularity="single" ;;   # ADR-0009 shorthand: /li:sc <capability>
esac
if [ "$granularity" = "single" ]; then
  echo "$action" | grep -qE "^(${capabilities})$" || { echo "ERROR: unknown capability '$action'"; exit 1; }
fi
```

### Step 2 — Read pack + profile preferences

```bash
source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh"

# Pack policy provides hard gates (the active pack's compliance gates; none by default)
compliance_hooks=$(resolve_pack_field compliance.hooks 2>/dev/null || true)
audit_paths=$(resolve_pack_field compliance.audit_paths 2>/dev/null || true)

# Profile preferences (engineering.security_compliance.*)
PROFILE="$LINTEL_HOME/profile.yaml"
secret_management=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'security_compliance:' | grep 'secret_management:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
secret_management="${secret_management:-local-encrypted}"

compliance_frameworks=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'security_compliance:' | grep 'compliance_frameworks:' | head -1 | awk -F': *' '{print $2}' | tr -d '[]"' | tr -d "'")
compliance_frameworks="${compliance_frameworks:-soc2,gdpr}"

audit_retention=$(grep -A30 '^engineering:' "$PROFILE" 2>/dev/null | grep -A10 'security_compliance:' | grep 'audit_retention_days:' | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]')
audit_retention="${audit_retention:-2555}"   # default 7 years
```

### Step 3 — Dispatch by granularity

#### `full` granularity

```bash
mkdir -p .claude/runtime/state/sc
audit="$LINTEL_HOME/audit/sc-decisions.jsonl"
mkdir -p "$(dirname "$audit")"

for checkpoint in threat_model_complete secrets_inventoried auth_flow_locked compliance_evidence_present audit_path_verified; do
  echo "─── Checkpoint: $checkpoint ───"
  run_checkpoint "$checkpoint" || handle_checkpoint_failure "$checkpoint"
  audit_checkpoint "$checkpoint" "$verdict"
done

score=$(apply_scoring_rubric)
if [ "$score" -lt 80 ]; then
  echo "SC full pass score=$score (threshold 80) — surface concerns"
  exit 1
fi

echo "SC full pass complete — score=$score, output .claude/runtime/state/sc/"
```

#### `loop` granularity

```bash
if [ ! -f ".claude/runtime/state/sc/00-state.md" ]; then
  echo "ERROR: no prior SC state — use /li:sc full first"
  exit 1
fi

prior_iteration=$(grep -E '^iteration:' .claude/runtime/state/sc/00-state.md | head -1 | awk '{print $2}')
new_iteration=$((prior_iteration + 1))

run_checkpoint threat_model_complete
run_checkpoint compliance_evidence_present

# Diff against prior iteration (threat surface focus)
echo "Threat diff vs iteration $prior_iteration:" > .claude/runtime/state/sc/iteration-${new_iteration}-diff.md
diff .claude/runtime/state/sc/iteration-${prior_iteration}-threats.md .claude/runtime/state/sc/iteration-${new_iteration}-threats.md \
  >> .claude/runtime/state/sc/iteration-${new_iteration}-diff.md || true
```

#### `single` granularity

```bash
# ADR-0009: no sub-skill files — dispatch straight off the Sub-capability dispatch table.
# Spawn the capability's agents via /li:brief-forge subagent_spawn, pass the prefs listed
# in its row (secret-management ← secret_management; compliance-evidence ← frameworks;
# audit-path ← retention), emit .claude/runtime/state/sc/${action}-<ts>.md, append the
# audit line (Step 6).
dispatch_capability "$action"   # no loop, no checkpoints
```

### Step 4 — Checkpoint failure handling (recovery + raise-help)

```bash
handle_checkpoint_failure() {
  local checkpoint="$1"
  echo "Checkpoint '$checkpoint' FAILED"

  case "$checkpoint" in
    threat_model_complete)
      if [ "$high_severity_unmitigated" -gt 0 ]; then
        ask_user_question "Threat model has $high_severity_unmitigated high-severity threats without mitigation. Re-loop / Accept-risk / Raise-help (block or override)?"
      fi
      ;;
    compliance_evidence_present)
      if [ "$framework_gap" = "true" ]; then
        ask_user_question "Compliance evidence gap in required framework. Re-loop / Accept-with-concern / Raise-help (decide override or comply)?"
      fi
      ;;
    secrets_inventoried)
      if [ "$no_rotation_secrets" -gt 0 ]; then
        ask_user_question "$no_rotation_secrets secret(s) without rotation path. Re-loop / Accept-toxic / Raise-help (rotate)?"
      fi
      ;;
  esac

  revert_to_last_locked
}
```

### Step 5 — 6-dimensional scoring rubric

```
| Dimension | Score 0-100 |
|---|---|
| Threat model coverage (STRIDE per surface) | <D1> |
| Mitigations declared per threat | <D2> |
| Secrets inventoried + rotation policy | <D3> |
| Auth flow review verdict (PASS) | <D4> |
| Compliance evidence (per required framework) | <D5> |
| Audit path verified (events + retention + integrity) | <D6> |

Pass threshold per dimension: 80.
Full-pass exit: every dimension ≥ 80 OR explicit operator override.
```

### Step 6 — Audit + emit ship report

```bash
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"sc_module_complete","granularity":"%s","score":%d,"checkpoints_passed":%d,"frameworks":"%s","operator":"%s"}\n' \
  "$ts" "$granularity" "$score" "$passed_count" "$compliance_frameworks" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — granularity completed, score ≥ 80, no high-severity unmitigated threats
- **DONE_WITH_CONCERNS** — completed but 1-2 dimensions below 80 with operator accept-with-concern
- **BLOCKED** — checkpoint failed, raise-help triggered, awaiting operator
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- `~/.lintel/profile.yaml` `engineering.security_compliance.*` block
- `lib/pack-resolver.sh` for pack policy (compliance.hooks, audit_paths)
- Existing security agents: SecurityAuditor, ThreatModelDrafter, DependencyAuditor, JWTSecurityReviewer, SBOMAuditor, PrivacyBoundaryAudit
- New agents: ComplianceOfficer
- Existing security-flavored ADRs (`.lintel/decisions/`, `docs/decisions/`, `.claude/decisions/`)

**Writes:**
- `.claude/runtime/state/sc/threat-model.md` (full)
- `.claude/runtime/state/sc/secret-inventory.md`
- `.claude/runtime/state/sc/auth-flow-review.md`
- `.claude/runtime/state/sc/compliance-evidence-<framework>.md`
- `.claude/runtime/state/sc/audit-path.md`
- `.claude/runtime/state/sc/incident-runbook.md`
- `.claude/runtime/state/sc/iteration-N-threats.md`
- `.claude/runtime/audit/sc-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:sc {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when auth/compliance intent detected
- `/li:full-engineering-pass`: parallel branch with DA after TA

**Hooks** (dormant by decision, ADR-0008 — ship in `hooks/shared/` but are opt-in, not auto-registered):
- `hooks/shared/sc-threat-coverage-warn/` (pre-edit on auth/data files not covered by threat model)
- `hooks/shared/sc-auth-bypass-warn/` (pre-edit on auth-flow files with high-risk patterns)
- `hooks/shared/sc-compliance-gap-warn/` (pre-edit on regulated-data paths)

Plus EXISTING hooks (sourced from earlier work):
- `hooks/shared/no-secrets-in-edit/` (already exists)
- `hooks/shared/secret-scan-block/` (already exists)
- `hooks/shared/customer-data-block/` (already exists)
- `hooks/shared/no-production-mutation-without-auth/` (already exists)

## Anti-patterns

- **Skipping threat_model_complete checkpoint for "obvious" features** — most surfaces have non-obvious threats
- **Single compliance framework when pack declares multiple** — gather evidence per framework, separately
- **Inventing new agents when existing cover** — security/ category has 6 agents already
- **Hardcoding secret_management when profile says different** — read preferences
- **Silent high-severity threat acceptance** — explicit operator override required, audited
- **Blocking on hook warnings** — SC hooks warn; blocking is operator's explicit decision via pack policy
