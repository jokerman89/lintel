# ADR-0034: MARS multi-model review and one shared Review Method

- **Status:** Accepted direction, 2026-09-25; merge timing and version assignment remain with
  the coordinator. Decision D1 below is adopted as designed and flagged for operator
  confirmation at merge.
- **Date:** 2026-09-25
- **Deciders:** the operator (requested MARS, its defaults, a live four-model pilot, and
  integration "according to our plan"); implemented on `jokerman-microsoft-mars-integration`
- **Supersedes:** —
- **Superseded by:** —

## Context

Lintel had several host-specific "outside voice" hooks (review Step 6, define's cross-model
opinion, plan-eng-review, code-review's Codex gate) and no way to put the same question to
several different models deliberately. Hosts such as the Copilot App now select a model per
child context and record which model ran, but many hosts override or fall back silently.
Swarm (ADR-0027) fans out implementation; it is the wrong tool for a targeted second look.

The reviewer instructions Lintel sent were thin and divergent: REVIEW's Stage 1/2 prompts
were a few lines each, and every review skill defined its own dimensions and P1 meaning.
The 2026-09-24 pilot showed the cost: a documented happy path returning the wrong page
was P2 for one model and P1 for three, a split caused by the rubric, not the models.

## Decision

We added `/li:mars` (Multi-Model Adversarial Review & Screening): a canonical skill plus
stdlib data helpers (`bin/li-mars.py`, `lib/mars_contract.py`, `lib/mars-defaults.json`,
`lib/mars-schema.json`). The helper resolves the latest model per family from the host's
live list, gates offers and keeps panel state; it never dispatches, consents or closes.
The coordinator dispatches with host tools, registers every child and closes only
registered, owned, collected nested sessions.

We made one Review Method (`skills/review/references/method.md`, `lib/review-questions.json`,
`lib/review_method.py`, `bin/li-review-packet.py`) the only reviewer text: stable standing
questions selected by subject kind and surface tag, four evidence levels, one consequence-
based severity rubric and a report shape with explicit per-question coverage. A single
REVIEW reviewer and every MARS slot receive byte-identical packet bodies; only the header
differs. The method library imports no entry point, so REVIEW runs without MARS and MARS
runs without a cycle.

Gating: automatic offers only at PLAN's approval gate of a canonical nine-phase cycle, or
once per standalone review workflow, and only when the host proves separate contexts,
per-child model selection, allowed delegation and observable identity for two or more
distinct models. Auto mode, silence and an offer are never consent. Defaults: latest
Claude (Opus first), GPT, Grok and MAI; extra-high effort and 1M context, clamped per model
and recorded; one blind pass and a challenge round only when contested.

Evidence: repository subjects are bound with the content-bound review snapshot
(ADR-0028); mutable records overlapping the selection are refused before any write, a
changed input blocks dispatch and inspection, and the selected profile reference (ADR-0029)
is recorded. `panel inspection` emits `purpose: inspection`, `release_clearance: false`.

**D1:** in REVIEW panel mode, REVIEW records its stage decision through the existing
content-bound path from the adjudicated panel result, using the same decision rule as a
single report (any P1 fails; missing coverage, a partial panel or a changed input is
incomplete, never a pass; P2 requests changes). MARS alone never clears anything;
standalone MARS stays advisory.

## Alternatives considered

- **Prompt-only skill.** Rejected: gating, close safety, identity evidence and coverage
  cannot be tested, and single and panel prompts would drift.
- **Provider-API runner.** Rejected: credentials, routing and billing outside host policy
  (R11), and a model catalog to maintain.
- **Keep per-skill rubrics and add MARS beside them.** Rejected: multi-model and single
  results would not be comparable, and upgrading one path would leave the other behind.

## Consequences

- **Positive:** one place for multi-model review; one reviewer packet whose standing
  questions carry durable risk knowledge instead of model-specific coaching; silence is
  visible because coverage is required; the decision rule is shared and tested.
- **Negative:** reviewer packets are longer; reports must fill a coverage table (the MARS
  word limit rose to 900). Identity is only as strong as the host's evidence. Reviewers cost
  tens of thousands of input tokens per call in a large repository with either transport
  (nested sessions 45-75k in the first pilot; subagents 40-71k first-call input in RM9).
  Subagents are the default because nothing needs closing, not because they are cheaper.
- **Neutral:** no `supports_mars` capability flag; eligibility is read from live host facts.

## Implementation notes

Applied: cycle Step 5 (surfaces PLAN's recorded answer, never offers), plan Step 10
(option E), review Stage 1/2 (method packet) and Step 6b (panel mode), code-review
(optional panel), Copilot `WORKFLOWS` and the MARS resource closure. Pending on the native
planning and quality consolidation: the inspection workflow replacing plan-eng-review,
define's spec review, cross-check and CodeReviewer
(`skills/mars/references/integration.md`). A repository-wide drift guard (no rubric outside
the method) waits for that consolidation; today's guard covers REVIEW's prompts.

## References

- `.claude/plans/mars/` (spec, research, pilot, review-method design, plan, status).
- ADR-0026, ADR-0027, ADR-0028, ADR-0029.
- `tests/unit/mars-contract.sh`, `tests/unit/review-method.sh`.
