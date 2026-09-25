---
name: profile-switch
layer: foundation
description: Inspect host install state and guide explicitly supported activation or owned snapshot recovery, without inventing plugin controls.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# Host install profiles

Preserve the useful status, temporary disable/re-enable, named snapshot and previous-setup
recovery entry points. This skill controls **host installation intent**, not the effective
company pack or a conversation's audience lens. Use `/li:pack-switch` for policy context
and `/li:role --audience <name>` for a temporary audience.

## Status and host operations

Resolve the exact client surface and [lifecycle roots](../../docs/lifecycle.md). Start with:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  host-profile status --client "$client"
```

The shipped helper reports activation as `unverified`; it does not infer activity from
cached plugin files, an executable in PATH, or a declared capability. `/li:doctor` checks
local file integrity separately.

`--dormant` and `--activate` map to `host-profile dormant|activate`. They currently return
`UNSUPPORTED_HOST_OPERATION` without mutation: no enable/disable binding ships here.
Keep the request useful by handing off to the exact host's documented controls or an
actually available authorized tool. Identify installed plugin identity/version first,
obtain any required host permission, perform only that operation, then inspect discovery
in a new session. Report success only after observing the requested change. If no such
operation is available, stop at unsupported/manual, not simulated success.

Never create a guessed disable marker, alter arbitrary plugin trees, rewrite model
configuration or treat a pack preference as a plugin on/off switch.

## Snapshot, list and restore aliases

`--snapshot <label>`, `--list` and `--restore <id>` retain their recovery purpose through
the [owned snapshot workflow](../safe-install/SKILL.md):

- Select an explicit installation root, separate private store and exact owned paths.
- Use source-owned `bin/li-snapshot.py create|list|verify|restore`. Retain the returned
  exact snapshot ID; a human label is only a label, not a guessed directory selector.
- An operation must bind its own verified result before restore can replace changed
  files. A copied host directory without ownership/postimage evidence is not that result.
- Explicit restore preflights all bytes, refuses later edits and records per-file
  progress. Do not auto-restore another snapshot after failure.

Old named backups and predecessor archives remain available for read-only inspection.
They lack the verified ownership format, so restoration requires a separately reviewed
file-level plan; do not relabel them or remove them because they are old.

## Boundaries and result

No broad host-settings restore, recursive uninstall, private synchronization, hook
registration or default repository change occurs. File recovery cannot undo external
host/service side effects. Use actual host uninstall for activation removal; use an
owned installer receipt for file rollback, not deletion of the whole install root.

Report the requested mode, exact surface, observed status, performed mutation (or none),
snapshot/recovery identity, preserved user content and remaining manual host boundary.
One host succeeding never hides another host's failed or unverified operation.
