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
