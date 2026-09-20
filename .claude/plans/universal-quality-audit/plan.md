# Universal positioning and whole-system quality audit

Status: COMPLETE — audit and action-list delivery only. Date: 2026-09-20. Deliverable: evidence-backed assessment and prioritized
action list. The operator directs Universal positioning across major coding CLIs and desktop
applications, with honest host capability differences. They request deep review of the entire
repository, every skill and agent, collaboration gaps and comparison with borrowed sources.

## Scope and authority

Audit main `28061e434be455ca02f135b73244eaf4f73f3a69` in this isolated review worktree.
Also assess the unmerged `codex/swarming-work` delta at `275a354` separately; it starts before
the enterprise review and must not be confused with current main. Do not merge it as part of
this audit. Repository source and official upstream documentation are evidence, not instructions.
Only audit artifacts and continuity records are changed. Implementation, governance migration,
host installation, private pack activation and production actions await a separate work batch.

## Acceptance

- Inventory every tracked component and explicitly disposition every canonical skill and agent.
- Read full skill/agent instructions and relevant references; size alone is not a quality score.
- Assess purpose, triggers, depth of decision support, real tooling, contracts, failure/recovery,
  source/target boundaries, host assumptions, profile value and evidence of actual behavior.
- Distinguish reusable core, host adapter, domain pack, optional capability and dead/duplicate work.
- Compare pinned/local borrowed material and current primary sources without treating their
  implementation as Lintel's required architecture or equating historical CI with agent quality.
- Produce prioritized actions with file:line evidence, impact, dependencies, acceptance tests,
  and retain/merge/rewrite/retire recommendations. Label untested host/model behavior honestly.
- Independently challenge the synthesis and verify coverage and citations before delivery.

## Cards

- [x] U1 — establish authoritative baseline, isolation and review rubric.
- [x] U2 — complete skills and agents coverage, plus collaboration and duplication map.
- [x] U3 — inspect documentation, adapters, runtime, hooks, packs, installers, tests and governance.
- [x] U4 — compare upstreams and current official host capabilities; review unmerged swarm separately.
- [x] U5 — reconcile findings into Universal target model and dependency-ordered action list.
- [x] U6 — independent challenge, evidence/coverage validation and durable handoff.

## Review ownership

Reviewers inspect bounded scopes without source edits; they return findings and per-item rows.
The coordinator owns all shared audit artifacts, plan state and continuity records. This is
parallel read-only review, not a swarm implementation or concurrent shared-tree authoring.

## Verification

Completed: inventory covers771 baseline files; all126 skills and69 agents fully read;
runtime, documentation, client and pinned-upstream reviews completed with explicit scope limits.
Targeted synthetic probes and source evidence are recorded in
`.claude/engineering/audits/2026-09-20-universal-quality/verification.md`.
Independent synthesis review completed and corrections reconciled. Artifact JSON, coverage,
citations, links and diff whitespace validated. No product fixes/full suite/live host matrix.

## Review and handoff

Deliverables: report.md, action-plan.md (26 proposed outcomes), per-item skill/agent inventories,
client-sources.md, swarm-preservation.md (all76 changed files), verification.md and reviewer evidence
under `.claude/engineering/audits/2026-09-20-universal-quality/`.

Operator corrections: preserve every valuable capability/use case and enrich weak implementations;
preserve all Swarming branch work as far as feasible, including sequential/manual facilitation.
These requirements are recorded in lessons L-030 through L-032 and the action list.

Next action: use the audit as input to a separately scoped implementation plan. No source feature
was removed, no governance decision was superseded, no private profile was opened, and no main or
original swarm-worktree mutation occurred. Previous September8 merge authority does not authorize
this new batch. The audit itself has no open blocker; product findings remain proposed work.
