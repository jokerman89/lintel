# Reusable patterns: frozen public contract (P1)

Status: FROZEN for dependent lanes at the P1 milestone, 2026-09-28, pending the parent's
independent review. Changes after freezing need a recorded revision here and notice to the
lane owners. Spec sections referenced below remain the requirement; this file records the
exact implemented interface. Module: `lib/patterns.py`. CLI: `bin/li-pattern.py`.

## Roots transport (spec section 3, RN-01)

The launcher (pack lane, `bin/li-pattern`) never interpolates data into shell code. It
obtains the ADR-0029 profile record and builds the envelope with Python JSON:

```bash
record=$(profile_context_json)             # existing adapter in lib/pack-resolver.sh
printf '%s' "$record" | python3 "$src/bin/li-pattern.py" envelope \
  --personal "$LINTEL_HOME" [--repository "$repo"] --profile-record - > "$envelope"
# on profile failure instead: ... envelope --personal "$LINTEL_HOME" \
#   --profile-error CODE --profile-error-message "message"
python3 "$src/bin/li-pattern.py" <command> --roots-stdin [args] < "$envelope"
```

Envelope (validated by `parse_roots`):

```json
{"schema_version": 1, "repository": "<absolute dir or null>", "personal": "<absolute LINTEL_HOME>",
 "pack_context": { "...": "spec section 3 record" }, "diagnostics": [{"code": "...", "message": "..."}]}
```

- `repository`, when not null, is an existing unlinked directory. Personal may not exist yet.
- Derived roots: repository catalog `<repository>/.claude/patterns/catalog.json`, repository
  bindings `<repository>/.claude/patterns/bindings.json`, personal catalog
  `<personal>/patterns/catalog.json`, pack catalog `<declaring ancestry root>/<patterns.source>`.
- `pack_context` is exactly the spec section 3 shape. `pack_context_from_profile` derives it
  from a profile record: status `neutral` when selection mode is neutral, `fallback` when the
  optional preference fell back, `error` via `--profile-error`, else `resolved`; `source` from
  `patterns.source` value and its provenance `path`; `ancestry` from the record's effective chain
  (root = manifest parent, digest without `sha256:`).
- Before reading a pack catalog the core re-hashes each used ancestry `pack.yaml`; a changed or
  missing manifest is `unavailable` (`pack_snapshot_drift`/`pack_snapshot_missing`).
- Locators: `repo` -> `<repository>/.claude/patterns`, `personal` -> `<personal>/patterns`,
  `pack:<name>` -> that ancestry root. Repository and pack catalogs may include their own locator
  or any ancestry `pack:` locator; personal catalogs may include only `personal`.

## Public Python API

All functions raise `PatternError(code, message, status=..., where=...)` for invalid input
(`status="invalid"`) or blocked sources (`"unavailable"`); they never return an empty success
for a failure. Records are frozen dataclasses.

| Function | Signature | Result |
| --- | --- | --- |
| `parse_json` | `(data: bytes, *, limit: int, what: str) -> Any` | Strict JSON (BOM ok; duplicates, NaN, depth > 64, size rejected) |
| `canonical_json` / `content_digest` | `(value) -> bytes` / `(value) -> str` | Sorted, compact, UTF-8; SHA-256 64-hex |
| `emit_json` | `(value) -> str` | Sorted keys, indent 2, LF, trailing newline |
| `validate_relative_path` | `(value, where="path") -> PurePosixPath` | Portable contained path rules |
| `contained_path` | `(root: Path, relative: str, where="path") -> Path` | Refuses links/junctions/escapes |
| `parse_pattern` | `(value, where="pattern") -> Pattern` | Section 4.1; `.digest`, `.raw`, `.clause_ref(id)` |
| `parse_catalog` | `(value, where="catalog") -> Catalog` | Section 4.2 incl. lifecycle/revocation validation |
| `parse_bindings` | `(value, where="bindings") -> tuple[Binding, ...]` | `bindings.json` |
| `parse_context` | `(value, where="context") -> Context` | `.facts`, `.evidence`, `.digest` |
| `parse_refs` | `(value, where="refs") -> tuple[InvocationRef, ...]` | JSON array for `--refs` |
| `parse_overrides` / `parse_exceptions` | `(value) -> tuple[Override, ...]` / `tuple[ExceptionRecord, ...]` | Sections 4.3 / 5 |
| `parse_exact_ref` / `parse_ref_text` | `(value, where)` / `(text) -> (source, id, version)` | Exact reference / `<source>:<id>@<version>` |
| `parse_pack_context` / `parse_roots` | `(value) -> PackContext` / `(value) -> Roots` | Transport records |
| `pack_context_from_profile` | `(record=None, *, error=None) -> dict` | Spec section 3 record from an ADR-0029 record |
| `build_envelope` | `(repository, personal, pack_context, diagnostics=()) -> dict` | Validated envelope |
| `evaluate_selector` | `(selector: Selector, context: Context) -> SelectorDecision` | `matched|rejected|needs-context` + keys |
| `load_sources` | `(roots, reader=None) -> SourceSet` | Catalogs, bindings, blockers, notes |
| `list_catalogs` | `(roots, reader=None) -> dict` | Summaries only; zero body reads |
| `show_pattern` | `(roots, ref_text, reader=None) -> dict` | One body read |
| `check_document` | `(path, kind=None, reader=None) -> dict` | Kinds: `DOCUMENT_KINDS` |
| `check_sources` | `(roots, reader=None) -> dict` | Every registered entry validated |
| `resolve` | `(roots, context, *, refs=(), overrides=(), exceptions=(), preview_draft=False, context_budget=24000, today=None, reader=None, explain=False) -> dict` | Resolution report |
| `exit_code` | `(status) -> int` | See exit codes |

`Reader` counts every file read by kind (`catalog`, `bindings`, `pattern`, `asset`,
`manifest`, `input`); consumers pass one to assert read budgets. `LIMITS` holds the v1
resource constants of spec section 6.

## Resolution report (spec section 4.4)

Keys (`REPORT_KEYS`): `schema_version`, `status`, `context_digest`, `selection_digest` (R2),
`sources`, `selected`,
`candidates`, `requirements`, `settings`, `overrides`, `exceptions`, `diagnostics`, `metrics`;
`resolve` adds `limits` (a fixed limitation statement) and `explain` adds `explanation`
(`bindings` evaluations, `precedence`). Invalid-input reports carry all keys with empty values.

- `status`: worst of error diagnostics by precedence invalid > unavailable > conflict >
  needs-context; otherwise `ready` (selections) or `empty` (none).
- `selected[]`: `ref`, `role` (`required|default`), `scope` (`repo|pack|personal`),
  `effective_status`, `summary`, `reasons[]` (`binding` with approval provenance, `explicit`,
  `include` with parent ref), `preview`, `clauses[]` (fully qualified IDs).
- `requirements[]` (sorted by clause): `clause`, `pattern`, `level`, `role`, `scope`, `state`
  (`mandatory|default|recommendation|suppressed|overridden|waived|conflict`), `text`, `verify`,
  optional `setting`/`value`, `reason`, `exception`.
- `settings{setting}`: `state` (`mandatory|default|overridden|conflict|none`), `value`, `winner`
  (clause ID or `override`), `scope`, `clauses[]`. Consumers such as the visual adapter use
  these final winners; they never recompute precedence.
- `candidates`: `{total, items[<=5]}`; items are advisory metadata only (`advisory: true`).
- `diagnostics[]`: `code`, `severity` (`error|warning|info`), `message`, optional `status` and
  details. `metrics`: read counts, `selected_patterns`, `selected_context_code_points`,
  `advisory_summary_code_points`, `context_budget`, `bindings_evaluated`.

Decisions within the spec's latitude (RN-09): explicit/required pattern whose own selector
rejects -> `conflict` (`applicability_mismatch`); missing facts -> `needs-context`; a default
binding whose pattern does not apply is skipped with a diagnostic, while any integrity or
lifecycle failure of a bound record is `unavailable` (R2/F2); a draft preview reports
`unavailable` (`draft_preview_only`) and is never executable; personal catalogs never supply
advisory candidates or active bindings; setting and override values are any JSON scalar
(string, number, boolean or null, per spec 4.1; null is compared as a distinct value);
until card 3.2.b a required pattern with an external URL source or a past
`review_after` is `unavailable`.

Revision R1 (2026-09-28, parent review note): the P1 milestone `eaffeb6c` wrongly rejected
null setting/override values, narrowing spec 4.1's "JSON scalar". Fixed to accept null;
covered by `AuthorityTests.test_null_is_a_json_scalar_setting_value`.

## Revision R2 (2026-09-28, independent review of `eaffeb6c`: F1-F7 and advisories)

Behavior fixes (the frozen names and signatures are unchanged except the additions noted):

- **F1** Every derived root is checked component by component from its trusted anchor:
  `<repository>/.claude/patterns`, `<repository>/.claude/patterns/bindings.json`,
  `<personal>/patterns`, and an unlinked pack ancestry root. A junction or symlink at `.claude`
  or `.claude/patterns` is `unsafe_path` (exit 2) for reads and writes. A directory where a file
  is expected is also `unsafe_path`.
- **F2** Lookup, digest, stale-metadata, draft, retired and revoked failures of ANY bound,
  included or explicit record are errors with status `unavailable` (exit 5), whatever the role.
  Only selector non-applicability of a default is a non-blocking skip (`default_not_applicable`).
  `verify-lock` applies the same rule to pinned defaults. This supersedes RN-09's former
  `default_skipped` warning.
- **F3** Clause identity is source-independent. The same `(id, version, sha256)` selected
  through several sources is one selection and one set of requirements. It takes the strongest
  role and the highest-precedence selecting scope, keeps every reason, and its
  `selected[].equivalent_refs` lists every exact ref. Differing digests for one `id@version`
  remain `clause_identity_collision` (conflict).
- **F4** A catalog's `scope` and its bindings' activation scope come from its own locator (`repo`,
  `pack:<name>`, `personal`), never from the catalog that included it. Including a pack catalog
  from the repository never promotes that pack's bindings to repository authority. A repository
  binding that uses a pack pattern still selects it at repository scope. Binding IDs must be
  unique per declaring file (`selected[].reasons[].origin` records it).
- **F5** Personal patterns are selected only through an explicit invocation reference or a
  repository binding, including those bindings' includes. A pack binding, or an include
  reached from it, that uses a personal pattern is `personal_ref_refused` (unavailable).

Interface additions (F6, F7). These are frozen for the visual adapter:

| Function / field | Signature or shape | Contract |
| --- | --- | --- |
| report `selection_digest` | 64-hex or `null` | Set for `ready`/`empty` (non-preview) resolutions. It is computed by the same `_lock_material` definition the lock uses, so `build_lock(report, context, refs=same refs)["selection_digest"]` equals it. `build_lock` refuses a report whose digest does not match its content or its refs. `null` for any other status |
| `selected[].assets` | `[{path, kind, sha256[, phases][, domains]}]` | Declared metadata only; no asset read |
| `asset_refs` | `(report_or_lock, *, kind=None, phase=None, domain=None) -> list[dict]` | Stable metadata-only refs `{pattern: <exact ref>, path, kind, sha256[, phases][, domains]}`, the same shape as the lock's `asset_pins`. Absent phase/domain filters on an asset match any task; a present empty filter matches none; zero reads |
| `read_asset` | `(roots, asset_ref, *, phase=None, domain=None, reader=None, selection=None) -> bytes` (`selection` added in R3) | Re-resolves the exact pattern ref: registered, digest-verified body, and effective status approved/deprecated. The asset must be declared with an identical path/kind/digest and pass the filters. It is read contained under the pattern directory with a 4 MiB limit, and the bytes are SHA-256-verified before return. Errors: `asset_not_declared`/`asset_digest_mismatch` (unavailable), `asset_not_applicable`/`unsafe_path` (invalid) |

Lock and projection shapes are those of "Locks, verification and task maps" above; they are now
frozen. Visual consumers read `settings`, `requirements`, `selected`, `selection_digest` and
`asset_refs`/`read_asset`. They never recompute precedence, hashing or validation.

Advisories fixed:

- A missing explicit input file is `input_missing` (exit 2); a missing configured source is still
  `source_missing` (exit 5).
- A malformed profile ancestry is `invalid_pack_context` (exit 2, JSON report, no traceback).
- Timestamp fractions of 1-6 digits are parsed without `datetime.fromisoformat`, so Python 3.10
  and 3.11 agree. Not observed on 3.10: no 3.10 interpreter exists on this host, and installing
  one is outside this authorization.
- Selection is metadata-first: a non-applicable bound or explicit record is decided from its
  validated catalog selector with zero body reads.

Stricter-than-spec choices retained (for reviewer ruling, see build log R1): C0 control
characters, JSON depth 64, dotted namespaces, a 64-character version cap, 128-character
selector keys/values, duplicate-record rejection, and (R2) a linked `LINTEL_HOME` or
repository root refused as a pattern anchor.

## Revision R3 (2026-09-28, independent review of `ae9d6df7`: P2-1, P3-1..P3-4)

No frozen name or signature changed. Digest values change (the opaque interface does not);
there are two additive optional parameters.

- **P2-1** `selection_digest` now covers complete `selected[]` records (`ref`, `role`, `scope`,
  `effective_status`, `summary`, `reasons`, `preview`, `clauses`, `assets`, `equivalent_refs`).
  The same definition is used for reports and locks, so there is one source of truth and no
  second digest policy. Mechanical rules:
  - `asset_pins` must equal `asset_refs(lock)`, which is derived from `selected[].assets`;
    otherwise `invalid_lock`.
  - Every selected record needs its reasons and an `equivalent_refs` list of identical content
    that includes the primary ref.
  - `build_lock` refuses a report whose selected records were edited.
  - Against a forger who also recomputes the digest, `verify_lock` re-derives from the pinned
    bytes and from re-resolution:
    - summary, clause IDs and declared assets must equal the pinned pattern body
      (`lock_content_mismatch`, invalid);
    - every `equivalent_refs` pin is checked like the primary;
    - `ref`, `role`, `scope`, `reasons` and `equivalent_refs` must equal the current resolution
      (`selection_provenance_changed`, conflict, re-plan).
  - Consumers may now treat a verified lock's `selected[].assets` and `asset_pins` as
    integrity-bearing metadata. Bytes still come only from `read_asset`.
- **P3-1** `read_asset(..., selection=<lock | ready/empty report>)`, optional and recommended for
  workflow consumers:
  - the ref must be one of `asset_refs(selection)` (`asset_not_selected`, unavailable);
  - a lock argument is fully parsed first;
  - a report must be ready/empty with a `selection_digest` (`selection_not_usable`).
  - Without `selection`, the call is standalone inspection of a registered approved/deprecated
    pattern, as `show` is, and never implies selection.
- **P3-2** `approve` reads its dependency and lifecycle state inside the owned per-root lock and
  checks that this snapshot equals the in-lock catalog preimage. A revocation committed before
  the lock blocks approval (`dependency_not_approved`). A lock-honouring writer that races it is
  held off (`write_locked`). An optional `expected_catalog_digest` / `--expected-catalog-digest`
  adds caller CAS. Dependencies registered in another source root are checked at the in-lock
  instant; a later revocation there is caught by `resolve`/`verify-lock`, not by this approval.
- **P3-3 remedy** A linked (junction/symlink) `LINTEL_HOME`, repository root, `.claude`,
  `.claude/patterns` or pack root is refused with `unsafe_path`. If your home or checkout lives
  behind a link, pass the real path, i.e. the fully resolved target directory, as the root.
- **P3-4** Scope follows the declaring locator (F4). A repository catalog may explicitly include
  any pack-ancestry catalog (`pack:<name>/<path>` with a pinned digest). That included catalog is
  active, and its own bindings activate at **pack** scope, even when it is not the declared
  `patterns.source`. The pack lane must not assume only `patterns.source` bindings can be active.
  This is an explicit repository decision recorded by the pinned include.

## Revision R4 (2026-09-28, independent review of `f1918e12`: P2-R3-1, P3-R3-1..3)

No names changed. Two optional parameters were added to `read_asset`, and digest values change.

- **P2-R3-1** `verify_lock` compares the whole locked selection with a fresh resolution of the
  locked inputs (context, invocation refs, overrides, exceptions and budget):
  - the selected set, and per record `ref`, `role`, `scope`, `summary`, `reasons`, `preview`,
    `clauses`, `assets` and `equivalent_refs`;
  - `effective_status`, except that approved -> deprecated after locking only warns;
  - canonical requirement records, including `text`, `verify` and `state`, so a must changed to
    waived without its exception fails;
  - settings, overrides and exceptions.

  Only two differences verify with a warning (`default_baseline_changed`,
  `default_setting_changed`): a default-role record that was added later (with its own clauses),
  and a pin that was deprecated later. Everything else is a conflict that forces a re-plan:
  - a record or clause the lock claims but resolution does not produce (`selection_changed`,
    `requirement_changed`);
  - a changed field (`selection_provenance_changed`, `requirement_changed`, `setting_changed`);
  - a clause that is missing from the lock for a record the lock does contain.

  Unchanged sources never bless a discrepancy. A verified lock's `selected[]` set, requirement
  text, state and assets can therefore be relied on, as long as its inputs still resolve the
  same way. Removing a default binding after locking is now a conflict (formerly a warning),
  because a removed record is indistinguishable from a forged one.
- **P3-R3-2**
  - `parse_lock` requires `status == "ready"` exactly when records are selected, else `"empty"`.
  - `context_budget` is part of `selection_digest`, for reports and locks alike.
  - `build_lock(context_budget=...)` must equal the budget the report was resolved with, so a
    changed budget can neither suppress rules nor be edited later.
- **P3-R3-1** `read_asset(..., selection=<report>)` now also requires `context=` (and `refs=` when
  the report was resolved with explicit refs). It recomputes the shared `selection_digest` and
  refuses an edited report (`selection_not_usable`).
  - A report selection is for **in-process use only**: the caller's own freshly resolved report.
  - Anything persisted or passed between processes or lanes must be a lock, checked with
    `verify_lock`.
  - The digest is unkeyed. It detects edits relative to content, and re-resolution detects
    resealed edits; neither authenticates an actor.
- **P3-R3-3** Locks built before R4 (for example by R2 or R3 heads) fail with `invalid_lock`, and
  the message says to regenerate. This is pre-release: re-run `resolve --lock` for any cached lock.
  No lock file is tracked in the repository.

## Locks, verification and task maps (additive, 2.2.b/2.2.c)

| Function | Signature | Result |
| --- | --- | --- |
| `build_lock` | `(report, context, *, refs=(), context_budget=24000, now=None) -> dict` | Ready/empty only; refuses previews |
| `write_lock` | `(roots, path, lock) -> {path, lock_sha256, selection_digest}` | Inside repository; atomic; never overwrites; refuses local absolute roots in content |
| `parse_lock` | `(value) -> dict` | Structure + recomputed `selection_digest` and `mapping_digest` (edits are invalid) |
| `selection_digest` | `(lock) -> str` | Over context, source snapshots, complete `selected[]` records (R3), requirements, settings, overrides, exceptions, invocation refs |
| `verify_lock` | `(roots, lock, context, *, today=None, reader=None) -> dict` | `ok|conflict|unavailable|needs-context`; never rewrites the lock; verifies every `equivalent_refs` pin (R3) |
| `parse_task_map` | `(value, lock) -> dict` | Spec 4.6 validation against the lock |
| `map_lock` | `(roots, lock_path, task_map, *, expected_lock_digest, write=False) -> dict` | Preview or CAS + exclusive-lock install |
| `project_package` | `(lock, task_map, package) -> dict` | Package clauses with `task_ids`, settings subset |

Lock = the report keys plus `limits` and `selection_digest`, `context`, `created_at`,
`source_snapshots`, `asset_pins`, `requirement_tasks` (null until mapped), `source_attestations`,
`review_evidence`, plus two recorded inputs so continuation can re-resolve: `invocation_refs`
and `context_budget`. `lock_sha256` / `--expected-lock-digest` is `content_digest` of the lock
JSON. `selected[]` records now also carry declared `assets` metadata. No asset is read.

`verify-lock` fails `conflict` on a changed context (`context_changed`), a changed mandatory
clause set (`mandatory_baseline_changed`, with `baseline.added/removed`) or locked inputs that
no longer resolve (`replan_required`). It fails `unavailable` on a missing source/entry,
changed bytes, retired/revoked pins or pack snapshot drift. Deprecated pins and changed
defaults are warnings. Unrelated catalog additions pass. `map --write` keeps old
`review_evidence` and reports `invalidated_review_evidence`. Evidence whose `mapping_digest`
differs no longer counts. Write collisions and stale digests exit 6.

## CLI (spec section 7)

Publication decisions within the spec's latitude (3.1):

- `capture --name` must equal the draft's `id`, as an explicit confirmation of what is registered.
- Every capture/index write to an existing catalog requires `--expected-catalog-digest` (spec:
  "Writes require compare-and-swap"). The first capture in a scope requires `--source-id` and
  must omit it. `approve` follows spec 7's row: `--expected-digest` pins the reviewed draft and
  `--expected-catalog-digest` is an optional whole-catalog CAS. Without it, every dependency and
  lifecycle check uses catalogs read inside the owned lock (R3), never a pre-lock snapshot.
- The per-source-root exclusive lock is `<root>/catalog.json.lock`. It is created exclusively
  and removed only by its owner; a held lock exits 6 and is never stolen.
- Content is staged at `<root>/<id>/<version>/pattern.json` (no-overwrite) before the catalog
  is replaced. An unregistered staged file with identical content is completed by the owning
  retry (`recovered_staging: true`). Different content there is a collision.
- `index` accepts only the repository or personal source root, writes only when derived
  metadata changed, and never adds, removes or blesses entries.
- `approve` writes a strictly newer `approved` version that includes the approval record in
  its digest, leaves the draft byte-identical, and requires every include to be approved or
  deprecated. Pack sources are never written; they publish through their own review.

| Command | Arguments | Status in this milestone |
| --- | --- | --- |
| `envelope` | `--personal P [--repository R] (--profile-record FILE|- \| --profile-error CODE [--profile-error-message M])` | Implemented |
| `list` | roots | Implemented (exit 0 even with zero entries) |
| `show` | roots, `--ref <source:id@version>` | Implemented |
| `check` | `--path P [--kind K]` or roots | Implemented |
| `explain`, `resolve` | roots, `--context F [--refs F] [--overrides F] [--exceptions F] [--preview-draft] [--context-budget-chars N]`; `resolve` also `[--lock PATH]` | Implemented. `--lock` writes only ready/empty and never overwrites; `--attestations` arrives with 3.2.b |
| `verify-lock` | roots, `--lock F --context F` | Implemented (2.2.b); `--attestations` with 3.2.b |
| `map` | roots, `--lock F --task-map F --expected-lock-digest SHA [--write]` | Implemented (2.2.c) |
| `project` | `--lock F --task-map F --package ID` (no roots) | Implemented (2.2.c) |
| `review` | spec section 7 | Planned, core owner (4.2.b-core) |
| `capture` | roots, `--input F --scope repo\|personal --name ID [--source-id SRC] [--expected-catalog-digest SHA]` | Implemented (3.1.a) |
| `index` | roots, `--source-root DIR [--expected-catalog-digest SHA]` | Implemented (3.1.b) |
| `approve` | roots, `--path F --version V --approval F --expected-digest SHA [--expected-catalog-digest SHA]` | Implemented (3.1.c; catalog CAS optional per spec 7, R3) |
| `apply`, `update`, `deprecate`, `retire`, `revoke`, `remove`, `export`, `import` | spec section 7 | Planned, core owner (3.2, 3.3) |

Roots are `--roots-stdin` or `--roots-file F` (exactly one). Reports go to stdout as
`emit_json`; each error diagnostic is also printed to stderr as
`[lintel/pattern] <code>: <message>`. Exit codes: 0 ok/ready/empty, 2 invalid, 3 needs-context,
4 conflict, 5 unavailable, 6 write collision, 7 unmet review requirement.

## Lane obligations

- Pack lane: `lib/paths.sh` (`lintel_patterns_dir`, `lintel_pattern_runtime_dir`), the
  `bin/li-pattern` launcher using the transport above, optional `patterns.source: null` in the
  neutral manifest and schema reference, pack/roots tests. It must not add a manifest parser.
- Workflow lane: canonical phase/consumer skills, the consumer reference and
  `lib/pattern_visual.py` consuming `resolve` reports (`settings`, `requirements`,
  `selected`) through this module; no copied validator.
