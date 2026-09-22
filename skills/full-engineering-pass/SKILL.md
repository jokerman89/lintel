---
name: full-engineering-pass
layer: foundation
workflow_root: true
description: Use for a customer engagement or major release that needs the whole engineering picture at once — composes all five domain modules (architecture, data, security, devops, testing) in dependency order. One invocation produces architecture decisions, a data model, a security posture, an ops plan, and quality validation together.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Cross-domain work lacks a verified dependency chain between architecture, data, security, operations and quality; isolated positive scores can conceal a missing requirement."
navigation:
  primary_intent: produce end-to-end engineering artifacts with original work and evidence identity
  triggers:
    - engagement or release explicitly requiring all engineering domains
    - operator types /li:full-engineering-pass
    - active workflow requests cross-domain depth
  sibling_workflows:
    - /li:ta — architecture first
    - /li:da — data after architecture
    - /li:sc — security after architecture
    - /li:dh — hosting after upstream evidence
    - /li:tq — validation of the prior domains
  risk_level: high
  auto_mode_eligible: false
  estimated_tokens: 500000
domain:
  composition_dag:
    - stage: 1
      modules: [ta]
      parallel: false
    - stage: 2
      modules: [da, sc]
      parallel: true
    - stage: 3
      modules: [dh]
      parallel: false
    - stage: 4
      modules: [tq]
      parallel: false
  cap_soft: 500000
  cap_hard: 750000
  partial_rollout: retain missing requirements and block dependent acceptance
  override_allowed: --skip-module only for a grounded optional exclusion
---

# Full engineering pass

Compose TA -> DA/SC -> DH -> TQ without inventing an execution engine. The module
methods remain in their canonical skills and retained role bodies. The caller owns
actual tool dispatch, explicit handoffs and verification, using the
[shared module procedure](references/domain-handoff.md#module-caller-procedure).
This is not a tenth phase. SENSE -> SCOPE -> DEFINE -> DISCOVER -> PLAN -> BUILD ->
REVIEW -> SHIP -> CAPTURE remains the lifecycle; resume is a utility.

Use for a genuinely cross-domain request, not an ordinary fix or mandatory venture/
customer interview. Direct single-module and single-capability entry points remain.
The historic 500k/750k planning hints are uncalibrated advice, not measured usage,
host context capacity, a spending authorization or an automatic model setting.

## Composition DAG

| Stage | Modules | Depends on | Required handoff |
|---|---|---|---|
| Stage 1 | TA | original accepted requirements | decisions, interfaces, dependency graph, NFRs and actual consumer impact |
| Stage 2 | DA and SC | selected TA artifacts | schema/migration/retention and threats/auth/control/audit evidence |
| Stage 3 | DH | TA, DA, SC | deploy/recovery, signals/SLOs, capacity/cost and on-call plan |
| Stage 4 | TQ | TA, DA, SC, DH | consumer tests, performance/coverage/regression and recovery evidence |

```yaml
stages:
  - stage: 1
    modules: [ta]
    parallel: false
    depends_on: []
  - stage: 2
    modules: [da, sc]
    parallel: true
    depends_on: [ta]
  - stage: 3
    modules: [dh]
    parallel: false
    depends_on: [ta, da, sc]
  - stage: 4
    modules: [tq]
    parallel: false
    depends_on: [ta, da, sc, dh]
```

`parallel: true` means eligible, not observed concurrency. Default to serial DA then
SC unless the selected approved work map opts into the existing Swarm coordination,
disjoint write ownership and actual attributable isolation. Reuse `/li:swarm` only
when those prerequisites hold; do not implement another scheduler or infer permission
from an environment variable. Shared data/security decisions may require serialization.

## Workflow

1. **Retain the requested operation.** Preserve selected map/package/leaves, actual
   cycle/phase and approved outcome. Full, `--resume` and `dry-run` retain their
   meaning: dry-run inspects/reports without domain execution or successful results.
2. **Discover from trusted source.** Read `skills/<module>/SKILL.md` under
   `LINTEL_SOURCE_ROOT`, not the target repository's potentially hostile/missing
   `skills/`. Do not search another installation or silently download a module.
3. **Fix expected scope before observations.** After live P07 verification and
   original work-reader admission, construct the accepted domain request with every
   required domain/checkpoint/control. Select real receiver modes and original file
   preimages. Explicit advisory preferences are distinct from required policy.
   Do not infer expected domains from whichever results happen to be present.
4. **Stage 1:** perform TA's methods and verify required upstream artifacts. Hand
   original IDs/profile/ref and exact artifact identity to DA/SC. Proposed decisions
   are not accepted decisions; obtain missing material choices through the actual
   host question channel, without repeating already granted authority.
5. **Stage 2:** perform DA/SC with scoped receivers. Migration planning and SQL
   artifacts do not imply live migration. Security reviewers never repair findings.
   Record actual starts/results; preserve both successful and failed observations.
6. **Stage 3:** DH uses verified upstream state/constraints and actual SLO/cost
   sources. Release planning does not imply deploy/merge/publish authority.
7. **Stage 4:** TQ tests actual requirements with inspected authorized runners.
   Zero tests, missing browser/renderer or skipped mandatory checks stay unverified.
8. **Verify and review.** Persist artifacts before external final P05 preparation.
   Fresh domain summary and actual QA must consume the same context. Request real
   independent spec then quality and use P05's latest applicable reader/corroboration.
   Only the original task owner updates original status after those gates.

The callable data commands in the [reference](references/domain-handoff.md) validate,
record, verify and summarize; they never perform the domain action. Do not paste
slash commands into a shell loop or report a suggested command as a completed one.

## Missing required domains and honest composition

Missing required domains, checkpoints, upstream artifacts or applicable mandatory
controls block dependent acceptance even when four other domains score 100.
Missing optional capabilities may be reported as partial scope with a grounded
exclusion; `--skip-module` does not change required obligations. If exclusion would
change the approved outcome, obtain that scope decision and fresh bound acceptance.
Unknown applicability is not optional. Continue truly independent authorized work
without claiming a complete composed pass.

The 30-dimension view (six advisory dimensions per module) remains useful feedback,
not a release mechanism. GREEN means observed required engineering gates and actual
independent acceptance hold in the selected scope; YELLOW denotes only advisory
concerns/grounded optional exclusions; RED denotes an unmet required gate. None is
SHIP authority and none overrules the exact control outcomes.

## Cold handoff and loop

Use one explicit handoff naming cycle ID, selected map and original task paths,
request/initial/final context, operation/iteration, actual artifacts, last observation,
next owner/action and any unknown side effects. Use the accepted runtime namespace
`.claude/runtime/state/domains/<operation>/iNNNN/`, not colon-bearing time filenames.
Preserve previously selected module artifacts as history rather than overwriting them.

`--resume` uses `workflow_resume` with the saved cycle/map then the shared cold-attempt
table. A started step without result is interrupted, not permission to replay a
deployment/migration/test. Identify the first unmet checkpoint from the original
request, verify live policy and reconcile actual receiver output. A revised loop
creates a new iteration with original prior-result references and affected checks.
No direct reset/rollback, guessed newest report or new lifecycle phase.

## Delivery and observation

Return an original-ID/requirement-to-domain evidence table, actual checks/tool actors,
artifact paths, mandatory blockers/advisories and next owner. Recording does not
prove review; the domain core always returns `release_clearance: false`.
The outer SHIP workflow still requires actual P05 same-context review/QA plus
publication authorization.

Brief Forge or audit use is explicit where configured; no new interception/hook
activation is implied. Installed consumer closure is a separate check against the
accepted installer. Local source/provider or copied-source tests cannot substitute.
