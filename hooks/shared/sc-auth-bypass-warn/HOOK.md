---
name: sc-auth-bypass-warn
tier: warn-only
event: PreToolUse (Edit|Write on auth-flow files)
fires_on: edit to a file in auth-flow surface with high-risk patterns (bypass routes, skip-auth flags, magic-credential checks, hardcoded admin paths)
override: pass --ignore-auth-bypass flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# sc-auth-bypass-warn

Surfaces when an Edit/Write to an auth-flow file introduces or modifies high-risk patterns. Warning, not block — bypass mechanisms have legitimate uses (test fixtures, admin tools); operator decides.

## What it does

- Detects auth-flow files (matches patterns or paths under `pack.security_compliance.auth_flow_glob`)
- Scans for high-risk patterns:
  - bypass routes (`/admin/skip-auth`, `/test/login-as-anyone`)
  - skip-auth flags (`skipAuth: true`, `if test_env { return user }`)
  - magic-credential checks (hardcoded user/pass combos)
  - role-elevation paths (any code path that sets admin role without check)
- If detected: WARN with the pattern + line

## Why warn-only

- Test fixtures legitimately bypass auth for fast iteration
- Admin tooling sometimes needs special paths (but should still log)
- Block would be too aggressive; warn forces operator to acknowledge

## Override path

`--ignore-auth-bypass "reason"` on the edit. Reason logged. CI can flag PRs with repeated overrides as auth-review candidates.

## What's NOT in scope

- Detecting authorization bypasses (different layer — that's RBAC analysis, not auth-flow)
- Auto-fixing patterns
- Blocking the edit (warn only)

## Audit format

```jsonl
{"hook":"sc-auth-bypass-warn","tier":"warn","ts":"...","file_edited":"src/auth/middleware.go","pattern":"skip-auth-flag","line":42,"operator":"<operator>"}
```
