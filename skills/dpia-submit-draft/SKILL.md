---
name: dpia-submit-draft
layer: ms-team
v1_alias: [li-dpia-prep]
description: Prepare a Data Protection Impact Assessment draft — GDPR Article 35, MS Privacy framework.
color: orange
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /dpia-submit-draft

Drafts a Data Protection Impact Assessment (DPIA) for a system that processes personal data. Maps to GDPR Article 35 plus MS-internal Privacy review framework. Output is a structured form draft the operator refines + submits to the MS Privacy team.

## When to use

- New system that processes personal data (any volume, any sensitivity)
- Significant change to existing system: new data fields, new processing, expanded audience
- High-risk processing per GDPR Article 35 (automated decision-making, large-scale special-category, public-area monitoring)
- Periodic re-assessment (typically annual or on architectural change)

## When NOT to use

- System processes only anonymized aggregates — typically DPIA-exempt
- Already-cleared system with no material change — re-prep wastes cycles
- Pure synthetic / test data — no DPIA needed

## Inputs

- Required `--system <name>` — short name for the system
- Optional `--source <path>` — code, design doc, or data flow diagram
- Optional `--out <path>` — output draft path (default: `~/.lintel/dpia/<system>-dpia-DRAFT.md`)
- Optional `--regime <gdpr|ccpa|both>` — privacy regime (default: gdpr; both adds CCPA-specific sections)

## Workflow

1. **Structured intake via AskUserQuestion.** Gather:
   - System purpose (specific, named)
   - Personal data categories processed (name, contact, location, behavioral, special-category, etc.)
   - Data subjects (employees, customers, prospects, minors, vulnerable individuals)
   - Lawful basis per data category (consent, contract, legitimate interest, legal obligation, vital interest, public task)
   - Data flow (collection → storage → processing → output → deletion)
   - Retention per category
   - Cross-border transfers (and SCCs / adequacy decision basis)
   - Automated decision-making impact (Article 22)
   - Special-category data (Article 9) — explicit yes/no per category
2. **Risk evaluation per GDPR Article 35:**
   - High-risk indicators triggered (yes/no per indicator)
   - Likely severity if data subject's rights are breached
   - Likelihood of breach given current controls
   - Combined risk score
3. **Build draft sections:**
   - **System overview**
   - **Personal data inventory** (categories × fields × basis × retention)
   - **Data flow diagram** (textual)
   - **Data subject rights mechanism** (access, rectification, erasure, portability, objection)
   - **Security controls** (encryption, access, monitoring)
   - **Cross-border transfer basis** (if applicable)
   - **Automated decision-making analysis** (if applicable — Article 22 details)
   - **Risk assessment** (per Article 35 indicators)
   - **Mitigation plan** (per risk)
   - **Residual risk** (after mitigation, what remains)
   - **Privacy team consultation status**
   - **Review schedule** (next DPIA refresh)
4. **Compliance scan.** Real personal data in the form BLOCKED (placeholders only).
5. **Mark DRAFT.**
6. **Report.**

## Report format

```
DPIA prep: system=case-intake

Output: ~/.lintel/dpia/case-intake-dpia-DRAFT.md (5.4 KB)
Regime: GDPR
Article 35 high-risk: TRIGGERED (automated decision-making on legal advice)

## Data subjects
- Customers (general population)
- Includes minors: yes (case examples may involve guardian-on-behalf-of-minor)

## Data inventory
- Name (basis: contract, retention: 7yr post-case-close)
- Contact email (basis: contract, retention: 7yr)
- Case description free-text (basis: contract, retention: 7yr, potential special-category if health/legal/financial details disclosed)
- IP address (basis: legitimate interest, retention: 90 days)

## Risk assessment
1. Special-category data inadvertent collection — HIGH severity, MEDIUM likelihood
   Mitigation: input prompt warns, output redaction layer
2. Automated decision impact (Article 22) — case routing decisions
   Mitigation: human review threshold, override mechanism
3. Cross-border transfer (EU → US compute) — SCCs in place, adequacy uncertain
   Mitigation: SCCs + Microsoft Customer Data EU Boundary if applicable

## Residual risk
MEDIUM. Recommend Privacy team consultation before launch.

## Next steps
1. Refine DRAFT (especially special-category mitigation detail)
2. Schedule Privacy team consultation
3. Submit to MS Privacy portal
4. Implement mitigations BEFORE launch
```

## Compliance integration

- Implements Item 6 of the 7 on-demand compliance items.
- Article 35 high-risk indicators triggered: REQUIRES Privacy team consultation. Skill surfaces this; operator schedules.
- Special-category data (Article 9): additional explicit basis required per category.
- Real personal data in form body → BLOCK (description-level only).
- For customer-facing AI: cross-link to `/onerai-submit-draft` (DPIA + One RAI together for AI processing personal data).

## Voice tier note

`voice: internal`. DPIA is MS-internal privacy review form.

## Failure modes

- **Lawful basis unclear:** require operator to pick one per category. Default to LEGITIMATE INTEREST is suspicious — surface "are you sure?" gate.
- **Retention "indefinite":** REJECT — Article 5(e) requires bounded retention. Refuse to finalize.
- **Special-category data + only one mitigation:** WARN — typically requires 2+ layers.
- **Article 22 triggered + no human-review path:** REJECT — automated decisions affecting individuals require Article 22(3) safeguards.
- **Operator skips a section:** form is INCOMPLETE — refuse to write final DRAFT; allow incomplete-draft save for iteration.

## Examples

**New system DPIA:**
```
> /dpia-submit-draft --system case-intake --source docs/design/case-intake-flow.md
[Intake interview, risk evaluation]
✓ DRAFT generated. Article 35 HIGH-RISK triggered — Privacy consultation required.
```

**Bi-regime (GDPR + CCPA):**
```
> /dpia-submit-draft --system marketing-segmentation --regime both
[Adds CCPA opt-out / sale-of-data sections]
✓ DRAFT covers GDPR + CCPA.
```

## See also

- `/onecs-check` Item 6 — surfaces DPIA requirement
- `/onerai-submit-draft` — for AI processing personal data
- `/dsb-submit-draft` — for personal data sharing scenarios
- `/rais-transparency-note` — customer-facing privacy notice complementary to DPIA
- MS Privacy portal — destination for DRAFT
