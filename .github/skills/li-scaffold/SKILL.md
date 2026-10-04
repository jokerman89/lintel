---
name: li-scaffold
description: Use to initialize or inspect repository foundations through the owned scaffold helper, preserving existing instructions, memory and explicit profile boundaries.
---

> **Lintel on GitHub Copilot.** Generated from `skills/scaffold/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/scaffold/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/scaffold/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Scaffold

Set up a new or existing repository with the current foundation, AGENTS/CLAUDE entry
templates, memory index, lessons/personas/working state, decisions, plan and swarm
templates. Keep the established base-initialization use case; use the actual helper
instead of a second copy/render recipe.

## Resolve the operation

Follow [lifecycle paths](../../../docs/lifecycle.md). Resolve helper code at the approved
`LINTEL_SOURCE_ROOT`; the explicit target alone selects where files change. Do not switch
to a different repository by basename, fetch a source implicitly or use the working
target's executable files as Lintel's implementation.

Reuse supplied name, intent and target. Ask only for missing decisions. `--mode` and
`--voice` are rendered preferences, not enabled controls. `--pack` must resolve through the
structured policy contract. Required caller and target policy cannot be silently
replaced by neutral defaults or by an identically named pack with different content.
The historical `--compliance` spelling returns an explicit unsupported-policy error
before writes; it never had a control implementation. Use validated pack policy instead
of treating a `full`/`minimal` label as enforcement.

## Application-mode acceptance (one owner)

This method owns the internal-tool and MVP questions, including calls through
the legacy aliases. Reuse supplied answers; ask each missing acceptance/failure
question once, not again on alias-to-owner handoff. Intent inputs below are not
new flags for `bin/li-scaffold`.

- **`internal-tool`:** retain `--name`, `--path`, `--language`, `--type`, `--ci`;
  `--path` selects the explicit target. Preserve CLI, service, dashboard and
  automation-script use cases with the selected available toolchain.
- **`mvp`:** retain `--name`, `--target-users`, `--path`, `--stack`, `--has-ai`,
  `--deploy`; preserve product/user framing and the first useful journey.
- Prefer existing manifests, architecture and framework-native generators when
  available and authorized. Ask about an unknown stack; do not assume a license,
  data classification, vendor, cloud, CI platform, AI feature or deployment target.
  An internal audience does not establish that all inputs are nonsensitive.

Define one useful end-to-end acceptance case and its principal failure case:

| Requested surface | Observable success and failure |
|---|---|
| CLI | Real arguments/input and result; invalid-input exit with actionable error |
| Service | Actual request/response and health contracts; validation and failure handling |
| Dashboard | Requested data/action flow; accessible loading, empty and error states |
| Script/automation | Explicit inputs/destination, deterministic output; safe failure/retry |
| MVP journey | First complete user job, needed state/API contracts; access and failure cases |

For AI features, retain sanitized **golden and adversarial cases**, expected
outcomes and reproducible evaluation commands; protect approved golden cases
from casual edits. Actual data classification/provenance, retention and ownership
remain explicit. Stubs carry an owner and follow-up phase and never satisfy
acceptance. A draft policy artifact is not a completed compliance review.

## Inspect, then initialize

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" check --target "$target"
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$target" --name "$name"
```

For a selected application mode, the same initializer receives only its existing
mode flag (with `mode` set to `internal-tool` or `mvp`):

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init \
  --target "$target" --name "$name" --mode "$mode"
```

`check`/`--dry-run` report the actual planned create/replace/delete paths without writing.
The helper preflights all paths and collisions, including late links, before publication.
Existing project instructions and seed files stay user-owned. Legacy data is migrated
only through the same verified transaction, never overwritten by new template seeds.

The legacy Claude `autoMemoryDirectory` pointer is a repository-local setting with
preserved surrounding configuration. Use `--no-memory-pointer` when that client-specific
setting is not wanted. A declared path is not proof of live host memory behavior.

For a native repository adapter, use `--client <exact-surface>` (repeatable) or the
preserved `--copilot` alias. These delegate to the existing ownership engine; they cannot
be combined with unsupported legacy rendering options. They do not register hooks,
change permissions, provision credentials or install a company pack.

## Implement and verify the selected application

Add the actual entry, domain/API/UI boundaries, minimal configuration, meaningful
tests and specific purpose/install/usage documentation for the accepted flow.
Use the project's chosen runner and conventions rather than generic stack advice
or speculative setup. Dependency installation needs actual authority and a changed
manifest or demonstrated missing dependency; never install automatically.

Run the smallest relevant build/type/lint checks and the actual success/failure
cases, with AI evaluation only where selected and authorized. CI must exercise real
commands and required controls; comments, no-op gates or slash-command text are not
enforcement. Customer guidance uses the selected pack's actual voice/corpus without
copying private material or inventing calibration.

Deployment preparation names environments, configuration/secrets boundaries,
observability and rollback. It does not deploy: no automatic hook registration,
external activation, private sync, image push or staging/production action. Each
needs its real authority and host support. Preserve existing governance.

## Context and recovery

When an existing caller context is supplied, the helper verifies that pin against its
original repository/home/source. An explicit new target is separately resolved, with a
required caller policy retained as an operation constraint. It does not transplant the
parent reference, change parent state or create a child profile generation. Start work
in the child with its own explicit bootstrap.

Record the helper's exact result and transaction/store identity. Its staged byte plan
uses P03 snapshots and explicit, conflict-preserving restore. On interruption, keep the
error and receipt; do not report success, retry into partial state or automatically roll
back. Use the documented `li-managed-transaction.py inspect|recover` command for the exact
target/store/ID. Later user edits and consumed recovery permissions are refused.

## Finish

Verify the returned changed/preserved files and relevant consumer checks. Leave Git
staging and commits to the authorized task; the helper never stages an unrelated index.
Preserve existing project governance. Additional compliance assets, private exports and
hook/host activation each need their own configured scope and evidence.

The internal-tool and MVP aliases delegate their preserved intent to this owner.
Report every placeholder, unavailable dependency/tool and unrun host/CI/environment
check explicitly. Keep source/target hashes, transaction receipt, profile context
and requirements with the selected work evidence. Foundation files alone are not
a functioning application or a verified live client session; independent
specification/quality review and deployment acceptance remain distinct gates.
