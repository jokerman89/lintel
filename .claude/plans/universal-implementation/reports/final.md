# Universal initiative final report (P15)

**Status:** draft for the A23.5 independent final review. It is completed at the final freeze
with the exact head, the joined-run results and the CI results. Nothing has been pushed yet
(L-045).

## Delivery identity

- Delivery branch `jokerman-microsoft-mastersession-recovery`. `main` at `e9401f52` (PRs #86 and
  #87) is merged in `fe9e6284`, so the branch is conflict-free against the current `main`.
- The product version is `0.11.0`, on all nine manifest fields (`99443cf8`), with a
  `CHANGELOG.md` entry. No tag or release is made.
- The exact head, and the exact diff against `main`, are recorded here at the final freeze.

## Acceptance by area

The count is 90/113 original top-level items. Each area links to its plan section,
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
| [A08 One lifecycle work map](../plan.md#a08-one-lifecycle-work-map-p08-r05) | 0/5 | Pending SAME9db's whole-P08 integration review and the joined run |
| [A09 Concrete specialist modules](../plan.md#a09-concrete-specialist-modules-p09-r06) | 5/5 | Accepted |
| [A10 Proportionate intake and composition](../plan.md#a10-proportionate-intake-and-composition-p08-r05) | 0/4 | Pending SAME9db's whole-P08 integration review and the joined run |
| [A11 Honest context capacity](../plan.md#a11-honest-context-capacity-p03-r05) | 4/4 | Accepted |
| [A12 Owned installer lifecycle](../plan.md#a12-owned-installer-lifecycle-p10-r01) | 4/4 | Accepted |
| [A13 Observable learning and status](../plan.md#a13-observable-learning-and-status-p08-r05) | 0/4 | Pending SAME9db's whole-P08 integration review and the joined run |
| [A14 Working design contract](../plan.md#a14-working-design-contract-p11-r07) | 4/5 | A14.1–.4 accepted; A14.5 blocked: the static page's direct image observation (V1) is unverified, and the framework half needs a dependency restore that failed on TLS; no workaround is authorized |
| [A15 Verifiable document formats](../plan.md#a15-verifiable-document-formats-p12-r07) | 0/4 | A15.1–.4 blocked: denied Word, Excel and PDF-raster application routes, denied P12 record persistence, and no Visio writer (a template-only staged slot) |
| [A16 Real browser operations](../plan.md#a16-real-browser-operations-p11-r03r07) | 4/4 | Accepted |
| [A17 Portable, useful agent roles](../plan.md#a17-portable-useful-agent-roles-p09-r06) | 5/5 | Accepted |
| [A18 Optional capabilities without loss](../plan.md#a18-optional-capabilities-without-loss-p13-r06) | 4/4 | Accepted |
| [A19 Coherent discovery and richer skills](../plan.md#a19-coherent-discovery-and-richer-skills-p13-r03r06) | 4/4 | Accepted |
| [A20 Provenance and versions](../plan.md#a20-provenance-and-versions-p07p13-r04) | 4/4 | Accepted |
| [A21 Safe dormant handoff](../plan.md#a21-safe-dormant-handoff-p04-r08) | 4/4 | Accepted |
| [A22 Preserved Swarming integration](../plan.md#a22-preserved-swarming-integration-p04-r09) | 7/7 | Accepted |
| [A23 Boundary regression evidence](../plan.md#a23-boundary-regression-evidence-all-owners-p14-r11) | 0/5 | Pending. A23.1 and A23.2 close with the A23 unit review; A23.3 with the A23.3.s3 reconciliation; A23.4 with its g3 and p2 leaves and the strict CI suite; A23.5 with this final review |
| [A24 Observable enterprise profile value](../plan.md#a24-observable-enterprise-profile-value-p14-r04r11) | 4/4 | Accepted |
| [A25 Trusted implementation source](../plan.md#a25-trusted-implementation-source-p01-r01) | 3/3 | Accepted |
| [A26 Explicit private-sync destination](../plan.md#a26-explicit-private-sync-destination-p02-r10) | 4/4 | Accepted |

Acceptance means the owning package's independent review passed on exact content. The coordinator
integrated the reviewed bytes unchanged, except through automatic three-way merges or through
resolutions that an independent integration review covers (P10 by SAME, P08 by SAME9db). It is
not live-host activation, compliance certification or model-quality evidence unless the area
says so.

## Blocked items that need an operator decision

- **A14.5, the static page and app exercise.** The static page ran, and its review passes seven
  data-backed controls. The required direct image observation (V1) stays unverified, so static
  SPEC is blocked (`reviews/P11-static-single-03.md`). The app half needs a framework build,
  whose dependency restore failed on TLS. No TLS workaround, offline cache or alternative
  registry is authorized.
- **A15.1–A15.4, verifiable document formats.** The Word, PowerPoint, workbook and PDF source
  helpers are integrated. Their acceptance needs rendering and editability evidence through
  application routes that the operator denied (Word, Excel, PDF raster). It also needs P12
  structured-record persistence, which was denied as well. In addition, A15.4's Visio part has
  no implemented writer or editor (`packages/P12.md`); Visio stays a template-only staged slot,
  which no permission would resolve.

None of these is counted as accepted, and none is waived.

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

- **Platforms.** The evidence is from native Windows with Python 3.11 and PowerShell 7. Linux and
  macOS results come from the delivery PR's CI. Windows PowerShell 5.1 and a Python 3.9 runtime
  are not verified.
- **Compliance.** Required-policy enforcement stays UNVERIFIED, because no required-policy
  source is resolved.
- **Host.** An outside actor restores journal timestamps about every 300 s (IC-F01); its identity
  is unknown. P10's bounded retry handles it, and F-INT-5 shields the tests' retry accounting.
- **Strict suite.** jq is denied locally (L-046), so the first strict full run is the PR's CI,
  which uses Python 3.12 against the local 3.11 evidence.
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
- **Unknown causes.** The cause of the intermittent WinError 5 on journal replacement is not
  established.

## Evidence at the final freeze

Filled at the freeze: the joined run on the exact head, the SAME9db and A23 verdicts, and the
CI results.
