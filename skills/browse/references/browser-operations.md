# Browser operations and session ownership

This is the shared method for browse, managed-browser, authentication, scrape and
browser-dependent preview/print tasks. It is a concrete consumer of the existing
[Universal adapter](../../../shims/universal/ADAPTER.md), not a new host registry,
policy engine or daemon. Design schemas and document-format producers are separate.

## Select real operations, not a client label

| Operation | Required observation | Unavailable boundary |
|---|---|---|
| open | Admitted URL, actual response/final URL and current page | Search/HTTP text alone is not a rendered page. |
| read | DOM/accessibility result from the owned page, with selector/state | Report inaccessible content; do not fabricate an accessibility tree from HTML. |
| act | Current target, authorized input, real action and changed state | Missing/ambiguous targets stop the sequence. |
| screenshot | Actual capture, viewport/media and inspected image | File existence/size is not visual review. |
| print | Actual print API/result, PDF artifact and content/layout observations | No print API means unverified print, not a renamed screenshot. |
| session | Proven creation/owner/handle, lifetime and observed closure | A profile folder, existing tab or tool name is not isolation. |

Use the current host's discovery API to inspect deferred tool schemas first.
`lib/client_capabilities.py` / `bin/li-client-capabilities.py resolve` can validate
the caller-inspected binding, but returns `executed:false`; it does not run a
browser or grant permission. Never call a tool on its default page to discover
whether that page is personal. Unknown isolation blocks that provider's operation.
No fallback circumvents a denial.

Before acting, validate the **selected** map with `bin/li-work-artifacts.py` and
verify the P07 profile reference with `lib/profile_context.py`/its shell accessors.
Keep `work_map`, the full `profile_ref`, and the actual stable `session_id` through
the browser result and handoff unchanged. Do not parse a profile cache, select a
map by mtime or reimplement either schema. The browser adapter accepts these as
opaque caller-verified context; it does not resolve policy or certify them.
Reverify before dependent actions and evidence consumption; drift blocks rather
than silently rebinding.

## URL and redirect boundary

Use `lib/url_policy.py` from the same trusted installed source as this reference.
It owns HTTP(S) parsing, exact versus explicit wildcard hosts, credentials/control/
backslash rejection, raw Location validation and HTTPS downgrade refusal.

Do not prefetch a chain and then navigate with unchecked automatic redirects:
the second request can return a different Location. The **actual** browser must
intercept requests and redirect responses before following them. Recheck each hop,
subresource and navigation caused by an action. Restrict local previews to explicit
scheme/host/port origins in addition to hosts, so another loopback service is not
implicitly authorized. An approved hostname is not a DNS/IP sandbox; a task needing
network-level confinement must have that control separately.

Never treat post-navigation hostname inspection as prevention. If the provider
cannot enforce the required boundary, retain the operation as blocked/manual.
User-chosen authentication does not enlarge the destination allowlist.

## Concrete source adapter and its verification boundary

`skills/browse/scripts/chromium.mjs` is a small **single-page Chromium CDP adapter**.
It requires an explicitly selected existing Chromium/Chrome/Edge executable,
Node.js 22+ with built-in WebSocket/fetch, and Python 3.9+ for the accepted P03 helper.
It installs nothing. Use an already available suitable native host provider first;
missing-tool restoration is task-local only after a real failure and provenance/
license review. A failed TLS download is not permission to disable verification.

**Current observation boundary (2026-09-22):** Chrome 153 completed eight owned
headless synthetic scenarios: read/action/keyboard, extraction, screenshots,
printing and URL/popup/auth refusals. Actual screenshot pixels and two printed
pages' text/origins were inspected separately. This is not complete visual/PDF-raster
review, headed/login validation or repeatable full-pipeline acceptance. A later
run stopped at `EBUSY` reading its own `DevToolsActivePort`; native execution is
stopped again at that boundary. Earlier startup failures and unverified background
effects remain retained. Do not replace these observations with static checks,
claim the remaining gates passed, or start a configuration-variant search.

The module discovers the actual owned browser's `/json/protocol` and version.
Unsupported isolation/interception blocks navigation. Missing print support blocks
only print; independent permitted reading/actions remain available. The transport is
Node's built-in WebSocket; no Playwright package or assumed MCP API is involved.
The supplied executable's presence is checked separately from actual launch.

For every start it creates a unique run and **new** user-data directory. A successful
start must launch an
attached browser on a loopback debugging port and creates its own incognito
`browserContextId`. It never attaches to an existing browser or imports storage.
The default browser page is not read. The selected page must match the exact
`Target.createTarget` handle and arrive paused. Other owned startup targets are
closed while paused; request/response guards are installed before the selected
page resumes. An earlier auxiliary attachment cannot become the selected page.

The guard uses `Fetch.continueRequest(interceptResponse:true)`,
`Fetch.requestPaused`, P03 admission, then `Fetch.continueResponse`. An invalid
initial destination is refused before `Page.navigate`; an invalid redirect is
failed while its response is paused, before its destination request. Loop/hop
bounds remain enforced. This is deliberately not a general browser automation
runtime: extra page/worker targets, WebSockets, downloads, HTTP authentication,
password/file inputs and unsupported dialogs are refused or unsupported.
It does not claim full-page screenshots, DevTools, accessibility audits, network
timing, multi-context persistence or enterprise enforcement.

### Concrete API example

Run only inside an authorized environment with isolated HOME/USERPROFILE/temp,
explicit source/target roots and an already verified responding preview server.
The following is a caller recipe, **not evidence that it ran**:

```javascript
import { Admission, BrowserSession } from './skills/browse/scripts/chromium.mjs';

// Values below are supplied by the caller after the shared preflight.
const admission = new Admission({
  python: pythonExecutable,
  hosts: ['127.0.0.1'],
  origins: [previewOrigin],
});
const browser = await BrowserSession.start({
  executable: selectedBrowserExecutable,
  outputRoot: ownedRuntimeDirectory,
  admission,
  context: { session_id, work_map, profile_ref, source_revision },
});
try {
  await browser.open(`${previewOrigin}/preview`);
  const before = await browser.read('#result');
  await browser.act({ kind: 'fill', selector: '#name', value: 'Synthetic Ada' });
  await browser.act({ kind: 'click', selector: '#increment' });
  await browser.act({ kind: 'wait', selector: '#result', text: '1' });
  const after = await browser.read('#result');
  await browser.screenshot('screen.png');
  await browser.media({ print: true, reducedMotion: true });
  await browser.screenshot('print-media.png');
  await browser.print('preview.pdf');
  // Inspect actual before/after, images and printed content; retain the results.
} finally {
  await browser.close();
}
```

`read(selector, {html:true})` adds an explicitly requested DOM excerpt; avoid it on
sensitive pages. Reads refuse more than 1000 matched elements or 65536 characters,
rather than silently truncating evidence. Default reads include text, geometry, computed colors/animation,
media and focus state, not an accessibility certification. Actions accept only
click/fill/wait plus bounded page keys (Tab, Enter, Escape, ArrowUp/ArrowDown).
They resolve a single visible unobscured element and use browser input APIs.
Fill values are not copied into operation logs. Optional `captureConsole:true` at
start enables `consoleMessages()` for non-sensitive pages; it is off by default
and must stay off during authentication. Artifacts use new simple filenames
inside the owned run; overwrites and traversal are refused.

A policy refusal remains the primary operation error if its blocked input also
times out. The secondary provider error is retained separately; neither error is
converted to a successful action.

The browser data directory is unrelated to the P07 company-policy profile reference;
neither one establishes the other's availability or identity.

The native adapter does not interpret `--actions` YAML. The invoking skill maps
its already parsed goto/click/fill/wait_for/screenshot entries to the methods above.
`open-managed-browser --check` maps to `checkProvider(executable)` (no launch).
For a user-selected visible **fresh** surface use `headed:true`; authentication
and reuse of persistent profiles are not implemented by this fallback.

## Authentication and cleanup

Choose the login surface with the user, unless already specified. They enter
passwords/SSO/MFA themselves. Pause automated recording while they do so; never
transfer cookies, headers, credential values, browser history or storage-state
files between surfaces. Verify only an agreed non-secret marker after the user
confirms. A user report and an automation observation are different evidence.

Do not close a user-owned browser. For an invocation-owned browser, use the
created context ID and attached process, not a browser name/process search.
Close the context, observe process exit, then remove only its new temporary
profile. A failed shutdown leaves cleanup incomplete and data retained for an
explicit owned recovery. No persistent global configuration changes are involved.
Keep preview servers attached; observe a real health response and stop the exact
server handle after use.

## Evidence and P05 controls

The adapter retains provider schema, actual version/argv/PID, ownership, operations,
admission decisions and closure in each run. These are observations, not an
independent review record. Bind their paths/digests using the existing P05
`lib/review_contract.py`; do not invent a second success schema or QA inventory.

A browser control needs actual tool, `executed:true` and observed states. Missing
providers/measurements stay `unverified`; errors stay errors. Normal text below
4.5:1 (including 3.5:1) fails the existing contrast control. Static documentation
checks cannot stand in for keyboard interaction, reduced-motion behavior, layout
inspection or a printed artifact. Required policy/control failure cannot be
averaged away by other green results.

`tests/integration/design-browser-pipeline.sh` separates static/contract checks
from `--live --browser <absolute-executable>` observations against owned synthetic
loopback fixtures. The live scenario is designed to exercise read/action/screenshot/print,
redirects, refusals, keyboard/reduced motion and P05/P07/work-map links; only cases
that actually run count as observations. Its deny-only loopback proxy is private
fixture machinery, not a public browser proxy or proof of OS-wide egress isolation.
PDF inspection defaults to an installed `pdftotext`. An explicit
`--pdf-reader pypdf` selects an already installed Python reader instead; there is no
installation or silent fallback. Its transformed text origins are not complete
glyph bounds or PDF raster review. The recorded `pdftotext` crash and separately
denied native raster-inspection attempt remain failures, not replaced observations.
It is not an A14
design-renderer test, real login, all-client validation or physical-printer test.
