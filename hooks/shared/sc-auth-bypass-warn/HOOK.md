---
name: sc-auth-bypass-warn
tier: warn-only
event: PreToolUse (Edit|Write on auth-flow files)
fires_on: selected filename has matches in the existing case-sensitive text-count regexes
audit: .claude/runtime/audit/hooks.jsonl
---

# sc-auth-bypass-warn

An existing optional **filename/regex heuristic**, not an authentication or
authorization proof. It reads the existing file named by the hook input (or manual
path argument), not a before/after diff or proposed future content. It cannot
establish that an edit introduced a reachable bypass. Nothing here enables the hook.

## What it does

- Selects filenames containing `auth`, `oauth`, `saml`, `jwt`, `session`, `login`
  or `middleware`, or optional comma-separated `security_compliance.auth_flow_glob`
  data. Filename selection is not actual authentication-flow discovery.
- Uses the four existing **case-sensitive** count regexes in `run.sh` for
  skip-auth-looking assignments, a small set of username-like literals, named
  route fragments and direct-role-looking assignments. Comments/strings can match;
  syntax, reachability, credential validity and access checks are not analyzed.
- Reports counts of matching lines per category and their sum, not line numbers,
  distinct vulnerabilities or severity. One line can contribute to several counts.
- Any positive total emits WARN and exits zero; no match or no selected file is
  silence, not proof of correct authorization.
- The shared text reader treats filenames as literal operands. A grep/read
  failure emits an unavailable-observation warning and keeps the optional hook
  non-blocking; it is not converted to a clean zero count or a successful scan.

## Why warn-only

- Text patterns alone cannot distinguish a real defect from inert documentation.
- The warning invites `/li:sc single --action auth-flow` review of actual trust
  boundaries; it does not force or record an acknowledgement.

## Policy and scope

There is no acknowledgement/override option parser. Optional filename data is
explained by the [preference reference](../../../skills/da/references/preferences.md).
Missing optional advice is benign; actual resolver/profile errors retain nonzero
failure. The conditional filename lookup is not a universal profile gate. Real
required profile/review controls remain required and are not satisfied by a warning.

## What's NOT in scope

- Proving either authentication or authorization correctness
- Auto-fixing patterns
- Hook activation, scanner expansion, live checks or mandatory policy

## Audit format

Only a warning calls the existing `audit_log hooks sc_auth_bypass_warn` router
with string fields `hook`, `tier`, `file_edited`, comma-separated `patterns` counts
and `total`. The router supplies common metadata and the actual destination.
It can fail advisory writes; absence of a record is not a successful auth review.
