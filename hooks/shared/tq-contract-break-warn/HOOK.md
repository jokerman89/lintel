---
name: tq-contract-break-warn
tier: warn-only
event: PreCommit on provider files
fires_on: edit to a provider file (matching pack.testing_qa.provider_glob OR identified by .lintel/state/tq/contract-test-suite-*.md) without paired contract-test update
override: pass --ignore-contract-break flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# tq-contract-break-warn

Surfaces provider edits without paired contract-test update. Warning, not block — sometimes provider changes are purely internal; operator decides.

## What it does

- Detects provider files via pack `testing_qa.provider_glob` or recent contract-test-suite
- Checks for paired contract-test changes in same commit
- If provider changed without contract-test update: WARN

## Why warn-only

- Internal refactors don't change contract; contract test unchanged is correct
- Block would interrupt routine refactors
- Warn forces operator to confirm change is contract-preserving

## Override path

`--ignore-contract-break "reason"` on commit. Reason logged.

## Audit format

```jsonl
{"hook":"tq-contract-break-warn","tier":"warn","ts":"...","file_edited":"src/api/users.go","contract_test_updated":false,"operator":"jokerman"}
```
