# Security evidence for review

This is an on-demand guide for the [shared method](method.md), not a scanner or a
new checklist to run wholesale. `lib/review-questions.json` owns question IDs and
selection. Use applicable questions, the real task's controls and the established
SC specialists. The [source register](sources.md) separates public ideas from
unverified product and performance claims.

## Make a claim testable

For a suspected defect, identify the protected asset, actor, controllable input,
entry point, trust boundary, sensitive operation, actual configured control and
observed consequence. Trace callers and failures, not just the suspicious line.
A dangerous-looking API or absent local guard is not proof of a reachable defect;
conversely, vendor documentation is not evidence of a deployed guard.

Use E1 for an actually executed authorized check and E2 for a concrete source
trace. Keep E3 patterns and E4 hypotheses labeled, with the smallest observation
that would settle them. Confidence does not change consequence-based severity.
Try to refute a finding before reporting it; preserve unresolved evidence rather
than turning it into a pass or a certain accusation.

Short, existing repository-local checks and benign synthetic fixtures are preferred.
This workflow does not generate exploits, orchestrate vulnerability reproduction,
contact live targets, test discovered credentials or change access to prove a claim.
Needed checks outside authority remain explicit handoffs, not covert retries.

## Spend effort at the actual boundary

| Surface | Questions / existing roles | Evidence worth obtaining |
|---|---|---|
| Identity and object/tenant authorization | SQ-AUTH-01/02; SecurityAuditor and applicable OAuth/JWT specialists | Identity-to-action/object decision, cache/job scope, negative authorization checks; authentication and residency are not tenant isolation |
| Paths, parsing and interpreter boundaries | SQ-PATH-01/02, SQ-INJ-01, SQ-PARSE-01 | Real source-to-use trace, containment/encoding contract and bounded regression coverage |
| Outbound network and resource use | SQ-NET-01, SQ-LIMIT-01 | Destination/redirect restrictions, credential forwarding, enforced size/depth/rate/retry/time limits and cancellation |
| Secrets and cryptography | SQ-SEC-01, SQ-CRYPTO-01; SecretsScanReviewer | Redacted flow, actual library/configuration, key lifecycle and safe failure; never disclose or try a secret |
| Memory, state and concurrency | SQ-MEM-01, SQ-CONC-01, SQ-DATA-01/02 | Ownership/lifetime, atomicity, interrupted or duplicate operation, old/new reader compatibility |
| Agents, tools and persistent knowledge | SQ-INJ-02, SQ-AGENT-01/02/03 | Actual host permissions and argument-bound approvals, attributable delegation, pinned tool definitions, provenance and correction of durable knowledge |
| Supply chain and delivery | SQ-DEP-01, SQ-REL-01/02 | Exact reviewed artifact and dependency identities, applicable scan/build results, rollout containment and evidenced recovery |
| Company/project invariants | SQ-CONTEXT-01 | Current provider-verified lock, applicable clauses and selected defaults, original task mapping and coverage |

Deep review adds SQ-DEEP-01: challenge the highest-consequence assumption with
separately attributable evidence. It does not imply every surface exists.
Uncertainty adds SQ-RISK-01; it cannot silently classify production as local.

## Use established implementations and close the loop

SQ-U11 compares a relevant sibling implementation's invariant, ordering and
ownership with the changed code. Similarity alone is not a bug, and a familiar
company pattern is not automatically an applicable requirement. Check its
version, owner, scope and accepted exception through the existing provider.

Deduplicate findings by the same root cause and smallest corrective change,
keeping every distinct consequence and evidence link. For an accepted defect,
look for the same unsafe assumption in related owned call sites, within the
authorized scope. The builder repairs and adds a regression check where feasible;
a separate reviewer verifies the revised result. Do not let the reviewer fix its
own finding or silently expand into unrelated remediation.

Record accepted/rejected/escaped outcomes with the existing `outcome` command.
Recurring false positives justify a reviewed wording proposal, not suppression
of rare catastrophic-risk checks. Evaluate the method on clean and decoy cases as
well as defects; count incomplete observations and actual supplied overhead.
