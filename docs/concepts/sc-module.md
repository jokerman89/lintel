# SC module — security-compliance for engineering depth

**Last updated:** 2026-05-31 (v4.3)
**Status:** Concept doc — referenced by `skills/sc/SKILL.md` + 7 sub-skills + 1 new agent + 3 hooks

> When work touches security or regulated paths — new external surface, customer-data path, auth flow, secret material, regulated feature — running it through plain BUILD discards what the operator needs: threat model with mitigations, secret inventory + rotation, auth review verdict, per-framework compliance evidence, durable audit path, incident response runbook. SC is the **third engineering-domain module in v4.x**, following the same pattern as TA + DA documented in [engineering-modules.md](engineering-modules.md).

## The problem

Pre-v4.3, security + compliance work happened through ad-hoc invocations:
- ThreatModelDrafter spawned manually when operator remembered
- Secrets cataloged in scattered docs or operator memory
- Auth reviews happened during PR review (or didn't)
- Compliance evidence assembled retroactively for audits
- Incident runbooks written post-incident, not pre-launch

The user explicitly named the gap: "When the work has security or compliance bearing ... invoke SC to produce threat-grade artifacts and compliance evidence."

The module fixes it with three granularities — `full`, `loop`, `single` — and 5 checkpoints with recovery.

## The model

```
Operator invocation
       │
       ▼
/li:sc {full|loop|single --action <name>}
       │
       │  Read pack policy + profile.engineering.security_compliance.*
       ▼
Granularity dispatch:
       │
       ├── full   → threat_model_complete → secrets_inventoried → auth_flow_locked
       │           → compliance_evidence_present → audit_path_verified
       │           → 6-dim scoring rubric → SHIP (score ≥80) or surface
       │
       ├── loop   → re-run threat-model + compliance-evidence → diff vs prior
       │
       └── single → direct sub-skill (no checkpoints, no orchestration)
                   sc-threat-model / sc-secret-management / sc-auth-flow /
                   sc-compliance-evidence / sc-audit-path /
                   sc-dependency-security / sc-incident-runbook
                       │
                       ▼
                   Spawn agent via Brief Forge:
                   ThreatModelDrafter / SecurityAuditor / JWTSecurityReviewer /
                   DependencyAuditor / SBOMAuditor /
                   ComplianceOfficer (NEW) / Architect / ReleaseEngineer
                       │
                       ▼
                   Output → .lintel/state/sc/<action>-<ts>.md
                   Audit → ~/.lintel/audit/sc-decisions.jsonl
```

## The five checkpoints (full pass)

### 1. `threat_model_complete`
STRIDE coverage with mitigations per threat. Produced by `sc-threat-model` + ThreatModelDrafter + SecurityAuditor.
Pass criterion: every enumerated threat has a mitigation OR explicit accept-risk; no high-severity unmitigated.

### 2. `secrets_inventoried`
All secrets cataloged with rotation policy. Produced by `sc-secret-management` + SecurityAuditor + SBOMAuditor.
Pass criterion: every secret has kind + scope + storage + rotation_cadence_days; raise-help on no-rotation secrets.

### 3. `auth_flow_locked`
Auth design + security review verdict. Produced by `sc-auth-flow` + JWTSecurityReviewer/SecurityAuditor.
Pass criterion: verdict PASS or PASS_WITH_CONCERNS (operator accepts); FAIL means re-loop.

### 4. `compliance_evidence_present`
Per-framework evidence collected. Produced by `sc-compliance-evidence` + ComplianceOfficer + Architect.
Pass criterion: every required framework has covered controls; gaps raise-help.

### 5. `audit_path_verified`
Audit log captures all required events with retention + integrity. Produced by `sc-audit-path` + SecurityAuditor + Architect.
Pass criterion: per-event emission point + durable transport + append-only sink + retention policy.

## The 6-dimensional scoring rubric (full pass exit gate)

| Dimension | Score 0-100 | Pass threshold | Source artifact |
|---|---|---|---|
| Threat model coverage (STRIDE per surface) | _ | 80 | `.lintel/state/sc/threat-model-<ts>.md` |
| Mitigations declared per threat | _ | 80 | `.lintel/state/sc/threats.json` (mitigation column) |
| Secrets inventoried + rotation policy | _ | 80 | `.lintel/state/sc/secret-inventory-<ts>.md` |
| Auth flow review verdict (PASS) | _ | 80 | `.lintel/state/sc/auth-flow-<ts>.md` (review verdict) |
| Compliance evidence (per required framework) | _ | 80 | `.lintel/state/sc/compliance-evidence-<framework>.md` |
| Audit path verified (events + retention + integrity) | _ | 80 | `.lintel/state/sc/audit-path-<ts>.md` |

## Sub-skill catalog

| Sub-skill | Primary agent | Other agents | Output |
|---|---|---|---|
| `sc-threat-model` | ThreatModelDrafter | SecurityAuditor | STRIDE threats + mitigations |
| `sc-secret-management` | SecurityAuditor | SBOMAuditor | secret inventory + rotation + supply-chain |
| `sc-auth-flow` | JWTSecurityReviewer or SecurityAuditor | SecurityAuditor (cross-check) | auth design + review verdict |
| `sc-compliance-evidence` | ComplianceOfficer (NEW) | Architect | per-framework evidence + cross-ref |
| `sc-audit-path` | SecurityAuditor | Architect | event schema + pipeline + retention |
| `sc-dependency-security` | DependencyAuditor | SBOMAuditor | SCA + license + SBOM |
| `sc-incident-runbook` | SecurityAuditor | ReleaseEngineer | per-threat-class runbook + rollback |

**L-002 win:** 6 of 7 sub-skills dispatch to **existing** security agents. Only 1 new agent (ComplianceOfficer) for genuinely new capability (cross-framework evidence orchestration).

## Agent additions (v4.3)

### `ComplianceOfficer`
- **Purpose:** cross-framework compliance evidence orchestration; control coverage mapping; gap surfacing
- **Why new:** existing security agents are threat-focused; compliance evidence is a different shape (control mappings, framework reuse, technical-vs-procedural distinction)
- **Spawned by:** `sc-compliance-evidence`

## Hook additions (v4.3)

All three are warn-only (per engineering-modules pattern). Each uses unified `audit_log` from `bin/_audit.sh`.

### `sc-threat-coverage-warn`
Pre-edit on auth/data surface files. Surfaces: "no threat model OR file not covered OR model > 90 days old."

### `sc-auth-bypass-warn`
Pre-edit on auth-flow files. Detects skip-auth flags, magic credentials, bypass routes, direct role assignments. Surfaces: "high-risk auth pattern(s) detected."

### `sc-compliance-gap-warn`
Pre-edit on regulated-data paths. Surfaces: "$N compliance gap(s) across $frameworks (oldest evidence: $age days)."

Plus EXISTING security hooks (sourced from earlier work, not duplicated):
- `no-secrets-in-edit` — already exists
- `secret-scan-block` — already exists
- `customer-data-block` — already exists
- `no-production-mutation-without-auth` — already exists

## Profile preferences

Under `engineering.security_compliance.*` in `~/.lintel/profile.yaml`:

```yaml
engineering:
  security_compliance:
    sdl_active: true
    secret_management: keyvault            # keyvault | aws-secrets-manager | hashicorp-vault | local-encrypted
    threat_model_required_on:
      - new_external_dependency
      - new_data_path
      - new_auth_flow
    compliance_frameworks: [soc2, gdpr]    # iso27001 | hipaa | pci-dss | fedramp
    audit_retention_days: 2555             # 7 years default
```

Hooks + sub-skills read these. Defaults baked in when absent.

## Pack overrides

Packs can declare `security_compliance.*` overrides:

```yaml
# packs/some-pack/pack.yaml
security_compliance:
  threat_surface_glob: "src/api/**/*,src/auth/**/*"
  auth_flow_glob: "src/auth/**/*,middleware/auth*"
  regulated_path_glob: "src/billing/**/*,src/health/**/*"
```

## Audit trail

Every module + sub-skill + checkpoint writes to `~/.lintel/audit/sc-decisions.jsonl`:

```jsonl
{"ts":"...","kind":"sc_module_complete","granularity":"full","score":87,"checkpoints_passed":5,"frameworks":"soc2,gdpr"}
{"ts":"...","kind":"sc_threat_model","threats":34,"high_unmitigated":0,"raise_help":false}
{"ts":"...","kind":"sc_secret_management","secrets":12,"no_rotation":1,"target_store":"keyvault"}
{"ts":"...","kind":"sc_compliance_evidence","frameworks":"soc2,gdpr","gaps":2,"raise_help":true}
```

## Composition — SC as parallel branch in full engineering pass

Per engineering-modules.md §"Composition":

```
TA
  │
  ├── DA  ┐  (parallel — data + security are independent at this layer)
  ├── SC  ┘
  │
  ▼
DH
  │
  ▼
TQ
```

SC runs in parallel with DA after TA produces architecture decisions. SC reads pack compliance fields (which DA needs for retention policy in cross-reference); DA reads architectural boundaries (which SC needs for threat modeling cross-reference). Each module makes its own decisions on its own clock.

## Anti-patterns

- **Treating threats as ranking exercise** — every threat needs a mitigation OR explicit accept-risk; ranking without action is theater
- **Single compliance framework when pack declares multiple** — gather per framework, identify reuse aggressively
- **Inventing security agents when 6 exist** — L-002 inventory pre-PR; ComplianceOfficer is the only new agent because it's the only genuinely new capability
- **Procedural-only evidence for technical controls** — policy doc ≠ access control implementation
- **Audit logs in best-effort transport** — durable transport is non-negotiable
- **Runbook without detection signals** — on-call needs the trigger, not just the response
- **Curating threat patterns / control mappings / runbook templates** — sub-skills are dispatch contracts (L-001); content from agents at invocation

## Integration points

**Reads:**
- `~/.lintel/profile.yaml` `engineering.security_compliance.*`
- `lib/pack-resolver.sh` for pack policy (sdl_active, audit_paths, compliance.hooks)
- Existing security agents (6) + 1 new agent
- Existing security hooks (4) — sourced, not duplicated

**Writes:**
- `.lintel/state/sc/*.{md,json}` (per-action artifacts)
- `~/.lintel/audit/sc-decisions.jsonl`
- Brief Forge envelopes through the standard gate

**Triggered by:**
- Operator: `/li:sc {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when auth/compliance intent detected
- `/li:full-engineering-pass` (when composition skill ships): parallel branch after TA

**Tested by:**
- `tests/shape/sc-module-contract.sh`
- `tests/unit/sc-routing.sh`
