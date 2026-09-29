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

  In R4, two differences verified with a warning (`default_baseline_changed`,
  `default_setting_changed`): a default-role record added later (with its own clauses), and a pin
  deprecated later. R5 removes the added-default warning: see "Revision R5". Everything else is a conflict that forces a re-plan:
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

## Revision R5 (2026-09-28, independent review of `d82b2919`: P2-R4-1, P3-R4-1, P3-R4-2)

This revision chooses the parent's simple strict alternative: no new snapshot or authentication
subsystem. It adds no names and changes no shapes; digest values are unchanged.

- **R4's "unchanged sources never bless a discrepancy" was false for omitted default records.** R5
  closes the gap: any difference between the lock and a fresh resolution of its own inputs is a
  conflict that forces a re-plan. This covers:
  - a selected record present only in the lock or only in the resolution, whatever its role;
  - a clause present on one side only;
  - a changed record, requirement or setting;
  - changed overrides or exceptions.

  The R4 warning bypass for added defaults (`default_baseline_changed`, `default_setting_changed`)
  is removed. A genuine later addition or removal of a default binding is therefore a re-plan, not a
  warning. This is the bounded stricter behavior allowed by spec 4.4's "no silent change". A catalog
  addition that nothing binds does not change the resolution and still passes.
- **Internal consistency is checked in `parse_lock`.**
  - The lock's requirement states and settings must be exactly what `_settle`, the same function
    resolution uses, derives from the lock's own clauses, overrides and exceptions. Exception
    expiry is evaluated at the lock's `created_at`. Legitimate override winners and waivers pass.
  - The `requirements` must list exactly the clauses of the selected records.
  - A setting whose winner or value is not produced by the lock's own clauses is `invalid_lock`.
    This holds even when another default was omitted, so a setting mismatch can never become
    success.
- **`effective_status` is historical.** In the lock it is the status at locking time;
  `verify_lock`'s `checked[].effective_status` is the current status.
  - approved (lock) -> deprecated (now) is a `pinned_deprecated` warning only when that pin's
    catalog changed since locking. Otherwise the deprecation already existed, the lock's claim is
    wrong, and the result is a `selection_provenance_changed` conflict.
  - Catalog identity is compared per source through `source_snapshots`. No catalog-wide identity is
    required.
- **`read_asset` precondition.** The docstring states that a persisted or cross-process lock MUST
  first pass `verify_lock` with status `ok`. Parsing proves internal consistency, not agreement with
  current sources. Reports remain in-process only.
- **Digests are unkeyed and authenticate no one.** They detect edits relative to content, and
  re-resolution detects resealed edits relative to current inputs.

## Revision R13 (2026-09-28, POSIX full-suite finding and INT review Low fixes)

No signature, exit code or report shape changes.

- **Planned names are classified before any read, on every platform** (`8fb265cf`). For a
  version's declared files, `_declared_files` rejects the reserved body name (`pattern.json`,
  casefolded) and runs the shared `_check_namespace` preflight over the planned names before it
  opens a file. Case-only and file-versus-directory collisions therefore report
  `destination_conflict` on case-sensitive POSIX filesystems too. Before, they could surface as a
  missing or unreadable file. `_is_link` treats ENOTDIR (a parent component is a file) like
  ENOENT: not a link. The caller then sees a missing path or a destination conflict. There is no
  new abstraction and no broad exception catch.
  - Disclosure (review P3): explicit `check`/`check_sources` now rejects a previously published
    or pack entry with a nonportable declared namespace (for example `guide.md` plus `Guide.md`)
    as `destination_conflict`. Ordinary metadata resolution is unchanged. The owner publishes a
    corrected version or layout; `check` and reindexing never accept the old entry.
- **No report means unavailable.** Consumers treat a run that writes no JSON report on stdout as
  `pattern check unavailable`, whatever the exit code. This is stated in the skill and the
  consumer contract. Exit 5 from the launcher's missing-runtime branch (R12) is one such case.
- **Byte preservation is a source-authoring step, not a runtime check.** Capture step 6 in the
  skill, the template README and the concepts page tell authors to add a source-scoped
  `.gitattributes` with `* -text` before Git tracks a pattern source. They must never overwrite
  existing attributes. `-text` does not disable filters, LFS, `working-tree-encoding` or `ident`,
  and `.git/info/attributes` can still override it. The kit generator normalizes text to LF, so
  the shipped example is LF-only, and tests enforce that.

## Revision R12 (2026-09-28, INT packaging: missing runtime and kit closure)

- **Missing runtime.** When Python 3.10+ is missing, the launcher now exits **5**. Before, it
  exited 2. It prints one stderr line starting `pattern check unavailable:` and writes no stdout
  report. This follows the parent's L-N1 decision, which the consumer contract's "Missing runtime"
  section states. The change applies only to that one branch of `bin/li-pattern`; the change is
  owned by CORE/INT after the join.
- **Kit closure.** `bin/li-copilot.py` exposes the `pattern` workflow (native wrapper
  `.github/skills/li-pattern/`). It also verifies `PATTERN_RESOURCES`: the skill, the consumer
  contract, the launcher and CLI, the core, visual and profile modules, the pack files and the
  authoring template with its canonical example. It ships `docs/concepts/patterns.md`. The bare
  native installer already copies these components and gains no Python prerequisite.
- **Known limitation.** On Windows without long-path support, `lib/patterns.py` opens files with
  ordinary spellings. It does not use `native_io_path` the way `profile_context.py` does, so a
  pattern file whose full path exceeds 260 characters reports as missing: fail-closed, never
  success. Keep pattern sources at ordinary path depths, or enable long paths. Hardening this is
  outside this release.

## Revision R11 (2026-09-28, independent review of R10: P3-R10-1, P3-R10-2)

The signature of `validate_selection_report` is unchanged. It now also refuses, with
`selection_not_usable`:
- A report whose `status` disagrees with its selection: `ready` exactly when records are selected,
  otherwise `empty`. This is the same rule `parse_lock` applies. `status` is outside the digest.
- A `selected` field that is not an array of records. This is checked before any field of those
  records is read.
- `refs` that is not a list or tuple, so generators and other one-shot iterables are refused, not
  silently consumed. Lists and tuples of parsed `InvocationRef`s or raw items still work, and mixed
  or invalid raw items keep the existing parser's `invalid_schema`.
- Content that cannot be serialized for the digest, such as NaN or a cyclic value. The
  `ValueError` is converted at that same narrow boundary; there is no blanket catch.

## Revision R10 (2026-09-28, WF review M2: shared fresh-report validation)

The check `read_asset` already applied to a report selection is now one public helper that
`read_asset` and the visual adapter both call:

`validate_selection_report(report, *, context, refs=()) -> report`

It raises `PatternError` `selection_not_usable` (invalid) in any of these cases:
- the input is a lock or not a report;
- the status is not `ready` or `empty`;
- there is no `selection_digest`;
- report fields are missing;
- a record is a draft preview;
- the context is missing, or differs from the report's `context_digest`;
- the `selection_digest` does not equal the digest recomputed from the report's own content,
  `context` and `refs`, using the same `_lock_material` definition as the lock.

`refs` may be parsed `InvocationRef`s or raw `--refs` items, which are parsed with the same parser.
The helper reads no file and returns the same report.

Scope of the guarantee: it detects edits relative to the report's own content; it does not
authenticate the producer. Fresh reports are in-process only. Anything persisted, or passed
between entries, processes or lanes, must be a lock that passed `verify_lock`. The context and
preview checks duplicate what the digest already covers, and give clearer messages.

## Revision R9 (2026-09-28, independent review of `445e3ad9`: P3-R8-1, P3-R8-2)

The shared namespace check compares every planned file key and every proper directory prefix of
each key, whatever the order or the siblings. R8 compared sorted neighbors only, so `a`, `a.md`,
`a/b` slipped through. The check refuses:
- a file that is also a directory of another file, at any depth;
- one directory spelled two ways (`Docs/x` and `docs/y`, including an asset and a source);
- files that differ only by Unicode casefold.

This is a portable-safety restriction for case-insensitive filesystems, not a model of every
filesystem's normalization rules (NFC/NFD folding is not attempted). No name or shape changed.

## Revision R8 (2026-09-28, independent review of `8addc395`: P3-R6-1, P3-R6-2, note 1, note 2)

- **One destination namespace per publication.** The shared `_preflight` validates the complete
  destination list before the first write, using the existing path validator, for capture,
  update, approve and import alike. It refuses (`destination_conflict`, invalid) any of these:
  - paths equal only by case;
  - a path that is both a file and a directory prefix of another (`a` and `a/b`);
  - the same path claimed with different bytes.

  An exact duplicate with identical bytes coalesces, for example an asset and a `root: pattern`
  source that name the same file. On disk, a destination whose ancestor is a file, or which is
  itself a directory, is a collision. Each version's closure is also checked on its own, at
  preview time, and a closure file may never take the version body name `pattern.json` at the
  version root (a nested `docs/pattern.json` is fine). A refusal writes nothing, so a retry is
  clean. A reader that meets a file where a directory is expected reports a missing file, never
  an uncaught `NotADirectoryError`.
- **Compatibility notice.** `check`/`check_sources` now verify every registered version's
  declared file closure. An entry approved before R6 without its files, or a pack that declares a
  `root: pattern` source it does not ship, now reports `unavailable` (`declared_file_missing`) in
  `check`. Remedy: in a repository, run `update --files-from <dir>`, then `approve`; a pack must
  ship the declared file. `list` and ordinary resolution stay metadata-first and are unaffected.

## Revision R7 (2026-09-28, independent PACK-lane review: coupled F1, F2, F3, F6)

- **F2** `build_envelope` checks each anchor (repository, personal) for a link or junction on the
  caller's spelling, before resolving it (`invalid_roots`, exit 2). `parse_roots` also refuses a
  linked personal root. The direct `envelope` command, the launcher's route and `--roots-file` now
  agree. The check covers only the anchor's final component. Linked ancestors (for example a
  junctioned profile directory above the repository) resolve normally, and a physical path produced
  upstream, such as Git's resolved top level, carries no alias to detect and is accepted as the real
  path. The remedy is unchanged: pass the real path. Consumers, including no-pattern WF and INT
  paths, must surface `invalid_roots` for a junctioned repository or `LINTEL_HOME` with the
  real-path remedy, and never treat it as a neutral success.
- **F1** No code change. After the PACK join, the neutral `_default` declares
  `patterns.source: null`, and a child whose `patterns` block lacks `source` gets
  `{"state": "null", "origin": "<neutral>/pack.yaml"}` (ADR-0029 defaults filling). With a legacy
  neutral manifest the same child is `absent`. Both are tested with explicit fixture baselines.
- **F3** The upgrade notice lives in ADR-0038 and the evolution entry. Every bound profile context
  must be rebound explicitly, with a reason, after the neutral manifest changes. INT's public docs
  repeat it (card 6.1.a).
- **F6** Outside Git, the launcher gives the ADR-0029 profile provider `LINTEL_HOME` as its working
  root. That provider therefore honors `$LINTEL_HOME/.claude/profile-requirements.json` and uses
  `$LINTEL_HOME/.claude/runtime/profiles/selected.json` as its selection record. This is existing
  provider behavior and is retained. It is not a repository pattern root: the envelope's
  `repository` stays `null`, and no repository catalog or bindings are read. INT's public docs
  describe it.

## Revision R6 (2026-09-28, independent review of `c92ae4dc`: P1-C92-1, P3-C92-1..9; R5 review P3-R5-1)

These changes add two optional parameters and one optional CLI flag; no name or shape changed.

- **P1-C92-1 Declared file closure.** Every new version carries its exact local file closure:
  - declared `assets[]`, whose sha256 is verified;
  - `root: "pattern"` sources, verified against any pinned sha256.

  Nothing else is copied (no unrelated files, no repository or external sources). Files are read
  contained with the asset limit and staged through the existing no-overwrite staging before the
  catalog-last replace.
  - `approve` copies the closure from the draft's own version directory.
  - `update(..., files_from=None)` reads new or changed files from `files_from` and unchanged ones
    from the previous version.
  - `capture(..., files_from=None)` reads from `files_from`.
  - The CLI `capture` and `update` default `--files-from` to the input file's directory.
  - A missing or changed file fails with `declared_file_missing` or `declared_file_changed`
    (unavailable) before any write, leaving the tree and catalog unchanged.
  - `check`/`check_sources` verify each registered entry's closure. `list` and ordinary
    resolution stay metadata-only.
  - Export still carries assets only, never source documents. An imported pattern with a
    `root: pattern` source therefore needs that file supplied (`update --files-from`) before
    approval.
- **P3-C92-8** `_publish` preflights every pattern and file destination before the first write.
  A collision leaves no orphan.
- **P3-C92-1** Lifecycle previews apply the same event rules as the write: transitions,
  monotonic time and no un-revoke. Previews of `deprecate`, `retire`, `revoke` and `remove` return
  `catalog_sha256` for the `--write` CAS.
- **P3-C92-2** A default-role URL source warns (`source_unverified_default`).
- **P3-C92-3 / -4** The attestation entry points validate raw input with the same parser and
  raise `PatternError`, never `KeyError`. This covers `resolve`, `explain`, `verify_lock`,
  `review_coverage`, `record_attestations` and `merge_attestations`. Duplicate identities are
  rejected. `parse_lock` validates saved `source_attestations`.
- **P3-C92-5** `apply` add/replace refuses a binding whose ref is unregistered, draft, retired,
  revoked or unreadable (`binding_ref_unavailable`). An existing binding with unreachable refs is
  reported (`binding_had_unavailable_refs`).
- **P3-C92-6** The first `apply` creates a missing `.claude/patterns` with contained, link-checked
  mkdir.
- **P3-C92-7** Bindings CAS diagnostics name `bindings` and `--expected-digest`
  (`stale_bindings_digest`). Catalog CAS codes are unchanged.
- **P3-C92-9** The import-derived effective status comes from the bundle's lifecycle events:
  revocation, else the latest lifecycle status, else the publication status. A declared
  `effective_status` that contradicts its events is `invalid_bundle`.
- **P3-R5-1** `build_lock` validates its own output with `parse_lock` at `created_at` and refuses
  (`lock_refused`) a lock that would be invalid, for example because an exception expired between
  resolution and locking. Resume-time expiry still blocks (`replan_required`). Tests build locks
  at a fixed instant.

## Maintenance, attestations, sharing and review (additive, 3.2-3.3, 4.2.b.core)

| Function | Signature | Result |
| --- | --- | --- |
| `dependents` | `(roots, targets, *, reader=None, sources=None) -> dict` | Includes, bindings and `*.lock.json` pins under `<repository>/.claude/plans` only; reports `inventory_scope` and unreadable items |
| `update` | `(roots, path, input, *, expected_digest, write=False, expected_catalog_digest=None) -> dict` | Strictly newer draft of the same id; clause diff and impact; the old version stays intact |
| `record_lifecycle` | `(roots, ref_text, *, action, record_value, expected_catalog_digest, write=False) -> dict` | `deprecate`/`retire`/`revoke`; monotonic timestamps; no un-revoke; pack sources are read-only |
| `apply_change` | `(roots, change, *, expected_digest=None, write=False) -> dict` | Repository `bindings.json` add/replace/remove; old/new/reduced required clause sets; CAS and exclusive lock |
| `remove` | `(roots, ref_text, *, expected_catalog_digest, write=False) -> dict` | Unregisters one entry that has no references and no lifecycle history; never deletes files |
| `parse_attestations` / `merge_attestations` | `(value)` / `(saved, supplied)` | Spec 4.5 records; renewal replaces the same pattern/source |
| `record_attestations` | `(roots, lock_path, attestations, context, *, expected_lock_digest, today=None) -> dict` | Verifies, then installs attestations under CAS; `selection_digest` unchanged |
| `export_bundle` | `(roots, refs, out) -> dict` | New directory with the exact closure and declared assets; no catalogs, bindings, source documents or absolute roots; refuses retired/revoked |
| `import_bundle` | `(roots, bundle, *, scope, destination_source, version_map_value, write=False, expected_catalog_digest=None) -> dict` | Whole-bundle preflight; children-first drafts with re-hashed includes; `extensions["lintel.imported"]` provenance |
| `review_coverage` | `(roots, lock, context, evidence, *, attestations=(), today=None) -> dict` | `verify_lock` first, then per-clause verdicts; `review-unmet` (exit 7); `release_clearance: false` |

`resolve`, `explain` and `verify_lock` accept `attestations=` / `--attestations`. A required
pattern with an external URL source needs a `source-verification`/`both` attestation. An overdue
required pattern (`review_after` in the past) needs a `freshness`/`both` attestation for every
source, reviewed on or after `review_after`. A rejected attestation is reported
(`attestation_rejected`) and does not count. Applied attestations appear in the report's
`source_attestations`, not in `REPORT_KEYS`, and `build_lock` stores them in the lock, outside
`selection_digest`.

Maintenance commands preview by default; `--write` performs the change with the stated CAS.
`remove` refuses (`remove_refused`, conflict) when anything in the inventory references the entry,
when it has history, or when the inventory is incomplete.

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
| `explain`, `resolve` | roots, `--context F [--refs F] [--overrides F] [--exceptions F] [--preview-draft] [--context-budget-chars N]`; `resolve` also `[--lock PATH]` | Implemented. `--lock` writes only ready/empty and never overwrites; `--attestations F` (3.2.b) |
| `verify-lock` | roots, `--lock F --context F [--attestations F] [--write --expected-lock-digest SHA]` | Implemented (2.2.b, 3.2.b); `--write` installs validated attestations under CAS |
| `map` | roots, `--lock F --task-map F --expected-lock-digest SHA [--write]` | Implemented (2.2.c) |
| `project` | `--lock F --task-map F --package ID` (no roots) | Implemented (2.2.c) |
| `review` | roots, `--lock F --context F --evidence F [--attestations F]` | Implemented (4.2.b.core); verifies the lock first, exit 7 on unmet mandatory coverage, `release_clearance: false` |
| `capture` | roots, `--input F --scope repo\|personal --name ID [--source-id SRC] [--expected-catalog-digest SHA] [--files-from DIR]` | Implemented (3.1.a) |
| `index` | roots, `--source-root DIR [--expected-catalog-digest SHA]` | Implemented (3.1.b) |
| `approve` | roots, `--path F --version V --approval F --expected-digest SHA [--expected-catalog-digest SHA]` | Implemented (3.1.c; catalog CAS optional per spec 7, R3) |
| `update` | roots, `--path F --input F --expected-digest SHA [--expected-catalog-digest SHA] [--files-from DIR] [--write]` | Implemented (3.2.a); preview by default |
| `deprecate`, `retire`, `revoke` | roots, `--ref <source:id@version> --record F [--expected-catalog-digest SHA] [--write]` | Implemented (3.2.a); preview by default, CAS required to write |
| `apply` | roots, `--change F [--expected-digest SHA] [--write]` | Implemented (3.2.b); preview by default |
| `remove` | roots, `--ref <source:id@version> [--expected-catalog-digest SHA] [--write]` | Implemented (3.2.c); unregisters only, keeps files |
| `export` | roots, `--refs F --out DIR` | Implemented (3.3.a); new local directory only |
| `import` | roots, `--bundle DIR --scope repo\|personal --destination-source SRC --version-map F [--expected-catalog-digest SHA] [--write]` | Implemented (3.3.b); preview by default, stages drafts |

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
