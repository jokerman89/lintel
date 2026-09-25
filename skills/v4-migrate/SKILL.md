---
name: v4-migrate
layer: foundation
description: Retain explicit v3-to-v4 identity inspection and recovery through the current migration reader and structured pack switch.
color: yellow
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# Historical v4 migration

This opt-in alias preserves the v3-to-v4 identity transition. It is not a public product
version requirement, automatic first-run action or reason to remove old state.
Start with [migrations](../migrations/SKILL.md), using the installed source and exact
consumer roots from [lifecycle paths](../../docs/lifecycle.md).

## Inspect, without changing identity

Run source-owned `bin/li-lifecycle.py migrations --all` and `profile-status`. Read only
the explicitly configured local profile and selected target's relevant legacy paths.
Retain the historical detection questions:

- Does the local preference file still contain `workprofile` or old compliance fields?
- Does explicitly authorized legacy state reference non-internal voice or unscoped hooks?
- Does this target retain `.lintel/state/` or pre-v5 knowledge paths?
- Is the desired company pack actually installed, valid and explicitly selected?

Record the concrete source of each signal, not private content in public evidence.
Do not recursively read a personal audit archive by default. Absence of signals is not
permission to choose `_default`; historical profile fields do not override the accepted
structured resolver or repository-required policy.

## Apply only an explicit, validated choice

`--apply` must include the operator's chosen pack and reason. If either is missing, stop
for that decision rather than inferring the "closest" company/compliance pack.

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  pack-switch "$selected_pack" --reason "$migration_reason"
```

Follow the complete [pack-switch](../pack-switch/SKILL.md) result/rebind contract. A failed
required pack stays failed; a mid-write interruption is not "effective next session".
Preserve the returned generation-bound reference and previous history, then replan
dependent work. Extension identity does not install its host plugin or hooks.

Layout migration is separate: use `bin/li-migrate-claude-home` after its explicit dry run.
Do not mass-rewrite legacy logs, preferences or content while changing a pack pointer.
Keep historical stubs and unverified backups available for reviewed recovery. Completion
means the requested effective change was observed in the intended target, not that the
old alias was invoked.
