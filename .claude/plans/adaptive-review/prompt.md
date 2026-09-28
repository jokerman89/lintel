# Cold-executor prompt: Adaptive review

## Context

The operator authorized a separate implementation improving Lintel's review
questions, risk-adaptive depth, established company/repository patterns and
honest evidence before shipping. This is not a new autonomous security scanner.
Read [spec.md](spec.md), [plan.md](plan.md) and [work.json](work.json) in full.

Existing Review Method and MARS contracts remain canonical. Two disjoint writer
lanes implement review-context helpers and offline evaluation; the coordinator
integrates them into the existing packet and adds compact workflow references.
Preserve all original T1-T12 IDs, acceptance and dependencies.

## Constraints

- Work only on this initiative's feature branch and owned files.
- Do not edit `.claude/plans/todo.md`: it is byte-bound historic authority.
- Do not alter the held review-remediation backlog, native-client-parity
  generators/adapters/hooks/cli_support or its 0.13.0 version reservation.
- The frozen patterns source is `64338b6c9fc30fb3618cc9f46b66d8b0d2ab1e7c`.
  It is not on main or release-cleared. No copying its whole stack or editing its
  artifacts. Use its exact public provider API for an isolated compatibility test.
- No personal/enterprise documents, credentials, benchmark exploits or live
  systems are accessed. Public sources support original questions, not copied
  proprietary checklists.
- No benchmark rank or model-quality gain is claimed without real matched runs.
- Requested worker configuration is Opus 5.5 / high / long_context. Actual 1M
  capacity is unverified. Do not hardcode this configuration into the product.

## Acceptance and continuation

Follow every card's checks. Keep real independent review separate from
implementation. Selected mandatory unknowns, provider failures and missing
independence cannot become PASS through a score or a table heading.

Runtime cycle is `adaptive-review-20260928`, original coordinator
`d9057650-8028-439a-85da-5849b5470136`; selected profile is the local neutral
ADR-0029 context. Resume through its actual verified reference; do not rebind
silently or borrow another checkout's profile.

Start by checking the plan's current status and Git state. Validate the explicit
work map and swarm topology before dispatch. Workers write only their own lane
and report. Coordinator alone updates shared records, commits and integrates.
Use `python -B` and the existing Bash test runner; no additional dependencies.

Delivery remains a feature commit/PR, not a deployment. If authenticated
publication is unavailable for the authorized account, preserve the exact branch
and report the blocker without reading or switching credentials.
