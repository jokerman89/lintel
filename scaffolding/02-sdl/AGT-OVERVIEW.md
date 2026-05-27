# AGT Overview — Agent Governance for JStack

Summary of Microsoft Agent Governance (AGT) as it applies to JStack-built agents.

## What AGT covers

The framework governs identities + capabilities + lifecycle for software agents that act on behalf of users or systems. Includes:

1. **Identity** — every agent has a registered identity (Entra Agent ID)
2. **Capabilities** — agents declare what they can do, with named scopes
3. **Authorization** — agents acquire tokens scoped to declared capabilities
4. **Monitoring** — agent actions emit auditable signal
5. **Anomaly response** — unexpected behavior triggers review
6. **Recertification** — periodic confirmation that the agent still does what it claims
7. **Deprovisioning** — clean shutdown of agents that change scope or retire

## When AGT applies to a JStack agent

The agent governance framework applies when an agent:

- Acts on behalf of authenticated users (delegated permissions)
- Holds app-only credentials with broad scope
- Interacts with MS Graph or M365 services
- Makes decisions that affect individuals or business
- Operates in production at scale

It generally does NOT apply when an agent:

- Is invoked by a single operator interactively
- Reads-only without writing or mutating
- Operates only on the operator's local machine
- Has no MS-system integration

## Most JStack agents are NOT AGT-scope

The 40 agents shipped in JStack Phase 4 are mostly READ-ONLY subagents invoked by the main Claude Code session. They:
- Run as the operator (same identity)
- Don't acquire their own tokens
- Don't act outside the operator's session

These do NOT need Entra Agent ID registration.

## When JStack-built agents DO need AGT

A JStack-built agent needs AGT registration when the operator productizes it into:
- A standalone service that processes customer requests
- A Copilot extension or M365 connector
- A Power Automate flow with delegated permissions
- An Azure Function holding a service principal that acts independently

These are typically NOT what JStack agents are. They're what an operator BUILDS using JStack's planning + design skills.

## How JStack supports AGT readiness

- `/entra-agent-id-submit-draft` — drafts the Entra Agent ID submission
- `/agt-tier-stamp` — license-tier classification (orthogonal to AGT identity, but the two pair together)
- `ProvenanceVerifier` agent — implements the audit-trail concept from AGT operational practice
- `OneCSAuditor` agent — checks Item 1 (AGT scope) in compliance gate

## Key concepts (terms appearing across JStack)

- **Entra Agent ID:** The registered identity of an agent in Microsoft Entra
- **Delegated permission:** Agent acts on a user's behalf, scoped to that user's access
- **App-only permission:** Agent acts on its own (service-principal model), scoped to app permissions
- **Conditional access:** Policy that decides whether agent can use its credentials in a given context (network, MFA, risk)
- **Audit trail:** Append-only record of agent actions

## Recertification cadence

Agents should be recertified:
- Quarterly for standard scope
- Monthly for high-scope (broad permissions, sensitive data)
- On every scope change (new permission, new audience)

`/caip-audit` surfaces recertification status when running against an engagement.

## What goes wrong without AGT

Without registered identity + monitoring + revocation:
- Compromised agent operates as legitimate
- Audit unavailable when incident review needed
- Scope creep over time without checkpoint
- Token theft has unbounded blast radius
- Compliance reviewers (Entra, Privacy, Sec) cannot evaluate the agent before launch

## See also

- [REFERENCE-RULES.md](REFERENCE-RULES.md) — Item 5 (AGT framework full) + Item 6 (operational scope)
- `/entra-agent-id-submit-draft` skill — Entra submission DRAFT
- `/agt-tier-stamp` skill — license-tier (paired concern)
- MS Entra Agent governance portal — destination for DRAFTs
