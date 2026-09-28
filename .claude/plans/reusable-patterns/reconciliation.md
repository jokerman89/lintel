# Reusable patterns: implementation reconciliation

Date: 2026-09-28. Card 0.1.a. Owner: the integration/core implementation session
(branch `jokerman-microsoft-patterns-core-integration`) beneath the parent coordinator.

## Authority and baseline

- Operator authority, 2026-09-24 22:38 +02: BUILD after the legacy cleanup, nested
  long-context High swarming, then a feature PR and a normal `main` merge after CI and
  review. Recorded in [implementation-release.md](implementation-release.md), which is
  the coordinator's release of this bundle and supersedes the planning-only DRAFT and
  no-publication wording of the original bundle for this feature only.
- Prerequisite PR #104 merged 2026-09-27T21:07:41Z at
  `224135581d4dd71f18d39efe5c0882b7e65ec76d` (reviewed head `22d502be`).
- Implementation base: `origin/main` at `7ba544a49f62d7e0eadb8ec383f07b3ba73a0b54`
  (merge of #100), later advanced by an ordinary merge of `origin/main`
  `fa8ddce5249b8730638644f8f59381d341361ea6` (#99, #108). It contains the #104 merge and the later client/docs batch
  (#94-#98, #100, #107, ADR-0035). Original planning baseline: `00136c9d`.
- No production, credential, real-home installation, private pack, cloud-tenant or
  organization discovery authority is granted. Tests use synthetic roots only.

The requirement IDs R01-R16 and all 48 leaf IDs (0.1.a-6.2.c) are preserved unchanged.
The notes below reconcile the bundle with the architecture accepted after `00136c9d`.
Where a note changes the meaning of the spec, the spec/plan line carries an `RN-NN` marker.

## Revision notes

**RN-01 Pack provenance reuses ADR-0029 (spec section 3).** `lib/profile_context.py`
already owns manifest parsing, whole-block inheritance, per-field provenance
(`profile_field_provenance`), stable bound contexts, fail-closed drift detection and
explicit rebind. The proposed `resolve_pack_field_origin` accessor and a separate
`pack_pattern_context` resolver are NOT added as a second parser or cache. Instead:

- The pack-context record in spec section 3 is an output shape. Core
  `lib/patterns.py` derives it with `pack_context_from_profile(record)` from the
  existing profile context record (`profile_context_json` / `profile_context.py ... context`),
  reusing that module's typed record, digest and `field_value` semantics.
- Explicit null keeps its origin; a neutral-default fill keeps the fallback origin only
  when that value is the effective value; absent has neither.
- The declaring manifest bytes are re-hashed against the record's ancestry digest before
  a pack catalog is read. A changed manifest or disappeared cached root is
  `unavailable`, never re-resolution from another pack. Pointer drift remains the
  ADR-0029 fail-closed error of the profile context itself.
- A thin shell adapter over the existing `_profile_cli` may be added by the pack lane;
  existing accessor outputs and statuses are unchanged.

**RN-02 Review authority stays with ADR-0028 (spec sections 4.6, 8).** Pattern clause
coverage (`review`, exit 7) is supplemental content evidence consumed by the existing v2
review/QA/lifecycle/swarm contracts. It never records a PASS, never clears stale or
missing independent review, and never overrides a later rejection. Work-map, task and
profile binding of review evidence is unchanged. The lock's `review_evidence` is an input
to REVIEW, not a clearance record.

**RN-03 Fail-closed profile context (spec sections 3, 5).** An `error` or `fallback`
pack-context status blocks pattern-dependent resolution (`unavailable`, exit 5). A valid
neutral pack without `patterns.source` is `neutral`, not an error. Ordinary
non-pattern callers keep their existing profile behavior.

**RN-04 Current workflow owners (ADR-0034; spec sections 8, 9; cards 5.1.c, 5.2.a, 5.2.b).**
Retired routes are not recreated. Single-file mockup output belongs to
`generate-web --mode mockup`; built-UI review belongs to `frontend-design-review`.
Card 5.1.c therefore wires `skills/frontend-design/SKILL.md` and the mockup mode of
`skills/generate-web/SKILL.md`; card 5.2.b wires `skills/frontend-design-review/SKILL.md`.
Plan/repository inspection uses `inspect`, checks use `verify`, independent review uses
`cross-check`, continuity uses `pause`/`resume`. Leaf IDs and acceptance are unchanged.

**RN-05 Document providers (ADR-0033; spec section 8, card 4.3.c).** The PDF writer
(`generate-pdf`, HTML preparation and browser print) and the workbook provider
(`generate-xlsx`) are working capabilities, not template slots. Only `generate-visio`
remains a template slot. Card 4.3.c keeps each provider's current status. No PDF reader,
`pypdf` or other third-party dependency is added; produced PDF text/page content stays
explicitly unverified. Helper tests are distinct from actual format/host acceptance.

**RN-06 Installation closure (ADR-0027, ADR-0030; cards 6.1.b, 6.1.c).** Extend the
existing generator resource/dependency closure and generated inventories; no new
installation registry. Bare installation keeps no Python prerequisite; runtime pattern
operations require the existing optional Python 3.10+ toolchain explicitly and report
its absence. Adapter and documentation work follows ADR-0035's four supported client
families (Copilot, Claude, Codex, Cursor, plus the manual route) and the current generator
inventories; removed clients are not reintroduced from older bundle fields.

**RN-07 Planned paths and the command-surface guard (ADR-0034).** The current-tree
guard fails on unresolved workflow paths and retired names in `.claude/plans/`. Until
their card creates them, planned skill files are written as "`SKILL.md` under
`skills/pattern/`" rather than as full paths. Ownership: the core owner creates the
canonical pattern skill in 3.3.b; the workflow lane owns its consumer reference (4.1.a).

**RN-08 Decision record.** The implementation ADR is
[ADR-0038](../../decisions/0038-reusable-patterns.md) (0035 is the client-family
decision; 0036/0037 are MARS and CI tiering). The structure-impact record is
[the evolution entry](../../engineering/evolution/2026-09-28-reusable-patterns.md).

**RN-09 Transport and CLI details (spec sections 3, 5, 6).** The frozen public contract is
[contract.md](contract.md). Decisions within the spec's latitude, recorded there:
an `envelope` subcommand builds the roots envelope from the profile record with JSON
serialization; `--roots-file` is accepted as a file form of `--roots-stdin`; reports add a
`settings` map of structured-setting winners; status precedence is
invalid > unavailable > conflict > needs-context > ready/empty; a draft preview is never
executable and reports `unavailable`; an explicit or required pattern whose own selector
rejects the context is a `conflict` (missing facts are `needs-context`); personal catalogs
are listable and explicitly referencable but never contribute advisory candidates or
bindings. Until card 3.2.b adds attestations, a mandatory pattern with an external URL
source or a past `review_after` is `unavailable` (the spec's blocking default).

**RN-10 Execution topology.** [topology.md](topology.md) records the actual dependency graph,
the approved safe reordering into disjoint lanes after P1, and file ownership. The parent owns
nested-session dispatch and commissions independent review.

**RN-11 Swarm reconciliation (2026-09-28).** The operator opted into swarm execution. The running
initiative is brought under the existing swarm contract:

- `work.json` gains `execution_mode: "swarm"` and a `coordination` pointer.
- A `swarm/` directory holds the charter, coordination.json and brief pointers, instantiated from
  the canonical templates.
- The 48 leaf tables were rewritten losslessly into the canonical tree-form checklist items, with
  the same IDs, text, files, requirements and verification keys, and declared prerequisites as
  `(depends ...)`. The reason: the swarm parser reads completion only from checklist items, never
  from a table column.
- The approved edge relaxations are 2.2.a and 4.1.a on 1.3.c, 4.2.c on 4.2.b.wf, and 6.1.a on the
  lane outputs. They are written into those items. 4.2.a and 4.2.b are split into `.core` and
  `.wf` children.
- A "Swarm execution packages" table groups every leaf exactly once.
- `li-work-artifacts.py`, `li-swarm.py validate` and `wave` pass. `wave` reports CORE, PACK and WF
  as the wave-1 frontier.

The chronology is recorded in the charter. P0/P1 and the current lane launches were
host-coordinated. They are not retroactively validated native dispatch, and no brief, QA or
corroboration receipt was fabricated.

Two representational tensions remain, surfaced rather than worked around:

1. The command-surface guard refuses nonexistent workflow paths in plans, while the swarm package
   boundary needs literal, possibly not-yet-created paths. The WF boundary
   `references/` directory under the pattern skill reported three `missing-path` findings at 8aa1f89e and d82b2919 (in plan.md, build-log.md and
   this file); prose rewrites in c92ae4dc reduced them to one (the plan.md boundary), which remains until
   the WF lane's consumer reference is integrated.
2. `skills/CATALOG.md` drifts from the new canonical pattern skill until the coordinator
   regenerates the shared reducers at integration (card 6.1.b).

Neither validator is weakened.

**RN-12 Strict continuation baseline (R5, 2026-09-28).** Following the parent's decision on the
independent review of `d82b2919`, `verify_lock` treats every binding-driven change to the selected
baseline, including added or removed defaults, as a conflict that requires re-planning.
`parse_lock` re-derives settings with the resolver's own settling logic. This is stricter than the
spec requires, within spec 4.4's latitude. Leaf IDs, requirements and acceptance are unchanged.

**RN-13 Raw asset bytes through Git (P6 acceptance addition, 2026-09-28).** The parent found this in an
owned Git fixture. The repository `.gitattributes` forces `*.json` and `*.md` to LF, so a
committed CRLF legacy visual asset changed bytes, and therefore its declared sha256, after a fresh
clone. A source-local `.claude/patterns/.gitattributes` containing `* -text` preserved the exact
bytes. That result is Git transport evidence, not pattern CLI acceptance.

Cards 6.1.a, 6.1.c and 6.2.a therefore add the following acceptance, without changing leaf IDs:

- **Real round trip with a CRLF asset.** Capture, approve, `git commit`, fresh clone, then `check`
  and `read_asset`. This must work on the repository scope and on a pack source layout.
- **Byte preservation in the template, skill and docs.** The authoring template and the
  skill/docs provide source-scoped byte preservation, for example a source-local `.gitattributes`
  with `* -text`, and explicit instructions for Git-hosted sources.
- **Limits.**
  - Original assets are never normalized.
  - Hashes are never weakened.
  - Existing user attributes are never overwritten.
  - Git is not made a runtime or bare-install prerequisite.
- **Precedence.** A conflict with an authoritative repository attribute policy is surfaced, not
  overridden.

The canonical JSON digest protects the pattern record only. Raw asset bytes need this transport
guarantee.
