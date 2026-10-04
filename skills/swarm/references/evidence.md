# Names behind coordination contract IDs

These retained IDs came from the Universal implementation packages. They are
cross-reference labels, not scores, phases or new authorities. Keep persisted
IDs and each contract's own version unchanged.

| ID | Named owner and actual source | Boundary to retain |
|---|---|---|
| P03 | Owned context selection/checkpoints: `bin/_context.sh`, `lib/context_safety.py`, `lib/native_paths.py`; owned rollback: `bin/li-snapshot.py` | Exact target identity, path/link admission, exclusions, byte bounds and source digests. Reading a checkpoint never restores source or authorizes another target. |
| P04 | Swarm topology/local observations and envelopes: `bin/li-swarm.py`, `lib/swarm_contract.py`, `lib/swarm_snapshot.py`, `lib/brief-forge.sh`, `lib/envelope_contract.py` | Original work/leaf IDs, attributable scopes, attempts and local report bindings; explicit validated/audited handoff, not dispatch or shared clearance. |
| P05 | [Content-bound review/QA evidence](../../review/references/evidence.md): `lib/review_contract.py`, `lib/review-schema.json`, `bin/li-review-evidence.py`, `bin/li-review-log`, `bin/li-review-read` | Raw base/HEAD/index/worktree snapshots, immutable QA obligations, latest applicable decision and real independent corroboration. Local normalized Swarm hashes are not interchangeable. |
| P07 | Content-bound profile: `lib/profile_context.py`, `lib/profile-context-schema.json`, `lib/pack-resolver.sh` | Verify the complete reference (`schema_version`, `context_id`, `generation`, `digest`, `name`, `version`) and unchanged `required_policy`. Missing/drifted required policy is blocked; no implicit bind/rebind/transfer. |
| P08 | [Selected work and lifecycle](../../spec-kit/references/work-map.md): `bin/li-work-artifacts.py`, `lib/workflow.sh`, `lib/state.sh` | Original map/spec/plan/tasks/prompt and package/leaf IDs; map-first cold resume, canonical phase and original operation/authority, not another backlog. |
| P09 | Domain observations: `lib/domain_result.py`, `lib/domain-result-schema.json`, `bin/li-domain-result.py` | Recheck declared starts/results/artifacts against the selected P05 context and live P07 profile. Domain QA is not independent review; `review: not_evaluated` and `release_clearance: false` remain. |
| A22.7 | Historical shared-consumer integration card in `.claude/plans/universal-implementation/packages/P04.md`; implemented join in `lib/swarm_evidence.py` and `bin/li-swarm.py` | Reuse the above providers with joined evidence and final integrated review; a component result does not establish programme/client acceptance. Consult its original record for historical status, not an inferred current verdict. |

The **one** shared-consumption procedure remains
[Swarm's shared-evidence consumer](../SKILL.md#shared-evidence-consumer). This
reference only names its dependencies; it is not a duplicate pipeline.
Resume, handoff budgeting and Brief Forge use these same owned-context, evidence,
work and profile contracts. Helper output, fixture actors and role labels never
prove model efficacy, policy enforcement or independent review.
