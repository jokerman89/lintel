# Plan: reusable patterns

Date: 2026-09-24. Status: APPROVED for BUILD 2026-09-28 (see [reconciliation](reconciliation.md)).
Size: XL; depth: tree. Design and requirements: [spec.md](spec.md).
Discovery: planning baseline `00136c9d`; implementation base `7ba544a4`; findings in spec
section 1, review.md and the reconciliation's revision notes RN-01..RN-10.
Scope: full local pattern system, workflow integration and visual compatibility.
Handoff: [prompt.md](prompt.md). Map: [work.json](work.json). Contract: [contract.md](contract.md).
Topology and ownership: [topology.md](topology.md). Evidence: [build-log.md](build-log.md).

## Summary and authorization

Deliver a small data-only runtime with explicit scope, context matching, lifecycle
and traceability. Integrate existing pack and design systems instead of replacing
them. Do not activate anything in a real company environment.

The original delivery was the plan, not implementation. The implementation release of
2026-09-28 settles the BUILD gate; checkboxes below record verified leaf completion only.
No production action or other-session access is authorized; publication is limited to the
feature PR and normal merge the operator authorized.

## Plan signals

- Leaf tasks: 48 original IDs and 50 executable leaves. 4.2.a and 4.2.b stay as parent IDs, each split
  into `.core`/`.wf` child leaves (topology.md). A parent is complete only when both children pass.
  Original packages P0-P6 below are retained as the planning boundary. Execution uses the
  swarm package table ("Swarm execution packages") under the approved topology.
- Phases: architecture record, core contract, pack resolution, lifecycle, workflow
  wiring, visual adapter, portability/delivery verification.
- Size prior: 120,000 tokens, UNCALIBRATED, from `size_default_prior XL` in the
  inspected `lib/scale-estimator.sh`; not a measured estimate or price quote.
  Recompute the helper's whole-cycle estimate before BUILD using isolated runtime.
- Each row is a leaf with one observable result. Test classes below split large
  implementations into narrow behaviors; implement and verify incrementally.
- Owner for every leaf: one selected `lintel-builder` or coordinating implementer.
  One independent `lintel-reviewer` reviews each substantive package against
  spec then quality. The reviewer does not fix its own findings.
- Indicative per-leaf context allowance: 1,000-3,000 tokens, not additive forecasts.
  If a leaf cannot remain bounded, split it with suffix IDs before executing;
  preserve its parent requirement and package evidence mapping.

## Profile impact and restrictions

No personal or company pack was activated/read for this planning task. The bundled
neutral manifest and accepted pack contract are the compatibility baseline.
R03 tests whole-block replacement; R09 tests data-only behavior; R15 tests neutral
no-pattern behavior. No private company requirements are invented.

Do not edit existing governance, model configuration, hooks, unrelated frontend
quality rules or another initiative's plan. All new durable knowledge goes under
the authorized initiative once promoted into the repository.

## Work packages and edit boundaries

| Package | Outcome | Owner edit boundary | Depends on | Review/rollback boundary |
| --- | --- | --- | --- | --- |
| P0 | Approved architectural record and selected work map | Initiative plan, new ADR and evolution record only | None | No runtime behavior change |
| P1 | Pure local records and resolution | `lib/patterns.py`, `bin/li-pattern.py`, `tests/unit/patterns.py`, runner wrapper | P0 | Runtime inactive until wired |
| P2 | Source scopes, origins and reproducible selection | P1 files, `lib/pack-resolver.sh`, `lib/paths.sh`, `bin/li-pattern`, optional pack fields, pack/pin tests | P1 | Preserve old accessor contracts |
| P3 | Safe authoring, lifecycle and sharing | P1/P2 generic runtime, `skills/pattern/`, lifecycle tests | P2 | Immutable files, catalog-last updates |
| P4 | Cycle/direct-entry context and evidence | Canonical core, document pipeline and engineering entry skills, consumer reference, projection tests | P3 | No hook or state/work-map schema change |
| P5 | Visual capture and compatible consumption | `lib/pattern_visual.py`, named frontend/generate skills, visual tests | P4 | Preserve legacy assets and no-pattern outputs |
| P6 | Portable distribution and verified delivery | Generator, generated adapters, docs, template/example, integration tests, own plan/evidence | P5 | No install into personal home or merge |

All leaves inherit their package's owner and only the narrower files listed in
their row. "Unit" below means `tests/unit/patterns.py`; "core" means
`lib/patterns.py`; "CLI" means `bin/li-pattern.py`; "launcher" means `bin/li-pattern`.
New test paths are planned, not currently existing.

## Swarm execution packages

Operator opt-in and parent approval of the split are recorded in [topology.md](topology.md) and
[swarm/charter.md](swarm/charter.md). The leaf items below remain authoritative for text,
dependencies, status and acceptance; this table only groups them. P0P1 is complete and INT is the
coordinator-only serial join (no lane). Cross-lane verification is pending join (topology.md).

| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Review |
| --- | --- | --- | --- | --- | --- |
| P0P1 | Promoted plan, ADR and pure P1 contract (reviewed milestone) | 0.1.a, 0.1.b, 1.1.a, 1.1.b, 1.1.c, 1.1.d, 1.2.a, 1.2.b, 1.2.c, 1.3.a, 1.3.b, 1.3.c | integration owner; `lib/patterns.py`, `bin/li-pattern.py`, `tests/unit/patterns.py`, `tests/unit/patterns.sh` | none | substantive |
| CORE | Pins, lifecycle, sharing and core evidence | 2.2.a, 2.2.b, 2.2.c, 3.1.a, 3.1.b, 3.1.c, 3.2.a, 3.2.b, 3.2.c, 3.3.a, 3.3.b, 4.2.a.core, 4.2.b.core | integration owner; `lib/patterns.py`, `bin/li-pattern.py`, `tests/unit/patterns.py`, `tests/unit/patterns.sh`, `skills/pattern/SKILL.md` | P0P1 | substantive |
| PACK | Roots, pack provenance and launcher | 2.1.a, 2.1.b, 2.1.c, 2.1.d | pack lane; `lib/pack-resolver.sh`, `lib/paths.sh`, `bin/li-pattern`, `packs/_default/pack.yaml`, `lib/pack-schema.yaml`, `tests/unit/pattern-pack-origins.sh`, `tests/unit/pattern-pack-origins.py`, `tests/unit/pattern-launcher-roots.sh`, `tests/unit/pattern-launcher-roots.py`, `tests/unit/pattern_pack_harness.py` | P0P1 | substantive |
| WF | Workflow, document, engineering and visual consumers | 4.1.a, 4.1.b, 4.1.c, 4.2.a.wf, 4.2.b.wf, 4.2.c, 4.3.a, 4.3.b, 4.3.c, 4.3.d, 5.1.a, 5.1.b, 5.1.c, 5.2.a, 5.2.b | workflow/visual lane; `skills/sense/SKILL.md`, `skills/scope/SKILL.md`, `skills/define/SKILL.md`, `skills/discover/SKILL.md`, `skills/cycle/SKILL.md`, `skills/plan/SKILL.md`, `skills/build/SKILL.md`, `skills/resume/SKILL.md`, `skills/review/SKILL.md`, `skills/ship/SKILL.md`, `skills/capture/SKILL.md`, `skills/generate/SKILL.md`, `skills/generate-outline/SKILL.md`, `skills/generate-write/SKILL.md`, `skills/generate-design/SKILL.md`, `skills/generate-qa/SKILL.md`, `skills/generate-word/SKILL.md`, `skills/generate-ppt/SKILL.md`, `skills/generate-pdf/SKILL.md`, `skills/generate-xlsx/SKILL.md`, `skills/generate-visio/SKILL.md`, `skills/ta/SKILL.md`, `skills/da/SKILL.md`, `skills/sc/SKILL.md`, `skills/dh/SKILL.md`, `skills/tq/SKILL.md`, `skills/frontend-style-extract/SKILL.md`, `skills/generate-style-learn/SKILL.md`, `skills/frontend-design/SKILL.md`, `skills/generate-web/SKILL.md`, `skills/design-dna/SKILL.md`, `skills/frontend-typography/SKILL.md`, `skills/frontend-motion/SKILL.md`, `skills/frontend-shader/SKILL.md`, `skills/generate-app/SKILL.md`, `skills/frontend-design-review/SKILL.md`, `skills/pattern/references`, `lib/pattern_visual.py`, `tests/integration/pattern-workflows.py`, `tests/integration/pattern-workflows.sh`, `tests/unit/pattern-visual.py`, `tests/unit/pattern-visual.sh`, `tests/integration/pattern-visual-roundtrip.py`, `tests/integration/pattern-visual-roundtrip.sh` | P0P1 | substantive |
| INT | Packaging, generated adapters, docs and release evidence | 6.1.a, 6.1.b, 6.1.c, 6.2.a, 6.2.b, 6.2.c | integration owner (coordinator-only, no lane); `scaffolding/01-foundation/templates/pattern`, `docs`, `skills/pack-create/SKILL.md`, `skills/pack-validate/SKILL.md`, `bin/li-copilot.py`, `.github`, `skills/CATALOG.md`, `tests/integration/pattern-portability.py`, `tests/integration/pattern-portability.sh`, `tests/shape/pattern-contract.sh` | CORE, PACK, WF | substantive |

## Verification command key

Use native Python 3 command available on the host. Commands below use Windows
path spelling. Shell-runner scripts use normal portable shell paths internally.
Create unittest classes with exactly these names so card checks remain runnable.

| Key | Command/procedure | Expected evidence |
| --- | --- | --- |
| V01 | `python tests\unit\patterns.py SchemaTests` | Valid records roundtrip; malformed/duplicate keys and incompatible versions rejected |
| V02 | `python tests\unit\patterns.py PathTests` | Traversal, drive, symlink/reparse and size attacks rejected without writes |
| V03 | `python tests\unit\patterns.py SelectorTests` | Exact matched/rejected/needs-context outputs, deterministic ordering and body-read counts |
| V04 | `python tests\unit\patterns.py AuthorityTests` | All must clauses preserved; conflicting settings/defaults explicit; exceptions validated |
| V05 | `bash tests\unit\pattern-pack-origins.sh` | Correct inherited origins and same-snapshot identity/value; no fallback success |
| V06 | `python tests\unit\patterns.py PinTests` | Includes/digests/lifecycle/context changes detected; cold projection complete |
| V07 | `python tests\unit\patterns.py LifecycleTests` | Draft/approval/version/events/bindings operations preserve old state and emit impact |
| V08 | `python tests\unit\patterns.py BundleTests` | Exact export closure; whole-bundle preflight; hostile input and collisions rejected |
| V09 | `python tests\integration\pattern-workflows.py` | Real helper outputs reach work IDs and review/continuation; missing evidence fails |
| V10 | `python tests\unit\pattern-visual.py` | Legacy conversion, structured setting application and no-pattern compatibility |
| V11 | `python tests\integration\pattern-visual-roundtrip.py` | Actual selection -> adapter -> frontend spec -> review, including negative case |
| V12 | `python tests\integration\pattern-portability.py` | Separate source/target, paths with spaces, non-Git explicit root, empty roots |
| V13 | `python bin\li-copilot.py check` and `python bin\li-catalog.py --check` | Generated files have no drift; init regeneration precedes check when needed |
| V14 | `bash tests\unit\enterprise-pack-resolution.sh`; `bash tests\unit\pack-inheritance-depth-3.sh`; `bash tests\integration\pack-source-target-resolution.sh`; `bash tests\shape\claude-home-paths.sh`; `bash tests\unit\memory-v2.sh` | Frozen contracts remain green |
| V15 | `bash tests\integration\copilot-kit.sh`; `bash tests\integration\frontend-design-roundtrip.sh`; `bash tests\unit\design-dna-search.sh`; `bash tests\unit\design-validator.sh` | Existing kit and frontend compatibility; legacy roundtrip is schema-only evidence |
| V16 | `bash tests\runner\run-all.sh --require-all` | Required full suite without silent skips, or explicit blocked toolchain evidence |
| V17 | Fresh host acceptance procedure in spec sections 8 and 10 | Dashboard plus direct technical-document behavior and negative QA, backend exclusion and pin continuation; host/tool permissions stated |
| V18 | Source/diff/manual record review | Exact file citations, scope result and limitations in review evidence |

Test scripts use isolated temporary roots and launchers' explicit root arguments.
They must not source helpers against the real personal Lintel home. Wrapper scripts
under tests/unit and tests/integration register Python suites with the existing
runner; a standalone unregistered Python file is not CI coverage.

Evidence for every leaf: `<initiative>/build-log.md#<leaf-id>`, with command,
exit status, case counts, relevant observed outputs and limitations. Never mark
pass on a test command that has not run. Implementation must add any missing
test tools only after a missing-dependency result and within authorized scope.

## Phase 0: architecture and integration authority

### 0.1 Establish the isolated implementation baseline

- [x] 0.1.a Promote this package only after BUILD authorization; select explicit work.json; preserve other plan entries and record actual base hash. Map validator passes. Files: Own initiative plan/map. Req: R16. Verify: V18. (depends None)
- [x] 0.1.b Allocate unused ADR number; record spec section 1, affected contracts and feature-only rollback. No accepted ADR/governance rewritten. Files: New ADR, `.claude/engineering/evolution/<date>-reusable-patterns.md`. Req: R16. Verify: V18. (depends 0.1.a)

Milestone: bounded authorization, compatible architecture and explicit task source.

## Phase 1: pure local contract and resolver

### 1.1 Parse and validate records

- [x] 1.1.a Pattern/clauses/sources/assets/exact-reference records and canonical digest per sections 4.1/4.4. Correct roundtrip; no bool schema or duplicate-key acceptance. Files: core, Unit. Req: R01. Verify: V01. (depends 0.1.b)
- [x] 1.1.b Catalog/binding/context/report records including lifecycle arrays and extension seam. Required fields, enums and cross-field constraints reject malformed input. Files: core, Unit. Req: R01. Verify: V01. (depends 1.1.a)
- [x] 1.1.c Central contained path resolver; reject escaping paths and symlink/reparse parents on reads/writes. Tests verify no access outside fixture root. Files: core, Unit. Req: R09. Verify: V02. (depends 1.1.b)
- [x] 1.1.d Strict size/depth limits, status codes and stderr/stdout contracts; register unit runner. CLI errors preserve destination bytes. Files: core, CLI, Unit, `tests/unit/patterns.sh`. Req: R09. Verify: V01, V02. (depends 1.1.c)

### 1.2 Match metadata before opening content

- [x] 1.2.a AND/OR selectors and evidenced context; known mismatch beats unknown, empty selector explicit. Multi-domain fixtures need no domain-specific runtime code. Files: core, Unit. Req: R01,R04. Verify: V03. (depends 1.1.d)
- [x] 1.2.b list/show/check and catalog-based explain scaffolding; unbound matching returns <=5 summaries/1,200 characters; unrelated body/asset reads stay zero. Files: core, CLI, Unit. Req: R04,R13. Verify: V03. (depends 1.2.a)
- [x] 1.2.c Selected body metadata/digest revalidation and read-once snapshots; stale metadata fails, file replacement cannot change validated content. Exact read metrics asserted. Files: core, Unit. Req: R04,R13. Verify: V03. (depends 1.2.b)

### 1.3 Resolve authority and completeness

- [x] 1.3.a Required bindings are independent of candidate ranking; six mandatory patterns survive top-five advisory cap; unknown required binding produces needs-context. Files: core, Unit. Req: R05. Verify: V04. (depends 1.2.c)
- [x] 1.3.b Required/default distinction and structured setting conflicts/default precedence; same-scope ties fail, must under default binding is conflict. Files: core, Unit. Req: R05,R07. Verify: V04. (depends 1.3.a)
- [x] 1.3.c Exact exception/override/ref-role inputs per spec; expired exceptions fail, explicit must never gains implicit authority, and budget excess emits no success lock. Files: core, CLI, Unit. Req: R05,R07. Verify: V04. (depends 1.3.b)

Milestone: deterministic local resolution with explicit uncertainty and no dropped rules.

## Phase 2: roots, pack compatibility and pins

### 2.1 Integrate existing pack resolution

- [ ] 2.1.a Add path helpers and roots-envelope parser; personal-only inspection works, repository operations require explicit valid root when outside Git. No writes to source tree. Files: `lib/paths.sh`, launcher, core, Unit. Req: R02. Verify: V02, V12. (depends 1.3.c)
- [ ] 2.1.b Exact same-snapshot context/ancestry transport; inherited/null/fallback origins correct; pointer change and missing cached origin explicit. Existing accessors unchanged. Files: `lib/pack-resolver.sh` (adapter only; RN-01), `tests/unit/pattern-pack-origins.sh`. Req: R02,R03. Verify: V05, V14. (depends 2.1.a)
- [ ] 2.1.c Optional `patterns.source: null`, source-aware pack/ancestry registry, JSON stdin bridge safely handles spaces and quoting. Declared absent catalog is not neutral success. Files: launcher, `packs/_default/pack.yaml`, `lib/pack-schema.yaml`, origin tests. Req: R02,R03. Verify: V05. (depends 2.1.b)
- [ ] 2.1.d Unconfigured roots preserve old workflow behavior; active enterprise fallback remains visible/unavailable for dependent use. No automatic personal activation. Files: core, launcher, Unit. Req: R02,R15. Verify: V05, V12, V14. (depends 2.1.c)

### 2.2 Bind and freeze a reproducible selection

- [x] 2.2.a Exact pattern includes, catalog includes and cycle/depth/conflicting-digest detection; transitive dependencies inherit requiredness and must match context. Files: core, Unit. Req: R01,R08. Verify: V06. Declared prerequisite `2.1.d` relaxed per topology.md. (depends 1.3.c)
- [x] 2.2.b resolve lock/verify-lock with stable digests, source snapshots and current lifecycle/revocations; pointer changes or missing source never silently upgrade pins. Files: core, CLI, Unit. Req: R03,R08. Verify: V06. (depends 2.2.a)
- [x] 2.2.c map/project use section 4.6 schema/digests; unknown IDs and unmapped clauses block; mapping changes invalidate review coverage; budget overflow emits no partial lock. Files: core, CLI, Unit. Req: R05,R11,R13. Verify: V06. (depends 2.2.b)

Milestone: reproducible selection across scopes with verified no-pattern compatibility.

## Phase 3: authoring, lifecycle and sharing

### 3.1 Capture and publish reviewed local patterns

- [x] 3.1.a capture writes only a valid draft in explicit scope; source statements and observations distinguish inference; existing name/version refuses overwrite. Files: core, CLI, Unit. Req: R06. Verify: V07. (depends 2.2.c)
- [x] 3.1.b Exclusive source lock/CAS and catalog-last publication; index never discovers unregistered staging or removed entries and preserves lifecycle events. Files: core, CLI, Unit. Req: R06. Verify: V07. (depends 3.1.a)
- [x] 3.1.c approve requires explicit newer version and valid approved dependencies; source evidence rejects if missing. Deprecate->index/remove->index preserve effective state. Files: core, CLI, Unit. Req: R06. Verify: V07. (depends 3.1.b)

### 3.2 Maintain without silently changing active work

- [ ] 3.2.a update versions and lifecycle/revocation events; changed requirements and configured dependents appear in impact preview; current pins remain unchanged. Files: core, CLI, Unit. Req: R08. Verify: V07. (depends 3.1.c)
- [ ] 3.2.b apply add/replace/remove and section 4.5 attestations; wrong-digest/expired/URL evidence handled; renewal preserves selection digest; binding reduction preview explicit. Files: core, CLI, Unit. Req: R07,R08. Verify: V07. (depends 3.2.a)
- [ ] 3.2.c remove preview, referenced-history protection and bounded dependency scan; unknown external consumers reported, unrelated sessions not read. Files: core, CLI, Unit. Req: R08. Verify: V07. (depends 3.2.b)

### 3.3 Share data, not execution or inherited trust

- [ ] 3.3.a export exact dependency closure and authorized assets to new directory; no external source fetch, private source-document copy or absolute-root leak. Files: core, CLI, Unit. Req: R09. Verify: V08. (depends 3.2.c)
- [ ] 3.3.b import transforms children-first with explicit source/version mapping and recomputed pins; closure imports then approves locally; collisions/external refs fail. Skill documents all operations. Files: core, CLI, Unit, canonical `SKILL.md` under `skills/pattern/` (planned; RN-07). Req: R09. Verify: V08, V18. (depends 3.3.a)

Milestone: safe complete local lifecycle; no remote distribution implied.

## Phase 4: workflow and handoff wiring

### 4.1 Resolve before decisions, including direct entry

- [ ] 4.1.a Single invocation/result contract with selector evidence and all failure branches; test invokes real launcher using this envelope. Files: `references/consumer-contract.md` under `skills/pattern/` (planned; RN-07), workflow test. Req: R10. Verify: V09. Declared prerequisite `3.3.b` relaxed per topology.md. (depends 1.3.c)
- [ ] 4.1.b Metadata-only startup and pre-design resolution/source verification; unknown target does not become a guessed deployment baseline. Files: `skills/sense/SKILL.md`, `skills/scope/SKILL.md`, `skills/define/SKILL.md`, `skills/discover/SKILL.md`. Req: R10. Verify: V09, V18. (depends 4.1.a)
- [ ] 4.1.c Direct PLAN and cycle PLAN produce equivalent selection on same inputs; no sources adds no prompts/mandatory artifacts. Preserve existing phase/approval protocol. Files: `skills/cycle/SKILL.md`, `skills/plan/SKILL.md`, workflow test. Req: R10,R15. Verify: V09. (depends 4.1.b)

### 4.2 Carry requirements through implementation and review

- [ ] 4.2.a Explicit lock verification and package projection; changed/revoked content blocks affected continuation, Spec Kit task IDs remain unchanged. Files: `skills/build/SKILL.md`, `skills/resume/SKILL.md`, core/CLI evidence functions. Req: R10,R11. Verify: V09. Parent: complete only when both suffix parts below pass on the integrated branch (topology.md).
  - [ ] 4.2.a.core Core/CLI part of 4.2.a: explicit lock verification and package projection functions consumed by BUILD and RESUME; changed or revoked content blocks affected continuation, Spec Kit task IDs unchanged. Files: core, CLI, Unit. Req: R10,R11. Verify: V06; V09 pending join. (depends 2.2.c)
  - [ ] 4.2.a.wf Skill part of 4.2.a: `skills/build/SKILL.md` and `skills/resume/SKILL.md` verify an explicit lock and use package projections; changed or revoked content blocks affected continuation, Spec Kit task IDs unchanged. Files: `skills/build/SKILL.md`, `skills/resume/SKILL.md`. Req: R10,R11. Verify: V09 pending join. (depends 4.1.c)
- [ ] 4.2.b review input validator and coverage verdict; omitted/failed/unverified must exits 7, exception is waived not passed; no claim evidence links prove truth. Files: `skills/review/SKILL.md`, `skills/ship/SKILL.md`, core/CLI, workflow test. Req: R10,R11. Verify: V09. Parent: complete only when both suffix parts below pass on the integrated branch (topology.md).
  - [ ] 4.2.b.core Core/CLI part of 4.2.b: review input validator and coverage verdict; omitted/failed/unverified must exits 7, exception is waived not passed; no claim evidence links prove truth. Files: core, CLI, Unit. Req: R10,R11. Verify: V09 pending join. (depends 4.2.a.core)
  - [ ] 4.2.b.wf Skill part of 4.2.b: `skills/review/SKILL.md` and `skills/ship/SKILL.md` consume the review verdict, with workflow-test cases; no claim evidence links prove truth. Files: `skills/review/SKILL.md`, `skills/ship/SKILL.md`, workflow test. Req: R10,R11. Verify: V09 pending join. (depends 4.2.a.wf)
- [ ] 4.2.c CAPTURE proposes rather than silently approves changes; cold handoff reconstructs from explicit artifacts; runner executes real traceability roundtrip. Files: `skills/capture/SKILL.md`, workflow test and runner wrapper. Req: R11. Verify: V09. Declared prerequisite `4.2.b` refers to its workflow part per topology.md. (depends 4.2.b.wf)

### 4.3 Integrate nonvisual standalone work

- [ ] 4.3.a Shared pipeline carries verified lock reference; direct subskill entry resolves itself; absent/stale attachment is not a pass. Files: `skills/generate/SKILL.md`, `skills/generate-outline/SKILL.md`, `skills/generate-write/SKILL.md`, `skills/generate-design/SKILL.md`, `skills/generate-qa/SKILL.md`. Req: R10. Verify: V09, V18. (depends 4.2.c)
- [ ] 4.3.b Direct brief and pipeline paths receive same clauses; direct document pattern requires a named section and quality gate flags absence; record real host case separately. Files: `skills/generate-word/SKILL.md`, `skills/generate-ppt/SKILL.md`, workflow test. Req: R10. Verify: V09, V17. (depends 4.3.a)
- [ ] 4.3.c At-invocation slot contracts resolve/verify patterns without falsely promoting renderer status; document conversion preserves required clauses. Files: `skills/generate-pdf/SKILL.md`, `skills/generate-xlsx/SKILL.md`, `skills/generate-visio/SKILL.md`. Req: R10. Verify: V09, V18. (depends 4.3.b)
- [ ] 4.3.d Engineering entries resolve target-bound expectations and pass projections; unknown target blocks dependent design, no live discovery implied. Files: `skills/ta/SKILL.md`, `skills/da/SKILL.md`, `skills/sc/SKILL.md`, `skills/dh/SKILL.md`, `skills/tq/SKILL.md`. Req: R10. Verify: V09, V18. (depends 4.3.c)

Milestone: core, document and engineering entries share the same selection contract.

## Phase 5: visual capture and reuse

### 5.1 Adapt existing visual artifacts

- [ ] 5.1.a Distinguish legacy schema-1 pattern from universal schema-1; convert to draft defaults with source confidence/rights, preserving unknown fields in legacy asset. Files: `lib/pattern_visual.py`, visual unit test. Req: R12. Verify: V10. (depends 4.3.d)
- [ ] 5.1.b Existing extraction emits universal draft via adapter; no implicit source copying or trust promotion, legacy originals preserved. Files: `skills/frontend-style-extract/SKILL.md`, `skills/generate-style-learn/SKILL.md`. Req: R12. Verify: V10, V18. (depends 5.1.a)
- [ ] 5.1.c Implement section 9 setting/destination/type table and explicit profile precedence; assert changed actual spec values and mismatch failures, not attachment presence alone. Files: `skills/frontend-design/SKILL.md`, `skills/generate-web/SKILL.md` (`--mode mockup`; RN-04), visual adapter. Req: R12. Verify: V10. (depends 5.1.b)

### 5.2 Wire decision, rendering and review consumers

- [ ] 5.2.a Direct callers verify/resolve context; requirements constrain decisions, ordinary brief/profile/corpus rules still apply for unconstrained choices. Each consumer has mapped acceptance case. Files: `skills/design-dna/SKILL.md`, `skills/frontend-typography/SKILL.md`, `skills/frontend-motion/SKILL.md`, `skills/frontend-shader/SKILL.md`, `skills/generate-web/SKILL.md`, `skills/generate-app/SKILL.md`. Req: R12. Verify: V11, V18. (depends 5.1.c)
- [ ] 5.2.b Baseline mismatch fails review; actual resolver->adapter->spec->review tested; no-pattern spec remains compatible; legacy schema-only test not called rendering proof. Files: `skills/frontend-design-review/SKILL.md` (sole built-UI review owner; RN-04), adapter, visual integration test and wrappers. Req: R12,R15. Verify: V10, V11, V15. (depends 5.2.a)

Milestone: shared patterns work with existing visual flow without replacing Design DNA.

## Phase 6: packaging and release evidence

### 6.1 Make adoption self-contained

- [ ] 6.1.a One canonical neutral example plus template; authoring and lifecycle documented; pack-create/validate understand optional source; no curated company rules. Files: `scaffolding/01-foundation/templates/pattern/`, `docs/concepts/patterns.md`, `docs/architecture.md`, `docs/the-cycle.md`, `docs/multi-cli.md`, `docs/copilot.md`, `skills/pack-create/SKILL.md`, `skills/pack-validate/SKILL.md`. Req: R14. Verify: V18. Declared prerequisite `5.2.b` relaxed per topology.md. (depends 2.1.d, 3.3.b, 4.2.b.core, 5.2.b)
- [ ] 6.1.b Add pattern workflow and required doc bundle entries; regenerate with existing init/catalog commands, never hand-edit generated profiles. Missing downstream links fail check. Files: `bin/li-copilot.py`, the generated `li-pattern` native wrapper under `.github/skills/` (planned; RN-07), managed inventory/plugin outputs as generator requires, `skills/CATALOG.md`. Req: R14. Verify: V13. (depends 6.1.a)
- [ ] 6.1.c Fresh kit includes helper, canonical skill and reference; explicit non-Git root and Windows paths work; old catalogs/legacy inputs don't imply active policy. Files: `tests/integration/pattern-portability.py`, runner wrapper, `tests/shape/pattern-contract.sh`. Req: R14. Verify: V12, V13. (depends 6.1.b)

### 6.2 Verify behavior and prepare later integration

- [ ] 6.2.a Run read-count/size boundaries, targeted compatibility and strict full suite. No claimed pass for skipped/missing tools. Files: New tests and only directly coupled fixes. Req: R13,R14,R15. Verify: V01-V16. (depends 6.1.c)
- [ ] 6.2.b Fresh host/model acceptance for dashboard/backend/resume, or explicit deferred host gate. Independent spec and quality review closes substantive findings. Files: Own acceptance/review record. Req: R14,R15. Verify: V17, V18. (depends 6.2.a)
- [ ] 6.2.c Final diff, requirement coverage and source/target baseline recorded; no unrelated changes, no other-session contact; leave feature ready for authorized later integration. Files: Own plan, ADR/evolution evidence, integration handoff. Req: R16. Verify: V18. (depends 6.2.b)

Milestone: local system verified; deployment/host claims limited to actual evidence.

## Required adversarial cases

These cases are mandatory even where happy-path tests pass:

- A company pack falls back to neutral while a required source is missing.
- An inherited source is relative to the parent, not the child/source bundle.
- An unbound personal pattern has a colliding ID and must clauses.
- A mandatory rule is sixth in relevance ranking or exceeds context budget.
- A selector lacks the production target but matches artifact/platform.
- A selected asset changes while catalog metadata stays unchanged.
- A catalog include cycle, cross-root traversal or Windows junction attempts escape.
- A bundle contains prompt injection, shell snippets or links to private documents.
- A source update races another writer; catalog remains old-valid or new-valid.
- A legacy schema-version-1 visual pattern is mistaken for universal schema version 1.
- A resumed selection has a current revocation, retired version or missing source.
- A reviewer marks not-applicable without changing applicability/selection.
- A direct renderer is invoked without SENSE/DEFINE first.
- A synthetic paper/report-style task works without Azure or UI special cases.

## Review and completion policy

Planning review is in review.md. Runtime evidence is recorded per leaf in
[build-log.md](build-log.md); a checkbox is ticked only with that evidence. Each package
requires spec then quality review and
every leaf's evidence; a successful aggregate test does not erase an open leaf.

The plan deliberately adds no universal compliance certification and no auto-update
service. It treats structural validation, local integration, model behavior and
enterprise control effectiveness as different claims.

Rollback during implementation is through feature-scoped changes only. Do not
delete pattern histories or personal vaults. Keep accepted locks/legacy inputs
readable; if reverting adapters, show unsupported required-pattern state instead
of silently continuing without the baseline.
