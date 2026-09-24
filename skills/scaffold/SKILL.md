---
name: scaffold
layer: foundation
description: Use to initialize or inspect repository foundations through the owned scaffold helper, preserving existing instructions, memory and explicit profile boundaries.
color: cyan
tools: Read, Bash, Edit, Write, Glob
voice: internal
cli_support: [claude-code, codex]
---

# Scaffold

Set up a new or existing repository with the current foundation, AGENTS/CLAUDE entry
templates, memory index, lessons/personas/working state, decisions, plan and swarm
templates. Keep the established base-initialization use case; use the actual helper
instead of a second copy/render recipe.

## Resolve the operation

Follow [lifecycle paths](../../docs/lifecycle.md). Resolve helper code at the approved
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

## Inspect, then initialize

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" check --target "$target"
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$target" --name "$name"
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

The internal-tool and MVP aliases add application intent and working-flow acceptance to
this base operation. Foundation files alone are not a functioning application or a
verified live client session.
