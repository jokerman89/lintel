# P10 migration F01 independent recheck

**Date:** 2026-09-21. **F01:** CLOSED for the reviewed repair.
**New scoped findings:** P1 0 / P2 0 / P3 0.
**Complete P10 specification/preservation:** BLOCKED, not accepted.
**Whole-P10 quality:** NOT STARTED. **A13:** CLOSED.

The exact malformed catalog now fails explicitly instead of disappearing into a
successful empty inventory. Independent real-skill preservation cases and the new
migration test class passed. This closes the narrow parser finding only; it does
not waive D01, D03 or any unverified original P10 acceptance.

## Immutable scope and provenance

| Identity | Value |
|---|---|
| Reviewed report-only candidate / parent required for this report | `c1de05c7f18770f34f950a8c4d4e194892da3291` |
| Reviewed product / candidate parent | `4407827f563fecac2ac6bf04a6bd0fc9cdd05641` |
| Product parent / rejected candidate | `62ffb9a072c3314b97e015e0f8f98b7f64459fc8` |
| Prior independent rejection, preserved unchanged | `1d871338dcdd1b6a535e4b546c2b2d0a7aea031b` |
| Coordinator preservation of that report | `46e8b0ffee3635a793a015140bea0f0c0540d6ba` |
| Narrow F01 authority | `def5d8db848b64cb1a18b597103806f1a5b383ac` and MasterSession's 2026-09-21 recheck instruction |
| Continuation branch | `jokerman-microsoft-p10-migration-recheck` |
| Same independent reviewer | App session `cb36a715-df4e-4c7a-8588-37115c8df3c8`; CLI session `1578dfd8-f239-4eba-989b-3c4bde3e5792` |

A new clean Git worktree was created at the exact candidate without switching,
resetting or discarding the prior review worktree. Its original branch still names
`1d871338` and was reverified clean. The continuation was clean before this report.
No nested agent, product repair, test repair, source import into master or shared
plan/memory/reducer update occurred. The only repository output is this file.

Read the coordinator's immutable F01 authority, the complete repair diff, the updated
reports/P10.md F01 evidence and the unchanged real migrations skill/dispatcher.
Original A12.4.b/CP-16 and the prior independent rejection remain the requirement.
The implementer's 13-test/52-subprocess evidence was not adopted as reviewer evidence.

The product changes exactly two paths. Independent AST comparison and Git diff agree:
only `migration_inventory` changes in `bin/li-lifecycle.py` (12 additions, 4 deletions);
`tests/integration/universal-lifecycle.py` adds the 218-line `MigrationInventory`
class with seven test methods. Removing that new class makes the entire original
test-module AST identical. No other production function or import changes.
The `4407827..c1de05c7` delta is only the builder's reports/P10.md.

### Verified source identities

Hashes are over immutable Git bytes, not checkout line-ending conversions. Product
and report-only candidate match. Six producer contracts match the rejected candidate;
only the authorized lifecycle parser hash changes.

| Artifact | Candidate SHA-256 |
|---|---|
| `bin/li-lifecycle.py` | `465db503bd518c8f453916aed961ff6e290e415ffb3e561b770578d09cd09b60` |
| `docs/native-installation.md` | `e2cf6bf3417e10ad12112002e0719a581f1632b0db2881459cfaad20208e1ae0` |
| `docs/lifecycle.md` | `e7a95f69b0f759024c4fc1ca001c290cff4a4d8cf225b2979c707ed6a8e51fa1` |
| `install/directories.txt` | `c8e0e825586f309c43bbcb5dc6644eb270a233ee638c7244696193db8f52d7c3` |
| `install/native.sh` | `1425c05888b24b413a45ec33f70a98fe432f73774634197cae4cbdc9d1c9e187` |
| `install/native.ps1` | `57173b99e0c809d3fe45a6c9b894ddab0c07b3961a2d73b6fd61af25047483f7` |
| `lib/managed_transaction.py` | `2594ec6a12a0e9c37affe80d4f8b60ecf8e45fe5a438e7096c5ed8cabea8f020` |
| Unchanged `skills/migrations/SKILL.md` | `736eae4f2e30154be86a55223ff7f9133b013a0c7f7ab8483fc94d70b015adba` |
| Unchanged `bin/li-lifecycle` dispatcher | `8075bb67aad321701235b44f570521b96d1aa6b086a7f981b159f63b18beeb7f` |

The prior lifecycle hash was
`7296534ea202b7bc45f3a62a93c871e659b48b5d114e891d53c2c7b3af7a2ece`.
Shared Markdown provider blob remains `0b3da55046358864fcd3075ba5bfb6c2348b1fec`.
The complete changed-path comparison plus explicit identities confirm unchanged P07
profile implementation/schema, pack resolver/schema, bootstrap, provider and the
previous validation fixture. No P03, native receipt or shared evidence format changed.

## F01 exact regression and closure

**Trace:** A12.4.b/CP-16; prior location `bin/li-lifecycle.py:525-527`.
The repair at `525-540` separates requested archive handling, applicable row width,
nonempty field validation and recognized ignorable rows. Only one outer delimiter is
removed; a bounded split retains pipes in the last prose field. Errors reach the
existing nonzero path before any success JSON.

Both full catalogs below are the original reviewer inputs: UTF-8, no BOM, LF-only,
exactly one trailing LF. The valid catalog is **192 bytes**, SHA-256
`4ca4751d30a521d13c18f0608d255960563c28a0de770882e37dfccbb737b7b0`:

```markdown
# Migrations

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| overdue-work | 2026-06-12 | 2026-09-12 | none | Pending consumer work |
```

The truncated catalog is **161 bytes**, SHA-256
`35adc26d85f0221cfb57f7de68e9823d4fbc371ba6992fc6dfeb8144b4a431c7`:

```markdown
# Migrations

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| overdue-work | 2026-06-12 | 2026-09-12 |
```

Each ran through the unchanged skill's actual single Bash block, extracted from a
Git-byte-verified copied source and invoked by Git Bash `--noprofile --norc -c`
with `set -euo pipefail`:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" migrations
```

The current directory was a separate synthetic caller, not the source or target.
Poisoned catalogs in caller and target could not substitute for the selected source.
The skill, shell dispatcher, Python helper and transitive imports were real; no
helper method was called in place of this path and no parser/result was mocked.

| Revision and input | Actual result |
|---|---|
| Rejected `62ffb9a`, 192 bytes | Exit 0; one `overdue-work`, `schedule: overdue`, `observation: unknown` |
| Rejected `62ffb9a`, 161 bytes | Exit 0; empty `migrations`, empty stderr: original defect independently reproduced, not a passing product result |
| Candidate `c1de05c7`, 192 bytes | Exit 0; same overdue/unknown record and description, empty stderr |
| Candidate `c1de05c7`, 161 bytes | **Exit 2; stdout empty**; explicit diagnostic below |

```text
li-lifecycle: MIGRATION_CATALOG_INVALID: active migrations row requires 5 nonempty fields: 'overdue-work'
```

Every invocation preserved the complete source/target/caller/default-home path set,
file SHA-256/size/mode/read-only state and synthetic personal/app/temp roots. No
selected reference, profile generation or hidden runtime output was created.
**F01 closure confidence: 10/10 for the exact defect and exercised preservation scope.**

## Independently executed preservation

The reviewer authored a separate case matrix before running the builder's new tests.
The matrix had **40 candidate invocations**: 14 valid exit-0 cases and 26 required
exit-2 refusals. All expected outputs and no-write comparisons passed. The two
rejected-baseline controls above are additional and remain labelled as baseline
evidence. The 42-invocation probe loop took 38.422 seconds, exited 0, with zero
failed expectations or skips; it is not a full-suite count.

| Case family | Observed preservation |
|---|---|
| Exact F01 plus valid-then-invalid | Original valid record retained; truncated row fails with no partial/success JSON |
| Active shape | Every empty field, short/false header, short/false separator, short/false placeholder and empty row refuses explicitly |
| Archive shape and selection | Unrequested archive rows remain excluded; `--all` includes valid rows and refuses truncated rows, empty fields and incomplete headers |
| Legitimate empty inventory | Complete actual headers, separators and canonical placeholders remain valid and empty |
| Prose and encoding | Final description/outcome pipes retained; aligned separators, CRLF, ordinary Unicode and an omitted closing delimiter preserve valid records |
| Literals | Fenced/indented/quoted/comment/raw-PRE fake rows and headings do not become obligations or change active-section interpretation |
| Missing/date errors | Missing catalog, missing active section, invalid start and deadline/closed dates are nonzero with empty stdout and explicit stderr |
| Schedule and detector | Overdue/unknown, no deadline, future deadline and deadline-today remain distinct; actual legacy layout reports needs_migration/incomplete/current/not_applicable correctly |
| Current source catalog | All 23 current active rows remain readable with and without `--all`; no archived placeholder becomes data |
| Root and state preservation | Exact source wins over poisoned caller/target catalogs; all compared content/path/mode states remain unchanged |

For archive checks, `--all` was appended to the real block using positional
arguments as documented by the skill; the two exact F01 cases used the unmodified
block with no additional command options. No alternate mutation implementation or
custom shortened home/store was introduced.

Then ran only the seven new methods, using an external safety wrapper whose Python
audit hook checks subprocess environments before their real execution:

```text
python -I -B <session-files>\p10_migration_test_runner.py
  <exact-source>\tests\integration\universal-lifecycle.py
  --root <exact-source> --bash <git-bash> MigrationInventory -v
```

**Actual result:** 7/7 tests, 44 actual subprocess invocations, 41.915 seconds,
exit 0; zero errors or skips. The copied source remained byte-identical.
Normal test cleanup returned the synthetic temp tree to its exact empty pre-run
state. These are this reviewer's results, not the builder's 13/13 or 52 invocations.
The seven-test pass is separate from, not a substitute for, the independent matrix.

## Isolation, retained evidence and remaining gates

Each command received a reconstructed allowlisted environment. HOME/USERPROFILE,
application/config/cache/temp roots, source/target/data home (the default runtime
home in the independent matrix), packs, pointer, audit/jobs/private-role paths and
derived profile/history/registry/state
paths were resolved and checked inside owned synthetic fixtures before execution.
Ambient Lintel/Claude/Gstack/Git redirects and BASH_ENV/ENV were absent. Global/system
Git configuration was disabled for the process; any test-specific Git config path
remained synthetic. Hooks were disabled through an owned empty per-process directory.
No global setting, profile or actual home was inspected or modified.

Twenty files per frozen candidate/baseline copied source were read from immutable
Git objects and verified before use and again after execution. Each case's own
copied dependencies matched its selected revision; only catalog/target fixture
data varied. The continuation used checkout-equivalent LF settings; the preserved
prior worktree's CRLF status was checked with its matching setting. No source
normalization, reset, reducer regeneration or cleanup of prior artifacts occurred.

Actual execution was Windows, Python **3.11.9**, Git Bash **5.3.15**. No Python 3.9,
stock Bash 3.2, POSIX OS, PowerShell performer, native installation or live client
acceptance is inferred. PowerShell 5.1 remains denied/unverified; no override or
alternate-host retry occurred. No network, authentication, private profile, hook
activation, paid model, release, push or PR operation occurred.

| Gate | Verdict after this recheck |
|---|---|
| P2 F01 migration parser repair and exercised regression/preservation | **CLOSED / scoped PASS** |
| Entire A12.4.b and other original P10 leaves | **BLOCKED / remaining acceptance unverified**; no blanket leaf completion |
| Complete owned P10 specification/preservation | **BLOCKED** |
| First whole-P10 quality review | **NOT STARTED** |
| D01 default-store setup | Prior **FAILED/BLOCKED** result retained, not rerun or waived |
| D03 actual validation-fixture cleanup/default-preservation proof | Prior **cleanup ERROR / BLOCKED** result retained, not rerun or waived |
| A13 interface release, master product import, final integrated/human/host approval | **Not granted** |

D01 remains the original failure before target publication at a normalized
260-character snapshot destination. Its original display-escaping overcount and
corrected length evidence remain preserved. The explicit-store neutral bridge was
control-only; it still cannot replace the default scenario. D03 remains the earlier
one-test cleanup ERROR; successful cleanup of this migration-only class does not
resolve it. The separate read-only P03 investigation `990b0daa` supplies no path
repair source to this candidate. No P03/P07 change or path/store workaround was used.

Historical **120/128, 8 failures, 0 skips, 0 partial** remains FAILED. Neither these
focused runs nor any builder result synthesizes a full-suite pass. No native/full
suite or known blocked default-path scenario was rerun just to repeat its failure.

### Evidence locations and identities

Raw invocation/environment records, output, fixture catalogs, complete before/after
state comparisons and source identities are retained under this reviewer's session
`files\p10-migration-recheck\`. The independent drivers are the session-only
`p10_migration_recheck.py` and `p10_migration_test_runner.py`. Manual probe fixtures
were deliberately retained, not deleted or relabelled; the existing tests' normal
cleanup was separately measured. Prior review fixtures and refs remain untouched.

| Evidence file | SHA-256 |
|---|---|
| `identities.json` | `3473f67e982fc3d5173884689be7a10735831470ac08dbe4906acc2a7b22f924` |
| `ast-scope.json` | `258403b4d188c9516a867b357151950760f8e8d0b998f25847e6635ecc515975` |
| `candidate-source-manifest.json` | `cf8301118f91b44dedcae0d8a430819e556f946a753678a33c21291154ee68eb` |
| `independent-results.json` | `048d285bbdd1ef9951a27113c2157a24b10ad7c573fdc9da0a56832b4152d0d1` |
| `03-f01-valid-192-evidence.json` | `4a1411633ee462a0c883a3d649d987826f1f59587cd359f2b9839f726a745aaf` |
| `04-f01-truncated-161-evidence.json` | `e2e913a18bbe640c5c9e8a159e4533ca0f9a7abdc7237b10f2ddc27e68c7dcab` |
| `04-f01-truncated-161.stderr.txt` | `0b164789b2d2ce527b2b2d4c33a77e084d884428993c721806542216bd464d13` |
| `existing-migration-tests.stderr.txt` | `4a7141d47d1520d16ff93c42db8f724146b55afcf1221a324b3453b25ff4dab9` |
| `existing-tests-subprocess-isolation.json` | `259e5044478c1c781adb4376ae70a7275869aa6af7486e884f21af0e3cf8f106` |
| `existing-tests-cleanup.json` | `230b179bccc6b1849ac4b4e9e5200e9757b29ed3254ec54a1d502a0cfc24f303` |

The wider `evidence-index.json` records runtime versions, unchanged copied sources
and both clean worktree observations. Hashes identify evidence; they do not
authenticate independent actors or establish host-policy enforcement.

**Cycle position:** narrow F01 recheck CLOSED -> await separately authorized combined
checkpoint -> complete specification/preservation -> first whole-P10 quality.
No further testing, cleanup, repair or scope expansion follows this report.
