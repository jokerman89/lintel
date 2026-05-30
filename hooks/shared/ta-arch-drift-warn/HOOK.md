---
name: ta-arch-drift-warn
tier: warn-only
event: PreToolUse (Edit|Write on ADR-claimed files)
fires_on: edit to a file path listed in any ADR's "decisions" block
override: pass --ignore-arch-drift flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# ta-arch-drift-warn

Surfaces when an Edit/Write hits a file path claimed by an ADR's `decisions:` block. Warning, not block — operator may have legitimate reason to revise the architectural decision (in which case the ADR should be updated too).

## What it does

- Scans `.lintel/decisions/*.md` (and `docs/decisions/`, `docs/adr/`) for ADRs with `decisions:` frontmatter listing file paths
- Compares the path being edited against the ADR-claimed set
- If match: WARN with ADR id + decision summary

## Why warn-only

ADRs codify decisions but don't freeze them. Operators evolve architectures. The warn surfaces the prior decision so the operator can choose: (a) update the ADR, (b) deliberately diverge (audit-logged), or (c) reconsider the edit.

## Override path

`--ignore-arch-drift "reason"` on the edit operation. Reason logged to audit. CI may inspect override frequency per file to surface ADR-update candidates.

## What's NOT in scope

- Detecting indirect contradictions (e.g. a change that violates an ADR through a dependency chain)
- Blocking the edit (warn only — operator decides)
- Auto-updating the ADR (operator-driven; ADRDrafter agent can be invoked separately)

## Audit format

```jsonl
{"hook":"ta-arch-drift-warn","tier":"warn","ts":"...","file_edited":"src/auth/jwt.go","adr_id":"ADR-007","adr_decision":"JWT signing key rotation policy","operator":"jokerman"}
```
