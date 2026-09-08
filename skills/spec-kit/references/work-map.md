# Committed work map

`bin/li-work-artifacts.py` owns the version-1 map contract and validates it without executing
artifact content. PLAN, BUILD, REVIEW and RESUME use these same fields. Paths are relative to
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
