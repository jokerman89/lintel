# Lintel with Spec Kit

Keep Spec Kit's constitution, specification, implementation plan and task list as the source of
truth for specification-driven development. Use Lintel for session preparation, focused build
execution, review and continuity around those files. One feature should have one authoritative
task list and one active executor.

This is an optional workflow bridge, not a fork of Spec Kit or an automatic installation of it.
The native `li-spec-kit` skill guides the handoff. Lintel does not vendor or automatically update
Spec Kit, and installing Lintel does not require Spec Kit.

## Connect an existing project

In Copilot, run `/li-spec-kit`, or ask it to read the installed skill directly. A useful request is:

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
| Work and completion | Existing feature `tasks.md` | Preserve task IDs, mark completion only after verification |
| Artifact mapping | `.claude/plans/<feature>/work.json` | Record exact original spec, design, tasks and handoff paths with the scope status |
| Session coordination | `.claude/plans/todo.md` | Link the active work map and next task; avoid copying the whole backlog |
| Durable context | `.claude/memory/` and `.claude/decisions/` | Capture lessons, working state and new decisions |

Feature paths vary by Spec Kit version and repository configuration. `specs/<feature>/` is a
common layout, not a path to fabricate. If the feature already has an execution prompt, reuse it;
otherwise a short Lintel handoff can reference the existing artifacts by path. The Lintel
plan/spec/prompt contract is satisfied by an explicit mapping, not by keeping duplicate copies.

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

On a fresh clone, local ledgers and checkpoints may be absent. `/li-resume` first follows the
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

Install Spec Kit through its [official repository](https://github.com/github/spec-kit) using a
version your team approves. Then inspect the locally installed CLI:

```bash
specify --help
specify init --help
specify version
```

The current upstream interface uses:

```bash
specify init --here --integration copilot
```

For PowerShell feature scripts, add `--script ps` when supported. Run initialization on a clean
branch, inspect the changes, and avoid `--force` over existing instructions or feature state.
Older releases may expose different flags; follow the installed help instead of mixing versions.
[Spec Kit's core reference](https://github.github.com/spec-kit/reference/core.html) documents the
current initialization and version commands.

Current Spec Kit defaults to `speckit-*` skills under `.github/skills/` for Copilot. Its optional
commands layout uses agent/prompt files; see the [upstream integration reference](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md).
Lintel uses separate `li-*` names. Verify discovery after installation and use the names your
installed version exposes rather than assuming older `/speckit.*` examples apply unchanged.

## Adoption checks

Confirm that both tools discover the same active feature, that only one authoritative task list
is updated, and that a fresh `/li-resume` session reads it correctly. Verify at least one task's
acceptance criteria against real tests. Record both source versions and any artifact mapping in
the adoption PR. Structural compatibility is not evidence of a live successful Copilot execution.

For rollout ownership and evidence, see [enterprise adoption](enterprise-adoption.md).
For the host integration, see [GitHub Copilot](copilot.md).
