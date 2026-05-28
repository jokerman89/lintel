# Az-tldr section glossary

The 15 standard sections that every `services/<service>.md` follows. Each section has a specific purpose + depth target + agent-dispatch behavior.

## Section purpose + token targets

| # | Section | Purpose | Token target | Default agent |
|---|---|---|---|---|
| §1 | What it is | Core abstraction in plain English | ~50 words | none (curated only) |
| §2 | What it does | Operational value, concrete | ~80 words | none |
| §3 | How it's used | Named patterns | ~120 words / 3-4 patterns | none |
| §4 | Frameworks it lives in | CAF/WAF/ALZ/Zero Trust positioning | ~150 words | AzureArchitect |
| §5 | Top 10 things to know | Hard operational truths | ~300 words / 10 items | none |
| §6 | Known pitfalls | Real fallgropar + fixes | ~300 words / 10 items | none |
| §7 | What's required of customer | Prerequisites | ~200 words | none |
| §8 | 10 typical customer questions | Q&A from real engagements | ~400 words / 10 Q&A | none |
| §9 | Latest greatest | Recent GA/preview + dated | ~150 words | none (curated, dated) |
| §10 | Read further | Curated links (MS + experts) | links only | none |
| §11 | ELI5 explanation | Non-technical audience | ~100 words | none |
| §12 | Level-500 explanation | Senior architect audience | ~250 words | AzureArchitect |
| §13 | Enterprise meaning | Strategic / outcomes language | ~250 words | AzureArchitect + role overlay |
| §14 | Commercial perspective | Cost / POC / pricing | ~200 words | CostAnalyzer |
| §15 | Implementation flow | First-meeting → CSA handover | ~400 words | AzureArchitect |
| §16 | Service-specific deep dive | Optional, service-warrants-extra | variable | service-specific |

## Section invocation modes

**Full mode** (`/li:az-tldr <service>`):
All 15 sections rendered. Agents invoked per agent-mapping.yaml. Cost: ~3-5k tokens.

**Brief mode** (`/li:az-tldr <service> --brief`):
- §1 What it is
- §5 Top 10 things to know
- §8 10 customer questions
- §13 Enterprise meaning
- §15 Implementation flow (abbreviated)
Cost: ~1k tokens.

**Section mode** (`/li:az-tldr <service> --section <name>`):
Just specified section + agents for that section if mapped. Cost: ~200-500 tokens.

Valid section names (mapped to numbers):
- `what-it-is` → §1
- `what-it-does` → §2
- `usage-patterns` → §3
- `frameworks` → §4
- `top-10` → §5
- `pitfalls` → §6
- `customer-requirements` → §7
- `customer-questions` → §8
- `latest-greatest` → §9
- `read-further` → §10
- `eli5` → §11
- `level-500` → §12
- `enterprise-meaning` → §13
- `commercial` → §14
- `implementation-flow` → §15
- `service-specific` → §16

## Role overlays per section

When a role is active (per `~/.lintel/profile.yaml` role_active), section emphasis shifts:

**Field CTO** (customer-facing strategy):
- Emphasize: §13 enterprise meaning, §15 implementation flow
- Deprioritize: §6 pitfalls, §12 L500
- Invoke: FieldCTOAdvisor + ExecutiveBriefingDrafter

**Solution Architect** (technical depth):
- Emphasize: §4 frameworks, §5 top 10, §6 pitfalls, §12 L500, §16 service-specific
- Invoke: ThreatModelDrafter + BicepReviewer (per service traits)

**Engineering Manager** (process + handoff):
- Emphasize: §14 commercial, §15 handoff
- Invoke: Planner + ReleaseEngineer

## Section evolution

Sections are stable interface. Don't add §17 lightly. If a service warrants extra depth beyond §16, that's signal for either:
- A service-specific sub-page (linked from §10)
- Splitting service into multiple service-IDs (e.g., expressroute + expressroute-direct as separate)

Never edit section structure in `_template.md` without:
1. Operator approval
2. Migration of all existing service files to new structure
3. Update of agent-mapping.yaml per-section keys
4. Update of this README
