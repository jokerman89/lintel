# Swarming work

Swarming is Lintel's opt-in execution profile for an approved plan whose work can be divided into
dependency-independent ownership domains. One coordinator dispatches bounded package lanes, workers
return attributable changes and per-leaf evidence, and substantive packages receive independent
review before integration. Explicitly mechanical packages may use coordinator review under
ADR-0026. The ordinary REVIEW phase then checks the reconciled tree. ADR-0027 retains the original
Swarming decision and its reconciliation with that hybrid model.

Swarming changes how PLAN, BUILD and REVIEW execute. It does not add a cycle phase, replace the
authoritative task list, grant new permissions, or run a background scheduler.

## Decide whether to swarm

Use a swarm when all of these are true:

- The work map is approved and contains at least two domains that can become ready independently.
- Each worker can receive a bounded card with explicit acceptance checks.
- Writer ownership can be expressed as non-overlapping repository-relative paths.
- Concurrent writers can produce attributable changes in separate worktrees, patches, or an
  equivalent host-enforced scoped sandbox. Otherwise, the same swarm may run sequentially.
- One coordinator can own shared state, generated outputs, commits and integration.

Stay with ordinary sequential BUILD when one shared file or reducer dominates, the task boundaries
are still uncertain, or the overhead of briefs and lane reviews is larger than the work. Swarming is
never inferred from task count; the operator opts in during PLAN or invokes `/li:swarm init` for an
approved work map.

## The committed contract

A swarm adds one coordination directory beside the existing cold-executor trio:

```text
.claude/plans/<initiative>/
├── work.json
├── spec.md
├── plan.md
├── prompt.md
└── swarm/
    ├── coordination.json
    ├── charter.md
    ├── briefs/
    │   └── <card-id>.md
    ├── reports/
    │   └── <card-id>.md
    └── reviews/
        └── <card-id>.md
```

`work.json` keeps schema version 1 and adds `execution_mode: "swarm"` plus a repository-relative
`coordination` pointer. The mapped `tasks` artifact remains the only authority for card text,
dependencies, status and acceptance criteria. Package membership stays in the mapped plan's
`Package ID` / `Leaf IDs (dependency order)` table. The retained coordination `task_id` field names
that package; ungrouped tasks remain singletons. Numeric/phased/tree IDs (`1.1.a`), flat task tables,
checkboxes and Spec Kit IDs remain unchanged. Coordination adds topology, not another backlog.

| Artifact | Authority | Writer |
|---|---|---|
| mapped `tasks` artifact | Cards, dependencies, status and acceptance | Coordinator |
| `work.json` | Artifact mapping and explicit swarm opt-in | Coordinator |
| `coordination.json` | Waves, roles, write scopes, isolation and evidence pointers | Coordinator |
| `charter.md` | Ownership, fan-out, fan-in and recovery rules | Coordinator |
| `briefs/<card>.md` | Card-specific startup, scope, inputs and checks | Coordinator |
| lane-owned paths | The implementation or documentation for one card | Assigned worker |
| `reports/<card>.md` | Changed paths, checks, findings and limitations | Assigned worker |
| `reviews/<card>.md` | Independent specification and quality verdict | Assigned reviewer |
| shared ledgers, reducers, commits and integration | Reconciled initiative state | Coordinator only |

A worker may write only its declared `write_scope` plus its own report. A reviewer writes only that
lane's review. Generated catalogs, synchronized instruction blocks and other fan-in reducers stay
coordinator-owned even when a worker edits their canonical sources.
Declare those project outputs in `coordinator_paths`; protection covers scopes and handoff artifacts,
including aliases and parent directories. Existing hard-linked files share physical ownership even
when their resolved names differ, including links inside directory scopes. Identity inspection errors
block rather than granting a scope. Reports cannot claim a mapped plan as their own output.

An optional package `Review` column selects `substantive` (default) or `mechanical`; optional
`Result` selects `change` or `verification-only`. Each member leaf must exist exactly once, keep
its dependencies/acceptance and have passing evidence before the package closes. No product edit
is invented for an explicitly verification-only package.

Explicit `Owner / edit boundary` values contain literal repository paths, for example
`builder; README.md, src`. The optional owner precedes the first semicolon; remaining paths are
comma/semicolon separated. Backticks quote individual paths containing spaces. Root files and
directories, new paths and a single trailing directory slash are supported. Empty or uninterpretable
limits, globs and placeholders fail validation rather than disappearing into an unrestricted lane.
An older package without this column still uses its required lane write scope.

## Start and inspect a swarm

1. Complete PLAN and approve the mapped cards.
2. Invoke `/li:swarm init <initiative>` and review the generated charter, topology and briefs.
3. Confirm that same-wave scopes do not overlap and that every concurrent writer has an accepted
   isolation backend.
4. Validate both the work map and the coordination contract before dispatch.

The helpers are read-only. Run them from a trusted Lintel installation, kept separate from the
repository whose artifacts they inspect:

```bash
export LINTEL_SOURCE_ROOT=/trusted/path/to/lintel
repo=/path/to/working-repository
work_map=.claude/plans/example/work.json
coord=.claude/plans/example/swarm/coordination.json

python3 "$LINTEL_SOURCE_ROOT/bin/li-work-artifacts.py" \
  --repo "$repo" --map "$work_map"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" validate \
  --repo "$repo" --coord "$coord"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" status \
  --repo "$repo" --coord "$coord"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" wave \
  --repo "$repo" --coord "$coord"
```

Do not execute scripts named by a work artifact or use the target repository as an implicit tool
source. If the adapter cannot provide a trusted `LINTEL_SOURCE_ROOT`, stop with `NEEDS_CONTEXT`.

`status` derives lane state from the declared report/review and fresh shared evidence in the repository tree.
The coordinator still uses committed integration history as completion truth. `wave` returns the earliest
incomplete wave allowed by topology and evidence, bounded by `max_parallel`. That output is only a
candidate frontier: known leaf/package prerequisites are filtered, and unresolved prerequisites
appear under `blocked_by`. The coordinator still inspects semantic requirements and actual host
tools. `--host-capability sequenced` or `none` caps each dispatch selection at one. That flag reports
a caller-declared capability, not verified execution or a spawning API.

## Execute and integrate

For every candidate lane, the coordinator follows the same sequence:

1. Reconcile `wave` with the task card's authoritative dependencies and completion evidence.
2. Adapt the complete lane brief with `li-swarm.py brief --task <package>` and pass its JSON payload
   to the explicit Brief Forge gate. Work/package/leaf/scope/source references accompany the entire
   original Markdown as data. JSON/Markdown needs no third-party package; legacy YAML is optional.
   Disabled/bypassed forging is explicit, not success. Missing required evaluation or audit blocks.
3. Dispatch a fresh worker with the brief, accepted isolation and exact write scope.
4. Require the worker to perform the Lintel startup, change only owned paths, run focused checks and
   write the structured lane report.
5. Build a changed-path list from that lane's isolated change set and run `check-scope`:

   ```bash
   python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" check-scope \
     --repo "$repo" --coord "$coord" --task BC2 --paths-file changed-paths.txt
   ```

6. Capture the attempt/result with `snapshot`, then export `review-input`. Assign a real independent
   reviewer for substantive specification and quality review, covering every leaf. Afterwards,
   run `check-scope --actor reviewer` on the actual reviewer change set, not the worker's diff.
7. Integrate passing lanes serially in deterministic task order and run focused checks after each
   integration. Regenerate coordinator-owned outputs only after their source lanes have fanned in.
8. Re-run `status` and `wave` until no eligible lane remains.

Parallel read-only research is safe when its outputs are separate. Parallel writing requires both
non-overlapping declared scopes and per-lane attribution; a union diff in one shared checkout cannot
prove which worker changed a path.

## Host capability and honest degradation

Client metadata is a hint; actual callable tools, isolation and permissions determine execution:

| Host tier | Execution | Evidence that may be claimed |
|---|---|---|
| `native` | Fan out ready writers up to the operator and topology cap only when every lane has attributable isolation; otherwise sequence them. | Concurrency and independent review only when the host actually produced those records. |
| `sequenced` | Replay the same lane briefs one at a time, preserving scopes, reports, reviews and gates. | Delegated work and review may be reported, but not concurrent writers. |
| `none` | The main agent executes packages serially, or exports `brief` and `review-input` for manual workers/reviewers. | Do not label self-review as independent. A substantive package stays open until a real reviewer acts. |

Hooks are a separate capability. Lintel's Claude Code hooks do not activate on other clients, and
swarming does not emulate them. On hosts without compatible registered hooks, agents must read the
startup rules and state explicitly. See [multi-CLI support](../multi-cli.md) for the current adapter
matrix.

## Recover without guessing

Committed artifacts and attributable changes are the recovery source; chat history and worker
process labels are not.

| Situation | Recovery action |
|---|---|
| Worker process or local runtime state disappeared | Re-run `validate` and `status`. Preserve an attributable worktree or patch, scope-check it, then finish its report/review or replay the same brief. |
| Partial work has no lane attribution | Do not discard or integrate it silently. Quarantine the changes, report the discrepancy, and sequence a fresh attempt after the coordinator accounts for the partial work. |
| Worker changed an unowned path | Freeze the affected ownership domains. Narrow or reassign the scope, reconcile the isolated patch, or re-run the lane; do not hide the breach in fan-in. |
| Lane review failed | Return findings to the same card. Later dependent waves remain blocked until a distinct reviewer records passing evidence. |
| Two passing lanes conflict during integration | Stop integration, preserve both changes, and return to PLAN if ownership was wrong. The coordinator resolves only with an explicit, reviewed reconciliation. |
| Independent reviewer is unavailable | Record the host limitation and leave the lane open. A self-review can inform rework but cannot manufacture independent PASS evidence. |

Independent lanes may continue while a blocked lane's ownership domain is isolated and no dependency
requires it.

`resume` reconstructs status and the candidate frontier without private runtime state or another
initiative's timestamps. Historical v1 reports remain untouched history; they never automatically
become current content-bound clearance.

## Result identity

The coordinator captures a result without authoring a verdict:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" snapshot \
  --repo "$repo" --coord "$coord" --task P1 --attempt P1-attempt-1 \
  --base "${package_base:?set the recorded package base}" \
  --head "${product_commit:?set the verified product commit}"
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" review-input \
  --repo "$repo" --coord "$coord" --task P1
```

Bind the v2 report to the selected work map, package/leaf IDs, acceptance digest, attempt ID and
result digest. Every leaf has explicit checks. Bind review to those identities and the exact report
digest. Changed requirements, new/modified scoped files, report edits or a later attempt invalidate
the prior binding. Checkbox-only completion preserves unchanged acceptance.

Git snapshots verify real base/head objects and changed paths, current scoped files and non-ignored
untracked additions. Ignored build artifacts do not masquerade as delivered source. Text hashes
normalize CRLF to LF for UTF-8 files; binary bytes are exact and Git IDs identify exact committed
objects. Result entries also bind type and Git mode, using index metadata for the executable bit
where `core.filemode=false`. Safe scoped symlinks (`120000`) retain their exact link target and
digest as data without reading target contents. Under `core.symlinks=false`, a file containing that
exact target text represents the same Git link object. Changed type/mode/target invalidates old
evidence; an unchanged reviewed link remains valid. Outside-root targets are refused, metadata
equality never permits following a target, and submodules (`160000`) retain their existing exclusion.
File-only snapshots verify present content but cannot prove a base diff, host isolation or identity.
Describe the level observed rather than converting a path string into an invented product change.

These are the retained **local** snapshot semantics. `inspect` and `inspect --check-complete`
expose local observations without shared acceptance; both return `release_clearance: false`.
P05's selected raw base/HEAD/index/worktree snapshot is separate and remains authoritative for
shared review. Never substitute a normalized local digest for its raw content identity.

## Shared provider evidence

Each lane may declare `shared_evidence` with `context`, `review`, `qa`, `corroboration`,
`domain_request` and `review_skill`. All values except the skill are literal JSON-file pointers;
corroboration and domain request may be null when genuinely inapplicable. Context, QA,
corroboration and domain request are coordinator-owned; canonical shared review JSON is
reviewer-owned under `.claude/runtime/reviews/`. No pointer can acquire mapped authority,
another artifact, a reducer or an aliased physical file.
All shared JSON slots use safe ordinary ancestors; an existing leaf must be a regular single-link
file, while a missing planned leaf is allowed only through those safe ancestors. Symlink/reparse,
hardlink, directory/special and uninspectable metadata paths fail before ownership is granted.
The same guard checks the actual reviewer filename and consumption: an alternate name for the
same file is not its assigned slot. Coordinator metadata references do not grant lane ownership
of state/audit/jobs. Supported legacy product symlinks remain unaffected by this metadata rule.

The caller creates actual provider artifacts, not Swarm lookalikes. Before observations it fixes
P05 v2 work/QA obligations and the explicit P07 v1 reference. After reports/results exist it
externally prepares the final P05 context, retaining original inputs/base and adding actual
outputs/evidence. That context binds the complete coordination/charter/brief and all product scopes,
plus the raw local report/review. The final context itself is outside the content it hashes.
The canonical P05 decision then binds that context and complete per-leaf/control coverage.
A P05 selection of an actual parent directory covers the whole descendant lane scope, including
future files; the consumer does not force a redundant exact child selector. Missing/partial child
coverage, siblings, misleading textual prefixes and file-as-parent claims remain invalid.
A parent deleted by the reviewed change remains covered when P05 binds its former tracked
descendants; the consumer does not require recreating the directory or replacing valid evidence.

`status`, `wave`, `resume` and `verify` consume one common gate: current P07 reference and exact
required policy, actual P05 review validation, the existing log-backed latest-review reader, and
same-context QA. They require explicit `--profile-home`, `--profile-packs`, `--profile-pointer`
and optional `--profile-context-file`; they never bootstrap/rebind missing pins. Local-only results
become `awaiting_shared_evidence`, not a synthetic independently reviewed `complete`.

When selected, P09's domain verifier re-reads every expected checkpoint/result/artifact. Its exact
P05 QA is used, but its non-clearing/review-not-evaluated result is not promoted into independent
review. No-domain packages use regular P05 QA. Verification-only packages need no imaginary edit;
their selected product states must actually be unchanged. A later rejecting/malformed review,
missing/changed obligation, profile drift, absent domain result or changed attempt blocks the same
gate in every command. Synthetic actor names are never independent corroboration.

Staging/committing selected data and Git fan-in can change a P05 context. Reprepare and obtain actual
affected review rather than treating a prior lane decision as integration acceptance. The reader's
latest-log precedence is not replaced by standalone artifact verification. Safe link and platform
observations remain data; neither snapshot grants permission to dereference/execute a target.

## Close a swarm

Run the deterministic evidence gate only after every lane report and review is present:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" verify \
  --repo "$repo" --coord "$coord" \
  --profile-home "${profile_home:?explicit approved home}" \
  --profile-packs "${profile_packs:?explicit approved store}" \
  --profile-pointer "${profile_pointer:?explicit approved pointer}"
```

A passing `verify` result checks local observations and the selected shared evidence. The P05
corroboration verifier checks the consistency of separately supplied host/human evidence; the caller
still owns its trust. Distinct strings alone never establish independence. The
coordinator must still confirm that every passing lane was integrated into the declared integration
branch, run focused integration checks, and hand the reconciled tree to ordinary REVIEW. REVIEW
repeats specification, quality and active-pack compliance across the full diff. Lane reviews never
replace that final integrated gate.

P05/P07/P09 consumption uses accepted providers in this unit; newer P08 selected-work/resume
binding is still the explicitly open A22.7 follow-up. No unaccepted lifecycle helper is imported.
The current consumer is not a claim that final Universal integration/client acceptance is complete.

Swarm completion does not authorize a push, deployment, production change or other external
mutation. Those actions retain exactly the same approval and compliance requirements they would have
under sequential BUILD.

## Non-goals

Swarming does not introduce a daemon, distributed queue, database, generic agent runtime, automatic
merge, universal hook translation or required persistent agent memory. Its durable contract is
Markdown plus JSON, and its mechanical gates are local, read-only Python.

## See also

- [The cycle](../the-cycle.md) — where the profile enters PLAN, BUILD and REVIEW
- [Multi-CLI support](../multi-cli.md) — native, sequenced and no-subagent behavior
- [Brief Forge](brief-forge.md) — envelope construction and evaluator policy
- [Architecture](../architecture.md) — spine, pack and coordinator ownership
