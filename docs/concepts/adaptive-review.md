# Adaptive review

Lintel uses one Review Method for focused review, BUILD packages, independent
cross-checks and optional MARS panels. Adaptive depth spends more effort where a
mistake has serious consequences without making a mechanical change launch an
agent fleet.

Use `/li:review --depth auto` for the normal path, `--depth lean` to request the
cheap path or `--depth deep` for explicit additional assurance. Native clients
use their generated `li-*` spelling. Known production, untrusted-input,
sensitive-data, irreversible, security-boundary or shared-impact changes require
deep; a lower explicit request is refused. Unknown facts remain unknown, not a
low-risk exemption. Facts and their declared source are visible to the reviewer.

Deep adds targeted questions and evidence, not automatic model selection or MARS
consent. Existing specification, mandatory policy, content-bound review/QA and
independence obligations remain. A checksum, review heading or agreeing panel
does not establish release authority.

## What improves

Reviews ask about concrete failure inputs, sibling implementations, caller
compatibility, tenant/object authorization, network destinations, resource
limits, cryptography, memory/state ownership, agent/tool authority and recovery
where those surfaces apply. Reviewers try to refute findings, distinguish traced
evidence from hypotheses and preserve unexamined work. Confirmed defects get
builder-owned corrections and regression evidence rather than a second rubric.

Required question IDs are recorded before observations in method metadata v2
and the exact packet body. An unexplored required question is incomplete;
explained optional exploration remains visible. Grounded question N/A does not
waive an applicable mandatory control. Single and MARS reviewers receive the
same body and assessment semantics.

Configured company or repository patterns use their existing provider and current
selection lock. Mandatory clauses and selected defaults are not truncated or
re-ranked by review depth. Only an explicitly relevant selected document is read;
a whole company knowledge base is not loaded. Missing required provider/policy
evidence is unavailable, never an empty success.

## Cost and evidence

Depth and packet helpers are local, standard-library operations: no network,
model or scanner calls. The optional offline evaluator measures supplied review
observations and separately aggregates imported CyberGym verification receipts.
It does not execute vulnerabilities or establish a leaderboard result.

Public MDASH, SDL, SSDF and Ultrareview ideas informed the method; proprietary
internals were not copied. No claim of equivalent detection performance follows
from the design. Establish gains through matched held-out tasks, independent
adjudication and actual measured overhead.

See [operating commands](../../skills/review/references/adaptive.md),
[security evidence](../../skills/review/references/security.md),
[evaluation](../../skills/review/references/evaluation.md) and
[sources and limitations](../../skills/review/references/sources.md).
