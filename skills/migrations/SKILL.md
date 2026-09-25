---
name: migrations
layer: foundation
description: Read the installed-source migration catalog against the selected target, preserving overdue, unknown and historical recovery states.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
---

# Migrations

A read-only view of migration obligations and recovery guides. It does not rewrite
code or select a new company pack. The historical v4/v5 names describe engineering
transitions, not the current public product version.

## Run the real reader

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" migrations
```

Use `--all` to include archived records. The helper reads the trusted source's
`docs/migrations/_INDEX.md`, never a same-named catalog in an unrelated current directory.
It classifies the full Markdown source with the accepted provider so examples and quoted
rows are not records. It never executes `detect_pattern`, shell fragments or catalog prose.

## Interpret the result

Keep two separate facts: the schedule (`open`, `overdue`, `archived`) and the target
observation (`current`, `needs_migration`, `incomplete`, `not_applicable`, `unknown`).
The layout reader checks actual legacy files, marker and retained redirect stubs.
Rows without an implemented detector remain unknown with a readable guide; they are not
assumed complete. A missing/malformed catalog is an error, not "no pending migrations".

An expired grace window never removes an unresolved migration, alias or backup. An
archived schedule is history, not evidence that this consumer finished its migration.
Use the operator's known target evidence before recommending any cleanup.

## Explicit execution and recovery

For the v5 layout, first run source-owned `bin/li-migrate-claude-home --dry-run --repo
<target>` and inspect conflicts. Apply only the authorized helper operation, retain its
receipt, and use its explicit recovery path if interrupted. Never substitute a shell
move/copy recipe, publish a marker over stranded data, or delete stubs by date.

### Historical identity migration

Use this same reader with `migrations --all` and `profile-status` to inspect the
explicitly selected target. Relevant signals include a local preference file with
old `workprofile`/compliance fields, authorized old voice/hook declarations, retained
`.lintel/state/` or pre-v5 knowledge paths, and the availability of the operator's
chosen company pack. Record the concrete signal source, not private contents.
Do not scan personal audit archives or infer a neutral pack from absent signals.
Old preference fields cannot override repository-required policy.

Applying an identity change requires the selected pack and a nonempty reason:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  pack-switch "$selected_pack" --reason "$migration_reason"
```

Follow [pack-switch](../pack-switch/SKILL.md) for validation, interruption recovery,
generation-bound references and explicit rebind. Missing/invalid required policy
remains blocked. Pack identity does not install a plugin or activate hooks. Keep
old logs, preferences, backups and redirect stubs readable; layout migration remains
the separate owned operation above, never a side effect of changing identity.

Report every surfaced row's evidence, action and limitation. No audit/schema mutation,
private-home search, network operation or automatic migration is needed to list status.
