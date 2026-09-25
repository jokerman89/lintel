---
slug: swarming-work
date: 2026-09-08
cycle_id: swarming-work-20260908
operator: jokerman
affected_paths:
  - lib/swarm-schema.json
  - lib/swarm_contract.py
  - bin/li-swarm.py
  - skills/swarm/SKILL.md
  - skills/{plan,build,review,resume,capture,cycle,full-engineering-pass}/SKILL.md
  - scaffolding/01-foundation/
  - docs/
risk_class: medium
breaking_change: false
---

# Structure change: swarming work

> Gate M1 (structure-impact analysis) artifact for the `swarming-work-20260908` meta-infra cycle.

## What changed (shape)

Add an optional swarm execution layer beside the existing schema-v1 work map. An opted-in
initiative gains a coordination JSON file plus separate charter, brief, report, and review Markdown
artifacts. A new canonical schema/parser and read-only CLI validate the topology and evidence. The
nine-phase cycle, task artifact authority, agent-role files, pack model, and sequential default do
not change shape.

The session protocol and scaffold gain portable coordination rules. Generated client surfaces gain
one swarm workflow adapter through their existing generators rather than a new adapter mechanism.

## Backward-compat

- Existing work maps without `execution_mode` and `coordination` remain valid.
- Existing PLAN/BUILD invocations remain sequential unless the initiative explicitly opts in.
- Existing tasks/spec/plan/prompt files keep their ownership and meaning.
- Hosts with sequenced or no subagent support replay the same artifacts without claiming native
  concurrency.
- Existing packs, hooks, manifests, and consumer repositories require no migration.

## Migration path

No migration needed — additive change. Existing initiatives may opt in by adding the two work-map
fields and valid swarm artifacts; they do not need to rewrite their mapped task content.

## Forward-compat

The shape enables alternate attributable isolation backends and additional read-only coordination
views without coupling the contract to one host. It deliberately forecloses shared-tree concurrent
writers without per-lane attribution and forecloses making coordination metadata a second task
backlog.

## Verification

- Shape-tests added: `tests/shape/swarm-contract.sh`
- Existing shape-tests affected: manifest identity, skill catalog, instruction synchronization,
  scaffold, work-map, and generated Copilot checks
- Regression coverage: focused unit tests exercise schema/path/topology/evidence failures; an
  integration fixture covers ready waves through close verification; one stable full suite validates
  the reconciled tree.

M2 compatibility, M3 shape evidence, and M4 post-build evidence will be appended during REVIEW and
CAPTURE. No pre-build statement is presented as completed runtime proof.

## Rollback procedure

Before release, revert the swarm commits in reverse order and remove only ignored runtime attempts
after confirming their work is accounted for. Because work-map additions are optional, no consumer
data migration is needed. After release, revert through a new patch release and keep the published
version immutable.
