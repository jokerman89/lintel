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

Performance measurement with baseline comparison. Runs the repo's benchmark suite (or a hand-rolled measurement against a named scenario), records results, diffs against the last recorded run, surfaces regressions.

Not a profiler — that's `PerformanceAnalyzer` subagent territory. This skill is for repeatable measurement gates.

## When to use

- Pre-`/release-ev2` regression check on perf-sensitive code paths
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
- Optional `--baseline <ref>` — git ref to diff against (default: last recorded run)
- Optional `--iterations <N>` — runs per scenario (default: 5, take median)
- Optional `--warmup <N>` — warmup iterations not counted (default: 2)
- Optional `--save-as-baseline` — record this run as the new baseline

## Workflow

1. **Detect benchmark mechanism.** Check `package.json` for `bench` script, `pyproject.toml` for hyperfine/pytest-benchmark, repo-specific `bench/` directory. If none: ask operator to declare via `~/.lintel/perfbench.yaml`.
2. **Compliance gate.** Benchmarks that hit external services (production APIs, paid endpoints): require per-call auth. Local-only benchmarks: no gate.
3. **Warmup.** Run warmup iterations, discard.
4. **Measurement run.** N iterations. Capture per-iteration metrics: wall time, peak memory, allocations (if available), cold-start time (if applicable).
5. **Aggregate.** Median + p50/p95/p99 for time metrics. Mean for memory.
6. **Load baseline.** Read `~/.lintel/benchmarks/<repo>/<suite>-baseline.json`. If absent: this run becomes the baseline (no diff possible first time).
7. **Diff.** Compare each metric to baseline. Flag regressions at +5% (warn), +15% (P2), +30% (P1).
8. **Persist.** Write run results to `~/.lintel/benchmarks/<repo>/<ts>.json`. If `--save-as-baseline`: also overwrite baseline file.
9. **Report.**

## Report format

```
Benchmark: <repo> / <suite>

Suite: bench (5 scenarios, 5 iterations each, 2 warmup)
Baseline: 20260520-114000 (git: f19d388)

## Results

| Scenario           | Median  | p95     | Memory  | vs baseline           |
|--------------------|---------|---------|---------|-----------------------|
| cold-start         | 412 ms  | 487 ms  | 48 MB   | +3% time, ±0% mem ✓   |
| list-render-1k     | 87 ms   | 102 ms  | 12 MB   | +18% time ⚠ [P2]      |
| api-roundtrip      | 234 ms  | 312 ms  | 6 MB    | -2% time ✓            |
| db-query           | 18 ms   | 24 ms   | 2 MB    | ±0% time ✓            |
| serialize-large    | 45 ms   | 51 ms   | 8 MB    | +34% time ⚠ [P1]      |

## Regressions
[P1] serialize-large: 34 ms → 45 ms (+34%)
   Likely cause: src/lib/dlxClient.ts:87 (new validation pass added)
   Investigation: /investigate "serialize-large regression"

[P2] list-render-1k: 74 ms → 87 ms (+18%)
   Likely cause: src/components/portal/Cases.tsx (new render path)

## Recommendation
Address P1 before /release-ev2. P2 acceptable if intentional — record reason in commit message.
```

## Compliance integration

- Layer 2 production-mutation rule applies if a benchmark scenario hits production. Per-call auth required.
- Network-dependent benchmarks: warning if network conditions vary (results not comparable).
- Benchmark runs logged to `.claude/runtime/audit/benchmarks.jsonl`.

## Failure modes

- **No benchmark mechanism found:** report + suggest setting one up. Do not fabricate baseline.
- **Single iteration only (someone passed `--iterations 1`):** WARN — noise will be high. Recommend ≥3.
- **Iteration crashes:** mark that iteration NaN, continue with remaining. If all crash: report + bail.
- **Baseline file corrupted:** offer to delete + treat run as new baseline. Operator confirms.
- **Network flake on remote benchmark:** retry once per scenario. Persistent failure: skip scenario, mark in report.

## Examples

**Standard run:**
```
> /perfbench
[5 scenarios × 5 iterations]
3 regressions (1 P1, 1 P2). Address P1 before /release-ev2.
```

**Single scenario, deeper sampling:**
```
> /perfbench --scenario cold-start --iterations 20
[20 iterations, p99 calculated]
Median 412ms, p99 524ms. ±2% vs baseline.
```

**Set new baseline after refactor:**
```
> /perfbench --save-as-baseline
[Runs full suite, saves results as new baseline]
New baseline written. Prior baseline archived to .../baselines-archive/
```

## See also

- `PerformanceAnalyzer` subagent — for finding the bottleneck once `/perfbench` flagged a regression
- `/qa` — correctness; `/perfbench` is performance
- `/investigate` — for hypothesis-driven follow-up on a regression
- `/release-ev2` — reads benchmark results as advisory signal (regressions don't block by default; operator can opt-in)
