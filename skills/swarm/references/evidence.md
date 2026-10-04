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

The shared-consumption procedure below is the single owner, not a duplicate pipeline.
The [main Swarm method](../SKILL.md) retains its public invocation and integration contract.
Resume, handoff budgeting and Brief Forge use these same owned-context, evidence,
work and profile contracts. Helper output, fixture actors and role labels never
prove model efficacy, policy enforcement or independent review.

## Shared-evidence consumer

The contract table above names the actual providers. The following procedure uses
those owners without duplicating or weakening their gates.

The CLI first calls the accepted trusted `li-work-artifacts.py` `work_context` provider for
`status`, `wave`, `resume` and `verify`. Optional `--map` must agree with the explicit
coordination backpointer; omission uses only that backpointer, never `LINTEL_WORK_MAP`,
recency or another active initiative. Original artifact paths, package/leaf identity and the
provider's bounded input selection must be valid. Empty, missing or over-bound selected
inputs block rather than selecting a decoy. The returned `work_context` is the provider's
read-only view: source checkboxes, manifest bytes and incomplete IDs do not grant acceptance
or create another hash/backlog. Composition stays in the CLI because the reader itself calls
Swarm validation; the Swarm libraries do not import it.

`status`, `wave`, `resume` and `verify` all use the same gate in `lib/swarm_evidence.py` when
local report/review checks are complete. Supply explicit `--profile-home`, `--profile-packs`
and `--profile-pointer` (optionally `--profile-context-file`); verification never creates,
rebinds or transfers a profile pin.

1. Before observations, the coordinator selects accepted work, original package/leaf IDs and QA
   obligations, then prepares an initial P05 context using its actual `prepare` CLI. P05 context,
   review and QA are v2; profile/work map/corroboration and P09 wrappers keep their own v1 formats.
2. Produce actual reports, evidence and optional domain results. After they exist, prepare an external
   final P05 context retaining the same non-snapshot fields and original base/input selection.
   Cover all declared product scopes, the exact local report/review files and actual evidence.
   A real selected parent directory such as `src` covers a lane's `src/core` and its future files;
   redundant child selectors are unnecessary. Individual child files, sibling prefixes and a
   selected file pretending to be a parent do not cover the whole scope. A deleted parent still
   counts when the verified P05 snapshot binds its former tracked descendants; an unobserved
   missing parent does not.
   Bind the full coordination, charter and brief as P05 acceptance sources. Do not embed the final
   context/digest in a report it hashes or exclude a whole report directory.
3. The common gate checks map/package/leaf/attempt and actor consistency, invokes P07's actual
   `verify_profile_reference` and `required_policy`, and consumes P05's actual review verifier,
   log-backed `li-review-read` and `verify_qa`. Later applicable rejection or malformed evidence
   blocks every acceptance path. Missing/retyped/downgraded obligations cannot be repaired by an
   aggregate score. Independently supplied host/human corroboration remains caller-trusted evidence,
   not something synthesized from role names or test actors.
4. With `domain_request`, P09 freshly verifies all declared starts/results/artifacts/evidence against
   that final context and live profile. Its `qa` must equal the selected P05 QA; its
   `release_clearance: false` and `review: not_evaluated` remain explicit. No-domain work uses
   ordinary P05 QA. Domain observations never substitute for independent review.
5. Verification-only work uses the authoritative no-change purpose; selected product states must
   remain unchanged. Mechanical packages may explicitly request non-independent review. Substantive
   manual/no-subagent work stays open without real host/human corroboration.

P05 owns raw base/HEAD/index/worktree snapshot semantics. Staging, committing or integrating selected
content can require new preparation and actual affected review even when a local normalized digest
is unchanged. Do not alias the two digest formats or call a P04 local PASS shared clearance.
Unchanged relevant inputs may reuse P05 evidence under its own rules; unrelated commits are not
automatic revocation. Pins are target-specific and missing runtime evidence is not reconstructed
from chat. Historical v1/v2 records remain untouched; new shared evidence is prepared separately.

The selected-work and cold-resume join consumes the accepted P08 mechanical providers without
changing their semantics or claiming completion of P08's agent-driven workflow. Joined
enterprise/hybrid/Swarm evidence, coordinator-generated outputs, final integrated REVIEW and
actual client evidence still gate **A22.7**. All Swarm CLI outputs remain observations, not
permission to publish or mutate external systems.
