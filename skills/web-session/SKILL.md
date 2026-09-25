---
name: web-session
layer: foundation
description: Use to browse, extract pages, open an owned browser or validate user-managed sign-in through an actual provider with explicit URL admission and lifecycle evidence.
color: blue
tools: Read, Write, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /web-session

One browser entrypoint with explicit modes. Select the current host's actual
provider and permission before operating; this skill installs no browser,
daemon, MCP server or credentials. The concrete local provider and extraction
module are retained under `scripts/`, not replaced by instructions to find a tool.

## Modes

Use `--mode browse|scrape|open|cookies`; omitted mode means `browse`.
Reject unknown, duplicate or conflicting options before page access or output.
Mode-specific options belong only to their selected mode. These are skill
arguments, not flags for an invented `web-session` executable.

| Mode | Preserved inputs and outcome | Procedure |
|---|---|---|
| `browse` | URL/local artifact, `--actions`, `--viewport`, `--out`, `--headed`; open/read/act/screenshot/print/close | [Browse](references/browse.md) |
| `scrape` | `--urls`, `--schema`, `--concurrency`, `--rate-limit`, `--diff`; structured extraction and comparison | [Extract pages](references/scrape.md) |
| `open` | `--url`, `--profile`, `--devtools`; explicitly owned operator-visible session. `--check` is non-launch provider preflight | [Open a session](references/open.md) |
| `cookies` | `--service`, `--login-url`, `--profile`, validation URL/marker; user-managed login. `--check` checks only that selected authorized context | [Authentication](references/cookies.md) |

All modes follow [browser operations and ownership](references/browser-operations.md):
actual discovery, current work/profile references, exact hosts and origins,
pre-navigation request/redirect admission, scoped artifacts and owned cleanup.
Authentication never grants cookie export/import or wider navigation permission.
An inaccessible user-chosen surface remains a manual task, not authorization to
transfer its session elsewhere.

## Provider and consumers

`scripts/chromium.mjs` exposes `Admission`, `checkProvider`, `BrowserSession`,
`artifactName` and `validateAction`. `scripts/extract.mjs` exposes `validateSchema`,
`extractPage` and `diffRecords`. The local provider requires an explicitly selected
installed Chromium-family executable, Node.js 22+ and Python 3.9+; it installs
nothing and preserves its single-page, no-credential boundaries.

Use `frontend-design-review` for built UI critique, `generate-web --mode mockup`
for static HTML authoring, and `generate-pdf` for composition/print choices. Printing
does not imply PDF text, dimensions or rendered-page inspection passed.

PDF and other consumers use these canonical resources through the existing
installed dependency inventory. Temporary resource bridges were removed after
those consumers were joined; they are not a second provider or entrypoint.
Missing installed resources remain an explicit integrity failure, not permission
to load a personal browser copy or a retired path.

## Evidence

Report mode, actual provider/API/version, requested versus supported operations,
work/profile references, owner/handles, admitted destinations, real observations,
artifact paths and cleanup. Record blocked, failed and unattempted work separately.
Source checks are not browser execution; preflight is not launch; a screenshot is
not an accessibility audit; a PDF file is not completed inspection. Required
missing observations remain unverified under P05.
