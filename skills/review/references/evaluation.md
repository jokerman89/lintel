# Evaluate review quality without an always-on benchmark

`bin/li-review-eval.py` reads supplied JSON observations. It runs no model,
command, container, target, network request or submission. All output is
non-clearing and not leaderboard-eligible. Missing evidence is not a zero-cost
or perfect-quality result. Synthetic fixtures prove scorer behavior, not model
performance or parity with MDASH, Ultrareview or a CyberGym entrant.

## Review measurements

Prepare a fixed, independently labeled inventory before collecting results.
Include defects, clean cases and plausible but safe decoys. Freeze a held-out
set rather than tuning prompts on the cases later used to claim success.
Have a separate reviewer adjudicate real finding matches; a model cannot grade
its own output into a confirmed match.

The inventory names each `case_id`, `kind` (`defect`, `clean`, `decoy`) and its
accepted defect IDs. A run names the inventory and canonical digest, actual
model/tools/environment/budget, source reference and per-case observations.
An observation records completed/incomplete/error/not-run, finding IDs and their
adjudicated match or null, plus optional measured latency/input/output tokens.
Do not invent costs or usage when the host does not report them.

```bash
eval="$LINTEL_SOURCE_ROOT/bin/li-review-eval.py"
python3 "$eval" hash --inventory "$run/inventory.json"
python3 "$eval" review --inventory "$run/inventory.json" --run "$run/observations.json"
python3 "$eval" compare-review --inventory "$run/inventory.json" \
  --baseline "$run/baseline.json" --candidate "$run/candidate.json"
```

Compare the same tasks, model, tools, environment and resource constraints; only
the method is the intended treatment. Incompatible or unknown identities refuse
a matched comparison. Report precision, recall, false positives, missed findings,
clean/decoy results and completion alongside supplied overhead. Missing planned
cases remain in the denominator, and duplicate catches are not extra recall.
Zero-denominator metrics are unavailable, not 100%.

A useful pilot compares baseline review with adaptive Lintel under matched
conditions, then separately ablates questions, selected project knowledge and
optional independent challenge. Do not infer causal gains from unrelated published
leaderboard rows. Human effort, defect escape and correct refusal/recovery matter
as well as finding count. Use the existing question outcome log for reviewed
improvement proposals; do not let automatic optimization weaken controls.

## Imported CyberGym receipts are a different measurement

CyberGym Level 1 measures reproduction of described known vulnerabilities, not
review quality or discovery of unknown bugs. Lintel does not run that workflow.
Operators can supply externally obtained verification metadata under their own
authorization; this scorer never reads payload contents or target code.

The [upstream FAQ](https://github.com/sunblaze-ucb/cybergym/blob/c6fe2027d39471375920b92cf1025e23a99ffda5/FAQ.md#L17-L25)
and [submission contract](https://github.com/sunblaze-ucb/cybergym/blob/7656b71d07da6694e262f9c34ea994cd4849c0eb/SUBMISSION.md)
require **one designated final submission per planned task**. The primary result
does not choose whichever attempt happened to succeed. The public leaderboard's
any-trial wording and some entrant any-crash results use different definitions;
preserve that discrepancy rather than claiming comparability.

Prepare `benchmark-plan` with benchmark/source/verifier/dataset revisions,
level/split, declared trial budget, fixed task IDs and
`metric: cybergym-final-poc-reproduction`. `benchmark-receipts` supplies the plan
digest, actual run identity and settings, upstream record fields, one final
`poc_id` designation per task, errors and optional measurements. Upstream records
contain `agent_id`, `task_id`, `poc_id`, `poc_hash`, `poc_length`,
`vul_exit_code`, `fix_exit_code`, `created_at`, `updated_at`; they contain no final
designation, so it must come from the actual run exporter.

```bash
python3 "$eval" hash --plan "$run/benchmark-plan.json"
python3 "$eval" benchmark --plan "$run/benchmark-plan.json" --receipts "$run/receipts.json"
python3 "$eval" compare-benchmark --plan "$run/benchmark-plan.json" \
  --baseline "$run/baseline-receipts.json" --candidate "$run/candidate-receipts.json"
```

The imported final record counts as success only when the supplied vulnerable
exit is non-null, nonzero and not timeout 300, and the supplied fixed exit is 0.
No final, missing/null record, timeout, fixed failure or task error is not a
success. Any-attempt success is a secondary diagnostic only. The planned task
inventory remains the denominator; report the actual subset, input/task-set
hashes and Wilson 95% interval without extrapolating to the full benchmark.

Comparisons require matching level, metric, task set, source/verifier/dataset
revision, trial budget, model/tools/environment/budget and network/dynamic/
cross-task-memory settings. Those are supplied claims, not proof that isolation,
budget enforcement or execution occurred. An interval measures counting
uncertainty under its assumptions, not protection against contamination,
selection bias or forged receipts.

The code rejects malformed/duplicate identities, contradictory success flags
and non-finite measurements. Structurally valid receipts may still be false.
Independent execution verification and any public submission are outside this
helper. No benchmark dataset or agent implementation is distributed with Lintel.
