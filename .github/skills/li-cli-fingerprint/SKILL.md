---
name: li-cli-fingerprint
description: Use to identify the current CLI, desktop, IDE or cloud surface and inspect its actual tools without inferring capability from a vendor name.
---

> **Lintel on GitHub Copilot.** Generated from `skills/cli-fingerprint/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** `<base>` and this skill's `scripts/`, `references/` and `data/` mean
>   `../../../skills/cli-fingerprint/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/cli-fingerprint/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Client fingerprint

Identify a surface and bind operations, not a vendor-wide support tier. Use the shared
reader in `lib/client_capabilities.py`; this skill is instruction-driven, not an automatic
process detector or hidden global cache.

## Inputs and authority

An explicit current-host declaration or host-provided session metadata is strongest.
`LINTEL_CLI` may be an operator hint, but cannot grant a tool or permission. `--declare`
means select the surface for this session; it does not write a personal configuration file.
`--force-redetect` means discard the prior declaration and inspect current evidence again.

Use exact IDs from:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-client-capabilities.py" list
python3 "$LINTEL_SOURCE_ROOT/bin/li-client-capabilities.py" show --client "$surface"
```

Set the source to the trusted checkout/bundle, not whichever repository happens to contain
a helper with the same name. Registry aliases such as `codex` and `copilot` select CLI only;
`copilot-app`, `copilot-vscode` and `copilot-cloud` never collapse to that CLI. `other` is an
explicit unidentified/manual route. A misspelled requested surface is an error.

## Procedure

1. Read the current host's supplied surface/session metadata and any explicit operator
   declaration. Retain both the actual session ID and separately selected work map.
   Resolve contradictory evidence before relying on a client-specific API.
2. Treat process names and installed-client folders only as weak hints. A desktop app can
   host a CLI engine. Do not inspect tokens, credential environment variables or private
   account settings. Having a binary installed does not mean it runs this session.
3. Inspect the actual tool inventory, including deferred-tool discovery where required.
   Identify question, plan, file/shell/browser, delegation, isolation, memory/resume, hooks
   and control operations by their schemas, not mandatory names such as `ask_user`.
4. Read the registry's source, delivered and observed fields separately. Missing vendor
   evidence is `unknown`; missing execution evidence is `not_run`. A documented feature
   can still be unavailable or forbidden in this session.
5. If needed, record a local session binding using the exact shape in
   [the Universal adapter](../../../shims/universal/ADAPTER.md). Run the real selector:

   ```bash
   python3 "$LINTEL_SOURCE_ROOT/bin/li-client-capabilities.py" resolve --session "$binding_file"
   ```

   The result is `declared-session-bindings`, with `executed: false`. It selects a route;
   it does not prove tool execution, authority or independent review.
6. Report the surface, actual version if available (otherwise unknown), identity source,
   available and missing operations, permission restrictions and selected fallback.
   Persist only non-sensitive evidence when continuity needs it, under project runtime
   storage, never an invented global `cli-id.txt` runtime.

## Degradation is useful

An unknown host can still read the same plan, execute permitted work serially, export a
package brief and resume from committed evidence. Missing a particular question-tool name
does not block questions; use the available channel. A denied tool is not an invitation to
bypass permission through shell or conversation.

Native delegation without attributable isolated writes selects serial work. Missing
delegation selects durable manual handoff. Independent review remains outstanding until
there is a separately attributable reviewer, not a second role played by the implementer.

## Recovery and compatibility

Malformed registry or bindings fail explicitly; repair the inputs rather than reporting
success with empty capability data. A new host needs a distinct surface record, official
sources for native outputs and consumer tests; a host outside the supported Copilot, Claude,
Codex and Cursor families first needs an ADR (ADR-0035). No `.disabled` marker, model setting
or plugin command is assumed.

The old `cli_tier_normalize`, `cli_tier_field`, `cli_tier_list` and table functions remain
in `lib/cli-tiers.sh`. They use the same registry; static hints never authorize concurrency.
Unknown legacy IDs produce a warned manual default, while the installer and explicit
surface selector reject unknown IDs.
