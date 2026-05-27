# REFERENCE RULES — 8 background docs

These documents are background context. Read on demand. NOT actively enforced.

Where the 5 always-on rules + 7 on-demand items operationalize policy, these 8 reference docs are the authoritative source.

## 1. SDL — Security Development Lifecycle

**Scope:** Engineering practices for secure development across the product lifecycle (threat modeling, security review, vulnerability handling, response).

**MS-internal source:** SDL policy + handbook (internal SharePoint).

**Relevance for JStack:**
- Influences `SecurityAuditor` agent's audit framing
- Threat modeling concepts surface in `/office-hours` design docs
- Vulnerability classes inform `no-secrets-in-edit` + `secret-scan-block` patterns

**When to read:** Pre-launch security review on customer-bearing system.

## 2. RAIS 2026 — Responsible AI Standard

**Scope:** Microsoft's Responsible AI principles + Standard (latest version: RAIS 2026). Six principles: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, Accountability.

**MS-internal source:** RAIS 2026 standard + handbook.

**Relevance for JStack:**
- The six principles structure `/rais-impact-assessment`
- Sensitive Uses categories from RAIS feed `/rais-sensitive-use`
- One RAI submission process (`/onerai-submit-draft`) maps to RAIS clearance

**When to read:** Any customer-facing AI feature design + launch.

## 3. 1CS — One Commercial Software

**Scope:** Commercial commitments to customers regarding software behavior, support, lifecycle.

**MS-internal source:** 1CS framework docs.

**Relevance for JStack:**
- Customer-bearing deliverables must align with 1CS commitments
- Lifecycle decisions (deprecation, sunsetting) follow 1CS process

**When to read:** Pre-launch on a deliverable that will become a customer commitment.

## 4. MS Privacy Commitments

**Scope:** Microsoft's privacy commitments (GDPR, CCPA, regional regulations) + internal Privacy framework.

**MS-internal source:** MS Privacy team docs + Privacy review portal.

**Relevance for JStack:**
- DPIA process (`/dpia-submit-draft`) maps to Privacy framework
- Personal data classifications + special-category handling
- Cross-border transfer mechanisms (SCCs, adequacy decisions, EU Boundary)

**When to read:** Any system processing personal data.

## 5. AGT — Agent Governance Framework (full)

**Scope:** Microsoft's framework for governing AI agents and automation: identity, capability declaration, monitoring, revocation, lifecycle.

**MS-internal source:** AGT framework docs + Entra Agent ID portal.

**Relevance for JStack:**
- `/entra-agent-id-submit-draft` produces submissions for this framework
- `tier-stamp-agents` skill operationalizes a piece of AGT (license-tier classification)
- 5-level precedence model in JStack adapts AGT's identity-precedence rules

**When to read:** Designing a new agent / Copilot extension / automation.

## 6. Agent Governance Operational Scope

**Scope:** The day-to-day operational practice of agent governance: audit, monitoring, anomaly response, recertification, deprovisioning.

**Distinct from AGT framework:** AGT is the policy; this is the operational layer.

**Relevance for JStack:**
- Audit logs (`~/.jstack/audit/`) implement operational-side traceability
- `ProvenanceVerifier` agent uses this scope's concepts (forgery detection, chain integrity)
- Periodic agent recertification surfaces in `/caip-audit`

**When to read:** Operating a deployed agent at scale; incident response.

## 7. DSB Process Detail

**Scope:** The full Data Sharing Board process: submission, review criteria, approval conditions, exceptions, appeals.

**Distinct from `/dsb-submit-draft`:** the skill produces a submission; this doc explains what reviewers look for.

**Relevance for JStack:**
- Informs `/dsb-submit-draft`'s field set + review-perspective pushbacks
- `RAIReviewer` agent surfaces DSB-relevant flags

**When to read:** Before submitting any data share; when reviewers push back.

## 8. Trailblazer / "Our Voice" Voice Guide (full)

**Scope:** Microsoft "Our Voice" framework — 3 modes (Reveal / Inspire / Provoke), 12 techniques, six ground rules, three brand-value words (Kind, Daring, Deep), CELA restrictions, examples.

**Internal source:** [Microsoft_ourVoice_guidelines.pdf](https://microsoft-my.sharepoint-df.com/personal/shawndeng_microsoft_com/VivaEngage/Attachments/Storyline/Microsoft_ourVoice_guidelines.pdf) (March 2023, Confidential).

**Distinct from `OurVoice.md` in this repo:** that file is the operationalized summary; this reference points at the canonical source.

**Relevance for JStack:**
- OurVoice-corpus.md draws verdicts from this source
- OurVoice-test.md applies this rubric
- All trailblazer-voice skills + the TrailblazerVoiceCritic agent reference this source

**When to read:** First time understanding the voice framework; when corpus calibration disagrees with intuition (the canonical source is the tiebreaker).

## How to access reference docs

- For 1-4, 7: MS-internal SharePoint or Confluence — operator's MS account + appropriate group membership required.
- For 5-6: Entra portal docs + AGT framework site.
- For 8: SharePoint link above (or its successor; verify the canonical link if it moves).

## Why "reference-only" vs enforced

These docs are too broad + nuanced to encode as patterns or checklists. They require domain expertise to interpret in context. JStack indexes them; operator reads + interprets.

## See also

- [COMPLIANCE-OVERVIEW.md](COMPLIANCE-OVERVIEW.md) — the 5/7/8 tier overview
- [HARD-RULES.md](HARD-RULES.md) — the 5 always-on
- [ON-DEMAND-RULES.md](ON-DEMAND-RULES.md) — the 7 on-demand
- `/help --rules reference` — surfaces this list
