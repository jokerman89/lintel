# Az-tldr service catalog

Curated Azure service content for `/li:az-tldr <service>` invocation.

## Status table

| Service ID | Status | Last curated | Coverage | Primary agent |
|---|---|---|---|---|
| `expressroute` | ✓ active | 2026-05-28 | full 15 sections + §16 BGP deep-dive | AzureArchitect |
| `azure-openai` | ✓ active | 2026-05-28 | full 15 sections + §16 deployment/filter/PTU sizing | AzureOpenAIAdvisor |
| `front-door` | ⚠ template only | — | none | AzureArchitect |
| `api-management` | ⚠ template only | — | none | GraphAPIAdvisor |
| `azure-firewall` | ⚠ template only | — | none | AzureArchitect |
| `azure-firewall-premium` | ⚠ template only | — | none | AzureArchitect |
| `aks` | ⚠ template only | — | none | AzureArchitect |
| `storage-account` | ⚠ template only | — | none | AzureArchitect |
| `sql-mi` | ⚠ template only | — | none | AzureArchitect |

**Status legend:**
- ✓ active — content shipped, dogfoodable
- ⚠ template only — agent-mapping.yaml has entry, no content yet
- ✗ removed — was active, no longer curated

## Adding a new service

1. Copy `_template.md` to `<service-id>.md`
2. Fill all 15 sections per template structure
3. Set `as_of:` to today's date
4. Add entry to `agent-mapping.yaml` with primary + per-section + conditional agents
5. Update this README's status table
6. Run `bash tests/unit/az-toolbox-service-files.sh` to verify
7. Test invocation: `/li:az-tldr <service-id>`

## Freshness policy

- Content `as_of` >90 days old triggers warning at invocation time
- Quarterly review recommended for §9 (latest-greatest) + §14 (pricing)
- Major Azure GA announcement → update §9 within 2 weeks
- Customer-question patterns from real engagements → update §8 if heard 3+ times

## Coverage priority (operator's call)

Operator decides what to curate next based on engagement pipeline. Heuristic:
1. Services operator personally preps for most often
2. Services with high customer-question density
3. Services where MS Learn coverage is weak/fragmented (curated content fills gap)
4. Services where operator's prior session lessons would benefit team

Don't curate every Azure service — bloat. Curate the 10-20 most operator-relevant.

## Anti-pattern: copy-paste from Microsoft Learn

Curated content should EARN its existence by adding what Learn doesn't:
- Operator's real-engagement pitfalls (§6)
- Customer questions in plain language (§8)
- Honest cost-trap warnings (§14)
- Concrete implementation flow with handoff details (§15)

If a section is just "rephrased MS Learn content," delete it — the §10 link is enough.
