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

## Pending

All other leaves. Host/model acceptance (V17) not attempted. Full required suite (V16) not run
at this milestone.

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
