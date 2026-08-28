---
slug: <kebab-case-summary>
date: YYYY-MM-DD
cycle_id: <cycle id from job.yaml>
operator: <whoami>
affected_paths:
  - <path-1>
  - <path-2>
risk_class: low | medium | high
breaking_change: false               # true = requires migration entry
---

# Structure change: <slug>

> Gate M1 (structure-impact analysis) artifact. Created by CAPTURE under meta-infra mode per v4.0 design Chapter 4 §5.4.

## What changed (shape)

Describe the SHAPE delta, not the content. Example: "added `cli_support.degradation` sub-field; previously cli_support was a flat list."

## Backward-compat

Which existing usages continue to work without action? List explicit callsite classes.

## Migration path

If breaking-change=true: link to `docs/migrations/<date>-<slug>.md` with the full migration guide. Otherwise: "No migration needed — additive change."

## Forward-compat

What does this structural change enable or foreclose? Be explicit. Example: "Enables per-CLI custom degradation strategies. Forecloses single-CLI override syntax."

## Verification

- Shape-tests added: <list of new tests/shape/*.sh>
- Existing shape-tests affected: <list>
- Regression coverage: <statement>

## Rollback procedure

How to revert this change cleanly if it goes wrong. Include git refs + manual steps.
