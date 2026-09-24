---
name: pack-switch
layer: foundation
description: Use to explicitly switch the effective pack through the structured profile lifecycle, preserving required policy, configured paths and generation-bound recovery.
color: green
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex]
---

# Pack switch

Change policy context only for the selected working repository and configured operator
store. Follow [lifecycle paths](../../docs/lifecycle.md); a bare install, source bundle,
working target and profile pointer are different things.

## Workflow

1. Read the current `profile-status`, then `pack-validate <target>` through the source-owned
   helper. Show the current and requested effective voice, compliance, navigation, persona,
   role and extension fields. A changed policy can invalidate the current plan and review.
2. Establish authorization for this target and reason. An explicit operator switch is
   already authorization; ask only for a missing decision. Never replace a repository's
   required pack or silently remove `LINTEL_PROFILE_PACK` to make the switch succeed.
3. Run the actual helper and retain its exit status:

   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
     --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
     pack-switch "$target" --reason "$reason"
   ```

4. Report `changed`, the effective pack, actual configured pointer and full returned
   reference: schema_version, context_id, generation, digest, name and version. A repeated
   switch to the already effective target is a verified no-op, not a new activation.
5. Carry the returned reference into subsequent work only as part of this explicit switch.
   Older handoffs must fail their reference check; replan affected work and obtain fresh
   review. Ordinary bootstrap verifies a pin and never silently adopts the new generation.

The helper consumes `LINTEL_PACKS_DIR` and `LINTEL_ACTIVE_PACK_FILE`, validates before
writing, atomically writes the configured pointer and invokes the accepted structured
rebind API. Profile history retains the previous generation and reason. Do not maintain
another parser, raw cache, home pointer or independent hand-written audit receipt.

## Drift and interrupted switching

`PROFILE_DRIFT`, missing history, invalid required packs and incompatible schema/product/
capability constraints are unresolved errors, never neutral success. A failed binding
after the pointer write is `PROFILE_SWITCH_INCOMPLETE`, not "active next session".
Preserve both pointer and history, inspect the error, then use an explicitly reasoned
rebind through the same helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  profile-rebind --pack "$target" --reason "$recovery_reason"
```

Do not automatically roll back, delete a context, forge a reference or retry against a
different target. The legacy `clear_pack_cache` accessor remains an explicit reasoned
rebind compatibility path, not a way to discard history.

## Extension and host boundary

An extension pack still contributes its declared namespace, workflow and specialist
methods. Show those from the validated target values, including which surfaces it
declares. Identity selection does **not** install/discover plugins, register hooks, grant
permissions, copy private packs or switch models. Use the actual host-supported extension
operation separately with its own authorization and observed discovery evidence.
