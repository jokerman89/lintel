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

**RN-14 Host obligations restored to the original scope (owner decision, 2026-09-28).**
MasterCoordinator `9854860c` chose Option 1, D1 and D2 of the independent spec adjudication
(reviewer `24bf5df0`, `spec-adjudication/host-obligations.md` sha256
`fca066e8c1e603fc30336dda5a5d879a3f3380f394c0288a07aab61afb7e472d`, JSON
`6c302715e81bf861b6b914acbb1471bfa323bf13442b756ea14424406025ee6d`).

This restores the scope the original cards defined; it is not a waiver or a downgrade. The
authorities are:

- the original cards at `2d750892` (with `eaffeb6c`);
- spec sections 8 to 10 (`spec.md:624`, `:632-636`, `:703-707`, `:721-731`);
- `implementation-release.md:21,76` (leaf acceptance is never dropped, and never silently
  enlarged);
- RN-05 and ADR-0033 (produced PDF text and pages stay unverified; no reader);
- ADR-0038 (host acceptance is a separate category, deferred when unavailable).

Leaf IDs and original leaf text are unchanged. Only later status annotations are corrected.

- **D1, card 4.3.c.** Acceptance is:
  - the original V09;
  - a V18 source and record review, not yet performed, of the PDF, workbook and Visio
    at-invocation contracts. It checks that required clauses are handed to the conversion input,
    that status and errors stay transparent and renderer status is never promoted, and that
    existing provider behavior is preserved;
  - the existing provider and preparation compatibility tests (`spec.md:636`) passing in the
    strict suite.

  Successful PDF text or page inspection is **not** a 4.3.c criterion; RN-05 keeps it
  unverified. No reader, restoration or new PDF requirement is added. 4.3.c stays unticked until
  its V18 record exists.
- **D2, card 5.2.a.** Acceptance is:
  - the original V11 (the `CONSUMER_ACCEPTANCE` mapped rows);
  - a V18 mapped-case review, including a new bounded source review of the `generate-web --mode
    mockup` route (RN-04), not yet performed.

  The six per-consumer model/render/host cells are supplemental and remain DEFERRED and
  unobserved. They cover `generate-web`, `design-dna`, `frontend-typography`, `frontend-motion`,
  `frontend-shader` and `generate-app`. No automatic behavior is claimed for them, and they are
  not V17 feature gates. 5.2.a stays unticked until that review exists.
- **Classification of the three later rows** in the `9e56dc79` diagnostic P05 request:
  - `document-page-render` is pre-existing generate-word and generate-pdf **artifact** QA. It
    blocks a produced artifact's DONE and is never N/A, but it is not a feature row.
  - `pdf-conversion-preservation` "in the produced PDF" is an expansion that RN-05 makes
    unsatisfiable. Its original part is D1 above.
  - `visual-consumer-host-cells` is a supplemental deferral (D2).

  The four V17 rows (dashboard, backend exclusion, required document section, cold resume) match
  the original acceptance.
- **Unchanged and still real:**
  - 6.2.a: a valid Windows strict verdict, or blocked-toolchain evidence. Linux passed 169/169 on
    `fdb9f27b`.
  - 6.2.b: the final independent aggregate review with actual ADR-0028 v2 context, QA and
    corroboration.
  - 6.2.c.
- **History stays verbatim:**
  - the `9e56dc79` request and its null profile;
  - the actor records (the WF review is non-clearing);
  - the C-PDF provider failure (no DevTools endpoint, no PDF);
  - Word pages unverified;
  - the six unobserved cells;
  - the `C:\lp` deviation.

  Old QA is not edited to PASS or N/A, and no actor verdict is rebound. A reconciled feature QA
  inventory may be declared only in a new context at the correct post-native-integration head,
  with artifact (B) and deferral (C) limits listed separately.
- **Provenance.** Coordinator ledger wording (`64c0091e`, `ebd087ec`, `64338b6c`), the P05
  request, and review wording (reviewer 24's WF and INT notes, and the WF test's "deferred: V17"
  label) expanded these rows to "required". The rows record genuine unobserved facts; only their
  mandatory classification was the expansion. See lesson L-063.

**RN-15 Pattern palette precedence at the design loader (owner decision, 2026-09-28).**
Reviewer `24bf5df0`'s source clarification of R-4 (`r4-clarification-118d1c71.md`, sha256
`e8e08cb6d68dbfd617e0a64cf1a7c42e4f987f6b6fdf284fb1cc12ec78fc75b0`) established the gap. The
original R12 precedence puts brief overrides above repository, pack and personal pattern defaults,
then the Design DNA profile, then the corpus (`spec.md:692-696`). But
`design_contract.load_design` refused any palette colour that differed from the pinned profile
without a brief override. MasterCoordinator `9854860c` approved Option 1 as a bounded join fix
within the original scope.

`23e8e194` adds a verified-pattern admission. `load_design`, and its CLI and pipeline-loader
callers, take an optional `pattern_lock` and `pattern_context`. Only a lock that the core
`verify_lock` accepts admits a differing palette colour. Its conditions:

- The roots come from this repository, the P07 home and the verified P07 pack context.
- The lock, the context and `.claude/patterns` are P05-selected with their current bytes.
- The spec's `pattern_context` matches.
- `validate_visual`, or the pipeline attachment, passes.
- Every palette winner equals the design's value.

A spec with a `pattern_context` but no lock is refused; no-pattern loading is unchanged.

**Ownership.** `skills/design-dna/scripts/design_contract.py`,
`skills/design-dna/references/design-contract.md`, `skills/generate/scripts/pipeline_inputs.py`
and `tests/integration/design-contract.py` are outside every lane scope. They are a CORE/INT
coordinator integration delta, authorized by the owner decision. The `lib/pattern_visual.py`
`palette_winners` helper is likewise a coordinator delta in the joined WF file.

**Unchanged:** leaf IDs, R12 text, ADR-0038, P05/P07 schemas, policy, profile and corpus files.
Typography is not projected by the v1 adapter and is unchanged.

**RN-15 clarification (2026-09-28, reviewer 24bf5df0 `r4-fix-b02b10cc.md` L-2; RN-15 text above
is unchanged).** The loader's pattern admission is palette-only. It accepts a frontend
`validate_visual` of `passed` or `incomplete` with no failed check. `incomplete` only leaves
unmapped settings as open review items. That is not render or review clearance: generate-web and
generate-app still require `passed` before rendering. Mandatory clauses keep their own QA evidence,
and incomplete or unknown mandatory coverage never becomes a pass. The loader also re-runs
`verify_lock` just before it returns. `pipeline_inputs` refuses the pattern flags for a
document-only design; its stages verify their `pattern_context` attachment.

**RN-16 External pattern inputs: supported binding and currentness at use (owner decision
(a), 2026-09-28).** The decision is on D-1 of reviewer `24bf5df0`'s `r4-fix-b02b10cc.md`
(sha256 `432754e441f7c36f47b0989794a0cbd71ed788bb4c2c5c36b092e3b38a4bd182`).
MasterCoordinator `9854860c` chose option (a). This is the explicit supported-binding
interpretation for A6; RN-15 and every earlier report are unchanged.

- **Repository inputs.** The repository lock, the current context and the relevant repository
  sources and evidence (`.claude/patterns`, the brief and other bound inputs) are in the actual
  P05 selection.
- **External inputs.** The pack and personal closure is content-addressed through that selected
  lock: pinned reference digests, catalog digests and the selection digest. It is not claimed
  to be repository-snapshotted. Standalone P05 remains repository-only.
- **Compound guarantee.** Every pattern-dependent consumer re-runs the core `verify_lock` on the
  actual current roots and context at use. That covers REVIEW, QA, render, SHIP and RESUME. It
  rejects changed, missing, revoked, conflicting or unavailable input before output. Only then
  does it take the same current P05, P07, QA, latest-review and corroboration gates.
  - A stored verification output is not enough.
  - Re-run after intervening work, and before dependent output or release.
  - Pattern success never grants release, and P05 success never skips the pattern check.
  - The rule is stated in the consumer contract ("Currentness at use") and the SHIP obligation.
- **In code.** `design_contract.load_design` (and so `renderer-args`, `review` and
  `pipeline_inputs`) verifies the lock at admission and again just before returning. It does so
  before its final P05/P07 rechecks, and `review_result` then applies QA.
- **Regression.** Committed tests take a positive pack or personal selection through the same
  review consumer. They mutate only the external source, leaving the repository lock and P05
  files byte-identical. P05 and QA alone still accept; the same consumer refuses before output;
  restoring the external content is admissible again.
- **Limits.** The loader cannot detect a spec that omits both `pattern_context` and the lock. That
  remains a workflow obligation (direct entry, `validate_visual` before render, REVIEW coverage).
  No P05/P07 schema, policy or release-authority change.
