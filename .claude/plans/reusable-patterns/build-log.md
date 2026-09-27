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

## Pending

All other leaves. Host/model acceptance (V17) not attempted. Full required suite (V16) not run
at this milestone.
