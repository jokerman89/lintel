---
name: pack-create
layer: foundation
description: Use to create a blank, inherited, or cloned Lintel pack and validate it before activation.
color: green
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

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
- One-off override for a single workflow — use `--mode` on `/li:cycle` instead

## Workflow

### 1. Select the authorized scope and source

Follow [lifecycle paths](../../docs/lifecycle.md). Use `--scope repo|home` explicitly:
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

### 3. Verify and report

Run `pack-validate "$name"` through that helper. Report the actual destination, effective
inherited fields, checked compatibility and unresolved resource/host boundaries. No
automatic activation or private synchronization follows creation. `/li:pack-switch`
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
- `/li:pack-switch <name>` to activate the new pack
- `/li:pack-list` to confirm

## Anti-patterns

- **Creating a pack to override one field** — edit `pack.yaml` of an existing pack instead
- **Not validating extends parent** — a broken explicit/required parent is an error
- **Copying neutral blocks into an inherited pack** — child blocks replace the parent's complete block; only declare an override when the change is intentional
- **Auto-activating after create** — operator decides when to switch (avoids surprise behavior changes mid-session)
