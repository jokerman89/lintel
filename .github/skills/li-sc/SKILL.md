---
name: li-sc
description: Use for security and compliance depth — threat models, auth flows, secret management, dependency-security audits, compliance evidence, and incident runbooks. Reach for it when a change has a security or regulatory surface. Runs full, loop, or single-capability, dispatching to the security agents and scoring against a rubric.
---

> **Lintel on GitHub Copilot.** Generated from `skills/sc/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/sc/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/sc/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Security and compliance

Read [security decision methods](../../../skills/sc/references/decision-methods.md): implementation
evidence, legal/policy applicability and unknowns are different. Produce threats,
auth/secret/audit designs, compliance coverage and incident playbooks, not a blanket
certification. The host's permission and actual policy remain authoritative.

`/li-sc full` covers the checkpoints below. `/li-sc loop` revisits explicitly saved evidence;
`/li-sc <capability>` or `/li-sc single --action <capability>` limits the assignment. Preserve
read-only review versus authorized implementation. No scan of live services,
customer data, credential use/rotation or incident message follows from invocation.

## Sub-capability dispatch

| Capability | Dispatches to (agents) | Produces | Decisions and checks |
|---|---|---|---|
| `threat-model` | ThreatModelDrafter, then distinct SecurityAuditor review | STRIDE by boundary, mitigations and residual-risk decisions | actual assets/actors; platform-covered threats need deployment evidence, not omission |
| `secret-management` | SecurityAuditor + SecretsScanReviewer; SBOMAuditor for dependency-shipped defaults | redacted inventory, owner, storage, response/rotation and default-credential triage | no values or live credential tests; cadence/provider comes from applicable risk/policy |
| `auth-flow` | OAuthFlowReviewer for OAuth/OIDC; JWTSecurityReviewer for JWT internals; SecurityAuditor for other auth | flow diagrams, token/claim/scopes/revocation checks | one protocol is not another; grant/client-specific checks, exact library/provider versions |
| `compliance-evidence` | ComplianceOfficer per applicable framework; Architect for system boundary | technical/procedural evidence, cross-framework reuse and gap map | source/edition/effective date/actor/scope, no default SOC2/GDPR or score-based certification |
| `audit-path` | Architect design + SecurityAuditor review | event/integrity/transport/retention design and checks | actor/action/target/outcome/context; UTC timestamp and ordering mechanism distinct; no blanket seven years |
| `dependency-security` | DependencyAuditor + SBOMAuditor | ecosystem SCA and artifact-scoped SPDX/CycloneDX evidence | actual advisory range/reachability and license use/distribution policy; unavailable feed remains unverified |
| `incident-runbook` | SecurityAuditor + ReleaseEngineer planning-only | detection, containment, eradication, recovery, escalation and postmortem | selected threat/observability evidence, named on-call/live-action authority; no real containment or notifications |

For auth, retain login/refresh/revoke/step-up diagrams, justified lifetimes, refresh/
revocation paths, role-specific MFA and replay/rate-limit/session-fixation checks.
For audit, consider append-only/WORM or tamper evidence only when justified; prove
transport loss handling and queryability. Policy sources, not templates, set retention.

## Workflow

1. Use [shared module admission](../../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure):
   original work/package/leaves, actual `work_context`/`workflow_inspect`, live P07
   reference and actual required-policy bridge. Unresolved policy stops its action.
2. Read full selected requirements and threat/data boundaries. Obtain typed verified
   pack fields or explicit advisory inputs, never grep personal preferences or execute
   a manifest. No framework is mandatory merely because the module knows it.
3. Prepare immutable P05 QA obligations and explicit domain checkpoints/receivers/
   artifact paths with original file states. Select actual review versus planning mode.
4. Record start; perform authorized synthetic/local observations or design work;
   persist redacted evidence and result. A reviewer reports and does not fix.
5. After artifacts exist, externally prepare the final P05 context, fresh domain
   verify/summary and actual QA, then independent spec and quality. All mandatory
   unknown/error/failure stays visible. Do not silently accept residual risk.

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
explicit new input identity and prior evidence links. ReleaseEngineer retains
authorized release execution for a separately authorized invocation; planning-only
here is a receiver mode, not deletion of that role capability.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
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
permission boundaries. Never claim a fictional no-production-mutation hook fired.
