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
python3 bin/li-work-artifacts.py --repo /path/to/project --map .claude/plans/001-feature/work.json
```

The helper requires all declared artifacts to exist inside the working repository. It does
not infer a feature, inspect personal history, select by timestamp, run shell commands from
a task or certify completed checkboxes. Readers must still inspect acceptance evidence.

RESUME chooses an operator-named map, then an unambiguous active map linked in the committed
todo/working-state. If multiple active maps remain, ask which initiative; do not choose the
newest file. A legacy committed plan without a map is valid: follow its explicit spec/handoff
links, confirm the task source and create a map within authorized scope. Reconstruct local
runtime bookkeeping only after this selection and verification; never invent missing evidence.
