# Domain data handoff

This is the shared consumer procedure for TA/DA/SC/DH/TQ and their composition.
The agent performs the domain work through actual host operations; the **data-core**
only records and verifies evidence. Neither replaces the selected work-map reader,
lifecycle ledger, task/package parser or host permission system. Installed-resource
closure and whole-P08 orchestration acceptance are separate from these provider calls.

## One contract and two evidence boundaries

`lib/domain-result-schema.json` defines request, started-checkpoint and result
wrappers. `lib/domain_result.py` is their sole producer/consumer implementation;
`bin/li-domain-result.py` is the thin CLI. Shared objects reference P05
`review-schema.json` definitions and use its public validators. Profile reference
validation and live resolution remain with P07. No new interpretation of tasks,
policy, QA obligations, acceptance hashes or review-log precedence is introduced.

All domain outputs contain `release_clearance: false`. `validate` establishes
syntax/relationships only. `record` publishes one owned data file and checks
readback; it does not verify a live profile, run a check, authenticate an actor,
authorize execution or accept work. Their receipts explicitly state
`verification: not_performed`.

`verify` and `summary` re-read the caller's request and **every expected** checkpoint
and result, verify the caller-selected external P05 context, the current P07
reference/policy, unchanged obligation inventory and actual evidence bytes.
`summary` calls the same fresh verifier; no stored `verified: true`, previous CLI
output or role name is input authority. Unknown fields are rejected in the wrappers.
Neither command evaluates independent review; `review: not_evaluated` stays explicit.

The resulting `ok` means no integrity or mandatory-observation blocker in this
data inspection, not permission to ship. P05's aggregate status can still be `fail`
for an advisory failure with `blocked: false`; those advisories remain visible.
Independent specification/quality acceptance and the latest applicable review are
still the existing P05 reader's responsibility.

## Request construction is a caller responsibility

The caller supplies a real accepted P05 `prepare` result as `input_context`.
It contains the original `bind_work` object, input snapshot, attempt/builder,
required policy, profile reference, required-control IDs and immutable
`qa_requirements`. This is historical **input** identity, not a snapshot of outputs
that do not exist yet. The data core requires a mapped context and an explicitly
pinned P07 reference, including a neutral pin when no company policy is required.
Unmapped ad-hoc advice can use P05's existing `inspect` path; do not invent a map.

The other request fields are:

| Field | Meaning |
|---|---|
| `schema_version`, `kind` | Domain wrapper version 1 and `domain-request`; P05 inside remains v2, P07 remains v1 |
| `operation_id`, `iteration` | Explicit filesystem-safe operation ID and iteration 1-9999; not a generated host-session identity |
| `domains` | Explicit subset of ta/da/sc/dh/tq, each with unique expected checkpoint IDs |
| Checkpoint `receiver` | Explicit nonblank role and role-specific mode, for example planning-only, artifact-only, authorized-execution or review; equality is checked, capability/permission is not inferred |
| Checkpoint `control_ids` | Assign every initial P05 QA obligation exactly once across the request; no omitted or duplicated obligation |
| Checkpoint `artifacts` | Explicit literal output/evidence-artifact paths; never a command or glob |
| Checkpoint `start`, `result` | Each holds an exact `path` and the **original** `expected_state` from P03, captured before the operation |
| `advisory_preferences` | Explicit JSON invocation advice, bound with the request, never promoted to mandatory policy |
| `release_clearance` | Always false |

Publication paths must be under
`.claude/runtime/state/domains/<operation_id>/iNNNN/`, with safe `.json` filenames.
For example, `ta/01-start.json` and `ta/01-result.json`. The checkpoint's semantic ID
stays in data; a timestamp need not become a colon-bearing filename. Portable path
validation rejects traversal, reserved device names, trailing dot/space, invalid
Windows characters, aliases and Git metadata. Requests, metadata and artifacts
cannot collide. Domain data directories are not a new phase/task ledger.

`expected_state` is either JSON null for original absence or P03's exact
`{sha256, size, mode}`. An original state of null does **not** mean "overwrite whatever
exists now". The `record` call also requires that same state explicitly. Supplying a
new state read after an intervening edit cannot match the pinned request and is
rejected. These values record ownership evidence, not a grant of permission.

The data core does not verify task existence/package membership by inventing a parser.
That remains the released work-reader/caller's responsibility. Its P05 work binding
does verify current accepted source identity. No P08 source is imported or imitated.

## Started checkpoint and result

A `domain-checkpoint` identifies the exact request file/digest, domain/checkpoint,
receiver and producer `{id, context}`. Provenance is `declared`, not authenticated.
The authorized caller records it before the domain action. A `domain-result` binds
the actual start file/digest and the same request, producer and receiver.

Results retain P05 `controls` and their exact `evidenceFiles` manifest; every immutable
QA requirement field must match the request. Artifact references use the same
`{path, sha256}` file identity. Decisions cite an original requirement, rationale
and a declared artifact. Limitations and `next: {owner, action}` are required; a
next action is inert text, never a command to execute. Scores are optional advice.

Record a failure/error/unverified observation honestly. Missing artifacts can be
recorded as an incomplete result but cannot pass fresh verification. A result cannot
silently remove an expected artifact, drop/retype/downgrade an obligation, substitute
N/A, or use another checkpoint's start. A started checkpoint without its result
remains incomplete. Missing expected domains/checkpoints are not skipped into a
high-scoring aggregate.

Migrator retains **artifact-only and authorized-execution** modes. ReleaseEngineer
retains **planning-only and authorized execution** value. The caller selects the actual
mode and obtains its real target/action authorization. The data core records the
declared mode without performing it; a syntactically valid execution-mode record
does not establish that execution happened. Reviewers remain separate from implementers.

## Noncircular preparation and consumption

1. Resolve/bind P07 through its existing producer with explicit source, target and
   approved profile locations. Build the initial P05 prepared context from the
   original accepted work/inputs and QA inventory. Fix the request and original
   publication preimages before collecting observations.
2. Record start data, perform only the actually authorized operation outside this
   helper, persist its artifacts/logs, then record the observed result. The helper's
   publication scope is only the request's exact metadata slot. It never writes the
   mapped task source, ledger, source artifacts or evidence on the caller's behalf.
3. **After outputs exist**, use P05 `prepare` again with the same work, attempt,
   builder, profile, policy, purpose, required controls and QA inventory. Retain the
   original base and input selections, and add the request, starts, results,
   artifacts and evidence files. Their raw bytes must all be in the final snapshot.
4. Keep that final context outside its selected content. Do not embed it or its
   digest inside the handoff it hashes. The data core takes it as an external,
   caller-selected verification argument, not from the result being judged.
5. Verify with the explicit live P07 configuration. Verification checks that the
   target/source match, the full profile reference still resolves and the produced
   `required_policy` equals the context. Drift, lost pin, wrong target/generation and
   required-load failure do not bootstrap, rebind or become neutral.
6. A complete verification returns a real P05 v2 `qa` envelope over the unchanged
   inventory and selected context. It has been checked through `verify_qa`. Feed
   the same observations to the existing QA procedure as needed; this adds no second
   review/clearance representation. Request independent review through the actual
   existing P05 protocol; a later rejection still revokes that outer acceptance.

Example CLI calls, after the named files and authorized profile paths exist:

```bash
src="${LINTEL_SOURCE_ROOT:?trusted source required}"
repo="${LINTEL_REPO_ROOT:?explicit target required}"
python="${LINTEL_PYTHON:?Python 3.9+ executable required}"
"$python" "$src/bin/li-domain-result.py" validate --repo "$repo" \
  --file domain-request.json
"$python" "$src/bin/li-domain-result.py" record --repo "$repo" \
  --request domain-request.json --file .claude/runtime/meta/result-input.json \
  --output .claude/runtime/state/domains/example/i0001/ta/01-result.json \
  --expected-state .claude/runtime/meta/original-state.json
"$python" "$src/bin/li-domain-result.py" summary --repo "$repo" \
  --request domain-request.json --expected .claude/runtime/meta/final-context.json \
  --profile-home "${profile_home:?explicit approved location}" \
  --profile-packs "${profile_packs:?explicit approved store}" \
  --profile-pointer "${profile_pointer:?explicit approved pointer}"
```

`original-state.json` contains exactly `{"state": null}` or
`{"state": {"sha256": "<original digest>", "size": 123, "mode": 384}}`,
with the actual original P03 values rather than these illustrative numbers.
It is not a place to reconstruct overwrite permission. `verify` accepts the same
arguments as `summary`; optional `--profile-context-file` preserves an explicitly
selected P07 context file. All JSON input paths are literal repository-relative
paths. Profile locations are explicit CLI paths; no personal home is inferred.

Exit 0 means the requested syntax/publication operation succeeded, or fresh data
inspection has no blocker. Exit 2 reports invalid invocation/data/publication/source;
exit 3 reports blocked fresh verification. Read the operation and verification
category, not just the exit code. Publication failure preserves state for inspection;
there is no automatic rollback or replay.

## Limits and verification

The helper consumes JSON only (2 MiB per data record, 16 MiB per artifact/evidence
file). It uses P05's strict duplicate/nonfinite rejection, delegates shared field
validation rather than copying definitions, and interprets only the domain schema's
small shape subset. P03 owns rooted no-link reads and expected-preimage atomic writes.
Writes assume one serialized owner; a preimage check is not a distributed lock or
a filesystem race-proof authorization mechanism.

The helper verifies file identity, obligation consistency and declared observations.
It cannot prove that an actor is independent, a log is truthful, a domain decision is
correct, or an external action took place. Those need actual host/human evidence
and independent review. It never executes evidence content, next actions, preference
values or a selected target's helper.

`tests/integration/domain-result-handoff.sh` exercises actual accepted P03/P05/P07
producers, CLI publication, fresh verification and QA/review consumers with synthetic
actors and data. Copied-source cases are not installed-adapter acceptance. The separate twelve documentary/illustrative role checks retain their narrower label.
Provider/consumer tests and any native demonstrations must report their own actual
scope; none establishes installed-resource closure or P11/P12 consumer acceptance.

## Module caller procedure

The module's checkpoint table defines method order, not a new task backlog. Read the
canonical role body from the trusted source before dispatch; preserve its inputs,
mode and returned output. The caller alone persists shared request/result metadata.
Do not execute slash invocations as shell commands or assume a model/agent is registered
because a file exists. A role read into a generic native task is a **source-guided**
invocation; identify the actual tool/context and retain that distinction.

### Select original work and live policy

Keep SENSE -> SCOPE -> DEFINE -> DISCOVER -> PLAN -> BUILD -> REVIEW -> SHIP -> CAPTURE.
These domain checkpoints are inside the selected phase, not extra lifecycle phases.
Use the already selected map/cycle. Start a new cycle only when actually requested
through the existing lifecycle, not on every module call. Resume is a utility.

```bash
# lintel-module-context
set -euo pipefail
: "${LINTEL_SOURCE_ROOT:?trusted source required}"
: "${LINTEL_REPO_ROOT:?explicit target required}"
: "${LINTEL_WORK_MAP:?select the original map}"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
if [ -n "${LINTEL_CYCLE_ID:-}" ]; then
  workflow_resume "$LINTEL_CYCLE_ID" "$LINTEL_WORK_MAP"
else
  workflow_inspect "$LINTEL_WORK_MAP"
fi
```

P07 must already be bound by the normal authorized bootstrap; this procedure never
creates a replacement pin on resume. Use `verify_profile_context`, then typed
`resolve_pack_field_json`/`profile_field_provenance` for applicable fields. Missing
required policy blocks before dispatch. Missing optional advice stays absent;
do not fill it with an invented cloud, framework, retention period or numeric target.
Effective pack identity is **not** personal `profile.yaml`. Accept explicit advisory
invocation values and selected repository-local evidence, not automatic home reads.

Create a P05 prepare request using original package/leaf IDs and the existing
acceptance sources. Before preparing, run the following read-only admission
procedure (arguments: trusted source, target, repository-relative prepare-input
file, optional explicit linked-handoff acceptance path). It calls the actual
released reader; it does not parse tasks again or grant execution authority.

```python
# lintel-module-select
from pathlib import Path
import runpy
import sys

source, repo = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(source / "lib"))
from context_safety import checked_root, read_owned
from review_contract import load_json, canonical_json

try:
    repo = checked_root(repo)
    request = load_json(read_owned(repo, sys.argv[3], 2 * 1024 * 1024)[0].decode("utf-8"))
    reader = runpy.run_path(str(source / "bin/li-work-artifacts.py"))
    work = reader["work_context"](
        repo, Path(request["work_map"]), package_id=request["package_id"],
        leaf_ids=request["leaf_ids"], acceptance_paths=request["acceptance_paths"],
    )
    if work["status"] not in ("APPROVED", "COMPLETE"):
        raise ValueError("Selected work is not approved")
    package = work["packages"].get(request["package_id"])
    if package is not None:
        if not set(request["leaf_ids"]) <= set(package["leaf_ids"]):
            raise ValueError("Selected leaves do not belong to this original package")
    else:
        authority = sys.argv[4] if len(sys.argv) > 4 else ""
        if not authority or authority not in request["acceptance_paths"]:
            raise ValueError("Package needs explicit original linked-handoff acceptance")
        if not read_owned(repo, authority, 2 * 1024 * 1024)[0].strip():
            raise ValueError("Linked package authority is empty")
    print(canonical_json(work))
except (OSError, ValueError, KeyError, TypeError) as error:
    print(f"NEEDS_CONTEXT [lintel/module]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

For a recognized package, check its original prerequisites **and their actual
acceptance evidence** before dispatch; source checkboxes alone are not verification.
An explicitly linked package/handoff keeps its original authority and membership
review with the caller; the code above only establishes that the declared source
exists and is bound. It does not infer membership from prose. Use singleton original
IDs for genuinely ungrouped work, not a renamed local task list. Read complete leaf
text from the returned original sources; malformed/unknown IDs stop, not disappear.

### Prepare and assign the work

Before dispatch, inspect the required canonical module files under the explicitly
trusted source. The following read-only guard takes the original expected domain
IDs as arguments; a same-named target file is not a fallback:

```bash
# lintel-module-discovery
set -euo pipefail
: "${LINTEL_SOURCE_ROOT:?trusted source required}"
[ "$#" -gt 0 ] || { echo 'NEEDS_CONTEXT: expected domains required' >&2; exit 2; }
for module in "$@"; do
  case "$module" in
    ta|da|sc|dh|tq) ;;
    *) echo "NEEDS_CONTEXT: unknown domain $module" >&2; exit 2 ;;
  esac
  [ -f "$LINTEL_SOURCE_ROOT/skills/$module/SKILL.md" ] || {
    echo "BLOCKED: required source module missing: $module" >&2
    exit 2
  }
done
```

Presence is not behavior, native registration or installed-consumer acceptance.
Read the actual method/role and its dependencies before invoking an available host
tool. Missing mandatory source resources block the affected operation.

Use the actual P05 `prepare` CLI on that request and retain its context outside the
selected input files. Its `work` must equal the reader's `binding`. The agent then
constructs the existing domain request from this context: expected domains and
checkpoint IDs, role-specific receiver mode, every predeclared QA obligation exactly
once, explicit artifact paths, and original publication states. Validate with the
data CLI before dispatch. Select all method/brief/policy evidence relevant to the task.
Budget/time preferences are advice, not evidence that the host can run a larger model.

For a full pass use the module's five checkpoints. A single capability has only its
applicable checkpoint/controls; do not silently escalate it into a full pass. A loop
is a newly authorized iteration against changed inputs, with the previous immutable
request/result paths linked in the selected handoff document, not a replaced verdict.

Use one owner for shared metadata. Each receiver gets the original requirement and
leaf IDs, current accepted inputs, verified profile reference/policy, exact read/write
scope, named role **mode**, expected output and observable checks. An implementer may
write only its scoped artifacts; a read-only specialist returns a report for the
caller to persist. Record the real host tool/context or disclose serial execution.
A required independent reviewer cannot be replaced by relabelling the implementer.

MigrationPlanner plans; Migrator gets artifact-only for migration-plan SQL drafts,
but a separately authorized migration invocation retains authorized-execution with
exact target/preconditions/recovery. ReleaseEngineer gets planning-only for DH/SC
pipeline/rollback/on-call work; authorized release execution is preserved separately.
The mode itself is never permission. The data contract does not execute either.

### Checkpoint publication and cold continuation

Record the start with `record` **before** the assigned work. After the real method and
checks, persist artifacts/logs, assemble result controls/evidence with actual output,
then record the result using the original expected state. Empty output, a skipped
required check or a missing browser is not a passing observation.

Keep an explicit handoff document in the selected work/artifact location: original
map and cycle ID, immutable request path, operation/iteration, initial/final context
paths, last observed checkpoint, next owner/action, pending review and known side
effects. These are references/observations, not copied task text or completion truth.
Use safe `i0001/01-start.json` names; a human-readable timestamp belongs inside data.
Readback publication before saying it succeeded. If persistence fails, stop and
preserve files; do not manufacture a success pointer in the main ledger.

On cold entry, re-read that explicit handoff and use the context procedure above.
Verify original map/profile/policy and re-read the request. Open its **literal**
start/result paths with a rooted reader: default search/glob can omit gitignored
`.claude/runtime/` files and cannot establish absence. A read/access/path error is
an unresolved observation, not a missing-file verdict; report the actual error.
The original task checkbox is not checkpoint status: it can correctly remain
unchecked while method results await independent review. Inspect each request slot
and its evidence rather than choosing the first unchecked original task.
For an incomplete attempt
the caller may prepare an external **inspection context over currently existing
files** and use `summary`; do not create a missing result merely so preparation passes.
Initial obligations and expected checkpoint list remain unchanged.

| Actual saved state | Next action, not automatic replay |
|---|---|
| No start and no result | Not started; run only after prerequisites/authority are still satisfied |
| Start present, result absent | **Missing result: do not replay** an action with unknown effects; reconcile recorded artifacts/actual receiver outcome first |
| Result present without matching start/request | Block; preserve orphan/mismatched evidence |
| Truncated/invalid result or publication conflict | Block and preserve; reconcile only owned state, never broad restore |
| Complete result with matching inputs | Reverify actual evidence/controls; remaining checkpoints stay expected |
| Relevant input, acceptance, profile or upstream artifact changed | New explicit attempt/iteration and affected review; never patch the old pass or silently rebind |

The caller names the first unmet checkpoint from the original ordered request and
reports its reason. A data inspector does not schedule the next action. An observed
artifact may be reconciled after interruption without repeating the domain action,
but only with attributable receiver/check evidence. Unknown production effects require
the approved recovery owner. Returning to a checkpoint is a decision step, not
resetting a checkout, restoring old data or applying an unverified down migration.

### Final verification and independent acceptance

After expected artifacts exist, externally prepare the final P05 context retaining
the original QA inventory and selecting request/start/result/artifact/evidence bytes.
Use fresh domain `verify`/`summary` and actual P05 `qa`; a mandatory failure blocks
dependent work regardless of scores. Domain `ok` does not satisfy independent review.
Obtain spec then quality from a separately attributable reviewer, record the actual
P05 review/corroboration, and consume `li-review-read` against that same context.
Never fabricate corroboration or normalize a later rejection away.

Only after those gates may the outer task owner update original task status or
phase metadata. A domain result may be linked from the current phase without
starting another phase. SHIP still uses its own actual reader/QA/authority checks;
successful engineering analysis does not publish, deploy, merge or send messages.
Optional audit/Brief Forge use must be explicit and actually observed; dormant
hooks stay dormant. A log write or complete shape is not an independent verdict.
