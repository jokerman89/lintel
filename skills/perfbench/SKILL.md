---
name: perfbench
layer: foundation
v1_alias: [li-benchmark]
description: Measure performance — runtime, memory, cold-start — and detect regressions vs baseline.
color: yellow
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /perfbench

Performance measurement with an explicitly selected comparable baseline. Uses the
repo's existing suite or an authorized named scenario, preserving every observation.

Not a profiler — that's `PerformanceAnalyzer` subagent territory. This skill is for repeatable measurement gates.

## When to use

- Pre-`/li:ship` regression check on perf-sensitive code paths
- After a hot-path refactor, confirm you didn't slow things down
- Periodic baseline capture for trend monitoring
- A teammate said "this feels slower" — instrument it

## When NOT to use

- One-off profiling to find a bottleneck — use `PerformanceAnalyzer` subagent
- No benchmark suite exists and no scenario can be defined — set one up first
- Comparing against a CI machine baseline from your laptop — apples to oranges, results misleading

## Inputs

- Optional `--suite <name>` — named benchmark suite (default: repo's `bench` script)
- Optional `--scenario <name>` — single named scenario (e.g. `cold-start`, `large-list-render`)
- Optional `--baseline <ref>` — explicit comparable recorded baseline/ref, not newest file by mtime
- Optional `--iterations <N>` — runs per scenario (default: 5, take median)
- Optional `--warmup <N>` — warmup iterations not counted (default: 2)
- Optional `--save-as-baseline` — record this run as the new baseline

## Workflow

1. **Detect benchmark mechanism.** Read the existing manifest/suite. If absent, obtain
   a named scenario and explicit local invocation; do not invent a global config reader.
2. **Check effects.** Inspect scripts/hooks/network/data before execution; local
   commands can still mutate shared systems. Use owned synthetic home/temp and exact
   target authority. Production/paid endpoints need their own explicit approval.
3. **Warmup.** Distinguish steady-state from cold-start measurement; warming the
   very cold-start path being measured invalidates that scenario.
4. **Measurement run.** N iterations. Capture per-iteration metrics: wall time, peak memory, allocations (if available), cold-start time (if applicable).
5. **Aggregate.** Report sample count, raw distribution and uncertainty. Five runs
   cannot support precise p99 claims. Retain failures separately, never silently drop them.
6. **Load baseline.** Read the explicitly selected repository-local artifact and
   verify source/env/workload/build/runtime identity. Missing baseline means no comparison,
   not permission to replace history automatically.
7. **Diff.** Report effect size versus the actual approved budget and baseline noise,
   not blanket severity from 5/15/30 percent. Hand cause diagnosis to PerformanceAnalyzer.
8. **Persist.** The authorized caller records named results under the selected safe
   operation/iteration path. `--save-as-baseline` needs an explicit owned destination,
   original preimage and retained previous reference; no global store or silent overwrite.
9. **Report.**

When part of TQ/mapped work follow [the shared procedure](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
and [comparison methods](../tq/references/decision-methods.md). Actual P05 tests/check
obligations are fixed before observations. Record runs/exits, environment, immutable
evidence and unrun scope; independent review and final QA are not a self-awarded score.
An unmapped measurement stays an inspection, not a new task ledger.

## Report format

```
Benchmark: <repo> / <suite>

Suite: synthetic report shape; actual scenarios/samples/warmup and confidence recorded per run
Baseline: 20260520-114000 (git: f19d388)

## Results

| Scenario           | Median  | p95     | Memory  | vs baseline           |
|--------------------|---------|---------|---------|-----------------------|
| cold-start         | 412 ms  | 487 ms  | 48 MB   | +3% time, ±0% mem ✓   |
| list-render-1k     | 87 ms   | 102 ms  | 12 MB   | +18% time; assess impact |
| api-roundtrip      | 234 ms  | 312 ms  | 6 MB    | -2% time ✓            |
| db-query           | 18 ms   | 24 ms   | 2 MB    | ±0% time ✓            |
| serialize-large    | 45 ms   | 51 ms   | 8 MB    | +32% time; assess impact |

## Regressions
[Unclassified] serialize-large: 34 ms → 45 ms (+32%, rounded)
   Hypothesis to test: validation pass; comparison alone does not isolate the cause
   Investigation: /investigate "serialize-large regression"

[Unclassified] list-render-1k: 74 ms → 87 ms (+18%)
   Hypothesis to test: new render path

## Recommendation
Assign severity from measured user impact and applicable policy; the illustrative
percent changes alone do not establish a blocker or acceptance exception.
```

## Compliance integration

- Layer 2 production-mutation rule applies if a benchmark scenario hits production. Per-call auth required.
- Network-dependent benchmarks: warning if network conditions vary (results not comparable).
- Claim logging only after actual authorized persistence; a pathname is not a receipt.

## Failure modes

- **No benchmark mechanism found:** report + suggest setting one up. Do not fabricate baseline.
- **Insufficient sampling:** state the unavailable inference; choose repetitions from
  observed variance and meaningful effect size, not a universal minimum for all metrics.
- **Iteration crashes:** preserve failure/exit and incomplete scenario; no nonfinite
  success record or averaging it away. Rerun only after effects/conditions are understood.
- **Baseline corrupted:** preserve it, block comparison and request an explicit new
  baseline decision; deletion is not a recovery prerequisite.
- **Remote flake:** retain actual failure and authority boundary; skipped required
  scenarios stay unverified, not a successful aggregate.

## Examples

**Standard run:**
```
> /perfbench
[5 scenarios × 5 iterations]
Report observed changes, failures and uncertainty; severity needs actual impact/policy.
```

**Single scenario, deeper sampling:**
```
> /perfbench --scenario cold-start --iterations 20
[20 iterations retained; tail uncertainty stated, not a precise p99 guarantee]
Median and spread reported against an actually comparable baseline.
```

**Set new baseline after refactor:**
```
> /perfbench --save-as-baseline
[After explicit destination/preimage authority, persist and read back the baseline]
Report actual new and retained old paths/digests; a failed write is not a new baseline.
```

## See also

- `PerformanceAnalyzer` subagent — for finding the bottleneck once `/perfbench` flagged a regression
- `/qa` — correctness; `/perfbench` is performance
- `/investigate` — for hypothesis-driven follow-up on a regression
- `/li:ship` — consumes the actual required/advisory QA obligation; required performance failures block
