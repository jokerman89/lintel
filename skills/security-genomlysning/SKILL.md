---
name: security-genomlysning
layer: ms-team
description: ⚠ TEMPLATE ONLY — Security + risk genomlysning (operator-request 5.5 REPLACED per L-001). Scaffolding-slot, posture-report genereras vid invokation.
color: blue
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
license_note: produces operator-internal output; never customer-share without explicit gate
---

## ⚠ TEMPLATE ONLY — Slot for security + risk genomlysning

This skill är **scaffolding slot** per L-001. Frontmatter + agent-mapping exist; posture-report-content AI-genereras vid invokation från current code + threat-model state.

## Why a slot exists

Operator-request 5.5: "En real djup review av där du står — security + risk. Reuse security agents + compliance agents. Producerar posture-report."

Posture innehåll ändras kontinuerligt — dependencies update, threat-landscape shift, compliance-versions evolve. Pre-baking = rosta direkt. Operator-AI generates fresh per invocation, leveragerar existing security agent catalog.

## At-invocation contract

Operator invokes med:
- `/li:security-genomlysning [--scope <code|infra|all>]` (default: all)
- `/li:security-genomlysning --since <ref>` (review only changes since git ref)
- `/li:security-genomlysning --quick` (high-confidence agent dispatch only, skip lower-confidence agents)

AI at invocation:
1. Scans code + infra för security-relevant patterns (auth, crypto, network-egress, data-handling)
2. Dispatches relevant security agents (per agent-mapping below)
3. Aggregates findings into posture-report:
   - Top 5 critical (P0-P1)
   - Top 5 high (P2)
   - Medium-low (summarized)
   - Compliance-state per applicable standard
4. Cross-references mot operator's WorkProfile compliance tier
5. Surface report med next-action recommendations per finding

## Agent dispatch (vid invokation)

Per backlog 5.5 — reuses existing security + compliance agents:
- **ThreatModelDrafter** — primary (STRIDE / threat-model artifact)
- **SBOMAuditor** — primary (supply-chain visibility)
- **SecurityAuditor** — primary (general OWASP + AppSec)
- **PrivacyBoundaryAudit** — primary (data-flow + boundary analysis)
- **OAuthFlowReviewer** — conditional (if OAuth/OIDC code present)
- **JWTSecurityReviewer** — conditional (if JWT handling)
- **EncryptionAtRestReviewer** — conditional (storage code present)
- **GDPRReviewer** — conditional (EU customer data)
- **HIPAAReviewer** — conditional (PHI handling)

## Posture-report structure (AI-generated vid invokation)

```markdown
# Security Posture — <timestamp>

## Executive summary
- N critical, N high, N medium, N low findings
- Compliance state: <X/Y standards green>
- Notable trends since last review: <delta>

## Critical findings (P0-P1)
[per finding: agent-source, file:line, why critical, recommended action]

## High findings (P2)
[same format]

## Medium/Low (summarized)
[counts + categories]

## Compliance state
| Standard | State | Evidence |
|---|---|---|
| OWASP Top 10 | <green/yellow/red> | <link> |
| GDPR | ... | ... |
| ... | ... | ... |

## Next actions (prioritized)
1. [action] — addresses [finding(s)]
2. ...
```

## Voice tier

`voice: internal` default. Security findings stannar operator-internal som default. Customer-share kräver dedicated `/li:rais-customer-voice-check` + threat-model-redaction pass.

## Status protocol

- **DONE** — posture-report rendered + N agents dispatched + findings categorized
- **DONE_WITH_CONCERNS** — rendered men some agents failed (e.g., tool missing) — report flags partial coverage
- **BLOCKED** — no readable code at cwd
- **NEEDS_CONTEXT** — invocation utan scope när repo har multiple sub-projects

## When to promote from slot till curated

Om operator finds att specific posture-pattern återkommer (e.g., MS-AppSec-bar för internal tools), promote till SKILL.md body. Until then: AI genererar fresh.

## Recommended next steps

After invocation:
- Critical findings → P0 fix via `/li:cycle --mode hotfix`
- Compliance gaps → `/li:compliance-gate` aggregate gate run
- High-finding cluster → consider `/li:threat-model-drafter` deep-dive
- For follow-up: `/li:security-genomlysning --since <last-review-ref>` för delta-view
