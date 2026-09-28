---
slug: adaptive-review
date: 2026-09-28
cycle_id: adaptive-review-20260928
operator: current operator
affected_paths:
  - lib/review_context.py
  - lib/review_method.py
  - lib/review-questions.json
  - bin/li-review-packet.py
  - skills/review/references/
risk_class: high
breaking_change: false
---

# Structure change: Adaptive review

## What changes

Add consequence facts and explicit mandatory-question metadata to the existing
review packet. Add a lazy consumer of the separate patterns provider and an
offline observations evaluator. No new execution, policy or release engine.

## Backward and forward compatibility

Keep current packet/report headers and review/profile schemas. Legacy question
extensions default to advisory; new selected mandatory questions cannot be
reported not-checked and still pass. MARS uses exactly the same assessment.
Existing commands remain available; new depth and pattern options are additive.

No migration or automatic rewriting of old evidence. Old reviews do not gain
newly claimed coverage. The patterns provider and native client generation remain
separate explicitly checked integration dependencies.

## Verification

Planned: depth truth table, positive/negative coverage, single/MARS parity,
offline metric invalid/partial cases, provider absence and exact frozen-provider
join, reference sizes and focused existing shape checks. Actual outcomes belong
to the initiative's final review, not this prospective assessment.

## Rollback

Use ordinary revert commits for this initiative's feature commits after checking
dependent callers. Preserve review history and independent branches. Do not
rewrite Git history, silently downgrade old mandatory evidence or reuse a
published product version.
