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

Keys (`REPORT_KEYS`): `schema_version`, `status`, `context_digest`, `sources`, `selected`,
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
binding whose pattern does not apply is skipped with a diagnostic; a draft preview reports
`unavailable` (`draft_preview_only`) and is never executable; personal catalogs never supply
advisory candidates or active bindings; setting values are JSON strings, numbers or booleans
(not null); until card 3.2.b a required pattern with an external URL source or a past
`review_after` is `unavailable`.

## CLI (spec section 7)

| Command | Arguments | Status in this milestone |
| --- | --- | --- |
| `envelope` | `--personal P [--repository R] (--profile-record FILE|- \| --profile-error CODE [--profile-error-message M])` | Implemented |
| `list` | roots | Implemented (exit 0 even with zero entries) |
| `show` | roots, `--ref <source:id@version>` | Implemented |
| `check` | `--path P [--kind K]` or roots | Implemented |
| `explain`, `resolve` | roots, `--context F [--refs F] [--overrides F] [--exceptions F] [--preview-draft] [--context-budget-chars N]` | Implemented; `--lock`, `--attestations` arrive with 2.2.b/3.2.b |
| `verify-lock`, `map`, `project`, `review` | spec section 7 | Planned, core owner (2.2.b, 2.2.c, 4.2.b evidence) |
| `capture`, `approve`, `index`, `apply`, `update`, `deprecate`, `retire`, `revoke`, `remove`, `export`, `import` | spec section 7 | Planned, core owner (P3) |

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
