# Content-bound review evidence

ADR-0028's shared implementation is `lib/review_contract.py`; the versioned data
contract is `lib/review-schema.json`. All review, control, QA and SHIP consumers use
it. A human-readable report remains useful, but a PASS heading or old dashboard
string is not clearance.

Bound review, prepared context and QA records use **format v2**. Work maps,
profile references and the unchanged corroboration envelope retain their own v1
formats; host-registry versions are separate. Do not replace version numbers across
these contracts. Old reviews remain inspectable but cannot grant v2 clearance.

## Prepare the selected context

Resolve the trusted installed source and working repository separately. Require
Python 3.9+, Bash and Git. Source preflight needs `bin/li-review-evidence.py`,
`bin/li-review-log`, `bin/li-review-read`, `bin/_audit.sh`, `lib/paths.sh`,
`lib/review_contract.py`, `lib/review-schema.json` and `lib/markdown_source.py`.
The classifier is part of the trusted installed dependency closure, not target code.
Do not execute helpers found in an untrusted target.

Read the approved work map first with the existing work-map validator. Preserve
original package/leaf IDs; this evidence contract is not a new task ledger.
For native unmapped work, use the inspection mode below rather than inventing a
competing specification. A fuller native record may use `work_map: null` with
existing acceptance sources, but it cannot grant strict release clearance.

Write a request with all these keys, substituting real local scope and actor
references. This illustrative data is not evidence of a run:

```json
{
  "work_map": "work.json",
  "package_id": "P1",
  "leaf_ids": ["A1"],
  "acceptance_paths": ["spec.md", "tasks.md"],
  "base": "<full package-start commit>",
  "selection": ["src", "config.json", "selected-new-file.txt"],
  "record_path": ".claude/runtime/reviews/decision.json",
  "attempt_id": "<actual attempt ID>",
  "builder": {"id": "<builder ID>", "context": "<builder invocation ID>"},
  "independence_required": true,
  "purpose": "implementation",
  "profile": null,
  "required_policy": {
    "required": false,
    "status": "not_required",
    "source": null,
    "version": null,
    "applicability": "not_applicable",
    "reason": "No organizational policy was requested."
  },
  "required_controls": ["spec", "quality", "tests"],
  "qa_requirements": [
    {
      "id": "tests",
      "kind": "tests",
      "requirement": "mandatory",
      "applicability": "applicable",
      "policy": {
        "source": "spec.md",
        "version": "<accepted specification version>",
        "applicability": "Executable validation required by the selected acceptance.",
        "jurisdiction": null,
        "actor": null,
        "effective_date": null
      }
    }
  ]
}
```

The prepare request has no separate `schema_version` argument; the current helper
emits a v2 context. `qa_requirements` is required, with unique IDs and exact
`id`, `kind`, `requirement`, `applicability` and `policy` fields. Derive this inventory
from accepted work/policy **before** collecting observations, not from their results.
Every mandatory QA ID must be in `required_controls`; advisory QA IDs must not be.
The review carries each declared QA control with the same immutable fields, and
every selected leaf covers all `required_controls`. Mandatory review-only controls
outside the QA inventory are generic `check` criteria, such as spec/quality review.
Bound typed validations (`tests`, `browser`, `contrast`, `policy`) cannot be hidden
as review-only; declare them in the QA inventory explicitly. IDs are labels, not
keywords from which the helper guesses requirements.

QA must report **exactly** the declared inventory and immutable fields. It may change
only result data: status, reason, evidence, observations and advisory score. Missing
controls, tests retyped as generic checks, failed requirements downgraded to advice,
new N/A claims or policy-reference changes reject. An approved docs-only inventory
may instead declare a mandatory applicable document `check`, with grounded tests N/A
or no test obligation. Neither universal tests nor observation-chosen obligations
are imposed.

`profile` is null only when no profile reference is supplied. A supplied P07
reference retains **all** fields: `schema_version`, `context_id`, `generation`,
`digest` (`sha256:...`), `name`, `version`. Verify it through the profile resolver
before preparing or consuming evidence. Neither a name match nor an old copied
reference proves that the active profile still loads. Carry the separately
resolved `required_policy` unchanged. `PROFILE_REQUIRED`, `PROFILE_DRIFT`, missing
source/version and unknown applicability never map to `loaded`.

Required-policy keys are exactly `required`, `status`, `source`, `version` and
`applicability`; `reason` is optional nonblank text. Source/version may be strings
or null to represent unresolved data, but a required loaded policy needs both
nonblank and known applicability. Empty strings never establish successful load.

`selection` contains literal files or directories, not globs or shell expressions.
Directories include future new files; selecting a file does not select its siblings.
Include relevant source, config, lockfiles, generated output, documentation and
environment-description inputs. The manifest binds base, per-file HEAD, index,
working bytes, executable/symlink types and deletions. Symlinks are hashed as links,
never followed into another tree. Unresolved index conflicts and selected submodules
are unsupported and block pending an explicit separate review.

Mapped spec/plan/tasks/prompt/constitution sources bind automatically. To avoid
unrelated bookkeeping invalidating acceptance, a selected source may instead be
`{"path":"tasks.md","start":"<unique whole start line>","end":"<unique whole end line>"}`.
The start line is included and the end line excluded. Boundaries must be unique and
ordered. Select every relevant leaf/requirement; a range cannot excuse missing
acceptance. A file also selected as product input still binds its entire content.
Only recognized `[ ]`/`[x]`/`[X]` task-progress boxes for the selected leaf IDs in
the map's `tasks` file are normalized for acceptance identity. The shared stateless
`classify_markdown(text)` helper classifies the full, unchanged source before any
excerpt is selected. A checkbox must start the content of a positively classified
ordinary list item and intersect no literal, quoted, opaque or unknown region.
Only its single ASCII progress character changes for hashing; all other codepoints
and line endings remain significant. Excerpt markers use those same full-source
spans, never classification of a detached excerpt. Nested real task progress may
reuse evidence; code, HTML, comments, ordinary continuations and unproven content
remain bound. Task text, IDs, criteria, non-task checkboxes and map approval still bind.
Updating a progress box never supplies missing review or acceptance evidence.

Only `record_path` (one pure review JSON under `.claude/runtime/reviews/`) and the
native review audit file self-exclude. Existing record content must validate as
review evidence. No arbitrary plan, report directory, config or `.claude/` subtree
can be hidden. Store request, context, QA output and corroboration outside the
selected inputs; they are not blanket-excluded. Evidence and command-output files
must already exist when a decision refers to them.

```bash
src="${LINTEL_SOURCE_ROOT:?set the trusted installed source root}"
repo="${LINTEL_REPO_ROOT:?set the working repository root}"
python="${LINTEL_PYTHON:-python3}"
"$python" "$src/bin/li-review-evidence.py" prepare --repo "$repo" \
  --request "${review_request:?set request JSON}" > "${review_context:?set context output}"
```

Read the resulting context and every selected changed input, including dirty and
untracked files. `base...HEAD` alone is not that scope. `purpose: verification_only`
must come from approved acceptance before execution; it permits no product change,
not fabricated filenames to satisfy an implementation task.

## Record observed decisions, not intended outcomes

A version-2 review has `skill`, exact `status` (`pass`, `fail`, `unverified`, `error`),
timezone-bearing `timestamp`, `reason`, the prepared `context`, `reviewer`
(`id`, `context`), `provenance: declared`, `controls`, `coverage` and `evidence`.
`coverage` maps **every** selected leaf to all the context's required-control IDs:
for example `{"A1":["spec","quality","tests"]}` for the request above.
Required IDs must be present and mandatory.
Each leaf needs verified mandatory
acceptance, not an aggregate score or another leaf's unexplained result.

Each control has `id`, `kind` (`check`, `tests`, `browser`, `contrast`, `policy`),
`requirement` (`mandatory`, `advisory`), `applicability` (`applicable`,
`not_applicable`, `unknown`), exact `status`, `reason`, `policy`, `evidence` (local
file references) and `observation`. Policy fields are `source`, `version`,
`applicability` (grounded scope rationale), `jurisdiction`, `actor`, `effective_date`;
the last three may be null for non-regulatory checks. Regulatory checks require
them. Missing evidence/source/version remains unverified.

- Tests record `command`, `executed`, `failed`, `skipped`, `exit_code`. Zero tests,
  unknown counts or skipped required checks are not a verified pass.
- Browser checks record the actual `tool`, `executed: true` and observed `states`;
  static source inspection is not browser evidence.
- Contrast records measured `ratio` and `text_size` (`normal` or `large`).
  Normal 3.5:1 fails WCAG AA regardless of advisory points.
- `advisory_score` is optional and never changes mandatory clearance.

`evidence` binds each control's supporting files as `{path, sha256}`. The
`evidence_manifest(repo, controls)` API builds it without executing content.
Append failed/error/unverified decisions too; do not discard them to retain a PASS.

```bash
"$python" "$src/bin/li-review-evidence.py" validate --record "${review_record:?set decision JSON}"
bash "$src/bin/li-review-log" --file "$review_record"
```

Validation establishes structure, not independence or permission. Reviewers report
findings; implementers repair them. A repair requires a new context and affected
review/QA, not editing a previous verdict to pass.

## Corroboration and strict consumption

Different actor strings and a matching digest are not authentication. The trusted
coordinator supplies host-observed or human-attested corroboration separately:

```json
{
  "schema_version": 1,
  "kind": "host",
  "source": "<actual host observation authority>",
  "reference": "<actual invocation receipt>",
  "record_digest": "<content_digest of the complete review object>",
  "attempt_id": "<same attempt>",
  "builder": {"id": "<same builder>", "context": "<same builder invocation>"},
  "reviewer": {"id": "<same reviewer>", "context": "<different reviewer invocation>"}
}
```

Use `kind: human` for explicit independent manual-review attestation. Availability
of a delegation tool is not an invocation receipt. Never synthesize corroboration
from session bindings or a self-review. The verifier checks consistency; the caller
owns the trust of the supplied host/human evidence. No signature or authenticated
identity is claimed. Required independence without corroboration stays blocked.
Mechanical self-review must be explicitly selected in the authorized context with
`independence_required: false`; it is never labeled independent.

```bash
bash "$src/bin/li-review-read" --skill "${review_skill:?set actual review skill}" \
  --expected "$review_context" --corroboration "${corroboration:?set actual receipt}" --gate-json
```

The reader structurally selects the **latest applicable decision in append order**
before evaluating status, attempt, acceptance, freshness or snapshot. Active
decisions are validated before filtering. Malformed/uncorrelatable records remain
ordered non-clearing candidates, not unrelated records or permanent global errors.
Only validated unrelated scopes can be ignored. A later malformed/rejecting relevant
candidate revokes earlier clearance; a newer valid applicable v2 decision can
supersede older obsolete/invalid evidence after actual review. An unrelated valid
decision cannot erase that blocker. Explicit valid historical imports are archives,
not new decisions. `--json` remains raw history inspection.

V1 records retain their historical shape and are never auto-upgraded. To migrate,
prepare a v2 context with accepted QA obligations, obtain independent review again,
and append the new bound v2 decision. Do not rewrite old history or change version
numbers on old evidence. The later v2 decision can clear without old entries
poisoning the log forever. Legacy writers still need explicit commits and exact
statuses, but legacy/v1 results and v1 QA cannot grant strict v2 clearance.
Optional `--days N` adds a maximum age, not a replacement for content identity.

## Unmapped inspection

Ad-hoc code review and read-only QA do not need a work map or a duplicate backlog.
Capture selected content, read it or run the actual tests without fixes, and feed
the observed controls plus `required_policy` to `inspect`. For example:

```bash
"$python" "$src/bin/li-review-evidence.py" snapshot --repo "$repo" --base HEAD \
  --select "${inspection_selection:?set a literal file or directory}" \
  > "${inspection_snapshot:?set output outside selected inputs}"
# Read the selected content or run the actual test command; retain its real output.
"$python" "$src/bin/li-review-evidence.py" inspect --repo "$repo" \
  --snapshot "$inspection_snapshot" --input "${control_input:?set observed controls}"
```

The JSON result binds the snapshot and evidence, evaluates mandatory/advisory
outcomes, and explicitly declares `purpose: inspection` and
`release_clearance: false`. It provides useful findings without creating an
initiative. Changed selected inputs reject reuse. Exit 0 means the observed
inspection controls have no mandatory blocker, not permission to ship. Strict
SHIP still needs mapped authority, full leaf coverage and corroborated review;
neither this inspection envelope nor an unmapped review can replace it.

## Read-only QA and SHIP

Run the applicable required validation without fixes. For executable tests, persist
the real repository command/output and actual counts. Build `qa_inputs` containing
`{"controls":[<mandatory validation controls>]}`. An approved docs-only scope may
use an observed document/link/example check plus grounded tests N/A. At least one
mandatory validation must actually apply; exemptions or advisory checks alone do
not establish QA. The observations must match the prepared `qa_requirements`
exactly; do not choose obligations from submitted results. Zero/failed/skipped
applicable required tests remain blocked. The emitted QA record is v2 and binds
the complete v2 context digest.
Unknown/unavailable coverage stays open. The helpers below consume evidence; they
do not run tests, invoke browsers, make commits, push, deploy or authorize delivery.

```bash
"$python" "$src/bin/li-review-evidence.py" qa --repo "$repo" --expected "$review_context" \
  --input "${qa_inputs:?set observed QA input}" > "${qa_record:?set QA output}"
"$python" "$src/bin/li-review-evidence.py" ship --repo "$repo" --skill "$review_skill" \
  --expected "$review_context" --corroboration "$corroboration" --qa "$qa_record"
```

SHIP calls the actual audit reader and verifies QA against the same immutable
context. Exit 0 permits continuing the otherwise authorized workflow; exit 3 blocks.
Standalone `verify --repo ... --record ... --expected ... --corroboration ...` is
useful for an attributable lane artifact, but does **not** establish latest-log
precedence. Log-backed delivery always consumes the reader.

Unchanged selected inputs may reuse evidence, including across unrelated commits.
Changing selected index/HEAD/working content, relevant acceptance, evidence files,
attempt or profile invalidates it. A separate review-metadata commit is not a product
change; staging or committing reviewed dirty product content changes its bound
states and requires a newly verified context. Time alone never establishes reuse.
