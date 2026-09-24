# P13 installed-consumer closure review

**Verdict: scoped SPEC PASS, then eligible QUALITY PASS_WITH_ADVISORY_P3.**
Findings: P1 0 / P2 0 / P3 2. N1 is a measured CI-duration input and N2 is an
ineffective fixture-root guard in new test code; neither blocks the unit. This is an
independent review of the released installed obligations of original A18.3, A18.4 and
A19.4. It is not acceptance of those original leaves, whole P13, A19.3, the version or
generated fan-in, or any P10/platform/policy clearance. The reviewer changed no product,
test, owner report or shared state; this file is the only addition.

## Frozen scope

Reviewer: new independent session "P13 installed review"
`30146eab-ddeb-467e-8f1b-8da575256ba2`, assigned by coordinator88. Its own host
`session.start` event records `claude-opus-5.5`, reasoning `max` and context
`long_context`, and its usage ledger confirms the model and effort. It has no role in
P13's implementation and used no subagent or helper.

Authority: the P13 card's "Installed consumer closure after P10 integration
(2026-09-24)", released at `f7cbe5bc55ade50117ab040334f9a7b6438724b4`, together with the
later "Frozen blocked unit" and "Installed-consumer revalidation and alternate reviewer"
paragraphs, read at recovery `a1b2b18fdfd2ea5043e5730a6ac3b8822aea4b0a`
(`packages/P13.md:446-489` and `:541-565` there).

| Identity | Exact value |
|---|---|
| Accepted corrected base | `f740141e9ab2d860d1fc2c824a5a4b7015cdc805` (P10 repair merge) |
| Tests commit | `5c77a984a0686e8659ec8294da6aa9084702cec7` |
| Report-only child / review parent | `9d7851a485cc33f230e6a64288a218e808fc2e03` |
| Owner report Git/LF SHA-256 | `d2f9b5f4169beafe6e17c4b1b6effa71052b6967577e584ec07d99f1eb31db50` |
| Owner report CRLF SHA-256 | `2d935fc81a1c15c90c5a3075e9ed067d0895326fd506a2a37cc589072f81302c` |
| Owner handoff SHA-256 | `e7401ad6672901a84f5346a9f72bdd2693951a2cb3335442d6520f7e2e285619` |
| Evidence manifest SHA-256 | `4706e396fc4e495a5469015cb4640bb6bc02e184dfeb80c914b0c8d23b900ca0` |
| Frozen blocked candidate | `235102a858fefd3c39ad763caf6f8d1f71f132fb` |
| Candidate's base | `b5c0fcf6dbd5edbd8de84e76cd4b3a919bce510e` |

Independently verified pair identity:

- `5c77a984` has sole parent `f740141e` and changes exactly the six test paths below
  (three added, three modified). `9d7851a4` has sole parent `5c77a984` and changes only
  `reports/P13.md`.
- The report is 1,353 LF lines; the preceding 1,196-line report is its exact byte prefix,
  followed by 157 appended lines. Its LF and CRLF hashes match the brief and handoff.
- Each commit is unsigned and carries exactly one trailer, the required
  `Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>`.
- The handoff and manifest hashes match. The manifest binds the owner's
  `logs/full-six.*` streams, whose stderr ends `Ran 6 tests in 1014.624s` / `OK`.
- Per-path `git patch-id --stable` of `f740141e`..`5c77a984` equals that of
  `b5c0fcf6`..`235102a8` for all six paths, so the recreation is exact. Between the two
  bases, only `copilot-kit.py` changed among these paths.
- AST comparison with the base: `copilot-kit.py` keeps the same 50 test methods, adds
  only `CopilotKit.catalog_query` and changes only the two reused methods.
  `catalog-metadata.py` only adds `observe_prompt_bodies`; `catalog-selection.py` changes
  only `test_actual_family_queries_keep_literal_alias_and_body_boundaries`, which now also
  guards `read_bytes` and asserts no body read.
- Recovery from `f740141e` to `a1b2b18f` changes seven `.claude/` files and no product or
  test path, so the revalidated base is still current.

| Test path | Git-byte SHA-256 | Blob equals `235102a8` |
|---|---|---|
| `tests/integration/catalog-installed.sh` | `368fea9218223bcba331a3c69fa2eb59a2a1afd19fca21e98b84fc0abdc97685` | yes |
| `tests/integration/catalog-installed.py` | `808668f3911011db1619507600f5f3ca19020971394f3f8e9acd4b73dc4ceb7f` | yes |
| `tests/integration/catalog-installed-probe.py` | `a47692b5beccd37193fb03074068126d1322cf971d154c7c65f1b8ec150ca027` | yes |
| `tests/integration/copilot-kit.py` | `49e9a23496d8e4fce6d5fa68098e01c6682ab4a5b597abd2e10238af8731ff62` | no (newer base) |
| `tests/unit/catalog-metadata.py` | `d6ceb34a6a7ff98bee0796d1011043e54a98b25411a6fa9fc5e793cfd2e170ab` | yes |
| `tests/unit/catalog-selection.py` | `8f5e78b53fadd82a0e183736baecf3c833c666980ad0efba2fd12d78e742d99a` | yes |

## SPEC: released installed obligations

| Released obligation | Result and concrete evidence |
|---|---|
| Accepted P10 surface, synthetic short roots, no selectors, no real profile | PASS. All 17 installation and check calls run `li-lifecycle.py --source --repo --store scaffold init\|check --client copilot-cli` (`catalog-installed.py:157-173`), the accepted lifecycle route through `li-adapter.py` (`bin/li-lifecycle.py:928-946`). Each test builds a whitelisted environment with its own synthetic HOME, USERPROFILE, APPDATA, LOCALAPPDATA, TEMP/TMP/TMPDIR, XDG, Claude and Copilot roots and a Git ceiling, and asserts no `LINTEL_*` (`catalog-installed.py:74-98`, `:129-131`); the probe refuses any selector (`catalog-installed-probe.py:33-34`). All 99 retained child requests have zero selectors, every present synthetic root inside the test base and the ceiling at the run root. The 21 kit-clone queries deliberately omit `CLAUDE_CONFIG_DIR`. |
| A18.3 consumer selects from metadata without unrelated role or prompt bodies | PASS within the observer's scope. The probe loads the installed bundle's `li-catalog.py`, selects `demo-script`/agent/`DemoNarrativeArc` and only then reads the chosen body (`catalog-installed-probe.py:36-68`). Any SKILL.md or agent read not yet allowed raises (`tests/unit/catalog-metadata.py:78-100`). Actual trace: 196 header calls, one allowed body read (`DemoNarrativeArc.md`), order metadata-complete then selected-body. The installed catalog is byte-identical to the source (`catalog-installed.py:206-207`), whose bounded header reader is `bin/li-catalog.py:48-68`. |
| A18.4 moved or aliased use cases keep method, discoverability and dependency assets | PASS. Installed `--kind=all` entries equal the source's, all 196 bodies equal source bytes, all 46 aliases resolve to exactly their target and all 35 module-capability rows exist (`catalog-installed.py:213-231`). Reviewer completeness check on the pristine target of the first method: all 375 tracked component files and three source-metadata files exist with the adapter's normalized source bytes, all 459 manifest digests match, and no relative link in the 12 alias-target bodies is unresolved. |
| A19.4 worked and negative examples, all aliases and dependencies validate in a consumer | PASS at the mechanical level. Every selection example heading resolves in installed bytes with nonempty inputs, outputs and limitations, and the ten family sections keep their Inputs, Method and output, Negative and Evidence limit labels (`catalog-installed.py:232-241`). All twelve selections resolve in an installed clone under an empty home, with exact resource bytes, existing notices, minimal standalone dependencies and order-independent unions (`copilot-kit.py:275-340`). A literal hostile query stays data with zero matches, while an invalid selection, three malformed descriptors and missing PyYAML refuse visibly; none writes (`catalog-installed.py:259-276`, `copilot-kit.py:242-246`). Model-level method negatives stay outside this unit. |
| Discriminating negatives | PASS. Unresolvable alias target: a named and an unmatched selection query each exit 1 with `config/aliases.yaml: alias has a missing target ...` (`catalog-installed.py:244-257`). Removed dependency asset: the clone's own check exits 2 with `Required source file is missing: <path>` for three resources (`copilot-kit.py:247-271`), and `frontend-design` refuses when either notice or a corpus file is removed (`copilot-kit.py:341-356`). Unrelated body exposure: the injected read exits 3 with `UNRELATED_BODY_EXPOSURE` (`catalog-installed.py:278-305`). All 14 nonzero outcomes had empty stdout and an unchanged fixture. |
| Reuse accepted tests and kit methods; change only tests and report | PASS. The two kit installed methods run through the class's lifecycle-backed `run_cli` and logged `catalog_query` (`catalog-installed.py:157-178`, `:210-211`); the selection and metadata helpers are reused. Only six test paths and the report changed. |
| Revalidate on the corrected P10 base | PASS. `f740141e` contains the accepted IC-F01 repair; the previously setup-blocked metadata method now completes, and all six journals end `complete`. |

## Independent execution

Every suite, test and analysis script ran through a reviewer launcher under PowerShell
7.6.6 (`C:\Program Files\PowerShell\7\pwsh.exe`). It builds each parent environment from
scratch: system variables, a PATH of a CI-style `python3` wrapper (`exec python "$@"`),
Python 3.11.9 with PyYAML 6.0.3, Git and System32, and synthetic HOME, USERPROFILE,
APPDATA, LOCALAPPDATA, TEMP, TMP, TMPDIR and XDG roots under the 41-character
`%LOCALAPPDATA%\Temp\p13v`. It sets `GIT_CEILING_DIRECTORIES` to that root,
`GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=NUL`, exports no `LINTEL_*` variable
(nothing in this suite reads `LINTEL_POWERSHELL`), closes stdin and preopens both
streams. WindowsApps and Windows PowerShell 5.1 are not on PATH; inside Bash,
`powershell` and `jq` were absent. Git Bash 5.3.15 printed no warning. Its `/tmp` mount
stayed on another session's existing root before and after both suite runs (L-049).

The frozen source was a `git clone --shared --no-checkout` of this repository, made
without system or global Git configuration under the same ceiling and checked out
detached at `5c77a984` with `core.autocrlf=true` (a Windows-CI-like CRLF tree;
`*.sh` and `bin/*` stay LF by attribute). The report-only child does not change any
executed path. After all runs the clone's HEAD was unchanged and
`git status --ignored --untracked-files=all` was empty.

| Check | Command | Outcome |
|---|---|---|
| Frozen suite, retained | `bash tests/integration/catalog-installed.sh --keep-fixtures` | exit 0; 6/6 ok, zero skips; `Ran 6 tests in 1096.757s`; 1,097.483 s wall |
| Frozen suite, runner form | `bash tests/integration/catalog-installed.sh` | exit 0; 6/6 ok, zero skips; `Ran 6 tests in 1756.846s`; fixture root removed by `tearDownClass` |
| Changed kit methods, original class | `python -B tests/integration/copilot-kit.py` with the two reused method IDs | exit 0; 2/2 ok in 453.021 s |
| Changed unit helpers and callers | `bash tests/unit/catalog-metadata.sh`, `catalog-selection.sh`, `catalog-consumers.sh` | 31, 29 and 33 ok; zero skips |
| Shell and grammar | `bash -n` on the entry; Python 3.9 grammar on the five Python files | all pass |

The retained run's 99 child calls reproduce the owner's distribution exactly:

| Operation | Actual exits |
|---|---|
| Lifecycle init, including one repeat | 7 at 0 (683.6 s in total, mean 97.7 s) |
| Lifecycle check | 7 at 0; 3 expected refusals at 2 |
| Catalog metadata and query | 70 at 0; 10 expected refusals at 1 |
| Test-owned body observer | 1 at 0; 1 injected refusal at 3 |

All six transaction journals are `complete` with 473 `applied` entries each. No child
stderr contains `File changed while reading`, `retry` or `Traceback`. Each of the 14
refusals is a one-line diagnostic naming its cause; the three removed-asset catalog
refusals surface the OS file-not-found message with the path. The longest fixture path
is 153 UTF-16 code units: 12 more than the owner's 141, exactly the difference between
the two fixture-root lengths (57 and 45).
Both body traces equal the owner's once each fixture root is replaced by a placeholder, so
their raw SHA-256 values differ only through embedded paths: positive
`9c6ad68e27730bcca2e15a4195d85224323cdf145bcea75f3e1da7bf1ede5571` (owner
`f6132d0f98f12e0879c423c6dc616bd902d38380b75eab40d732ccaa14277811`), injected
`5ca959752b0ffd755bbf8ede111c588ee42b2d75e430fd2646dfc382db791a34` (owner
`45ed4553ce1e50df35b53270d4e9396c0eb0d827a2ed6e7b39d26dc1a11995bd`).

## QUALITY (eligible after SPEC PASS)

The unit is narrow and reuse-first. It changes no producer, and the extraction keeps the
original kit methods' behavior: the AST delta and the 2/2 original-class run confirm it.
Children get whitelisted synthetic environments. Every call leaves request, stream and
result receipts with before and after fixture snapshots, the source tree must stay
unchanged, and a path budget is enforced after every call. The three released negatives
assert specific diagnostics rather than any failure. Both reviewer runs started from the
shell entry, and the second used exactly `run-all.sh`'s invocation
(`tests/runner/run-all.sh:90`); the owner had run only the Python entry.

### N1 (P3): the new entry is a large share of the Windows CI budget

`run-all.sh` discovers every `tests/integration/*.sh` (`tests/runner/run-all.sh:121`),
and CI runs `run-all.sh --require-all` on ubuntu, macOS and Windows within a 30-minute
job (`.github/workflows/ci.yml:21`, `:25`, `:55`). On this shared Windows host the entry
alone took 1,097 s and then 1,758 s; the owner measured 1,015 s. Its seven lifecycle
inits (six fresh installations and one repeat) account for 683.6 s of 1,038 s of child
time in the retained run. The known P15 timing risk
(`.claude/plans/universal-implementation/handoff.md:459-472`) predates this entry.

Recommendation: include this entry's measured cost in the P15 timing decision, for
example in a Windows integration shard or budget. If its duration must fall, the
read-only methods could share one verified pristine installation. A silent skip or tag
exclusion would not preserve the evidence. No change is required in this unit.

### N2 (P3): the fixture-root link guard can never fire

`catalog-installed.py:43-45` resolves `--fixture-root` (or the temp directory) with
`resolve(strict=True)` and only then checks `is_symlink()` and the reparse attribute.
Resolution has already replaced any symlink or junction with its target, so the guard
cannot reject a linked root. A reviewer probe on a junction inside the synthetic root
showed the unresolved path has the reparse attribute, while the guard as written does
not fire. The same guard before resolution would have fired. The product checks in that
order (`bin/li-catalog.py:245-249`).

Impact is test hygiene only. The synthetic subdirectories are checked separately after
creation (`catalog-installed.py:85-88`), and no product claim depends on the parent
check. Recommendation: test the unresolved path, then resolve it for use.

## Evidence and limits

Private reviewer evidence is under `%LOCALAPPDATA%\Temp\p13v`, outside the repository
and not backing `/tmp`: `o\` holds the launcher (`launch.ps1`, SHA-256
`13871892d51b42c59fb3878394b3c2eccf84f3d31d4aba658ec2d5535c0bbaee`), scripts, receipts
and streams, and `t\p13i-6b3ij9k8` holds the retained fixture. Suite stderr SHA-256:
retained run `0d131f98016ccd5f6748654ef9dbf14524f6183459c9af734ed895cc58d2d05c`, runner
form `6c83087cd8476943bbdc3130a466256123b7cd63a426a70a270997801696b28e`. The coordinator
may delete the directory.

Retained reviewer failures:

- The first suite launch passed `--keep-fixtures` through `pwsh -File`, whose parameter
  binder rejected it before any process, receipt or fixture existed. The same command was
  relaunched in-process; the refusal note remains.
- The first identity and AST checks ran with the reviewer's inherited environment. They
  only read Git objects without system or global configuration and parsed ASTs under
  `python -I`; no product was imported and no test ran. Both were rerun through the
  launcher with byte-identical output. Read-only hashing of the owner's handoff,
  manifest and logs, the clone setup and the junction for N2 ran directly in the
  reviewer's PowerShell 7 shell.
- The first pre-commit check of this review failed because the authoring tool wrote CRLF
  line endings. Its hash, abbreviation and citation checks had passed; only the line
  endings were converted to LF before the passing recheck.

Limits:

- Evidence is Windows with Python 3.11.9 only. No Python 3.9 runtime, Linux, macOS or
  hosted CI ran; per L-045 nothing was pushed or dispatched.
- The body observer sees only `Path.read_text` and `Path.read_bytes`
  (`catalog-metadata.py:78-100`), while the catalog reads headers through `Path.open`
  (`bin/li-catalog.py:52`). A body read through `open` would not be observed. The installed
  A18.3 claim also rests on the catalog's byte identity with the source and the accepted
  source-level header-only regression. No model context, native role or host activation
  was observed.
- The suite isolates its children, but its own process imports the kit adapter before
  `setUp` patches the environment (`catalog-installed.py:36-37`, `:94-96`). The reviewer's
  launcher supplied parent isolation here; no import-time profile read was found.
- Durations come from a shared, loaded host and are not CI predictions.
- The owner's rehash of the old IC-F01 and fan-in packets was not independently repeated;
  it is outside these obligations. Compliance and required policy were not assessed.
- To confirm its configuration, the reviewer read its own host session metadata. No
  Lintel profile, `~/.lintel` or other home configuration was read. The review commit
  uses the normal Git identity. At the host's request, this session's own worktree branch
  was renamed to `jokerman-microsoft-p13-installed-review` before the review branch was
  created; no other ref changed.
