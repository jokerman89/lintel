# Task-relevant intake

This is the shared question/authority procedure for SCOPE, DEFINE, PLAN and
inspection. It is instruction-driven, not a question daemon or an
automatic approval mechanism. Use the [Universal adapter](../../../shims/universal/ADAPTER.md)
and the [selected work map](../../spec-kit/references/work-map.md).

1. Separate the requested **operation** (read, review, plan, build, deliver) from
   its **topic**. Preserve the original request, selected work map, answered
   decisions and explicit authorization. A plan's approval is not release authority.
2. Read the relevant specification, existing decisions and supplied answers first.
   List only unresolved decisions that would materially change scope, acceptance,
   risk, data handling, an irreversible action or the implementation approach.
   If that list is empty, ask nothing and continue the authorized work.
3. Use the actual host question channel, whatever its name. If no question tool
   exists, ask in conversation. A denied/pending question permission remains
   blocked; do not bypass it through another channel. Ask one decision at a time,
   with concrete choices and a recommendation when justified.
4. Reuse an existing answer for the same decision and unchanged scope. State an
   ordinary low-risk assumption rather than interviewing again. An unresolved
   material decision blocks only its dependent action, not independent work.
5. Write decisions and their authority in the selected design/handoff; do not make
   another question ledger or task backlog. A changed decision identifies what
   changed and which original tasks/reviews need reconciliation.

## Choose questions by the work, not by size

| Work | Useful unresolved decisions |
|---|---|
| Defect or maintenance | Reproduction, intended behavior, regression boundary, acceptance |
| Migration | Source/target versions, compatibility, owned data, interruption/recovery |
| Research or comparison | Research question, source boundary, evidence quality, uncertainties |
| Feature or internal tool | User task, smallest useful outcome, constraints, viable alternatives |
| Explicit strategy | Demand or outcome evidence, status quo, smallest useful outcome, adoption, future fit |

L/XL size, a fresh repository, missing `scope.md` or an unfamiliar domain never
selects a strategy lens. `--lens strategy`, the explicit `--lens venture` spelling,
a task-relevant operator-selected pack lens, or the operator's strategy request
can select it. DEFINE retains strategic questions without making them universal
gates. `--mode minimal` reduces narration and optional exploration, not mandatory
risk, policy, approval or review obligations.

## Examples

- "Migrate this service to the supported runtime; keep its API" needs compatibility
  and rollout facts only if absent, not questions about startup demand or payment.
- "Research deployment options only" can produce sourced findings and uncertainty;
  it neither needs an approved implementation design nor grants deployment permission.
- "Implement approved T014" reuses the mapped acceptance and prior authorization.
  Do not ask for the same scope approval at intake, PLAN and pre-BUILD.
- "Should we build a new product for this unmet need?" can use demand, observed
  workarounds and the narrowest paying-user wedge. Mark unsupported premises rather
  than inventing market evidence or psychological traits.

Existing question-preference history remains inspectable data at its original
path. No runtime reader applies it, and entry consolidation does not delete it.
It cannot resolve a design conflict, change host permissions or override a
material decision. Record current decisions in the selected design/handoff.
