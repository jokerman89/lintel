# Lintel with Spec Kit

Keep Spec Kit's constitution, specification, implementation plan and task list as the source of
truth for specification-driven development. Use Lintel for session preparation, focused build
execution, review and continuity around those files. One feature should have one authoritative
task list and one active executor.

This is an optional workflow bridge, not a fork of Spec Kit or an automatic installation of it.
The native `li-spec-kit` skill guides the handoff. Lintel does not vendor or automatically update
Spec Kit, and installing Lintel does not require Spec Kit.

## Connect an existing project

Invoke the `spec-kit` workflow in your client's form (`/li:spec-kit` in the Claude plugin,
`li-spec-kit` in generated adapters such as Copilot's `/li-spec-kit`), or ask the agent to read
the installed skill directly. A useful request is:

```text
Use Lintel with this repository's existing Spec Kit feature. Find the active feature and
read its constitution, spec.md, plan.md and tasks.md. Keep those files authoritative.
Map each task to acceptance criteria and verification, then resume the next incomplete
build card. Do not create a second feature branch or duplicate the task list.
```

First inspect the installed Spec Kit configuration and feature selection. Do not assume the
newest directory is active. Resolve the feature from the tool's state, current branch and explicit
operator intent; report ambiguity before changing feature artifacts.

## Artifact ownership

| Concern | Authoritative artifact | Lintel action |
|---|---|---|
| Governing principles | `.specify/memory/constitution.md` when present | Read it and reconcile with repository instructions |
| What to build | Existing feature `spec.md` | Reference requirements and acceptance criteria during planning and review |
| How to build | Existing feature `plan.md` and supporting design files | Use its design decisions; propose changes explicitly |
| Work and completion | Existing feature `tasks.md`, including converge-appended IDs/phases | Preserve task IDs, mark completion only after verification |
| Analysis, convergence, bug/test and assessment evidence | Explicitly selected original reports | Read/bind originals; retain verdicts and unresolved ownership, not duplicate Lintel reports or backlogs |
| Artifact mapping | `.claude/plans/<feature>/work.json` | Record exact original spec, design, tasks and handoff paths with the scope status |
| Session coordination | `.claude/plans/todo.md` | Link the active work map and next task; avoid copying the whole backlog |
| Durable context | `.claude/memory/` and `.claude/decisions/` | Capture lessons, working state and new decisions |

Feature paths vary by Spec Kit version and repository configuration. `specs/<feature>/` is a
common layout, not a path to fabricate. If the feature already has an execution prompt, reuse it;
otherwise a short Lintel handoff can reference the existing artifacts by path. The Lintel
plan/spec/prompt contract is satisfied by an explicit mapping, not by keeping duplicate copies.

## Select reports and resolve overlapping checks

Use the bridge's [selected external authority procedure](../skills/spec-kit/references/selected-authority.md)
before ANALYZE, DEFINE, DIAGNOSE, FIX or REVIEW. Select original reports by explicit
path from the operator, mapped handoff or inspected project configuration.
`tasks.md` remains the only task source, including tasks appended by convergence.
An assessment decision or bug verdict remains an input, not source approval,
independent review or permission to publish.

Observe command registration, workflow-gate coverage and hook enablement only
from supplied/inspected host registration or known version-specific configuration.
A filename, extension folder or upstream comparison pin proves none of these.
Retain disabled/unknown/unsupported observations and resolve ambiguous ownership
before the affected action. Choose one owner for overlapping consistency, gap,
fix or gate work; do not run both workflows, enable extensions or resume an
external run merely to fill an observation gap.

The existing work reader accepts repeated `--warm-path` inputs for read-only
intake/budgeting. With original `--package` / `--leaf` IDs, repeated `--acceptance`
paths bind selected reports using P05 and include their full original files in
P03's deduplicated manifest/budget. Carry them into the review prepare request's
`acceptance_paths` or explicit product selection; warming alone is not a binding.
No report fields are added to `work.json`. Changed selected reports, task text/IDs
or relevant configuration invalidate affected evidence; progress boxes are not
verification. Uncovered Lintel-specific checks may add linked evidence, never a
competing analysis/task list.

## A committed map for a fresh checkout

The `li-spec-kit` workflow writes `work.json` and links it from the committed plan index. Its
`spec`, `plan`, `tasks` and `prompt` fields identify the existing artifacts. `workflow` is
`spec-kit`; native Lintel work uses `lintel` and can point `tasks` to its own plan checklist.
Start with DRAFT and record APPROVED only for scope already approved by the operator. The map
does not grant new permissions or prove that checked tasks were verified.

The [shared work-map contract](../skills/spec-kit/references/work-map.md) defines the fields.
From an installed target repository, validate the chosen map with:

```bash
python3 .github/lintel/bin/li-work-artifacts.py --repo . --map .claude/plans/your-feature/work.json
```

Use the installed Python 3.9+ executable name if it differs. The validator checks declared paths
and schema without executing task content. It does not select a feature for you.

Add `--view context` to inspect original task IDs, package membership and a bounded,
deduplicated input manifest without creating another task list. In an explicitly
selected Swarm map, the validated coordination supplies existing lane/package
recognition, including legacy named singletons, and is counted once in that
manifest and its byte budget. Unselected prose headings are not guessed into
tasks. DRAFT inspection and source checkboxes do not establish approval, execution
or review clearance; an actual acceptance binding remains a separate operation.

On a fresh clone, local ledgers and checkpoints may be absent. `resume` first follows the
explicit active map or unambiguous committed plan/handoff links in todo.md and working-state.md.
It reads the original task IDs, code and verification evidence before recreating local runtime
state. Multiple active initiatives require a choice; the newest directory is not an authority.

## Build one task at a time

1. Read the next incomplete task and the requirements it implements. Verify dependencies are done.
2. State the changed files, acceptance criteria, verification and authorized scope. Ask only for
   decisions the existing plan and authorization do not settle.
3. Implement the task. When the host supports subagents, give independent tasks bounded scopes
   and use a separate review context. Avoid simultaneous edits to the same task-state file.
4. Run relevant checks and review the result against the specification and project standards.
5. Record evidence beside the task or in the linked review record, then mark it complete.
   Capture the next action for a fresh session.

If requirements change, update the specification and plan before continuing. If a task is
blocked, record the cause without checking it off. Do not run Spec Kit's implementation workflow
and Lintel's BUILD concurrently against the same feature.

## Starting with Spec Kit

Only when separately requested, install Spec Kit through its
[official repository](https://github.com/github/spec-kit) using a version your team
approves. First inspect the actually available CLI/help; this bridge neither
requires it nor infers installation from the repository's artifacts:

```bash
specify --help
specify init --help
```

Use only integration/script flags the inspected version supports. Run authorized
initialization on a clean branch, inspect the changes, and avoid `--force` over
existing instructions or feature state. Verify actual host discovery afterwards;
do not derive installed command names or an extension grammar from old examples.
Lintel's `li-*` names do not establish which Spec Kit commands this host exposes.

The original 2026-09-28 comparison used Spec Kit
[`c00dc0551583428a10a94443c58c6a41e5e0138c`](https://github.com/github/spec-kit/tree/c00dc0551583428a10a94443c58c6a41e5e0138c/templates/commands).
It records analysis/converge methods and optional extension/workflow overlap, not
an installed local tool or a fresh upstream check. See [provenance](provenance.md)
for dated comparison pointers and their limits.

## Adoption checks

Confirm that both tools discover the same active feature, that only one authoritative task list
is updated, and that a fresh `/li-resume` session reads it correctly. Verify at least one task's
acceptance criteria against real tests. Record both source versions and any artifact mapping in
the adoption PR. Structural compatibility is not evidence of a live successful Copilot execution.

For rollout ownership and evidence, see [enterprise adoption](enterprise-adoption.md).
For the host integration, see [GitHub Copilot](copilot.md).
