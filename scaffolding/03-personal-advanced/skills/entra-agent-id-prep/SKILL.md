---
name: jstack-entra-agent-id-prep
description: Prepare a Microsoft Entra Agent ID submission — identity, capabilities, governance scope.
color: orange
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /entra-agent-id-prep

Drafts a Microsoft Entra Agent ID submission for an agent (custom AI / automation / Copilot extension) that needs identity governance. Output is a structured form draft for the MS Entra Agent governance portal.

Per Layer 2: agents that act on behalf of users / interact with MS Graph / hold credentials / take consequential actions require Entra Agent ID registration.

## When to use

- Custom agent / AI extension that will be deployed against MS Graph or M365 services
- Agent that holds delegated permissions or app-only credentials
- Copilot connector / extension that needs MS identity governance
- Automation that acts as a service principal with broad scope

## When NOT to use

- Read-only agent against public data — no identity governance needed
- One-off script not in production — overkill
- Internal-tooling agent that uses operator's existing credentials — operator identity is sufficient

## Inputs

- Required `--agent-name <name>` — short name for the agent
- Optional `--source <path>` — agent code / design doc
- Optional `--out <path>` — output draft path (default: `~/.jstack/entra/<agent-name>-agent-id-DRAFT.md`)

## Workflow

1. **Structured intake via AskUserQuestion.** Gather:
   - Agent purpose (specific, named)
   - Acting on behalf of (user / app-only / hybrid)
   - Required permissions (MS Graph scopes, M365 service scopes, Azure scopes)
   - Permission justification per scope (least-privilege check)
   - Data accessed (Public / Non-business / Business / Sensitive / etc.)
   - Action capabilities (read / write / delete / send-on-behalf-of)
   - Audit + monitoring (where do agent actions log?)
   - Revocation path (how is the agent disabled if compromised?)
2. **Least-privilege check.** For each requested scope, verify justification is specific (not "general access for flexibility"). Flag broad scopes.
3. **Build draft sections:**
   - **Agent overview**
   - **Identity model** (user-context / app-only / hybrid)
   - **Permission inventory** (table: scope × justification × class accessed × volume)
   - **Action scope** (what the agent can do, explicitly)
   - **Out-of-scope actions** (explicit limits)
   - **Audit trail mechanism** (where logs land, retention)
   - **Monitoring + alerting** (anomaly thresholds, escalation)
   - **Revocation path** (disable, rotate, deprovision)
   - **Risk assessment** (3-5 named risks per the agent governance framework)
   - **Mitigation per risk**
   - **Open questions for Entra reviewer**
4. **Cross-link.** If agent involves AI: cross-link to `/onerai-prep` and `/sensitive-use-report`.
5. **Mark DRAFT.**
6. **Report.**

## Report format

```
Entra Agent ID prep: case-intake-agent

Output: ~/.jstack/entra/case-intake-agent-agent-id-DRAFT.md (4.0 KB)

## Identity model
User context (acting on behalf of authenticated user)

## Permissions requested (4)
| Scope                           | Justification                              | Class       | Volume    |
|---------------------------------|--------------------------------------------|-------------|-----------|
| User.Read                       | Identify caller for personalization         | Public      | per-call  |
| Mail.Send                       | Send case follow-up confirmations           | Business    | ≤5/day    |
| Files.Read.All (delegated)      | Read user-uploaded case attachments         | Business    | per-call  |
| Calendars.ReadWrite (delegated) | Book follow-up meetings                     | Business    | ≤2/week   |

## Least-privilege check
✓ User.Read — minimum needed
✓ Mail.Send — minimum (not Mail.ReadWrite)
✓ Files.Read.All — DELEGATED only, no app-only
⚠ Calendars.ReadWrite — broader than needed; consider Calendars.ReadWrite.Shared or per-event scope

## Audit + monitoring
- All actions log to Azure Monitor with correlation IDs
- Anomaly threshold: > 10 mail-sends/hour triggers alert
- Retention: 90 days

## Revocation path
- App registration: disable via Entra admin
- Per-user revoke: user can revoke consent via account portal
- Emergency rotation: secret rotation in Key Vault, agent restart picks up new

## Risks (4)
1. Token theft → unauthorized access. Mitigation: short-lived tokens, MFA at consent
2. Over-broad calendar scope → inadvertent meeting modification. Mitigation: per-event-id auth check
3. Mail spoofing → trust impact. Mitigation: signed sender, audit on every send
4. Compromised app secret → broad access. Mitigation: Key Vault managed identity

## Cross-references
- AI involvement: yes → see /onerai-prep --feature case-intake
- Sensitive use: see /sensitive-use-report --feature case-intake

## Next steps
1. Refine DRAFT (especially Calendar scope narrowing)
2. Submit to Entra Agent governance portal
3. After approval: implement audit hooks + monitoring
4. Pre-launch: smoke-test revocation path
```

## Compliance integration

- Implements Item 1 of the 7 on-demand compliance items (AGT / agent governance).
- DRAFT only. Operator submits via portal.
- Cross-links with `/onerai-prep` for AI agents and `/sensitive-use-report` for sensitive-use category.
- Audit + monitoring described concretely — vague answers are flagged.

## Voice tier note

`voice: internal`. Entra prep is MS-internal review form.

## Failure modes

- **Scope requested with vague justification:** WARN — Entra reviewer will reject. Require named outcome per scope.
- **App-only credential against highly-privileged scope (e.g. Directory.ReadWrite.All):** require explicit operator confirmation; this is unusual.
- **No revocation path described:** REJECT — Entra requires a documented revoke mechanism.
- **Sensitive-class data + no Privacy review reference:** WARN — recommend `/dpia-prep`.

## Examples

**User-context agent:**
```
> /entra-agent-id-prep --agent-name case-intake-agent
[Intake interview, least-privilege check]
✓ DRAFT generated. 1 scope flagged for narrowing.
```

**App-only service:**
```
> /entra-agent-id-prep --agent-name nightly-analytics-aggregator
[App-only auth, batch volume noted]
✓ DRAFT generated with managed-identity-based credential flow.
```

## See also

- `/compliance-gate` Item 1 — AGT/agent-governance trigger
- `/onerai-prep` — for AI agents
- `/sensitive-use-report` — for sensitive-use category agents
- `/tier-stamp-agents` — for license/precedence (different concern than Entra ID)
- MS Entra Agent governance portal — destination for DRAFT
