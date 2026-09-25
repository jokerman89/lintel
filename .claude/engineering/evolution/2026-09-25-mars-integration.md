---
slug: mars-integration
date: 2026-09-25
cycle_id: mars-integration-20260925
operator: jokerman
affected_paths:
  - skills/mars/
  - skills/review/references/method.md
  - skills/{cycle,plan,review,code-review}/SKILL.md
  - lib/{mars_contract.py,mars-defaults.json,mars-schema.json}
  - lib/{review_method.py,review-method-schema.json,review-questions.json}
  - bin/{li-mars.py,li-review-packet.py,li-copilot.py}
  - .github/skills/li-mars/SKILL.md
  - tests/unit/{mars-contract.sh,mars_contract.py,review-method.sh,review_method.py}
  - tests/shape/skill-descriptions-trigger.sh
risk_class: medium
breaking_change: false
---

# Structure change: MARS integration

> Gate M1 (structure-impact analysis) artifact for ADR-0036 (drafted as ADR-0034; renumbered
> 2026-09-25 because #104 holds 0034 and the client cleanup holds 0035).

## What changed (shape)

A new optional workflow, `/li:mars`, with a stdlib panel-state helper and a header schema.
A new shared reviewer layer: the Review Method document, a standing-question catalog with
stable IDs and advisory tag rules, a method library and a packet CLI. REVIEW's Stage 1/2
reviewer prompts became references to that packet. Four workflows gained one optional,
gated MARS paragraph each. The Copilot generator gained `mars` in `WORKFLOWS` and a required
`MARS_RESOURCES` closure. No phase, mode, frontmatter field, capability flag or pack field
changed shape.

## Backward-compat

Every workflow runs unchanged when MARS is absent, declined or unsupported: the offer gate
returns 3 and the caller says nothing. Existing MARS panels without method meta, input
binding or profile keep working; the new request and synthesis header fields are optional.
The REVIEW packet replaces prompt text only; its stage order, fix loops, Stage 3 policy
controls and the content-bound decision path are unchanged.

## Migration path

No migration needed — additive change. Projects may add `.claude/review/questions.json`
with a namespace to extend the standing questions.

## Forward-compat

Enables comparable single and multi-model reviews, per-question calibration data and
project/pack domain questions under namespaced IDs. The consolidated planning and quality
workflows adopt the method and the pending hooks listed in
`skills/mars/references/integration.md`. Forecloses role-played panels and model-specific
reviewer prompts: identity must come from host evidence, and the method never names models.

## Verification

- Unit: `tests/unit/review-method.sh` (catalog, selection, packet parity, coverage, decision
  rule, independence, calibration) and `tests/unit/mars-contract.sh` (roster, offer gate,
  panel ownership/close, method meta, input binding, overlap refusal, profile, inspection).
- Shape: `tests/shape/skill-descriptions-trigger.sh` now covers `mars`.
- Generator: the committed `.github/skills/li-mars/SKILL.md` equals the generator output;
  a portable bundle includes every `MARS_RESOURCES` path.
- Live: RM9 re-pilot evidence is recorded separately in `.claude/plans/mars/`.

## Rollback procedure

Revert the integration commits on `jokerman-microsoft-mars-integration`. Nothing else reads
MARS panel state or the method outcome log, both of which live in gitignored runtime paths.
