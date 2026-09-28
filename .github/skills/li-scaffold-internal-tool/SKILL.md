---
name: li-scaffold-internal-tool
description: Create a working internal CLI, service, dashboard or script using the common owned foundation initializer and the project's chosen toolchain.
---

> **Lintel on GitHub Copilot.** Generated from `skills/scaffold-internal-tool/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Scaffold an internal tool

Retain the CLI, service, dashboard and automation-script use cases, with a leaner
application scope than an MVP. Reuse [scaffold](../../../skills/scaffold/SKILL.md) for Lintel's
foundation; do not reimplement instruction, memory or migration copying.

## Establish the requested flow

Reuse the supplied `--name`, `--path`, `--language`, `--type` and `--ci` choices. A path
means the explicit working target, not a guess from its name. Support the chosen
TypeScript, Python, Go or Rust toolchain where available; ask about an unknown stack
instead of silently falling back. Prefer existing manifests and framework-native
generators. Do not choose a license, data classification, vendor, cloud or CI platform
without a project/brief basis.

Define one useful end-to-end acceptance case and its principal failure case:

- CLI: real arguments/input, observable result, invalid-input exit and actionable error.
- Service: actual request/response contract, health behavior, validation and failure handling.
- Dashboard: the requested data/action flow, loading/empty/error states and accessible UI.
- Script/automation: explicit inputs/destination, deterministic output and safe failure/retry.

An internal audience is not evidence that the tool never handles customer or sensitive
data. Load actual pack requirements and keep secrets/private state out of starter fixtures.

## Implement the base and application

Create only the authorized target using the selected ecosystem's tooling. Then dispatch:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init \
  --target "$target" --name "$name" --mode internal-tool
```

Follow its source/target/profile, collision and recovery contract. Existing prose, configs,
roles and extensions must survive. A bound parent profile stays an operation constraint;
the child is not silently bootstrapped or activated.

Add the actual application entry, typed boundaries, minimal configuration and tests for
the requested flow. Preserve the useful language-specific methods: strict TypeScript
checking, Python package/lint/test configuration, Go's module/layout conventions, or
Rust's Cargo entry and tests. Use the repository's selected runner instead of installing
another one reflexively. Dependency installation follows a changed manifest or a real
missing-dependency failure, not speculative setup.

Keep purpose/install/usage docs, ignore rules and editor conventions useful and specific.
Add GitHub/Azure DevOps CI only when selected, exercising real commands; never claim a
comment, a no-op gate or a slash command in YAML is enforced CI. Preserve existing
governance and do not register pack hooks automatically.

## Acceptance and handoff

Run the smallest relevant build/type/lint checks and both actual flow cases. Report
placeholders, unconfigured dependencies, unavailable tools and unrun host/CI checks
explicitly; a skeleton is not a working tool. Preserve source/target hashes and the
foundation transaction receipt where recovery matters. Commit only within current
authority and never imply deployment, publication or private synchronization.
