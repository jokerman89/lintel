# P10 independent component review

**Date:** 2026-09-21. **Stage 1 specification:** FAIL. **Stage 2 quality:** NOT STARTED.
**Confirmed findings:** P1 0 / P2 1 / P3 0. **Component acceptance:** not granted.

Specification review stopped on F01 as instructed. The first whole-P10 quality review,
remaining specification scenarios and integrated acceptance remain outstanding. Zero
reported quality findings is not a quality pass. MasterSession confirmed the stop and
retains authority to issue a bounded repair to the original builder.

## Identity, authority and attribution

| Identity | Exact value |
|---|---|
| Reviewed candidate / required parent of this report-only commit | `62ffb9a072c3314b97e015e0f8f98b7f64459fc8` |
| Candidate's parent / frozen product plus coordinator dependencies | `a400c03d384be29879644ec11214f0eeadafe7df` |
| Original P10 product | `a73cf9ee38977501c201225d8269dac3668c1080` |
| Accepted-dependency base of the original 48-path P10 diff | `fb96f71342f7994c42bdfc7cd61e6d452e6acb54` |
| Authorized one-file fixture follow-up | `acf97f1ca47d115501613ca29e91d902300b9bf6` |
| Prior implementer report checkpoint, retained | `1117b9b54a55105d7202f92141a670f7b0cff578` |
| Distinct reviewer context | App session `cb36a715-df4e-4c7a-8588-37115c8df3c8`; CLI session `1578dfd8-f239-4eba-989b-3c4bde3e5792` |
| Review branch | `jokerman-microsoft-universal-installer-review` |

HEAD matched the requested candidate and porcelain status was empty before work.
The branch was renamed before creating files; its filesystem location did not move.
The reviewer did not implement this package, launch nested agents or repair findings.
The only repository output is this report. Separate host context is declared provenance,
not authentication through an actor string, content digest or synthetic receipt.

Read authority included AGENTS.md, AGENT-INSTRUCTIONS.md, the Copilot and Universal
adapters, CORE-PRINCIPLES, relevant memory and architecture, ADR-0029/0030, the selected
work map/spec/plan, packages/P10.md and the complete reports/P10.md. Original audited
A12, CP-02/04/12/16, RU-06/07/08/11 and the lifecycle skill-inventory rows were retained.
Coordinator refinements `0ecdb520`, `fefbc9de` and `9a4d177` were read through immutable
Git artifacts; neither the work map nor shared planning state was rewritten.

These later changes are dependencies, not P10 authorship:

| Coordinator source | Candidate import | Attribution |
|---|---|---|
| `d53dc38efa41a8ea562ca5078f36b0ce4010b712` | `dcf0448aa6bb3d5d94d958b56655eca5362d3c6e` | P05 evidence CLI Git mode, 100644 -> 100755; not a P10 content repair |
| `aa56a672b0db187db20201d969f990ab0093802a` | `7a8927788b31610a38263b8f83a295268806eb48` | Literal runner diagnostics and regression |
| `935b640c0038a28921f130b7e48c6262cf6ecfd5` | `a400c03d384be29879644ec11214f0eeadafe7df` | Welcome footer and current parity oracle |

The final `a400c03..62ffb9a` delta is only reports/P10.md. The fixture follow-up is
one file and two spans: the copied-source list in `ProfileLifecycle.setUp` and
`test_validation_skill_executes_shared_contract_without_activation`. Git diff and
AST comparison confirmed every other class method was unchanged. The original
48-path product remains the review scope, not just that fixture.

### Immutable producer contracts

Independently computed SHA-256 over Git blob bytes at original product, `a400c03`
and the candidate; all three revisions matched every value below.

| Artifact | SHA-256 |
|---|---|
| `docs/native-installation.md` | `e2cf6bf3417e10ad12112002e0719a581f1632b0db2881459cfaad20208e1ae0` |
| `docs/lifecycle.md` | `e7a95f69b0f759024c4fc1ca001c290cff4a4d8cf225b2979c707ed6a8e51fa1` |
| `install/directories.txt` | `c8e0e825586f309c43bbcb5dc6644eb270a233ee638c7244696193db8f52d7c3` |
| `install/native.sh` | `1425c05888b24b413a45ec33f70a98fe432f73774634197cae4cbdc9d1c9e187` |
| `install/native.ps1` | `57173b99e0c809d3fe45a6c9b894ddab0c07b3961a2d73b6fd61af25047483f7` |
| `lib/managed_transaction.py` | `2594ec6a12a0e9c37affe80d4f8b60ecf8e45fe5a438e7096c5ed8cabea8f020` |
| `bin/li-lifecycle.py` | `7296534ea202b7bc45f3a62a93c871e659b48b5d114e891d53c2c7b3af7a2ece` |

The shared Markdown provider is blob `0b3da55046358864fcd3075ba5bfb6c2348b1fec`.
The complete intervening changed-path list and focused comparison confirmed no
P07 runtime/schema or provider modification. This review does not change native
TSV v1, P03 snapshot/result/restore, P05 v2 evidence or P07 v1 reference contracts.

## F01 - Malformed migration rows disappear into successful empty output

**Severity:** P2 (must fix). **Confidence:** 10/10 for the reproduced case.
**Location:** `bin/li-lifecycle.py:525-527`, with successful return at `544-545`.
**Trace:** A12.4.b and its A12.4 parent; original CP-16's missing/malformed/unsupported/
overdue distinction; `skills/migrations/SKILL.md:35-39` and `docs/lifecycle.md:169-172`.

`migration_inventory` groups short data rows with ignorable headers/placeholders:

```python
cells = [cell.strip() for cell in line.strip("|").split("|", 4)]
if len(cells) < 4 or cells[0] in ("Slug", "_none yet_") or set(cells[0]) <= {"-", ":"}:
    continue
```

An active heading sets `found` even though the subsequent malformed obligation is
discarded. Therefore this is not a missing-helper, alternate-parser or test-oracle
disagreement: the actual shipped reader reports no migrations for invalid metadata.
An operator can lose visibility of unresolved work, precisely the original CP-16 defect.

### Exact fixture bytes and real invocation

Both catalogs were UTF-8 without BOM, LF-only, with one trailing LF after the final
row. The complete valid catalog was 192 bytes, SHA-256
`4ca4751d30a521d13c18f0608d255960563c28a0de770882e37dfccbb737b7b0`:

```markdown
# Migrations

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| overdue-work | 2026-06-12 | 2026-09-12 | none | Pending consumer work |
```

The complete malformed catalog was 161 bytes, SHA-256
`35adc26d85f0221cfb57f7de68e9823d4fbc371ba6992fc6dfeb8144b4a431c7`:

```markdown
# Migrations

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| overdue-work | 2026-06-12 | 2026-09-12 |
```

The source-owned shell/Python dispatcher, profile dependencies, shared Markdown
provider and migrations skill were copied byte-for-byte from the frozen candidate
into an owned synthetic source. Only its catalog data was varied. The real skill's
single Bash block was extracted unchanged and executed with Git Bash
`--noprofile --norc -c`, preceded only by `set -euo pipefail`:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" migrations
```

Source was `<fixture>\migration-case\source`; target was the separate
`<fixture>\migration-case\target`. Synthetic HOME/USERPROFILE and the target's
default runtime home, packs, pointer and audit paths were verified before execution.
No mock helper, substituted parser or product edit was used.

| Case | Expected | Observed |
|---|---|---|
| Valid obligation | Exit 0; one overdue, unknown-detector record | Exit 0; slug `overdue-work`, schedule `overdue`, observation `unknown`; empty stderr |
| Truncated active obligation | Nonzero with an explicit malformed-row/catalog diagnostic, such as `MIGRATION_CATALOG_INVALID`; no successful empty list | Exit 0; `"migrations": []`; empty stderr; ordinary schedule/unknown-detector notice only |

Observation date was `2026-09-21`. Full returned JSON, exact argv, durations and
before/after file states are retained. Both invocations preserved source, target,
caller and synthetic-home bytes. The catalogs remained mode 0666/read-only false
on this Windows filesystem. The independent probe returned 3 to flag the failed
spec assertion; that must not be confused with the malformed consumer's exit 0.

**Repair direction, not implemented:** distinguish recognized header/separator/
placeholder rows from malformed data. Validate the applicable active/archived row
shape and report invalid metadata instead of filtering it into success. Add the
truncated-row regression while retaining valid overdue/unknown, archived and
literal/fenced-row behavior. No second parser or P03 repair is required for F01.

## Separate failed setup and test-harness evidence

These observations are not additional confirmed product findings and do not clear
any required acceptance. They remain separate from F01.

### D01 - Default-store installed-consumer setup failed

Actual command, with personal prefixes replaced by `<fixture>`:

```text
python <fixture>\exact-source\bin\li-adapter.py init
  --source <fixture>\exact-source
  --target "<fixture>\installed consumer" --client copilot-cli
```

Exit **1**, stdout **empty**, stderr **WinError 3** from the actual snapshot
`atomic_write` -> `os.replace` call. No completion was claimed. Measured normalized
Windows paths, before redacting the common prefix:

| Path | Characters |
|---|---:|
| `<fixture>` | 94 |
| `<fixture>\installed consumer` | 113 |
| `<fixture>\.lintel-recovery-c3bb072a6fd67d0a` | 128 |
| `<default-store>\snapshots\.pending-snapshot-86c1bfe6045d4c7fb76cb3f92f10f0bd\blobs\.lintel-write-i3gvinuv` | 218 |
| `<default-store>\snapshots\.pending-snapshot-86c1bfe6045d4c7fb76cb3f92f10f0bd\blobs\5c64df8ab08e48572508fb67addefd1bf02cc601e80e2ec536803aa389ee91e6` | **260** |

An initial review diagnostic counted escaped Python-repr backslashes, reporting
230/272 for the last two paths. That erroneous measurement and the original log
were preserved; a separate normalized-length artifact records 218/260. The
product failure was not rewritten or discarded.

Target publication had not begun. The target still contained exactly the two
initially written seeds, no additions/deletions, mode 0666/read-only false:

| File | Initial supplied bytes -> independently observed after SHA-256 | Size |
|---|---|---:|
| `AGENTS.md` | `5c64df8ab08e48572508fb67addefd1bf02cc601e80e2ec536803aa389ee91e6` -> same | 20 |
| `unrelated.txt` | `634031d1876a1801b158609feb2d3cef7d149c27311c00f6f67c23551199a24a` -> same | 29 |

The initial seed values are recorded by the creation harness; a separate complete
pre-command tree snapshot was not taken for this first setup attempt. The post-failure
inspection verified exact equality to both known seed values and the complete path set.

The store retained its 162-byte `.lintel-managed-store.json` owner marker, SHA-256
`c0a84520df9cc946e72c16cd8936fcf94999256c83507c8fdde1fa19752740d7`,
and an empty pending snapshot/blobs directory. There was no transaction directory,
completed snapshot manifest, result receipt or retained operation lock. No rollback,
lock theft, relabeling, store cleanup or source mutation was attempted.

Classification: the required default-store setup is **FAILED/BLOCKED**, consistent
with the documented absence of a guarantee for arbitrarily long parent paths in
docs/lifecycle.md. Failure occurred before target mutation and did not claim success;
there is no demonstrated user-data loss or hidden successful recovery. It is not
counted as F01 or expanded into a P03 finding. Default-scenario acceptance remains
unverified; a narrower success cannot waive it.

### D02 - Explicit-store setup and real neutral bridge are controls only

MasterSession permitted a separately labelled diagnostic/control. The same source
and same target were installed using explicit `--store <fixture>\setup-store`
(exit 0, 66.234 seconds), leaving the failed default-store evidence unchanged.
This was not a relocation or repair of that evidence.

The actual bundled helper and its direct/transitive dependencies were checked for
presence and byte identity before executing:

```bash
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
# Read-only reviewer checkpoint records the exported reference and file states.
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$REVIEW_CHILD"
```

The real shell bridge exited **0** in 5.453 seconds. It used the installed bundle,
original caller/child paths, the caller's full default
`.claude\runtime\lintel-home`, inherited verified reference and the child's default
sibling recovery store. No pin was removed, no helper was mocked and no custom short
home was supplied. The caller history filename was **304 characters**, not shortened.

It created the 26 reported child foundation files and its declared recovery evidence.
Caller bytes/modes, synthetic-home bytes/modes and unrelated child bytes stayed
unchanged. The returned operation reference matched the caller's generation 1;
`target_profile_reference` was null, with no child selected reference or profile
generation. Source bytes remained unchanged.

This establishes only the neutral bridge **after the explicit-store setup control**.
It is not a passing end-to-end default-store scenario. Required-caller, real
configured-store/repository-local policy, matching-policy, conflicting-target and
missing/drifted-caller branches were not independently run before the spec stop.
The synthetic caller/child directories were not Git-initialized; this control
does not establish clean-clone, index or branch-preservation behavior.

### D03 - Actual authorized validation fixture ended in cleanup ERROR

Executed unchanged:

```text
python -I -B <session-files>\p10_test_runner.py
  <exact-source>\tests\integration\universal-profile-context.py
  --root <exact-source> --bash <git-bash>
  ProfileLifecycle.test_validation_skill_executes_shared_contract_without_activation
```

The reviewer wrapper records/verifies subprocess isolation and calls the real
subprocess; it does not replace the dispatcher or its results. The actual one-block
skill ran through the copied trusted helper. The body reached cleanup without a
reported assertion failure, but the runner finished **exit 1, 1 test, 1 ERROR** in
`TemporaryDirectory.cleanup`: `WinError 145`, directory not empty under the synthetic
profile history. The retained file and remaining fixture contents are recorded.

This is **not 1/1 PASS**, nor successful cleanup or acceptance of the fixture.
Its original failure log is retained; no shorter-root rerun or cleanup workaround
was used to turn it green. The queued native no-Python/preservation/recovery selectors
were not reached. This observation is not asserted as a P07 product defect.

## Per-parent and per-subleaf verdicts

`UNVERIFIED` means selected acceptance is not complete, not that static inspection
found a defect in every listed behavior. Every quality cell is deliberately NOT STARTED.

| Original control | Specification | Evidence / remaining limit | Quality |
|---|---|---|---|
| A12 | FAIL | F01; remaining acceptance cannot be averaged into a pass | NOT STARTED |
| A12.1 | UNVERIFIED | Dispatcher/root inspection and bounded controls, not full lifecycle acceptance | NOT STARTED |
| A12.1.a | UNVERIFIED | Real neutral bridge control passed; default setup blocked; doctor/health not executed | NOT STARTED |
| A12.1.b | UNVERIFIED | Structured profile paths inspected; actual validation test ended in cleanup ERROR; switch matrix unrun | NOT STARTED |
| A12.1.c | UNVERIFIED | Role/persona helpers, privacy/metadata boundaries and retained skill methods inspected; behavioral matrix unrun | NOT STARTED |
| A12.1.d | UNVERIFIED | Owned migration/recovery dispatch inspected; mutation/recovery scenarios unrun | NOT STARTED |
| A12.2 | UNVERIFIED | D01 prevents full default fresh/repeat acceptance | NOT STARTED |
| A12.2.a | UNVERIFIED | Default fresh setup FAILED; explicit-store setup is a control only; repeat/native matrix unrun | NOT STARTED |
| A12.2.b | UNVERIFIED | Known prose/unrelated files preserved in controls; full config/roles/packs/hooks/brand/conflict matrix unrun | NOT STARTED |
| A12.3 | UNVERIFIED | No independent complete interruption/recovery matrix | NOT STARTED |
| A12.3.a | UNVERIFIED | D01 returned failure before target publication; committed interruption tests inspected, not run | NOT STARTED |
| A12.3.b | UNVERIFIED | Root/store/receipt and consumed-permission implementations inspected; explicit recovery/replay tests unrun | NOT STARTED |
| A12.4 | FAIL | F01 loses malformed unresolved migration metadata | NOT STARTED |
| A12.4.a | UNVERIFIED | Native/runtime/uninstall and host-operation limits inspected; live/native host controls unrun | NOT STARTED |
| A12.4.b | FAIL | Valid overdue/unknown positive; malformed row silently vanishes with exit 0; F01 | NOT STARTED |

### Selected owned surfaces

All 49 paths were identified from the immutable original diff plus the authorized
fixture. Static inspection covered the current implementations/dispatchers, direct
docs/skills and touched test seams. This is a scope record, not a claim that every
path or acceptance scenario passed before the required stop.

| Group | Selected paths |
|---|---|
| Runtime entries (8) | `bin/li-copilot.py`, `bin/li-doctor`, `bin/li-lifecycle`, `bin/li-lifecycle.py`, `bin/li-managed-transaction.py`, `bin/li-migrate-claude-home`, `bin/li-pack-scaffold`, `bin/li-scaffold` |
| Native installation (6) | `install/directories.txt`, `install/install.ps1`, `install/install.sh`, `install/native.ps1`, `install/native.sh`, `install/verify.sh` |
| Shared runtime primitive (1) | `lib/managed_transaction.py` |
| Direct documentation (5) | `docs/client-adapters.md`, `docs/copilot.md`, `docs/lifecycle.md`, `docs/migrations/_INDEX.md`, `docs/native-installation.md` |
| Skills (16) | `skills/{doctor,health,migrations,pack-create,pack-list,pack-switch,pack-validate,personas-rotate,profile-switch,role-new,role,roles-list,scaffold-internal-tool,scaffold-mvp,scaffold,v4-migrate}/SKILL.md` |
| Original tests (12) | `tests/behavior/{install-fail-closed,install-target-boundaries}.sh`; `tests/integration/{copilot-kit.py,enterprise-workflow-snippets.sh,pack-source-target-resolution.sh,universal-lifecycle.py,universal-lifecycle.sh}`; `tests/shape/extension-pack-contract.sh`; `tests/unit/{managed-transaction.py,managed-transaction.sh,native-receipt.ps1,v37-closeout-additions-present.sh}` |
| Fixture-only follow-up (1) | `tests/integration/universal-profile-context.py`, only the authorized copied-source list and validation method |

## Executed evidence, isolation and limits

The exact candidate was materialized from Git objects into a disposable source;
all **966 files** were verified against blob identity and SHA-256 before execution,
and rechecked unchanged afterward. No source normalization, reset, reducer regeneration
or candidate edits were used. Git modes were recorded separately from Windows file
attributes. Git config/hooks were isolated; original-worktree status used
checkout-equivalent `core.autocrlf=true`, not an isolated false-dirt diagnostic.

Every product invocation used a rebuilt allowlisted process environment: synthetic
HOME/USERPROFILE, home/config/cache/temp, Lintel source/target/home/packs/pointer/
audit/jobs/private-role paths and derived profile/registry/state roots. Ambient
Lintel/Claude/Gstack/Git redirects and BASH_ENV/ENV were not inherited. Subprocess
effective paths were checked before the existing validation fixture ran. Actual
source and any intentional caller reference were then supplied explicitly.
No real personal profile, home-state inspection, network/authentication, hook
activation, global install, paid model, LongPathsEnabled or execution-policy change occurred.

| Actual selector / command | Exit and result |
|---|---|
| Immutable identity, original scope and fixture AST comparison | Assertions completed; 48 + 1 paths, seven contracts and provider verified. The combined preparation process then exited 1 at D01, not 0 overall. |
| Default `li-adapter.py init` | **1; FAILED/BLOCKED**, D01; 5.656 seconds |
| Explicit-store setup control | 0; bounded control only, D02 |
| Real bundled neutral caller bootstrap -> child scaffold | 0; bounded control only, D02 |
| `li-work-artifacts.py --repo <exact-source> --map .claude/plans/universal-implementation/work.json` | 0; APPROVED map and original artifact paths |
| Actual pack-validation fixture selector | **1; 1 test, 1 cleanup ERROR**, D03 |
| Actual migrations skill, valid catalog | 0; one overdue/unknown obligation; unchanged bytes |
| Actual migrations skill, malformed catalog | **0 despite invalid data**; failed specification; reviewer probe exit 3 |

Python actually used was **3.11.9**. Git Bash was the available Windows host, not
stock Bash 3.2/POSIX. PowerShell 7.6.6 was explicitly selected in fixture environments,
but the native tests were not reached; there is no independent native installer pass
in this report. PowerShell 5.1 remains denied/unverified and was not retried or bypassed.
Python 3.9, other OSs, real client discovery/enforcement and private company policy are
unrun. No dependency installation or jq use was needed.

No independent full suite ran. Historical **120/128, 8 failures, 0 skips, 0 partial**
remains FAILED. Later builder-owned 46/46, runtime 7/7, targeted 8/8 and committed 1/1
are not this reviewer's runs and do not manufacture a full-suite pass. Catalog drift,
coordinator reducers, final P04/P08/P10/P14/CI acceptance and human/host approval remain
separate. No A13 interface acceptance or release is granted.

### Durable raw evidence and cleanup

Raw outputs, invocation/environment records, source identities and before/after
hash/size/mode records remain in this reviewer's session artifact store:
`files\p10-review\`. The executable review drivers are
`files\p10_review_probe.py` and `files\p10_test_runner.py`. They are not product changes.
The report includes the complete F01 inputs and reproduction contract so the finding
does not depend on access to a private absolute workstation path.

| Evidence artifact under `files\p10-review\` | SHA-256 |
|---|---|
| `identity.json` | `18df4549f727f2e6179b7356c98b52dbbd9014e9815d572bb0b95d85c2ea152d` |
| `source-manifest.json` | `9faded6f1e207f63445165ca9ee4ab6378aee3cd40346c71910efdeebd167f44` |
| `migration-spec-probe.json` | `da375683c7b72a7292146ee27548def0bfca58148975123427d7b4dfab5acf88` |
| `migration-malformed-three-cells.stdout.txt` | `7614e46e36a53e815f9751249b6829a19d8d795e4c5322b8a0da5f9d8b2b364a` |
| `install-consumer.stderr.txt` | `d42e6ef8ed904c2ee17bae2aa82501e38055c01e3156a9c4fee8d2e3b542cbc3` |
| `failed-default-setup-state.json` (retains initial overcount) | `fa4654c440581a93b55f2231ff0da2e1df423b169aae4f18e322514be4a824ad` |
| `failed-default-setup-normalized-lengths.json` | `6c9d287f5fb87839707e6311e18dad44d62a15dbf98be1d8ed8c04acfe73dafd` |
| `canonical-checks.json` | `92c0d55dbb8bdd66d6fafd2fe0e28f3e3101afae2f4eaab44c77cc28ff54b76e` |
| `actual-validation-fixture.stderr.txt` | `d8905971ca94a30f9ff9d1f28fa64a7797eaca7626320586782d3d42c1ffc194` |
| `focused-cleanup-state.json` | `69bf770bbe8f95f77010b420ae76f8cb8292f992a2d5ef40990127815aa69e6f` |

`review-evidence-index.json` records the wider evidence manifest and retained fixture
state. Failed setup evidence and the cleanup-error fixture were deliberately retained
under the operator's preservation instruction. No cleanup success, silent retry,
global inspection, rollback or broad deletion is claimed. The final read-only evidence
seal reconfirmed the source's 966 identities and unchanged canonical caller bytes.

**Next gate:** MasterSession scopes F01 repair for the original builder, freezes a
new candidate and requests renewed specification review. Only a complete owned spec
pass permits the first whole-P10 quality review.

**Cycle position:** REVIEW / SPEC FAIL -> scoped P10 repair -> new frozen spec review
-> first whole-P10 quality review. A13 remains closed.
