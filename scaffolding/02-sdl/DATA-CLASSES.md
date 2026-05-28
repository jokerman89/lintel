# MS Business Data Classes

The 6-tier classification for data sensitivity. Used throughout Lintel's compliance gates.

## The 6 classes (low → high sensitivity)

### 1. Public

**Definition:** Information already publicly disclosed or intended for public disclosure.

**Examples:**
- Press release content
- Public marketing copy
- Open-source code (MIT/Apache repos)
- Published research papers

**Handling:** No restrictions. Can flow anywhere.

### 2. Non-business

**Definition:** Operational data that doesn't materially affect Microsoft if disclosed.

**Examples:**
- Internal-tool README content
- Generic engineering documentation
- Synthetic test data
- Public conference talk drafts

**Handling:** Default for internal tooling. Loose handling acceptable. Audit not required.

### 3. Business

**Definition:** Information that supports business operations and has limited business impact if disclosed.

**Examples:**
- Internal architecture diagrams
- Engineering decisions and trade-offs
- Customer engagement metadata (sanitized)
- Aggregated metrics not specifically attributable

**Handling:**
- Internal sharing OK
- External sharing requires explicit decision + DSB if cross-organization
- Audit recommended

### 4. Sensitive

**Definition:** Information with significant business impact if disclosed.

**Examples:**
- Customer identities tied to engagement specifics
- Detailed feature roadmaps before public announcement
- Specific customer pain points + responses
- Pre-release product code names
- Employee individual performance data

**Handling:**
- Internal sharing on need-to-know basis
- External sharing requires DSB + explicit operator + reviewer approval
- Audit required
- Lintel: customer-data-block hook prevents commit

### 5. Highly Sensitive

**Definition:** Information with extensive business impact if disclosed.

**Examples:**
- Customer financial data (in customer's hands, not Microsoft's)
- Material non-public information (MNPI)
- Pre-acquisition target information
- Active legal matter content
- Production cryptographic material

**Handling:**
- Need-to-know basis with named individuals
- External sharing: only via explicit legal + DSB + executive approval
- Audit required at every access
- Lintel: not appropriate to handle in Lintel repos at all

### 6. Confidential

**Definition:** Information with extreme business impact if disclosed.

**Examples:**
- Active M&A negotiations
- Customer-specific contracts with cross-boundary licensing
- Active incident response material involving regulatory body
- Material customer financials shared in trust

**Handling:**
- Specifically-named individuals only, often on physically-isolated systems
- No Lintel handling — out of scope

## Class declaration in Lintel repos

Each artifact handling data should have a `compliance/data-class.md` file declaring its highest-class:

```yaml
---
artifact: docs/customer-engagement-summary.md
class: Business
rationale: Engagement metadata with customer placeholder names; no direct customer data
declared_at: 2026-05-27
declared_by: SE-engineer
---
```

## Default class assumptions

- **Internal tooling (no customer surface):** Non-business
- **Internal tooling with engagement metadata:** Business
- **Customer-engagement repos (sanitized):** Business
- **Customer-engagement repos (raw):** Sensitive — should NOT be in Lintel at all

## Class escalation rules

A repo's class is the MAX of all its artifact classes.

If a Sensitive-class artifact is added to a Business-class repo: the repo is now Sensitive. The compliance posture changes:
- Audit becomes mandatory
- External sharing gets stricter
- May require migration to a Sensitive-class-appropriate repo location

## What Lintel supports

Lintel actively supports Public → Business class data. It supports Sensitive class data WITH operator vigilance + opt-in additional controls. It does NOT support Highly Sensitive or Confidential data — those classes belong in dedicated MS systems with different controls.

## Cross-reference

- [HARD-RULES.md](HARD-RULES.md) Rule 1 — no customer data in repo
- [ON-DEMAND-RULES.md](ON-DEMAND-RULES.md) Item 3 — class declaration check
- `/onecs-check` skill — surfaces class declaration requirement
- `compliance/data-class.md` — where the declaration lives per repo
