# Synthetic inventory plan

This is fixture task data, not a second Universal initiative. T001-T003 are
original fixture IDs and must not be replaced with A24 IDs or another backlog.
All profile variants start from these identical bytes.

## Work packages

| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Acceptance evidence | Review |
|---|---|---|---|---|---|---|
| P1 | Correct offline inventory reconciliation | T001, T002, T003 | Released native implementer; `inventory.py`, `plan.md` | - | Immutable business oracle; applicable resolved-policy evidence | substantive |

P1 requires independent SPEC followed by quality review. The table's Review
cell uses the existing reader's exact `substantive` value. Edits to plan.md are
limited to actual design/profile/handoff prose and original task progress.

## Original leaves

- [ ] T001 Select the algorithm and publication boundary against R1-R6 and actual profile sources.
- [ ] T002 Implement inventory.py without changing the frozen business requirements (depends T001).
- [ ] T003 Run business and applicable policy acceptance; leave a cold handoff and request independent review (depends T002).

## Design and profile impact

Not authored. A native implementer must supply an actual decision and source
trace here after the coordinator releases that actor. Identical valid choices
across profiles are acceptable; differences must not be forced.

## Cold handoff

Not authored. Preserve original IDs, source revision, target identity, exact
profile reference, actual last completed work, evidence and next action.
