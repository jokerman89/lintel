# Review: reusable patterns implementation package

> Historical planning review of the original session bundle (baseline `00136c9d`).
> It is not implementation evidence. BUILD evidence is in [build-log.md](build-log.md);
> the reconciliation with the later architecture is in [reconciliation.md](reconciliation.md).

Status: planning package prepared for BUILD approval. Date: 2026-09-24.
Scope: proposed spec, build cards and handoff, not runtime code.
Baseline: `00136c9d`; repository working tree was clean before preparation.

## Discovery and reconciliation

The earlier policy-hook restrictions no longer blocked direct reads in this turn.
Architecture, core principles, personas, recent lessons and ADRs 0005, 0008, 0015,
0016, 0018, 0024 and 0026 were inspected. No content-exclusion bypass was used.
Read existing plan templates, work-map validator, Copilot generator, pack interfaces
and frontend roundtrip test. No docs/risks directory was present in the inspected
checkout; constraints are traced to accepted architecture and the risks in spec.

Changes from the initial proposal:

- One canonical deep example; other domains use small synthetic test fixtures.
- Define explicit catalog binding activation rather than treating keyword matches
  as automatically authoritative.
- Require same-snapshot pack source provenance, including inherited block behavior.
- Keep normal brief/profile/corpus precedence; mandatory bindings are explicit.
- Immutable approved content with catalog lifecycle events and CAS publication.
- Distinguish legacy visual schema version 1 from universal schema version 1.
- Separate actual host behavior from schema/structural checks.
- Keep the entire planning package outside the repository as requested; promotion
  and map rebasing are a named first implementation card.

## Independent review and corrections

A read-only `lintel-reviewer` reviewed the initial bundle and focused source
contracts. It reported zero P1 and eight P2 findings. The coordinator resolved
all eight in the specification and corresponding build cards:

| Finding | Resolution and acceptance |
| --- | --- |
| F1: publication/index/lifecycle ambiguity | Catalog field list includes lifecycle. Publication is explicit; index rechecks only registered entries and preserves events. Removed/staging files never reappear. Approval requires explicit new version. Cards 3.1.b/c add the three regression sequences. |
| F2: missing attestation contract | Section 4.5 defines exact source/pattern identity, digest, reviewer, validity and renewal semantics. CLI consumes attestations before resolve/verify/review. Card 3.2.b tests wrong digest, expired, URL and renewal cases. |
| F3: invocation and binding authority gaps | Section 4.3 defines explicit reference roles and overrides. Section 7 defines add/replace/remove binding changes with CAS and reduced-baseline preview. Cards 1.3.c/3.2.b cover these branches. |
| F4: no ancestry transport | Section 3 specifies one JSON snapshot, ordered cached ancestry and locator/content-ID distinction. Card 2.1.b checks null, inheritance, fallback, pointer change and missing-origin behavior. |
| F5: task-map shape missing | Section 4.6 defines task/package/clause inventory and mapping digest separate from selection digest. New map command persists it; card 2.2.c verifies coverage and stale evidence. |
| F6: visual projection unspecified | Section 9 defines small setting-to-field/type/comparison table, final-value application, unknown-setting limits and precise pattern/profile precedence. Card 5.1.c checks actual spec values and negative review. |
| F7: imported draft hashes break dependencies | Section 7 specifies destination source/version mapping, children-first transformation/re-hashing, inert original provenance, no external refs, and local approval sequence. Card 3.3.b covers multi-pattern closure. |
| F8: nonvisual standalone consumers missing | Section 8 inventories shared document pipeline, direct document renderers/template slots and engineering entries. Cards 4.3.a-d add coverage; real direct document generation/negative QA is a separate host acceptance requirement. |

Further coordinator checks clarified that unrelated catalog additions do not
invalidate pinned requirements; changed mandatory bindings do require re-planning.
Automatic selection rejects bound drafts/retired/revoked patterns. Asset filters,
monotonic lifecycle transitions and bundle manifest shape are explicit.

These are coordinator-verified corrections following an independent first pass.
An independent second-pass confirmation was not obtained: the sync review agent
could not accept a follow-up message. Do not label the corrected version as
independently approved. There are no known unresolved contract findings in this
planning delivery; BUILD still performs independent package reviews.

## Planning validation

The existing `bin/li-work-artifacts.py` passed with this artifact directory as the
explicit --repo validation root and work.json as --map. This proves the scratch
bundle's map/paths are internally valid, not that it is installed or committed.
The first implementation card promotes/rebases the map into the repository.

A read-only Python check verified:

- 48 unique pending leaf cards across P0-P6; no completed build checkbox.
- Every dependency exists earlier in the plan; the graph is acyclic.
- All 16 requirements are mapped in both directions between spec and cards.
- The two fenced JSON transport/mapping examples parse.
- Local companion links resolve.
- Named existing skill paths and compatibility test scripts exist in this checkout.

The independent first pass separately confirmed the original 44-card graph and
work-map validity; the coordinator verified the revised 48-card graph.
`git diff --check` and `git status --short` showed no repository changes.
No package dependencies were installed and no generators modified the checkout.

## Handoff state

Current deliverable: spec, 48 build cards, cold-executor prompt, work map and this
review record. All files are in session artifacts; the earlier proposal is
superseded as implementation input. Read prompt.md to begin a later authorized
BUILD. The original repository memory/plan ledgers and other sessions are unchanged.
No production permissions, build approval or merge authority is inferred from
this document's completion.

## Runtime evidence

Not applicable to this planning delivery. No runtime code written, no pattern
resolver executed, no cloud resource inspected, no pack installed and no merge made.
All implementation cards remain unchecked.
