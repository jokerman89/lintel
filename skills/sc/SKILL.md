---
name: sc
layer: foundation
workflow_root: true
description: Use for security and compliance depth — threat models, auth flows, secret management, dependency-security audits, compliance evidence, and incident runbooks. Reach for it when a change has a security or regulatory surface. Runs full, loop, or single-capability, dispatching to the security agents and scoring against a rubric.
color: red
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Security-bearing work lacks explicit threat, auth, secret and applicable-control evidence; vulnerabilities or unsupported clearance can reach delivery."
navigation:
  primary_intent: produce threat-grade artifacts and applicable compliance evidence
  triggers:
    - new external surface / customer-data path / regulated feature
    - operator types /li:sc {full|loop|single --action <name>}
    - active workflow requests security depth
  sibling_workflows:
    - /li:ta — technical architecture
    - /li:da — data architecture
    - /li:dh — hosting and operations
    - /li:tq — testing and QA
    - /li:full-engineering-pass — dependency-ordered composition
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 80000
domain:
  # Legacy discovery hint, not a validated pack-schema field; see DA preference reference.
  preferences_root: engineering.security_compliance.*
  granularities: [full, loop, single]
  checkpoints:
    - threat_model_complete: boundaries, threats, mitigations and residual decisions evidenced
    - secrets_inventoried: redacted secret metadata with actual owner and response policy
    - auth_flow_locked: applicable flow and token validation evidence
    - compliance_evidence_present: all applicable required control outcomes visible
    - audit_path_verified: required events, integrity and retention actually checked
  recovery:
    - on_failure: preserve evidence and stop the affected action pending scoped resolution
  continuation:
    - after_fix: reverify changed inputs and the unmet checkpoint
  raise_help:
    - high_severity_threat_without_mitigation: refer the specific residual risk to its owner
    - required_policy_unresolved: retain blocked acceptance rather than neutral fallback
    - secret_without_authorized_response: escalate redacted facts to the incident owner
---

# Security and compliance

Preference metadata only: [optional engineering preferences](../da/references/preferences.md)
explains the retained `preferences_root` hint; it is not a validated pack interface.

Read [security decision methods](references/decision-methods.md): implementation
evidence, legal/policy applicability and unknowns are different. Produce threats,
auth/secret/audit designs, compliance coverage and incident playbooks, not a blanket
certification. The host's permission and actual policy remain authoritative.

For an implementation review, use the same
[adaptive Review Method](../review/references/adaptive.md) and
[targeted security evidence](../review/references/security.md) as REVIEW and MARS.
Keep source/version, actual trust boundary and selected mandatory controls
explicit. Object/tenant authorization is distinct from privacy or residency;
agent/tool authority is distinct from a model's declared role. This adds review
questions, not a scanning engine, credential use or permission to reproduce vulnerabilities.

`/li:sc full` covers the checkpoints below. `/li:sc loop` revisits explicitly saved evidence;
`/li:sc <capability>` or `/li:sc single --action <capability>` limits the assignment. Preserve
read-only review versus authorized implementation. No scan of live services,
customer data, credential use/rotation or incident message follows from invocation.

## Sub-capability dispatch

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `threat-model` | ThreatModelDrafter, then distinct SecurityAuditor review | STRIDE by boundary, mitigations and residual-risk decisions | actual assets/actors; platform-covered threats need deployment evidence, not omission |
| `secret-management` | SecurityAuditor + SecretsScanReviewer; SBOMAuditor for dependency-shipped defaults | redacted inventory, owner, storage, response/rotation and default-credential triage | no values or live credential tests; cadence/provider comes from applicable risk/policy |
| `auth-flow` | OAuthFlowReviewer for OAuth/OIDC; JWTSecurityReviewer for JWT internals; SecurityAuditor for other auth | flow diagrams, token/claim/scopes/revocation checks | one protocol is not another; grant/client-specific checks, exact library/provider versions |
| `compliance-evidence` | ComplianceOfficer per applicable framework; Architect for system boundary | technical/procedural evidence, cross-framework reuse and gap map | primary/consolidated source/version, effective/application dates, verified_on, responsible owner and currency limits; no default SOC2/GDPR or score-based certification |
| `audit-path` | Architect design + SecurityAuditor review | event/integrity/transport/retention design and checks | actor/action/target/outcome/context; UTC timestamp and ordering mechanism distinct; no blanket seven years |
| `dependency-security` | DependencyAuditor + SBOMAuditor | ecosystem SCA and artifact-scoped SPDX/CycloneDX evidence | actual advisory range/reachability and license use/distribution policy; unavailable feed remains unverified |
| `incident-runbook` | SecurityAuditor + DeploymentEngineer | detection, containment, eradication, recovery, escalation and postmortem | selected threat/observability evidence, named on-call/live-action authority; no real containment or notifications |

For auth, retain login/refresh/revoke/step-up diagrams, justified lifetimes, refresh/
revocation paths, role-specific MFA and replay/rate-limit/session-fixation checks.
For audit, consider append-only/WORM or tamper evidence only when justified; prove
transport loss handling and queryability. Policy sources, not templates, set retention.

## Workflow

Read and execute the [shared module caller procedure](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
before domain work. It is the sole owner of original work/package/leaf admission,
live P07/policy checks, immutable obligations, checkpoint publication, cold continuation
and final QA/independent acceptance. Apply this security method inside that procedure:

1. Read the selected requirements and actual threat/data boundaries. Obtain typed
   verified pack fields or explicit advice; no framework is mandatory merely because
   the module knows it. Unresolved applicable policy stops its affected action.
2. Use the capability and checkpoint tables to distinguish design, implementation
   evidence and legal/control applicability. Keep actual review versus planning mode;
   only authorized synthetic/local observations are evidence, not suggested scans.
3. Retain redacted findings, missing observations and the residual-risk owner's
   decision. A reviewer reports and does not fix or silently accept the risk.

## Checkpoint ownership

| Checkpoint | Method and owner | Observable acceptance |
|---|---|---|
| `threat_model_complete` | ThreatModelDrafter | trust boundaries, concrete failure paths, mitigation owners and explicit residual decisions |
| `secrets_inventoried` | SecretsScanReviewer/SecurityAuditor | redacted location/type/owner/scope, actual configured response and missing evidence |
| `auth_flow_locked` | Applicable flow/token reviewers | correct client/grant/profile checks with implemented-versus-planned evidence |
| `compliance_evidence_present` | ComplianceOfficer | every required applicable control has source/version/evidence/outcome; grounded N/A is distinct from unknown |
| `audit_path_verified` | SecurityAuditor | required-event producer-to-sink observation and retention/integrity evidence, or explicitly unverified |

Worked contrast: signature validation on a correctly signed ID token does not
establish API authorization. Trace issuer/audience/type to the decision, then test
the wrong-audience case in an authorized synthetic fixture. A missing SDK setting
is not proof of a leak; a policy brochure is not proof of configured protection.

## Handoff, scoring and recovery

Preserve named threat model, secret-management plan/inventory, auth-flow review,
per-framework coverage/reuse/gap reports, audit-path and incident runbook artifacts.
Bind them to the selected request under safe attempt paths; old `state/sc/` outputs
are selected evidence only, never the newest-file default.

The six rubric dimensions remain Threat model coverage, Mitigations declared,
Secrets inventoried, Auth flow review verdict, Compliance evidence and Audit path verified,
each measured against the observable checkpoint criteria. Scores are advisory; one
mandatory unresolved result blocks regardless of five high scores. DONE requires
required evidence and independent acceptance. DONE_WITH_CONCERNS has advisory
residuals only; missing policy/authority/evidence is BLOCKED or NEEDS_CONTEXT.

Use the shared cold-attempt table. Missing result after start is interrupted;
do not rerun scans, notify owners or rotate keys on inferred permission. Loop with
explicit new input identity and prior evidence links. DeploymentEngineer provides
planning-only recovery/on-call content alongside SecurityAuditor's security response
reasoning; the caller persists it. ReleaseEngineer retains authorized release
execution for a separately authorized invocation, not this planning dispatch.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
Module entry resolves the security expectations bound to the current target context and passes
each sub-capability only its projected clauses (`project` for the mapped package, or the clauses
mapped to it). An unknown deployment target or trust boundary yields `needs-context` and blocks
the dependent design; no live cloud, tenant or environment discovery is implied, and
requirements are never inferred from generic recommendations. When the runtime reports no
patterns, the module is unchanged.

## Integration and dormant hooks

TA/DA supply system/data boundaries, DH consumes response/audit needs, TQ tests the
actual mitigations. No new policy parser, scheduler, phase or release authority.
Optional Brief Forge/audit invocation is explicit, with observed persistence.
No active control is inferred from these opt-in domain files (ADR-0008):

- `hooks/shared/sc-threat-coverage-warn/`
- `hooks/shared/sc-auth-bypass-warn/`
- `hooks/shared/sc-compliance-gap-warn/`

Existing secret/customer-data hooks retain their host-specific registration and
permission boundaries. Optional domain warnings remain unobserved without actual
execution evidence and cannot replace the required review or control outcome.
Never claim a fictional no-production-mutation hook fired.
