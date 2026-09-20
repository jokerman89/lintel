---
name: tq-perf-regression-warn
tier: warn-only
event: PreToolUse (Edit|Write on perf-budget paths)
fires_on: edit to a file in pack.testing_qa.perf_path_glob OR identified as on a critical journey by .claude/runtime/state/tq/perf-budget-*.md
override: pass --ignore-perf-regression flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# tq-perf-regression-warn

Surfaces when an edit touches a perf-budget-bound path. Warning, not block — the actual regression check happens at run-time; the warn prompts operator to think about budget impact.

## What it does

- Detects perf-bound paths from `pack.testing_qa.perf_path_glob` or the latest perf-budget spec at `.claude/runtime/state/tq/perf-budget-*.md`
- Loads resolver code from its own installation or `LINTEL_HOME`, never the inspected repository. Project pack files remain data; the hook remains opt-in.
- For matched files: WARN
- Journey and p95 metadata are optional: a pack-only match still warns without a budget file or matching metadata. A failed metadata read or malformed present value is reported with non-blocking exit 1, not represented as a successful empty read.

## Budget metadata

Metadata lookup matches the edited path as literal text, never as a regular expression.
For the first matching entry, `journey` is read from the preceding line and `p95_ms`
from the following five lines, stopping before another `journey` or `path` entry.
Missing fields do not borrow values from a neighboring entry.

This warning reads a bounded scalar format, not general YAML: an unquoted `journey`
contains only lowercase letters and underscores (`[a-z_]+`); `p95_ms` contains only
decimal digits (`[0-9]+`), representing nonnegative whole milliseconds. Values are
preserved verbatim, including zero and leading zeros. Fractional values, numeric
suffixes and journey suffixes outside these patterns are explicit errors, not
truncated values.

Fields may be indented or prefixed with a YAML list marker (`- `). Spaces/tabs around
the scalar and an inline `#` comment separated from it by whitespace are supported.
Comment-only lines and differently named keys are not metadata fields.

```yaml
journey: checkout
path: custom/[id].txt
p95_ms: 120 # whole milliseconds
```

## Why warn-only

- Edit-time can't predict runtime perf
- The actual regression check is in CI (perf-budget enforcement)
- Block would be too aggressive at edit-time

## Override path

`--ignore-perf-regression "reason"` on the edit. Reason logged.

## Audit format

```jsonl
{"hook":"tq-perf-regression-warn","tier":"warn","ts":"...","file_edited":"src/api/search.go","journey":"search","budget_p95_ms":150,"operator":"<operator>"}
```
