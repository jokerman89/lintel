---
name: setup-browser-cookies
layer: foundation
description: Use to keep login on the user's chosen browser surface and verify authorized signed-in state without copying cookies or credentials.
color: orange
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /setup-browser-cookies

Preserved authentication entry point for `/browse` and `/scrape`, using the
[shared browser operations](../browse/references/browser-operations.md). The name
does **not** authorize cookie export/import. Authentication remains on the user's
chosen browser/provider surface, with the user entering credentials and MFA.

## When to use

- First authorized visit to a test or other permitted authenticated service.
- Revalidation after session expiry or account changes.
- Explicit separation of two user-selected test accounts/surfaces.

Prefer a supported authorized API when browser sessions are unsuitable. Customer
systems and production data are not substitutes for sanitized fixtures. Session
setup does not authorize later reads, form submissions or scraping.

## Inputs

- `--service <name>`: non-secret friendly label.
- `--login-url <url>`: user-selected login destination, when login is requested.
- `--profile <name>`: optional opaque session label resolved only by the chosen
  provider/user; never a path to search in personal browser storage.
- `--check`: recheck **only** the explicitly selected authorized session.
- Validation URL plus expected visible signed-in marker: ask if not already known.
  A 200 response, cookie file or populated profile directory is not that marker.

## Establish authentication

1. Resolve the approved work/profile/policy and intended account/service scope.
   Ask which surface the user wants when not already selected: their own browser,
   a host-managed visible session, or a fresh isolated provider context.
2. Inspect the actual provider's isolation, visibility and persistence API before
   opening anything. If it cannot demonstrably use that chosen surface, stop only
   automated authentication and give a manual handoff. Do not switch surfaces or
   copy cookies to make the workflow appear successful.
3. Validate login and validation URLs through P03. Identity-provider redirects
   need explicit authorized hosts/origins too. Do not learn an allowlist by first
   visiting an unapproved redirect target.
4. The **user** logs in using their normal password manager/SSO/MFA flow. Never ask
   for a password/token, capture login keystrokes, inspect the password store, save
   storage-state files or submit credential changes. Stop automated snapshots,
   console/DOM capture and traces while the user is authenticating.
5. After the user confirms, use only a permitted non-sensitive marker or their
   explicit attestation to assess sign-in. Distinguish `observed in selected
   context` from `user-reported; automation unverified`. A login redirect or
   missing marker is stale/unverified, not proof of which account is present.
6. Retain only necessary non-secret metadata in the selected work's gitignored
   runtime: service label, provider/context owner, authorized validation URL,
   checked time, observed marker/result and persistence limitations. Do not create
   a fictional global `services.yaml`, inspect cookies for expiry or invent a
   "30 day" freshness estimate.
7. Keep or close the session according to the user's choice and provider's real
   lifetime. Do not claim a closed ephemeral context retains authentication.

## `--check` mode

Use the already selected context only if its owner authorized this check and the
provider proves that same context is accessible. Validate the destination and all
redirects before following them. Observe the agreed non-secret signed-in marker.
Return one of: observed signed-in, observed login/stale, user-attested only,
blocked, or unverified with the exact reason.

If only a profile directory remains, engine execution and sign-in are both
unverified. Do not launch another browser, reuse a personal session, or inspect
cookie databases to repair that gap.

## Concrete local-provider boundary

`skills/browse/scripts/chromium.mjs` requires a fresh isolated context and declares
an optional headed launch. Its complete native launch/interaction acceptance is
currently blocked on the recorded host; do not treat these source methods as
verified login support. Its methods refuse password/file inputs and HTTP
authentication challenges and never supply credentials. It implements no
persistent profile reuse, SSO transfer, cookie export/import or global service registry.

A user may choose that visible ephemeral surface for a permitted manual login
with separately scoped observation afterward. They may instead keep login in
their ordinary browser and supply non-sensitive manual evidence. Neither choice
is silently converted into authenticated automation on another surface.

## Failure handling and report

If the user does not confirm within the agreed waiting period, report no
confirmation; do not close their own browser or infer saved cookies. On crash,
expiry, MFA challenge or unknown persistence, retain the exact limitation and
offer the same chosen-surface workflow, not a cookie-copy recipe.

Report service/surface choice, owner, actual provider operation (or none),
validation observation/attestation, lifetime and unresolved checks. No cookie
contents, credential values, account identifiers or personal profile paths belong
in evidence, memory, sync or committed artifacts.
