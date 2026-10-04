# Interpreting scale and planning depth

SCOPE owns the initial scale judgment; PLAN revisits it against DEFINE's approved
design and the current repository. `lib/scale-estimator.sh` remains the existing
lexical hint API, not an ambiguity detector, policy engine or measured estimator.
Its `no`/`high` labels describe keyword rules. A keyword miss cannot prove that
ambiguity is absent, and an infrastructure word cannot prove that settled work
needs another interview.

Read the actual requested outcome and acceptance, existing answers and artifacts,
owners and interfaces, unknowns, and reversibility/rollback boundaries. Distinguish
facts with source paths from assumptions. Try two plausible readings in **any**
domain: for example, “reconcile records” could mean a one-off comparison or a
recurring correction workflow even when no infrastructure keyword matches.
Ask only when those readings materially change work, authority or verification
and the selected requirements do not already decide between them. Ask the one
unresolved question, not DEFINE's entire intake again. An unanswered material
choice stays unresolved; a conservative hint is not permission for the larger job.

Use those facts to interpret the size and `depth_schema` hint:

| Observed work | Useful structure |
|---|---|
| One bounded outcome/owner, few interfaces and a single rollback boundary | `flat` |
| Ordered milestones with distinct interfaces or acceptance checkpoints | `phased` |
| Nested outcomes and dependencies requiring separately owned or reversible stages | `tree` |

These are reasoning prompts, not new thresholds. Record why the selected structure
fits the actual work, including uncertainty and any departure from the lexical
hint. Preserve original IDs and settled approval; deeper structure does not expand
scope. Where no scope artifact exists, PLAN chooses the simplest sufficient shape
from the approved design rather than assuming all missing scopes are small.

All shapes retain ADR-0026's 2–5 minute leaves, dependencies and per-leaf acceptance.
Package grouping shares execution/review context, not authority or acceptance.
Split incompatible ownership, approval, risk or rollback boundaries. The nine
phases, mandatory policy/review controls and actual approval decision are unchanged.

`scale_token_estimate` returns one whole-cycle prior plus basis/sample count.
An uncalibrated prior is a planning hint, not measured usage, model capacity,
elapsed time, a price or evidence that a resource limit is satisfied. CAPTURE's
calibration writer is dormant under ADR-0008. No new counter or automatic writer
is implied. Present the signals once at PLAN's actual decision point; re-open only
a changed or unresolved scope/resource boundary, not permission already granted.
