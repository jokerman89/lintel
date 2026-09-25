# P13 integrated fan-in review

**Verdict: scoped SPEC PASS, then eligible QUALITY PASS_WITH_ADVISORY_P3.**
Findings: P1 0 / P2 0 / P3 3 (N3, N4, N5 below; N1 and N2 are the installed review's
numbers). This is an independent review of the frozen integrated P13 fan-in and the N2
correction on local base `ad1045b8`. It is not final selected P08 SPEC, the F06 appendix,
original-leaf acceptance, a version agreement or delivery. The reviewer changed no
product, test, owner report, descriptor or shared state.

**Delivery status:** the brief asked for a report-only commit on the owner's report child.
The operator rejected the reviewer's branch creation ("Branch creation is a repository
mutation not authorized by user's review request"). No branch, commit or repository file
was created; this review is held in the reviewer's session artifacts for coordinator88.

## Frozen scope

Reviewer: `30146eab-ddeb-467e-8f1b-8da575256ba2` (`claude-opus-5.5`, max reasoning,
long context; unchanged since the installed review). Authority: the P13 card's "Fan-in
rebase and review release (2026-09-24)" at recovery `ae31dbbd` (`packages/P13.md:603-619`
there), coordinator88's assignment message of 14:00, and the P08 card's "P08 integration
branch and reconciliation 6" (`packages/P08.md:2560-2591` there).

| Identity | Exact value |
|---|---|
| Base (local `jokerman-microsoft-p08-integration`) | `ad1045b8b10a56fa3bcc5c310a8cad84f7ccf2c4` |
| N2 product | `e922515cc552bdc6150043e0e1b1987b41693b26` |
| Fan-in product | `f581b07299d5f89b5e878bba112e8e769a9fab8e` |
| Report-only child | `d12bbf6dddc4d03418bf0a42689d544e5b47c844` |
| Owner report Git/LF SHA-256 | `1a4f251c25621e6632f48796e15ccc7eef5d9d5b98987357502ad8f2be5fd7fe` |
| Owner report CRLF SHA-256 | `8a67709d554ef73a5f670426157bd05578d49d4c374c677c0193f1acf18a6ce8` |
| Owner handoff SHA-256 | `73f4c19a358fe607c4cc6d43af75cb2ecc65a313030c7c5ed8d8ffb2e3a9793f` |
| Owner packet manifest SHA-256 (704 entries) | `32adc9f3f3d21a80516d7b54decf77895651af031f47780e958fa25e163216f0` |
| Preview product / report child | `e7f799ec6022a13ff8ff089eddea56106d9d1c24` / `9096135aa4e3f0060110db5fe17f97b1c0498da7` |

Independently verified identity:

- Each commit has exactly its stated sole parent, is unsigned and carries only the Copilot
  trailer. `e922515c` changes only `tests/integration/catalog-installed.py`; `f581b072`
  adds `reports/P13-fanin-proposal.md` and modifies the map, `skills/status/SKILL.md` and
  `tests/unit/catalog-consumers.py`; `d12bbf6d` changes only `reports/P13.md`. From the
  base to the child exactly these six paths change.
- All five stated Git-byte SHA-256 values match (`ece581d9…`, `fc24a67b…`, `87e7ff5f…`,
  `b68aa9cf…`, `b837fa1f…`). Status and its tests are blob-identical to `e7f799ec`, and
  their base blobs equal the preview's base blobs.
- The report is 1,639 LF lines. Its first 1,353 lines are the accepted revalidation report
  exactly; then `9096135a`'s 159-line preview appendix follows verbatim, then 127 new lines.
  Both report hashes match.
- The map change is append-only relative to the base: its 400-line prefix is unchanged, and
  the integrated section replaces only the preview's current-view section.
- The handoff and manifest hashes match; seven spot-checked manifest entries (handoff,
  map-reconciliation/verified receipts and the N2 RED/GREEN streams) rehash exactly.
- All nine product version fields in the seven identity manifests remain `0.10.0`
  (read with Python; jq is denied), and neither `0.11.0` nor `v0.11.0` is a local tag.

## SPEC

| Released obligation | Result and concrete evidence |
|---|---|
| (a) A19.3 126-row map complete and correct against the integrated inventory | PASS. A reviewer verifier parsed the current view: exactly 126 rows, one per audit record (46 WF + 80 CAP, one-based indexes), each with the audit's exact `action`, canonical name/path and a record link. All 126 paths exist at `f581b072`; the tree has 127 skills, the extra one being `swarm`, which appears only in its separate section. The C/U label of every row equals Git identity between `28061e4` and the base (118 C / 8 U). Every registered alias (46) appears on its target's row, the 35 module sub-capabilities exist in their bodies, all 23 evidence keys used are defined, all relative links resolve, and 157 package/leaf pairs match the plan's leaf owners. Against the preview view, exactly 49 rows changed: 48 in the limit column only (24 P08, 14 P10, 5 A13 learning, 3 P13 installed, 2 A13 event) and `hooks-status` in method, example and limit. Since `14b0b51c` the only changed original body is `hooks-status`, whose new doctor-JSON `li-events.py installer` read is in the source (`skills/hooks-status/SKILL.md:43-44`). 58 original bodies changed from `42abfcba` to the base; `status` is the one further change, disclosed as this fan-in's own. |
| (b) A19.4 examples, negatives and migration/alias coverage | PASS. The map adds one worked or recheck scenario and an evidence key per row, and explicit limits; it does not claim 126 executions. Alias argument mappings match the registry and the target bodies' flags (`role --off/--rotate/--frame/--deep-dive`, `role-new --update`, `context-budget --watch`, `context-save --label`, and so on). The installed evidence carries over and was rerun on the N2 tree: `catalog-installed.sh` passed 8/8 with the same 99 child calls and exit distribution as the accepted run. |
| (c) A20.4 P13 part: external-contribution provenance | PASS. Both `bundled_materials` records in `install/upstream-sources.yaml` name source, relationship, local paths, license, notice, attribution and modifications, keep `import_commit: null`, and the corpus keeps release `v2.5.0`. The attribution names each source, links each notice and states the release. Selections that close over adapted material (design-knowledge, frontend-design, document-content, document-ppt) declare both provenance IDs with notices and attribution in their resource closure; the other eight close over none and declare none. In a fresh installed bundle the registry, attribution, both notices and `LICENSE` are content-equal to source, and every adapted local file is present. The existing refusal of a removed notice ran again in the installed suite. N5 records one dangling guide pointer. |
| (d) Status union with P08's read-only jobs observations | PASS. `skills/status/SKILL.md:156-178` keeps original work first, then sources the trusted `$source_root/bin/_jobs.sh` with `LINTEL_JOBS_NO_INIT=1` and explicit repo-local `LINTEL_JOBS_DIR`, `_ACTIVE`, `_ARCHIVE` and `_REGISTRY`, runs `list_jobs --read-only` and `stale_jobs 24`, keeps the stale list after a partial read, reports an absent registry as unobserved, and exits with the reader's nonzero result under `UNVERIFIED`. This matches the P08 card's union exactly. With `NO_INIT` set, `_jobs.sh:59-62` creates nothing, and the explicit directory bypasses its home fallback (`_jobs.sh:43`). |
| (e) Generated fan-in drift and the N2 correction | PASS. On a CRLF checkout of the child, `li-catalog.py --check`, `li-wiki-gen --check` and `tests/shape/cli-tiers-sync.sh` pass, and `manifest-identity.sh` passes its tripwires with the version-parity branch honestly skipped for jq. No generated file needed a commit. N2: `catalog-installed.py:44-47` now checks the unresolved root before `resolve(strict=True)`. With the old order restored in a scratch copy, the new negative failed exactly as intended: a real PowerShell 7 junction was admitted and a `p13i-*` run root was created inside its target. The frozen file passes 2/2 with no admitted root and an unchanged sentinel. |
| (f) Reconciliation 6 (coordinator change) | PASS for the selection contract. `bin/li-lessons.py` is an explicit regular source file that two core members call by name (`skills/capture/SKILL.md:120-123`, `skills/discover/SKILL.md:86`). That meets the resource field's contract (`skills/catalog/references/selections.md:54`). It enters every selection through the shared core, with reason `resource-of:core`, giving a 19-file core closure. Declaring no selection resource for `li-events.py` and `event-catalog.json` also fits: only `audit`, `hooks-status`, `maintenance`, `retro` and `usage-log` read them, and none is a selection member, so declaring them would invent a requirement (`packages/P13.md:124`). This narrows A13's literal fan-in item (`reports/P08-A13.md:703-704`), and the narrowing is disclosed on the P08 card. The adapter part (`bin/li-copilot.py:148`) works as intended: the kit's data-driven refusal now covers 85 required files, and removing `bin/li-lessons.py` from an installed clone makes `scaffold check` exit 2 with "Required source file is missing". N4 records one undeclared transitive dependency. |
| (g) Version proposal | PASS as report-only. `0.11.0` is proposed for all seven identity manifests and both nested marketplace entries; nothing was bumped, tagged or published, and the proposal itself notes that a jq-skipped parity branch is not proof. |

## Independent execution

All suites, tests and analysis scripts ran through a reviewer launcher under PowerShell
7.6.6 (`launch2.ps1`, SHA-256 `86104248bdc733f2dd12002ad57994b44db9b8a4c6f3c6b41693df47f6b3b360`,
derived from the installed review's launcher). It builds each parent environment from
scratch with synthetic HOME, USERPROFILE, APPDATA, LOCALAPPDATA, TEMP, TMP, TMPDIR and XDG
roots under `%LOCALAPPDATA%\Temp\p13v`, a CI-style `python3` wrapper, the Git ceiling at
that root, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=NUL` and no `LINTEL_*`. A new
`-ExtraPath` parameter appended PowerShell 7's directory for the N2 child and, for one
probe, Git's `bin` so the lessons helper could find Bash. No jq or Windows PowerShell 5.1
ran. Git Bash printed no warning, and `/tmp` stayed on another session's existing root
before and after (L-049).

The source is a `git clone --shared` of this repository in `p13v\f`, checked out detached
at `d12bbf6d` with per-command `-c core.autocrlf=true` (no configuration write, L-052).
After all runs its HEAD was unchanged and `git status --ignored --untracked-files=all` was
empty.

| Check | Outcome |
|---|---|
| `bash tests/integration/catalog-installed.sh --keep-fixtures` | exit 0; 8/8 ok (2 N2 + 6 installed), zero skips; `Ran 8 tests in 2618.201s` |
| Retained child receipts | 99 calls: lifecycle init 7 at 0; check 7 at 0 and 3 expected at 2; catalog 70 at 0 and 10 expected at 1; observer 1 at 0 and injected 1 at 3. Six journals `complete` with 477 applied entries; no retry, IC-F01 or traceback text; longest path 153 |
| `catalog-consumers.sh`, `catalog-metadata.sh`, `catalog-selection.sh` | 37, 31 and 29 ok; zero skips; 18 status methods among the 37 |
| Four new status tests against the base status body | 4/4 FAIL (RED), then the frozen body restored byte-exactly |
| N2 negative with the old guard order (scratch copy) | exit 1: linked root admitted; ordinary-root case passes |
| N2 class on the frozen file | 2/2 ok |
| Kit resource inventory and missing-dependency refusal | 2/2 ok in 486.173 s (85 refusal subtests) |
| Generators and shapes | four checks exit 0 (see (e)) |
| Map, owner/leaf, identity and provenance verifiers | all pass, apart from the provenance oracle failure disclosed below |

## QUALITY (eligible after SPEC PASS)

The fan-in is narrow and faithful: an exact reapplication plus disclosed integration facts,
with no change to providers, descriptor, aliases, generated files or manifests. The status
union reuses the trusted provider instead of re-parsing jobs, and its four regressions are
discriminating (all fail on the base body). The map's changed cells are factual limit
updates, and the historical tables remain intact above it.

### N3 (P3): the N2 negative's PowerShell child inherits the parent environment

`catalog-installed.py:319-328` starts `pwsh` with `env = dict(os.environ, …)`, whereas
every `InstalledDiscovery` child gets the test's whitelisted synthetic roots
(`catalog-installed.py:76-100`). PowerShell writes its own state under the inherited
profile. In this run it created
`%USERPROFILE%\AppData\Local\Microsoft\PowerShell\telemetry.uuid` and
`StartupProfileData-NonInteractive` in the launcher's synthetic `h` root at the first
junction creation. Under a non-synthetic developer parent those writes would land in the
real profile. No `POWERSHELL_TELEMETRY_OPTOUT` is set; whether startup telemetry was
transmitted was not observed. The entry now also requires `pwsh` on `PATH` on Windows. It
fails closed, and CI's Windows runner provides it.

Recommendation: pass the child a synthetic HOME, USERPROFILE, APPDATA, LOCALAPPDATA and
TEMP (as the class does) plus `POWERSHELL_TELEMETRY_OPTOUT=1`. Keep the fail-closed
PowerShell 7 requirement.

### N4 (P3): reconciliation 6 declares the lessons helper but not its default resolver

`bin/li-lessons.py` resolves the default store through `lib/memory.sh`
(`bin/li-lessons.py:39`, `:237-249`). `ADAPTER_RESOURCES` does not declare it; `_audit.sh`
and `paths.sh` are covered by `SWARM_RESOURCES`, `context_safety.py` by
`ADAPTER_RESOURCES`, and a missing lessons template already makes `check` refuse. In a
reviewer probe on an installed clone, removing `lib/memory.sh` and its inventory entry
left `scaffold check` at exit 0. `li-lessons.py get --id L-001` then exited 3 with
"cannot resolve the project lessons store: … memory.sh: No such file or directory".

Impact is small: the failure is visible and writes nothing, whole `lib/` ships by default,
and the selection contract rightly excludes an inferred import graph. However,
reconciliation 6's stated goal ("an incomplete installed source must refuse cleanly")
covers the helper but not its default path. Recommendation, a coordinator decision: add
`lib/memory.sh` to `ADAPTER_RESOURCES`, or record why a use-time refusal is sufficient.

### N5 (P3): the installed provenance registry points to a guide that is not bundled

The bundled `install/upstream-sources.yaml:7` says "See docs/provenance.md", but
`docs/provenance.md` is not in the adapter's public docs (`bin/li-copilot.py:61`) and is
absent from the installed bundle. Attribution and notices are not lost: the registry,
attribution and both notices are installed and content-equal, and the installed
`CONTRIBUTING.md` keeps the short rule for new third-party material (source
`CONTRIBUTING.md:189`). What the consumer cannot reach is the fuller contribution
procedure (source URL, exact revision, component path and modification records).

Recommendation, routed to the adapter/provenance owner: bundle `docs/provenance.md` with
the public documents, or reword the registry comment for the bundled copy.

## Evidence and limits

Private reviewer evidence is in `%LOCALAPPDATA%\Temp\p13v`: `o2\` (launcher, scripts,
receipts, streams), `f\` (clone), `t\p13i-nz7kw32s` (retained fixture), `r6` and `r7`
(probe scratch). Installed-suite stderr SHA-256:
`0c545795b4d0ee19c044666fbb0b8d216bd531572445028af40927ba1ee99cff`. Body traces:
positive `8b9f409727c1c4617dba1f4f8e2fec695cd8d4a11d27eabef823661e3632d8dc`, injected
`d6886fcd909dcd73094ad291927ddf65b17f981ef364cd1ab07796dd9309efbc`. Keep until the P13
fan-in closes.

Retained reviewer failures and deviations:

- The first provenance oracle exited 1: it required the installed `CONTRIBUTING.md` to
  equal source, but the adapter intentionally prepends its bundled-source banner. The
  third-party rule is intact at installed line 191. This was an oracle error, not a finding.
- The first `li-lessons` probe exited 1 on a scratch-directory name collision before
  reporting. The first run of its corrected copy failed to compile (an extra parenthesis),
  and that attempt's empty receipt files were deleted to reuse the label; a note in `o2\`
  records both. The third run succeeded and is the evidence cited in N4.
- Two read-only PowerShell `Select-String` calls for citation line numbers were denied by
  the preToolUse hook `HKLM_Software_Policies_GitHub_Copilot_Defender` ("hook errored").
  The same line lookups in the reviewer's private clone were then made with the built-in
  search tool.
- The operator rejected the review-branch creation; see Delivery status.
- The first check of this review file failed on one citation range (`li-lessons.py:237-248`
  omitted the diagnostic at line 249); the range was corrected before the passing recheck.
- Durations are not representative: the installed suite overlapped the focused unit
  suites and verifiers on a host at 87–94% CPU load.

Limits: Windows with Python 3.11.9 only; no Linux, macOS, hosted CI or Python 3.9 runtime;
no jq-based version parity; no model, native role or host activation. The status evidence
is fixture caller evidence, not a live user repository. Compliance and required policy
were not assessed. F06, final selected P08 SPEC, merge, the version agreement and N1's CI
budget stay with the coordinator.
