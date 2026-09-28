# Review-method sources and limits

**Reviewed:** 2026-09-28. These public sources informed original review questions,
not copied proprietary prompts or standard text. Revisit a source when its
applicability changes; source age alone neither proves validity nor invalidates
unchanged evidence. Pack/project owners maintain their own applicable policy.

| Source | Useful public idea | Boundary |
|---|---|---|
| [Microsoft MDASH introduction](https://www.microsoft.com/en-us/security/blog/2026/05/12/defense-at-ai-speed-microsofts-new-multi-model-agentic-security-system-tops-leading-industry-benchmark/) | Prepare context, develop hypotheses, challenge, deduplicate and seek evidence; compare correct sibling implementations | Public architecture, not published agent prompts or a portable checklist |
| [MDASH overview](https://learn.microsoft.com/en-us/security-exposure-management/ai-code-security-overview) and [FAQ](https://learn.microsoft.com/en-us/security-exposure-management/codename-mdash-faq) | Independent validation; read-only review versus developer-initiated repair; complement deterministic analysis | Preview product, nondeterministic model analysis; no Lintel performance equivalence |
| [Microsoft SDL](https://learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle) | Independent code review, security testing and staged rollout | A documented practice is not evidence it ran here |
| [STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) | Threat coverage by trust boundary | Not a mandatory full-system diagram on every change |
| [Zero Trust](https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-overview) | Explicit verification, least privilege and assume breach | Configuration and actor/action scope still need evidence |
| [Microsoft agentic failure taxonomy update](https://www.microsoft.com/en-us/security/blog/2026/06/04/updating-taxonomy-failure-modes-agentic-ai-systems-year-red-teaming-taught-us/) | Approval, inter-agent trust, tool metadata and durable-memory risks | Blog read; linked taxonomy PDFs not inspected for this change |
| [NIST SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | PO.4 verification criteria, PW.7/PW.8 review/testing, RV.3 related weakness analysis | Risk-based framework, not certification; [1.2 source](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd) was a draft when reviewed |
| [OWASP ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0) | Versioned technical verification coverage | CC BY-SA 4.0; reference and write original questions, do not reproduce requirements wholesale |
| [Claude Code Ultrareview](https://code.claude.com/docs/en/ultrareview) | Separately verified findings | Anthropic feature, not Microsoft's method; internals and parity are not established |
| [CyberGym paper](https://arxiv.org/abs/2506.02548v3) and [FAQ](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/FAQ.md) | Fixed task identity, metric definitions and evaluation isolation | Known-vulnerability reproduction is not secure-code-review quality |
| [Sangfor write-up](https://github.com/Sangfor-AI/cybergym-submission-sangfor-ai-v2) | Separate exploration from final acceptance; preserve rerun reasons | Entrant report, not an independently reproduced comparison |
| [Alipay write-up](https://github.com/Alipay-Risk-Tech/CyberGym-Writeup/blob/main/WRITEUP-20260906.md) | Conservative result accounting and environment auditing | Host-enforced isolation cannot be replaced by prompt instructions |
| [Microsoft evaluation follow-up](https://www.microsoft.com/en-us/security/blog/2026/06/17/beyond-the-benchmark-advancing-security-at-ai-speed/) | Hold the model constant and attribute misses to stages | Any-crash and designated-final metrics are not interchangeable |
| [Wiz Atlas](https://www.wiz.io/blog/atlas-ai-vulnerability-researcher) | Challenge and deduplicate; evaluate true and false positives | Public methodology, not a license to copy implementation or claim its results |

Lintel adopts bounded preparation, concrete evidence, refutation, sibling-pattern
checks and honest evaluation. It does not adopt autonomous exploit generation,
large always-on fleets, mandatory multi-model panels, extra company-policy
schemas or automatic updates of review policy. Existing MARS consent, profile
resolution and content-bound release controls remain authoritative.

No external benchmark material is bundled. CyberGym harness code is Apache-2.0;
the inspected dataset card and example-agent repository did not supply a usable
blanket redistribution license. Review fixtures are self-authored observations,
not republished vulnerabilities or target archives.
