---
name: li-pack-list
description: List configured-store, repository and installed-source packs with resolver precedence, validation results and the actual effective profile.
---

> **Lintel on GitHub Copilot.** Generated from `skills/pack-list/SKILL.md`; edit the canonical file, then run
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

You are the PACK-LIST skill — surfaces every pack available on this machine.

## What this skill does

Calls `bin/li-lifecycle.py pack-list` with the [configured roots](../../../docs/lifecycle.md).
The helper inventories configured-store, target-repository and trusted-source packs with
the same structured resolver as consumers. Render its actual results as a table:

```
PACK       ORIGIN       SELECTED SOURCE  VALID  EFFECTIVE
_default   source       yes              yes    yes
example    repository   no (shadowed)    yes    no
example    store        yes              yes    no
```

`*` marks the active pack. Only `_default` ships with Lintel; other packs are installed by the operator — a company pack contributes its own voice, compliance, and roles on top of `_default`.

## When to use

- Operator forgot which packs exist
- Before `/li-pack-switch` to confirm target
- Before `/li-pack-create` to avoid name collision
- After an explicit identity migration through `/li-migrations` to confirm the selected pack is present

## When NOT to use

- To infer which host plugins or hooks are active; manifest discovery does not prove that
- For pack-content introspection — read the pack.yaml directly

## Workflow

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" pack-list
```

Keep the historical skill `--validate` spelling as a request to show the helper's
per-row validation/compatibility details; the helper always checks them. Include:
origin, selected versus shadowed source, validity and diagnostics, pack release and
separate schema/product/feature compatibility. Do not equate `requires_lintel` with
the public product version.

Report `effective_pack` and the exact bound reference if present. `reference: null`
means an unbound read, not a stable handoff. Distinguish optional fallback diagnostics
from valid neutral first use; a broken required profile or drift is an error.

Retain duplicate names as shadowed rows instead of hiding them. Listing never binds a
context, changes a pointer, installs an extension or inspects private role bodies.
Use `/li-pack-validate <name>` for effective field details and `/li-pack-switch <name>`
for an explicit policy-context change.

## Integration

**Reads:**
- Configured pack store, selected target and trusted installed source manifests
- Configured active pointer, repository requirements and any selected profile reference

**Writes:**
- stdout only — no state mutation

## Anti-patterns

- **Hardcoding pack list** — always re-discover (operators add packs frequently)
- **Hiding home-packs** — both scopes count; surface both
- **Suppressing pack collisions** — configured store wins over target and source; show all origins
