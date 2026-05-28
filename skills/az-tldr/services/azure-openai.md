---
service: Azure OpenAI Service
service_id: azure-openai
category: ai-ml
caf_pillars: [security, governance, performance]
waf_pillars: [security, reliability, performance, cost, operational-excellence]
as_of: 2026-05-28
refresh_cadence_days: 60
subagent_mapping:
  primary: AzureOpenAIAdvisor
  per_section:
    "4": AzureOpenAIAdvisor          # frameworks (CAF/WAF AI workload)
    "13": AzureOpenAIAdvisor          # enterprise meaning
    "14": CostAnalyzer                # commercial / provisioned-vs-standard
    "15": AzureOpenAIAdvisor          # implementation flow
  secondary_conditional:
    RAIReviewer: [customer-facing-output, sensitive-use-scenario, transparency-note-required, generative-content]
    KeyVaultAuditor: [byok, customer-managed-keys, encryption-at-rest]
    EUAIActReviewer: [eu-customer, high-risk-tier, eu-deployment]
    SecurityAuditor: [private-endpoint, vnet-injection, public-tier]
    BicepReviewer: [iac-discussion, deployment-design, aoai-landing-zone]
---

# Azure OpenAI Service — TLDR

> Customer-prep rundown. Operator-internal. Refresh every 60 days — model catalog moves fast.
> As of 2026-05-28. Verify against learn.microsoft.com/azure/ai-services/openai before high-stakes customer use.

## §1 What it is

Azure OpenAI is Microsoft's managed offering of OpenAI's models (GPT-4 family, GPT-5, o-series reasoning, embeddings, DALL-E, Whisper, Sora) deployed inside the Azure trust boundary. The customer rents inference capacity against a chosen model+region+deployment, paying per token or per provisioned throughput unit. Identity, networking, data residency, and content-safety policy stay under Azure's regular controls — not OpenAI's. It is OpenAI's models without OpenAI's data-handling terms.

## §2 What it does

Three operational deliverables: **regulated-environment AI access** (data stays in Azure tenant boundary, no training on customer prompts, EU Data Boundary support, FedRAMP High applicability), **production-grade SLAs and capacity guarantees** (Provisioned Throughput Units give deterministic latency + reserved capacity, Standard tier gives elastic but bursty inference), and **integrated Azure controls** (Entra ID auth instead of API keys, private endpoints, customer-managed keys, diagnostic logging to Log Analytics, Defender for Cloud posture). The point is: enterprise customers cannot use OpenAI direct for sensitive workloads; Azure OpenAI is the route.

## §3 How it's used (4 named patterns)

**1. RAG with Azure AI Search (most common enterprise pattern).** Customer indexes their private corpus into Azure AI Search (or Cosmos DB vector store, or Postgres+pgvector), retrieves top-k chunks at query time, stuffs into prompt context, calls Azure OpenAI chat completion. Variants: hybrid search (vector + BM25), semantic ranking, multi-index orchestration. Typical SKU: GPT-4o or GPT-4.1 + text-embedding-3-large. Lives in product features like internal copilots, doc Q&A, support deflection.

**2. AOAI behind APIM gateway (multi-tenant or quota-controlled access).** API Management fronts one or more AOAI deployments, handles token-budget enforcement, per-team quotas, API-key abstraction, fallback routing between regions, and circuit-breakers when content-filter blocks spike. Used when 3+ internal teams share AOAI capacity. Microsoft's published "AI gateway" pattern covers this — see the Azure Architecture Center reference.

**3. Provisioned Throughput Units (PTU) for latency-critical production.** Customer reserves PTUs in a region for a specific model version. Inference is dedicated capacity, no shared-tenant bursting. Lower per-token cost at high volume + deterministic p50/p99 latency. Used by customer-facing workloads where Standard-tier latency variance is unacceptable. Typical commitment: monthly or annual reservation.

**4. Agent orchestration via Azure AI Foundry or Semantic Kernel.** Customer builds multi-step agents calling AOAI repeatedly per user turn (planner → tool-calls → critic → synth). Foundry provides hosted orchestration; Semantic Kernel / LangGraph / AutoGen are code-first alternatives. Token-budget control becomes hard — that's where context-warming patterns and PTU sizing show up.

## §4 Frameworks it lives in

**CAF (Cloud Adoption Framework):**
Azure OpenAI is positioned in CAF's **AI workload reference architecture** under the AI Landing Zone (a sub-pattern of the regular ALZ). Sits in a workload subscription, peered into the connectivity hub. CAF guidance: separate AOAI deployments per environment (dev/test/prod), use private endpoints (Disable public network access), enforce Entra ID auth, and route through APIM if multi-tenant. AOAI is RAI-tier classified, so the AI Landing Zone adds an RAI policy layer not present in regular ALZ.

**WAF (Well-Architected Framework) — AI Workload guidance:**
- **Security:** dominant pillar. Private endpoint or VNet injection, Entra auth, CMK, content filtering policy review, prompt-injection defense, output-grounding controls.
- **Reliability:** PTU vs Standard tradeoff, regional failover (paired regions), retry-with-backoff on 429s, capacity headroom.
- **Performance:** model selection (latency vs quality), prompt-engineering optimization, caching responses where applicable, streaming responses.
- **Cost:** per-token vs PTU breakeven analysis, embedding model choice (3-small vs 3-large is ~6x cost), context-window control.
- **Operational excellence:** model deprecation tracking (3-6 month notice), eval gates before promote, regression testing on prompt changes.

**Microsoft RAI standard (mandatory for MS-internal use):**
AOAI invocations are in scope of MS Responsible AI Standard v2. Operator must complete RAI Impact Assessment for the workload, Transparency Note for customer-facing surfaces, Sensitive Use review if applicable (medical, legal, employment, financial decisions, content moderation, etc).

**EU AI Act:**
GPAI obligations on the model provider (OpenAI/Microsoft); high-risk obligations on the deployer (customer) when the system is used for in-scope use cases. Customer must classify their use case before procurement.

**Zero Trust:**
Service-to-service Entra auth (no API keys), conditional access on the deployment, network isolation via private endpoint, audit via diagnostic logs.

## §5 Top 10 things to know

1. **Model deprecation moves faster than Azure-service deprecation.** A model can deprecate in 3-6 months. GPT-4 (legacy) was deprecated. GPT-4 Turbo (2024-04-09) was deprecated. Budget for prompt-regression testing per upgrade — system prompts that work on GPT-4o may degrade on GPT-5 without re-tuning.

2. **Quota is regional + per-deployment, not per-subscription.** Standard tier TPM (tokens per minute) and RPM (requests per minute) are allocated per (region, model, deployment name). Two deployments of the same model in the same region don't share quota — but they do share regional capacity, so creating more deployments doesn't multiply available throughput.

3. **Content filter blocks count as 200 OK from Azure's billing perspective but render as 400 in the API.** Customer pays for the input tokens consumed by classification. Filter-block rates above 5% suggest prompt-engineering or use-case-tier mismatch — investigate before throwing at higher SKU.

4. **PTU pricing model is reservation-based, not consumption.** PTUs are billed whether or not you're inferring. Breakeven vs Standard depends on (utilization × model × region). Rule of thumb: >70% sustained utilization → PTU wins on cost AND latency. <50% sustained utilization → Standard wins.

5. **Region availability varies wildly per model.** GPT-5 may be GA in East US 2 + Sweden Central + UK South but Preview-only in West Europe. Embeddings may be GA in 20+ regions. Always check region availability before committing on customer's data-residency-required region.

6. **Default content filter tier (`Medium`) blocks more than customers expect.** Categories: hate, sexual, violence, self-harm. Each has filter severity (high/medium/low/off). "Off" requires Microsoft approval via the Modified Content Filter form (and only for specific categories, with justification). Plan customer onboarding around getting the approval before go-live.

7. **Streaming completions count tokens per chunk but are billed at the end.** First-chunk latency is what matters for UX. Time-to-first-token (TTFT) is region+SKU dependent — Provisioned tier guarantees TTFT; Standard tier does not.

8. **Whisper, DALL-E, Sora have separate quota systems.** They are not chat-completion models. Pricing model differs (per-image, per-minute-of-audio). Region availability is narrower. Don't assume "AOAI is available in region X" covers them.

9. **Customer-managed keys (CMK) require regional Key Vault + system-assigned managed identity on the AOAI resource.** CMK encrypts data at rest in the AOAI resource. Doesn't cover prompts in transit (that's TLS) and doesn't cover anything OpenAI uses for model-version filter training (which is OpenAI's not customer's).

10. **Prompt + completion logging is OFF by default in AOAI.** OpenAI's API logs prompts/completions for abuse monitoring. AOAI does NOT — unless you turn on diagnostic logging to Log Analytics yourself. This is a privacy feature but also means you have no audit trail by default. Decide explicitly.

## §6 Known pitfalls

1. **Quota exhaustion mid-demo** — Customer ran fine in dev but production launch hit regional TPM cap. Why bites: quota requests have 1-3 day SLA. How to avoid: file quota increase form 7-10 days before launch; if PTU, reserve before launch week.

2. **Content filter blocks spike when prompt template changes** — Customer added few-shot examples containing words that tripped the violence filter. How to avoid: run new prompts through a filter-classification test before production rollout; consider Modified Content Filter for specific use cases.

3. **Public network access not disabled by default** — Customer's AOAI is reachable from internet even with private endpoint configured. How to avoid: explicitly set publicNetworkAccess to Disabled; verify in Azure Policy.

4. **CMK rotation breaks deployment** — Customer rotated Key Vault key without first granting the AOAI MI access to the new version. How to avoid: use auto-rotation with grace period; test rotation in non-prod first; monitor AOAI resource health.

5. **API key in prompt logging** — Diagnostic logging captured prompts that contained API keys, dumped to Log Analytics, visible to analytics team. How to avoid: never include secrets in prompts; if logging on, scope log access via RBAC.

6. **Token-budget runaway in agent loops** — Multi-step agent recursed through 50+ LLM calls per user turn. How to avoid: hard cap on tool-call depth + total tokens per session; observability on per-session cost.

7. **Embedding model swap requires full re-index** — Customer upgraded from text-embedding-ada-002 to text-embedding-3-large mid-flight; new queries don't match old index. How to avoid: dual-index during cutover; never query across embedding model versions.

8. **GPT-5 reasoning tokens not counted in input but billed** — o-series and GPT-5 reasoning emit internal "reasoning tokens" billed at output rate but invisible in API response by default. How to avoid: enable reasoning-summary in API, monitor billed-vs-visible token ratio, budget for 2-5x output tokens on hard reasoning tasks.

9. **Sensitive Use slipped past RAI review** — Customer-facing chatbot in a medical domain shipped without Sensitive Use approval; flagged at audit. How to avoid: run `/li:rais-sensitive-use` checklist at DEFINE phase, not BUILD.

10. **Region pairs assumption breaks failover** — Customer assumed Sweden Central → West Europe failover would work for AOAI; West Europe didn't have the same model. How to avoid: verify model+region availability for primary AND failover region; align deployment names across regions for clean DNS-based failover.

## §7 What's required of customer

- **Identity:** Entra ID tenant (no consumer Microsoft accounts). Recommend Workload Identity or system-assigned MI for service-to-service.
- **Networking:** if private endpoint, customer needs hub VNet + private DNS zone + DNS resolution from app subnet. If VNet injection, dedicated subnet with delegation.
- **Quota:** initial deployments get default quota; production volume requires quota increase request (form on Azure Portal). Allow 1-3 business days.
- **RAI artifacts (for MS-internal AND many customer-side compliance contexts):** Transparency Note, RAI Impact Assessment, Sensitive Use review if applicable.
- **Commercial:** EA/CSP with AOAI service enabled. AOAI access form required for some models/regions (legacy gate for GPT-4 era — mostly auto-approved now but check).
- **Compliance:** customer classifies use case under EU AI Act if EU-deploying. GDPR DPIA if EU customer data in prompts. HIPAA BAA if PHI in prompts (covered by Microsoft's BAA when deployed correctly).
- **Operational:** observability stack (Log Analytics, App Insights), eval framework (Azure AI Foundry evaluations, promptfoo, custom), incident-response runbook for content-filter spikes and quota exhaustion.

## §8 10 typical customer questions

**Q1: Does Microsoft or OpenAI train on our prompts?**
A: No. Azure OpenAI prompts and completions are not used for training, retraining, or fine-tuning of any base models. This is contractually different from OpenAI's direct API. Customer data stays in the Azure tenant boundary.

**Q2: What's the cheapest way to run GPT-4o at production scale?**
A: It depends on utilization pattern. If you're sustaining >70% of a PTU's capacity, PTU wins on per-token cost. If your traffic is bursty or below 50% utilization, Standard tier wins. Run a 2-week measurement on Standard, then calculate breakeven before committing PTU.

**Q3: Can we use AOAI for medical / legal / financial advice to end users?**
A: Technically yes, but those are Sensitive Use scenarios under Microsoft's RAI Standard. Requires Sensitive Use review approval before production. Customer-facing surfaces also need Transparency Notes. Most customers under-scope this — expect 4-6 weeks for the review cycle.

**Q4: Is our data exposed to OpenAI?**
A: No. Microsoft hosts the models in Azure infrastructure. OpenAI does not have inference access to AOAI deployments. The exception is abuse-monitoring: Microsoft (not OpenAI) inspects a small sample of flagged inputs for policy violations. Customers can request abuse-monitoring opt-out via the Modified Abuse Monitoring form — approval requires justified business reason.

**Q5: How do we handle model deprecation?**
A: Microsoft publishes a deprecation calendar per model. Notice is typically 6 months before retirement, with End-of-Sale earlier. Build prompt-regression test suite (Azure AI Foundry evaluation runs work well) so you can validate new model behavior before flipping production traffic. Budget engineering time for system-prompt re-tuning per major upgrade.

**Q6: What's the latency we should expect?**
A: TTFT (time-to-first-token) for streaming: ~300-800ms on Standard tier in same region; ~150-400ms on PTU. Total response time scales with output token count. Cross-region calls add 50-150ms. Reasoning models (o-series, GPT-5 thinking modes) add seconds for the internal reasoning step.

**Q7: Can we use customer-managed encryption keys?**
A: Yes. CMK encrypts data at rest in the AOAI resource using a key you control in Azure Key Vault. Setup: enable system-assigned MI on the AOAI resource, grant Key Vault Crypto Service Encryption User role to the MI, point the AOAI resource at the key. Rotation needs grace-period handling.

**Q8: How do we control which models employees can use?**
A: Each deployment is a model-version + region + name. Restrict access via Entra ID + Azure RBAC at the deployment level. Most customers front AOAI behind APIM and govern access per-team or per-app-id there. Avoid the "one giant deployment shared by all teams" anti-pattern.

**Q9: What's our data residency story?**
A: AOAI deployment region controls where inference happens and where data-at-rest lives. EU Data Boundary covers EU customer data when deployed in EU regions. Some models are available in Sweden Central, West Europe, North Europe, France Central, Switzerland North — verify per-model availability in your required region.

**Q10: How does pricing actually work?**
A: Standard tier: per-token input + per-token output, billed monthly. Token rates vary per model (GPT-5 > GPT-4o > GPT-4o-mini > embeddings). Provisioned tier: per-PTU-per-hour reserved capacity. Hidden costs: reasoning tokens (billed at output rate, sometimes 2-5x visible output for hard tasks), embedding re-indexing on model upgrades, content-filter-blocked requests (input tokens still billed). Always calculate against actual measured traffic, not vendor estimates.

## §9 Latest greatest

- **GPT-5 family (GA: 2026-Q1)** — reasoning models with adjustable reasoning effort, replaces o3 line for most use cases — [MS Learn](https://learn.microsoft.com/azure/ai-services/openai/concepts/models)
- **GPT-4.1 (GA: 2025-Q4)** — improved instruction-following + structured output, 1M context window — [MS Learn](https://learn.microsoft.com/azure/ai-services/openai/concepts/models)
- **Sora video model (Preview: 2026-Q2)** — text-to-video, limited region availability, separate quota — [MS Learn](https://learn.microsoft.com/azure/ai-services/openai/sora)
- **EU AI Act GPAI compliance attestation** (effective 2026-08) — Microsoft published GPAI documentation for AOAI base models — verify your high-risk system classification before launch.
- **Provisioned Managed (legacy term Provisioned Throughput Units) updated tier structure** — new entry-level tier reduces minimum PTU commitment for smaller workloads.
- **Token caching for prompt prefixes** — input-side cache reduces cost on repeated system prompts (common in RAG); auto-applied where deployment supports it.

## §10 Read further

**Microsoft Learn:**
- Overview: https://learn.microsoft.com/azure/ai-services/openai/overview
- Model catalog + deprecation: https://learn.microsoft.com/azure/ai-services/openai/concepts/models
- Quotas + limits: https://learn.microsoft.com/azure/ai-services/openai/quotas-limits
- Provisioned throughput: https://learn.microsoft.com/azure/ai-services/openai/concepts/provisioned-throughput
- Content filtering: https://learn.microsoft.com/azure/ai-services/openai/concepts/content-filter
- Responsible AI for AOAI: https://learn.microsoft.com/azure/ai-foundry/responsible-ai/openai/overview
- AI Landing Zone reference: https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-openai-e2e-chat

**Microsoft architecture diagrams:**
- Baseline OpenAI end-to-end chat: https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-openai-e2e-chat
- AOAI APIM gateway pattern: https://learn.microsoft.com/azure/architecture/ai-ml/guide/azure-openai-gateway-multi-backend

**Reference architectures (ALZ):**
- AI Landing Zone: https://github.com/Azure/AI-Landing-Zones
- Bicep AVM module for AOAI: https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/cognitive-services/account

**Known expert voices (independent):**
- Simon Willison (simonwillison.net): in-depth notes on model behavior across providers
- Hamel Husain (hamel.dev): production LLM evaluation patterns
- Microsoft AI Foundry team blog: https://techcommunity.microsoft.com/category/azure-ai

## §11 ELI5 explanation

Imagine Microsoft built a soundproof, locked room around OpenAI's smartest robots and only lets your company's employees in through a key-card door you control. The robots inside are just as smart as the public ones, but everything they hear stays in the room — Microsoft promises not to share it, and Microsoft can't even teach the robots anything new from what your employees say. You pay either per question (Standard) or you rent a dedicated robot for the month (PTU).

## §12 Level-500 explanation

AOAI exposes inference endpoints sitting on top of the same Azure ML / Cognitive Services control plane used by other Azure AI services, but with model weights hosted on Microsoft-managed GPU clusters under the OpenAI partnership terms. The data plane is Azure-native: requests authenticate via Entra ID (or legacy keys), traffic terminates at the AOAI resource's regional endpoint, content filtering runs synchronously before model invocation (and on output), and inference happens on dedicated capacity (PTU) or shared pooled capacity (Standard) within the region. Provisioned Throughput Units are pre-allocated GPU capacity reservations; each PTU corresponds to a tokens-per-second commitment per model. The PTU pricing model is utilization-agnostic — once reserved, you pay regardless of consumption. Network isolation options: public endpoint (default, filtered by IP allowlist), private endpoint via Azure Private Link (recommended production posture), or VNet injection for AI Foundry hosted scenarios. CMK encrypts at-rest data using customer Key Vault keys via service-managed identity. Diagnostic logging is opt-in and emits to Log Analytics — model invocations, content-filter classifications, token usage. RAI policy enforcement is layered: base-model safety training (OpenAI), Microsoft-built content filter (synchronous per-request), Modified Content Filter (per-customer custom severity), Modified Abuse Monitoring (opt-out of Microsoft's sample inspection). Token billing splits into input/output/reasoning/cached buckets at different rates; reasoning tokens (o-series, GPT-5) are emitted internally but not returned by default and bill at output rate. Model deprecation runs on a 3-6 month cycle; the deprecation calendar is canonical.

## §13 What it means for enterprise customer

Buying Azure OpenAI signals four enterprise-posture choices: (1) **the customer accepts that AI is a regulated-software category, not a consumer toy** — RAI artifacts, Sensitive Use review, audit-trail diagnostic logs are non-negotiable, not optional polish; (2) **the customer wants OpenAI quality without OpenAI's data-handling terms** — they will not send sensitive prompts to consumer ChatGPT, will not let employees paste IP into chat.openai.com, but they will give them the same models through a trusted boundary; (3) **the customer is willing to invest in eval, prompt-regression, and capacity planning** — these are not optional engineering practices, they are operational requirements that distinguish a PoC from production; (4) **the customer is committing to Microsoft as their AI platform partner** — AOAI shares the Azure stack (Entra, ALZ, observability, billing), making it more expensive to switch to Anthropic Bedrock or Vertex AI later. The CIO cares because AI delivers measurable productivity outcomes when deployed in production (not just demos); the CISO cares because it's the route that doesn't violate data-handling policy; the CFO cares because PTU vs Standard is a real procurement choice with 30-50% cost variance.

## §14 Commercial perspective

- **Cost model:** Standard tier per-token (input + output + reasoning + cached, all at different rates per model). PTU tier per-PTU-per-hour reservation. Embeddings billed separately, much cheaper per token. Image/video/audio models billed per asset.
- **Indicative pricing (as of 2026-05-28, USD, subject to change):**
  - GPT-4o Standard: ~$2.50 per 1M input tokens / $10 per 1M output (with prompt-cache discount for repeated prefixes)
  - GPT-4o-mini: ~$0.15 per 1M input / $0.60 per 1M output (10-15x cheaper than 4o, good for high-volume low-stakes)
  - GPT-5 reasoning: ~$15+ per 1M output equivalent including reasoning tokens
  - text-embedding-3-large: ~$0.13 per 1M tokens
  - PTU baseline: starts around $1.5k-2k/month per PTU at minimum reservation
- **POC viability:** Yes — Standard tier is the right tool for PoC, ~$50-500 in tokens to validate a use case.
- **First commercial commitment threshold:** PTU minimums (per-region, per-model) — typically when monthly token spend exceeds $3-5k on Standard, PTU starts breaking even.
- **Cost-trap warnings:**
  - Reasoning tokens silently 2-5x output billing on hard tasks
  - Embedding re-indexing on model upgrade can be $$k for large corpora
  - PTU reserved but underutilized = burning rate
  - Content-filter-blocked requests still bill input tokens
  - Multi-step agents recursing without token budget controls

## §15 Implementation flow — first meeting → CSA handover

**1. First meeting (SE).** Discovery: use case classification (productivity copilot? customer-facing? decision-support?), expected concurrency, data sensitivity (PII? PHI? regulated industry?), residency requirements, existing AI investments. Surface RAI scope early — if it's Sensitive Use, the timeline doubles.

**2. Discovery + scoping (SE + customer arch + DPO/legal).** Architecture questions: which models (GPT-5 vs 4o vs 4o-mini for cost), Standard vs PTU forecast, RAG vs fine-tune vs prompt-only, private endpoint vs public, CMK requirement, EU AI Act classification, GDPR DPIA scope. RAI artifacts initiated in parallel — Transparency Note draft, Impact Assessment kickoff.

**3. Design proposal (SE + customer arch board).** AI Landing Zone topology (workload subscription, AOAI deployment, AI Search index, AOAI-behind-APIM if multi-tenant), eval framework selection (AI Foundry evaluations, promptfoo, custom), observability plan (Log Analytics workspace, dashboards, alerts on content-filter spike and quota exhaustion), capacity sizing (TPM/RPM forecast → quota request).

**4. Pre-sales technical close (SE).** Quote validation: PTU vs Standard breakeven worked, monthly cost projection signed-off by Finance. RAI sign-off: Impact Assessment approved (and Sensitive Use approved if applicable). Microsoft AOAI access form filed if needed.

**5. CSA handover.** Implementation timeline (typically 4-8 weeks PoC → 12-16 weeks first production workload). IaC drop-in (Bicep AVM module for AOAI, AI Search, Key Vault, APIM if used). Eval suite + golden dataset for prompt-regression. Runbooks: quota exhaustion, content-filter spike, model deprecation, key rotation. Operator handoff doc covers ownership of prompts, eval gates, and model-upgrade cadence.

## §16 Service-specific deep-dive — deployment + content filtering + PTU sizing

**Deployment lifecycle:** A "deployment" is the (model, version, name, capacity) tuple in a specific region. Deployments are mutable on capacity but immutable on (model, version). Promoting GPT-4o → GPT-5 means creating a new deployment + re-pointing application traffic + retiring old deployment. This is why deployment names should be model-version-agnostic (`chat-prod-eu`, not `gpt4o-2024-11-20-prod`) — application code points at the deployment name, not the underlying model version.

**Content filtering tiers:**
Default filter: 4 categories (hate, sexual, violence, self-harm) × 4 severities (safe, low, medium, high) × 2 directions (prompt, completion). Default is to block at medium+ on all categories. "Modified Content Filter" (MCF) is a Microsoft-approved exception process for specific categories/severities — required justification, intended use, and risk mitigation. MCF is NOT a get-out-of-RAI-jail card; it shifts the responsibility for downstream handling to the customer's safety review.

**Custom categories (preview/GA depending on region):**
Customer-defined filter categories using few-shot examples. Useful for domain-specific safety (e.g., financial advice disclaimers, medical decision exclusions). Applied alongside default filters.

**Prompt-injection defenses:**
"Prompt Shields" filter detects user-input-as-system-instruction patterns. Useful but not sufficient — also need application-level defenses (sandboxed tool calls, output validation, capability scoping).

**PTU sizing math (operator's cheat sheet):**
1. Measure peak TPM on Standard for 2 weeks.
2. Convert TPM to PTUs using Microsoft's per-model conversion table (1 PTU ≈ X tokens/sec depending on model).
3. Calculate Standard monthly cost vs PTU monthly cost at the measured peak.
4. If PTU cost ≤ Standard cost × 1.3 (allowing for 30% over-provisioning headroom) → PTU wins on cost and latency.
5. Below that threshold, Standard is correct.
6. NEVER size PTU on demo / PoC traffic — real production curves are different.

**Model selection heuristic:**
- High-stakes reasoning, low volume: GPT-5 reasoning
- Production chat, balance quality/cost: GPT-4o (or GPT-4.1 for instruction-heavy)
- High-volume, low-stakes (classification, summarization, light RAG): GPT-4o-mini
- Pure embeddings: text-embedding-3-large for quality, text-embedding-3-small for cost
- Audio/video/image: dedicated SKUs (Whisper, DALL-E, Sora)

---

**Curation notes (for future maintainers):**

- Model catalog moves fast — check §9 latest-greatest monthly, not quarterly
- §14 pricing changes per Microsoft pricing page updates — re-verify before customer quotes
- §6 pitfalls: high-priority for engagement teams — promote new patterns from incident reports
- §10 links rot fast on aka.ms shortcuts — prefer canonical learn.microsoft.com paths
- RAI artifacts referenced in §7 and §15 should match current MS RAI Standard version (currently v2)
- EU AI Act references in §4 + §9 will need rework after GPAI guidelines mature post-2026-08
