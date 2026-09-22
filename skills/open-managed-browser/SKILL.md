---
name: open-managed-browser
layer: foundation
description: Use to open an explicitly owned browser session for operator debugging, or check a real provider without touching personal profiles.
color: blue
tools: Read, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /open-managed-browser

The operator-driven entry point for the [shared browser operations](../browse/references/browser-operations.md).
Retain manual exploration, debugging, preview and authentication-surface choice without
assuming a Lintel-installed Chromium or a shared cookie store.

## Inputs

- `--url <url>`: optional authorized initial URL; otherwise an owned `about:blank`.
- `--profile <name>`: an **explicit user-owned session choice**, not a directory to
  discover or create under the user's home. Resolve it through the selected provider
  only after the user chooses that surface and scope. Never scan personal profiles.
- `--check`: read-only provider preflight; no browser launch or inspection of tabs,
  credentials, cookies or service history.
- `--devtools`: request DevTools if the actual host exposes it. Report unsupported
  rather than inventing a flag or opening another user's window.

## Check without launching

1. Inspect the host's actual deferred/native tool schemas and permission state.
2. Identify how a new isolated context is created and which exact handle owns it.
   A default tab or tool named "browser" is not proof of isolation.
3. For an explicitly selected local executable, check its file presence and the
   required API/runtime dependencies. The concrete Chromium provider's
   `checkProvider(executable)` returns `executed:false` and `version:null`.
4. Report separate facts: binary present/missing, provider API observed/unverified,
   launch not run, isolation unverified, and permission allowed/unknown/denied.
   A healthy profile directory cannot turn any of these into an engine pass.

Do not execute a browser's ambiguous `--version` switch against its default profile.
Read the running **owned** browser's version API after safe launch instead.

## Open for the operator

1. Establish the chosen surface, exact allowed hosts/origins, intended work and
   profile reference, and whether the user or this invocation will own closure.
2. Use the shared provider preflight and URL/redirect admission. A permitted tool
   still needs a fresh context or an explicitly authorized user-owned context.
   Do not attach to discovered personal tabs or silently reuse an old profile.
3. Request a visible session through the actual provider. The delivered Chromium
   source API accepts `headed:true` with a **new** temporary user-data directory
   and an isolated-context requirement. Owned headless operations were observed,
   but a subsequent startup failed reading its own endpoint file and native
   execution stopped again. Headed use is not verified. It does not reopen saved
   profiles or prove persistent authentication.
4. Verify launch through the owned endpoint and actual page state. Keep the
   process attached and retain its handle. Do not detach by default.
5. Report executable/API and version, owned context/PID, opened URL, available
   actions and exact lifetime. Let the user drive their chosen login surface.
6. When requested work ends, close only what this invocation owns. Leave a
   user-owned browser/session alone. Removal of user-retained profile data needs
   separate scope; never "repair" a personal profile by deleting it.

The single-page Chromium fallback refuses additional targets, credential filling,
downloads and unsupported dialogs. If the operator needs interactive DevTools,
multi-tab work or a persistent session, select a host/provider that demonstrably
supports it or retain a manual handoff. Do not claim these fallback gaps are solved.

## Failure and recovery

- **Missing binary/API:** report the exact missing prerequisite. Use an existing
  installed provider first. A scoped dependency restore requires an actual failure,
  provenance/license review and permission; no automatic global installation.
- **Unknown isolation:** do not list or navigate existing tabs to "find out".
  Retain the requested URL/actions as a manual task on the user's chosen surface.
- **Launch exits early:** retain its actual error/exit; file presence is not success.
- **Policy or permission denies navigation:** stop that operation, without a
  production override flag, security warning bypass or fallback to personal Chrome.
- **Cleanup fails:** retain owned profile/path and exact PID evidence; report
  unfinished cleanup. Never kill browsers by name or delete a broad profile root.

## Examples

`/open-managed-browser --check` reports preflight facts without opening a page.
`/open-managed-browser --url http://127.0.0.1:5173` requests a new owned visible
session after that exact loopback service has been authorized and observed responding.
`/open-managed-browser --profile team-test` asks the provider to resolve the
user-selected session; the local ephemeral fallback reports persistent reuse unsupported.

See `/browse` for repeatable actions, `/scrape` for extraction, and
`/setup-browser-cookies` for manual login and subsequent non-secret validation.
