# Universal initiative final report (P15)

**Status:** A23.5 passes on the frozen head `ad529ebc` (`reviews/A23.5-final-ad529eb.md`). The branch is
published as draft PR #93 by `jokerman89`. Its first hosted strict runs found portability defects,
which the coordinator repaired (see "Delivery CI"). On the repaired head, every CI job passes except
the three that run `document-pdf`. That entry needs a `pypdf` the repository does not declare, and
adding it is an open operator decision.

## Delivery identity

- Delivery branch `jokerman-microsoft-mastersession-recovery`. `main` is merged twice: at
  `e9401f52` (PRs #86 and #87) in `fe9e6284`, and at `9575aaac` (PRs #88–#92, presentation-only)
  in `d6d4d6a8`. The branch is conflict-free against that `main`.
- The product version is `0.11.0`, on all nine manifest fields (`99443cf8`), with a
  `CHANGELOG.md` entry. No tag or release is made.
- The exact head, and the exact diff against `main`, are recorded here at the final freeze.

## Acceptance by area

The count is 108/113 original top-level items. Each area links to its plan section,
where the leaf evidence and the review files are cited.

| Area | Closed | Status |
|---|---|---|
| [A01 Safe execution and recovery](../plan.md#a01-safe-execution-and-recovery-p03-r01) | 5/5 | Accepted |
| [A02 Mandatory control outcomes](../plan.md#a02-mandatory-control-outcomes-p05-r02) | 4/4 | Accepted |
| [A03 Content-bound independent review](../plan.md#a03-content-bound-independent-review-p05-r02) | 5/5 | Accepted |
| [A04 Helper failure semantics](../plan.md#a04-helper-failure-semantics-p01-r01) | 3/3 | Accepted |
| [A05 Universal product identity](../plan.md#a05-universal-product-identity-p06-r03) | 4/4 | Accepted |
| [A06 Honest host capabilities](../plan.md#a06-honest-host-capabilities-p06-r03) | 4/4 | Accepted |
| [A07 Stable effective profile](../plan.md#a07-stable-effective-profile-p07-r04) | 5/5 | Accepted |
| [A08 One lifecycle work map](../plan.md#a08-one-lifecycle-work-map-p08-r05) | 5/5 | Accepted |
| [A09 Concrete specialist modules](../plan.md#a09-concrete-specialist-modules-p09-r06) | 5/5 | Accepted |
| [A10 Proportionate intake and composition](../plan.md#a10-proportionate-intake-and-composition-p08-r05) | 4/4 | Accepted |
| [A11 Honest context capacity](../plan.md#a11-honest-context-capacity-p03-r05) | 4/4 | Accepted |
| [A12 Owned installer lifecycle](../plan.md#a12-owned-installer-lifecycle-p10-r01) | 4/4 | Accepted |
| [A13 Observable learning and status](../plan.md#a13-observable-learning-and-status-p08-r05) | 4/4 | Accepted |
| [A14 Working design contract](../plan.md#a14-working-design-contract-p11-r07) | 5/5 | Accepted |
| [A15 Verifiable document formats](../plan.md#a15-verifiable-document-formats-p12-r07) | 0/4 | Blocked: denied Word, Excel and PDF-raster application routes, denied P12 record persistence, and no Visio writer (a template-only staged slot) |
| [A16 Real browser operations](../plan.md#a16-real-browser-operations-p11-r03r07) | 4/4 | Accepted |
| [A17 Portable, useful agent roles](../plan.md#a17-portable-useful-agent-roles-p09-r06) | 5/5 | Accepted |
| [A18 Optional capabilities without loss](../plan.md#a18-optional-capabilities-without-loss-p13-r06) | 4/4 | Accepted |
| [A19 Coherent discovery and richer skills](../plan.md#a19-coherent-discovery-and-richer-skills-p13-r03r06) | 4/4 | Accepted |
| [A20 Provenance and versions](../plan.md#a20-provenance-and-versions-p07p13-r04) | 4/4 | Accepted |
| [A21 Safe dormant handoff](../plan.md#a21-safe-dormant-handoff-p04-r08) | 4/4 | Accepted |
| [A22 Preserved Swarming integration](../plan.md#a22-preserved-swarming-integration-p04-r09) | 7/7 | Accepted |
| [A23 Boundary regression evidence](../plan.md#a23-boundary-regression-evidence-all-owners-p14-r11) | 4/5 | Blocked: A23.4's strict CI passes on every job except `document-pdf`'s, which needs the undeclared `pypdf` (operator decision); A23.1–.3 and A23.5 are closed |
| [A24 Observable enterprise profile value](../plan.md#a24-observable-enterprise-profile-value-p14-r04r11) | 4/4 | Accepted |
| [A25 Trusted implementation source](../plan.md#a25-trusted-implementation-source-p01-r01) | 3/3 | Accepted |
| [A26 Explicit private-sync destination](../plan.md#a26-explicit-private-sync-destination-p02-r10) | 4/4 | Accepted |

Acceptance means the owning package's independent review passed on exact content. The coordinator
integrated the reviewed bytes unchanged, except through automatic three-way merges or through
resolutions that an independent integration review covers (P10 by SAME, P08 by SAME9db). It is
not live-host activation, compliance certification or model-quality evidence unless the area
says so.

## Blocked items that need an operator decision

A14.5 is now accepted. On the operator's instruction, the framework app's dependencies were
restored task-locally through the Microsoft npm feed proxy, and the image-capable reviewer
`aba328fd` passed both halves, with V1 observed directly (`reviews/P11-a145-static-v1.md` and
`reviews/P11-a145-app.md`). Two items stay blocked:

- **A15.1–A15.4, verifiable document formats.** The Word, PowerPoint, workbook and PDF source
  helpers are integrated. Their acceptance needs rendering and editability evidence through
  application routes that the operator denied (Word, Excel, PDF raster). It also needs P12
  structured-record persistence, which was denied as well. In addition, A15.4's Visio part has
  no implemented writer or editor (`packages/P12.md`); Visio stays a template-only staged slot,
  which no permission would resolve. The operator's question about lifting the Word, Excel and
  record-persistence denials went unanswered, so no authorization is assumed.
- **A23.4, the strict CI suite, blocked only on `document-pdf`.** P12's PDF checks read PDFs
  through an existing `pypdf` installation (`skills/generate-pdf/SKILL.md`), and the local runs had
  pypdf 6.13.2. The repository does not declare pypdf, and the operator refused to have it added as
  a CI dependency (L-054). `tests/integration/document-pdf.sh` therefore errors with
  `ModuleNotFoundError: No module named 'pypdf'` in integration shard 3 on every system, and those
  three jobs fail. The entry is neither excluded nor weakened. A23.4 closes once the operator
  authorizes pypdf for CI or chooses another course.

None of these five items counts as accepted, and none is waived.

## Preserved Swarming integration

A22 accepted all 76 paths of the original Swarming delta
([P04 preservation map](P04-preservation.md)). At the delivery head, 75 of them exist at their
original path. Row 2, `0026-first-class-swarming.md`, exists at its mapped destination,
`.claude/decisions/0027-first-class-swarming.md`, with its original body. No path is lost.

## Coordinator-owned changes

These are reviewed at A23.5, not by a package review:

- **P08 integration reconciliations.** Reconciliations 1–3 are test reconciliations. 4 and 5
  remove catalog kinds whose producers were retired. 6 and 7 declare A13's resources in
  `ADAPTER_RESOURCES`, `lib/memory.sh` included, and add `bin/li-lessons.py` to the core
  selection. SAME9db's whole-P08 integration review covers reconciliations 1–6.
- **CI (ADR-0032).**
  - `run-all.sh --shard K/N` (`8651f392`), with its runner contract.
  - The sharded `ci.yml` (`736cb82f`), with the PowerShell 7 selector and a short `TEMP` on
    Windows (`b3620e5c`), and separate tier steps (`6d12fd91`).
  - The runner's `N/A` category for `platform: windows-only` skips off Windows (`917d7125`), and
    the 22 canonical skip reasons (`89131723`, only reason strings change).
  - The repair after the first hosted run (ADR-0032, "First hosted run"):
    - plan bullets that parsed as task definitions (`261efeae`);
    - the CI environment (`d739d479`): the declared YAML parser, plus a synthetic home and a
      physical temporary root on every system;
    - product portability: the PATH Bash in the review and swarm readers, and no bytecode written
      into installed kits (`d677efaa`); resolved lifecycle staging roots (`3dc8a01b`); and raw
      script and style regions that close on newer `HTMLParser` releases (`8c9893f9`);
    - fixture portability (`497863de`, `9d23accc`, `53383406`);
    - lessons L-054 and L-055 (`c5667a7e`, `ed91ef4f`).
    A23.5's Phase 3 addendum reviews this delta.
- **The `main` merges** (`fe9e6284`, and at the freeze any later presentation-only PRs), which
  resolve the README conflict.
- **Version `0.11.0` and its CHANGELOG entry** (`99443cf8`, `3ea42d70`).
- **Earlier coordinator product commits.** They carry surviving product lines that no package
  review covers as its own content. The A23.5 Phase 1 review statically passes all of them:
  - `80f36fb0`: schema references and refusal before writes (A23.4.g1/g2);
  - `2d83a0c8` and `4d6e9929`: unavailable jq and parser coverage reported as SKIP (A23.3);
  - `ebfbcd0d`: the e2e footer aligned with status-grounded resume;
  - `935b640c`: the welcome footer and the ADR-0025 parity oracle;
  - `aa56a672`: literal failure diagnostics;
  - `ca280747`: deferred annotations for Python 3.9;
  - `98ad7edf`, `59ca1b6b`, `7b0a30cf`, `2cea48ec`, `42900fa2`, `ad605dea` and `6885d9e4`:
    adapter resource closure and selection unions (A23.4.g3);
  - `678ae228`: PDF and XLSX stage evidence left unknown, with Visio template-only;
  - `2b672bbe`, `d7eb92fa` and `0eab731c`: tests;
  - `9f49e261`: `docs/provenance.md` and the upstream registry;
  - `b72ab473` and `1d40193a`: the routing slice, whose code P08's review covers.

## Known limits

- **Platforms.** The local evidence is from native Windows with Python 3.11 and PowerShell 7. The
  PR's CI adds Linux (Python 3.12.14), macOS (Python 3.12.10, Homebrew Bash) and hosted Windows
  (Python 3.12.10, PowerShell 7). Windows PowerShell 5.1 and a Python 3.9 runtime are not verified.
- **Compliance.** Required-policy enforcement stays UNVERIFIED, because no required-policy
  source is resolved.
- **Host.** An outside actor restores journal timestamps about every 300 s (IC-F01); its identity
  is unknown. P10's bounded retry handles it, and F-INT-5 shields the tests' retry accounting.
- **Strict suite.** jq is denied locally (L-046), so the strict full runs are the PR's CI runs,
  on Python 3.12 against the local 3.11 evidence.
- **P08 advisories.** SAME9db's recheck of `624` routes five P3 advisories here:
  - `state.sh:32` handles drive-relative and UNC paths incompletely;
  - `workflow.sh:114-122` re-exports an unset profile reference as empty;
  - `li-work-artifacts.py:72` imports P04's private `_task_sources`;
  - the routing scan is worst-case O(n²) and lowercases byte-wise, and fails safe;
  - the whole ledger is rescanned repeatedly.
- **Unrouted finding F-HOOK-MKDIR.** 25 hook files still run the unguarded
  `mkdir -p "$LINTEL_HOME/audit"`, for example `hooks/shared/customer-data-block/run.sh:25`.
  It is outside every released package scope.
- **Invalid historical evidence.** The `shell27` and `q02` isolation incidents stay invalid, and
  their effects on the actual home are UNKNOWN.
- **Standing limits on closed items** (the A23.3.s3 reconciliation):
  - P07-3: live UNC I/O;
  - P08-5: the case-sensitive positive;
  - P09-5: the installed test's path budget at a long root;
  - P10-4: the long linked-worktree positive;
  - P13-6: the `verify.sh` upstream listing without yq.
  X1, Python 3.9; X4, Windows PowerShell 5.1; and X5, live host and native role registration,
  appear under Platforms.
- **SAME9db's carried P08 limits:**
  - the 704/aa5 seam is qualified by revision;
  - the inherited P03/P07 14/18 and 22/23 groups are not exercised at their failing depth,
    because the joined runs use short roots;
  - the cycle authority sentences are reviewed as instruction text only;
  - host activation, native roles and paid models are not verified.
- **Unknown causes.** The cause of the intermittent WinError 5 on journal replacement is not
  established.
- **Later review advisories, all P3.**
  - SAME9db's integration QI-1: `li-lessons.py:380-381` reads the lessons template without
    `OSError` handling, so a missing template gives a traceback instead of a typed refusal.
  - QI-2: the gated `_audit.sh:53` still names `pack-lifecycle`.
  - QI-3: the node-absent fallback of `hooks-registration-safe.sh:41` misreads escaped quotes.
  - The A23 unit's Q1: `universal-a23.py` runs a whole P09 test module through `runpy`.
  - P13's N1: the installed-consumer entries are a large share of a Windows CI shard.
- **A14.5 restore.** 24 lock entries carry SHA-1 integrity only, because the feed supplies only a
  shasum. The tarballs arrive through Azure DevOps' first-party CDN redirects, and the signed
  delivery URLs are never copied into reports.

## Evidence at the final freeze

The frozen head is the commit that adds this section. Its product differs from `14ab496e`, the
targeted run's tree, only in `CHANGELOG.md` wording and in `presentations/`, which equals `main`
`9575aaac`. Evidence lives under the coordinator's session files, `verification/<label>/`. All
runs used launcher `d288e74b` with PowerShell 7 only, synthetic roots and no other `LINTEL_*`.

**Joined run on the integrated tree** (`3d7f1284`, whose P08 content equals `3ff59984`):

| Label | Result | `results.json` SHA-256 |
|---|---|---|
| `fin2-kit` | `copilot-kit`: Ran 50 tests in 12,578 s, OK, no skip | `857bcdbe…baa70eeb` |
| `fin2-rest-a` | 72/73; `domain-installed-consumers` exceeds its own 235-character budget under the launcher's long root | `b82813c5…5f7adeff` |
| `fin2-dic-short` | the same test from a short work directory: exit 0 | `e0dcf3c5…5075a70b` |
| `fin2-rest-b` | 74/75; `catalog-installed` is F-INT-6, now fixed, reviewed and integrated | `4496f946…679654a8` |

**Targeted run on `14ab496e`** (`fin3-targeted`, 16/16 exit 0, `results.json` `cfdfdb09…cb84947f`),
covering every executable change since `3d7f1284`. The one exception is `ci.yml`: only CI itself
exercises it, and it was validated statically and in the A23.5 review. The entries are:
- the runner contract, with the platform N/A and shard cases;
- `context-safety`, `profile-path-identity` and `snapshot-ownership`, whose skip reasons changed;
- `catalog-metadata`;
- CI's cheap steps: catalog, instructions, adapter check, wiki and `install/verify.sh --all`;
- the whole shape tier;
- `universal-profile-context` and `universal-a23`;
- `domain-installed-consumers` from a short work directory;
- `catalog-installed` (1,254 s) and `review-evidence` (1,000 s).

**Independent verdicts added in this delivery's final phase.** Earlier verdicts are preserved under `reviews/`:
- P10: `f460eb9f`, `9ca6402a` and F-INT-5 (`70bdcd69`).
- P09's installed closure: `2e71a94b`.
- P13:
  - the installed consumers (`d0eb793e`);
  - the fan-in (`2172dd31`);
  - N3/N5 (`8a1ebf33`);
  - F-INT-6 (`0a6df5f6`).
- P08:
  - the recheck of `624` (F06 accepted, `a337161c`);
  - the whole integration review (`f724834c`).
- The P14 A23 unit: `8a74d548`.
- A14.5: the static page (`562f0386`) and the app (`9d23f2ff`).
- The P14 A23 unit's first review (`fb17f69f`, SPEC FAIL, repaired) and its recheck.
- A23.5: the Phase 1 notes (`9c6f65a4`), the Phase 1b notes (`edd2f556`) and the Phase 2 final
  review (`reviews/A23.5-final-ad529eb.md`).

**Not run locally:** the strict `--require-all` suite, because jq is denied (L-046); Linux and macOS;
Python 3.9 and 3.12; and Windows PowerShell 5.1. The delivery PR's CI supplies the strict suite on
all three systems, and A23.4 closes on it.

## Delivery CI

PR #93's CI runs the strict suite in 21 shard jobs plus a syntax job (ADR-0032). The per-job logs
and summaries are under the coordinator's session files, `ci93/`.

| Run | Head | Outcome |
|---|---|---|
| `36054668106` | `2ab1f25d` | The first hosted strict run. It failed on all three systems; ADR-0032's "First hosted run" section records the causes. |
| `36063322462` | `c5667a7e` | The repair batch. It confirmed most of the repair and exposed two further classes: macOS `mktemp` ignores `TMPDIR`, and a quiet skip was counted as partial. It was superseded when those fixes were pushed. |
| `36065850657` | `ed91ef4f` | 20 of 23 jobs pass, and each system passes 149 of its 150 entries. The only failing entry is `document-pdf`, in integration shard 3 on each system (27 errors, `No module named 'pypdf'`). |

On `ed91ef4f`, every other entry passes with no skipped or partial result. That includes
`copilot-kit`, `universal-a23` and every `platform: windows-only` method on hosted Windows. Off
Windows, those methods are reported as N/A: 23 on Linux and 23 on macOS. The once-per-system checks
all pass: repository verification, stock Bash 3.2 installation on macOS, `check-install.ps1` on
Windows, and the catalog, instructions, adapter and wiki checks. The jq-dependent assertions X2,
C-5 and C-7 and the platform row X3 therefore now run strictly. A23.4 stays open only for the
`pypdf` decision above.
