---
name: open-managed-browser
layer: foundation
v1_alias: [li-open-gstack-browser]
description: Open the Lintel-managed Chromium in headed mode — interactive operator session.
color: blue
tools: Bash
voice: internal
cli_support: [claude-code]
---

# /open-managed-browser

Simple launcher: opens the same managed Chromium that `/browse` and `/scrape` use, but in headed mode for the operator to drive directly. Same persistent profile, same cookie store. Use when you want to do manual work (debug, screenshot, explore) without scripting it.

Name preserves continuity with the gstack `/open-managed-browser` convention even though we're in Lintel — the alternative (`/open-li-browser`) is less recognizable, and operators carry muscle memory across both stacks.

## When to use

- Manually debug a UI bug — easier to drive a real browser than script `/browse`
- Verify a `/setup-browser-cookies` session interactively
- Explore a third-party site before writing a `/scrape` schema
- Inspect a deployed staging build hands-on

## When NOT to use

- Scripted/repeatable browser work — use `/browse`
- Bulk data extraction — use `/scrape`
- Customer-data-bearing production page — STOP. Layer 2 customer-data gate.

## Inputs

- Optional `--profile <name>` — managed profile to use (default: `default`)
- Optional `--url <url>` — open directly to this URL (otherwise opens to about:blank)
- Optional `--check` — verify Chromium is installed + profile dir is healthy, do not actually launch
- Optional `--devtools` — open with DevTools pane visible

## Workflow

1. **Check Chromium binary.** Locate the managed install. If absent: print install command + exit.
2. **Profile dir.** Verify `~/.lintel/browser-profiles/<profile>/` exists + is writable + `chmod 700`. Create with correct perms if missing.
3. **Optional compliance.** If `--url` is set AND hostname matches Layer 2 prod-host list: BLOCK + ask for override reason.
4. **Launch.** `chromium --user-data-dir=<profile-path> [--url <url>] [--auto-open-devtools-for-tabs]`. Process detaches; skill returns immediately.
5. **Report.** PID, profile path, URL (if any), reminder of cookie state (last-validated services).

## Workflow (--check mode)

1. Confirm binary exists.
2. Confirm profile dir healthy.
3. Print services registered in this profile (from `services.yaml`).
4. Exit without launching.

## Report format

```
Open Lintel browser

Binary: ~/.lintel/bin/chromium (v124.0.6367.x)
Profile: default (~/.lintel/browser-profiles/default/)
URL: about:blank
PID: 47821

## Registered services in this profile
- github.com (validated 4h ago)
- stage.example.com (validated 2d ago)
- internal.docs.example.com (validated 9d ago, may be stale)

Browser detached. Close manually when done.
```

## Compliance integration

- Same Layer 2 prod-host gate as `/browse` — if `--url` is set and hits a prod host, it blocks.
- Profile dir perms verified (chmod 700) — if loose, surface fix.
- If `audit-mode` is on per `~/.lintel/config.yaml`: log the launch event with timestamp + profile + URL.
- Browser process is detached and runs under operator's user — anything they do in it is THEIR action, not skill-mediated.

## Failure modes

- **Chromium binary missing:** print exact install command, exit. Do not fall back to system Chrome (which is unmanaged + may have personal cookies).
- **Profile dir broken (permissions, corruption):** offer to back up + recreate.
- **Compliance block on `--url`:** report + offer override path (--force-prod + reason).
- **Launch succeeds but process dies in <1s:** report crash, suggest re-running `--check` to verify install.

## Examples

**Just open it:**
```
> /open-managed-browser
✓ Launched headed Chromium, PID 47821, profile=default.
```

**Open to a URL:**
```
> /open-managed-browser --url http://localhost:5173
✓ Launched to http://localhost:5173, PID 47823.
```

**Diagnose install:**
```
> /open-managed-browser --check
✓ Binary OK, profile healthy. 3 services registered.
```

## See also

- `/browse` — scripted browser work
- `/scrape` — multi-URL extraction
- `/setup-browser-cookies` — bootstrap auth in this same profile
- `/make-pdf` — PDF generation using the same browser
