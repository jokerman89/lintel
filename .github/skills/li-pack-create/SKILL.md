---
name: li-pack-create
description: Use to create a blank, inherited, or cloned Lintel pack and validate it before activation.
---

> **Lintel on GitHub Copilot.** Generated from `skills/pack-create/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/pack-create/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/pack-create/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the PACK-CREATE skill — scaffolds a new pack in `<repo>/packs/<name>/` or `~/.lintel/packs/<name>/`.

## What this skill does

Creates a new pack directory + manifest. Three modes:

- **Blank pack:** starts from `packs/_default/pack.yaml` skeleton (every field declared with neutral value)
- **Extending pack:** declares its identity and `extends: <parent-name>`; inherits the parent's blocks and declares only intentional overrides
- **Cloned pack:** copies an existing pack as a starting point (operator edits per their needs)

## When to use

- Operator wants a new pack for a fresh customer/team/domain
- Sister pack to an existing pack (extends: shared parent)
- Forking an existing pack for an isolated experiment

## When NOT to use

- Tweaking an existing pack — just edit `packs/<name>/pack.yaml` directly
- One-off override for a single workflow — use `--mode` on `/li-cycle` instead

## Workflow

### 1. Select the authorized scope and source

Follow [lifecycle paths](../../../docs/lifecycle.md). Use `--scope repo|home` explicitly:
`repo` means the selected working repository's `packs/`; `home` means the configured
`LINTEL_PACKS_DIR`, not an assumed personal directory. Keep private identity out of
repository/public outputs unless that exact transfer is authorized.

Gather only missing facts: safe pack name, scope, and blank/inherited/cloned-manifest
intent. Do not invent policy, company identity or a compliance posture.

### 2. Dispatch through the structured helper

```bash
create_args=("$name" --scope "$scope")
[ -z "${parent:-}" ] || create_args+=(--extends "$parent")
[ -z "${template_pack:-}" ] || create_args+=(--from "$template_pack")
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  pack-create "${create_args[@]}"
```

Set `parent` for inheritance or `template_pack` for a cloned manifest, otherwise leave
both empty. These options are mutually exclusive. The helper stages and
validates the manifest and ancestry with the same profile API used by consumers, then
publishes one verified file without replacing existing content.

An inherited child declares only identity and its parent. It does not copy neutral
blocks over company policy. Cloning copies the manifest as an editable starting point,
**not** referenced private corpora, credentials, executable extensions or hook settings.
Inspect and explicitly configure referenced resources before claiming they are usable.

A pack may point at a reusable-pattern catalog. Set the optional field
`patterns: { source: patterns/catalog.json }`, whose path is relative to the pack root; the
neutral value is `source: null`. The block replaces a parent's block wholesale. Keep a
source-local `.gitattributes` with `* -text` beside that catalog so asset bytes stay exact. Do not
invent pattern content: capture it with the [pattern workflow](../../../skills/pattern/SKILL.md) from the
owner's confirmed expectations, and ship every declared asset and pinned `root: pattern` source.

### 3. Verify and report

Run `pack-validate "$name"` through that helper. Report the actual destination, effective
inherited fields, checked compatibility and unresolved resource/host boundaries. No
automatic activation or private synchronization follows creation. `/li-pack-switch`
is the separately authorized activation path.

For an extension-plugin skeleton, retain `bin/li-pack-scaffold` with the explicit
namespace/workflow and destination. This creates source files, not a running plugin;
host installation/discovery still needs its own supported operation and evidence.

## Pause-points

- Step 1 if scope ambiguous: ask `repo` or `home`
- On validation failure: retain the diagnostic, do not claim a created/usable pack

## Integration

**Reads:**
- `packs/_default/pack.yaml` (template)
- `bin/li-lifecycle.py` and the shared structured profile implementation

**Writes:**
- `<scope>/packs/<name>/pack.yaml`
- The helper's observed result; no independent handwritten audit schema

**Triggers (recommends):**
- `/li-pack-switch <name>` to activate the new pack
- `/li-pack-list` to confirm

## Anti-patterns

- **Creating a pack to override one field** — edit `pack.yaml` of an existing pack instead
- **Not validating extends parent** — a broken explicit/required parent is an error
- **Copying neutral blocks into an inherited pack** — child blocks replace the parent's complete block; only declare an override when the change is intentional
- **Auto-activating after create** — operator decides when to switch (avoids surprise behavior changes mid-session)
