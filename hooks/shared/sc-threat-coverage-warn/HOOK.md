---
name: sc-threat-coverage-warn
tier: warn-only
event: PreToolUse (Edit|Write on auth/data files)
fires_on: edit to a file in pack.security_compliance.threat_surface_glob OR matching auth/data heuristic, when no recent threat-model exists OR file not covered by latest threat model
override: pass --ignore-threat-coverage flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# sc-threat-coverage-warn

Surfaces when an Edit/Write touches a security-surface file with no recent threat-model coverage. Warning, not block — threat surfaces evolve; the warn prompts operator to refresh the model.

## What it does

- Reads `.claude/runtime/state/sc/threat-model-<latest>.md` if present (within 90 days)
- Resolves pack policy `pack.security_compliance.threat_surface_glob` (defaults to auth/data/api file patterns)
- For matched files: checks whether the file is referenced in the latest threat model
- If no threat model exists OR file not covered: WARN

## Why warn-only

Threat modeling is recursive — every iteration improves coverage. Warning prompts the operator to either: (a) extend the threat model, (b) deliberately defer (audit-logged), or (c) reconsider whether this is actually a security surface.

## Override path

`--ignore-threat-coverage "reason"` on the edit. Reason logged.

## What's NOT in scope

- Auto-extending the threat model (operator-driven via `/li:sc single --action threat-model`)
- Blocking the edit (warn only)
- Detecting indirect threats (the model itself produces those)

## Audit format

```jsonl
{"hook":"sc-threat-coverage-warn","tier":"warn","ts":"...","file_edited":"src/auth/oauth.go","threat_model_age_days":-1,"file_in_model":false,"operator":"<operator>"}
```
