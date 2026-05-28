---
service: ExpressRoute
service_id: expressroute
category: networking
caf_pillars: [security, reliability, performance]
waf_pillars: [security, reliability, performance, cost, operational-excellence]
as_of: 2026-05-28
refresh_cadence_days: 90
subagent_mapping:
  primary: AzureArchitect
  per_section:
    "4": AzureArchitect
    "13": AzureArchitect
    "14": CostAnalyzer
    "15": AzureArchitect
  secondary_conditional:
    KeyVaultAuditor: [private-peering, ipsec-overlay, certificate-rotation]
    BicepReviewer: [iac-discussion, gateway-deployment]
    SecurityAuditor: [public-tier-discussion, transit-routing]
    OneBranchReviewer: [provider-config-pipeline]
---

# ExpressRoute — TLDR

> Customer-prep rundown. Operator-internal. 15 sections per Lintel az-tldr template.
> As of 2026-05-28. Verify against learn.microsoft.com before high-stakes customer use.

## §1 What it is

ExpressRoute is private connectivity between on-prem infrastructure and Microsoft cloud services (Azure, Microsoft 365, Dynamics 365). It bypasses the public internet entirely. The customer's network attaches via a connectivity provider's MPLS or directly via Microsoft Enterprise Edge (MSEE) routers. Traffic flows over BGP-routed circuits with SLA-backed availability. It is private, dedicated, predictable bandwidth — the opposite of "internet, but Microsoft."

## §2 What it does

ExpressRoute solves three operational pains simultaneously: **predictable bandwidth** (customer reserves capacity, no contention with internet traffic), **low + consistent latency** (single AS hop to Microsoft backbone, no public-internet variability), and **audit-friendly connectivity** (traffic never traverses public internet, simplifying compliance audits like PCI-DSS, HIPAA, FSIA, NIS2). Operationally: workloads requiring stable performance (SAP, Oracle, real-time financial, telco signaling) become viable in Azure. Customer's existing on-prem networking team retains BGP routing control instead of treating Azure as a black box.

## §3 How it's used (4 named patterns)

**1. Hub-spoke with central transit (most common enterprise pattern).** Customer terminates ExpressRoute in a hub VNet, which contains shared services (firewall, DNS, Bastion). Spoke VNets peer with hub. On-prem networks reach Azure workloads via hub. The hub's ExpressRoute Gateway is the choke-point — sizing matters because traffic from all spokes converges. Typical for organizations with 5+ workload subscriptions where centralized inspection is mandatory.

**2. ExpressRoute Direct for hyperscale workloads.** Customer connects directly to Microsoft Enterprise Edge ports (10 Gbps or 100 Gbps) without a connectivity provider in between. Used when bandwidth exceeds 10 Gbps total, when customer wants single-customer-isolation on physical ports, or when MACsec data-plane encryption is required. Higher upfront commitment ($) but lower per-Gbps cost at scale.

**3. Global Reach for site-to-site over Microsoft backbone.** Two ExpressRoute circuits in different geographies can be linked, allowing on-prem-to-on-prem traffic over Microsoft's WAN. Used to replace customer's existing MPLS between regional offices when customer already has ExpressRoute for Azure. Avoids paying MPLS provider for inter-site connectivity.

**4. Multi-region active/active with redundant circuits.** Two ExpressRoute circuits, each in a different metro (e.g., Stockholm + Helsinki for Nordic customer), with redundant Azure regions. BGP communities steer traffic preference. Handles full-circuit failure, full-region failure, and provides regional latency optimization. The most expensive pattern but the only one that survives a metro-level outage.

## §4 Frameworks it lives in

**CAF (Cloud Adoption Framework):**
ExpressRoute lives in the **Ready phase** of CAF — specifically in the connectivity subscription of the Azure Landing Zone (ALZ) reference architecture. The ALZ Connectivity subscription is the canonical location: a centralized hub-VNet hosts the ExpressRoute Gateway, and workload subscriptions consume connectivity via VNet peering. CAF guidance: avoid distributing ExpressRoute Gateways across multiple subscriptions (operational overhead + cost) unless tenant-segmentation demands it.

**WAF (Well-Architected Framework):**
- **Reliability (dominant pillar):** SLA-backed connectivity (99.95% per circuit; 99.99% with dual-circuit redundancy). Failure modes well-understood. Service Health alerts available per circuit.
- **Performance Efficiency:** Bandwidth is reserved, not best-effort. Latency consistent (single AS hop to Microsoft).
- **Security:** Bypasses public internet. Combined with Private Endpoints + Private DNS, eliminates internet-routed paths to Azure PaaS.
- **Cost:** Predictable monthly fee + (Premium tier) per-GB outbound. Standard tier unlimited outbound within geopolitical region.
- **Operational Excellence:** Circuit monitoring via Azure Monitor + Connection Monitor. BGP session state visible. Customer-side routing in customer's control.

**Azure landing zones (ALZ):**
Canonical pattern: Connectivity subscription hosts hub-vnet with ER Gateway. Workload subscriptions VNet-peer to hub. Reference Bicep: [Azure/ALZ-Bicep](https://github.com/Azure/ALZ-Bicep). Use Azure Virtual WAN as alternative if simpler hub-and-spoke insufficient (e.g., 50+ branches).

**Zero Trust:**
ExpressRoute alone is NOT Zero Trust. Private connectivity does NOT replace identity-based access control. Combine ExpressRoute (network layer) with Conditional Access + Entra Private Access (identity layer) + Private Endpoints (PaaS layer). Customers conflating "private network = secure" should be politely corrected — that's 1990s thinking.

**MITRE ATT&CK relevance:**
ExpressRoute reduces external-network-exposure attack surface (T1190 Exploit Public-Facing Application) but expands internal-attacker reach (T1021 Remote Services). Customer's on-prem compromise can now reach Azure resources directly. Net-zero security posture change unless paired with proper segmentation.

## §5 Top 10 things to know

1. **Two BGP sessions per circuit, always.** A circuit comprises primary + secondary connection in active/active. Both are BGP-peered. Customer's router(s) must handle this. Single-router-customer is a misconfiguration even if circuit is "single-circuit."

2. **Circuit ≠ Connection ≠ Gateway.** Circuit is the provisioned capacity (you pay for this). Connection is the binding between circuit and gateway. Gateway is the Azure-side network device routing traffic into VNets. You can have multiple connections from one circuit to multiple gateways (multi-tenancy or hub-spoke).

3. **SKU choice locks Standard vs Premium semantics.** Standard: ≤10 VNets per circuit (post-2020 default raised from 10 actually), connectivity to home geopolitical region only. Premium: 100+ VNets, global connectivity across geopolitical regions, more BGP routes accepted. Premium is ~2x cost. Common mistake: provisioning Standard then discovering Premium needed → SKU upgrade requires circuit recreate (downtime).

4. **ExpressRoute Direct vs Provider-based has dramatic billing implications.** ExpressRoute Direct: customer commits to physical port (10 Gbps = ~$2-5k/mo, 100 Gbps = ~$15-25k/mo) plus per-circuit billing. Provider-based: pay provider for delivery + Azure for circuit (50 Mbps starts around $50/mo Azure-side; provider varies wildly). Direct breaks even at ~5+ circuits OR sustained 5+ Gbps total throughput.

5. **Global Reach billing is separate.** Linking two ExpressRoute circuits via Global Reach incurs additional per-GB charges (different from circuit charges). Customer often misses this in initial pricing and gets a surprise bill in month 2.

6. **FastPath bypasses the ER Gateway data plane for certain traffic.** When enabled (Ultra Performance Gateway + Premium circuit + FastPath-compatible config), traffic between VNet workloads and on-prem skips the gateway's data-plane bottleneck. Critical for high-throughput workloads where gateway is the limit. Not available for all VNet types or for transit-routing scenarios.

7. **ExpressRoute Gateway has SKU-based throughput limits.** Standard: 1 Gbps. High Performance: 2 Gbps. Ultra Performance: 10 Gbps. ErGw1AZ/ErGw2AZ/ErGw3AZ are the zone-redundant variants. Once gateway is throughput-limited, FastPath becomes mandatory (or gateway upgrade).

8. **MACsec encryption is ExpressRoute Direct only.** Standard provider-based circuits run over MPLS, customer trusts provider's transport. ExpressRoute Direct supports MACsec on the physical ports (customer manages keys via Azure Key Vault). Required for FedRAMP High + some EU sovereignty deployments.

9. **Connectivity SLA is per-circuit.** 99.95% for a single circuit. For 99.99% (~4.4 min downtime/month vs ~22 min), you need redundant circuits in different metros. Single-circuit-with-redundant-providers is NOT the same — Microsoft doesn't SLA that.

10. **Azure-side public IPs are not exposed by ExpressRoute by default.** Private peering routes Azure VNet RFC1918 traffic. Microsoft peering (formerly Public peering) routes traffic to PaaS services (Azure SQL, Storage) via Microsoft-IP-space — DEPRECATED for new circuits since 2024-Q3. Use Private Endpoints instead for PaaS.

## §6 Known pitfalls (top 10)

1. **Single-circuit production deployments.** Customer architects sometimes provision single circuit to "save cost." Then provider outage takes them down for hours. Fix: dual-circuit design in different metros. Talk customer through the math: extra circuit cost is small fraction of incident cost.

2. **Wrong SKU at provisioning, discovered post-deployment.** Standard SKU customer needs Premium (global routing or 100+ VNets). Fix: upgrade requires circuit deletion + recreate. Always assess scale requirements explicitly in design phase — write SKU choice into design doc.

3. **ExpressRoute Direct customer not understanding port-cost-vs-circuit-cost split.** They expect Direct to be cheaper than Provider, get surprised by port fee. Fix: explain Direct = port (always paid) + circuit (per-Gbps). Worth it at scale + isolation.

4. **Gateway SKU mismatch.** Customer deploys Standard gateway, then provisions Premium circuit with 10 Gbps capacity. Gateway bottlenecks at 1 Gbps. Fix: match gateway SKU to expected throughput + enable FastPath if eligible.

5. **Skipping MACsec on Direct circuits in regulated industries.** Customer compliance team didn't know it was available. Provider-based circuits can't add it. Fix: in regulated discovery, ask about MACsec requirement BEFORE choosing Direct vs Provider.

6. **Routing-table-bloat with Premium tier.** Premium allows more routes, customer accepts everything, BGP table on customer's router degrades. Fix: BGP route filtering on customer's side. Don't accept default 0.0.0.0/0 from Azure — controls outbound routing.

7. **Forgetting that Global Reach is per-region-pair.** Customer connects Stockholm circuit to Helsinki circuit via Global Reach. Six months later wants to add Frankfurt. Global Reach is now needed for all three pairs (Stockholm↔Helsinki, Stockholm↔Frankfurt, Helsinki↔Frankfurt). Fix: design for full mesh if multi-region from start.

8. **Treating BGP routes as immediate.** Customer assumes routes propagate in seconds. Reality: BGP convergence can take 30-90 seconds for major topology changes. Fix: in failover testing, give convergence time before declaring failure.

9. **Site-to-site VPN as "backup" to ExpressRoute — without testing failover.** VPN configured, never tested. Failover doesn't work when needed. Fix: schedule quarterly failover drills with customer ops. Test, don't assume.

10. **Customer's edge router doesn't support BGP communities customer needs.** Customer wants to use BGP communities for failover-preference logic. Edge router (often older Cisco ISR or aging branch device) doesn't fully support custom communities. Fix: validate router capabilities in discovery phase. Push for edge refresh if needed.

## §7 What's required of customer

**Hardware:**
- Edge router(s) supporting BGP and the chosen connectivity model
- For ExpressRoute Direct: physical fiber connectivity to Microsoft's nearest peering location (Equinix, Megaport, etc.)
- For MACsec: router with MACsec support (Cisco IOS-XR 7.x+, Juniper QFX 5x series, etc.)
- For provider-based: existing MPLS or carrier-Ethernet connectivity to provider

**Software / configuration:**
- BGP capability + AS number (private or public)
- Authorization to peer with Microsoft (customer's networking + security team alignment)
- DNS strategy compatible with Private DNS or hybrid resolver
- Routing policy: customer decides outbound preferences (which traffic to Azure via ER vs internet)

**Operational:**
- IT-change-window alignment (provisioning has lead-time: 1-7 days for provider, longer for Direct)
- Customer NOC trained on circuit monitoring and BGP troubleshooting
- Incident-response process including Microsoft escalation path

**Commercial:**
- Customer's relationship with connectivity provider (or willingness to commit to Microsoft port for Direct)
- Multi-year commit if leveraging discount tiers
- Bandwidth-growth forecast for SKU choice

**Compliance:**
- For regulated industries: data-residency requirements informing which Azure regions to peer to
- Audit-trail expectations for BGP changes (often customer-side logging required)

## §8 10 typical customer questions

**Q1: What's the SLA?**
A: 99.95% for a single circuit, 99.99% for dual-circuit redundancy in different metros. SLA is connectivity availability — not data delivery latency or jitter. For latency SLA, you need Connection Monitor measurements documented separately. The SLA covers Microsoft's side of the peer. Provider-side (if applicable) has its own SLA, often weaker.

**Q2: Can we POC ExpressRoute?**
A: Functionally yes, commercially difficult. Provisioning a circuit takes 1-7 days. Provider-side fees often have minimum commitments (3-12 months). The honest answer: a true POC of ExpressRoute is a multi-week engagement, not a weekend trial. Better POC paths: use VPN Gateway to demonstrate hybrid connectivity patterns, then commit to ExpressRoute when scale justifies it.

**Q3: How does ExpressRoute integrate with our existing MPLS?**
A: Two patterns: (a) Treat ExpressRoute as another MPLS endpoint — your existing routing logic chooses paths via BGP communities or local preferences; (b) Use ExpressRoute as primary path and MPLS as fallback (or vice versa). Don't run both as active/active without route-control thinking — you'll get asymmetric routing surprises.

**Q4: What about latency to Microsoft 365?**
A: ExpressRoute provides predictable latency to Microsoft's Azure regions. M365 services route within Microsoft's network from there. Net latency improvement vs internet is typically 10-50% depending on geography. For latency-sensitive M365 use (Teams real-time, large file sync), ER helps. For email + SharePoint browsing, internet is often fine.

**Q5: How do we secure traffic over ExpressRoute? Is it encrypted?**
A: Default: no encryption on the wire. ExpressRoute Direct supports MACsec on physical ports (customer-managed via Key Vault). Provider-based: encrypted at MPLS provider's transport layer (trust the provider). For application-layer encryption: use IPsec over ExpressRoute (Microsoft supports this pattern). Or TLS at app layer — most common.

**Q6: Can we connect our on-prem AD over ExpressRoute?**
A: Yes — traffic over Private peering reaches Azure VNets where Domain Controllers can sync. Many customers run Entra Connect with sync server on-prem reaching Azure-hosted DC over ER, or vice versa. Standard pattern.

**Q7: What if our connectivity provider goes down?**
A: That's the single-circuit failure mode. Mitigations: (a) Dual-provider redundancy — two circuits, different providers; (b) Single-provider with dual-circuit in different metros; (c) VPN Gateway as backup path. Each adds cost. The right answer depends on customer's RTO appetite + budget.

**Q8: Can we route internet traffic through Azure via ExpressRoute?**
A: Yes via Azure Virtual WAN secure-hub or by running NVAs (Palo Alto, Fortinet, etc.) in Azure that customer's traffic egresses through. This is "outbound forced tunneling" pattern. It works but has cost (NVA SKUs + Azure egress data charges). Often the customer's actual question is "can we centralize security inspection?" — answer is yes via NVA + ER + routing controls.

**Q9: How does ExpressRoute support our DR strategy?**
A: ER is a connectivity layer; it doesn't do DR itself. But: ER circuits in different metros (e.g., West Europe + North Europe for EU customer) plus paired Azure regions enables cross-region failover with maintained connectivity. Combine with Azure Site Recovery for workload DR and you have a complete pattern. Important: test failover quarterly.

**Q10: We have a legacy MPLS provider. Do we need to switch?**
A: Probably not. Most ExpressRoute connectivity providers are existing MPLS carriers (Equinix, Megaport, AT&T, BT, Verizon, etc.). Add ExpressRoute on top of existing MPLS without ripping out the carrier. Some customers leverage Global Reach to gradually move site-to-site over Azure backbone, then deprecate MPLS years later. Pragmatic path.

## §9 Latest greatest (as of 2026-05-28)

- **ExpressRoute Metro** (GA: 2025-Q2): High-availability circuit terminating in two metro peering locations simultaneously, with single provisioning workflow. Replaces the older dual-circuit-in-same-metro pattern. Single SLA, simpler ops. — [MS Learn: ExpressRoute Metro](https://learn.microsoft.com/azure/expressroute/metro)
- **FastPath GA scope expansion** (2025): FastPath now supports VWAN secure-hub scenarios + VNet-to-VNet via gateway transit. Earlier limitations on UDRs largely resolved. — [FastPath docs](https://learn.microsoft.com/azure/expressroute/about-fastpath)
- **Premium tier pricing adjustments** (2025-Q4): Per-GB outbound rates restructured; check pricing calculator before quoting.
- **ExpressRoute Direct 100 Gbps in more peering locations** (rolling 2024-2026): Added to Singapore, Tokyo, Frankfurt during 2025. Stockholm expected 2026-Q2 (verify).
- **Global Reach pricing tier changes** (2025-Q3): Discount for sustained throughput; affects multi-site customers.
- **Microsoft peering deprecation in progress**: New circuits cannot enable Microsoft peering. Existing circuits with it must migrate to Private Endpoints + Private DNS for PaaS access by 2027.

> Always verify against learn.microsoft.com/azure/expressroute — features change weekly.

## §10 Read further (curated, not generated)

**Microsoft Learn (authoritative):**
- Overview: https://learn.microsoft.com/azure/expressroute/expressroute-introduction
- FAQ: https://learn.microsoft.com/azure/expressroute/expressroute-faqs
- SKUs + features: https://learn.microsoft.com/azure/expressroute/expressroute-about-virtual-network-gateways
- ExpressRoute Direct: https://learn.microsoft.com/azure/expressroute/expressroute-erdirect-about
- Global Reach: https://learn.microsoft.com/azure/expressroute/expressroute-global-reach
- FastPath: https://learn.microsoft.com/azure/expressroute/about-fastpath
- Designing for HA: https://learn.microsoft.com/azure/expressroute/designing-for-high-availability-with-expressroute
- Designing for DR: https://learn.microsoft.com/azure/expressroute/designing-for-disaster-recovery-with-expressroute-privatepeering

**Azure Architecture Center (reference architectures):**
- Hub-spoke with ExpressRoute: https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke
- Connect on-prem to Azure: https://learn.microsoft.com/azure/architecture/reference-architectures/hybrid-networking/expressroute

**Azure Landing Zones (canonical ALZ):**
- Connectivity sub design: https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/network-topology-and-connectivity
- ALZ-Bicep ExpressRoute module: https://github.com/Azure/ALZ-Bicep/tree/main/infra-as-code/bicep/modules/expressRoute

**Pricing calculator + reference:**
- https://azure.microsoft.com/pricing/details/expressroute/
- https://azure.microsoft.com/pricing/calculator/

**Independent expert voices:**
- John Savill (azurearchitectures.com / YouTube): networking deep-dives, ExpressRoute episodes worth full watch
- Daniel Mauser (MS, learn.microsoft.com/users/danielmauser/): ER-specific guidance + field experience
- Microsoft Networking Tech Community blog: https://techcommunity.microsoft.com/category/azure-networking — best for new GA announcements

**Avoid (often outdated):**
- Generic Azure networking blogs older than 12 months
- Cisco/Juniper marketing materials about ER integration (often wrong on specifics)

## §11 ELI5 explanation

Imagine your office has a phone. You can call Microsoft over that phone — like everyone else calling Microsoft on regular phones — but during business hours the lines are busy and quality is unpredictable. ExpressRoute is installing a dedicated phone line between your office and Microsoft, just for you. The line is always available, always sounds the same quality, and nobody else can listen in. It costs more than regular phone calls, but if you need to be sure the call gets through clearly every time, you install the dedicated line.

## §12 Level-500 explanation

ExpressRoute architecture at the data plane: customer's BGP-speaking edge router(s) establish two eBGP sessions with Microsoft Enterprise Edge (MSEE) routers — primary and secondary, both active. BGP exchanges routes; default propagation includes Azure RFC1918 ranges (Private peering) and historically Microsoft IP space (Microsoft peering, deprecated for new circuits). BGP attributes used for path selection: AS_PATH, MED, LOCAL_PREF, BGP communities. Customer controls outbound preference via LOCAL_PREF; Microsoft controls inbound via BGP communities + MED.

Data plane: traffic ingresses MSEE at the peering location, enters Microsoft's WAN, traverses to the home VNet's ExpressRoute Gateway. Gateway runs in a managed PaaS form, with throughput SKU-determined. FastPath, when applicable, bypasses the gateway's data plane (specifically the gateway VM's vNIC bottleneck) by programming the underlying SDN fabric to send traffic directly between MSEE and the destination VNet VM's NIC — gateway still controls control-plane (BGP), but data plane is gateway-bypass. Critical: FastPath requires Ultra Performance gateway + Premium circuit + specific VNet topology (no UDR conflicts).

ExpressRoute Direct architecture differs: customer's router(s) connect via physical fiber to a Microsoft-owned port pair (10 Gbps or 100 Gbps) at the peering location. No connectivity provider in between. Customer is allocated a dedicated VLAN per circuit. MACsec, when enabled, encrypts at the Ethernet layer between customer's router and MSEE — keys managed via Key Vault, rotated per customer policy. Direct supports up to 200 Gbps aggregate (two 100 Gbps ports) with circuit-level QoS.

Global Reach implements a managed cross-circuit connection: BGP sessions established between two ExpressRoute circuits enable customer's on-prem networks to reach each other over Microsoft's backbone. Latency comparable to direct internet but with private routing. Billing: per-GB inter-circuit + circuit-level fees on both ends.

Failure modes: BGP session timeout (default 60s hold-timer) triggers failover to secondary connection. Provider-side failure isolates one connection. Metro-level failure (rare) requires dual-metro deployment to survive. Gateway-side failures during scheduled maintenance: zone-redundant gateways (ErGw*AZ SKUs) provide AZ-level redundancy.

Performance characteristics: latency is single AS hop to Microsoft WAN plus WAN-internal-routing. Jitter low (Microsoft backbone deterministic). Packet loss extremely low (private path). Throughput limited by gateway SKU unless FastPath active.

## §13 What it means for enterprise customer

For an enterprise CIO, ExpressRoute is connectivity insurance, not bandwidth purchase. The line item is monthly recurring + per-GB (Premium); the business value is predictability. It enables business outcomes that public-internet-routed Azure cannot guarantee: real-time financial transactions where latency variability is a regulatory issue, SAP/Oracle ERP migrations where IOps and microsecond consistency matter, telecommunications signaling where jitter destroys service quality, and regulated workloads where the auditor demands "the data never touched the public internet."

For the CFO: ExpressRoute moves connectivity cost from variable (cloud egress data charges on internet path) to semi-fixed (circuit fee + bounded outbound). The forecast becomes a budget line, not a quarterly surprise. For sustained outbound throughput above ~100 Mbps average, ExpressRoute is typically cheaper than per-GB internet egress.

For the CISO: ExpressRoute reduces external attack surface (no public-internet path to internal-only Azure resources), enables audit-friendly architecture (private path provable from end-to-end), and supports compliance frameworks that demand network isolation. It does NOT replace identity-based security — customers must combine ER (network) + Entra (identity) + Private Endpoints (PaaS) + Conditional Access (policy). The CISO who thinks ER alone is sufficient is missing 70% of modern security thinking.

For the procurement office: ExpressRoute commits the customer to a multi-year operational relationship with Microsoft. SKU choice locks redundancy semantics. Provider relationship adds another vendor to manage. The procurement complexity is higher than VPN Gateway, but the operational outcomes justify it for organizations with serious Azure investment.

Strategically: customers who choose ExpressRoute signal that Azure is core infrastructure, not a temporary experiment. It's not the right choice for a customer running 10 VMs as a side project. It IS the right choice for a customer running their P&L through Azure.

## §14 Commercial perspective

**Cost model:**
ExpressRoute pricing is structured as: monthly circuit fee (per circuit, per bandwidth tier) + per-GB outbound data (Premium tier only; Standard tier unlimited within geopolitical region) + optional ExpressRoute Direct port fees (per port pair, monthly) + optional Global Reach fees (per-GB inter-circuit, plus add-on monthly).

**Indicative pricing (as of 2026-05-28, USD, varies by region):**
- Standard tier circuit: 50 Mbps ~$55/mo, 1 Gbps ~$870/mo, 10 Gbps ~$8,200/mo (unlimited outbound in geopolitical region)
- Premium tier circuit: same Mbps tiers + ~2x base + per-GB outbound (typical $0.02-0.05/GB depending on destination)
- ExpressRoute Direct ports: 10 Gbps pair ~$3,200/mo, 100 Gbps pair ~$22,000/mo (port cost — circuits on top)
- Global Reach: ~$0.027/GB inter-circuit (varies by region pair)
- Gateway SKU: ~$140 (Standard) to ~$1,750 (Ultra Performance) per month

**POC viability:** Limited. Real ExpressRoute POC requires 1-3 weeks lead time, provider contract, and minimum monthly commitment. Better to scope POC as VPN Gateway hybrid pattern, then commit to ER as production deploy.

**First commercial commitment threshold:** Typical enterprise initial deploy is 1 Gbps Standard circuit + gateway + 12-month commit = ~$15-20k/year minimum. Customers below this scale should evaluate VPN Gateway alternative.

**Cost-trap warnings:**
1. **Premium tier per-GB outbound** — customer expects "ER = bandwidth I bought" then sees per-GB on bill. Educate before quote.
2. **Global Reach billing — separate from circuit fee** — multi-site customers underestimate this.
3. **Gateway in Premium tier** — Ultra Performance gateway adds ~$1,750/mo on top of circuit cost. Required for >2 Gbps throughput or FastPath.
4. **ExpressRoute Direct minimum commits** — port pair fee paid even if circuits underutilized.
5. **Inter-region data charges on Azure backbone** — when traffic crosses Azure regions internally, separate per-GB charges apply. Multi-region active/active customers see this.

## §15 Implementation flow — first meeting → CSA handover

**1. First meeting (SE, ~90 minutes).**
Discovery topics:
- Current connectivity: MPLS providers, bandwidth, geographic scope
- Azure investment scope: subscriptions, regions, workload types
- Compliance posture: regulatory frameworks, audit requirements
- Pain points: existing internet-based connectivity reliability, performance complaints
Outputs: high-level appropriateness check (ER vs VPN-Gateway), customer's near-term cost-tolerance window, named decision-maker on customer side
Voice for this meeting: business-outcome anchored. Field CTO role active (if not already).

**2. Discovery + scoping (SE + customer architect, ~3-5 working days).**
Architecture topics:
- Bandwidth forecast: current peak + growth trajectory (12/24/36-month)
- Geographic distribution: which sites, which Azure regions
- Redundancy requirements: single-circuit, dual-metro, multi-provider?
- Connectivity provider relationship + contracts
- BGP capability: customer's edge router capability + AS number
- Identity + network integration: AD, DNS, Entra Connect topology
- Security: MACsec requirement? Forced tunneling needs? NVA/firewall central inspection?
Outputs: scoped solution proposal, BOM (bill of materials), provider selection if applicable
Voice: technically precise. Solution Architect role active.

**3. Design proposal (SE + customer architecture board, ~1-2 weeks).**
Deliverables:
- Topology diagram (using customer's preferred tool or operator's design-html skill output)
- SKU recommendation with justification (Standard vs Premium, Direct vs Provider, Gateway SKU)
- Redundancy design with named failure modes covered
- Cost forecast (monthly + 12-month TCO including gateway + Global Reach if applicable)
- IaC drop-in references (Bicep modules from ALZ-Bicep or AVM, parameter values per customer choice)
- Compliance fit summary (regulatory frameworks satisfied + caveats)
Activities: walk customer architects through design, defend SKU choices, surface failure modes explicitly
Outputs: signed-off design doc

**4. Pre-sales technical close (SE, ~1 week).**
Topics:
- Final pricing validation with Microsoft + provider
- Provisioning timeline confirmed
- Customer-side prep: edge router config, IT-change-window, NOC training
- Initial test plan + acceptance criteria
- Contract terms (multi-year commit discounts if applicable)
- Voice gate on customer-facing artifacts (proposal, SOW): TrailblazerVoiceCritic if customer-engagement mode
Outputs: signed quote, provisioning request submitted, transition-to-implementation plan

**5. CSA handover (SE → CSA, ~1 day).**
Handoff package (cold-executor trio in v3.5 terminology):
- **plan.md (final):** signed-off design doc with all phase decisions
- **spec.md (final):** technical implementation spec with file-level Bicep, parameter values, provider config templates, BGP routing policy
- **prompt.md (self-contained):** brief for CSA to pick up — context, constraints, customer relationships, decisions taken + rationale, what's resolved vs what's open, who to contact for what
- Plus: customer's preferred communication style (from Field CTO persona context), audit-trail expectations, prior commitments made in pre-sales
Activities: live handover meeting between SE and CSA, customer introduction, transition of relationship ownership
Outputs: CSA owns delivery; SE remains advisor for strategic questions but withdraws from operational management

---

## §16 ExpressRoute-specific deep dive — BGP attributes and route control

Worth a dedicated section because BGP behavior surprises customer architects new to ExpressRoute.

**BGP attributes Microsoft advertises:**
- AS_PATH: short (single AS hop). Customer can prepend their AS to influence Microsoft's path preference (rarely needed).
- LOCAL_PREF: not advertised across eBGP (irrelevant to customer-Microsoft session).
- MED (Multi-Exit Discriminator): Microsoft sets these on advertised routes; customer can use for primary/secondary preference.
- BGP communities: Microsoft advertises communities indicating Azure region origin (useful for customer-side filtering or path-preference logic).

**Routes Microsoft advertises:**
- Per VNet linked to the circuit: RFC1918 ranges, max ~10,000 routes per circuit (Premium increases this).
- Customer can filter accepted routes via route maps to prevent accepting routes for VNets they don't need to reach (security best practice).

**Customer-side BGP control:**
- LOCAL_PREF: customer sets on their own routers to prefer primary connection over secondary (or vice versa). 
- AS-prepending: customer's own AS prepended on routes advertised to Microsoft, influencing inbound preference.
- BGP communities: tagged on routes for downstream processing (e.g., "this is production traffic, prefer ER path").
- Route filtering: deny-by-default + explicit allows, prevents accidental leak of internal routes to Azure.

**Common BGP mistakes:**
- Accepting default 0.0.0.0/0 from Azure (treats Azure as default gateway — usually unintended).
- Not filtering inbound: accepting all Azure routes, including ones for irrelevant VNets, causes RIB bloat on customer router.
- Symmetric routing assumed when actual is asymmetric (return traffic via different path) — diagnostically painful, often surfaces as application-layer timeouts.

For deeper coverage: John Savill has a multi-hour ExpressRoute series on YouTube that walks BGP scenarios. Worth the time investment before high-stakes customer engagements.

---

**Maintenance notes:**
- Re-verify §9 latest-greatest every quarter — Azure roadmap moves fast
- Update pricing figures (§14) at minimum every 6 months — pricing changes silently
- §15 implementation flow tweaks based on operator's real engagement experience — promote durable patterns
- If new ExpressRoute feature lands that materially changes design (e.g., new SKU): add §17+ for it, don't bury in §9
- When customer-question patterns emerge from real engagements: update §8 with the patterns operator has actually heard 3+ times
