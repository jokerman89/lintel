# Spec: reusable patterns

Date: 2026-09-24. Status: APPROVED for BUILD on 2026-09-28 under the recorded operator
authority; see [implementation-release.md](implementation-release.md) and the revision notes
in [reconciliation.md](reconciliation.md) (RN-01..RN-10), which take precedence where marked.
Companions: [plan](plan.md), [handoff](prompt.md), [review](review.md), [contract](contract.md).
Planning baseline: Lintel `00136c9d`. Implementation base: `7ba544a4` (recorded in reconciliation.md).
Authority: the user requested a universal reusable system, asked to make it ready for
implementation, and then authorized BUILD, a feature PR and a normal merge after CI and
review. No change to organizational policy, personal installations or other sessions is approved.

## 1. Architectural decision

Introduce a data-only pattern runtime, shared by workflow skills and frontend
adapters. A pattern records expectations, applicability, evidence and optional
assets. A blueprint is a pattern with explicit dependencies, not another schema.
Context bindings select defaults and requirements for named targets. A target can
be a document, audience, application or deployment environment.

Implement the generic runtime in `lib/patterns.py` using Python standard library,
with `bin/li-pattern.py` as the CLI and `bin/li-pattern` as the Bash launcher.
`lib/patterns.py` owns parsing, typed records, validation and result serialization.
Do not duplicate validators in skills or make prose-only assertions into runtime
guarantees. Use the minimum Python version already required by the portable kit.

The launcher uses `lib/paths.sh` and `lib/pack-resolver.sh` to obtain roots and
pack identity. (RN-01: reuse the ADR-0029 profile record and its provenance instead of
adding an accessor; no second YAML parser or cache.)
No service, embeddings, background crawler, automatic network fetch, MCP server,
new scheduler or hook registration.

Alternatives rejected: loading all knowledge into instructions loses relevance and
evidence; a hosted retrieval service adds a new operational system before the local
contract is proven. The local design preserves the spine/pack split.

### Accepted architecture reconciliation

- ADR-0005: repository output remains under `.claude`; personal configuration uses
  `LINTEL_HOME`. This planning package is in session artifacts by explicit request.
- ADR-0008: behavior tests, not prose-presence checks, establish runtime activation.
  Host/model acceptance is a separate evidence category.
- ADR-0015/0016: keep Design DNA and `brief > profile > corpus` for unconstrained
  choices. Binding an approved mandatory pattern adds a visible constraint; it
  does not turn every design profile into policy or remove the normal defaults.
- ADR-0018 and current pack docs: one-parent inheritance; top-level blocks replace
  wholesale; existing pack error/fallback behavior stays intact. New callers must
  distinguish fallback from successful resolution.
- ADR-0024: canonical source plus generated Copilot adapters; source and working
  target are different roots. No claim of translated Claude hooks.
- ADR-0026: short leaves, coherent package implementation/review, per-leaf evidence.
- L-001/002/004/025: one canonical example, reuse existing extraction, preserve
  design/rendering separation, edit generators before their outputs.

An implementation ADR must record this additive decision and the bounded
precedence change. Allocate its numeric ID at implementation time to avoid
colliding with concurrent work. Do not edit accepted ADRs or governance.

## 2. Requirements and traceability

| ID | Requirement | Source intent | Cards |
| --- | --- | --- | --- |
| R01 | Domain-neutral patterns, targets and blueprints | Universal reuse | 1.1.a, 1.1.b, 1.2.a, 2.2.a |
| R02 | Explicit repository, active-pack and personal scopes | Share across levels | 2.1.a, 2.1.b, 2.1.c, 2.1.d |
| R03 | Preserve pack semantics and declaring-origin paths | Fit existing Lintel | 2.1.b, 2.1.c, 2.2.b |
| R04 | Metadata-first relevance and unknown-context decisions | Context efficiency | 1.2.a, 1.2.b, 1.2.c |
| R05 | No required rule lost to ranking, overrides or budgets | Proactive expectations | 1.3.a, 1.3.b, 1.3.c, 2.2.c |
| R06 | Evidence-backed capture; approval separate from inference | Discover expectations | 3.1.a, 3.1.b, 3.1.c |
| R07 | Explain conflicts, authority and exceptions | Avoid policy surprises | 1.3.b, 1.3.c, 3.2.b |
| R08 | Immutable pins, lifecycle, drift and dependency impact | Maintain/update/remove | 2.2.a, 2.2.b, 3.2.a, 3.2.b, 3.2.c |
| R09 | No implicit execution/network or unsafe paths | Trust boundary | 1.1.c, 1.1.d, 3.3.a, 3.3.b |
| R10 | Cycle and direct skills consume the same resolution | Workflow integration | 4.1.a, 4.1.b, 4.1.c, 4.2.a, 4.2.b, 4.3.a, 4.3.b, 4.3.c, 4.3.d |
| R11 | Cold handoff and complete review traceability | Durable knowledge | 2.2.c, 4.2.a, 4.2.b, 4.2.c |
| R12 | Reuse existing visual extraction and named inputs | Website reuse | 5.1.a, 5.1.b, 5.1.c, 5.2.a, 5.2.b |
| R13 | Measured retrieval limits; no irrelevant asset loads | Lightweight system | 1.2.b, 1.2.c, 2.2.c, 6.2.a |
| R14 | Neutral example, portable kit, reproducible checks | Team adoption | 6.1.a, 6.1.b, 6.1.c, 6.2.a, 6.2.b |
| R15 | No-pattern compatibility, transparent failure | Safe later integration | 2.1.d, 4.1.c, 5.2.b, 6.2.a, 6.2.b |
| R16 | Isolation, reviewed architecture and merge handoff | Do not disturb work | 0.1.a, 0.1.b, 6.2.c |

## 3. Files and roots

Runtime code uses `Path` objects and native paths at its OS boundary. Serialized
relative paths use canonical slash-separated portable paths, as existing work maps
do; reject backslashes, drive/UNC prefixes, empty segments, dot segments and colons.
The slash spelling here is a data format, not a Windows shell command.

| Root | Entry | Selection |
| --- | --- | --- |
| Repository | `.claude/patterns/catalog.json` | Always inspect if present |
| Repository bindings | `.claude/patterns/bindings.json` | Always inspect if present |
| Active pack | `patterns.source` in effective pack manifest | Null/absent means none |
| Personal | `$LINTEL_HOME/patterns/catalog.json` | Available, not automatically active |
| Scratch | `.claude/runtime/patterns/<run-id>/` | Explicit run ID, never latest-mtime selection |
| Durable | `<selected-initiative>/patterns.lock.json` | Beside existing work artifacts |

No repository is required for personal capture/list/show. A non-Git environment
must supply an explicit writable `--repo` working root before using repository
bindings or locks; never fall back to filesystem root or the installed source.

Add `lintel_patterns_dir` and `lintel_pattern_runtime_dir` to `lib/paths.sh`.
The launcher sends resolved roots to Python as JSON on stdin (`--roots-stdin`),
constructed with Python JSON serialization, not shell string interpolation.
The roots envelope has `schema_version:1`, `repository` (absolute path or null),
`personal` (absolute path), `pack_context` (the exact record below) and `diagnostics`
(array of diagnostic code/message records). Python derives repository and personal
catalog paths from those roots, not arbitrary environment variables in content.
No content from a pattern is passed as shell source, an executable or an eval.

### Pack origin accessor (revised by RN-01)

RN-01 replaces the new shell accessor below with the existing ADR-0029 provenance
(`profile_field_provenance`, `profile_context_json`) and the core converter
`pack_context_from_profile`; the semantics and the JSON shape remain the requirement.
Original text: add `resolve_pack_field_origin <dotted.path>` to `lib/pack-resolver.sh`.
Return the absolute declaring manifest path on stdout; 0 = found, 1 = absent,
2 = invalid/unavailable. Explicit null has an origin. Find the top-level block
winner under the current effective cached ancestry, then test the complete field.
If absent, use the neutral fallback's origin only when the accessor would use its
value; explicit null/false/empty values do not fall through.

Value and origin must come from the same pack-resolution snapshot. Add a public
JSON context function for the launcher, `pack_pattern_context`, returning this shape:

```json
{
  "schema_version": 1,
  "status": "resolved",
  "identity": {"name": "team", "version": "1.0.0"},
  "source": {"state": "value", "value": "patterns/catalog.json", "origin": "C:/packs/base/pack.yaml"},
  "ancestry": [
    {"pack": "base", "version": "1.0.0", "root": "C:/packs/base", "manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
    {"pack": "team", "version": "1.0.0", "root": "C:/packs/team", "manifest_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}
  ],
  "diagnostics": []
}
```

Absolute example paths are transport-only, never copied into a durable lock.
`status` is `resolved|neutral|fallback|error`; `identity` is null only for error.
`source.state` is `value|null|absent|unavailable`, with `value`/`origin` strings or
null. Absent has both null; explicit null retains origin; unavailable has any known
origin and diagnostics. A valid neutral pack without patterns is status neutral,
not fallback. Fallback means selected pack could not be used. `ancestry` is ordered
root-to-leaf for the EFFECTIVE cached identity, not the newly selected pointer.
Roots and manifest digests must match that same snapshot; otherwise unavailable.

Python registers allowed catalog source locators as `pack:<pack-name>` for each
ancestry item and `repo`/`personal` for their explicit roots. A catalog's content
`source_id` is a namespaced stable ID recorded alongside its locator; resolve exact
references by that content ID. If two registered catalogs declare the same content
ID with different digests, fail. Includes use locator plus contained path before
the included catalog's source_id is known; exact pattern refs use content source_id.
Only the effective patterns.source catalog and its explicit includes are active;
ancestry registration alone never loads a parent's catalog or activates bindings.

Refactor a common internal
snapshot only if necessary; preserve existing public accessor outputs/statuses.
If the cached directory/origin has disappeared, a required pattern source is
unavailable, not successfully resolved from another pack. Invalid company fallback
blocks pattern-dependent resolution; an entirely unconfigured neutral pack is not
an error. Ordinary existing non-pattern callers retain existing fallback behavior.

Optional `patterns.source` is a catalog file relative to its declaring pack root.
Follow whole-block replacement. Parent catalog composition uses explicit includes;
never merge catalogs merely because manifests are ancestors.

## 4. Canonical data contracts

All JSON objects reject duplicate keys, NaN/Infinity, bool-as-int versions and
unknown top-level keys. An `extensions` mapping is the only extension seam; its
keys must be namespaced and its data never supplies authority or execution.
UTF-8 BOM may be accepted, emitted JSON is UTF-8 without BOM, sorted keys and LF.
Emit explicit machine-readable errors, not empty-success results.

`lib/patterns.py` is the single executable validator. Documentation tables below
specify its contract; consumers import it. Do not introduce a general JSON Schema
interpreter or an unvalidated second schema copy. Tests exercise the validator
through both API and CLI.

### 4.1 Pattern (`pattern.json`)

Required fields:

| Field | Type and semantics |
| --- | --- |
| `schema_version` | Integer 1 |
| `id` | Lowercase dotted namespace plus kebab leaf, max 128 ASCII chars; e.g. `example.internal-dashboard` |
| `version` | Three nonnegative integers `major.minor.patch`; no ranges/prereleases in v1 |
| `status` | `draft|approved|deprecated|retired` |
| `summary` | Nonempty string, at most 240 Unicode code points |
| `owner` | Nonempty organizational/person role label, not a secret |
| `applies_to` | Selector defined below |
| `includes` | Array of exact references defined below |
| `sources` | Array of source records; at least one for approval |
| `requirements` | Array of clauses; may be empty for a blueprint |
| `guidance` | String; at most 4,000 code points; may be empty |
| `assets` | Array of declared local file references; may be empty |

Optional fields: `review_after` (ISO date), `approval` (record below),
`replaced_by` (exact reference), `extensions` (mapping).
An approved/deprecated pattern requires `approval`, and at least one requirement
or include. Approval records `by`, `reference`, `at` (UTC RFC3339). This is declared
provenance, not proof that the named approver has permission.

Clause: `id` (unique uppercase letters/digits/hyphens within pattern), `level`
(`must|default|recommendation`), `text` (nonempty, <=2,000 code points), `verify`
(nonempty, <=2,000), optional `setting` (namespaced stable string), optional `value`
(JSON scalar only). `setting` and `value` appear together. Structured settings allow
mechanical conflict detection; natural-language clauses still require review.
Fully qualified clause identity is `<pattern-id>@<version>#<clause-id>`.

Source: `kind` (`operator-statement|approved-standard|observation`), `ref` (path,
URL or statement text), `root` (`pattern|repository|external|statement`),
`section` (string), `observed_at` (UTC timestamp), `confidence`
(`confirmed|inferred|unknown`), `reuse` (string describing rights/limitations).
Optional `sha256` pins local document bytes. URLs are provenance, not auto-fetch
instructions. A URL-only mandatory source is unverified until an authorized reader
records a reviewed source digest/attestation in the selection evidence.

Asset: `path` (contained relative path), `kind`
(`guide|tokens|diagram|example|visual-legacy`), `sha256` (64 lowercase hex).
Optional `phases` (list of known phase IDs) and `domains` (list of fact values).
Do not execute examples or treat diagrams as verified cloud state.
Phase IDs are lowercase sense/scope/define/discover/plan/build/review/ship/capture/
resume or standalone. Absent phase/domain filters mean applicable to any selected
task; a present empty filter matches none. An asset is still read only when a
consumer explicitly needs its kind, never just because its pattern was selected.

Exact reference: `source` (source ID from roots/catalog registry), `id`, `version`,
`sha256`. All four required. References never resolve by display name alone.

### 4.2 Catalog (`catalog.json`)

Fields: `schema_version:1`, `source_id` (namespaced ID), `entries` (array),
`includes` (array of `{locator, path, sha256}`), `bindings` (array using 4.3),
`lifecycle` (array of `{id,version,sha256,status,reason,reference,at,replaced_by?}`),
optional `revocations` (array of `{id, version, sha256, reason, reference, at}`).

Each entry is `{id, version, path, sha256, summary, status, applies_to}`.
Metadata is generated from a validated pattern on publication; never hand-maintain
two independent authoritative versions. `path` points to a contained pattern.json.
Entry `status` is publication-time status and must equal the pattern; compute
effective status from lifecycle and revocation events, never overwrite the entry's
publication status from those events.
Catalog includes can reference only its own registered locator or explicit ancestry
locators supplied by the pack context, with contained paths. No arbitrary home/repo
scanning. Recursively included catalogs must have unique source IDs and pinned
digests. Same source+ID+version with different bytes fails; exact duplicates dedupe.

Lifecycle state and revocations are checked in the currently configured catalogs
at continuation boundaries even when an old pattern is pinned. No network
revocation service is implied; a local stale checkout cannot prove no newer
revocations exist.

### 4.3 Bindings and context

Repository `bindings.json`: `{schema_version:1, bindings:[...]}`.
Binding: `id` (unique), `when` (selector), `use` (nonempty exact references),
`role` (`required|default`), `approved_by`, `approval_ref`.
Pack bindings are in its catalog. Personal bindings are not auto-applied in v1;
personal entries require an explicit invocation reference or repository binding.

Explicit invocation `--refs` takes a JSON file containing an array of
`{ref:<exact-reference>, role:"default"|"required", approved_by, approval_ref}`.
There is no implicit role. Required is a declared task binding needing provenance;
a bare display name accepted by legacy frontend adapters maps only to defaults.
Default-bound must clauses conflict exactly as for repository bindings.

`--overrides` accepts `{schema_version:1, items:[...]}`; each item has `setting`,
scalar `value`, `reason`, `approval_ref`, and `replaces` (array of exact clause IDs).
It applies only to matching setting clauses in the current selection. Unknown
clauses/settings or duplicate override settings fail. An override selecting an
existing same-scope default or replacing defaults is recorded explicitly; touching
a must requires a matching exception. No arbitrary new policy is created by an
override. The record is pinned into selection_digest.

Selector: mapping of fact key to nonempty array of exact string values. Keys
match `[a-z][a-z0-9_.-]*`; values are case-sensitive, nonempty, <=128 code points.
AND between keys; OR within a key. Empty selector means explicitly universal and
is allowed only on a pattern or approved binding, not inferred from absent metadata.
No regex, glob, executable expression, numeric range or negation in v1.

Context: `{schema_version:1, facts:{key:value}, evidence:{key:reference}}`.
Every fact has a nonempty evidence reference. Intent labels can cite the brief;
deployment target/subscription/organization facts must cite binding or confirmed
user/environment evidence. The runtime checks structure, not truth of that evidence.
Conflicting values for a fact are an input error, never last-writer wins.

For a selector: any known mismatch -> rejected; otherwise any missing key ->
needs-context; otherwise matched. Required bindings with needs-context make
resolution incomplete. Unrelated known mismatches do not block. Unbound fuzzy
suggestions never become requirements. No LLM call inside the runtime.

### 4.4 Lock and resolution report

Report always includes `schema_version`, `status`
(`ready|empty|needs-context|conflict|unavailable|invalid`), `context_digest`,
`sources`, `selected`, `candidates`, `requirements`, `overrides`, `exceptions`,
`diagnostics`, `metrics`. Each selection records binding reason, exact reference
and applicable clause IDs. Candidate records include decision and missing keys.

Lock adds `selection_digest`, `context`, `created_at`, `source_snapshots`,
`asset_pins`, `requirement_tasks`, `source_attestations`, and `review_evidence`.
It stores selected compact clause text, provenance and local content digests so
handoffs are understandable, but does not copy secret/private source documents.
Local absolute roots are not committed: durable locators are repository-relative,
pack source IDs or explicitly named personal source IDs. Unavailable personal
sources on another machine block continuation until supplied; do not silently use
model memory. Sharing the lock requires review of its clause text.

Content digest: SHA-256 of canonical JSON (sorted keys, compact separators,
ensure_ascii=False, UTF-8; no trailing newline). Reject duplicate keys first.
Pattern digest covers all pattern fields, including asset digests; actual assets
are hashed when indexed and before use. Catalog digest covers its canonical JSON.
Selection digest excludes timestamps, metrics and review evidence; covers context,
source snapshot digests, references, clauses, overrides and exceptions. Changing
only evidence does not invalidate the selected design; changing a clause does.
On verify-lock, retain the original source_snapshots/digest as historical evidence.
Read current catalogs for availability, selected-reference integrity and lifecycle.
Unrelated catalog additions do not change a pinned selection or require identical
whole-catalog digests; selected bytes changing, lost references and revocations do.
If current bindings would remove/add mandatory requirements for this context,
return conflict/replan with the old/new clause sets. Do not silently keep an obsolete
mandatory baseline or overwrite the original lock.

Read a selected pattern once, validate its catalog metadata/digest and use the same
bytes for resolution. Atomic file replacement cannot swap validation and use.
An index digest mismatch is unavailable, not a prompt to silently reindex.

### 4.5 Attestations and source freshness

`--attestations <file>` on resolve/explain/verify-lock/review takes
`{schema_version:1, items:[...]}`. Each attestation contains an exact pattern `ref`,
`source_index` (zero-based sources index), `source_ref` (must equal that source),
`source_digest` (reviewed source bytes, 64 lowercase hex), `reviewed_by`,
`review_ref`, `reviewed_at` (UTC timestamp), `valid_until` (ISO date) and `purpose`
(`source-verification|freshness|both`). No future reviewed_at or expired valid_until.
For statement sources source_digest hashes the UTF-8 statement text; for local
files it must match current bytes and any pinned source digest. External URLs are
not fetched: the digest identifies the reviewed snapshot cited by review_ref.
Require nonempty reviewer/reference but do not claim to authenticate them.

A mandatory URL source needs source-verification/both. An overdue mandatory
pattern needs freshness/both attestations for ALL its sources reviewed on/after
review_after, with current valid_until. A changed pattern digest, changed source
index/ref or changed local bytes invalidates attestation. Renewal replaces evidence
for the same pattern/source and does not change selection_digest, since attestation
is approval evidence, not a new requirement. Approved source content changing
requires recapture/update, not a freshness attestation that hides changed content.
CLI merges supplied evidence into source_attestations only after validation;
verify-lock without newly supplied attestations uses the saved records. Missing
or stale required attestations returns unavailable. Default-only sources warn.

### 4.6 Task mapping

Do not extend work-map v1. Use a companion file supplied as `--task-map`:

```json
{
  "schema_version": 1,
  "selection_digest": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "tasks": ["T1", "T2"],
  "packages": [{"id": "P1", "tasks": ["T1"]}, {"id": "P2", "tasks": ["T2"]}],
  "clauses": [
    {"clause": "example.internal-dashboard@1.0.0#DASH-01", "tasks": ["T1", "T2"]}
  ]
}
```

`tasks` is the explicit inventory of existing plan/task IDs, not a second task
definition. PLAN/review verify it against the authoritative artifact. Each task
belongs to exactly one package. Duplicate task/package/clause records, unknown
tasks/clauses and empty mappings reject. Each selected must and default clause
must map to at least one task; recommendations may be omitted. Project requires
matching selection_digest and complete mapping before emitting a package subset.
Shared clauses appear in each package that owns a mapped task.

The lock's `requirement_tasks` stores this record plus `mapping_digest` (canonical
hash of the record). It is excluded from selection_digest: regrouping work does
not change selected expectations. Projection emits both digests. Review evidence
must include mapping_digest and task_ids valid for the corresponding clause;
changing the mapping invalidates old task-coverage evidence, not the baseline.

## 5. Resolution and authority algorithm

1. Load trusted roots, configured catalogs and binding metadata. Missing optional
   roots are empty; a declared missing catalog is unavailable. A corrupt configured
   catalog is invalid and visible, not a successful empty scan.
2. Evaluate binding selectors and explicit invocation references. Explicitly
   requested drafts require `--preview-draft` and can never produce a ready lock.
   Explicit references still check pattern applicability; missing/mismatched facts
   require correction, not a bypass.
   Only approved/deprecated records are eligible for normal resolution; deprecated
   emits a replacement warning. Bound or included draft/retired/revoked records
   are unavailable, rather than silently omitted. Preview may inspect drafts but
   never produce executable selection evidence.
3. Add all matched bindings. Metadata matches not bound to the task are advisory
   candidates, not active rules. Pack authors obtain automatic application through
   explicit catalog bindings; being installed alone never grants policy authority.
4. Traverse includes in deterministic source/ID/version order. Each dependency must
   match context too. Missing/needs-context dependency blocks its parent. All
   includes of a required binding are required; never demote transitive constraints.
5. Resolve clauses. `must` is mandatory only when reached from a required binding;
   a default-bound pattern with must clauses is a configuration conflict, requiring
   an explicit required binding or an authoring correction. This prevents accidental
   policy promotion and accidental weakening. Legacy imports contain defaults only.
6. Mandatory clauses accumulate. Different `value` for the same `setting` among
   must clauses is conflict. A lower-priority default disagreeing with a must is
   suppressed with explanation. Same-scope competing defaults conflict unless an
   explicit override chooses one. Equivalent values dedupe evidence, not identities.
7. Default precedence: explicit authorized task choice > repository > active pack
   > explicitly selected personal pattern > existing corpus/model fallback.
   Within a scope there is no automatic most-specific-wins rule. Transitive default
   dependencies inherit the selecting scope. Explicit task settings cannot override
   a must clause without a valid scoped exception.
8. Emit full mandatory clauses and selected defaults; rank only unbound advisory
   candidates by number of matched selector keys, then source ID/pattern ID/version.
   Return five candidate summaries maximum, 240 code points each, with total count.
9. Write a lock only for ready/empty resolutions explicitly requested with `--lock`;
   preview/report works without writing. Never write a success lock for conflicts
   or unknown mandatory context.

Sources are configured by the operator/repository owner. A malicious repo can
forge a binding, so none of this replaces enterprise enforcement. Prose conflicts,
source authenticity and approval authority need human/agent review. The report
must state these limits.

Exceptions supplied via `--exceptions <file>` contain exact clause reference,
target/context digest, reason, approval reference, approver, expiry and replacement
verification. Expired/mismatched/missing fields reject the exception. A record
changes the workflow verdict to waived, not passed, and never changes policy.

## 6. Limits and failure semantics

Limits are fixed v1 constants in the shared module, not per-skill heuristics:
pattern JSON 64 KiB; catalog 2 MiB; context/bindings 256 KiB each; 2,000 catalog
entries per configured source; 32 source catalogs; 16 include edges deep; 256
selected patterns; 4 MiB per asset; 32 MiB total export bundle. Reject excess,
never truncate mandatory data. Limit tests use tiny fixtures around boundaries.

No whole-body startup reads. Runtime metrics count catalog reads, selected body
reads, asset reads and output code points, not guessed token counts.
Advisory preview <=1,200 summary code points. Compact selected context >24,000
code points returns needs-context with `budget_exceeded`, complete clause inventory
in the report and an instruction to split by task/component; no partial lock.
Allow explicit `--context-budget-chars N` to raise that output ceiling, not the
resource safety limits. User authorization is a host responsibility.

A package projection may omit clauses only when the work map maps them to another
package. An unmapped mandatory clause blocks the projection. No silent "top N"
mandatory rules; shared clauses can appear in multiple packages.

Normal calls read metadata anew; a runtime index is an optional derived cache,
not a required persistent daemon. If implemented, key it by content digests and
scope identity. Do not rely on mtime alone or TTL for correctness.

Exit codes: 0 ready/empty/successful inspection; 2 invalid input/schema/path/resource
limit; 3 needs-context; 4 conflict; 5 unavailable/stale/revoked source; 6 write
collision/concurrent update; 7 unmet review requirement. Structured report on
stdout, concise actionable diagnostics on stderr. `explain` uses the same resolution
status codes; `list` returns 0 even with zero entries. Never broad-catch and return 0.

## 7. Authoring, lifecycle and sharing

Canonical skill: `SKILL.md` under `skills/pattern/` (planned, RN-07); generated Copilot native `li-pattern`.
Skill drives reasoning and source capture; CLI performs deterministic validation,
resolution and safe persistence. It never claims to automatically infer policy.

CLI surface (all through the same launcher/API):

| Command | Required inputs | Output/side effects |
| --- | --- | --- |
| `list` | roots | Catalog summaries, no pattern bodies |
| `show` | `--ref <source:id@version>` | One validated pattern; ambiguous version/digest fails |
| `check` | `--path` or roots | Validation/reference/digest diagnostics |
| `index` | `--source-root`, `--expected-catalog-digest` if exists | Verify/rebuild metadata for already registered entries only; preserve bindings/includes/lifecycle/revocations |
| `resolve`, `explain` | `--context`, optional `--refs`, `--overrides`, `--exceptions`, `--attestations`, `--lock` | Shared report; resolve alone may write the explicit lock |
| `capture` | `--input <draft.json>`, `--scope repo|personal`, `--name`, `--source-id` on first source creation | Validate and create draft, refuse overwrite |
| `approve` | `--path`, `--version <new-version>`, `--approval <record.json>`, `--expected-digest` | Persist reviewed next version/status; record provenance, not grant permission |
| `apply` | `--change <file>`, `--expected-digest` if bindings exist | Preview by default; `--write` atomically updates repository bindings |
| `update` | `--path`, `--input`, `--expected-digest` | Create a strictly newer content version; diff clauses and dependents, old version intact |
| `deprecate`, `retire`, `revoke` | `--ref`, `--record`, `--expected-catalog-digest` | Record lifecycle event/replacement or revocation with impact report |
| `remove` | `--ref`, `--expected-catalog-digest` | Preview by default; explicit `--write` removes only unused draft/current catalog entry; never recursively delete history |
| `export` | `--refs`, `--out` | Create new contained directory bundle + digest manifest; no upload |
| `import` | `--bundle`, `--scope repo|personal`, `--destination-source`, `--version-map` | Validate whole bundle and preview; `--write` stages new drafts, preserving provenance but not trust |
| `verify-lock` | `--lock`, `--context`, optional `--attestations` | Check pins, current source revocations/lifecycle and context; no auto-upgrade |
| `map` | `--lock`, `--task-map`, `--expected-lock-digest` | Preview mapping; `--write` installs validated requirement_tasks atomically and invalidates old task review evidence |
| `project` | `--lock`, `--task-map`, `--package` | Clauses mapped to package, preserving IDs and completeness |
| `review` | `--lock`, `--context`, `--evidence`, optional `--attestations` | Verify current lock/sources first, then per-clause coverage; missing mandatory evidence exits 7 |

Versions are directories `<source-root>/<id>/<version>/pattern.json`. Approved
content is immutable; approval of a draft writes a new approved version (including
approval in the digest), leaving the draft. The caller supplies the strictly greater
version; no automatic version allocation. Lifecycle events live in the catalog
and do not mutate pinned bytes. `status` in pattern is its state at publication;
effective state is the latest validated catalog event. Add `lifecycle` catalog
array of `{id,version,sha256,status,reason,reference,at,replaced_by?}` for deprecation
and retirement. Conflicting events with the same timestamp fail; order by `at`.
Lifecycle event status is only deprecated or retired, with monotonically increasing
timestamps. An approved record can become deprecated or retired; deprecated can
become retired; retired cannot return to approved/deprecated. Corrections publish a
new version, not a status reset. Revocation overrides any lifecycle state and has
no un-revoke operation in v1. Retirement excludes new selection;
pinned deprecated work warns; pinned retired/revoked work blocks dependent use.
`review_after` in the past warns for defaults and blocks mandatory use without
current source attestation referencing the same content digest and a next review date.

Catalog is the publication registry. `capture`, `approve`, `update` and `import`
register new entries explicitly in a catalog-last transaction. First capture
requires a unique namespaced source-id and creates an empty catalog plus the new
draft entry. Subsequent capture must use that same source identity.
`index` only validates/rebuilds EXISTING registered entries, never scans version
directories to discover publications. Missing entries are errors, not silently
removed; content digest mismatch is an error, not a request to bless edited bytes.
Preserve bindings, includes, lifecycle and revocations byte-equivalently in meaning.
Unregistered directories, including crash staging and removed entries, stay
unregistered. To introduce hand-authored content, use capture/import, not index.
Test deprecate->index, remove->index and interrupted-stage->index explicitly.

`apply --change` input is `{schema_version:1, operation, id, binding, reason,
approved_by, approval_ref}`. Operation `add` requires absent id and a complete
matching binding; `replace` requires existing id and a complete replacement;
`remove` requires existing id and `binding:null`. All operations require reason
and approval provenance. Replacing/removing a required binding emits old/new
required clause sets and reduced baseline in preview, and requires --write plus
the current bindings digest. This records authorized change, not approver validation.
Unknown IDs, add collisions and stale expected digests do not modify files.

Writes require compare-and-swap expected digests plus an exclusive lock for each
source root. Acquire via exclusive creation, release only own lock; no automatic
stale lock stealing. Atomic replacement within the same directory; preflight all
paths before writes. Multi-file publish stages immutable new content first and
replaces catalog last. Readers see either old or new complete catalog. Interrupted
unreferenced staging is reported/cleaned by its owning operation, not indexed as
published data. An approved catalog MUST NOT refer to half-written files.

Update/deprecate/remove previews inspect dependents in configured catalogs and
locks under the explicit repository plan root, not other repos or sessions. Report
the inventory scope: it cannot prove no external consumer exists. Referenced
approved history is not physically deleted by v1. Removing a required binding needs
an approval reference and must expose the reduced baseline.

Capture from docs, policy exports, source code, screenshots or interviews:
inspect only authorized sources; separate confirmed expectations from observations;
write draft; verify selectors, clauses and provenance; review before approval.
Cloud access is external to this system. Never infer tenant network requirements
from generic ALZ/CAF recommendations. Inaccessible mandatory sources remain unknown.

Export is local and opt-in. Include selected dependency closure and authorized
declared assets only; never follow URL references or copy full policy documents,
credentials, caches, absolute home paths or unrelated pack files. Import validates
all digests/containment/limits before publication; rejects collisions rather than
overwriting. Bundle can be committed to a team pack by its normal review process.
Remote publication, package installation and credential configuration are out of scope.

Import transformation is normative:

The export directory has `bundle.json` with `schema_version:1`,
`patterns` (array of `{ref:<exact-reference>,path}`), `files` (array of
`{path,sha256}` for every pattern and asset) and `lifecycle` (effective status plus
source event provenance per exact ref). Paths are contained bundle-relative files;
only regular files are allowed; reject symlinks/reparse points. No archive
extraction is involved.
Every file appears exactly once; unexpected files, absent dependency members and
duplicate refs fail import. File hashes cover raw exported bytes; ref hashes cover
canonical pattern JSON as usual. Export copies no source catalogs or bindings.

1. Verify original manifest, every original pattern/asset digest, closure, paths
   and limits before changing content. All includes must be in the bundle;
   external dependency references are rejected in v1, not fetched.
2. `--version-map` supplies an array `{original:<exact-ref>, id, version}` covering
   every imported record exactly once. Destination source ID must match the selected
   local catalog (or create that new source explicitly); reject duplicate output
   identities and any existing destination version, including identical bytes.
3. Traverse dependencies children-first. For each record, set destination id/version,
   status draft, remove operative approval, rewrite includes to the mapped child
   destination references/new digests, then calculate its new digest. Copy authorized
   assets unchanged after hash validation. Never preserve an old digest after mutation.
4. Preserve the original reference, digest, publication status and approval in
   `extensions["lintel.imported"]` as inert provenance. It is not operative trust.
   Do not import bindings, lifecycle or revocation authority as local approval;
   record original lifecycle status in provenance, warn on deprecated, and refuse
   bundles containing retired/revoked sources.
5. Preflight all destinations; stage the whole closure and publish catalog last.
   Preview shows the complete old->new reference/digest mapping. No writes on any
   collision, unresolved dependency or failed preflight.

Local approval is children-first. After approving children, use update on the
parent draft to replace its references with the newly approved child references,
then approve that reviewed parent version. Approval must reject a dependency that
is draft, retired, revoked or unavailable. This explicit versioned workflow avoids
silently rewriting a reviewed blueprint's dependency graph.

## 8. Workflow integration

One shared reference, `references/consumer-contract.md` under `skills/pattern/` (planned, RN-07), documents
inputs, exact helper invocation, output status handling and phase obligations.
Phase skills link it; do not copy a separate resolution algorithm into each.

SENSE only discovers metadata availability; SCOPE identifies context uncertainty.
DEFINE resolves applicable expectations before design, DISCOVER verifies sources.
PLAN adds requirement IDs to the existing spec/work-map task IDs and writes the lock
beside that initiative. Do not modify the work-map v1 schema; link companion lock
explicitly from plan/prompt. Spec Kit sources remain authoritative.
BUILD verifies lock and supplies projections. REVIEW requires complete clause
evidence as supplemental content evidence inside the ADR-0028 v2 review contract
(RN-02); pattern coverage never clears stale/missing review or a later rejection. SHIP exposes failed/waived/unverified mandatory clauses without claiming
platform enforcement. CAPTURE proposes updates; RESUME verifies pins and status.

Direct entry into any phase must either resolve the current context or consume
and verify an explicitly supplied lock. No reliance on a preceding SENSE call.
Without configured pattern sources/bindings, behavior is unchanged apart from
optional empty report; no new prompts or lock files are required.

### Standalone consumer inventory

Initial automatic skill integration covers these explicit entry points, not every
arbitrary prompt in every host. Schema/CLI reuse is universal; automatic invocation
still depends on the host following the installed skill.

| Entry group | Required integration |
| --- | --- |
| `generate`, `generate-outline`, `generate-write`, `generate-design`, `generate-qa` | Shared pipeline context attachment; direct sub-skill entry resolves when no verified attachment exists |
| `generate-word`, `generate-ppt` | Both direct brief and from-pipeline modes resolve/verify before structure/content choices; pass clauses to existing quality review |
| `generate-pdf`, `generate-xlsx`, `generate-visio` | Preserve each provider's current status (RN-05: PDF writer and workbook are working providers; only Visio is a template slot; no PDF reader); their at-invocation contracts require resolution and evidence |
| `ta`, `da`, `sc`, `dh`, `tq` | Engineering module entry resolves target expectations and passes only applicable clauses to its scoped subskills |
| Frontend entries in section 9 | Resolve/verify through the same contract, not an independent design-only policy loader |

Add optional `pattern_context` to shared pipeline design-spec.json with
`schema_version:1`, `selection_digest`, `lock_ref` (run-relative safe path) and
`clause_ids`. Attach the same reference to pipeline handoffs. Consumers validate
the reference/digest and read the lock; the attachment is not proof of resolution.
Direct `generate-word --brief` must demonstrate a document pattern adding a
required section to the generated technical document, and QA detecting its removal.
Use an existing generator/tool available during host acceptance; an artifact fixture
tests helper integration only and cannot count as the host generated-document pass.
Preserve existing format conversion/template behavior and inherited compliance gates.
Unlisted direct subskills can opt into this contract; do not claim they automatically
consume patterns until an explicit adapter and acceptance case are added.

Evidence input: `{schema_version:1, selection_digest, mapping_digest, items:[...]}`; item =
`{clause, task_ids, status, evidence_refs, explanation}`. Status is
`passed|failed|waived|not-applicable|unverified`. Passed requires nonempty evidence
references and review explanation, not just a checkbox. Waived needs a matching
valid exception. Mandatory not-applicable requires a reviewed applicability
correction and newly resolved lock; it cannot be a convenient skip in the old lock.
The runtime checks coverage and evidence structure, not whether screenshot/test
claims are true. Workflow review assesses the referenced artifacts.

## 9. Frontend adapter

Keep `frontend-style-extract` and `generate-style-learn` as specialist capture routes.
Emit draft universal records and reference existing visual assets by validated
digests; no duplicated authoritative tokens. Legacy `pattern.json` becomes an
asset with kind `visual-legacy` because its schema_version 1 is NOT this schema.
Discriminate by location/adapter and required fields, not schema_version alone.

Add `lib/pattern_visual.py` consuming shared records, with functions to:
convert validated legacy observations to a draft pattern; project selected visual
defaults/constraints into optional `pattern_context` on frontend-design-spec; and
validate mechanical structured-setting differences against that spec.
`pattern_context` = `{schema_version:1, selection_digest, clauses, asset_refs}`.
Keep outer frontend-design-spec version 1; field is optional. Unrecognized legacy
fields stay in the asset, not silently interpreted as universal policy.

Supported v1 structured settings are deliberately small:

| Setting | Frontend spec destination | Type and comparison |
| --- | --- | --- |
| `visual.layout.max-width` | `layout_grammar.max_width` | Nonempty string; exact equality |
| `visual.layout.section-spacing` | `layout_grammar.section_spacing` | Nonempty string; exact equality |
| `visual.layout.grid` | `layout_grammar.grid` | Nonempty string; exact equality |
| `visual.interaction.scroll-smoothing` | `interaction_signature.scroll_smoothing` | Boolean; exact type/value |
| `visual.interaction.hover-intent` | `interaction_signature.hover_intent` | Nonempty string; exact equality |
| `visual.interaction.page-transitions` | `interaction_signature.page_transitions` | Nonempty string; exact equality |
| `visual.palette.<token>` | `palette.tokens[<token>]` | Token matches `[a-z][a-z0-9-]*`; value is #RRGGBB; compare lowercase |

Only these keys are mechanically projected in v1. Unknown visual settings remain
clause requirements for explicit review, return `unverified_settings` and cannot
be claimed mechanically passed. No arbitrary dot-path assignment from imported data.
Type mismatch or duplicate destination values is a conflict, not coerced input.

`project_visual(base_spec, resolution)` requires ready resolution and applies its
final structured-setting winners to the destinations above, creating missing
mapping objects but rejecting a wrong-shaped existing object. It preserves all
other fields. Record applied clause IDs and old/new values in pattern_context.
The consumer must turn explicit brief decisions about bound settings into
--overrides before resolving; adapter never guesses whether an existing value was
a deliberate brief choice. Those overrides still cannot bypass must clauses.
`validate_visual(spec, resolution)` checks the same mapped destinations and reports
each mismatch by clause ID; prose clauses use normal evidence review.

Frontend preference order is explicit brief overrides > repository pattern defaults
> active-pack pattern defaults > explicitly selected personal defaults > active
Design DNA profile > corpus recommendations. Mandatory bindings constrain this
entire chain. With no selected patterns, preserve ADR-0016 brief > profile > corpus
exactly. Profile/corpus files are not modified to implement a selected pattern.

`--pattern <name>` / `--baseline <name>` retain legacy lookup when no qualified
universal reference exists; collisions across sources require qualification.
Legacy usage keeps existing preference behavior. Import is explicit, non-destructive
and does not reclassify visual observations as mandatory standards.

Integrate consumers (revised by RN-04): frontend-design, design-dna, frontend-typography,
frontend-motion, frontend-shader, generate-web (including `--mode mockup`, the current
single-file mockup owner), generate-app and frontend-design-review (the sole built-UI
review owner). Each direct decision/render entry receives resolved context
or verifies a supplied selection; purely reading a palette need not run a full cycle.
Do not replace Design DNA retrieval/validators. Mandatory constraints bound its
choices; defaults apply only to choices not explicitly overridden.

Only extract permitted design principles/assets. URL/screenshot observations do
not prove accessibility, exact fonts, dependencies or licensing. Preserve
attribution and record unknowns; never copy arbitrary proprietary shader/source code.

## 10. Verification and acceptance

Synthetic fixtures cover dashboard behavior, network targeting and document style,
but ship only one canonical deep dashboard example. The other domains are small
test data, not curated product knowledge.

Every new helper has positive/negative tests. Requirements R01-R16 are complete only
after cards' behavioral outputs and applicable compatibility checks pass.
Unit assertions must inspect actual returned clauses/statuses and read counts.
Integration tests call real resolver/launcher/adapter code, not grep for skill prose.

Separately perform a host acceptance transcript: start a fresh local session with
synthetic pack/target, request a dashboard, show selected baseline and produced
behavior; request an unrelated backend change, show zero visual asset reads;
resume and demonstrate changed/revoked pin handling. Model or remote use requires
its own host permissions. If unavailable, mark host acceptance deferred and do not
claim automatic behavior in that host.

## 11. Open decisions and release boundary

No ordinary implementation choice is intentionally left open in this spec.
The design is proposed, not a record of organizational approval. BUILD approval
and actual host validation remain explicit gates. Re-plan only if current code or
accepted decisions invalidate this contract; do not use that as permission to
silently drop lifecycle, portable installation or direct-entry coverage.

Before integration, compare the base commit and overlapping files against the then
current target branch. Other sessions are out of scope; never inspect their
worktrees, send them messages, switch their branches or overwrite their ledgers.
No push, PR creation, merge, release or production discovery is part of this
planning delivery.
