---
name: az-discover-presale
layer: ms-team
description: ⚠ TEMPLATE ONLY — Presale Azure discovery skill (operator-request 5.4 REPLACED per L-001). Scaffolding-slot, content genereras vid invokation.
color: blue
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
license_note: produces customer-bound output if --customer-share flag set
---

## ⚠ TEMPLATE ONLY — Slot for presale Azure discovery

This skill is a **scaffolding slot** per L-001 (Lintel = scaffolding, not curated content). The frontmatter + agent-mapping entry exist; the workflow body är AI-generated vid invokation från customer environment context + operator AI:s aktuella förståelse av Azure-tjänste-katalog.

## Why a slot exists

Operator-request 5.4: "Customer has all this in their environment — where's money on the table that adds value given their direction?" Upsell-discovery skill: reads described/warmed customer env, maps to Azure services that extend their direction, surface upsell-opportunities med SE framing (outcome-led, ej pushy).

Pre-baking detta = L-001-violation. Azure-tjänste-katalog ändras månadsvis (new services, deprecated SKUs, pricing-shifts). Upsell-rekommendationer kräver fresh-AI-reasoning per customer-engagement. Slot pattern = scaffolding + agent-mapping; AI genererar matchning vid invokation.

## At-invocation contract

Operator invokes med:
- `/li:az-discover-presale --customer-env <env-description-file>` (warmed customer-env via /li:context-warm-customer)
- `/li:az-discover-presale --direction "<customer's stated direction>"` (where customer wants to go)

AI at invocation:
1. Reads env-description (compute, network, storage, identity, AI/ML, data, monitoring, security)
2. Cross-references operator-AI's current Azure-service catalog knowledge (post-training-cutoff context)
3. Identifies under-utilization gaps (services kunden borde använda men inte gör)
4. Identifies extension opportunities (services som extend befintliga investments)
5. Maps each opportunity till customer-stated direction (filter: relevance score >= 6/10)
6. Drafts SE-framed upsell narrative (outcome-led: "denna unlock:ar X för kunden")
7. Calls Cost Analyzer agent för pricing context (per relevant SKU)
8. Surface as structured report

## Agent dispatch (vid invokation)

Per backlog 5.4-spec — reuses existing ms-specific agents:
- **AzureArchitect** — primary (Azure service-mapping)
- **FieldCTOAdvisor** — secondary (customer-direction-mapping, outcome-language)
- **CAIPEngagementCoach** — secondary (SE framing, not-pushy-tone)
- **CostAnalyzer** — conditional (pricing-context per identified opportunity)

## Brand template

`~/.lintel/brand/presale-templates/` slot (optional). Operator kan dropp customer-engagement-report templates som AI använder som baseline-format.

## Voice tier

`voice: internal` default. Customer-share kräver upstream `/li:rais-customer-voice-check` PASS innan PR/deliverable shared externt.

## Status protocol

- **DONE** — presale-report rendered + N opportunities identified + agent-dispatch successful
- **DONE_WITH_CONCERNS** — rendered men some opportunities had low confidence (<6/10)
- **BLOCKED** — customer-env-description ej parseable, eller no `--direction` flag
- **NEEDS_CONTEXT** — customer-env file missing eller empty

## When to promote from slot till curated

Om operator ser repetitiva presale-patterns (e.g., Arc-discovery alltid följer samma template för Nordic-Public-Sector engagements), promote pattern till SKILL.md body — det blir canonical workflow för den scenario.

Until then: AI genererar fresh per invocation. Repo stays clean per L-001.

## Recommended next steps

After invocation:
- QA på output: `/li:rais-customer-voice-check` om customer-share
- Brand-render: `/li:generate-ppt --from-pipeline <run-dir>` om operator vill ha deck-form
- Engagement-context warming: `/li:context-warm-customer <engagement-id>` innan next solo-invocation av denna skill
