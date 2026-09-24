# Committed work map

`bin/li-work-artifacts.py` owns the version-1 map contract and validates it without executing
artifact content. SENSE/SCOPE, PLAN, BUILD, ANALYZE, budgeting, REVIEW, CAPTURE and RESUME
use these same fields. Paths are relative to
the working repository, never to the installed Lintel source. Keep one map per initiative at
`.claude/plans/<initiative>/work.json`, and link it explicitly from `.claude/plans/todo.md`.

```json
{
  "schema_version": 1,
  "workflow": "spec-kit",
  "status": "APPROVED",
  "spec": "specs/001-feature/spec.md",
  "plan": "specs/001-feature/plan.md",
  "tasks": "specs/001-feature/tasks.md",
  "prompt": ".claude/plans/001-feature/prompt.md",
  "constitution": ".specify/memory/constitution.md"
}
```

Swarming is an additive, explicit schema-version-1 extension:

```json
{
  "schema_version": 1,
  "workflow": "lintel",
  "status": "APPROVED",
  "spec": ".claude/plans/example/spec.md",
  "plan": ".claude/plans/example/plan.md",
  "tasks": ".claude/plans/example/plan.md",
  "prompt": ".claude/plans/example/prompt.md",
  "execution_mode": "swarm",
  "coordination": ".claude/plans/example/swarm/coordination.json"
}
```

`execution_mode` and `coordination` are optional but atomic: declare both or neither. Absence keeps
legacy sequential BUILD unchanged. The coordination document follows `lib/swarm-schema.json` and
owns only waves, roles, write scopes, isolation, and brief/report/review pointers. It never repeats
task text, dependencies, acceptance, checkbox state, or approval status from the mapped `tasks`
artifact. `/li:swarm` explains the lifecycle and host-aware degradation.

For Lintel-native work, `workflow` is `lintel` and `tasks` points to the same plan.md that
contains the build cards. `constitution` is optional and may be null. Status starts DRAFT;
record APPROVED only when the current operator authorization covers the plan's scope. A
committed status records a decision; it never grants tool permissions or new external authority.

The mapped `spec` owns requirements, `plan` owns the implementation design, `tasks` owns card
IDs/dependencies/checkboxes, and `prompt` owns the handoff. Spec Kit's technical plan.md does
not need Lintel-specific approval headings or duplicated task text. Optional Lintel plan/spec
companions are reference-only documents. On updates, change original tasks and verification
records, not a parallel copy.

Validate the selected map from the Lintel source root (or use its absolute helper path):

```bash
export LINTEL_SOURCE_ROOT=/path/to/installed/lintel
python3 "$LINTEL_SOURCE_ROOT/bin/li-work-artifacts.py" --repo /path/to/project --map .claude/plans/001-feature/work.json
```

Claude may use `CLAUDE_PLUGIN_ROOT` as the trusted fallback. Every other adapter must substitute or
export its known installed bundle path as `LINTEL_SOURCE_ROOT`; source-tree tests/self-checks export
it explicitly. If neither trusted root exists, return `NEEDS_CONTEXT`. Never use the working
repository as executable source merely because it is passed to `--repo`.

The helper requires all declared artifacts to exist inside the working repository. It does
not infer a feature, inspect personal history, select by timestamp, run shell commands from
a task or certify completed checkboxes. When swarm fields are present it imports the shared
`lib/swarm_contract.py` validator, so map and topology use one parser instead of divergent rules.
Readers must still inspect acceptance and integration evidence.

Swarm operations are read-only mechanical gates:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" validate --repo /path/to/project --coord .claude/plans/example/swarm/coordination.json
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" wave --repo /path/to/project --coord .claude/plans/example/swarm/coordination.json
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" status --repo /path/to/project --coord .claude/plans/example/swarm/coordination.json
python3 "$LINTEL_SOURCE_ROOT/bin/li-swarm.py" verify --repo /path/to/project --coord .claude/plans/example/swarm/coordination.json
```

`wave` returns the earliest evidence-aware ready frontier bounded by `max_parallel`. Workers may
change only their lane's `write_scope` plus their own report; reviewers may change only their own
review. The coordinator owns shared ledgers, reducers, commits, and serial integration. Concurrent
writers require disjoint scopes and attributable isolation; sequenced/no-subagent hosts replay the
same artifacts serially without claiming concurrency or independent work that did not occur.

RESUME chooses an operator-named map, then an unambiguous active map linked in the committed
todo/working-state. If multiple active maps remain, ask which initiative; do not choose the
newest file. A legacy committed plan without a map is valid: follow its explicit spec/handoff
links, confirm the task source and create a map within authorized scope. Reconstruct local runtime
bookkeeping only after this selection and verification; never invent missing evidence. For a swarm
map, recompute status/frontier from committed reports and reviews. Missing runtime attempts are
unfinished unless an attributable worktree or patch can be scoped and completed through its lane.

## Read the selected work, not another backlog

The original `load_work_map(root, map_path)` API and default CLI output are unchanged.
The additive `--view context` reads original task/package definitions through P04's
shared parser and emits a derived view: `artifacts`, `tasks`, `packages`,
`incomplete_ids` and P03's bounded `manifest`. It never changes task text or checkbox
state. `task_evidence: source-status-only` is not proof of acceptance;
`release_clearance` is always false. Empty/missing selected artifacts fail visibly.

```bash
python="${LINTEL_PYTHON:-python3}"
"$python" "$LINTEL_SOURCE_ROOT/bin/li-work-artifacts.py" \
  --repo "$LINTEL_REPO_ROOT" --map "${LINTEL_WORK_MAP:?select work.json}" --view context
```

`--field artifacts.tasks` (or spec/plan/prompt/constitution) returns the actual
path for a thin consumer. Do not substitute a sibling or a newer initiative.
Mapped Spec Kit `tasks.md` retains its IDs; native maps may intentionally point
plan and tasks at the same file. No parser or schema fork is needed.

When acceptance identity is required, use `--package <id> --leaf <original-id>`
(repeat `--leaf` as needed) and optional `--acceptance <path>`. The `binding`
is P05's actual `bind_work` result, not the manifest's byte hash or a text-only
substitute. Full-source Markdown classification and selection-relative excerpt
eligibility remain P05's responsibility. See
[the accepted evidence contract](../../review/references/evidence.md).

## Start and resume with verified profile references

Use the host adapter's explicit P07 bootstrap for a **new** work context. Before
phase consumption, `lib/workflow.sh` calls the actual profile verifier and obtains
the unchanged required-policy bridge. It never bootstraps during resume.

The same rule applies to a standalone authorized PLAN/BUILD entry: establish its
chosen cycle once before phase writes, or explicitly resume its original cycle.
Pure read-only inspection needs no new runtime ledger; if writes were forbidden,
use the derived views and report the unbound/non-clearing boundary.

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/workflow.sh"
workflow_begin "$LINTEL_CYCLE_ID" "$mode" "${LINTEL_WORK_MAP:-}" \
  "operation=$intent" "first_phase=$first_phase"
```

This writes the existing CYCLE ledger with `cycle_id`, `work_map_path`,
`work_artifacts` (paths only), `profile_reference`, its actual `profile_context_file`
and `required_policy`.
It is not a second work map. For new planning/research without a map, preserve the
explicit initiative/design selection; attach PLAN's map with
`workflow_bind_work "$LINTEL_WORK_MAP"` as soon as its DRAFT artifacts exist, before
ANALYZE/budgeting and before BUILD. Binding a path does not approve a draft.
Attaching a different map to the same cycle is refused.

```bash
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume "$LINTEL_CYCLE_ID" "${LINTEL_WORK_MAP:-}"
```

RESUME selects the original cycle, verifies its actual P07 context/generation/digest,
policy and target, checks the original mapped paths, and reports its unfinished
phase. Missing or drifted references, changed policy, a different initiative or a
different target do not fall back to neutral or a fresh profile. Resolve an explicit
rebind/transfer/replan first; it invalidates affected evidence. A new clone can inspect
the committed map read-only, but cannot turn a missing old profile into clearance.

The ledger now correlates resumed phase entries by cycle ID. Legacy untagged entries
inherit their original start marker. `state_cycle_segment <file> <cycle-id>` retrieves
that history even after another initiative has started. `state_resume_phase` returns
STARTING/BLOCKED/NEEDS_CONTEXT to the same phase, never to a planned later phase.
After `workflow_resume`, retain the exported cycle/profile/work references on subsequent
calls. Never use a PID, timestamp or newest directory as the work selection.
New entries carry an end marker so a truncated DONE is observed as INCOMPLETE and
cannot advance. Legacy unframed records remain readable history; they are not
content-bound review evidence or proof of atomic persistence.

For an analysis report, record its exact `analyze_report_path` in this cycle's
ANALYZE entry. After `workflow_resume`, retrieve that literal pointer with
`state_cycle_field analyze_report_path`; do not fall back to a global latest report.
Check the report's original map/profile/package/leaf identity before treating its
advisory findings as current. Use P05 `bind_work` when it is an acceptance input.
The path selection alone does not verify the report's reasoning or clear release.

## Budget the real handoff

`--view budget` measures the map and its distinct original artifacts once. Add
explicit `--warm-path <repo-relative-file>` arguments from the actual P03 selection,
not an unrelated warming log. Authority files cannot be cooled out of this read.
No warming inputs supplied means `warming: not-supplied`, not a complete zero-load census.

Use P03's `--capacity`, `--capacity-source`, `--used`, `--usage-source`, `--usage-kind`
and `--reserve` only for supplied host/usage evidence. Unknown remains unknown.
The byte/4 input estimate is not tokenizer usage, free context or billable cost.
The budget result is advisory for PLAN/CAPTURE; an actual host refusal or explicitly
required task limit still blocks the dependent load. Read failures return nonzero;
a successful estimate or unknown capacity does not certify that a handoff fits.
