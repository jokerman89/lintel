# Adaptive review research

**Checked:** 2026-09-28.
**Method:** two separately delegated public-source research contexts, requested
Opus 5.5 / high / long_context. No private Microsoft sources, proprietary prompts,
target execution, benchmark downloads or dataset redistribution.
**Attribution:** Microsoft-method research `452869ff-04da-45f6-84d3-55d59592a56c`;
benchmark research `fd6c6b65-476c-41c7-bd46-80390824af4c`.

## Findings and decisions

MDASH is Microsoft's multi-model agentic scanning harness, not an open checklist
that can be copied. Public sources describe preparation, candidate analysis,
adversarial validation, deduplication and evidence. The internals are unpublished.
Lintel already has independent review, evidence levels, challenge rounds and
content binding. Its useful increment is consequence-based depth, more precise
questions and measured outcomes, not another always-on agent fleet.

Public Ultrareview is an Anthropic Claude Code feature, not a Microsoft method.
Neither product's marketing or reported measurements establishes Lintel parity.
AI review complements deterministic tests/scanners and human review; instructions
or a metadata label do not become host enforcement.

CyberGym Level 1 measures reproduction of described known vulnerabilities, not
secure review or unknown-bug discovery. Its task, model, attempt, environment and
success definitions differ between published results. Offline aggregation is
useful for honest evaluation accounting, but cannot establish leaderboard rank
or perform that reproduction task.

## Source register

| Source | Verified public basis | Adopted idea / limitation |
|---|---|---|
| [Microsoft MDASH introduction](https://www.microsoft.com/en-us/security/blog/2026/05/12/defense-at-ai-speed-microsofts-new-multi-model-agentic-security-system-tops-leading-industry-benchmark/) (2026-05-12) | Described staged pipeline, specialist analysis, counterpoint review and sibling implementation evidence | Prepare only relevant context; refute candidates; group equivalent fixes; inspect established patterns |
| [MDASH overview](https://learn.microsoft.com/en-us/security-exposure-management/ai-code-security-overview) (docs commit `0b053a0617bb799097c154f5b42a14bff23748b7`) | Public product behavior and preview architecture | Source facts are dated, not a claim about available tools in this session |
| [MDASH FAQ](https://learn.microsoft.com/en-us/security-exposure-management/codename-mdash-faq) (docs commit `ca3ec480f63e518feb0b49af7f07ff2baacb5038`) | Read-only scan, developer-initiated fixes, manual/static-analysis complement; nondeterministic asynchronous review | Keep review and repair separate; do not promise a deterministic model verdict |
| [Microsoft SDL](https://learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle) (docs commit `ebb697feb5b7b5ad004d15352007f09b759613a4`) | Threat modeling, independent review, testing and staged release | Consequence-triggered boundary and rollout questions |
| [STRIDE threats](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) (docs commit `2862bc030bf88db4a315e37429f65194a585312d`) | Threat categories, not deployment evidence | Coverage vocabulary only; no exhaustive diagram for a typo |
| [Zero Trust overview](https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-overview) (docs commit `a84ca5373964512a66ae39357f5e9c4a6070986b`) | Explicit verification, least privilege, assume breach | Tenant, tool and action authority must be checked at the boundary |
| [Microsoft agentic failure taxonomy update](https://www.microsoft.com/en-us/security/blog/2026/06/04/updating-taxonomy-failure-modes-agentic-ai-systems-year-red-teaming-taught-us/) (2026-06-04) | Public discussion of approval, delegated trust, tool metadata and cross-session memory risks | Original agent-authority and durable-knowledge questions; linked PDFs were not read |
| [NIST SSDF v1.1 final](https://csrc.nist.gov/pubs/sp/800/218/final) and [PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) | PO.4, PW.7/PW.8, RV.3: criteria, review/testing and related weaknesses | Explicit acceptance, evidence, follow-up variants; v1.2 remains [draft](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd) in this research |
| [OWASP ASVS](https://github.com/OWASP/ASVS/tree/v5.0.0) (5.0.0, CC BY-SA 4.0) | Versioned verification requirements and assurance levels | Reference source/version; do not copy requirement text into MIT source |
| [Claude Code Ultrareview](https://code.claude.com/docs/en/ultrareview) (retrieved 2026-09-28) | Public feature promises independent verification; internals unpublished | Evidence and separate review, not copied orchestration/billing or parity claim |
| [CyberGym paper](https://arxiv.org/abs/2506.02548v3) (v3, 2026-03-24) | 1,507 tasks, 188 projects, known memory-safety reproduction | Not a review-quality metric; no execution integrated |
| [CyberGym FAQ](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/FAQ.md#L17-L25) | Exactly one designated final submission for primary result | Never choose the best attempt after the fact |
| [Submission contract](https://github.com/sunblaze-ucb/cybergym/blob/7656b71d07da6694e262f9c34ea994cd4849c0eb/SUBMISSION.md) | Final metric, cost and per-instance exits | Fixed inventory and provenance, supplied costs only |
| [Verification record](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/src/cybergym/server/pocdb.py#L16-L41) | Agent/task/hash identity, nullable vulnerable/fixed exits; no final marker | Operator final designation is separate; no artifact contents read |
| [Timeout semantics](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/src/cybergym/server/server_utils.py#L28-L43) and [re-verification filter](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/src/cybergym/server/__main__.py#L217-L219) | Code 300 is timeout, not a successful crash | Null, 0 or 300 never success; fixed exit must be 0 |
| [CyberGym leaderboard](https://www.cybergym.io/cybergym/) (retrieved 2026-09-28) | Team-submitted stochastic runs with differing trials; page's any-of wording conflicts with FAQ | Preserve metric difference; no Lintel rank or comparative claim |
| [Sangfor write-up](https://github.com/Sangfor-AI/cybergym-submission-sangfor-ai-v2) | Exploration/acceptance separation; controlled-ablation limitations | Preserve failures and infrastructure reruns explicitly |
| [Alipay write-up](https://github.com/Alipay-Risk-Tech/CyberGym-Writeup/blob/main/WRITEUP-20260906.md) | Conservative exit accounting, environment isolation and trajectory auditing | Isolation is a host fact, not prompt text |
| [Microsoft pipeline evaluation](https://www.microsoft.com/en-us/security/blog/2026/06/17/beyond-the-benchmark-advancing-security-at-ai-speed/) | Model-held-constant comparison and stage-attributed misses | Measure changed method with matched model/tools; do not mix any-crash and target metrics |
| [Wiz Atlas](https://www.wiz.io/blog/atlas-ai-vulnerability-researcher) | Reproduction/discovery distinction, validation and deduplication | Clean/decoy/defect cases and false-positive measurement |

CyberGym harness code is Apache-2.0. The inspected dataset card did not declare a
license, and example-agent code had no license. Dataset archives contain third-party
source. Nothing from those datasets, agents or proprietary tools is bundled here.

## Adopted and rejected approaches

Adopt source-attributed questions, contract/sibling comparisons, strong evidence,
refutation, deduplication, bounded additional review, explicit uncertainty and
matched held-out evaluation. Required controls remain bound before observations.

Reject a 100-agent default, automatically required multi-model panels, new
pack-specific review parser/fields, model-confidence-based severity changes,
autonomous exploit construction and generated-proof pipelines. Preserve MARS
consent and consequence-based severity. Do not retire rare severe controls because
few incidents were observed. Cost reduction must preserve stale-approval,
wrong-selection, policy-drift and role-play-independence defenses.

## Unverified outcomes

No live model comparison, CyberGym task execution, leaderboard submission,
scanner-availability claim or internal company-pattern acceptance occurred.
Scorer fixtures can validate arithmetic and refusals only. The actual provider
join and source tests belong to the implementation evidence, not this research.
