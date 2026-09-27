# Reusable patterns: dependency topology and lane ownership

Status: PROPOSED by the integration/core owner at the P1 milestone; the parent approves
before dispatching any dependent lane. Leaf IDs, requirement mappings and acceptance in
[plan.md](plan.md) are unchanged; only the dependency edges below are relaxed.

## Original graph

The plan's 48 leaves form one chain: each leaf depends on the previous leaf
(0.1.a -> 0.1.b -> 1.1.a -> ... -> 6.2.c). A single chain permits no disjoint parallel lane.

## Proposed safe reordering (after P1 is frozen at 1.3.c)

| Lane | Leaves | Relaxed prerequisite | Why it is safe | Join point |
| --- | --- | --- | --- | --- |
| Core (integration owner) | 2.2.a, 2.2.b, 2.2.c, 3.1.a-3.3.b, the core/CLI parts of 4.2.a-4.2.c | 2.2.a depends on 1.3.c (not 2.1.d) | Pins, lifecycle and sharing consume the frozen roots envelope; tests build synthetic envelopes without the launcher | Pack lane merge before 6.1.c |
| Pack | 2.1.a, 2.1.b, 2.1.c, 2.1.d | 2.1.a depends on 1.3.c | Launcher, paths and pack field only produce the frozen envelope; no core file changes | Core integration; end-to-end launcher checks in 6.1.c/V12 |
| Workflow/visual | 4.1.a-4.1.c, 4.3.a-4.3.d, 5.1.a-5.2.b, skill text of 4.2.a-4.2.c | 4.1.a depends on 1.3.c and the frozen CLI table | Skills and the adapter consume the frozen report and CLI; commands not yet implemented are called only by their contract | V09/V11 real roundtrips close after core 2.2.b-3.3.b and pack 2.1.c are integrated |

Unchanged serial gates: P6 (6.1.a-6.2.c) starts only after all three lanes are integrated;
shared generators, catalog, adapters, plan/evidence reduction and the feature PR stay with the
integration owner. A lane leaf whose verification needs another lane's output stays open
(`pending join`) until the integrated branch runs it; no lane marks such a leaf complete.

## File ownership (no concurrent writers)

| Owner | Files |
| --- | --- |
| Core | `lib/patterns.py`, `bin/li-pattern.py`, `tests/unit/patterns.py`, `tests/unit/patterns.sh`, core lifecycle/sharing/evidence tests, the canonical pattern skill (3.3.b), this initiative's plan files, ADR-0038, the evolution entry, `bin/li-copilot.py`, `bin/li-catalog.py` outputs, generated `.github/` adapters, `skills/CATALOG.md`, docs of 6.1.a |
| Pack | `lib/profile_context.py` (only if strictly needed; no parser change), `lib/pack-resolver.sh`, `lib/paths.sh`, `bin/li-pattern` (launcher), `packs/_default/pack.yaml`, `lib/pack-schema.yaml`, `tests/unit/pattern-pack-origins.sh`, pack/roots tests |
| Workflow/visual | Canonical phase, document, engineering and frontend skill sources named in cards 4.1-5.2, the pattern consumer reference, `lib/pattern_visual.py`, `tests/integration/pattern-workflows.py`, `tests/unit/pattern-visual.py`, `tests/integration/pattern-visual-roundtrip.py` and their runner wrappers |

Lanes commit only inside their scope on their own branch. The integration owner merges
reviewed lane commits serially (ordinary merge or cherry-pick, never rebase/reset/amend),
regenerates shared outputs from source and runs the targeted and full suites.
