---
name: sc-compliance-gap-warn
tier: warn-only
event: PreToolUse (Edit|Write on regulated-data paths)
fires_on: edit to a file in pack.security_compliance.regulated_path_glob, when no compliance evidence exists for required frameworks OR latest evidence shows gaps in covered controls
override: pass --ignore-compliance-gap flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# sc-compliance-gap-warn

Surfaces when an Edit/Write touches a regulated-data path with no current compliance evidence. Warning, not block — compliance gathering is recursive; the warn prompts operator to refresh evidence.

## What it does

- Reads `pack.security_compliance.regulated_path_glob` (or default heuristic — paths handling PII, payment data, health data)
- Reads `engineering.security_compliance.compliance_frameworks` from profile
- For each required framework: checks `.lintel/state/sc/compliance-evidence-<framework>.md` exists + recent (within 90 days)
- If gap detected (no evidence OR stale evidence OR known-gap controls): WARN

## Why warn-only

- Compliance is iterative; the system constantly evolves
- Block would interrupt operator flow for every regulated-path edit
- Warn forces operator to acknowledge + schedule evidence refresh

## Override path

`--ignore-compliance-gap "reason"` on the edit. Reason logged. CI can summarize override frequency per file/framework to surface evidence-refresh candidates.

## What's NOT in scope

- Auto-collecting evidence
- Identifying which specific controls apply (that's `/li:sc single --action compliance-evidence`)
- Blocking the edit

## Audit format

```jsonl
{"hook":"sc-compliance-gap-warn","tier":"warn","ts":"...","file_edited":"src/payments/processor.go","required_frameworks":"pci-dss","evidence_age_days":-1,"gap_count":3,"operator":"<operator>"}
```
