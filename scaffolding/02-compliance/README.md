# Layer 2 — Compliance

MS-policy-driven, non-negotiable. Lives near the top of the canonical session-start ritual so it runs BEFORE any work begins.

## What lives here

(Pending Phase 6 — currently placeholder. Files below will land during Phase 6 implementation.)

- **`HARD-RULES.md`** — 5 always-on rules with consequences + recovery actions. Read at every session-start.
- **`SESSION-START-CHECK.md`** — the 5-step compliance checklist. ~50 tokens. Highest-leverage budget in the harness.
- **`INLINE-RULES.md`** — during-work rules (≥8-line copyright flag, no OpenAI code in Claude Code, etc.).
- **`ON-DEMAND-RULES.md`** — 7 rules surfaced via `/compliance-check` skill (OneRAI, threat model, DPIA, transparency doc, sensitive-use report, SAST, Entra Agent ID).
- **`REFERENCE-RULES.md`** — 8 documented-only rules (SDL AI subtopics, Agent 365 details, evaluation framework, AAA Policy, quarterly refresh ritual). Operator can elevate any to always-on per project via `~/.jstack/config.yaml`.
- **`ACCOUNT-SETUP.md`** — MS SSO + GovID + SSPA onboarding checklist.
- **`REFRESH-PROCESS.md`** — quarterly MS-policy review cadence.
- **`AGENT-365-INTEGRATION.md`** — Entra Agent ID + Purview + Defender pointers.
- **`DSB-PREP.md`** — Deployment Safety Board prep guide.
- **`PATH-TO-PRODUCTION.md`** — INT → Stab → PPE → Business value → PROD → Post-prod gates.

## Change rate

**MS-policy-driven.** Quarterly review against authoritative MS internal sources (SharePoint Data-Use-Guidance, 1ES Engineering Guidance, RAIS 2026 standard). Refresh when MS-policy updates are announced. Date-stamp each refresh in this layer.

## The "checklist not gate" framing

These rules are an **operator-confirmed checklist**, not automated enforcement. The harness surfaces the 5 always-on items at session-start; the operator confirms each. "No customer data" can't be auto-verified at session-start — it's a check the operator runs against their working set.

The compliance hooks in Layer 4 (`secret-scan`, `data-classification`, etc.) add automated checks for specific failure modes, but Layer 2 is the floor: the rules every session acknowledges before tool calls fire.

## Why this layer exists

These rules are MS-employee-specific. Keeping them as separate layer lets the rest of JStack stay portable across employer contexts while compliance gets priority placement.

## Per-tier operator override

Per `~/.jstack/config.yaml`, operator can:

- Elevate any of the 7 ON-DEMAND rules to always-on (becomes a 6th, 7th... step in the session-start checklist)
- Elevate any of the 8 REFERENCE rules to ON-DEMAND or always-on
- Cannot DEMOTE a HARD-RULE — those 5 are non-negotiable, the harness refuses configs that disable them
