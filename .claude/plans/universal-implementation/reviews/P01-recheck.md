# P01 same-reviewer repair review

**Spec and preservation: FAIL.** R1 is closed; R2 and R3 have narrower fixes but
still fail the requested source-contract/preservation checks. Six leaves pass;
A25.2 and A25.3 remain open. **Quality: NOT RUN**, because spec has not passed.
The 43-test green result and unchanged original supplemental program do not establish
package acceptance.

| Identity | Exact value |
|---|---|
| Date | 2026-09-20 |
| Independent reviewer | CodeReview, same native `lintel-reviewer` session `6c55f7b0-1ea4-4955-a62b-a1c329f65e26`; not the builder |
| Original base | `21261f1ff76be994246060a7817924f2893f2454` |
| Earlier rejected product | `c4542e48aa8968bdbe19e96ae1e85f191b9ad330` |
| Earlier rejected snapshot | `d6820a1b9fd8d92ed019e9eab25128b2c7699e0d` |
| Earlier immutable review | `4e848a94dc240fbe9641bd429dbc73b0395087a9`, `reviews\P01.md` |
| Reviewed repaired product | `bf51fea9b61540a3235e1acb0babdd6da262eb2d` |
| Reviewed frozen snapshot | `b5ae0067a44c83609211a19d58f61bdd90dcc88b` |
| Review branch | `jokerman-microsoft-universal-trusted-tools-recheck`, created clean at the frozen snapshot |
| Stage 1 open severities | P1 **0**, P2 **2**, P3 **0** |
| Stage 2 severity counts | Not assessed; not a zero-finding quality pass |

The original report remains unchanged on branch
`jokerman-microsoft-universal-trusted-tools-review` at `4e848a9`.
No reset, original-report overwrite or other-worktree modification was used.
Ancestry confirms `d6820a1` precedes the repair and `b5ae006` has parent `bf51fea`.
The frozen snapshot changes only the builder's `reports\P01.md`.

## Spec authority and old findings

The mapped approved spec, plan, P01 card, repository/adapter instructions, memory and
decisions are unchanged from the first review. The explicit work-map validator passes.
This pass inspected the complete repair diff and added tests, reread the repaired
helpers/report, and checked the scalar domain against the unchanged TQ dispatch,
`PerfBudgetEnforcer` output and TQ concept documentation. Earlier inspected package
surfaces were verified unchanged; the entire focused behavioral suite was rerun.

| Old finding | Disposition on this product |
|---|---|
| P01-R1, unrelated ADR staging | **CLOSED.** `bin\li-adr-new:103-104` stages the generated ADR and uses `git commit --only -- "$FILE"`. The original counterexample passes. The expanded fixture at `tests\unit\universal-trusted-tools.py:605-642` also preserves unrelated staged modifications, additions and deletions, newer worktree bytes, index entries, cached binary diff and unstaged binary diff. Only the ADR appears in the commit. No reset/stash recovery was introduced. |
| P01-R2, incomplete scalar validation | **PARTIAL; P2 remains.** Whole-scalar garbage such as `120oops` and `120 999` now fails explicitly, and valid integer spelling/comments are preserved. However, the new integer-only domain is not established by the producer contract and rejects valid fractional numeric budgets. See R2 below. |
| P01-R3, literal path extraction | **PARTIAL; P2 remains.** Bracketed filenames and regex-decoy fixtures now work; missing fields no longer borrow the tested adjacent records. Fixed-string substring matching still selects a different path's record or a comment before the actual record. See R3 below. |

### P01-R2 - P2: the repair narrows the producer's numeric budget without authority

**Product:** `hooks\shared\tq-perf-regression-warn\run.sh:72-84`.
**New documentation:** `hooks\shared\tq-perf-regression-warn\HOOK.md:28-33`.
**Affected leaves:** A25.2, A25.3. **Confidence:** high on the contract mismatch and
reproduced behavior.

`skills\tq\SKILL.md:85` explicitly pairs this hook with the per-journey budget producer
`PerfBudgetEnforcer`. That producer declares `p95_ms: <number>` at
`agents\engineering\PerfBudgetEnforcer.md:49-57`, not an integer or whole-millisecond
field. The producer is byte-identical at original base and repaired product:
`dac19601388bc65f9a72da726918e6f1a78f835a`. The relevant TQ source describes measured
latency budgets, without a whole-millisecond restriction.

Both `p95_ms: 0.5` and `p95_ms: 120.5` now return exit 1 with
`invalid p95_ms budget metadata` and no warning output. These are valid numeric
millisecond budgets, not suffix garbage. The appended HOOK.md restriction and new test
at `tests\unit\universal-trusted-tools.py:351` cannot create authority to narrow the
producer's supported domain. The previous unanchored `[0-9]+` extraction was the defect
being repaired, not a shared numeric schema.

**Review-oracle correction:** my original supplemental program required exit 1 for
`120.5`; I replayed it unchanged and it passes. That assertion was too restrictive
without checking the producer. The earlier report said supported values must be
preserved, but its exact program did not establish whether decimals were supported.
This pass corrects that evidence limitation rather than treating a green old assertion
or newly added prose as permission for value loss. The original report is retained.

**Required repair:** preserve complete numeric values supported by the producer,
including fractional milliseconds, while rejecting complete invalid scalars. Align
the consumer description/tests to the existing producer contract; do not redefine
valid data as invalid merely to satisfy a regex. Any deliberate narrower product
domain needs a separate authorized contract decision, not a repair-only docs change.
This finding does not ask for general YAML parsing or a redesign of the domain module.

### P01-R3 - P2: the first substring occurrence is not the edited path's record

**Product:** `hooks\shared\tq-perf-regression-warn\run.sh:44-46,54-56,66-84`.
**Affected leaves:** A25.2, A25.3. **Confidence:** high (reproduced).

`grep -F -m1 -- "$file_edited"` removes regex interpretation but still matches a
substring anywhere in the file, not a complete `path` field. With edited file
`custom/[id].txt`, put either `path: custom/[id].txt.bak` or
`path: other/custom/[id].txt` before the exact record. The hook exits 0 and reports
the decoy's `journey: decoy, p95 budget 999ms`, instead of the target's
`journey: checkout, p95 budget 120ms`.

A leading comment `# Updated notes for custom/change.txt` also wins `-m1` over the
actual record. The hook then returns 0 with both present metadata fields omitted.
The first-match change makes a comment permanently mask the actual record for that
invocation. The adjacent-record stop cannot fix this: extraction already started
from the wrong source.

The repaired cases at `tests\unit\universal-trusted-tools.py:393-448` discriminate
regex decoys and missing adjacent values, but do not exercise substring/comment
decoys. Correctly matching a filename literally is necessary, not sufficient to
associate metadata with its record.

**Required repair:** select the actual complete path value/record, then read optional
fields belonging to that same record. Do not let comments, prefixes, suffixes or
other fields impersonate a path entry. Keep the passing bracket, absence, adjacent
record, read-failure and comment-scalar cases. This is the approved extractor boundary,
not broader canonical host-event/path normalization.

## Per-leaf preservation and spec decision

| Leaf | Verdict | Evidence and boundary |
|---|---|---|
| A25.1.a | PASS | Previously inventoried ten hooks plus vault; initial-base hostile reproduction remains in the immutable first review. Current suite reruns hostile caller coverage without target-marker execution. |
| A25.1.b | PASS | All ten trusted lookups are unchanged by repair. Own installation/home fallback and stale source-environment tests pass; target policy still affects each decision. |
| A25.1.c | PASS | Vault lookup is unchanged; hostile target, explicit/configured path, `--repo`, home/template fallback, disposable install/idempotency and dry-run pass again. |
| A25.2 | FAIL | Policy and domain heuristics/evidence remain effective, with dormant registration preserved. R2/R3 still violate metadata domain/source preservation. |
| A25.3 | FAIL | All 43 committed tests pass without skips, but the additional applicable source-contract regressions fail. |
| A04.1 | PASS | Title/status order and error cases, literal metacharacters, custom/stock templates and help pass again. |
| A04.2 | PASS | Decimal IDs, empty/existing/legacy stores and exact contents pass. Expanded dirty-index and original reviewer fixtures verify unrelated Git state and worktree preservation. |
| A04.3 | PASS | Unchanged updater passes stubbed discovery/fetch/pull/host failures, real fallback invocation in the fixture, successful/failing fallback outcomes, aggregation, continuation and dry-run again. No real host-update claim. |

**Aggregate:** six of eight leaves pass; two remain open. P01 is not accepted.
No extra failure is counted for the same root cause in both A25.2 and A25.3.

## Executed evidence

| Command/scenario actually run | Observed result |
|---|---|
| `python bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | Exit 0; approved selected map verified. |
| `git show bf51fea... -- bin hooks` and `git diff d6820a1... bf51fea... -- tests` | Inspected the complete four-file repair, not just its report. |
| `bash --noprofile --norc tests\unit\universal-trusted-tools.sh` | **43 tests, 324.225 seconds, exit 0; no skips.** |
| Execute the exact Python block from `4e848a9...:reviews/P01.md`, unchanged, via `git show` and `python -` | **3 tests, 14.201 seconds, exit 0; no skips.** Confirms R1, original scalar assertions and bracket-path counterexample are fixed; scalar-oracle limitation above applies. |
| Replay the six new committed repair methods against fixture copies from `d6820a1...` | **6 tests, 19 expected assertion/subtest failures, 62.874 seconds, exit 1; no errors/skips.** Independently confirms the builder's red-count claim. |
| Supplemental source-contract program below, executed as a PowerShell here-string piped to `python -` | **3 tests, 5 assertion/subtest failures, 15.127 seconds, exit 1.** Two substring decoys, two fractional values, one leading comment. |
| `bash --noprofile --norc tests\shape\hooks-registration-safe.sh` | Exit 0, all assertions pass; Node JSON validation ran. |
| `bash --noprofile --norc tests\unit\obsidian-patterns.sh` | Exit 0, all assertions pass against disposable vault data. |
| `bash --noprofile --norc tests\shape\tq-module-contract.sh` | Exit 0, all structural assertions pass. |
| `bash --noprofile --norc tests\unit\tq-routing.sh` | Exit 0, all structural scenarios pass. |
| `bash --noprofile --norc -n <each changed shell file>` and `ast.parse` of the Python fixture | Fourteen Bash files parse; Python AST parses. |
| `git diff --check <original-base> <repaired-product>` | Exit 0. |
| Immutable ancestry, diff-name allowlists and `git diff --quiet <repaired-product> -- bin hooks tests` | Expected scope and exact product bytes retained; worktree clean before report creation. |

Abbreviated refs in this table resolve to the full SHAs in the identity table.
Existing scripts ran in separate disposable environments with `HOME`, `USERPROFILE`,
`XDG_CONFIG_HOME`, `LINTEL_HOME`, audit and Git configuration isolated; inherited
Lintel/Claude/Copilot/Git overrides were sanitized. Supplemental programs used actual
Git Bash `usr\bin\bash.exe`, not the PATH-prepending launcher. No updater command in
these checks could use a real source/home/remote; the updater's committed stubs were
inspected previously and remain unchanged.

The red replay used current committed test methods but replaced only the fixture
copies of `bin\li-adr-new` and `hooks\shared\tq-perf-regression-warn\run.sh` with
`git show d6820a1...:<path>` bytes. Its six selectors were:

```text
Adr.test_adr_commit_preserves_unrelated_index_and_worktree
TrustedHooks.test_performance_metadata_requires_complete_scalars
TrustedHooks.test_performance_metadata_preserves_valid_values_and_comments
TrustedHooks.test_performance_metadata_treats_filenames_literally
TrustedHooks.test_performance_metadata_does_not_select_regex_decoys
TrustedHooks.test_performance_missing_metadata_does_not_borrow_adjacent_records
```

### Reproducible source-contract regressions

This exact program was executed from the pinned worktree inside a PowerShell
single-quoted here-string piped to `python -`. It only creates and cleans disposable
fixtures; it does not modify the reviewed product.

```python
import runpy, shutil, subprocess, sys, unittest
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
root = Path.cwd()
bash = subprocess.check_output([shutil.which('bash'), '--noprofile', '--norc', '-c', 'cygpath -w "$BASH"'], text=True).strip()
sys.argv = ['p01-recheck-source-contract', bash]
m = runpy.run_path(str(root / 'tests' / 'unit' / 'universal-trusted-tools.py'), run_name='p01_fixtures')
write = m['write']
class MetadataSourcePreservation(m['Fixture']):
    def test_complete_path_value_selects_its_own_record(self):
        path = 'custom/[id].txt'
        self.set_policy('custom/*')
        write(self.target / path, 'fixture\n')
        budget = self.target / '.claude/runtime/state/tq/perf-budget-recheck.md'
        for decoy in (path + '.bak', 'other/' + path):
            with self.subTest(decoy=decoy):
                write(budget, f'journey: decoy\npath: {decoy}\np95_ms: 999\n\njourney: checkout\npath: {path}\np95_ms: 120\n')
                result = self.bash(self.source / 'hooks/shared/tq-perf-regression-warn/run.sh', path)
                print('PATH_SOURCE:', repr({'path': path, 'decoy': decoy, 'rc': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}), flush=True)
                self.assertFalse(self.marker.exists())
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('journey: checkout', result.stdout)
                self.assertIn('p95 budget 120ms', result.stdout)
                self.assertNotIn('journey: decoy', result.stdout)
                self.assertNotIn('999ms', result.stdout)
    def test_path_mention_in_comment_does_not_hide_actual_record(self):
        path = m['CUSTOM_PATH']
        write(self.target / '.claude/runtime/state/tq/perf-budget-recheck.md', f'# Updated notes for {path}\n\njourney: checkout\npath: {path}\np95_ms: 120\n')
        result = self.bash(self.source / 'hooks/shared/tq-perf-regression-warn/run.sh', path)
        print('COMMENT_SOURCE:', repr({'rc': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}), flush=True)
        self.assertFalse(self.marker.exists())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('journey: checkout', result.stdout)
        self.assertIn('p95 budget 120ms', result.stdout)
    def test_numeric_producer_domain_preserves_fractional_milliseconds(self):
        path = m['CUSTOM_PATH']
        budget = self.target / '.claude/runtime/state/tq/perf-budget-recheck.md'
        for value in ('0.5', '120.5'):
            with self.subTest(value=value):
                write(budget, f'journey: checkout\npath: {path}\np95_ms: {value}\n')
                result = self.bash(self.source / 'hooks/shared/tq-perf-regression-warn/run.sh', path)
                print('NUMBER_DOMAIN:', repr({'value': value, 'rc': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}), flush=True)
                self.assertFalse(self.marker.exists())
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f'p95 budget {value}ms', result.stdout)
suite = unittest.defaultTestLoader.loadTestsFromTestCase(MetadataSourcePreservation)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
```

## Ownership, limits and next gate

The repair changes only `bin\li-adr-new`,
`hooks\shared\tq-perf-regression-warn\run.sh`, its `HOOK.md`, and
`tests\unit\universal-trusted-tools.py`. The complete product package still has the
same sixteen owned implementation/test/doc paths as the first review. The report-only
snapshot updates the builder's report. No shared helper/profile/registration change
is hidden in the repair. Base and repaired `hooks\hooks.json` remain the same blob:
`07506e49733298bad28ee4c1d59aa01e01e6134b`; all ten domain hooks remain unregistered.

Only this `reviews\P01-recheck.md` is authored by the reviewer in the new branch.
Product repairs, common plan/state/memory writes, source/builder/master worktree edits,
additional agents and external publication remain prohibited and were not performed.
No real vault/update, hook activation, global configuration change, account/credential
operation, network call, full repository suite or CI run occurred.

Four of the builder's fifteen existing scripts were rerun here; the other eleven
remain builder-reported for this repair. Full integration, fresh consumer installation,
native Linux/macOS/Bash 3.2 and actual host/model acceptance are unverified.
**P07 joint effective-profile/trusted-source acceptance is still an explicit integration
gate**; no substituted future resolver or passing package fixture discharges it.

**Quality verdict: NOT RUN.** Do not treat this spec-only recheck as the full-package
quality stage previously deferred. Return R2/R3 to the builder, preserve R1's verified
index/worktree behavior, and request a new immutable candidate. After spec passes,
perform quality review of the complete bounded P01 package, not only these repairs.
P01, A25.2 and A25.3 remain open.
