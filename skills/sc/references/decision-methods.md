# Security and compliance decision methods

Use to reason about a specified design or implementation, not to initiate scans of
live systems. ThreatModelDrafter owns design threats; SecurityAuditor and specialist
reviewers assess implementation evidence; implementers repair; legal/control owners
decide policy applicability and accepted residual risk. Role labels do not prove
independence. Use the existing [control/evidence contract](../../review/references/evidence.md).

## From a pattern to an actionable finding

Identify the protected asset, attacker-controlled input, entry point, transformation,
trust boundary, sensitive sink and missing control. Record what was read, what was
actually exercised, relevant versions, confidence and the missing observation.
A suspicious function name is not an exploit path; an absent code check is not
proof that no platform control exists. Conversely a platform brochure is not evidence
that a control is configured for this deployment.

Use synthetic invalid inputs with scoped local tests. Do not try a discovered secret,
contact a third-party endpoint, fetch private policy or change a permission to prove
a finding. Findings cite redacted locations and evidence IDs, never secret values.

## Synthetic worked example: token substitution

An API receives a correctly signed ID token intended for a web client. A signature-only
check accepts it, but the API's access-token audience/type contract rejects it.
JWTSecurityReviewer traces the verifier's configured algorithms, trusted issuer keys,
audience and token-kind rules through to the authorization decision. It proposes
negative tests for wrong issuer, wrong audience, wrong type, expiry and untrusted key
locations, not a replacement crypto implementation.

Reading a token header to select among already trusted keys is not itself a failure.
Letting its `alg`, `jku` or `x5u` choose a new trust policy or arbitrary fetch is.
Validation call order differs between libraries; no claim may authorize an action
before all applicable cryptographic and claim checks succeed. Cache TTL, overlap
during rotation and token lifetime derive from provider behavior and risk, not
one-hour, one-day or annual universal cutoffs.

OAuthFlowReviewer separately examines the grant/client and callback binding. A
client-credentials flow has no browser callback to protect with `state`. Native
loopback/custom-scheme redirects have RFC-defined rules distinct from web callbacks.
For authorization-code flows, inspect S256 PKCE, transaction binding and downgrade
protection. Establish which approved mechanism supplies CSRF protection rather than
flagging `state` absence without checking the flow.

## Policy applicability is not implementation evidence

For each obligation retain the actual source/edition/date, jurisdiction, regulated
actor, processing/system scope, applicability rationale, owner and evidence period.
A mandatory unknown/error is not N/A; an advisory preference is not silently mandatory.
An ISO/SOC policy document can describe a control but cannot prove it operated over
the audit period. Reuse evidence across frameworks only when scope and period fit
each obligation; do not claim that one checkbox certifies several regimes.

For GDPR, determine purposes and means per processing activity rather than inferring
controller/processor from who "owns" data. EU residency can be a real contractual
requirement; it is not a universal substitute for Chapter V transfer analysis.
For the AI Act, keep AI-system classification, actor duties, GPAI-model obligations
and phased application dates distinct. Refer unsettled interpretation to counsel.
No proprietary standard text is needed in a role body.

## Sources

- [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.txt), sections 3.1, 3.8-3.12:
  algorithm/key binding, issuer/audience validation and cross-JWT confusion.
- [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.txt), sections 2.1, 2.4 and 4.7:
  current OAuth security BCP and CSRF/PKCE applicability.
- [RFC 8252](https://www.rfc-editor.org/rfc/rfc8252.html), sections 7-8:
  native redirects and external user agents.
- EDPB, [Controller or processor](https://www.edpb.europa.eu/sme/learn-the-basics/data-controller-or-data-processor_en).
- European Commission AI Act Service Desk, [Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6)
  and [Article 43](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-43);
  verify the current applicable EUR-Lex text and amendments before a legal assessment.
