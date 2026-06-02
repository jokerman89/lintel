---
name: tq-perf-regression-warn
tier: warn-only
event: PreCommit on perf-budget paths
fires_on: edit to a file in pack.testing_qa.perf_path_glob OR identified as on a critical journey by .lintel/state/tq/perf-budget-*.md
override: pass --ignore-perf-regression flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# tq-perf-regression-warn

Surfaces when an edit touches a perf-budget-bound path. Warning, not block — the actual regression check happens at run-time; the warn prompts operator to think about budget impact.

## What it does

- Detects perf-bound paths from `pack.testing_qa.perf_path_glob` or the latest perf-budget spec at `.lintel/state/tq/perf-budget-*.md`
- For matched files: WARN

## Why warn-only

- Edit-time can't predict runtime perf
- The actual regression check is in CI (perf-budget enforcement)
- Block would be too aggressive at edit-time

## Override path

`--ignore-perf-regression "reason"` on the edit. Reason logged.

## Audit format

```jsonl
{"hook":"tq-perf-regression-warn","tier":"warn","ts":"...","file_edited":"src/api/search.go","journey":"search","budget_p95_ms":150,"operator":"jokerman"}
```
