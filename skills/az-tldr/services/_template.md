---
service: <Service Display Name>
service_id: <kebab-case-id>
category: networking | compute | data | ai-ml | security | integration | observability | other
caf_pillars: [security, reliability, performance, cost, operational-excellence]
waf_pillars: [security, reliability, performance, cost, operational-excellence]
as_of: YYYY-MM-DD
refresh_cadence_days: 90
subagent_mapping:
  primary: AzureArchitect
  per_section:
    "4": AzureArchitect          # frameworks
    "13": AzureArchitect          # enterprise meaning
    "14": CostAnalyzer            # commercial
    "15": AzureArchitect          # implementation flow
  secondary_conditional:
    KeyVaultAuditor: [private-peering, secrets-touching, ipsec-overlay]
    BicepReviewer: [iac-discussion, deployment-design]
    SecurityAuditor: [public-tier, sensitive-data-flow]
---

# <Service Display Name> — TLDR

> Template — replace placeholders. Each section's depth target in parens.

## §1 What it is (~50 words)

[One paragraph. Plain English. What is this service AT THE CORE? No jargon explosion. What core abstraction does it embody?]

## §2 What it does (~80 words)

[How does the abstraction become operationally useful? Two-three concrete things the service DOES for the customer.]

## §3 How it's used (~120 words, 3-4 named patterns)

[Common deployment patterns. Name each pattern: e.g., "Hub-spoke with central NVA", "Private peering for on-prem", "Multi-region active/active". One paragraph per.]

## §4 Frameworks it lives in (~150 words)

- **CAF (Cloud Adoption Framework):** [Where in CAF: Strategy / Plan / Ready / Adopt / Govern / Manage / Secure? What specific guidance?]
- **WAF (Well-Architected Framework):** [Per pillar applicability: security / reliability / performance / cost / operational-excellence. Which pillars dominate?]
- **Azure landing zones (ALZ):** [What's the canonical ALZ pattern for this service? Sub-design considerations?]
- **Zero Trust:** [How does this service participate in/enable/complicate Zero Trust posture?]
- **Other relevant frameworks:** [If MITRE, NIST, ISO, etc. — note alignment]

## §5 Top 10 things to know (~300 words, numbered)

[10 hard-truth bullets. Things SE must know cold. Not marketing claims — real operational truths. Examples: "SKU choice locks redundancy mode irreversibly", "BGP attributes are visible to customer routers", "Connectivity SLA is per-circuit not per-connection".]

1. <Hard truth 1>
2. <Hard truth 2>
...
10. <Hard truth 10>

## §6 Known pitfalls (~300 words, numbered top 10)

[10 real fallgropar SE has seen or curated from MS field reports. Each: pitfall + why it bites + how to avoid. Example: "Single-circuit redundancy assumption — bites because provider outage cascades, avoid via dual-circuit design or ExpressRoute Metro."]

1. **<Pitfall name>** — <why bites> — <how to avoid>
...
10. <Pitfall>

## §7 What's required of customer (~200 words)

[Customer-side prerequisites for this service to work. Categorize:
- Hardware (e.g., specific router models, MACsec support)
- Software (e.g., BGP capability, peering authorization)
- Operational (e.g., IT-change-window, customer NOC)
- Commercial (e.g., provider relationship, billing arrangement)
- Compliance (e.g., audit requirements, residency)
]

## §8 10 typical customer questions (~400 words)

[Q&A pairs. Real questions from customer architects + concise answers. Format: Q + 2-4 sentence answer. Cover technical + commercial + operational.]

**Q1: <Question>**
A: <Answer>

...

**Q10: <Question>**
A: <Answer>

## §9 Latest greatest (~150 words, dated)

[As of <as_of> date: notable recent GA/preview features. Pricing changes. SKU expansions. New regions. Format: bullet per item with date + 1-line description + Microsoft Learn URL.]

- **<feature name>** (GA: <date>): <one-line description> — [MS Learn](URL)
- **<feature name>** (Preview: <date>): <description> — [URL]
...

## §10 Read further (links, not content)

**Microsoft Learn:**
- Overview: [URL]
- Deep technical: [URL]
- Reference architectures: [URL]
- Cost calculator (if applicable): [URL]

**Microsoft architecture diagrams:**
- [URL to learn.microsoft.com architecture page]
- [URL to architecture center for this service]

**Reference architectures (ALZ):**
- [Azure Landing Zones canonical pattern URL]

**Known expert voices (independent):**
- <Name> (<blog URL>): <one-line on their expertise>
- John Savill (azurearchitectures.com): <if applicable, what they cover>
- <Microsoft FTE blog>: [URL]

[Avoid linking to outdated or low-quality sources. Default to MS Learn + 2-3 named experts.]

## §11 ELI5 explanation (~100 words)

[Plain English a non-technical decision-maker would understand. No tech terms. Analogy if helpful. For ExpressRoute: "Think of it like installing a dedicated phone line between your office and Microsoft, instead of yelling across an open room."]

## §12 Level-500 explanation (~250 words)

[Deep technical for customer's senior architect. Protocol-level details. Internals. Performance characteristics. Edge cases. For ExpressRoute: BGP attributes, MACsec internals, MSEE architecture, FastPath data plane.]

## §13 What it means for enterprise customer (~250 words)

[Strategic / outcomes language. Not features — business meaning. Cost predictability, sovereign-cloud connectivity, hybrid posture, audit-readiness, vendor-lock-in (or not). What does buying this signal about customer's posture? Why does CIO care?]

## §14 Commercial perspective (~200 words)

- **Cost model:** [Per-unit pricing. Recurring vs one-time. What's metered vs flat.]
- **Indicative pricing:** [Ranges in $/mo for typical SKUs. As-of-date.]
- **POC viability:** [Yes / No / With-caveats. Why?]
- **First commercial commitment threshold:** [Typical entry-point dollar value]
- **Cost-trap warnings:** [Things that surprise customers in month 2 bill]

## §15 Implementation flow — first meeting → CSA handover (~400 words)

[Phased flow. Per phase: who's involved + what's produced + when SE hands off.]

1. **First meeting (SE).** [Discovery topics. Customer pain to surface.]
2. **Discovery + scoping (SE + customer arch).** [Architecture questions. Bandwidth/scale forecast. Compliance constraints.]
3. **Design proposal (SE + customer arch board).** [Topology sketch. SKU selection. Redundancy strategy.]
4. **Pre-sales technical close (SE).** [Quote validation. Provider selection if applicable.]
5. **CSA handover.** [Implementation timeline. IaC drop-in references (Bicep/AVM modules). Cutover plan. Operator handoff doc.]

## §16 (Optional) Service-specific deep-dive sections

[If service has unique aspects warranting extra depth, add §16+ here. E.g., for ExpressRoute: BGP-attribute deep dive, FastPath internals. For Azure OpenAI: model catalog deep dive, content filtering tiers. Keep concise.]

---

**Curation notes (for future maintainers):**

- as_of field reflects manual review against Microsoft Learn
- Re-verify §5 + §6 + §9 every 90 days minimum
- Update §9 latest-greatest with each major GA announcement
- If §10 links rot, fix immediately (broken links are voice-gate failures)
- Customer-question §8 evolves with engagement experience — promote durable patterns
