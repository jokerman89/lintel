# P03 joined Windows path investigation

**Status:** investigation complete; no product repair or acceptance waiver.
**Date:** 2026-09-21. **Owner:** original P03 implementer, sole investigator.
**Authority:** the appended read-only scope in `packages/P03.md` at
`1105ebeb4df3792c78437a74a5bd852bea96209d` and MasterSession's bounded dispatch.
Only this report is a repository change. No reviewer, builder or nested agent was spawned.

## Result

The observations have **three distinct execution boundaries**, not one demonstrated
cross-component bug:

1. **Python ordinary-path I/O:** the actual checkpoint reservation fails at 260 characters
   and at the four P08 reported lengths, despite existing parents. P10's actual default
   setup fails at the actual snapshot blob `os.replace`, from a 218-character temporary
   path to a 260-character destination. Same-location extended-path syscall diagnostics
   succeed without shortening either destination. This identifies a path-representation
   limitation in the current Python/Windows process, not missing data or a successful restore.
2. **Git's own path handling:** the actual 283-character bisect ref-lock fails with
   `Filename too long` under isolated unset/default `core.longpaths`. The same executable
   succeeds in a same-depth second synthetic worktree with a **per-command diagnostic**
   `-c core.longpaths=true`. No Python path helper participates in Git's internal ref write.
3. **Fixture cleanup:** P07's actual producer and verifier can retain a long history file,
   while ordinary stdlib read/unlink/cleanup of that path fails. A separate actual
   `TemporaryDirectory.cleanup` reproduction ends in `WinError 145` with the file retained.
   This is not a P07 product failure or a passing P10 D03 test.

Neither extended-path diagnostics nor the Git process option is a shipped fix, a new
default, default-scenario acceptance or authorization to alter workstation policy.
The exact OS-policy/executable-opt-in cause of the ordinary Python limit was **not**
measured: no `LongPathsEnabled` or real global Git setting was inspected or changed.

## Immutable sources and preservation

| Input | Exact identity |
|---|---|
| Investigation parent/coordinator | `1105ebeb4df3792c78437a74a5bd852bea96209d` |
| Preserved original P03 branch | `jokerman-microsoft-universal-context-safety` at `399a2e6b03a9ca3b3dfaddc4f38498f9f88115f4` |
| Accepted historical P03 product | `500adb370c726b86047046998a6a5240ebd8ea8f` |
| Continuation branch | `jokerman-microsoft-p03-joined-path-investigation`, created clean at the investigation parent |
| P08 product/report | `8d477701bf05c545790d4c5fdbdc84945dd130db` / `062ffc6cc0cfecee80646fda2a54bad4db837fad` |
| P08 parent/control | `f9685530c458b456021e30ddab699c03b49614ca` |
| P10 independent report | `1d871338dcdd1b6a535e4b546c2b2d0a7aea031b`, preserved on the coordinator as `46e8b0f` |
| P10 immutable reviewed source | `62ffb9a072c3314b97e015e0f8f98b7f64459fc8` |

Read both complete reports using local `git show`, not another worker's runtime/home.
No P08/P10 WIP or report branch was imported. P10 implementation is not yet present
in the investigation parent, so its actual setup used a disposable export of its exact
reviewed source. All **966 exported files** matched their Git blob identities before
execution; all bytes/modes and the complete file inventory matched afterward. Nine
selected joined source/helper/test files also matched their recorded before-state.
The accepted P03 branch/ref/history stayed intact.

The final source seal, before adding this report, recorded clean porcelain status and
HEAD `1105ebe`. No source file, test, schema, generator, shared plan/memory or setting was
edited. The report commit's sole parent is the investigation parent; its SHA is supplied
in the handoff rather than embedded self-referentially.

### Source bytes and EOL are separate from fixture isolation

For the three Python rows below, LF Git blobs are equal across `1105ebe`, `f968553`,
P08 product and P10 reviewed source. The CRLF working bytes match P08's recorded
p8r5/p8r6 common-dependency hashes exactly:

| File | LF Git-blob SHA-256 | Current CRLF checkout SHA-256 / line count |
|---|---|---|
| `lib\context_safety.py` | `7c0e469694f17936908d6aad69ad613ad9ffd1f3ef0e10a370494147079183c3` | `9291dd8989109ae2b897f6757d9235a22922e265f17b219d963b7daea518800c` / 493 |
| `lib\profile_context.py` | `4c5628232ca7d70d28c35b36242f921e9b49091700cb156224698cc815e030a4` | `cd96361982dfd1f5a3130e17376e022caec02ba71e6aec0b69d8df13c0e86c71` / 1143 |
| `tests\unit\context-safety.py` | `a1e430c2cd922f294b3dc8809a08e6c2588189f73f59cd03640e5ad1e6184412` | `a71fd331070d6be9eea1d6477a386163592ccc104f411c96bee8b9394d50205c` / 503 |

`bin\li-snapshot.py` is LF in both index and working tree, SHA-256
`dd3f1713bddda9024a63cc3da86db1fadb0ac1f125b03f0113c2a372bafed7ab`,
477 lines, Git mode 100755. The three rows above have Git mode 100644.
`bin\_context.sh` is LF, 207 lines: current/control hash
`1bf27608685f69f1038667eceae4b867bd7491b7818fb7478fdf67014f2b1905`;
P08's separately owned interpreter-probe delta is
`b91ad52266e5d2f9b158387ef544d287d1e78cc24af419e54c680bdd51584efb`.
That difference was not mistaken for a common dependency change.

Source checkout/status operations explicitly used `core.autocrlf=true` and
`core.eol=crlf`; shell/bin attributes still select LF. Fixture Git used isolated
configuration and `core.autocrlf=false`. No source normalization or reset occurred.
An initial disposable archive attempt used the checkout settings and failed
its raw-blob hash check before tests. Its incomplete export was retained. A separate
export with explicit archive `core.autocrlf=false`, `core.eol=lf` passed all 966 raw-blob
checks. That preparation failure is not product failure or passing test evidence.
The P10 default setup reproduces with raw LF source; the direct checkpoint/snapshot
probes use the unchanged CRLF joined helper. No evidence attributes these I/O failures to EOL.

## Prior evidence retained, not reclassified

P08's exact reported p8r5 selection was the 18-wrapper preservation run through
`.claude\runtime\p08-isolated-run.py --run p8r5 --jq $Jq`; aggregate **exit 1**,
14 wrappers exit 0, four exit 1. Its exact same-depth control was:

```powershell
python -I -S .claude\runtime\p08-isolated-run.py --run p8r6 `
  --source-ref f9685530c458b456021e30ddab699c03b49614ca `
  --slot 4 --slot 5 --slot 6 --slot 10 --jq $Jq `
  tests\unit\context-repository-ownership.sh `
  tests\unit\context-checkpoint-roundtrip.sh `
  tests\unit\context-safety.sh `
  tests\unit\memory-v2.sh
```

All four control wrappers failed. Per the complete immutable P08 report, all 16
effective path lengths matched per slot between p8r5 and p8r6:

| Effective path | c4/c5/c6 lengths in both runs | c10 lengths in both runs |
|---|---:|---:|
| HOME / USERPROFILE | 140 / 140 | 141 / 141 |
| LINTEL_HOME | 148 | 149 |
| packs / pointer / profile | 154 / 166 / 161 | 155 / 167 / 162 |
| global audit / hook audit / resolver audit | 154 / 159 / 154 | 155 / 159 / 155 |
| jobs / registry / canonical registry | 158 / 164 / 164 | 158 / 165 / 165 |
| state / sessions | 159 / 162 | 159 / 162 |
| repo / source | 137 / 137 | 137 / 137 |

Checkpoint errors were 268/278/277/290 characters; the separate Git ref-lock was
283. Ownership assertions never ran after c4's empty output; apparent equality of
empty outputs in c5 is not preservation proof. These failed wrappers were **not**
rerun as broad suites here. The present direct checkpoint probes retain the operation's
path suffix and exact reported failing lengths; they are not claimed to reproduce
every p8r5/p8r6 outer fixture location.

P08 also discloses its two final `skills\cycle\SKILL.md` authority-confirmation
sentences changed after p8r4/p8r5. That documentation-only delta was self-reviewed,
not behaviorally rerun. Its pre-existing invalid unisolated shell27 evidence and
unknown possible home effects remain untouched; no investigation or rollback of those
effects was authorized or attempted here.

P10 D01 remains failed default setup. D02's explicit-store setup and later neutral
caller/child bridge remain controls, not default acceptance. D03 is an actual cleanup
ERROR, not a passing body or a P07 defect. P10 F01's migration-row parser repair
belongs to its original owner and was not investigated or changed.

## Isolation and observed toolchain

Every diagnostic had a fresh allowlisted process environment and a recorded preflight.
No ambient environment was copied into its initial process. HOME and USERPROFILE were
explicit synthetic paths, not unset values. HOMEDRIVE/HOMEPATH, APPDATA/LOCALAPPDATA,
XDG config/data/state/cache, TEMP/TMP/TMPDIR, Claude/Gstack homes, private-role storage,
Git global-config path and empty hook path were also scoped to the exact owned fixture.
Inherited Lintel/pack/profile/reference/session/audit/registry/Git redirects,
`BASH_ENV`, `ENV` and Python overrides were absent.

Before each diagnostic, Bash `--noprofile --norc` sourced the trusted frozen
`paths.sh`, pack resolver and jobs reader with `LINTEL_JOBS_NO_INIT=1`. The collector
verified the actual 16 effective locations above plus temp/cache against the explicit
fixture and trusted source. Python independently verified `tempfile.gettempdir()`.
The complete environment, resolved native paths and lengths precede each command in
its artifacts. Audit-directory creation during that preflight is recorded; no Lintel,
host or Git hook was registered or invoked.

For the actual P10 setup, the preflight created only empty target-local
`.claude\runtime\audit` directories. The complete before-tree was recorded **after**
that preflight and before product execution, so those directories are not attributed
to installer mutation. Its two seeded files and all recorded directories are unchanged
after the failure. The diagnostic wrappers returning 0 means observations were collected;
the nested product exit 1 and failed syscalls are preserved explicitly, not called passes.

Observed tools:

| Tool | Actual observation |
|---|---|
| Python | CPython 3.11.9, MSC v.1938, 64-bit AMD64 |
| Windows | Kernel version 10.0.26200 |
| Git Bash | 5.3.15(1)-release, x86_64-pc-cygwin; startup-free invocations |
| Git used for synthetic ref probe / selected by Bash | 2.55.0.windows.3, existing Git for Windows |
| Git used for source object/branch checks | 2.53.0.windows.4, existing app Git |

No package/tool download, credentials, network, actual-home inspection, production,
global install, PowerShell-policy change, global `core.longpaths` write or OS-policy
write occurred. Python 3.9, other Windows configurations, UNC/network paths and other
OSs were not tested. Runtime-floor and Python-free native-install requirements remain
unchanged (L-033/L-035, ADR-0030).

## New bounded observations

### Python checkpoint reservation

Called the actual `context_safety.reserve_checkpoint(directory, name)` from the
unchanged joined source. The name retained the timestamp, forty-character repository
key, label and `-context-save.md` shape. The `.claude\runtime\sessions\main`
parent existed; only synthetic parent padding selected the exact normalized length.
All strings in these probes are ASCII, so character and UTF-16-unit counts agree.

| Final path length | Actual `Path.open("xb")` | State immediately after product call |
|---|---|---|
| 259 | Success | Reserved empty file, mode 0666 |
| 260 | `FileNotFoundError`, errno 2 | No checkpoint; parent exists |
| 268 | Same failure | No checkpoint; parent exists |
| 278 | Same failure | No checkpoint; parent exists |
| 277 | Same failure | No checkpoint; parent exists |
| 290 | Same failure | No checkpoint; parent exists |

For each failed destination a **separately labelled diagnostic** opened its exact
same-location `\\?\` spelling without shortening it. Creation/native read succeeded;
ordinary read still failed. The diagnostic content is explicitly not a saved context
checkpoint. Product-before/product-after and diagnostic-after are separate records.
No actual checkpoint was restored, and these controls do not make reservation pass.

Relevant joined source: `lib\context_safety.py:143-159`, ordinary `path.open("xb")`;
`bin\_context.sh:91-109` consumes this helper. Directory construction/path validation
does not establish that the subsequent ordinary file API supports the full destination.

### Actual P10 default setup and snapshot publication

Executed the real reviewed dispatcher with its unmodified arguments and no `--store`:

```text
python <frozen-source>\bin\li-adapter.py init
  --source <frozen-source> --target "<fixture>\installed consumer"
  --client copilot-cli
```

Execution used `runpy` only to record stdlib audit events; neither the dispatcher nor
its I/O results were replaced. Fixture/source paths were 94/107 characters; the target
was 113 and the actual default sibling store 128, matching the original D01 dimensions.
Actual result: **exit 1**, `WinError 3` from `context_safety.atomic_write` ->
`os.replace(temporary, destination)` at `lib\context_safety.py:123`.

| Observed operand | Normalized Windows characters |
|---|---:|
| Default store | 128 |
| Pending snapshot directory | 189 |
| Pending `blobs` directory | 195 |
| `.lintel-write-<8 characters>` source | 218 |
| Sixty-four-character SHA-256 destination | 260 |

Target supplied before/observed after:

| File | Bytes | Before = after SHA-256 | Mode / attributes |
|---|---:|---|---|
| `AGENTS.md` | 20 | `472673fd6409b3c8cff8abc2abb52f7b78b2af6e3f8120bbffb7c9066c6de438` | 0666 / 32, read-only false |
| `unrelated.txt` | 29 | `362be0f9c54222bf07121ea0a442377d8a7090d81c8f253dd31f408f2037ab5b` | 0666 / 32, read-only false |

The synthetic seed bytes are `# preserved context\n` and
`user-owned unrelated content\n`; they are not claimed to be the original reviewer's
seed content. The complete pre/post path set, bytes and modes match.

Residual store: a 163-byte `.lintel-managed-store.json`, SHA-256
`fd2676398fb718454931804f33863b157a5b4d4f2972384140e6aa7c3c5f95fc`,
and empty `snapshots\.pending-snapshot-<id>\blobs` directories. No transaction
directory, completed snapshot manifest, result receipt, restore journal, completion
or retained `.operation-lock`. Target publication never started. All are retained.

A second, separate same-depth fixture called the real `atomic_write` at the same
218 -> 260 lengths and failed identically. Only a subsequent direct diagnostic
`os.replace` using extended spellings for both operands succeeded; SHA-256/20 bytes
verified. It did not modify the failed default setup's store or target. No helper was
patched, alias extracted into product code, alternate store selected or default
installation marked successful.

P03's bounded directory-activation retries do not address this failure: this is blob
publication before snapshot activation, and error code 3 is not the earlier transient
Windows sharing/access error class.

### Git-owned bisect ref handling

Used the observed Git 2.55 executable in a synthetic two-commit repository, root
length 191, with staged/unstaged/untracked changes retained. Existing global/system
configuration was disabled; `core.longpaths` was unset in the fixture. Both detached
trial worktrees were created successfully.

| Invocation | Observed ref operation |
|---|---|
| `git -C <trial-success> bisect start <bad> <good>` | Exit 1; cannot create `.git\worktrees\trial-success\refs\bisect\good-<40-hex>.lock` at 283 characters; `Filename too long` |
| `git -c core.longpaths=true -C <trial-control> bisect start <bad> <good>` | Exit 0; same 283-character lock dimension, final 278-character good ref exists |

The trial names have equal length. Neither invocation changed the caller HEAD,
staged blob, status (`MM value.txt`, untracked unrelated file), file hashes or modes.
`value.txt` remained 14 bytes, SHA-256
`8a8400c18af0b94ebd7bb3b6ac4526877e84c87c4ef371d684d5dfcf1b7804e2`;
untracked content remained 15 bytes, SHA-256
`4466b2bf7332cdb989bf9df12b1df61233f743b622f98a203a26bded88385402`.
Both are mode 0666/attributes 32.

Failed/successful synthetic trial administration is retained. This tests the precise
Git ref-creation boundary, not the entire reproducer/bisect/cleanup skill. The command
option is a diagnostic, not a source/global Git setting change or a new supported default.
A Python I/O-alias repair cannot by itself change Git's internal file handling.

### Profile history and independent cleanup mechanism

The unchanged accepted P07 `bootstrap_profile_context` and
`verify_profile_reference` successfully created/verified a synthetic context using
its real default `sessions\profiles\<64-hex>` and full history digest names.
The current record was 227 characters; history was 286. Both contained 25,843 bytes,
mode 0666/attributes 32, SHA-256
`6c77f1bcd6abdcbabb030fc739fed6edb6b06eb895234b94e7a5b2f8fdcc97d2`.
Ordinary history `Path.read_bytes` failed with errno 2 and `unlink` with WinError 3;
native read verified that history was still present and unchanged.

A separately owned history replica at 268 characters failed ordinary `shutil.rmtree`
on `os.unlink` with WinError 3. A fresh `TemporaryDirectory` replica retained the
same profile-history filename layout at 297 characters. Its **actual**
`TemporaryDirectory.cleanup` failed with **WinError 145** on the nonempty history
directory: that routine's missing-file handling does not delete the long file.
The 39-byte diagnostic history file stayed unchanged, mode 0666/attributes 32,
SHA-256 `6bd2e6cfa03ed01e2dc5daaae900eae63deb77a0fbd8fe2589f6dfddeba26453`.
The cleanup finalizer was detached and no automatic retry or alias cleanup was performed.

This reproduces the stdlib failure mechanism, **not** the complete original P10 D03
validation scenario. It neither upgrades D03 to a pass nor identifies a P07 defect.
P07 already uses checked same-location native I/O (`profile_context.py:675-719`);
an external caller/fixture's ordinary `unlink` or cleanup does not inherit that support.

## Confirmed causes, unknowns and minimal choices

**Confirmed here:** ordinary full-length Python open/replace/unlink operations have
a representation-sensitive limit in this process; the parent/data are not actually
missing. Git has its separately controllable internal ref-path boundary. Stdlib cleanup
can leave a long file behind and surface directory-not-empty after its own error handling.
No common helper mutation, source drift, permission denial, hash collision or EOL cause
is demonstrated by these cases.

**Not established:** which OS policy/executable manifest combination enables or disables
unprefixed long paths; behavior on another Python/Git/OS version, UNC, Unicode-length
edges or case-sensitive/reparse directories; full default installation/restore,
all transaction phases, the original P08 four-wrapper preservation assertions or
P10 D03 cleanup acceptance. The unchanged dependencies and passing historical bounded
P03/P07 reviews remain distinct facts, not blanket joined-path acceptance.

The next coordinator card can select explicitly among these alternatives:

| Alternative | Minimal owned scope | Value and risk/trade-off |
|---|---|---|
| Checked same-location native I/O for Python; independently scoped Git operation handling; faithful fixture cleanup | Coordinated P03/P07 shared path boundary, P10 consumers and affected fixture owners; Git recipe/harness treated separately | Retains existing full roots, hashes, owner bindings and default-store selection. Reuses P07's proven approach only after defining a supported shared boundary. Must cover reads/stat/reparse checks/mkdir/temp/open/replace/unlink/locks/journals and same-location identity; blindly prefixing writes or importing an internal helper is insufficient. |
| Explicit conservative path-support preflight and operator-selected short locations | P03/P10 diagnostics plus each caller that owns location choice | Can reject unsupported operations before partial artifacts. Does not preserve every currently requested default scenario. Short recovery/scratch locations need explicit selection, bound identity and historical-recovery handling; never silently relocate a store, shorten IDs or treat the control as acceptance. |
| Document and verify host/runtime prerequisites instead of providing a product I/O adaptation | Host-support/installation documentation and environment owner; explicit operator/enterprise authorization | Less shared product code, more environment dependence. Cannot assume permission to enable OS/Git settings; process/version coverage and unavailable-control failure must be tested. It is not authorization to change `LongPathsEnabled`, global `core.longpaths` or native install prerequisites. |

Recommendation for scoping, **not implementation authority**: retain full default-path
value with a reviewed same-location Python I/O boundary; keep Git's process-specific
handling and fixture teardown explicit separate subcases. A future native alias must
not change serialized owner roots, profile references, case-sensitive containment,
symlink/junction refusals, ADS/reserved-path checks, snapshot ownership/digests or
consumed restore permission. Test every affected real consumer at these actual lengths
and with later-user-edit/interruption negatives before accepting it.

P10 still owns F01; P08 still owns its partial lifecycle changes and A13 gate.
No shared alias extraction, schema change, installer Python prerequisite, profile
relocation, broad suite run or repair was performed here.

## Evidence seal and handoff

Session-only collectors are `files\p03_joined_path_probe.py` and
`files\p03_joined_path_child.py`; they are diagnostics, not repository tooling.
Actions executed: `versions`, `checkpoints`, `p10`, `snapshot-io`, `cleanup`,
`git-ref`, `tempfile-cleanup`, followed by the read-only source seal.
Each has an environment/command preflight, effective resolved paths, stdout/stderr and
status record under `files\p03-joined-path\`. Original failures, partial export,
default failed store and synthetic cleanup/ref fixtures remain retained, not rolled back.

| Sealed artifact | SHA-256 |
|---|---|
| `joined-source-identities.json` | `7a0ad137079f34565a2f8f03037c577a68de04002344940ffd1e34b6e0b350a6` |
| `p10-source-manifest.json` | `90b8197e76ad30098896d0ecf0753d962ddbc356e5d891107c7fe9dea6dca286` |
| `checkpoints-stdout.bin` | `6cd7d1acb48bcf40d5bd452a2f0bb18f7a5b0a250bd0094e68415dab6b18f447` |
| `p10-stdout.bin` | `4e2ae962b03cf1bfe8615aeb25972816cbf834e394ca0b306a2bf81886d061c2` |
| `snapshot-io-stdout.bin` | `bbb20aa271d1968c9da27afd289ce159eaaf67fd2bb4861b36d79f67d55b3635` |
| `git-ref-stdout.bin` | `2b3eca200907d9146470e42ef128e6b3f5f933c72e3e6824f470cc47d5eea0df` |
| `cleanup-stdout.bin` | `e5ab97d1d0878311d39672288cfc24a607095232a6bef188bb829c19645931f4` |
| `tempfile-cleanup-stdout.bin` | `c2bb3f915269b0a23ef5c392f531ad872552ef88b80d988611cdeb7dfd3911fb` |
| `source-seal.json` | `2e2d5919e8f09512cbeda21a52638034068d6da205437cc6e5ca5fce7ce683c1` |
| `evidence-index.json` | `b5c3f446df6a9d7fa535742b9aa4553e2000b5fb14e69ed427c58d3bf97ccc12` |

No actual-home effects from P08 were examined or asserted absent. No product, test,
schema, global setting or previous branch was repaired. No independent acceptance,
SHIP clearance or waiver is granted. **Next:** MasterSession scopes a coordinated
repair card from these separate mechanisms and their retained support boundaries.
