# Reusable patterns: dependency topology and lane ownership

Status: split APPROVED by the parent (2026-09-28) after the independent re-review of the R2 contract
(`ae9d6df7`) accepted it for dependent dispatch. V09, V11 and all of P6 wait for the real integrated
join. Revision R2 (2026-09-28): the relaxed edges, the suffix splits and the package membership are
now written into the authoritative plan.md leaf items and its "Swarm execution packages" table, and
they are validated by `li-work-artifacts.py` and `li-swarm.py validate`/`wave`. This file keeps the
rationale. The coordination document is [swarm/coordination.json](swarm/coordination.json). The suffix
IDs are spelled `4.2.a.core`, `4.2.a.wf`, `4.2.b.core` and `4.2.b.wf`, because the swarm parser
recognizes dotted children of an original leaf. R1 spelled them `4.2.a.core` and so on; the meaning
is unchanged.

## Original graph (as declared)

Each leaf's `Deps` cell in plan.md names exactly one prerequisite. Extracted mechanically on
2026-09-28 from all 48 rows:

- 0.1.a has `None`. Every other leaf's single declared prerequisite is the leaf immediately
  before it in plan order.
- This includes the package boundaries: 1.1.a depends on 0.1.b, **2.1.a depends on 1.3.c**,
  2.2.a on 2.1.d, 3.1.a on 2.2.c, 4.1.a on 3.3.b, 4.3.a on 4.2.c, 5.1.a on 4.3.d, and 6.1.a on
  5.2.b.
- The declared edges therefore form one total order. The package table, however, groups
  leaves by owner and edit boundary. That is the basis for the split below.

This order was the planning author's conservative sequencing, not a record that every leaf
consumes the previous leaf's output. Only the edges changed below are relaxed. Every other
declared edge stands.

## Changed edges

| Leaf | Declared prerequisite | Proposed prerequisite | Justification |
| --- | --- | --- | --- |
| 2.1.a | 1.3.c | 1.3.c (unchanged) | Already starts right after P1; the pack lane needs no relaxation |
| 2.2.a | 2.1.d | 1.3.c | Includes/pins consume the frozen roots envelope. Tests build envelopes directly, and the implementation exists and is tested (build log) |
| 4.1.a | 3.3.b | 1.3.c and the frozen contract | The consumer reference documents only the frozen CLI/report. Its "real launcher" verification stays pending join with 2.1.c |
| 4.2.a, 4.2.b | 4.1.c; 4.2.a | split by file ownership (below) | Each leaf names both skill files (workflow lane) and core/CLI evidence functions (core lane). The plan permits suffix splits that keep requirement mapping |
| 6.1.a | 5.2.b | 2.1.d, 3.3.b, 4.2.b.core, 5.2.b, all integrated and reviewed | P6 is the serial join |

Suffix splits, both parts keeping the parent leaf's requirement IDs and verification keys.
The parent leaf is ticked only when both parts pass on the integrated branch.

- **4.2.a.core:** lock verification and package projection functions/CLI. Depends on 2.2.c.
- **4.2.a.wf:** `skills/build/SKILL.md` and `skills/resume/SKILL.md` wiring. Depends on 4.1.c.
- **4.2.b.core:** the `review` input validator, coverage verdict and exit 7. Depends on 4.2.a.core.
- **4.2.b.wf:** `skills/review/SKILL.md`, `skills/ship/SKILL.md` and the workflow-test cases.
  Depends on 4.2.a.wf.

## Explicit lane membership

| Lane | Member leaves (in execution order) | Entry prerequisite |
| --- | --- | --- |
| Core (integration owner) | 2.2.a, 2.2.b, 2.2.c, 3.1.a, 3.1.b, 3.1.c, 3.2.a, 3.2.b, 3.2.c, 3.3.a, 3.3.b, 4.2.a.core, 4.2.b.core | 1.3.c |
| Pack | 2.1.a, 2.1.b, 2.1.c, 2.1.d | 1.3.c |
| Workflow/visual | 4.1.a, 4.1.b, 4.1.c, 4.2.a.wf, 4.2.b.wf, 4.2.c, 4.3.a, 4.3.b, 4.3.c, 4.3.d, 5.1.a, 5.1.b, 5.1.c, 5.2.a, 5.2.b | 1.3.c and frozen contract |
| Integration (serial, core owner) | 6.1.a, 6.1.b, 6.1.c, 6.2.a, 6.2.b, 6.2.c | All lanes integrated |

Every one of the 48 original IDs appears exactly once above; 4.2.a and 4.2.b appear through
their suffix parts. Leaves already completed before the split (0.1.a-1.3.c) are not lane
members.

**Pending-join rule.** A lane leaf whose verification needs another lane's output stays open
until the integrated branch runs it. No lane ticks such a leaf. This covers:

- 4.1.a, 4.1.c, 4.2.b.wf and 4.2.c, which need the launcher (2.1.c) and core lock/review
  commands;
- 5.2.a and 5.2.b, which need V11;
- all of P6.

## File ownership (no concurrent writers)

| Owner | Files |
| --- | --- |
| Core | `lib/patterns.py`, `bin/li-pattern.py`, `tests/unit/patterns.py`, `tests/unit/patterns.sh`, core lifecycle/sharing/evidence tests, the canonical pattern skill (3.3.b), this initiative's plan files, ADR-0038 and the evolution entry. At integration only: `bin/li-copilot.py`, `bin/li-catalog.py` outputs, generated `.github/` adapters, `skills/CATALOG.md` and the docs of 6.1.a |
| Pack | `lib/profile_context.py` (only if strictly needed; no parser change), `lib/pack-resolver.sh`, `lib/paths.sh`, `bin/li-pattern` (launcher), `packs/_default/pack.yaml`, `lib/pack-schema.yaml`, `tests/unit/pattern-pack-origins.sh`, pack/roots tests |
| Workflow/visual | Canonical phase, document, engineering and frontend skill sources named in cards 4.1-5.2, the pattern consumer reference, `lib/pattern_visual.py`, `tests/integration/pattern-workflows.py`, `tests/unit/pattern-visual.py`, `tests/integration/pattern-visual-roundtrip.py` and their runner wrappers |

Lanes commit only inside their scope, on their own branch. The integration owner merges
reviewed lane commits serially, by ordinary merge or cherry-pick, never by rebase, reset or
amend. It then regenerates shared outputs from source and runs the targeted and full suites.
