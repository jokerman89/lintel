# P01 third-candidate independent review

**Spec and preservation: PASS, all eight leaves. Quality: PASS.**
R1-R3 are closed on the exact product below. No new in-scope findings were identified:
**P1 0, P2 0, P3 0** in each stage.
This is scoped package acceptance, not integrated release, host activation or permission
to ship. **Combined P07 effective-profile/trusted-source acceptance remains open.**

| Identity | Exact value |
|---|---|
| Date | 2026-09-20 |
| Reviewer | CodeReview, same separate native `lintel-reviewer` session `6c55f7b0-1ea4-4955-a62b-a1c329f65e26`; not the builder |
| Original base | `21261f1ff76be994246060a7817924f2893f2454` |
| Reviewed product | `041417aa7174be732c6ac17624cd3759236a8800` |
| Frozen package snapshot | `5b2cd8ffda6132df00ff9ed29651ad489e4d1f5e` |
| Snapshot distinction | Parent is `041417a`; snapshot changes only `reports\P01.md` |
| First rejected product/snapshot | `c4542e48aa8968bdbe19e96ae1e85f191b9ad330` / `d6820a1b9fd8d92ed019e9eab25128b2c7699e0d` |
| First repair product/snapshot | `bf51fea9b61540a3235e1acb0babdd6da262eb2d` / `b5ae0067a44c83609211a19d58f61bdd90dcc88b` |
| Preserved first review | `4e848a94dc240fbe9641bd429dbc73b0395087a9`, `reviews\P01.md` |
| Preserved second review | `58f7bfe9179a62dbdb429523423a6bf953d76604`, `reviews\P01-recheck.md` |
| Current review branch | `jokerman-microsoft-universal-trusted-tools-final-review`, created clean at `5b2cd8f` |

The original two review branches still point to their original report commits. No reset,
history rewrite, source/builder/master worktree edit or original-report amendment occurred.
The approved work map, spec/plan/card, repository and adapter instructions, memory and
accepted decisions were verified unchanged from the earlier passes.

## Stage 1: source authority and old finding closure

Requirements remain the selected `work.json`, approved `spec.md`/`plan.md`,
`packages\P01.md`, A04/A25 and the explicitly authorized performance-metadata repair.
The unchanged producer is `agents\engineering\PerfBudgetEnforcer.md:49-57`;
`skills\tq\SKILL.md:85` pairs it with the hook. The producer's blob at original base
and current product is `dac19601388bc65f9a72da726918e6f1a78f835a`.
Its `<name>` and `<number>` domains were not rewritten to fit the consumer.

| Prior finding | Current disposition and evidence |
|---|---|
| R1: unrelated ADR staging | **CLOSED; closure retained.** `bin\li-adr-new:99-109` remains byte-identical to the independently accepted repair: the new ADR is the only commit path. The complete suite again verifies unrelated staged modifications/additions/deletions, newer worktree bytes, index entries and staged/unstaged diffs. An additional forced commit-failure fixture also preserves unrelated state and emits no committed-success message. |
| R2: scalar truncation/domain narrowing | **CLOSED.** `hooks\shared\tq-perf-regression-warn\run.sh:57-89,97-107` decodes text and validates complete numeric spelling without conversion. Fractional/exponent/core-integer forms and full journey names survive; invalid suffixes, quoted numeric strings, nonfinite/empty values and malformed supported scalars are explicit errors. Producer-derived positive fixtures and the exact corrected second-review program pass. |
| R3: incorrect path/record association | **CLOSED.** The same hook at `:91-156` selects the complete decoded path once for applicability and metadata, retains record boundaries, prefers `budget.p95_ms` and excludes other namespaces. Prefix/suffix/comment/other-key/regex decoys do not impersonate the target; optional absence does not borrow adjacent values. Independent namespace, document/sequence and nested-precedence probes also pass. |

The old `4e848a9` assertion demanding rejection of `120.5` remains historical and
superseded, not forced green. The exact corrected program from `58f7bfe` was executed
unchanged and passes, including `0.5`, `120.5`, path decoys and leading comments.
The historical report and its acknowledged oracle mistake were not edited away.

### Per-leaf acceptance and preservation

| Leaf | Verdict | Independently checked outcome |
|---|---|---|
| A25.1.a | PASS | Ten optional hook callers plus vault remain inventoried. Original-base hostile execution was independently reproduced in the first review; current tests confirm no target marker is executed. |
| A25.1.b | PASS | All ten hooks source implementation from their own tree, then trusted home fallback; source root is pinned independently of target data. Hostile target, stale source environment, installed-pack precedence, missing-resolver and positive/negative policy cases pass. |
| A25.1.c | PASS | Vault source/target separation, `--repo`, relative/explicit/configured paths, trusted resolver/template fallback, dry-run and disposable-vault non-overwrite/idempotency pass. Additional trusted-load/field-resolution/missing-source failures are explicit and leave destination bytes unchanged. |
| A25.2 | PASS | Target policy continues to change each domain decision. Existing rollback/cost/instrumentation/auth/evidence/consumer/contract behavior is preserved. Producer number/name values and correct record-owned optional metadata now pass. Dormant hooks stay dormant. |
| A25.3 | PASS | All 51 focused tests, the corrected three-case replay and five independent semantic methods pass with no skips. Coverage includes every modified trusted resolver caller, not just the last repair. |
| A04.1 | PASS | Documented title/status orders and negative arguments work; shell metacharacters/template tokens remain literal. A nested-cwd custom-template probe retains exact title content, status and customization. |
| A04.2 | PASS | Empty/existing/legacy ADR stores, decimal numbering and exact template contents pass. Only the generated ADR is committed; unrelated Git/worktree state survives both successful and failed commits. |
| A04.3 | PASS | Stubbed source fetch/pull, discovery/update failures, successful/failing Copilot install fallback, first-unrecovered status, independent-host continuation, dry-run and operator guidance pass. A recovered Copilot failure does not erase an earlier discovery failure. |

Stage 1 was explicitly completed before starting the quality stage. No acceptance was
weakened because a test count was green.

## Stage 2: first full bounded P01 quality review

**PASS: P1 0, P2 0, P3 0.** This stage was performed for the first time, after the
spec gate passed. It covered the cumulative base-to-current package, not only the
three-file third repair. The cumulative diff, complete current helpers/tests and
needed resolver/path/audit/input/caller context were considered. Previously read
unchanged domain bodies were checked against the pinned diff and exercised again.

| Quality area | Review and observed evidence |
|---|---|
| Trusted implementation boundary | Reviewed every modified resolver lookup and its downstream use of `LINTEL_SOURCE_ROOT`/`LINTEL_REPO_ROOT`. Existing own-tree/fallback prior art is reused; target manifests are data. Hostile/stale-environment and real synthetic-policy cases pass. No registration, shared resolver or installer change is hidden in the package. |
| ADR correctness and ownership | Reviewed parser, explicit value errors, decimal number selection, literal stock/custom rendering and Git operations. Success and forced failure preserve unrelated index/worktree contents. Failure exits 61 in the injected fixture, without `Committed on branch` or a changed HEAD. No reset/stash/automatic rollback is used. |
| Updater failures and recovery | Reviewed `run`, discovery, source-update subshell, fallback and aggregate status across all hosts. Tests assert commands actually invoked and the fallback's fixture artifact, not only status text. Explicit first failure remains 25 when Copilot recovers and Droid later fails. Cwd changes do not leak to independent host operations. |
| Metadata correctness and data handling | Reviewed scalar decoding, exact textual path equality, numeric validation without precision loss, namespace/depth handling, record boundaries, duplicate selected values, parser/read failures and output transport. A dynamic-looking journey remains literal in warning and JSONL audit; no command executes and `+1.205E+2` is unchanged. |
| Simplicity and maintainability | One checked metadata read and record-selection path replace divergent applicability/context scans. The bounded reader stays local to this hook; no dependency, general YAML engine, scheduler or shared policy rewrite was added. Documentation distinguishes supported single-line block fields from arbitrary YAML/host events. |
| Tests and evidence quality | Inspected fixture isolation, command stubs, actual Git state comparisons, source-derived producer examples and explicit error assertions. Existing tests remain; obsolete numeric expectations were corrected openly. Structural checks are not represented as runtime/host evidence. |

No broader pre-existing doctor/plugin-identity/profile/host-event issue is declared
fixed by this quality pass. Those boundaries remain outside A04/A25.

## Commands and outcomes actually observed

| Command/scenario | Result on the pinned current product |
|---|---|
| `python bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | Exit 0; approved explicit work map and paths verified. |
| `git diff --no-ext-diff --no-textconv <original-base> <product> -- bin` and owned hook/test diffs, plus direct file reads | Actual cumulative implementation, caller context and all test assertions inspected. |
| `bash --noprofile --norc tests\unit\universal-trusted-tools.sh` | **51 tests, 498.422 seconds, exit 0; no skips.** |
| Exact corrected Python program from `58f7bfe...:reviews/P01-recheck.md`, executed through `python -` | **3 tests, 15.881 seconds, exit 0; no skips.** |
| Independent semantic-boundary program via `python -`, five methods described below | **5 tests, 37.736 seconds, exit 0; no skips.** |
| Independent full-package quality program via `python -`, five methods described below | **5 tests, 7.470 seconds, exit 0; no skips.** |
| `bash --noprofile --norc tests\shape\hooks-registration-safe.sh` | Exit 0, ALL PASS; Node JSON validation ran. |
| `bash --noprofile --norc tests\unit\obsidian-patterns.sh` | Exit 0, ALL PASS on disposable vault data. |
| `bash --noprofile --norc tests\shape\tq-module-contract.sh` | Exit 0, all structural assertions pass. |
| `bash --noprofile --norc tests\unit\tq-routing.sh` | Exit 0, all structural scenarios pass. |
| `bash --noprofile --norc -n <each changed shell file>`; Python `ast.parse` of the fixture | All 14 changed shell files parse; Python AST parses. |
| `git diff --check <original-base> <product>` | Exit 0. |
| `git diff --quiet <product> -- bin hooks tests`; ancestry, path, mode and blob checks | Product remained exact; clean worktree before report creation; expected ownership and executable test mode. |

All symbolic table labels refer to the full immutable refs above. The four existing
scripts ran serially with a separate disposable environment per check. The fixture
driver was inspected before execution and uses temporary homes/source/target/vault,
isolated Git configuration and updater stubs. Actual Git Bash `usr\bin\bash.exe` was
used for supplemental programs, avoiding the previously recorded launcher/PATH issue.

The exact corrected replay command was:

```powershell
@'
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
ref = '58f7bfe9179a62dbdb429523423a6bf953d76604:.claude/plans/universal-implementation/reviews/P01-recheck.md'
report = subprocess.check_output(['git', '--no-pager', 'show', ref], text=True, encoding='utf-8')
program = report.split('```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(program, ref + ':source-contract-regressions', 'exec'))
'@ | python -
```

### Additional independent scenarios

The two inline standard-library programs loaded the committed fixture module with
`runpy.run_path(..., run_name="p01_fixtures")`, disabled bytecode writes, and explicitly
selected their own five methods each with `unittest`. Every case used fixture-local
files and `Fixture.bash`; temporary directories were cleaned up. These methods were
review probes, not new committed product tests.

| Semantic method | Concrete scenarios and asserted result |
|---|---|
| `test_nested_budget_wins_without_borrowing_flat_or_deep_namespace_values` | Nested `120.50` wins over flat `999` before/after the nested block, deeper `other.budget.p95_ms: 999`, and invalid `slo.p95_ms`. Exact `Checkout V2`/`120.50ms`, exit 0. |
| `test_matching_path_inside_another_namespace_does_not_select_a_record` | With nonmatching pack policy, `other.path` plus `other.budget` cannot select the edited file; exit 0 and no warning. |
| `test_document_boundaries_and_path_first_sequence_keep_metadata_owned` | `---`, `...` and Markdown fences separate a decoy from a path-first sequence record and a later record. Only selected `Checkout V2`/`1.205E+2ms` survives; no 999/888 contamination. |
| `test_invalid_or_duplicate_nested_budget_never_falls_back_to_valid_flat_value` | Invalid suffix, quoted numeric value or duplicate nested p95 refuses the record with diagnostic exit 1; a valid flat 777 does not turn failure into success. |
| `test_unselected_numeric_errors_do_not_contaminate_selected_record` | Invalid numeric metadata on an unrelated complete path does not corrupt selected `0.500`; exit 0 with exact spelling and no error. |

| Quality method | Concrete scenarios and asserted result |
|---|---|
| `test_failed_adr_commit_preserves_unrelated_state_and_never_claims_commit` | Git shim returns 61 only for commit and delegates other commands to real fixture Git. HEAD, unrelated index entries, cached/unstaged binary diffs and latest worktree bytes remain unchanged; no committed-success message. |
| `test_nested_cwd_and_literal_template_tokens_keep_exact_adr_content` | Invoke from `nested\context` with custom template and title `Data {{TITLE}} {{NNNN}} {{DATE}} & $HOME`. Literal title, accepted status and custom content remain; one expected ADR is created. |
| `test_trusted_load_resolution_and_missing_source_fail_without_target_code_or_vault_changes` | Trusted resolver returns 65 at load, returns 66 from field resolution, or is absent. Each yields explicit exit 1, no `Done.`, no hostile target marker and unchanged disposable destination bytes. |
| `test_successful_copilot_recovery_does_not_erase_prior_discovery_failure` | Gemini discovery 25, Copilot update 22 with successful install, Droid update 24: final exit stays 25; install marker and continued Droid invocation are verified. |
| `test_literal_dynamic_looking_name_and_numeric_text_survive_output_and_audit` | Journey ``Checkout $(touch metadata-executed) & `literal` `` and p95 `+1.205E+2` remain data in warning and parsed JSONL audit. Neither target resolver nor metadata command marker executes. |

The builder's latest old-`b5ae006` replay count of 56 expected failures was not rerun
in this pass and remains builder evidence. Earlier independent baseline/repair-red
replays remain recorded in the immutable prior reports. The current 51-test suite,
corrected replay and all additional pass results above are independently observed,
not accepted from the builder's report.

## Ownership and retained boundaries

From the original base, the cumulative package owns the same sixteen product/test/doc
paths: three `bin` helpers, ten optional hook scripts, TQ hook documentation and the
two focused test files. The latest repair changes only the TQ performance hook, its
documentation and the Python fixture. Other helpers/hooks, resolver/input/audit
libraries, producer/dispatch, registration, common plan and memory are unchanged.
The report-only frozen snapshot changes only the builder report.

`hooks\hooks.json` remains blob `07506e49733298bad28ee4c1d59aa01e01e6134b` at base and
current product; all ten affected optional hooks remain unregistered. The focused
shell entry point remains mode `100755`. No new dependency or installation occurred.
This review's only authored repository file is `reviews\P01-final.md`.

The four existing checks were independently rerun on this product. The other eleven
checks in the builder's historical fifteen-script list were not rerun here.
No full repository suite, CI, ShellCheck, native Linux/macOS/Bash 3.2, fresh consumer
installation, actual client/model update or real vault check was performed.
The path-scalar fixture's environment transport tests literal parser input; it does
not prove every Windows native argv/host event path. The reader is not a general
YAML parser; its documented producer/legacy block-field limits remain explicit.

No account, credential, remote/network, global-configuration, live/private update,
hook activation, extra-agent, external publication or production operation was
performed. No mandatory enterprise or private-pack enforcement was claimed from
the neutral synthetic fixtures. Updater stubs prove subprocess contract behavior,
not current vendor CLI/network success.

**Disposition:** P01 may proceed to coordinator integration with all eight leaves and
both package-review stages accepted for this immutable product. Preserve both prior
reports and their corrected oracle history. The joint **P07 profile/trusted-source
gate**, combined-tree regression/consumer/platform checks and final integrated
independent review remain required; this report does not discharge them.
