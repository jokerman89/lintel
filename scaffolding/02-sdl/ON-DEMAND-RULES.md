# ON-DEMAND RULES — 7 operator-checklist items

These run via `/onecs-check` skill (operator-triggered). Surface checklist; operator confirms each item with judgment.

Per A4: operator-confirmed checklist, NOT automated enforcement. Claude surfaces what to check; the operator's domain knowledge decides the call.

## Item 1: AGT / Agent governance

**The check:** Does the work introduce a new agent (custom AI, automation, Copilot extension) that needs Microsoft Entra Agent ID registration?

**Triggers AGT requirement when:**
- Agent acts on behalf of users (delegated permissions)
- Agent holds app-only credentials with broad scope
- Agent interacts with MS Graph or M365 services
- Agent makes consequential decisions

**Skill to run:** `/entra-agent-id-submit-draft`

**Reviewer:** MS Entra Agent governance team

## Item 2: First-party-first explicit check

**The check:** Has the explicit first-party-first scan been run on the current scope?

**When required:** Pre-ship of any work that touches dependency manifests, integrations, or external services.

**Skill to run:** `/first-party-check`

**Documents acceptance:** commit message / ADR / `/learn` entry

## Item 3: MS Business Data class declaration

**The check:** Each artifact handling data has its data class explicitly declared.

**MS Business Data classes** (highest to lowest sensitivity):
1. Confidential (extreme business impact)
2. Highly Sensitive (extensive business impact)
3. Sensitive (significant business impact)
4. Business (limited business impact)
5. Non-business (operational, no harm if disclosed)
6. Public (publicly disclosable)

**See:** [DATA-CLASSES.md](DATA-CLASSES.md) for class boundaries + examples.

**When required:** Any new system handling data; significant scope change to existing.

**Where declared:** `compliance/data-class.md` in the artifact's repo.

**Default for internal tools:** Non-business (operational data, no harm if disclosed). Operator escalates if scope is higher.

## Item 4: Sensitive-use case classification

**The check:** Does this fit a Sensitive Uses category per MS Responsible AI?

**Categories** (see `~/.lintel/sensitive-uses.yaml` for operator-extendable list):
- Decisions consequential for individuals (legal, financial, health, employment)
- Inferring emotional or psychological state
- Biometric identification / categorization
- Public safety / law enforcement
- Critical infrastructure
- Education access / outcomes
- Welfare benefits eligibility
- Migration / asylum / border processes
- AI used by or about minors
- AI in elections / democratic processes
- Generative content at scale without provenance

**When required:** Any customer-facing AI feature.

**Skill to run:** `/rais-sensitive-use`

**Reviewer:** MS RAI Sensitive Uses team (when triggered)

## Item 5: Data Sharing Board (DSB)

**The check:** Does this share data outside its intended audience?

**Triggers DSB requirement when:**
- Sharing with new third party (partner, vendor, customer)
- Exporting to new geography
- Exposing to new audience class (internal → public)
- Significantly changing scope of existing share

**Skill to run:** `/dsb-submit-draft`

**Reviewer:** MS DSB

## Item 6: Data Protection Impact Assessment (DPIA)

**The check:** Does the system process personal data?

**Triggers DPIA requirement when:**
- Any system processing personal data (regardless of volume)
- Significant change to existing system: new fields, new processing, expanded audience
- High-risk processing per GDPR Article 35 (automated decision-making, large-scale special-category, public-area monitoring)

**Skill to run:** `/dpia-submit-draft`

**Reviewer:** MS Privacy team

## Item 7: Transparency note

**The check:** Does this customer-facing output need a transparency note disclosing AI usage + capabilities + limitations?

**Required for:**
- Customer-facing AI features (including pilots, betas)
- Public-facing AI surface (website, in-product, doc site)
- Significant change to existing AI feature

**Skill to run:** `/rais-transparency-note`

**Format:** MS Transparency Note template

## How `/onecs-check` orchestrates these

The skill walks each item in sequence:
1. Asks "applies / not applies / N/A?"
2. If applies: asks "PASS / NEEDS_ACTION?"
3. If NEEDS_ACTION: names the follow-up skill
4. Aggregates verdict

Operator confirms the aggregate. Audit-logged to `~/.lintel/audit/onecs-check.jsonl`.

## When to run /onecs-check

- Before shipping customer-bearing artifact
- Before production deploy
- Before sharing externally (customer, partner, public)
- After scope-change that may introduce new compliance surface
- Periodic spot-check (weekly during active engagement)

## See also

- [HARD-RULES.md](HARD-RULES.md) — 5 always-on
- [REFERENCE-RULES.md](REFERENCE-RULES.md) — 8 reference docs (full text of frameworks)
- `/onecs-check` skill — orchestrates this checklist
- `OneCSAuditor` agent — automated audit pass
