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
  `skills/pattern/references` in the package boundary. It is pending join (RN-11). The
  `catalog-regenerates-clean` shape test reports drift for the new `pattern` skill; this is
  pending INT 6.1.b. `frontmatter-lint-all` and `skill-descriptions-trigger` pass.

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
