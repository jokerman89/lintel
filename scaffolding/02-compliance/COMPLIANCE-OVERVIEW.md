# JStack Compliance Overview

Layer 2 of the JStack architecture: MS compliance posture. Tiered as 5/7/8 per A4 design decision.

## The three tiers

### Tier 1 — 5 always-on rules

Run automatically at session start. Cannot be disabled. Surface inline if violated.

See [HARD-RULES.md](HARD-RULES.md).

1. No customer data in repo, prompts, or artifacts (ever)
2. No secrets, credentials, tokens in committed content or prompts
3. Production-mutation operations require explicit per-call authorization
4. MS SSO only (zero retention, feedback off, no Claude.ai workbench)
5. First-party-first: prefer MS solutions before third-party

### Tier 2 — 7 on-demand items

Run via `/compliance-gate` skill (operator-triggered). Surface checklist; operator confirms each item.

See [ON-DEMAND-RULES.md](ON-DEMAND-RULES.md).

1. AGT / Agent governance (Entra Agent ID prep)
2. First-party-first explicit check
3. MS Business Data class declaration per artifact
4. Sensitive-use case classification
5. Data Sharing Board (DSB) prep
6. Data Protection Impact Assessment (DPIA)
7. Transparency note for customer-facing AI

### Tier 3 — 8 reference-only docs

Background context. Read on demand. Not actively enforced.

See [REFERENCE-RULES.md](REFERENCE-RULES.md).

Includes: SDL principles, RAIS 2026 framework details, 1CS commitments, MS Privacy commitments, full AGT framework, full Agent Governance scope, DSB process detail, full Trailblazer voice guide.

## Why tiered?

Per the design A4 decision: an honest compliance posture is OPERATOR-CONFIRMED CHECKLIST, not automated enforcement. Claude can surface what to check; the operator confirms each item with judgment.

The 5/7/8 split:
- **5 always-on** — non-negotiable, automated detection where pattern-matching is reliable
- **7 on-demand** — operator-judgment items that require domain context, surfaced via checklist
- **8 reference** — background reading, indexed for retrieval, not actively triggered

## How JStack enforces (and what JStack does NOT)

**JStack DOES:**
- Surface patterns at session start (5 always-on)
- Provide operator-driven checklist (7 on-demand via `/compliance-gate`)
- Index reference docs for retrieval (8 reference)
- Audit-log compliance decisions to `~/.jstack/audit/`
- Provide skills to prepare submission DRAFTs (DSB, DPIA, One RAI, Sensitive Use, Transparency Note)

**JStack does NOT:**
- Auto-submit any compliance form (operator does that via MS portals)
- Replace MS RAI / Privacy / DSB review (skills produce DRAFTs; reviewers approve)
- Replace operator judgment (the 7 are CHECKLIST items, not gates)
- Replace server-side enforcement (e.g. branch protection still needed)

## Implementation layers

JStack compliance lives in:
- **5 always-on:** detection runs inline in skills + as opt-in hooks (`02-compliance/hooks/`)
- **7 on-demand:** orchestrated by `/compliance-gate` skill
- **8 reference:** documents in this directory, accessible via `/help --rules reference`

Hooks are OPT-IN. Operator manually symlinks chosen hooks into `~/.claude/hooks/`. See `02-compliance/hooks/README.md`.

## Cross-references

- `LAYERS.md` — JStack architecture overview
- `/compliance-gate` skill — runs the 7 on-demand items
- `/health` skill — verifies compliance hook activation state
- `MSComplianceAuditor` agent — automated 5+7 audit pass
