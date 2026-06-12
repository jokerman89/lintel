---
name: ta-contract-collision-warn
tier: warn-only
event: PreToolUse (Edit|Write on declared interface files)
fires_on: edit to a file matching pack.tech_architecture.interface_glob OR with declared consumers via .claude/runtime/state/ta/consumer-registry.json
override: pass --ignore-contract-collision flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# ta-contract-collision-warn

Surfaces when an Edit/Write hits an interface file with known consumers. Warning, not block — interface evolution is normal; the warn prompts operator to consider consumer impact before merging.

## What it does

- Reads pack policy: `pack.yaml.tech_architecture.interface_glob` (e.g. `**/api/*.proto`, `**/*.openapi.yaml`)
- Reads consumer registry: `.claude/runtime/state/ta/consumer-registry.json` (populated by `/li:ta contract-collision` or operator)
- If edited file matches interface_glob OR appears in registry: WARN with consumer count + suggestion to run `/li:ta single --action contract-collision`

## Why warn-only

- Most interface edits are additive (new endpoint, new field) — backward-compat
- Operator has full context; hook just prompts the consideration
- Block would be too aggressive for the common case

## Override path

`--ignore-contract-collision "reason"` on the edit operation. Reason logged to audit. CI can inspect override frequency per interface.

## What's NOT in scope

- Running the full contract-collision analysis (that's `/li:ta contract-collision`'s job)
- Identifying consumers automatically (the sub-skill populates the registry)
- Blocking based on consumer count (warn-only by design)

## Audit format

```jsonl
{"hook":"ta-contract-collision-warn","tier":"warn","ts":"...","file_edited":"api/v1/user.proto","consumer_count":7,"operator":"<operator>"}
```
