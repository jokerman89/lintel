# Reusable patterns: build log

Evidence per leaf (`#<leaf-id>`). Unrun checks are pending, never passed. Environment for
every recorded run: Windows host, Python 3.11.9, working tree
`jokerman-microsoft-patterns-core-integration` on base `7ba544a4`, and a synthetic
environment (HOME, USERPROFILE, LINTEL_HOME, APPDATA, LOCALAPPDATA, TEMP, TMP, XDG_*) under
this session's artifact directory. Tests create their own temporary roots; none reads a real
home, pack or another session. Implementer: the integration/core session. Independent spec and
quality review of this package: NOT YET OBTAINED (parent-owned).

Host note (L-049): the Git Bash wrapper run mounted MSYS `/tmp` on the synthetic TEMP; that
directory is retained, not deleted, while MSYS processes may use it.

## 0.1.a

Promoted the six bundle files into `.claude/plans/reusable-patterns/`; no prior initiative
existed at that path. Recorded authority, base and 10 revision notes in
[reconciliation.md](reconciliation.md); spec/plan/prompt/review carry status and RN markers.
48 leaf IDs and R01-R16 unchanged. `work.json` rewritten to repository-relative paths, status
APPROVED. Pointer added to `.claude/memory/MEMORY.md`. `.claude/plans/todo.md` was NOT changed:
its lines are byte-bound by `.claude/plans/legacy-cleanup/residuals.md` spans, and editing it
disabled the command-surface guard's reviewed classifications (553 findings; restored).

- `python -I -B bin\li-work-artifacts.py --repo . --map .claude\plans\reusable-patterns\work.json` -> exit 0.
- `python -I -B tests\shape\native-command-surface.py` -> PASS (0 findings) after the RN-04/RN-07
  rewrites of planned skill paths and retired route names.

## 0.1.b

Allocated ADR-0038 (0035 client families, 0036 MARS, 0037 CI tiering exist):
`.claude/decisions/0038-reusable-patterns.md`. Evolution entry
`.claude/engineering/evolution/2026-09-28-reusable-patterns.md`. No accepted ADR or governance
document edited. Feature-only rollback recorded. Verification V18 (manual record review).

## 1.1.a / 1.1.b

`lib/patterns.py` typed frozen records and parsers for pattern, clause, source, asset,
approval, exact reference, catalog (entries, includes, bindings, lifecycle, revocations,
extensions), bindings file, context, refs, overrides, exceptions, pack context and roots.
Canonical digest per spec 4.4.

- `python -I -B tests\unit\patterns.py SchemaTests` -> exit 0, 8 tests OK (roundtrip and
  key-order-independent digest; duplicate keys, NaN/Infinity, bool/2 schema versions, unknown
  fields, prerelease/leading-zero versions, limits, lifecycle transitions and timestamps,
  2,001-entry catalog; ADR-0029 record conversion with inherited origin, explicit null,
  whole-block replacement and fallback).

## 1.1.c

`validate_relative_path`, `contained_path`, link/junction refusal in `Reader`.

- `python -I -B tests\unit\patterns.py PathTests` -> exit 0, 5 tests OK (19 hostile spellings;
  catalog traversal; a real NTFS junction escaping the root; include escape; oversize pattern;
  envelope validation). Assertions verify no read under the outside directory.

## 1.1.d

Fixed limits (`LIMITS`), status/exit codes, stdout report / stderr diagnostics, registered
wrapper `tests/unit/patterns.sh` (discovered by `tests/runner/run-all.sh` as `*.sh`).

- `bash tests/unit/patterns.sh` -> exit 0, 33 tests OK.
- CLI cases in SchemaTests: invalid pattern exit 2 with stderr line; oversize context exit 2;
  conflicting roots options exit 2; a failed call leaves every fixture file byte-identical.

## 1.2.a / 1.2.b / 1.2.c

Selector evaluation, list/show/check, advisory candidates, read-once selected bodies and
digest/metadata revalidation.

- `python -I -B tests\unit\patterns.py SelectorTests` -> exit 0, 6 tests OK (known mismatch beats
  missing; dashboard/network/document fixtures with no domain code; unrelated request reads 0
  bodies and 0 assets; 8 candidates -> 5 items, <=1,200 summary code points, 0 body reads;
  list 0 reads, show exactly 1; pattern reached twice read once; changed bytes and stale
  summary unavailable; personal scope explicit only).

## 1.3.a / 1.3.b / 1.3.c

Required bindings independent of ranking, required/default semantics, setting conflicts and
precedence, overrides, exceptions, explicit reference roles and budget.

- `python -I -B tests\unit\patterns.py AuthorityTests` -> exit 0, 10 tests OK (six mandatory
  patterns with ten advisory; must under default conflict; must/must, same-scope default,
  repo-over-pack precedence, override resolution; override of must needs a valid exception,
  waived not passed; expired/mismatched/unknown exceptions rejected; explicit mismatch conflict;
  drafts, deprecated, retired, revoked; 14 x 1,900-character musts exceed the budget with the full
  inventory and no success; fallback/error pack contexts unavailable; no-source repository is
  `empty` with zero reads; URL and overdue mandatory sources blocked; CLI exit codes 0/3/4/0).

## 2.2.a (implemented ahead of its original prerequisite; checkbox pending topology approval)

Pattern includes (requiredness inherited, context applied, cycle, depth 16, conflicting
digests) and catalog includes (ancestry locator, pinned digest, source-ID collision, manifest
drift, declared missing catalog, origin outside ancestry).

- `python -I -B tests\unit\patterns.py PinTests` -> exit 0, 4 tests OK.

The plan's chain makes 2.2.a depend on 2.1.d (pack lane). The leaf stays unchecked until the
parent approves the reordering in [topology.md](topology.md) or 2.1.d lands.

## Publication access denial (preserved evidence)

2026-09-28, after commit `eaffeb6c`, the integration session ran `git push -u origin HEAD`
once. It ran under the host session's injected identity. Verbatim result, exit 128:

```text
remote: Permission to jokerman89/lintel.git denied to jokerman_microsoft.
fatal: unable to access 'https://github.com/jokerman89/lintel.git/': The requested URL returned error: 403
```

The session followed L-053 and the parent's instruction of 2026-09-28. It did not retry,
did not switch or unset accounts or tokens, did not inspect credentials and did not ask
another actor to bypass the denial. Local branch milestones are used for nested review.
Final publication is an open host-account access block. The parent surfaces it through the
sanctioned UI at delivery. BUILD authorization does not cover an authentication bypass.

## Review revision R1 (after parent note on `eaffeb6c`)

The parent flagged that the milestone rejected null setting values, although spec 4.1 says
"JSON scalar". An audit of all validators against the spec text found further unjustified
narrowing. Each is now accepted as the spec permits:

- Null setting/override values.
- Clause IDs of any uppercase letters, digits and hyphens. The 64-character cap was lifted to 128.
- Binding IDs as any nonempty string. The spec requires only uniqueness.
- Free-text provenance fields: `owner`, approval `by`/`reference`, reasons, references and
  evidence refs are bounded only by their document limit. `section` and `reuse` may be empty.
- UTC RFC 3339 `Z`/`z`/`+00:00` timestamps and a lowercase `t`. Lifecycle ordering and
  same-instant detection now compare instants, not strings.
- Personal catalogs may include ancestry `pack:` locators (spec 4.2), still inactive.
- Exactly 16 include edges is allowed and 17 fails. The first draft rejected 16.
- `--context-budget-chars` has no upper cap. The spec lets it raise only the output ceiling.
- Carriage return is allowed in text.

Stricter-than-spec choices retained, with their justification, for the reviewer:

- Other C0 control characters are rejected (R09 terminal/log injection).
- JSON nesting is capped at 64, preventing recursion exhaustion. Real records nest at most 4 levels.
- Settings, extension keys and source IDs must be dotted namespaces (spec says "namespaced").
- Version strings are capped at 64 characters, and selector keys and fact values at 128.
- Duplicate revocations, override settings and exception clauses are rejected as ambiguous.

`topology.md` R1 records explicit lane membership: each of the 48 IDs is either completed or
assigned once, with 4.2.a and 4.2.b suffix-split. It also records the accurate original
graph: a declared total order in which 2.1.a already depends on 1.3.c.

- `python -I -B tests\unit\patterns.py` -> exit 0, 36 tests OK. New cases:
  `AuthorityTests.test_null_is_a_json_scalar_setting_value`,
  `SchemaTests.test_spec_permitted_forms_are_accepted`,
  `SchemaTests.test_lifecycle_order_uses_instants_not_spellings`, the 16/17-edge boundary in
  `PinTests.test_cycles_depth_and_conflicting_digests`, and the personal-to-pack include case in
  `SelectorTests.test_personal_scope_is_explicit_only`.

## 2.2.b / 2.2.c (core lane; implemented ahead of the join, checkboxes pending P1 review acceptance)

`build_lock`, `write_lock`, `parse_lock`, `selection_digest`, `verify_lock`, `parse_task_map`,
`map_lock`, `project_package`; shared `_WriteLock` (exclusive creation, owner-only release, no
stealing) and `_atomic_write` (same-directory temp, fsync, atomic publish; no-overwrite mode).
CLI `resolve --lock`, `verify-lock`, `map`, `project`.

- `python -I -B tests\unit\patterns.py PinTests` -> exit 0, 14 tests OK:
  - Includes: 4 tests, from 2.2.a.
  - Lock (6):
    - digest stable across `created_at`;
    - evidence/metrics excluded from the digest;
    - asset pins and compact clause text present;
    - LF/no-BOM output with no local absolute root;
    - tampered clause text and tampered context rejected;
    - needs-context and conflict never lock;
    - existing lock never overwritten;
    - outside-repository path refused, with no temp residue;
    - verify cases: unchanged, unrelated addition, changed context, deprecated warning,
      retired and revoked block, changed bytes, deleted catalog, added mandatory binding,
      demoted required binding, pack manifest drift;
    - lock bytes unchanged by verify;
    - CLI exit codes 0/6/0/3/5.
  - Mapping (4):
    - preview writes nothing;
    - `--write` installs the mapping without changing `selection_digest`;
    - per-package projection, with a shared clause in both packages;
    - unknown package rejected, uninstalled map warned;
    - nine invalid maps rejected with the lock byte-identical;
    - stale digest gives a collision;
    - a foreign `.lock` file gives `write_locked` and is left intact;
    - recommendations optional;
    - remap reports the invalidated evidence and keeps it;
    - CLI exit codes 0/6/0.
- Mutation probe (run once, source restored byte-identical): disabling the revocation block
  failed 1 test, skipping the unmapped-must check failed 4, and allowing lock overwrite
  failed 2.
- Full file: `python -I -B tests\unit\patterns.py` -> exit 0, 46 tests OK.

## 3.1.a / 3.1.b / 3.1.c (core lane; checkboxes pending P1 review acceptance)

`capture`, `index_source`, `approve` plus CLI `capture`, `index`, `approve`. Publication runs
under one per-root exclusive lock, with CAS on the catalog digest, immutable no-overwrite
staging and catalog-last atomic replacement.

- `python -I -B tests\unit\patterns.py LifecycleTests` -> exit 0, 9 tests OK:
  - First capture requires `--source-id` and creates the catalog plus a draft; the
    `inferred_sources_only` warning fires.
  - Six refusals leave the tree byte-identical: non-draft, name mismatch, missing or stale
    CAS, source-ID mismatch, existing version.
  - Repo scope without a repository root is refused. Personal capture works without one and
    is never active.
  - A foreign lock blocks the write and is left intact.
  - Interrupted staging:
    - `index` never discovers it;
    - identical bytes are recovered by the owning capture;
    - different bytes are a collision;
    - no `.lock`/`.tmp` residue remains.
  - `index` rebuilds a hand-edited summary while preserving lifecycle, bindings, revocations,
    includes, extensions and source ID. This covers the spec's explicit sequences:
    deprecate->index keeps `deprecated`, and remove->index keeps the entry removed although
    its directory remains.
  - `index` refuses edited bytes, a missing registered file and a foreign root.
  - `approve`:
    - rejects equal or lower versions and a stale digest;
    - publishes 1.0.0 with the approval inside the digest, leaving the draft byte-identical;
    - the result resolves;
    - re-approval collides, and approving a non-draft is refused.
  - Children-first approval: a draft dependency blocks with the tree unchanged, a child
    approval followed by the parent update succeeds, and a source-less draft is refused.
  - CLI exit codes 0/6/0/0.
- Mutation probe (run once, source restored byte-identical): each of six broken guarantees
  failed at least one test. They were: CAS disabled, non-draft capture, dependency check
  skipped, lock stealing, index blessing edits, and staging overwrite.
- Full file: 55 tests (see the commit record).

## Review revision R2: fixes for independent review of `eaffeb6c` (FAIL: 2 P1, 5 P2, 5 P3)

Source: reviewer c3015de8 report `review-p0-p1-eaffeb6c.md` and `repro.py`, read only through
the parent's authorization. The reviewer's files were not modified. A copy of `repro.py` in this
session's artifacts was executed against the fixed tree.

Reviewer repro outcomes, before (eaffeb6c, per the report) and after this fix:

| Repro | Before | After |
| --- | --- | --- |
| R1 `.claude` junction | `ready`, outside pattern selected and read | `unsafe_path` (invalid), zero reads |
| R2 default-bound tampered / revoked / retired / missing | `empty`, exit 0, warning | each `unavailable`, exit 5 |
| R3 identical bytes in two sources plus one exception | two `M-1` records (`pack/mandatory`, `repo/waived`) | one `M-1`, `repo`, `waived` |
| R4 repo include of the pack catalog | `pack.base` re-scoped to repo; default conflict | `pack.base` stays `pack`; winner repo `12`, same as without the include |
| R5 missing `--context` | exit 5 `source_missing` | exit 2 `input_missing` |
| R6 malformed profile ancestry | exit 1, traceback, no JSON | exit 2, JSON `invalid_pack_context` |
| R7 pack binding to a personal pattern | `ready`, personal selected at pack scope | `unavailable`, `personal_ref_refused` |

New tests: `ReviewRegressionTests`, 10 cases:

- F1 `.claude` and `.claude/patterns` junctions refused for resolve, list and capture, with zero
  reads and no outside writes; a directory at a file path is `unsafe_path`.
- F2 five default-bound failure modes are unavailable, while non-applicability is still a skip
  with zero body reads; verify-lock blocks a revoked pinned default.
- F3 identity dedupe, with equivalent refs, merged reasons and the strongest role; differing
  digests conflict.
- F4 an included pack catalog is scope-stable, and a repo binding to a pack pattern selects at
  repo scope.
- F5 personal refs from pack bindings or pack includes are refused; repo bindings and explicit
  references are allowed.
- F6 `asset_refs` filters, and `read_asset` success, wrong phase, undeclared or escaping paths,
  tampered bytes and pin-shape equality.
- F7 `selection_digest` presence, equality with the lock, refs sensitivity and tamper refusal.
- Advisories: missing input, malformed profile, 1-6 fraction digits, and no `fromisoformat`
  dependency.
- A positive real ADR-0029 stored context record through the API and the `envelope` CLI; a forged
  record is refused.

- `python -I -B tests\unit\patterns.py` -> exit 0, 65 tests OK. No temp residue: the profile case
  removes MAX_PATH-length history through the native path, as the existing profile integration
  test does. Two directories left by an earlier failed run were removed from the synthetic TEMP.
- Mutation probe (run once, source restored byte-identical): reverting each of F1-F7 made exactly
  its own regression test fail, and no other test.
- Not observed: Python 3.10 (none on the host; downloading one would write the real user cache).

## Milestone acceptance and review revision R3 (`ae9d6df7` re-review)

Reviewer c3015de8 report `review-milestone-ae9d6df7.md`, read only through the parent's authorization:

- SPEC PASS and QUALITY PASS; findings P0 0, P1 0, P2 1, P3 4.
- Accepted for dependent dispatch. The parent approved the topology reordering.
- Leaves 2.2.a-2.2.c and 3.1.a-3.1.c are ticked on that reviewed milestone evidence. The whole
  feature is still pending: this is not ADR-0028 v2 clearance or ship readiness.

Fixes (contract R3):

- **P2-1** `selection_digest` now covers complete selected records.
  - `parse_lock` checks `asset_pins == asset_refs(lock)`, the reasons and the equivalent-ref
    shape.
  - `build_lock` refuses edited reports.
  - `verify_lock` re-derives summary, clauses and assets from the pinned bytes, verifies every
    equivalent pin, and compares role, scope, reasons and equivalents with the current
    resolution.
- **P3-1** `read_asset(selection=)` enforces selected-asset membership.
- **P3-2** `approve` takes its dependency snapshot inside the owned lock, checked against the
  in-lock preimage, with an optional caller catalog CAS.
- **P3-3 / P3-4** Documented.

Tests: `MilestoneReviewTests`, 5 cases:

- **Lock edits.** Five lock edits are rejected in two ways:
  - with the stale digest (invalid_lock);
  - with a forger-recomputed digest (invalid_lock, lock_content_mismatch, or
    selection_provenance_changed).
- **Report edits.** Three report-field edits give lock_refused.
- **Provenance change.** A real pinned-equivalent removal gives unavailable, and an added
  binding gives a conflict on `reasons`.
- **Asset selection.**
  - `read_asset` with a selection succeeds;
  - an unselected pattern's asset is refused with a selection but allowed without one;
  - a needs-context report gives selection_not_usable;
  - a tampered lock gives invalid_lock.
- **Concurrent revoke.** A lock-honouring revoker firing at the first `load_sources` is held
  off (`write_locked`), and the approval never co-exists with a revoked dependency.
- **Revoke before approval.** This gives dependency_not_approved with the tree unchanged. A
  stale catalog CAS gives a collision, and a correct CAS writes.

Results:

- `python -I -B tests\unit\patterns.py` -> exit 0, 70 tests OK.
- Mutation probe (run once, source restored byte-identical): each of seven reverted guarantees
  failed at least one of these tests. The reversions were:
  - the digest stripped to ref/role/scope;
  - no asset_pins check;
  - no body re-derivation;
  - no provenance compare;
  - a pre-lock snapshot with the in-lock check kept;
  - the exact old approve behaviour;
  - no membership check.

## Swarm reconciliation (RN-11)

- `python -I -B bin\li-work-artifacts.py --repo . --map .claude\plans\reusable-patterns\work.json` -> exit 0.
- `python -I -B bin\li-swarm.py validate --repo . --coord .claude/plans/reusable-patterns/swarm/coordination.json`
  -> `ok: true`, no diagnostics.
- `li-swarm.py wave --host-capability native` -> wave 1, with CORE, PACK and WF as the dispatch
  candidates and no `blocked_by`. The P0P1 prerequisites were read as complete from the converted
  checklist items. `release_clearance: false`.
- `li-swarm.py check-scope --task CORE --actor worker` over the CORE subset of `ae9d6df7..777b4f6d`
  (`bin/li-pattern.py`, `lib/patterns.py`, `skills/pattern/SKILL.md`, `tests/unit/patterns.py`)
  -> `ok: true`. The same range's `.claude/plans/reusable-patterns/**` paths are coordinator
  writes by the same session in its coordinator role, and `check-scope` correctly flags them as
  outside the CORE worker scope.

  Attribution: path-level only. The integration session plays both roles, and some commits mix
  coordinator and CORE paths. The pack and workflow lanes have their own worktrees and branches;
  their check-scope runs before each join.
- Command-surface guard: 1 finding, `missing-path` for the WF-owned planned path
  `references/` directory under the pattern skill in the package boundary. It is pending join (RN-11). The
  `catalog-regenerates-clean` shape test reports drift for the new `pattern` skill; this is
  pending INT 6.1.b. `frontmatter-lint-all` and `skill-descriptions-trigger` pass.

## Review revision R4 (re-review of `f1918e12`: SPEC PASS, QUALITY PASS with 1 P2 and 3 P3)

Reviewer c3015de8 report `review-r3-f1918e12.md`, read only. An unmodified copy of `repro-r3.py`
(SHA256 `68CDD742…6ACD`) was run against the fixed tree, using a discriminator module from
`git show ae9d6df7:lib/patterns.py` in the synthetic TEMP (removed afterwards). Output is kept in
this session's artifacts.

| Repro | Before (f1918e12, per report) | After |
| --- | --- | --- |
| R3 add an unselected record, resealed | verify `ok`; `read_asset(forged lock)` returned bytes | `conflict` `selection_changed` (the forged lock still carries its own asset ref, so consumers must verify first) |
| R3b remove the only selected record, resealed | verify `ok` | `invalid_lock` (status/selection mismatch) |
| R4 edit must `text`, resealed | `ok` | `conflict` `requirement_changed` |
| R4b must state mandatory -> waived | `ok` | `conflict` `requirement_changed` |
| R2 `effective_status` edited | `ok` | `conflict` `selection_provenance_changed` |
| R6b edited report, stale digest | bytes returned | `selection_not_usable` |
| R10 `status` empty / `context_budget` edited | parse ok | `invalid_lock` |
| R9b ae9d6df7-built lock | `invalid_lock` (misleading message) | `invalid_lock`, and the message says to regenerate |
| R0, R7, R8 and R9 known-good paths | as reported | unchanged: `ok`, `pinned_revoked`, `dependency_not_approved`/`write_locked`, empty lock `ok` |

R6 `selection=report` without `context` now reports `selection_not_usable` by design, since
report selections are in-process only.

New `ResealedLockTests` (8 cases) cover:

- a genuine lock;
- a grafted record, with `read_asset(selection=genuine)` still refusing its asset;
- seven resealed edits: record removed, must text, must -> waived, verify, setting,
  effective_status, dropped default clause;
- legitimate later changes that still verify: an added default binding (warning), and a
  deprecation (warning);
- a genuine waived lock and an empty lock both `ok`;
- status and budget binding;
- an edited report and a wrong-context report refused;
- map/verify/project on a verified lock.

`python -I -B tests\unit\patterns.py` -> exit 0, 78 tests OK.
Mutation probe (run once, source restored byte-identical): each of seven reverted R4
guarantees fails at least one `ResealedLockTests` case. The reverted guarantees were:
lock-only records, requirement records, extra clauses, the status check, the budget
digest, report recomputation and settings.

Coordinator metadata (same session, coordinator role): PACK `write_scope` is now the lane's
confirmed literal inventory. `lib/profile_context.py` is removed (conditional, unused), and the
guessed `pattern-roots.*` entries are replaced by `pattern-launcher-roots.*` and
`pattern_pack_harness.py`. The plan records 48 original IDs and 50 executable leaves.
`li-swarm.py validate` reports ok, and the map validator exits 0.

## 3.2.a-3.3.b and 4.2.b.core (CORE lane; implemented, unticked pending independent review)

New code: `dependents`, `update`, `record_lifecycle`, `apply_change`, `remove`, the spec 4.5
attestations (`parse_attestations`, `merge_attestations`, checks inside `resolve`, and
`record_attestations`), `export_bundle`/`import_bundle`, `review_coverage`, and the CLI commands
`update`, `deprecate`, `retire`, `revoke`, `remove`, `apply`, `export`, `import`, `review`,
`verify-lock --attestations/--write` and `resolve --attestations`.

`python -I -B tests\unit\patterns.py MaintenanceTests BundleTests ReviewCoverageTests` -> exit 0, 21 tests OK:

- **MaintenanceTests** (V07, 10 tests):
  - update: diff, includes and lock impact, a preserved old version, 3 refusals and a stale digest;
  - lifecycle: preview, CAS, the monotonic rule, revoked pins blocking verify-lock, no un-revoke;
  - pack sources are read-only;
  - apply: add/replace/remove with the reduced baseline, CAS and 4 refusals;
  - URL and overdue attestations: 4 rejection reasons, and another content digest does not count;
  - statement and local-file attestations, including changed bytes that need recapture;
  - renewal: saved attestations are used, expiry blocks, a renewal under CAS keeps the selection digest;
  - remove: refused for a referenced entry, files kept, remove->index stays removed;
  - the lock scan is bounded to the repository plan root;
  - CLI exit codes.
- **BundleTests** (V08, 6 tests):
  - the exact closure with an asset, with no catalogs or absolute roots and no staging residue;
  - revoked members are refused;
  - preview, then children-first drafts with inert provenance and re-hashed includes; imports
    are not eligible until local approval;
  - hostile bundles are rejected with nothing written: a stray script, a tampered asset, a
    partial or duplicate version map, an external dependency, a retired member, an existing
    destination version, a source mismatch;
  - a junction inside the bundle is refused;
  - CLI.
- **ReviewCoverageTests** (4.2.b.core, 5 tests):
  - complete evidence gives `ok` with `release_clearance: false`;
  - seven unmet mandatory forms each give exit 7, and a missing default only warns;
  - a waived clause needs the exception recorded in the lock;
  - stale mapping, invalid items or selection, and failed source verification before coverage;
  - an unmapped lock is refused;
  - CLI exit 7.

Results:

- Full file: `python -I -B tests\unit\patterns.py` -> exit 0, 99 tests OK.
- Mutation probe, run once with the source restored byte-identical. Each of these reverted
  guarantees failed at least one of these tests:
  - update same version;
  - lifecycle monotonicity;
  - apply CAS;
  - attestation expiry;
  - local source bytes;
  - remove references;
  - import stray files;
  - import dropping approval;
  - review passed without refs;
  - review skipping verification.

The pattern skill documents the delivered operations. Contract: "Maintenance, attestations,
sharing and review".

## Review revision R5 (re-review of `d82b2919`: CONDITIONAL SPEC PASS, QUALITY PASS; 1 P2, 2 P3)

Reviewer c3015de8 report `review-r4-d82b2919.md`, read only. Parent decision: the simple strict
alternative. An unmodified copy of `repro-r4.py` (SHA256 `E0C458CD5F5330D3…`) was run against the
fixed tree. The discriminator module came from `git show f1918e12:lib/patterns.py` in the synthetic
TEMP and was removed afterwards. Output is in this session's artifacts.

| Repro | Before (`d82b2919`) | After |
| --- | --- | --- |
| D1 resealed omission of a default record, repo and catalog binding | `ok` + warnings | `conflict` `selection_changed`, both locations |
| D2 omission + forged winner value | `ok` | `invalid_lock` (internally inconsistent), both locations |
| D3 forged required record's default setting | `ok` | `invalid_lock` |
| D3b / D3c | conflict | `invalid_lock` (caught earlier, at parse) |
| D4 deprecated-at-lock resealed as approved | `ok` + warning | `conflict`; the genuine lock is `ok` + `pinned_deprecated` |
| G1/G2/G3 genuine later default add, default remove, required add | G1 `ok` + warnings | all `conflict` (re-plan) |
| G5 re-scope with the same selection | `ok` | `ok` (unchanged) |
| E, B, O, N | as reported | unchanged; E's parse-only resealed lock still reads assets, which the documented precondition now forbids |

New `StrictBaselineTests` (6 cases), plus an updated `ResealedLockTests` legitimate-change case:

- D1 on repository and catalog bindings;
- D2, D3 and a plain value edit, each giving `invalid_lock`;
- a dropped recommendation clause gives `invalid_lock`, and a clause dropped from both the record
  and its requirements gives `lock_content_mismatch`;
- genuine later default add and remove give conflict, while an unbound catalog addition gives `ok`;
- P3-R4-1: a deprecated-at-lock pin resealed as approved;
- legitimate cases still verify: an override winner, a waiver, an empty lock, map, verify and project.

Results:

- `python -I -B tests\unit\patterns.py` -> exit 0, 105 tests OK.
- Mutation probe, run once with the source restored byte-identical. Each reverted guarantee failed
  at least one test: fresh-only records, the settle re-derivation, the settings comparison, the
  unchanged-catalog deprecation rule, and the record/requirement invariant. The probe first
  exposed an uncaught gap, the invariant; it was added and its regression written before this
  commit.

Truthful guard counts: at `8aa1f89e` and `d82b2919` the command-surface guard reported 3
`missing-path` findings, not the 1 that reconciliation RN-11 stated. RN-11 is corrected. After
`c92ae4dc` it reports 1, the WF-owned plan boundary, pending join. That later cleanup is not
retroactive evidence for R4.

## Review revision R6 (review of `c92ae4dc`: FAIL, 1 P1 and 9 P3; R5 review P3-R5-1)

Reviewer c3015de8 reports `review-core-c92ae4dc.md` and `review-r5-c177509b.md`, read only. The
R5 review passed with 0 P0/P1/P2 and closed P2-R4-1, P3-R4-1 and P3-R4-2.

An unmodified copy of `repro-c92.py` (SHA256 `6C68E3872CADBE7B…`) was run against the fix. Its
output is in this session's artifacts.

| Repro | Before (`c92ae4dc`) | After |
| --- | --- | --- |
| A1 import -> approve child -> read_asset / export | only `pattern.json`; `source_missing` | `guide.md` + `pattern.json`; read ok; export ok; check ok |
| A2 update -> approve -> read_asset | `source_missing` | ok |
| A3 approve with a pattern-root source | `pattern.json` only | `evidence.md` + `pattern.json` |
| B1/B2 preview of an invalid transition | `ok` | `invalid_schema` transition (same as the write) |
| C2 default URL source | no warning | `source_unverified_default` |
| C3 raw attestations | `KeyError`/`TypeError` | `invalid_schema` |
| C7b malformed saved attestation | conflict | `invalid_schema` at parse |
| D1 apply binding to a ghost | written | `binding_ref_unavailable`. The repro's unwrapped D section stops at this intended exception, so D2/D3 are covered by unit tests instead |
| F1 orphan after collision | `guide.md` written | no files written |
| F3 revoked events, approved status | imports | `invalid_bundle` |

New `CoreReviewTests` (10 cases, real flows):

1. export -> import -> children-first approve -> update the parent's includes -> approve ->
   resolve -> lock -> verify -> `read_asset(selection=lock)` -> `check_sources` -> re-export.
2. update -> approve, carrying an asset and a pinned pattern-root source; unrelated files are not
   copied, and the local-source attestation still applies.
3. A missing, a tampered, or an edited-after-capture file fails before publication, with the tree
   unchanged.
4. capture: `files_from` is required; `check` detects a deleted asset while `list` reads zero
   assets; the CLI default directory works.
5. P3-1 preview rules and the returned `catalog_sha256`.
6. P3-2.
7. P3-3 and P3-4, covering 5 malformed inputs on resolve and verify_lock, and junk saved
   attestations.
8. P3-5, P3-6 and P3-7: ghost refs refused; the first apply creates `.claude`; the CAS message
   names bindings and `--expected-digest`.
9. P3-8.
10. P3-9 is in `BundleTests`: an inconsistent retired status and laundered revocation events are
    refused.

`LockTimeTests` covers P3-R5-1 (reviewer K1):

- building at 2027-01-01 across the expiry gives `lock_refused`;
- building on the resolution day gives `ok`;
- resume after expiry is still a conflict.

Every test lock is now built at a fixed `NOW`.

Results:

- `python -I -B tests\unit\patterns.py` -> exit 0, 115 tests OK.
- Mutation probe, run once with the source restored byte-identical. Each reverted fix failed at
  least one test. The reverted fixes were:
  - approve drops files;
  - update drops files;
  - check ignores files;
  - no preflight;
  - preview skips the rules;
  - no default URL warning;
  - raw attestations unchecked;
  - apply accepts ghost refs;
  - bundle status trusted;
  - build_lock not self-validated.

## Review revision R7 (independent PACK review of snapshot `db7f6df1`: coupled core fixes)

The report is `pack-lane-independent-review.md`, from a separate integration reviewer; I read it
only. No pack-owned file was changed.

- **F1.** `SchemaTests.test_pack_context_reuses_profile_record` now pins an explicit fixture
  neutral baseline and asserts both outcomes:
  - legacy neutral (no `patterns` block): the child `{other: x}` stays `absent`;
  - new neutral (`patterns.source: null`): the missing field is filled, giving `null` with the
    neutral origin, while an inherited value still wins.

  Probe: I overlaid db7's `packs/_default/pack.yaml` and `lib/pack-schema.yaml` onto a scratch
  copy of this tree, in session artifacts, and removed it afterwards. `patterns.py` ran 116/116
  OK. Before the fix, the same overlay failed exactly that test (115 run, 1 FAIL).
- **F2.** `build_envelope` refuses a linked anchor before resolving it, and `parse_roots` refuses
  a linked personal root. `PathTests.test_linked_anchors_are_refused_on_every_route` covers
  junctioned repository and personal roots through:
  - the API envelope;
  - raw `parse_roots`;
  - `--roots-file`;
  - the CLI `envelope`.

  The outside tree is byte-identical afterwards, and the real path is accepted. The launcher
  route is PACK's; its tests run at the join.
- **F3.** Upgrade and rebind notice added to ADR-0038 and the evolution entry. INT public docs
  are pending.
- **F6.** The existing provider behavior is described in contract R7. No new root was added.

`python -I -B tests\unit\patterns.py` -> exit 0, 116 tests OK.

## Review revision R8 (review of `8addc395`: R6 closure accepted; P3-R6-1, P3-R6-2)

Reviewer c3015de8's report is `review-core-closure-8addc395.md`, which I only read. SPEC and
QUALITY both passed, with 115 tests and the clock shifted to 2027 and 2030; all prior findings
are closed. This revision is applied on top of R7 (`2fd07f00`), whose target stays unchanged.

The fix is one shared namespace check inside `_preflight`, applied to every destination before
the first write. Each version's closure is also checked on its own by `_version_files`, at
preview time.

New `NamespaceTests` (6 cases):

1. **Reserved body name.** The name `pattern.json` is refused, for an asset and for a
   case-varied `root: pattern` source, on the first attempt and on retry. An update preview that
   would create it is refused too. A nested `docs/pattern.json` publishes.
2. **Resealed draft.** A registered draft resealed with a `root: pattern` source named
   `pattern.json` cannot be approved, and two attempts leave no `1.0.0` directory.
3. **Case collisions.** Case-variant assets are refused, and so is an asset colliding by case
   with a source. An asset and a source naming the same exact file coalesce.
4. **Update prefix collision.** Mixing a fallback `a/b` with a supplied `a` is refused in both
   preview and write. Valid nested `a/b` plus `a/c` publish.
5. **Existing disk file.** A file already on disk where a directory is needed gives
   `destination_conflict`, not a traceback.
6. **CLI.** A case collision exits 2 with no traceback.

Results:

- `python -I -B tests\unit\patterns.py` -> exit 0, 122 tests OK.
- Mutation probe, run once with the source restored byte-identical. Each removal failed at least
  one test:
  - the casefold key;
  - the prefix check;
  - the on-disk ancestor check;
  - update bypassing the version check;
  - the version-level reserved check (caught by the preview case);
  - the publish-level preflight.

Contract R8 records the compatibility notice for the stricter `check`.

## Review revision R9 (review of `445e3ad9`: SPEC/QUALITY PASS; P3-R8-1, P3-R8-2)

Reviewer c3015de8's report is `review-core-closure-445e3ad9.md`, read only. I ran unmodified copies
of `repro-r8.py` (`80B46DD9…`) and `repro-r8b.py` (`F296B80C…`).

Repro results:

- **S1** (a sibling `a.md`, `a-b` or `a b` between `a` and `a/b`): preview, write and retry each
  give `destination_conflict`, and the CLI gives no traceback.
- **S3**: the reserved body name is still refused, and nested `docs/pattern.json` still publishes,
  approves and checks.
- **T1**: CLI preview and write exit 2, the catalog is unchanged, and there is no orphan.
- **T2** (`Docs/x` + `docs/y`, and an asset `docs/` + a source `DOCS/`): `destination_conflict`,
  with nothing stored.
- **T3**: a case collision is refused, a same-file pinned source coalesces, and a different
  pinned sha gives `declared_file_conflict`.
- **T4**: a valid nested approval publishes.

New `NamespaceInvariantTests` (4 cases):

- 11 refused sets, checked in every permutation. They cover the sibling separators `.`, `-`,
  space and `_`, a grandchild, a deep child with siblings in between, a case-varied file versus a
  directory, a file case collision, a directory spelled two ways, a multilevel ancestor, and a
  Unicode casefold (`Straße`/`STRASSE`).
- 4 allowed sets, checked in every permutation, plus same-bytes coalescing and a different-bytes
  refusal.
- 8 real CLI `update` cases that mix previous-version fallback files with supplied files. Each is
  run as preview, write and retry, and each exits 2 with no traceback and no change to the tree.
- Valid similar siblings and nested paths publish through capture and approve.

Results:

- `python -I -B tests\unit\patterns.py` -> exit 0, 126 tests OK.
- Mutation probe, run once with the source restored byte-identical. Each of these failed at least
  one test: the old R8 adjacency check, removing the directory-spelling check, and removing the
  file-versus-ancestor check.

## Supplementary POSIX run (parent-owned) and R7 doc corrections

- **POSIX (parent-provided, supplementary).** The parent ran the exact R7 archive of `2fd07f00`,
  taken with `core.autocrlf=false` (archive SHA256 `0190a2fd…8070`), on an existing WSL Ubuntu
  24.04 host. It used native `/tmp` fixtures and `env -i` with a synthetic HOME, TEMP and Git
  config. `python3 -I -B tests/unit/patterns.py` gave 116/116 OK with no skips; the log is in the
  parent's session artifacts.
  - Toolchain: Python 3.12.3, Bash 5.2.21, Git 2.43. The existing PyYAML is 6.0.1, below the
    declared 6.0.3 floor.
  - This is supplementary POSIX behavior evidence only. It is not supported-toolchain, full-suite
    or host acceptance, and it does not validate Python 3.10 or a native client.
- **R7 non-blocking doc corrections** (the reviewed targets are unchanged):
  - The contract now says the anchor check covers only the final component, that linked ancestors
    resolve normally, and that consumers must surface `invalid_roots` rather than neutral success.
  - The evolution migration section now says there is no data migration, but an explicit context
    rebind is required.

## Main reconciliation and R9 acceptance

- **R9 review.** Reviewer c3015de8 reviewed `1575a90a`: SPEC PASS and QUALITY PASS with zero
  findings at every severity. This is milestone acceptance only, not native ADR-0028 v2
  clearance. A final joined review is still required.
- **Main merge.** `b33fe3f0` is an ordinary merge of settled `main` at `49f2d152`, which contains
  #109 and only touches `docs/GLOSSARY.md` and `docs/faq.md`, into `1575a90a`. There were no
  conflicts. After it:
  - `tests/unit/patterns.sh` passes, 126 OK;
  - the map validator exits 0;
  - `li-swarm validate` is ok;
  - the guard reports only the known pending WF finding.

## Revision R10 (WF review M2: public report validation helper)

The parent authorized this core interface action. The WF review report
(`wf-visual-independent-review.md`, reviewer 24bf5df0) was read only. M2: the visual adapter
trusted a raw report after checking only its key and digest format, while `read_asset` already
recomputed the digest.

The fix extracts that existing check as `validate_selection_report`, and `read_asset` now calls it.
There is no new digest policy, parser, cache or authority. The WF adapter adopts the helper in its
own lane.

`SelectionReportTests` (6 cases):
- a fresh ready or empty report is accepted with file reads forbidden, both `Reader.read` and
  `open` monkeypatched to raise;
- missing or wrong context, missing refs, raw versus parsed refs, and invalid raw refs;
- edits with an unchanged digest are refused: the M2 repro (setting value `9999px`), requirement
  text and state, selected assets, an added record, and exceptions;
- invalid states: needs-context, no digest, a lock, missing keys, a preview, a non-mapping, and a
  status edited to `conflict` or `needs-context`;
- legitimate overrides and waivers pass;
- `read_asset` refuses the M2 tampered report through the same helper.

`python -I -B tests\unit\patterns.py` -> exit 0, 132 tests OK. Mutation probe (restored
byte-identical): removing the digest recompute, the status check, or `read_asset`'s use of the
helper each fails at least one test. The context and preview checks are redundant with the digest
by design; the digest catches them.

## Authorized harness correction: `tests/integration/design-contract.py` (inherited failure)

Attribution: `tests/integration/design-contract.py` is added ONLY to the coordinator/INT reserved
paths (`coordinator_paths`, and the INT package boundary in plan.md). It is not in the CORE worker
`write_scope`, and `tests/` as a whole is not reserved. This is an explicitly authorized early
validation-harness correction, not the start of INT generators or docs.

The commits are separate and attributed:
- `67cb2ef4` is the harness fix, a coordinator/INT write.
- `1f7784e5` is the CORE worker's public helper.

The recorded acceptance is the actual 18-case runner, with its exact `source_revision`, under the
controlled synthetic empty setting. The parent's `--git-dir` repro only diagnosed the configuration
failure.

- **Scope extension.** The parent authorized one directly coupled correction to
  `tests/integration/design-contract.py`, which the integration coordinator owns (not WF).
- **Inherited failure.** The design-contract epilogue failed with exit 128 before any pattern
  change. The parent's root-cause repro, which touched no real credentials or config:
  - after `patch.dict(clear=True)` restores `os.environ`, a Windows child inheriting the native
    environment loses `GIT_CONFIG_VALUE_0=''`;
  - the counted `GIT_CONFIG_*` config then breaks, and `git rev-parse` exits 128;
  - passing `env=os.environ` explicitly preserves the value.
- **Change.** The final `source_revision` subprocess passes `env=os.environ`, with a why-comment.
  No `GIT_CONFIG_*` scrubbing, no trust, auth or hook flags, and no hard-coded index.
- **Evidence.** Synthetic HOME and TEMP, with the process-scoped synthetic config
  `GIT_CONFIG_COUNT=1`, `KEY_0=core.fsmonitor`, `VALUE_0=''`:

  | Run | Result |
  | --- | --- |
  | Before (HEAD `1f7784e5` file) | 18 tests ran; exit 1 from `CalledProcessError`, git exit status 128; no `source_revision` |
  | After | exit 0; 18 tests; `source_revision` = `1f7784e5…` exactly |
  | Without the synthetic config | exit 0; 18 tests; 0 failures, 0 skipped; exact `source_revision` |

  The before run used a temporary `git stash push`/`pop` of this one file in my own worktree. No
  history was changed.

## Attribution of `132bb9bb..67cb2ef4` (complete, unfiltered)

- **`1f7784e5`:** `lib/patterns.py` and `tests/unit/patterns.py` are CORE worker paths.
  `.claude/plans/reusable-patterns/contract.md` and `build-log.md` are coordinator writes by the
  same session. `li-swarm check-scope --task CORE --actor worker` over all four paths reports the
  two plan files as outside CORE scope, correctly, and passes the other two.
- **`67cb2ef4`:** `tests/integration/design-contract.py` is a coordinator/INT reserved path, plus
  the coordinator's `build-log.md`.
- The metadata commit that follows reserves `design-contract.py` in `coordinator_paths`.
  `li-swarm validate` is ok and the map validator exits 0.

## Review revision R11 (R10 review of `132bb9bb..67cb2ef4`: SPEC/QUALITY PASS, 2 P3)

Report: `review-core-r10-67cb2ef4.md`, read only. The harness fix was proven on committed
`67cb2ef4` (18 of 18 pass, exit 0, exact revision) and the old control fails with exit 128, so the
harness fix is closed.

This revision fixes P3-R10-1 and P3-R10-2 (contract R11). `SelectionReportTests` now has 9 cases:
- The mislabeled case is renamed from "edited to empty" to "status edited to needs-context".
- Both genuine flips are now tested: a ready report carrying required clauses and assets relabelled
  `empty`, and a genuinely empty report relabelled `ready`.
- `selected` as `None`, a string, or an array with a non-record element; NaN and cyclic settings.
  All raise `PatternError`, never a Python error.
- Generator and string refs are refused; a tuple of parsed refs passes; mixed raw and parsed refs
  keep the parser's `invalid_schema`.

Results:
- `bash tests/unit/patterns.sh` -> 135 OK.
- Mutation probe (source restored byte-identical): removing any of the four new checks fails at
  least one test. The four are status agreement with selection, the `selected` shape, `ValueError`
  conversion and the refs-type check.

## PACK join (serial join 1 of 2)

- **Authorization.** Integration reviewer 24bf5df0 approved `44c6b176` for serial join (report
  `pack-44c6-closure-review.md`; F1-F7 closed). One new non-blocking low finding, opaque MSYS
  conversion, is assigned to PACK as a separate later ordinary merge.
- **Merge.** `075a797d60a77c8244c39fddd9f24692c3702362` is an ordinary `--no-ff` merge with
  parents `a8ef0ae3` (integration head) and `44c6b176` (PACK). The tree was clean before and after.
- **PACK history.**
  - `7b0b246c` sits on `ae9d6df7`.
  - `d15d8664` merges `7b0b246c` with `2fd07f00`. This moves PACK's authorized dependency base from
    `ae9d6df7` to R7 `2fd07f00`, recorded here explicitly.
  - `44c6b176` is a test-only follow-up on top of `d15d8664`.
  - The review-only object `db7f6df1` was never promoted.
- **Join delta.** `a8ef0ae3..075a797d` is exactly the 9 PACK files: `bin/li-pattern` (100755),
  `lib/pack-schema.yaml`, `lib/paths.sh`, `packs/_default/pack.yaml` and the five pattern
  pack/launcher tests. `li-swarm check-scope --task PACK --actor worker` over the complete list
  reports `ok: true`. `ae9d6df7..7b0b246c` and `2fd07f00..44c6b176` are the same 9 files, and no
  inherited CORE file differs.
- **Joined checks** (synthetic HOME and TEMP, Windows, Python 3.11.9):

  | Check | Result |
  | --- | --- |
  | `bash tests/unit/patterns.sh` | 132 OK |
  | `bash tests/unit/pattern-pack-origins.sh` | 13 OK |
  | `bash tests/unit/pattern-launcher-roots.sh` | 12 OK |
  | `enterprise-pack-resolution`, `pack-inheritance-depth-3`, `pack-source-target-resolution`, `claude-home-paths`, `memory-v2`, `bin-scripts-executable` | all pass |
  | Map validator | exit 0 |
  | `li-swarm validate` | ok |
  | Command-surface guard | 1 finding: the pending WF consumer reference (`plan.md:82`). It is pending the WF join, not a pass and not faked |

- **Leaves.** 2.1.a-2.1.d are ticked on the PACK review approval plus these joined results. V05 and
  V14 run on the joined tree. The launcher-dependent parts of V09, V11 and V12 remain pending the
  WF join and INT.

## R11 acceptance and PACK L-P1 follow-up join

- **R11 accepted.** The same core reviewer checked `56d750d6`: SPEC and QUALITY PASS, with no
  findings at any severity (report `review-core-r11-56d750d6.md`). This is milestone acceptance,
  not native v2 clearance. WF is authorized to merge exactly `56d750d6` and adopt
  `validate_selection_report`. When WF is joined, its dependency base moves to `56d750d6`, and
  that will be recorded explicitly.
- **PACK L-P1 approved.** Integration reviewer 24bf5df0 approved `5e2ba144` (report
  `pack-5e2b-lp1-review.md`). It closes the production opaque-argument issue L-P1. A new low
  finding, L-P2, concerns only the test harness; it stays PACK-owned and will come in a later
  follow-up.
- **Join.** `69f208c648579002bc3062998de60c367b38355d` is an ordinary `--no-ff` merge with
  parents `56d750d6` (frozen R11 target) and `5e2ba144`. `5e2ba144`'s parent is `44c6b176`. Its
  3 PACK files (+52/-9) are `bin/li-pattern`, which keeps mode 100755,
  `tests/unit/pattern-launcher-roots.py` and `tests/unit/pattern_pack_harness.py`.
  `li-swarm check-scope --task PACK --actor worker` over the complete list returns `ok: true`.
- **Joined checks:**
  - `bash -n bin/li-pattern` exits 0;
  - `patterns.sh`: 135 OK;
  - `pattern-pack-origins.sh`: 13 OK;
  - `pattern-launcher-roots.sh`: 13 OK;
  - `li-swarm validate`: ok.

## WF final candidate pre-check (read-only; not joined)

Candidate:
- `14492a49` has parent `35937372`.
- `35937372` is the merge of `0364a664` and exact R11 `56d750d6`.

Delta `56d750d6..14492a49`:
- 45 WF files, +2919.
- `li-swarm check-scope --task WF --actor worker` over the complete list returns `ok: true`.
- WF changed no core or PACK path. Three PACK files differ from the integration head only
  because that head already carries PACK L-P1 (`5e2ba144`); WF did not touch them.

The join waits for integration reviewer 24bf5df0's verdict. At the join, WF's dependency base
update to `56d750d6` will be recorded explicitly.

Pending PACK follow-ups: L-P2 `660d7a32` is not merged; a replacement assertion was requested.

P6 addition: see reconciliation RN-13 (raw CRLF asset bytes through Git).

## WF join (serial join 2 of 2) and PACK L-P2 join

- **WF approval.** Integration reviewer 24bf5df0 approved `14492a49` (report
  `wf-14492-closure-review.md`). It closed M1-M4 and L1-L6 and retained I1. The only new finding
  is a low one, L-N1, and the parent decided it: see the consumer contract's "Missing runtime".
  - The reviewer ran V09 (31), V10 (26) and V11 (18) with no skips, using a real null-neutral
    envelope and the P07 fallback.
  - This is not native v2, feature or host clearance.
- **WF join.** `ab47b7d8e21b57131435f1a6c5f7ce04c9c0689f` is an ordinary `--no-ff` merge of
  `677aa38e` and `14492a49`.
  - Delta `677aa38e..ab47b7d8`: exactly WF's 45 files. `check-scope --task WF --actor worker`
    reports `ok`. The three PACK files carrying L-P1 are unchanged by the merge.
  - WF's authorized dependency base moved from `ae9d6df7`, through R6 `8addc395`, to R11
    `56d750d6` (through `35937372`). This is recorded explicitly.
- **PACK L-P2 join.** `ba4944045b7ff858af57d4b95e45404fe1d67cbb` is an ordinary merge of
  `ab47b7d8` and `118e3037`. The PACK chain is `660d7a32` then `118e3037`, on top of the
  already-joined `5e2ba144`, and it was approved with no new findings (report
  `pack-118e-lp2-closure.md`). The delta is 2 test files (+36/-21); production code is unchanged.
  `check-scope --task PACK` reports `ok`.
- **Joined tests** (synthetic HOME and TEMP; Windows; Python 3.11.9). None skipped, and the
  launcher cases ran for real.

  | Suite | Result |
  | --- | --- |
  | `patterns.sh` | 135 OK |
  | `pattern-pack-origins.sh` | 13 OK |
  | `pattern-launcher-roots.sh` | 13 OK (rerun after L-P2) |
  | `pattern-visual.sh` (V10) | 26 OK |
  | `pattern-workflows.sh` (V09) | 31 OK |
  | `pattern-visual-roundtrip.sh` (V11) | 18 OK |
  | `design-contract.sh` | 18 OK, exit 0 |

  The map validator exits 0 and `li-swarm validate` reports ok.
- **Guard.** The command-surface guard now reports PASS with 0 findings: the WF consumer reference
  that was the pending path has arrived. After the SKILL link commit it still reports 0.
- **Leaves ticked on the reviewed lane evidence plus these joined runs:**
  - 3.2.a-3.3.b and 4.2.a/b, including their `.core` and `.wf` parts;
  - 4.1.a-4.1.c;
  - 4.2.c;
  - 4.3.a, 4.3.b and 4.3.d;
  - 5.1.a-5.2.b.
- **4.3.c stays open.** Its acceptance needs real conversion, provider and host validation, which
  INT must perform; a format-fact test is not that validation.
- **Also still open:** real model/render V17 and host acceptance.

## INT packaging milestone (6.1.a-6.1.c)

- **Ownership.** The `bin/li-pattern` missing-runtime change is a coordinator/INT integration
  delta. It is not retrospective PACK worker work, and it is authorized by the parent after the
  accepted join. `tests/integration/pattern-portability.*` and `tests/shape/pattern-contract.sh`
  are INT-reserved paths, per the INT package boundary.
- **6.1.a.** Added:
  - `scaffolding/01-foundation/templates/pattern/`, holding `README.md`, the draft
    `pattern.template.json`, and the canonical neutral synthetic `example/`. The example has one
    approved dashboard pattern generated through the core API (digest `ec1759e0…`), a guide asset,
    a catalog with one required binding, and a source-local `.gitattributes` containing `* -text`.
  - `docs/concepts/patterns.md`, carrying the limits, the optional runtime, linked roots, the
    upgrade/rebind notice, the stricter-`check` compatibility notice and Git byte preservation.
  - pattern sections in `docs/architecture.md`, `docs/the-cycle.md`, `docs/multi-cli.md` and
    `docs/copilot.md` (the upgrade notice).
  - `skills/pack-create` and `skills/pack-validate`: the optional `patterns.source`, shipped
    files, and a separate pattern check.
- **6.1.b.** `bin/li-copilot.py` gains the `pattern` workflow, the `PATTERN_RESOURCES` closure
  check and `docs/concepts/patterns.md` in `DOCS`. I regenerated with the existing
  `li-copilot.py init --client copilot-cli`, using a recovery store in session artifacts
  (transaction `transaction-c406b06d…`). That created `.github/skills/li-pattern/SKILL.md` and
  updated `.github/lintel/manifest.json`. `python bin/li-catalog.py` regenerated
  `skills/CATALOG.md`. `tests/shape/skill-descriptions-trigger.sh` now lists `pattern`.
- **6.1.c.** Added:
  - `tests/integration/pattern-portability.py` with its wrapper, 6 tests. It generates a real kit
    into a target whose path has spaces and metacharacters, then runs the kit's own launcher and
    modules. It covers:
    - the closure and the wrapper link, with `li-copilot check` on the target passing;
    - a non-Git explicit root and a non-Git cwd, where the repository root is null;
    - the missing runtime: with no Python on PATH, exit 5, `pattern check unavailable`, no stdout;
    - the canonical example: `check` ok, then `resolve --lock`, `verify-lock`, and `read_asset`
      with the verified lock through the kit module; an unrelated backend resolves `empty` with
      0 pattern and 0 asset reads;
    - RN-13 for a repository source. A CRLF asset goes through capture, approve, commit and a
      fresh clone under a repository `*.md text eol=lf` policy. Without source attributes the
      bytes are rewritten and `check` reports `declared_file_changed` (exit 5). With the
      template's `* -text`, the bytes are exact, `check` is ok and `read_asset` returns the CRLF
      bytes.
    - RN-13 for a pack source. A pack declaring `patterns.source` with `* -text` goes through
      commit and a fresh clone. With `LINTEL_PROFILE_PACK=team`, the launcher `check` is ok at
      pack scope, and a real envelope, resolve and report-bound `read_asset` return the CRLF
      bytes.
  - `tests/shape/pattern-contract.sh`, 13 assertions.
- **Results** (synthetic HOME and TEMP, Windows, Python 3.11.9):
  - `pattern-portability.sh`: 6 OK.
  - `pattern-contract.sh`: all pass.
  - `native-command-surface`: 0 findings.
  - `catalog-regenerates-clean`, `frontmatter-lint-all`, `skill-descriptions-trigger` and
    `bin-scripts-executable`: all pass.
  - `li-copilot.py check`: 22 managed files verified.
- **Ledger.** 4.3.b and 5.2.a are unticked again. Their local helper acceptance is reviewed, but
  their original real-document and per-consumer model/render/host acceptance remains V17.

## First strict Windows full run on `b8312bb7` (interrupted, not a pass)

- `bash tests/runner/run-all.sh --require-all` ran with synthetic HOME and TEMP in the
  background. After 95 `RUN` lines it stalled for more than 45 minutes inside
  `integration/copilot-kit.sh`. The parent authorized stopping only this session's own run. I
  stopped it and its leftover own processes, and the runner printed no summary.
- The log is kept as session artifact `fullsuite-b8312bb7.log`, marked `INTERRUPTED`. It is
  partial evidence only and records no V16 result.

## POSIX full-suite finding and fix (`8fb265cf`, contract R13)

- The parent's Linux full run on `b8312bb7` (169 files: 165 pass, 4 fail) found one core
  defect. On a case-sensitive filesystem, a case-only or file-versus-directory collision among a
  version's declared files could surface as a missing or unreadable file rather than
  `destination_conflict`. The other three failures were two environment artifacts and a missing
  `pwsh`; the parent handled those separately. This is the parent's log, not a claim of a Linux
  full pass.
- The fix classifies the planned names before reading (reserved body name plus the shared
  namespace preflight) and treats ENOTDIR as not-a-link. `PlannedNamespaceBeforeReadTests`
  was added.
- Results:
  - Windows, synthetic environment: `tests/unit/patterns.py` 137 OK.
  - Parent's Linux run: 137 OK. Log `posix-8fb-patterns.log` in the parent's artifacts; read
    for this reduction.
- Independent review of `b8312bb7..8fb265cf` is with reviewer c3015de8.

## INT review of `b8312bb7` and Low fixes (`ea2c139d`, `fed0d884`)

- Reviewer 24bf5df0 accepted the INT packaging milestone with four Low findings and seven Info.
  This is milestone acceptance, not ADR-0028 v2 release clearance. Fixes, docs and tests
  committed separately:
  - `ea2c139d`, docs:
    - a missing JSON report means `pattern check unavailable`, whatever the exit code;
    - the Windows path-length limit (R12) is stated in the skill, template README and concepts
      page, with an observed and environment-dependent bare-install home budget rather than a
      promised number;
    - skill capture step 6 is the source-scoped `* -text` attributes step: never overwrite
      existing attributes, and state what `-text` does not disable;
    - a "Portable kit boundary" section in the template README.
  - `fed0d884`, tests:
    - the installed kit's example must be raw byte-identical to the source;
    - the source example must be LF-only, the boundary imposed by the generator's text
      normalization. (The commit also adds a missing final newline to the test files themselves;
      no test asserts that the example ends with a newline.)
- Rechecked after the commits, synthetic environment:
  - `li-copilot.py check`: 22 managed files verified.
  - `li-catalog.py --check`: clean.
  - `pattern-contract.sh`: all pass.
  - `pattern-portability.sh`: 6 OK.
  - `git diff --check`: clean.

## V17 host observations (coordinator-observed on frozen `b8312bb7`)

The parent ran fresh Copilot App task sessions and consolidated them in its artifact
`host-observations.json`, which I read for this reduction. The setup:

- development-mode native wrappers in separate fresh worktrees, not installed-target App
  discovery;
- ordinary user requests, with no expected pattern IDs, clauses or outcomes supplied;
- synthetic environment only, with no dependency, private pack or publication;
- no acceptance branch is an integration source, and none is merged here.

| Case | Request | Observed | Explicit limits |
|---|---|---|---|
| A | Internal analytics dashboard | Required repository dashboard pattern selected, with lock and task mapping. `project_visual`/`validate_visual` ran on the real frontend spec. In Chromium: sticky filters, consistent filters, CSV downloads matching visible rows, 1280px and `#1f6feb`. Coordinator: 12/12 app tests, and a 9999px in-memory negative failed DASH-03 with the original bytes unchanged | Chromium only. Builder self-review only; BUILD stayed blocked on independent review. One model and one client |
| B | Retry with backoff (backend) | `list` read metadata only. `resolve` returned `empty`: 0 selected, 0 requirements, 0 body reads, 0 asset reads. No lock or task map. Protected paths unchanged; 11/11 tests | Self-review only. Observed behavior, not universal automatic activation |
| C1 | Technical change document | Canonical `generate-word` route found DOC-01 and produced a real DOCX in Word Canvas. Copy-reopen, edit and readback restored identical bytes. Ledger 96/96 blocks; DOC-01 coverage passed with `release_clearance: false`. Coordinator checked the XML: Rollback is a Heading1 with content, and there are no macros or tracked revisions | **Word page rendering is unavailable in this host.** Shared rendered-page inspection stayed unverified (exit 3). No rendered-page or release clearance |
| C2 | Remove Rollback, run QA | A marked negative copy lost 21 paragraphs. Positive artifact, pattern, lock and map unchanged. `verify-lock` still passed. Pattern review exit 7, DOC-01 `mandatory_unmet`. Shared QA blocked. Review reader and SHIP exit 3 with no applicable independent decision; nothing fabricated | QA observations were authored by the task; helpers check structure and binding, not their truth. No page rendering |
| D | Resume dashboard (cold) | Coordinator revoked the pin in a separate cold worktree. The fresh task loaded the committed handoff and map; `verify-lock` exited 5 with `pinned_revoked`, digests unchanged. It stopped before BUILD or review | The first next-action prose wrongly suggested withdrawing the revocation. A docs-only correction states that v1 is append-only with no un-revoke; the original result is preserved |
| C-PDF | PDF companion via the existing provider | Work map, P07 profile and companion lock/mapping validated. The declared Markdown converter was unavailable, so labeled AI-authored HTML kept 96/96 blocks. The owned loopback server passed. **The existing print provider's fresh Chrome gave no verified DevTools endpoint, so no PDF was produced.** Cleanup was verified. Pattern review exit 7, DOC-01 unverified | Prepared-HTML fidelity is not PDF fidelity. No alternate flags, COM, private profile, dependency or PDF reader was used |

Deferred host rows, recorded as blocked or deferred rather than passed:

- **PDF conversion endpoint (4.3.c).** BLOCKED on the host/provider: no DevTools endpoint and
  no authorized PDF reader. Conversion preservation of required clauses is unobserved.
- **Word page rendering (C1/C2 shared inspection).** Unavailable in this host; still a required
  unverified control.
- **Per-consumer visual cells (5.2.a).** Case A's route was `li-cycle`/`li-build` with
  `project_visual`/`validate_visual` and a real browser, not an observed `generate-web` command
  route. `generate-web`, `design-dna`, `frontend-typography`, `frontend-motion`,
  `frontend-shader` and `generate-app` have no model, render or host cell.
- **Clients and browsers.** One client, one model, Chromium only. No installed-target App
  discovery, screen reader or other client. The numeric context capacity was not observed.

Ledger: 4.3.b is ticked. Its specific host case (a required named section, plus a QA negative
on a real generated document) is observed in C1/C2; page rendering stays a separate deferred
shared control. 4.3.c remains unticked and blocked. 5.2.a remains unticked. 6.2.b's host part is
recorded, but it remains unticked until the final independent aggregate review.

## RN-14 scope reconciliation (owner decision, 2026-09-28)

MasterCoordinator `9854860c` restored the original host obligations (reconciliation RN-14,
adjudication sha256 `fca066e8…e472d`):

- 4.3.c closes at V09 plus a V18 review, which is still missing.
- 5.2.a closes at V11 plus a V18 mapped-case review, which is still missing.
- PDF/Word pages are artifact QA, and the six per-consumer cells are disclosed deferrals.

The entries above stay verbatim as history; only the plan's status annotations changed.

## V18 at RN-14 and the direct-entry fix (`18489982`)

Reviewer 24bf5df0 reviewed `82e97d74` (`v18-rn14-82e97d74.md`, sha256 `d10a528f…659d`):

- 4.3.c is MET at source level, with 0 blocking and three Low findings.
- 5.2.a is NOT MET. M-1 (Medium): a direct `generate-web --mode mockup` entry relied on a lock
  that only the frontend-design route hands over. L-4: the plain `--brief` route had the same
  shape.

The fix, `18489982`, is bounded to the owner-approved D2 join scope and changes no resolver,
schema, provider or runtime:

- generate-web's "Reusable patterns" section adds one direct-entry rule for both routes:
  - resolve before the first design choice;
  - on `ready`, rerun with `--lock` inside the repository run and confirm the same
    `selection_digest`;
  - `empty` changes nothing;
  - every other status, and a run with no JSON report, blocks;
  - `project_visual` writes the final spec before its binding;
  - `load_design` and `validate_visual` run before rendering;
  - a handed-over lock goes through `verify-lock` first.
- `mockup.md` step 2 applies the rule before its decision method, and step 3 validates.
- L-1: a required section missing from the readable source or prepared HTML is failed at the
  source; presence in the produced PDF stays unverified.
- L-2: Visio DONE needs no failed or unverified mandatory clause, and the slot is never promoted.
- L-3 and I-2: the V09 docstring and the V11 deferral labels now follow RN-14 (supplemental, not
  V17 gates).
- New V11 `DirectEntryTests`, helper and source-wiring evidence only (not an executed model
  route, browser render or host cell):
  - a cold required max-width;
  - empty with no forced lock;
  - profile error, pack fallback, unevidenced fact and needs-context refusals;
  - stale, edited and changed-source locks;
  - mockup and plain-brief parity, and parity with a cycle lock.

Checks, synthetic HOME/TEMP, Windows:

| Check | Result |
|---|---|
| V11 `pattern-visual-roundtrip.py` | 23 OK |
| V09 `pattern-workflows.py` | 31 OK |
| `document-pdf.sh` | 16 OK + 6 node pass |
| `generate-skills-present.sh` | PASSED |
| `pattern-contract.sh` | ALL PASS |
| `frontmatter-lint-all.sh` | PASSED |
| `native-command-surface` | PASS, 0 findings |
| `li-copilot.py check` | 22 managed files |
| catalog check | clean |

The re-review is pending; 5.2.a and 4.3.c stay unticked.

## R12 palette precedence join (`23e8e194`, RN-15)

Reviewer 24's follow-up at `118d1c71` (`v18-m1-118d1c71.md`, sha256 `72dc0ae5…`) closed M-1, L-4
and the earlier Lows. Its R-4 source clarification (`e8e08cb6…`) then showed that `load_design`
could not admit a selected pattern palette winner over the pinned profile. MasterCoordinator
`9854860c` authorized the bounded Option 1 fix, with seven acceptance cases.

**Change (10 files, +473/-25):**

- `design_contract.py`: a verified-pattern admission in `load_design`, plus
  `--pattern-lock`/`--pattern-context` on `renderer-args` and `review`.
- `pipeline_inputs.py`: the same plumbing.
- `pattern_visual.palette_winners`.
- Docs: design-contract reference, frontend-design, generate-web, mockup, consumer contract.
- Reviewer R1: explicit `verify-lock` of a new direct-entry lock.
- Reviewer R2: a test message no longer claims an `--out` observation.

**Acceptance mapping** (new `tests/integration/design-contract.py` cases, real core
resolve/build_lock/write_lock, `project_visual` and `load_design`):

| # | Case |
|---|---|
| 1 | Repository default ink `#112233` loads over profile `#141413`, including the CLI; profile bytes unchanged. Pack default the same, selected scope `pack` |
| 2 | Without a lock, a projected spec is refused. A bare differing ink is refused. A real brief override still loads |
| 3 | Refused: a claimed winner, a forged `pattern_context` digest, an edited lock, an unselected lock, foreign lock paths, and a lock without its context |
| 4 | Refused before output: context change (`context_changed`), revoked pin, changed pinned source, missing lock |
| 5 | A brief override resolved through the core wins over a default. A brief against a `must` is a resolver conflict, and a brief colour against the mandatory lock is refused |
| 6 | Unselected `.claude/patterns` and a source changed after selection are refused |
| 7 | An empty selection leaves the spec and loading unchanged. A pipeline design-spec with a real attachment loads; without its lock it is refused, and with drifted ink it is refused |

**Checks** (Windows, synthetic HOME/TEMP):

| Suite | Result |
|---|---|
| `design-contract.sh` | 26 tests, 0 failures/errors/skips |
| V11 | 23 OK |
| V09 | 31 OK |
| V10 | 26 OK |
| `document-pipeline-binding.sh` | 33 OK |
| `frontend-design-roundtrip.sh` | pass |
| `design-validator.sh` | all pass |
| `generate-skills-present.sh` | pass |
| `pattern-contract.sh` | all pass |
| `frontmatter-lint-all.sh` | pass |
| `native-command-surface` | PASS, 0 findings |
| `li-copilot.py check` | 22 managed files |
| catalog check | clean |

**Limits:**

- A spec with no `pattern_context` and no supplied lock cannot be detected by the loader. The
  direct-entry rule, `validate_visual` before render and REVIEW coverage remain those obligations.
- Pack and personal pattern bytes are lock-pinned and re-read, not P05-selected (they are outside
  the repository).
- `pipeline_inputs` pattern plumbing is exercised through `load_design` tests, not a dedicated
  pipeline-inputs case.

5.2.a stays unticked until reviewer 24 has reviewed `23e8e194`.

## R12 review follow-up and D1 currentness at use (`99de0741`, RN-15 clarification, RN-16)

Reviewer 24bf5df0 reviewed `b02b10cc` (`r4-fix-b02b10cc.md`, sha256 `432754e4…d182`):

- SPEC was MET, with D-1 left for the owner to decide.
- QUALITY found 1 Medium and 5 Low.

MasterCoordinator `9854860c` released those fixes and chose D-1 option (a), which requires the
compound guarantee. The fix, `99de0741`, is limited to CORE and INT consumer plumbing:

| Finding | Fix |
|---|---|
| M-1 | Committed patterned `pipeline_inputs` API and CLI cases. Both flags are needed, and omission, lock only, context only, mismatched context, repeated flag and edited lock are refused. The pipeline commands in `generate/SKILL.md` and `fidelity-and-evidence.md` now carry the flags |
| L-1 | `pipeline_inputs` refuses pattern flags for a document-only design. The ordinary path is unchanged |
| L-2 | Palette-only admission wording in `design-contract.md` and the loader docstring. RN-15 gains an appended clarification, and its accepted text is unchanged |
| L-3, L-4 | `assertRaisesRegex` with the actual reasons: the verified-selection mismatch, `pattern_context` mismatch, `unusable (invalid)`, `Unsafe relative path`, `pinned_revoked` and `reference_digest_mismatch`. A pack negative plus a pack-drift case in which P05 and P07 still verify but the loader refuses |
| L-5 | The `review` CLI with the flags: accepted, omission gives exit 2, and drift gives exit 2 with no stdout |
| I-2 | `verify_lock` re-runs just before the loader returns |
| D-1 (a) | Consumer contract "Currentness at use". SHIP re-runs `li-pattern review` before the SHIP gate. frontend-design-review and generate-app verify at use. RN-16. The compound-consumer regression is below |

**Compound-consumer regression** (`test_compound_consumer_refuses_old_clearance_after_pack_drift` /
`..._personal_drift`):

- A real selected lock, bound spec and bound passing QA go through the same
  `design_contract.review_result`, which accepts.
- Only the pack or personal source is mutated. The repository lock, context, spec and evidence
  hashes are unchanged.
- P05 `verify_context` and QA still accept, but the same consumer refuses with
  `reference_digest_mismatch`.
- Restoring the external content makes it admissible again.

**Checks** (Windows, synthetic HOME/TEMP):

| Suite | Result |
|---|---|
| `design-contract.sh` | 29 tests, 0 failures/errors/skips |
| `document-pipeline-binding.sh` | 36 OK |
| V11 | 23 OK |
| V09 | 31 OK |
| V10 | 26 OK |
| `frontend-design-roundtrip.sh` | pass |
| `design-validator.sh` | all pass |
| `generate-skills-present.sh` | pass |
| `pattern-contract.sh` | pass |
| `frontmatter-lint-all.sh` | pass |
| `native-command-surface` | 0 findings |
| `li-copilot.py check` | 22 managed files |
| catalog check | clean |

**Limits:**

- Standalone P05 remains repository-only.
- The compound guarantee is enforced in the design loader and its callers, and in `li-pattern
  review`/`verify-lock`. Other consumers carry it as the contract's workflow obligation.
- A spec that omits both `pattern_context` and the lock is still undetectable by the loader.

5.2.a stays unticked until reviewer 24 re-checks the fixed head.

## D1/M1 re-review and source freeze (reviewed head `d4acf3e7`)

Reviewer 24bf5df0 re-checked exact `d4acf3e7` (`d1-m1-d4acf3e7.md`, sha256
`ecae248974c10cb2e9611e529ef0cc8015a49fb47395a199bd94581def70f0f1`; JSON
`9b316e3b0bd003974f5bc708098d6bd22f7be6efff52fc88c58af85b220a1dd5`):

- SPEC MET for A1-A7; QUALITY acceptable, with no Medium or High.
- D-1, M-1, L-1 to L-5 and I-2 are closed.
- L-6 is addressed by the appended RN-16 clarification: mechanical currentness applies only in
  `design_contract` / `pipeline_inputs` / `li-pattern`, and the other consumers carry it as a
  workflow obligation.
- The reviewer independently ran design-contract (29) and four pipeline selectors.

Parent Linux at `d4acf3e7`: design-contract 29/29 and document-pipeline-binding 36/36, exit 0, no
skips (`posix-d4acf3e7-d1-compound.log`, sha256
`f03081549d9a4b1c2f025f88058f3bc31254e971766e34094b2d6b05737a538f`).

**Delta.** The product delta `b484e2d7..99de0741` is 11 files, +322/-24. `d4acf3e7` adds the
ledger only.

**Closure batch.** This batch is metadata only. It changes the plan (4.3.c and 5.2.a ticked with
annotations, 48 leaves kept), reconciliation (RN-16 clarification), this log, the handoff and the
working state. It has zero product, code or test delta against `d4acf3e7`.

**Recorded, non-blocking:**

- I-4: the final recheck is not isolated by a test.
- I-5: the CLI edited-lock case asserts only exit code and empty stdout.
- I-6: document-only stage checks are prose.

**Still open:**

- 6.2.a: Windows strict verdict, and hosted CI before main;
- 6.2.b: the final integrated P05 context, aggregate review, QA and corroboration;
- 6.2.c;
- native 1a and current main;
- `ef48d7a0`;
- publication.

Artifact PDF/Word DONE stays blocked or unverified.

## Pending

- 6.2.a: final fixed-head strict full suite (Windows here; Linux by the parent).
- 6.2.b: final independent aggregate review and actual ADR-0028 v2 context/QA/corroboration.
- 6.2.c: final diff and baseline record.
- 4.3.c and 5.2.a: closed at source/helper level (reviewed at `d4acf3e7`).
- GitHub write access for the feature PR (403, unresolved).
- No release clearance is claimed.

## Milestone integration with main

- P0/P1 commit `2d750892` on base `7ba544a4`. Ordinary merge of `origin/main` `fa8ddce5`
  (#99, #108) as `e128d08a`; one conflict in `.claude/memory/MEMORY.md` resolved by keeping
  main's updated client note and adding this initiative's line.
- On the merged head: `bash tests/unit/patterns.sh` -> 33 OK; command-surface guard PASS
  (0 findings); work-map validator exit 0; `tests/shape/bin-scripts-executable.sh` ALL PASS
  (`bin/li-pattern.py` is 100755); `tests/unit/memory-v2.sh` ALL PASS;
  `bash tests/runner/run-all.sh --scope unit --tag patterns` exit 0 (discovers
  `unit/patterns.sh`). Before the merge, `run-all.sh --scope shape`: 42 total, 0 failed,
  1 partial (pre-existing: `jq` absent on this host skips version-parity assertions).
