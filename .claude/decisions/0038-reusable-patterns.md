# ADR-0038: Data-only reusable patterns

**Status:** Accepted within the authorized 2026-09-24 reusable-patterns implementation.
**Authority:** `.claude/plans/reusable-patterns/implementation-release.md` and the work map
`.claude/plans/reusable-patterns/work.json`. This decision is not evidence that any leaf
is implemented; per-leaf evidence lives in the initiative's build log.
**Related:** ADR-0005, ADR-0008, ADR-0015, ADR-0016, ADR-0018, ADR-0024, ADR-0026 through
ADR-0031, ADR-0033, ADR-0034.

## Context

Teams repeat the same expectations across work: deployment topology, dashboard behavior,
document structure, visual language. Lintel has no local, evidenced way to state such an
expectation once, decide whether it applies to a named target, carry it into a plan and
check it at review. Loading all knowledge into instructions loses relevance and evidence;
a hosted retrieval service adds a new operational system before a local contract exists.

## Decision

Add one data-only pattern runtime. `lib/patterns.py` (Python standard library) is the
single validator and resolver; `bin/li-pattern.py` is its CLI and a Bash launcher supplies
resolved roots as JSON on stdin. A pattern records expectations (`must`, `default`,
`recommendation` clauses), applicability selectors, provenance and optional hashed local
assets. A blueprint is a pattern with exact includes. Catalogs publish immutable versions
and record lifecycle/revocation events; bindings state which patterns a named context
requires or defaults to. Repository, active-pack and personal scopes are explicit, and
personal patterns are never applied automatically.

Authority is bounded and additive:

- `must` clauses are mandatory only when reached from a required binding or required
  explicit reference; unknown required context blocks dependent work rather than guessing.
- Default precedence is explicit authorized task choice > repository > active pack >
  explicitly selected personal pattern > the existing corpus/model fallback. With no
  selected pattern, ADR-0016's brief > profile > corpus order is unchanged.
- Pack identity and provenance come from the ADR-0029 profile record; no second manifest
  parser or cache. Fallback or error contexts block pattern-dependent resolution.
- Pattern clause coverage is supplemental content evidence consumed by the ADR-0028
  review contract; it never clears missing or stale independent review.
- Nothing in a pattern is executed, fetched or used as shell input. Declared URLs are
  provenance only. A repository can forge a binding, so this is not enterprise enforcement.

## Upgrade notice

The neutral pack gains the optional field `patterns.source: null`. Under ADR-0029, that changes
the neutral manifest digest. Every existing bound profile context, including one used only by
unrelated callers such as `resolve_pack_field`, therefore reports `PROFILE_DRIFT` until an explicit,
reason-bearing rebind (`rebind_profile_context "<reason>"`). This is intended fail-closed
behavior:

- Nothing rebinds automatically.
- Snapshot drift is never ignored.
- Work planned against the old context is re-planned after the rebind.
- One-shot reads without a bound context are unaffected.

## Alternatives

1. Keep expectations in instructions and memory. Rejected: no relevance selection,
   provenance, versioning or review traceability.
2. A hosted retrieval or policy service. Rejected for now: new operational authority and
   lifecycle before the local contract is proven.
3. **Selected:** a small local, versioned, data-only contract reusing the existing pack,
   work-map, review and adapter mechanisms.

## Consequences and verification

The precedence change applies only when a pattern is selected. Existing callers with no
configured sources behave as before. Behavior tests with synthetic roots (unit, launcher,
workflow and visual integration) establish runtime behavior; host/model acceptance is a
separate evidence category and is recorded as deferred when unavailable. Rollback is an
ordinary revert of the feature; no pattern history or user data is deleted.
