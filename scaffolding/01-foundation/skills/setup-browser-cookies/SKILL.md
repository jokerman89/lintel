---
name: jstack-setup-browser-cookies
description: Bootstrap auth cookies for the managed Chromium profile — operator-driven, one-time per service.
color: orange
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code]
---

# /setup-browser-cookies

Establishes authenticated cookies in the JStack-managed Chromium profile so that subsequent `/browse` and `/scrape` runs can hit logged-in pages without re-auth.

Operator-driven by design: the skill launches a headed (visible) browser, the operator logs in manually using their actual SSO or password manager, and on close the cookies persist in the managed user-data-dir. No password ever enters this skill's prompt.

## When to use

- First time you need `/browse` or `/scrape` against a page behind login
- After cookie expiry (typically every 7-30 days depending on the service)
- After a password rotation that invalidated old sessions
- Switching managed profile (e.g. personal vs work account separation)

## When NOT to use

- The service has API tokens — use the API instead; cookies are fragile and short-lived
- Production customer-bearing system — STOP. Layer 2 customer-data gate blocks; the right move is sanitized fixtures
- Service requires MFA on every login and you can't store an MFA token — skill won't help; live `/browse` with manual MFA each time is the workflow

## Inputs

- Required `--service <name>` — friendly name for the service (used in cookie store labeling)
- Required `--login-url <url>` — the URL where login lives
- Optional `--profile <name>` — managed profile to use (default: `default`)
- Optional `--check` — verify existing cookies are still valid (visits a known authed page, checks for redirect)

## Workflow

1. **Compliance gate.** Hostname checked against Layer 2 prod-host list. If matched: BLOCK.
2. **Launch headed Chromium.** With persistent user-data-dir at `~/.jstack/browser-profiles/<profile>/`.
3. **Operator login.** Browser navigates to `--login-url`. Skill prints "Waiting for operator login. Press Enter here when logged in."
4. **Verify.** When operator confirms, skill navigates to a service-known authed URL (per `~/.jstack/browser-profiles/services.yaml`) and checks for non-login response.
5. **Persist + close.** Cookies are already on disk (persistent profile); skill just confirms presence + closes browser.
6. **Register service.** Append metadata to `~/.jstack/browser-profiles/services.yaml`: service name, last-validated-at, login URL, validation URL.
7. **Report.** Confirmation + expiry estimate (read from cookie max-age if available).

## Workflow (--check mode)

1. Launch headless Chromium with same profile.
2. Navigate to the service's validation URL.
3. If logged in: print OK + report cookie freshness.
4. If redirected to login: print STALE + recommend re-run without `--check`.

## Report format

```
Setup browser cookies: github.com

Profile: default (~/.jstack/browser-profiles/default/)
Login URL: https://github.com/login
Validation URL: https://github.com/settings/profile

[Headed browser launched. Operator logged in at 16:14:03.]

✓ Validated — settings page loaded as logged-in user
Cookies persisted to profile
Estimated expiry: ~30 days (based on max-age headers)
Service registered in services.yaml
```

## Compliance integration

- Layer 2 prod-host gate ALWAYS applies — you cannot bootstrap cookies against a customer-data-bearing prod host through this skill. Use sanitized staging/test environments.
- Profile dir permissions: `~/.jstack/browser-profiles/` should be `chmod 700` (skill verifies + warns if loose).
- NEVER prompts operator for passwords. NEVER captures keystrokes. NEVER reads the browser's password autofill store.
- Cookie store excluded from gstack/jstack brain-sync by default (per Layer 2 secrets-rule). If sync is enabled: a hook will block.

## Voice tier note

`voice: internal`. Setup operations are engineering-internal — concrete steps, no narrative.

## Failure modes

- **Operator never confirms login:** 5-minute timeout, then skill closes browser + reports no-confirmation. Cookies that ARE present will still persist.
- **Validation URL fails (got redirected to login):** report STALE state. Operator can retry, possibly with a different account.
- **Profile dir permissions too open:** print chmod 700 fix command + ask whether to apply.
- **Browser crash during login:** report + ask operator to retry. Cookies from a clean shutdown will persist; from a crash may not.
- **Service has rotating cookies (every request):** cookies persist but may not survive idle time. Note this limitation; operator should run `--check` more often.

## Examples

**First-time setup for GitHub:**
```
> /setup-browser-cookies --service github --login-url https://github.com/login
[Headed browser opens. Operator logs in.]
✓ Validated. Cookies stored, est. 30 days.
```

**Check existing:**
```
> /setup-browser-cookies --service github --check
✓ Cookies fresh, last validated 4h ago, settings page loaded.
```

**Stale cookies:**
```
> /setup-browser-cookies --service github --check
✗ STALE — redirected to /login. Re-run without --check to refresh.
```

## See also

- `/browse` — uses the cookies set up here
- `/scrape` — same
- `/open-managed-browser` — manual interactive session in the same profile
- Layer 2 compliance — secrets handling, profile permissions
