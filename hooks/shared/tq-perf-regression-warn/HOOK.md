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

The [TQ dispatch](../../../skills/tq/SKILL.md) pairs this hook with
[PerfBudgetEnforcer](../../../agents/engineering/PerfBudgetEnforcer.md), whose output
declares `journey: <name>` and `budget.p95_ms: <number>`. The consumer does not narrow
these to lowercase identifiers or whole milliseconds.

The reader selects the first record whose complete `path` scalar equals the edited
path. Prefixes, suffixes, comments and other fields cannot select a record. Both
budget-based applicability and metadata use that same selection; pack-only matches
still warn when there is no record. Missing fields never borrow another record's
values.

Per-journey block mappings start with `journey`; a path-only record may omit it.
A new journey/path, sequence item, YAML document boundary or Markdown code fence
ends the preceding record. Sequence records support either journey/path order.
All fields in the selected record are considered, without a fixed line window.
The producer's nested `budget.p95_ms` is preferred; the existing flat `p95_ms`
annotation is still supported. SLO and other nested fields do not supply the budget.

Numeric scalars retain their complete spelling, including fractions (`0.5`, `120.5`),
signs, decimal exponents, zero/leading zeros and YAML hexadecimal/octal integers.
Validation does not convert or round the number or impose a new budget-range policy.
Malformed suffixes, empty values, strings in numeric fields and nonfinite tokens
such as `.inf`/`.nan` are errors. A journey name may contain uppercase letters,
digits, punctuation and spaces; its complete value is retained.

This is a reader for the producer's single-line block fields, not a general YAML
parser. Indentation, sequence markers, plain/single/double-quoted text scalars and
whitespace-separated inline comments are supported. Quoted text supports doubled
single quotes and escaped double quotes, backslashes, slashes and tabs. Multiline
text/escape forms are not interpreted. Comment-only lines and differently named
keys are not metadata fields. Invalid selected scalars and read/parser failures
produce diagnostics and exit 1, not a successful metadata-absent warning.

```yaml
journey: Checkout v2
path: custom/[id].txt
budget:
  p95_ms: 120.5 # fractional milliseconds are preserved
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
