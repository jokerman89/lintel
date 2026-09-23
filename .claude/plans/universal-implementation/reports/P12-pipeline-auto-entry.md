# P12 automatic pipeline-test entry checkpoint

Date: 2026-09-23. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`,
runtime `0a75211f-455c-4318-864f-bc8023ce9142`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Entry/bootstrap correction is implemented and its admission is observed.
Full-suite status is NOT PASS: both full routes execute 33 methods, with 30 PASS
and three retained P05 snapshot failures, exit 1.** Per the coordinator's follow-up,
freeze this completed entry correction and exact caller evidence without changing
the selected roots, repairing/importing P05 or running another substitute.

## Exact authority and source

Read the full **Automatic integration-test entry** section at
`5e1d21a38f2747b614f8c3d9707e595298ef25eb` from Git only.
The accepted source review `c75eabce70c117cb363076093a91a91158d81e33` was read
completely and verified: 223 LF lines, 17,766 Git bytes, SHA-256
`ce9f35ae4aba80244eb0148e672f3aa38f4907d06abc6b66e269bf827ae20299`.
Its full fourteen-control SPEC/first whole ten-path QUALITY PASS and B01 closure
remain attributed to `fa5139c`, not expanded to the normal runner or native gates.

The clean prior report `e309b173a50c4cb3c021d13d371a29ae5efbdef6` was fast-forwarded
only to that exact report-only child `c75eabce`. All product bytes were unchanged.
No moving master, pending P05 repair or other provider candidate was imported.

Product **`e7e97d463e7960305b1249fbf97f8dbb5e20fe7d`**, sole parent
**`c75eabce70c117cb363076093a91a91158d81e33`**, changes only:

- `tests\integration\document-pipeline-binding.sh`
- `tests\integration\document-pipeline-binding.py`

This report is a separate report-only child; its exact identity and Git-byte
digest are in the handoff. Both commits include the required Copilot trailer.
All 33 assertion-method ASTs are identical to the accepted source. Production
helper/callers, shared providers, schema, normal runner and previous reports
remain unchanged. The separate P05 native-observation repair remains with its
original owner/coordinator under `18787a5`.

## Corrected entry and preserved behavior

`tests\runner\run-all.sh` invokes each discovered script as `bash "$test_file"`
without arguments. The original entry forwarded none to Python's two required
arguments, producing argparse exit 2 before any test. That exact failure was
reproduced locally and retained.

The Python main now accepts omitted `--fixture-root` and `--git`. Default fixture
parent is the explicit repository-local
`.claude\runtime\p12-pipeline-binding`; each run gets a fresh owned
`pipeline-tests-*` child. Existing explicit arguments and `--test` choices remain.
Existing Git is discovered on PATH unless explicitly selected; unavailable tools
fail rather than install or skip. The shell entry uses `exec` to preserve the
actual child exit and retains its missing-Python refusal.

The test-only bootstrap uses standard-library path checks before importing product
helpers. It rejects filesystem-root and linked/reparse fixture roots, creates
owned home/app/local/temp/XDG/Lintel/target/config directories, constructs PATH
from the selected existing Git/Python and required OS directories, and fixes
PATHEXT. It clears the inherited environment before product imports or any
environment artifact. Git global/system config is an owned empty file; prompts
are disabled, and actual strict ancestor ceilings are configured.

An initial automatic-selector run exposed the previous per-case ceiling equal
to Git's starting directory: Git still discovered the source repository. The
existing assertion caught this before fixture Git initialization. Only bootstrap
plumbing now sets the ceiling to the case's strict parent. The root and assertion
were not shortened, changed or weakened. The same automatic-root selector then
passed, including actual CLI success and error controls.

The preflight now records selected executables and isolated fixture parent before
product imports; the shell entry is included in source seals. The file is LF per
existing `.gitattributes`. No application, renderer, record publisher or shared
runtime API was added or changed.

## Actual runs, including non-clearing outcomes

`D` means:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
All outer labels below have preopened stdout/stderr, real exit JSON and explicit
source/target/tool/environment records under `D\logs`.

| Log label | Actual result |
|---|---|
| `pipeline-auto-noargs-red` | Exit 2, zero tests: missing required fixture/Git arguments |
| `pipeline-auto-default-selector-first` | Exit 1: original Git ceiling failed its unchanged ancestor-refusal assertion |
| `pipeline-auto-default-selector-ceiling` | Exit 0: one original selected method through automatic roots/Git and actual CLI |
| `pipeline-auto-noargs-isolation` | Actual zero-test-argument Bash entry: **33 executed, 30 PASS/3 FAIL**, no errors/skips, exit 1; 248.087 seconds |
| `pipeline-auto-explicit-isolation` | Explicit `--fixture-root`/`--git`: **33 executed, 30 PASS/3 FAIL**, no errors/skips, exit 1; 180.018 seconds |
| `pipeline-auto-refusal-cases` | Audit exit 0: five actual refusal outcomes below; no test/skip/artifact success substituted |
| `pipeline-auto-audit-failures` | Exit 1: private recursive inspection hit a long synthetic profile path; retained as failed inspection |
| `pipeline-auto-audit-scoped` | Exit 0: 704 exact environment records inspected; six existing result files read through the accepted native-path helper |
| `pipeline-auto-method-preservation` | Exit 0: all 33 method ASTs/assertions unchanged; Python 3.9 grammar only |
| `pipeline-auto-old-artifact-hashes` | Exit 0: all 397 earlier artifact/QA bytes match their original hashes |
| `pipeline-auto-freeze-evidence` | Exit 0: source/data identity freeze, explicitly `full_suite_pass:false`; not another test run |

The full default invocation supplies **no test arguments**, with stdin closed
like the normal runner. The explicit route uses the existing argument spellings.
The existing `--test` selector was separately observed at the automatic root.
The later explicit-driver selector step was not reached after its full run failed;
no result is invented for that unexecuted step. No whole `run-all.sh` suite is claimed.

Five refusal cases: missing selected Python gives exit 127; missing explicit Git,
missing default-discovered Git, a file used as the fixture parent, and an unknown
option each give exit 2. Stdout is empty and diagnostics explicit. Default Git
absence was exercised directly through the same Python bootstrap; the other
refusals used the actual Bash entry. None imported product or started tests.

Both full runs used deliberately invented ambient credential/profile/cache/Git
configuration markers, not real credentials. Inspection covered 352 environment
records per run, including the initial and all case/command preflights. Markers
are absent; HOME/USERPROFILE/AppData/temp/XDG/Lintel and Git config paths are owned,
PATH/PATHEXT reconstructed, and ceilings are strict ancestors. Source order also
places bootstrap before product imports. Entry environment artifacts contain
the reconstructed allowlist, not ambient credentials/profile/cache variables.
These controls are not an OS sandbox or enterprise enforcement.

The private inspector initially recursed into an unnecessary long synthetic
profile directory and failed. Its follow-up read only the known initial/case/
command-log locations, retaining the initial error. No fixture path or root was
moved, normalized or shortened; this changed inspection scope, not test behavior.

## Exact immutable caller failure

The three failing methods are the unchanged upstream partial-profile, unselected/
stale-artifact and own-context/profile cases. They stop at actual P05 `prepare`
with:

```text
li-review-evidence: Selected input has no tracked or working content: .claude/runtime/state/domains/pipeline-fixture/i0001/ta/01-result.json
```

No P05 result was manufactured to pass them. The coordinator confirmed the
original P05 owner had reproduced and was fixing the same native snapshot
omission family, including longer untracked-evidence coverage. That is relayed
coordination, not a provider repair or accepted-provider run by this owner.

Default run root `A`:

```text
C:\Users\jokerman\reference-repos\copilot-worktrees\jokerman-session-setup\jokerman-microsoft-literate-adventure\.claude\runtime\p12-pipeline-binding\pipeline-tests-vmybtbfp
```

Explicit run root `E`:

```text
D\pipeline-auto-entry\working-explicit\explicit-fixtures\pipeline-tests-rwzmmb4m
```

For each row, the full logical file is
`<root>\<case>\repo\.claude\runtime\state\domains\pipeline-fixture\i0001\ta\01-result.json`.
Every ordinary `Path.exists()` and `Path.is_file()` returns **false**.
The accepted `native_io_path` returns the exact `\\?\C:\...` spelling; its
`is_file()` returns **true**, and a read succeeds with **1,605 bytes**.
This is read-only filesystem evidence, not a native application operation or
substitute passing P05 consumer. All selected roots and files are unchanged.

| Root / case | Logical characters | Actual file SHA-256 |
|---|---:|---|
| A / `case-6tzw1syd` | 263 | `43e12300fcdfff6bae53ecfc69596f539b505da75040788aba4f640a74fe840d` |
| A / `case-f7m2ku5l` | 263 | `837c5b9f8a9919abeb80cf8f93f1637addbf115f892100c4580ab334b4629c8e` |
| A / `case-_vgeejpy` | 263 | `d5623a4dbf14056b34a740cd31e3a0196ccc5a490ab789cf15450ed98a3154f9` |
| E / `case-q89d5wff` | 260 | `9aa6c31756ca161607bab050397e552e72b512d853e7995ff5daa68c63b9c18a` |
| E / `case-xnc8n6na` | 260 | `f83d83cfaa99a7fef67b6bb221a0ca86915aaa6a1a7f10e82f91cc401dec6aca` |
| E / `case-zpgareud` | 260 | `1b6316da0ead6ed89d4ea1f664a2b2cd29357f6c9eb49fb1738ebafda12b9af0` |

Full logical/native path strings, method names, hashes, source seals, environment
observations and actual non-clearing results are retained in the source freeze.
No caller pin was relocated. The coordinator will use this immutable evidence
for its accepted-provider join/recheck; no further substitute was run here.

## Frozen evidence and limits

| Evidence relative to D | SHA-256 |
|---|---|
| `pipeline-auto-entry\source-freeze.json` | `e4aa818f4134d8841d558301994172796c38b7f22e8fc26edbf8ab14cd542fa4` |
| `pipeline-auto-entry\working-observations-scoped.json` | `af6e7945fd642be0d0e6548c178171a4d59247ceeea77ccd3a3e8f9de74d482a` |
| `pipeline-auto-entry\working-errors\results.json` | `6e9fc2a8a39dec1ed72d0a81ed094673ab8c29c2f5371265c270dd10ff4364ba` |
| Both full-run `result.json` files | `63d0695244ca853cad8a5ca8c30bef7b5963705ab2f7778c85774025529289ca` |

The last files have identical outcome bytes, but distinct roots, preflights,
profiles and case-file hashes. They each explicitly record `success:false`,
33 executions and three failures. Successful source/ownership audits do not
turn either suite into PASS.

Execution used the exact working bytes later frozen in the product commit;
post-commit checks verify source identity without rerunning a substitute.
Git versus checkout EOL is recorded separately from raw artifact bytes.
Python 3.11.9 is observed; 3.9 grammar is not execution on that runtime.
No dependency restoration, global setting or policy change occurred.

All 397 original artifact/QA entries remain byte-identical; accepted source and
B01 closure keep their original scope. Caller fixtures and logs are retained,
not cleaned up or relocated, for the coordinator's provider recheck.
No production/helper/caller/provider, installer, shared schema, renderer, native
Office/UI/COM, browser/server/raster, network, P05 decision/corroboration writer,
SHIP or remote operation was changed or performed.

Builder self-review found no remaining owned entry/bootstrap defect after the
ceiling correction. This is not independent acceptance. SAME31 focused SPEC and
QUALITY remain with the coordinator; full-suite success needs the separately
accepted P05 join/recheck. Remaining native/format/shared-runtime and parent gates
stay open; earlier accepted scopes are not revoked or expanded.
