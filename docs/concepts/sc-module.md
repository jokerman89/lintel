# SC: security and compliance

SC preserves threats, auth, secret handling, dependency evidence, applicable control
coverage, audit paths and incident runbooks. Use the [canonical skill](../../skills/sc/SKILL.md),
[security methods](../../skills/sc/references/decision-methods.md) and shared
[engineering-module contract](engineering-modules.md).

## Retained capabilities

| Capability | Receiver and output |
|---|---|
| threat-model | ThreatModelDrafter maps assets/boundaries/STRIDE; separate SecurityAuditor reviews |
| secret-management | SecurityAuditor/SecretsScanReviewer produce redacted owner/response inventory; SBOMAuditor checks dependency-shipped defaults |
| auth-flow | OAuthFlowReviewer handles grant/client flow; JWTSecurityReviewer handles JWT profile; SecurityAuditor covers other auth |
| compliance-evidence | ComplianceOfficer maps applicable frameworks, technical/procedural evidence and reuse/gaps |
| audit-path | Architect designs and SecurityAuditor reviews required event/integrity/transport/retention evidence |
| dependency-security | DependencyAuditor interprets advisories/use; SBOMAuditor binds shipped inventory/provenance |
| incident-runbook | SecurityAuditor + ReleaseEngineer planning-only design detection/containment/recovery/escalation |

Full checkpoint order remains `threat_model_complete`, `secrets_inventoried`,
`auth_flow_locked`, `compliance_evidence_present`, `audit_path_verified`. A direct
capability stays narrow. Actual authorized release execution remains a separate
ReleaseEngineer mode, not an action performed by incident planning.

## Apply the right evidence

Trace input -> trust boundary -> sensitive sink before claiming an implementation
finding. A dangerous-looking call is not an exploit proof; an undocumented platform
control is not a verified defense. Test only authorized synthetic inputs and redact
secrets. Do not use credentials to establish whether a scan finding is genuine.

A valid JWT signature is not sufficient audience/type authorization. OAuth's native,
service and browser flows have different checks. Exact sources/library versions
and actual configured behavior matter, not a universal token lifetime/cache interval.

Control applicability requires source, edition/date, jurisdiction, actor and scope.
No default SOC2/GDPR, vendor requirement or seven-year audit retention. A policy
document cannot prove a control operated; one framework's evidence may not fit
another's period/scope. Mandatory unknown/error/failure stays blocked, grounded N/A
and advisory preferences stay distinct. The result is not legal certification.

## Handoff and recovery

Retain threat/mitigation decisions, auth diagrams, redacted inventory, per-framework
coverage/reuse/gaps and runbooks as actual named artifacts. Fresh profile/work/result
verification and external P05 preparation/QA precede real independent spec/quality.
Reviewers report rather than repair. No fictitious actor, score or hook log clears work.

A missing checkpoint result is interrupted; don't replay a scan with side effects,
notify customers or rotate secrets without exact authority. Loop with new input
identity and preserve old evidence. Six advisory dimensions remain threat coverage,
mitigations, secrets, auth, controls and audit path, never average-based clearance.

Opt-in `sc-threat-coverage-warn`, `sc-auth-bypass-warn`, `sc-compliance-gap-warn`
remain dormant unless separately registered. Existing secret/customer-data hooks
retain their actual host boundaries; no nonexistent production-mutation hook is claimed.
