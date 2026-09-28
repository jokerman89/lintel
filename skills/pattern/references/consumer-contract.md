# Reusable pattern consumer contract

This is the one contract every workflow, document, engineering and frontend entry uses to
consume reusable patterns. Phase skills link here; none carries its own resolution, precedence,
digest or validation logic. The executable validator and resolver is `lib/patterns.py`
(CLI `bin/li-pattern.py`, launcher `bin/li-pattern`). Design-spec projection for visual
settings is `lib/pattern_visual.py`. Their frozen interface is recorded in the reusable-patterns
initiative contract; this page states how a consumer calls them and what it must do with the result.

The runtime checks structure, declared provenance, digests, lifecycle and completeness. It does
not prove that a source is authentic, that an approver had authority, that prose clauses agree,
or that cited evidence is true. A repository can forge a binding. None of this replaces
enterprise controls, branch protection or required independent review.

## Contents

- [No configured patterns](#no-configured-patterns)
- [Invocation](#invocation)
- [Inputs](#inputs)
- [Status handling](#status-handling)
- [Direct entry](#direct-entry)
- [Phase obligations](#phase-obligations)
- [Standalone consumers](#standalone-consumers)
- [Design-spec attachments](#design-spec-attachments)
- [Review evidence](#review-evidence)
- [Capture and approval](#capture-and-approval)
- [Assets](#assets)
- [Evidence categories](#evidence-categories)

## No configured patterns

When the repository has no `.claude/patterns/` catalog or bindings, the active pack has no
`patterns.source`, and the task names no explicit reference, resolution is `empty` (exit 0)
with zero pattern body and asset reads. Then behavior is unchanged:

- no new question, prompt, approval or confirmation;
- no required lock, task map, evidence file or attachment;
- existing design precedence stays exactly brief > Design DNA profile > corpus (ADR-0016);
- an optional empty report may be mentioned in one line; it is never a blocker.

A consumer may skip invoking the runtime entirely when it can see none of those sources exist.
Personal catalogs under `$LINTEL_HOME/patterns/` never activate on their own.

## Invocation

Call the launcher with explicit inputs. It resolves roots from the working repository,
`LINTEL_HOME` and the ADR-0029 profile context record, and passes them to the Python CLI as a
JSON envelope on stdin. Never interpolate pattern data into shell code, never build the envelope
by string concatenation, and never source pattern content.

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" resolve --context "$ctx" [--refs F] [--overrides F] \
  [--exceptions F] [--lock <initiative>/patterns.lock.json]
bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" verify-lock --lock "$lock" --context "$ctx"
bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" map --lock "$lock" --task-map "$map" \
  --expected-lock-digest "$sha" [--write]
bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" project --lock "$lock" --task-map "$map" --package P1
bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" review --lock "$lock" --context "$ctx" --evidence F
```

`list` and `show --ref <source>:<id>@<version>` inspect metadata and one body; `explain`
reports the same resolution with binding evaluations. A non-Git working directory must supply
an explicit repository root; the launcher never falls back to the filesystem root or the
installed source tree. Runtime pattern operations require the optional Python 3.10+ toolchain;
report its absence instead of guessing. Bare installation has no Python prerequisite.

If the installed CLI rejects a command or option (exit 2, `invalid_arguments`), that phase
obligation is **unavailable** in this installation. Report it; never replace a missing command
with prose inspection, a hand-written lock or a mock result.

Scratch output goes under `.claude/runtime/patterns/<run-id>/` with an explicit run ID, never
the latest-modified directory. The durable lock is `<selected-initiative>/patterns.lock.json`
beside the existing work artifacts; the companion task map is a separate file supplied with
`--task-map`. The work-map v1 schema is not changed.

## Inputs

**Context** (`--context`): `{"schema_version":1,"facts":{...},"evidence":{...}}`. Every fact
has a nonempty evidence reference (brief path, confirmed user answer, binding or environment
record). Intent labels may cite the brief. Deployment target, subscription, tenant and
organization facts must cite a binding or confirmed user/environment evidence. **Omit a fact
you do not know.** A missing fact yields `needs-context`; a guessed fact silently selects the
wrong baseline. Never infer a production target from artifact type, platform or generic
landing-zone recommendations. No live discovery is implied.

**Explicit references** (`--refs`): an array of `{ref, role, approved_by, approval_ref}` with an
exact `{source,id,version,sha256}` reference and an explicit `default` or `required` role.
There is no implicit role. A legacy bare display name (`--pattern <name>`, `--baseline <name>`)
maps only to a default and keeps legacy lookup when no qualified universal reference exists.
Colliding names across sources require qualification.

**Overrides** (`--overrides`): explicit brief decisions about bound settings become override
items (`setting`, scalar `value`, `reason`, `approval_ref`, `replaces`) **before** resolution.
The consumer decides whether a brief value was deliberate; no adapter guesses. An override
never bypasses a `must` clause without a matching exception.

**Exceptions** (`--exceptions`): scoped, approved, expiring waivers of exact mandatory clauses.
A waiver changes the verdict to `waived`, never to `passed`, and never changes policy.

## Status handling

| Status | Exit | Consumer action |
| --- | --- | --- |
| `empty` | 0 | Continue exactly as without patterns ([No configured patterns](#no-configured-patterns)) |
| `ready` | 0 | Carry the full `requirements` and `settings` winners into the decision; show selected references and reasons |
| `needs-context` | 3 | Ask for, or cite, the listed missing facts; do not guess them. `budget_exceeded` means split the work by task or component. No lock |
| `conflict` | 4 | Stop the dependent decision; present the conflicting clauses/settings and the authoring or override correction. No lock |
| `unavailable` | 5 | A configured, bound, pinned or required source is missing, drifted, retired, revoked, draft, unattested or past review. Block dependent use; never resolve from another source or from memory |
| `invalid` | 2 | Fix the input file or source; visible, never an empty success |
| write collision | 6 | Re-read and retry with the current digest; never steal a lock |
| unmet review | 7 | Mandatory clause evidence is missing, failed or unverified; REVIEW/SHIP cannot report it as passed |

Read `requirements[]` in full. `mandatory` clauses are never ranked, truncated or dropped;
`default`, `recommendation`, `suppressed`, `overridden`, `waived` and `conflict` are shown with
their reasons. Read setting winners from `settings{}`; never recompute precedence, hashing or
validation. `candidates` are advisory metadata only and never become requirements. Treat
`selection_digest` as an opaque identity of the selection, not as proof of anything else.

## Direct entry

Every phase and standalone entry is independently correct. When invoked directly it either
resolves the current context itself or consumes an explicitly supplied lock and runs
`verify-lock` against the current context. It never relies on a preceding SENSE or DEFINE call,
a remembered chat, or the presence of an attachment. Direct entry and cycle entry call the same
command with the same inputs and therefore produce the same `selection_digest`.

## Phase obligations

| Phase | Obligation | Never |
| --- | --- | --- |
| SENSE | Note whether pattern sources exist (catalog/bindings/`patterns.source`) from metadata; `list` reads summaries only | Read pattern bodies or assets at startup |
| SCOPE | Record which context facts are unknown (target, audience, environment) and their evidence needs | Fill an unknown target from defaults |
| DEFINE | Resolve before design choices; carry mandatory clauses into acceptance criteria and show defaults with their reasons | Treat an unresolved or `needs-context` target as a baseline |
| DISCOVER | Verify cited local sources and flag URL-only or overdue mandatory sources as needing attestation | Fetch URLs or claim external sources were verified |
| PLAN | Resolve with `--lock` beside the initiative; map every selected must/default clause to existing spec/work-map/Spec Kit task IDs with `map --write`; link the lock and task map from plan and prompt | Invent task IDs, change work-map v1 or write a lock for a non-ready result |
| BUILD | `verify-lock` before each package; hand implementers the `project` output for their package | Continue affected work after changed, retired, revoked or missing pins |
| REVIEW | Assess clause evidence with `review` as supplemental content evidence inside the ADR-0028 v2 review | Let pattern coverage clear stale, missing or rejected independent review |
| SHIP | Show failed, waived and unverified mandatory clauses in the delivery summary | Claim platform enforcement or a pass from coverage alone |
| CAPTURE | Propose new or changed patterns as drafts with provenance | Approve, publish over or bless inferred expectations |
| RESUME | `verify-lock` the saved lock with the saved context before the next card | Silently re-resolve, upgrade pins or keep an obsolete mandatory baseline |

Changed context or a changed mandatory baseline (`context_changed`,
`mandatory_baseline_changed`, `replan_required`) returns to PLAN with the old and new clause sets.
Deprecated pins and changed defaults are warnings to surface, not silent changes.

## Standalone consumers

| Entry | Obligation |
| --- | --- |
| `generate` pipeline and its `generate-outline`, `generate-write`, `generate-design`, `generate-qa` stages | Pipeline runs resolve once and attach a verified `pattern_context` to `design-spec.json`; a direct stage entry without a verified attachment resolves itself |
| `generate-word`, `generate-ppt` | Brief mode and from-pipeline mode receive the same clauses before structure/content choices; required sections become outline items and are passed to the existing quality review |
| `generate-pdf`, `generate-xlsx`, `generate-visio` | Keep each provider's current status: PDF writer and workbook provider are working providers, Visio is a template slot. Conversion preserves required clauses; no PDF reader is added and produced PDF text stays unverified unless inspected |
| `ta`, `da`, `sc`, `dh`, `tq` | Resolve target-bound expectations at module entry and pass each scoped sub-capability only its projected clauses; an unknown target blocks the dependent design |
| Frontend decision, render and review entries | Resolve or verify through this contract, then project visual settings with `lib/pattern_visual.py`; no design-only policy loader |

Unlisted subskills may opt in by following this contract; do not claim they consume patterns
automatically until an explicit adapter and acceptance case exist.

Frontend preference order with selected patterns: explicit brief overrides > repository pattern
defaults > active-pack pattern defaults > explicitly selected personal defaults > active Design
DNA profile > corpus recommendations. Mandatory bindings constrain the whole chain. Profile and
corpus files are never modified to implement a pattern. Design DNA retrieval, validators and
quality rules remain in force for every unconstrained choice.

## Design-spec attachments

Both attachments are optional fields; the outer design-spec versions stay unchanged and the
shared `design_contract` validator accepts them as additional fields. An attachment is a
reference, not proof of resolution: consumers verify it before use.

- Pipeline `design-spec.json`: `pattern_context = {schema_version:1, selection_digest,
  lock_ref, clause_ids}`, with `lock_ref` a safe run-relative path. Build it with
  `pattern_visual.design_attachment(lock, lock_ref)` and verify it with
  `pattern_visual.verify_design_attachment(roots, run_dir, attachment, context)`, which reads the
  lock contained under the run, checks its digest and clause IDs, then runs core `verify_lock`.
  A missing, stale or mismatched attachment is `unavailable`, never a pass.
- `frontend-design-spec.json`: `pattern_context = {schema_version:1, selection_digest, clauses,
  asset_refs}` written only by `pattern_visual.project_visual(base_spec, resolution)`. It
  applies the final structured-setting winners of a `ready` resolution to the fixed v1 table
  (`visual.layout.max-width`, `.section-spacing`, `.grid`; `visual.interaction.scroll-smoothing`,
  `.hover-intent`, `.page-transitions`; `visual.palette.<token>`), preserves every other field
  and records old and new values per clause. Unknown visual settings are returned as
  `unverified_settings` and stay open review obligations. `validate_visual(spec, resolution)`
  reports each mechanical mismatch by clause; prose clauses need ordinary evidence review.

## Review evidence

`review --evidence` takes `{schema_version:1, selection_digest, mapping_digest, items:[...]}`
with one item per clause: `{clause, task_ids, status, evidence_refs, explanation}` and status
`passed|failed|waived|not-applicable|unverified`.

- `passed` needs nonempty evidence references and a review explanation, not a checkbox.
- `waived` needs a matching valid exception; it is reported as waived, not passed.
- Mandatory `not-applicable` needs a reviewed applicability correction and a newly resolved
  lock; it is never a convenient skip inside the old lock.
- Task IDs must be valid for the clause under the installed `mapping_digest`; a changed mapping
  invalidates old task coverage evidence, not the baseline.
- Omitted, failed or unverified mandatory clauses exit 7.

Clause coverage is **supplemental content evidence**. It is recorded in the ADR-0028 shared v2
review/QA evidence for the same work, task and profile binding. It never records a review PASS,
never clears stale or missing independent review, and never overrides a later rejection. The
reviewer still assesses the referenced artifacts; the runtime checks structure only.

## Capture and approval

Capture turns authorized sources (documents, policy exports, code, screenshots, interviews)
into **draft** patterns via `li-pattern capture`. Separate confirmed statements from
observations; record `confidence` and `reuse` rights honestly. Screenshots and URLs do not
prove accessibility, exact fonts, dependencies or licensing; record those as unknown. Never
copy proprietary source code, shaders or assets without permission. Approval is a separate,
explicit `approve` with a reviewed approval record and a strictly newer version; inference is
never approval. CAPTURE and the specialist style routes propose changes; they do not publish
over, approve or re-bind existing patterns.

## Assets

`asset_refs(report_or_lock, kind=..., phase=..., domain=...)` returns metadata references with
zero reads. Read an asset only when the consumer explicitly needs that kind, with
`read_asset(roots, ref, phase=..., domain=..., selection=<ready/empty report or verified lock>)`,
which verifies containment, declaration, lifecycle, selection membership and bytes before
returning them. Workflow and design consumers always pass `selection`; an asset of a foreign
or unselected pattern is `asset_not_selected` (unavailable). Omitting it is only for standalone
inspection. Selecting a pattern is not a reason to load its
assets; an unrelated task (for example a backend change) reads zero visual assets. Examples and
diagrams are never executed or treated as verified cloud state. Do not derive integrity from
`selected[].assets` metadata alone.

## Evidence categories

Report each claim at its actual level: helper unit tests, local integration through the real
resolver/launcher, and host/model acceptance in a fresh session are different categories. A
synthetic fixture never counts as host acceptance of automatic behavior. When a command,
launcher or host observation is unavailable, state it as pending or deferred.
