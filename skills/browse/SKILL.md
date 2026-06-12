---
name: browse
layer: foundation
description: Drive a headless Chromium to a URL — screenshot, extract DOM, click, fill forms, verify UI.
color: blue
tools: Read, Bash, Edit, Glob
voice: internal
cli_support: [claude-code]
---

# /browse

The browser-control skill. Launches a managed Chromium (Playwright under the hood), navigates to a URL, and performs the requested actions: screenshot, DOM extraction, click chains, form fills, console-log capture. Use for visual verification of frontend work, third-party site reconnaissance (within auth bounds), and any "I need to see what the user actually sees" task.

Codex and Copilot do not have native browser-control. This skill is `claude-code` only — operator running another CLI should run `/qa-only` against the deployed URL instead.

## When to use

- After a frontend change — verify the running app looks right
- Reproduce a UI bug reported by a user (with their sanitized URL/path)
- Take screenshots for `/design-review` or PR-attached visual evidence
- Sanity check a deploy: `https://staging.example.com` renders without console errors
- Extract a snippet of public-web content for citation (no auth)

## When NOT to use

- Bulk data extraction across many URLs — use `/scrape`
- PDF generation from page — use `/make-pdf`
- Authenticated session that needs cookies established first — run `/setup-browser-cookies` first
- Customer-data-bearing production page — STOP. Layer 2 customer-data rule blocks reads of prod data.

## Inputs

- Required: URL or local file path
- Optional `--actions <yaml>` — list of click/fill/wait/screenshot steps (inline or path to YAML)
- Optional `--viewport <WxH>` — default 1440x900
- Optional `--out <dir>` — where screenshots / DOM dumps land (default: `~/.lintel/browse-runs/<ts>/`)
- Optional `--headed` — show the browser window (default: headless)

## Workflow

1. **Preflight.** Verify managed Chromium present (run `/open-managed-browser --check` internally). If missing: surface install command.
2. **Compliance gate.** Check URL against Layer 2 patterns: if hostname matches `~/.lintel/compliance/prod-hosts.txt`, BLOCK with reason "production host — customer-data risk". Operator can override via explicit per-call confirmation.
3. **Launch.** Playwright with `--user-data-dir` pointed at the Lintel profile (so cookies established via `/setup-browser-cookies` persist).
4. **Execute actions.** Step through the action list. Each step logs to `~/.lintel/browse-runs/<ts>/trace.jsonl`. Console messages from the page captured to `console.log` in same dir.
5. **Capture.** Final screenshot (PNG) + DOM snapshot (HTML) saved.
6. **Report.** Summary of what was loaded, what was clicked, any console errors, paths to artifacts.

## Report format

```
Browse: https://app.example.com/portal

Viewport: 1440x900 (headless)
Duration: 4.2s
Actions: 3 (goto, click #login-btn, fill #email)

## Console
[error] Failed to load resource: net::ERR_NAME_NOT_RESOLVED (analytics.thirdparty.com)
[warn] Deprecated API: window.webkitURL
[log] x6 application-level logs (full content in console.log)

## Artifacts
- screenshot.png — 142KB (~/.lintel/browse-runs/20260527-160142/)
- dom.html — 87KB
- trace.jsonl — full action timeline
- console.log — page console output
```

## Compliance integration

- Layer 2 customer-data gate: production hosts blocked unless explicitly overridden + logged.
- Screenshot persistence: artifacts land in `~/.lintel/browse-runs/`. If `customer-data-block` hook is symlinked active, the hook may flag screenshots containing customer-data patterns and refuse upload to downstream skills.
- Auth state: managed via shared user-data-dir. Per-call auth NOT required for read-only navigation against authorized hosts (the cookie store itself was set up under explicit auth via `/setup-browser-cookies`).

## Failure modes

- **Chromium not installed:** print install command + exit. Do not silently fall back to a different browser.
- **URL unreachable (DNS, network):** report explicitly, distinguish from "loaded but empty page".
- **Page load timeout:** report partial DOM + screenshot at timeout. Capture is better than nothing.
- **Action fails (selector not found):** stop the action chain, report which step failed and surrounding DOM context.
- **Compliance block triggered:** STOP. Report which pattern matched. Do not auto-override.

## Examples

**Quick screenshot:**
```
> /browse http://localhost:5173
✓ Loaded in 1.1s, 0 console errors, screenshot.png 98KB
```

**Action chain:**
```
> /browse https://staging.example.com --actions actions.yaml
actions.yaml:
  - goto: /portal/login
  - fill: { selector: '#email', value: 'test@example.com' }
  - click: '#submit'
  - wait_for: '#dashboard'
  - screenshot: dashboard.png
✓ 4 actions complete, dashboard.png captured.
```

**Compliance-blocked:**
```
> /browse https://app.production.example.com
✗ BLOCKED — production host matches Layer 2 customer-data list.
  Override: rerun with --force-prod and a logged reason.
```

## See also

- `/scrape` — multi-URL extraction
- `/make-pdf` — page-to-PDF conversion
- `/setup-browser-cookies` — establishes auth for the managed profile
- `/open-managed-browser` — manual interactive session in the same profile
- `/qa` — for non-browser test verification
