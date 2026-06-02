---
name: tq-coverage-drop-warn
tier: warn-only
event: PreCommit
fires_on: commit drops aggregate or critical-path coverage below threshold from profile
override: pass --ignore-coverage-drop flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# tq-coverage-drop-warn

Surfaces when a commit drops coverage below the configured threshold. Warning, not block — sometimes coverage drops are unavoidable (deleted dead code); operator decides.

## What it does

- Reads thresholds from `~/.lintel/profile.yaml` `engineering.testing_qa.coverage_target` (default 80) + `critical_path_coverage` (default 100)
- Compares current coverage report against thresholds
- If below: WARN

## Why warn-only

- Coverage drops can be legitimate (test removal alongside code removal, refactor-with-paired-test-changes)
- Block would interrupt routine refactor work
- Warn forces operator to acknowledge

## Override path

`--ignore-coverage-drop "reason"` on commit. Reason logged. CI can flag repeated overrides as test-debt candidates.

## Audit format

```jsonl
{"hook":"tq-coverage-drop-warn","tier":"warn","ts":"...","coverage_pct":78,"target_pct":80,"critical_below":1,"operator":"jokerman"}
```
