# P13 source selection and preservation review

**Source-only A+B SPEC: PASS. Subsequent QUALITY: PASS. P1: 0 / P2: 0 / P3: 0.**
Distinct independent reviewer, retained from the accepted first unit; no product
implementation, nested reviewer or repair. This accepts the released second source
unit, not whole P13, A18/A19, installed closure or native/model execution.

## Exact selection and authority

| Item | Pinned identity |
|---|---|
| Authority | `bdfd1274b47fb54687076ef89082fddf2ceda3b5` |
| Accepted base | `204ea7253b18fb1849fa6de94e1b283b098039b5` |
| Product, sole parent base | `72253ed82e92cbe085a8cd40cb950195e210c4db` |
| Builder report checkpoint, sole parent product; required review parent | `cc3de22afed7d3f27a291e56bc8f4f39eb2222b9` |
| `reports/P13.md` Git-byte SHA-256 | `363caecbe4f5b48c8b98221aaa01f3761719205f7052cf429b3871ba0e74a0f2` |
| Retained first-unit independent PASS | `09a3c6ec3c3fa2c3232e921f52accc9262088e8b` |
| First-unit review Git-byte SHA-256 | `695e934d0b393e1c8c3a34644db0bb67964344d62830527de40f7c071fb3de58` |
| Original audit baseline | `28061e434be455ca02f135b73244eaf4f73f3a69` |

Selected authority is `packages/P13.md`'s **Source selection and preservation second
unit**, with the same initiative's `work.json`, `spec.md`, plan and original action
acceptance. Read startup, Copilot/Universal adapters, accepted ADR-0028/0029 and relevant
memory. Independently checked both sole-parent relationships, the entire seven-path
base-to-product diff, and the entire 546-line builder report: exact 341-line prefix plus
205-line append. No parent WIP, later producer state or installer repair was imported.

Paths below are repository-relative; initiative reports are under
`.claude/plans/universal-implementation/`. Exactly these seven product paths changed:

| Product path | Reviewed responsibility |
|---|---|
| `bin/li-catalog.py` | Additive selection, validation and closure using the existing inventory/reader |
| `lib/capability-selections.json` | Shared core, demo-script pilot and three source-stage bindings |
| `skills/catalog/references/metadata.md` | Additive selection reference and unchanged-default boundary |
| `skills/catalog/references/selections.md` | Literal query, closure, stage/provenance and failure contract |
| `tests/unit/catalog-selection.py` | 19 focused selection/preservation methods |
| `tests/unit/catalog-selection.sh` | Existing-runner-style Python wrapper |
| `.claude/plans/universal-implementation/reports/P13-skills-preservation.md` | All 126 originals, separate Swarm history, aliases and explicit limits |

Reviewer repository write scope is this report alone; all scripts, fixtures, process
receipts and failed evidence remain private. Product and builder report stayed immutable.

## SPEC, completed before QUALITY

Full scoped SPEC PASS was frozen at **2026-09-22 17:33:04 UTC**, with QUALITY explicitly
not started. All following controls passed; no requirement was waived.

| Control | Verdict and specific evidence |
|---|---|
| S01 - Exact release and source | PASS: chain/hash/prefix and exact seven-path delta verified; retained first-unit acceptance reused, not reissued as new work. |
| S02 - Canonical implementation | PASS: `bin/li-catalog.py:130-145,373-405,457-471` reuses script-bound helpers, strict envelope reader, P06 registry and full canonical inventory. Data roots cannot supply executable helpers. |
| S03 - Actual pilot and shared core | PASS: `lib/capability-selections.json:5-77`; canonical query returns 15 closure members, 21 resources and three demo roles. Plan -> approved arc -> narration -> distinct critique modes remain source declarations, not actor/PPT execution. |
| S04 - Literal deterministic projection | PASS: `bin/li-catalog.py:300-321,489-542`; repeated selections form a deterministic deduplicated union with inclusion reasons. Required core/resources survive agent-only and zero-match display filters. Unknown/repeated IDs and CLI conflicts refuse. |
| S05 - Validate before display/output | PASS: `bin/li-catalog.py:323-406,457-471,582-594`; unselected invalid definitions, duplicate/unknown/alias members, cycles, malformed fields, unsafe/missing resources and inventory ambiguity refuse visibly with no JSON or writes. A valid zero match succeeds. |
| S06 - Conservative stages | PASS: `bin/li-catalog.py:407-421`, descriptor `:78-106`; all general maturity remains unknown. Three actual TEMPLATE ONLY descriptions bind canonical path, literal quote and full parsed-description SHA-256. Wrong/missing/changed proof and promoted status refuse. |
| S07 - Provenance and notices | PASS: `bin/li-catalog.py:423-453,514-540`; provenance IDs, explicit null historical imports, notices and attribution join selected closure. Unknown/omitted required provenance and missing/empty notice assets refuse. Existing registry/notices are unchanged. |
| S08 - Read-only trusted boundary | PASS: `bin/li-catalog.py:46-67,130-145,457-542`; bounded opening-frontmatter guard and invalid-UTF-8 body fixtures passed. Source-data/target helper, YAML and sitecustomize decoys did not execute. No query source/target writes or private policy reads. |
| S09 - Default compatibility/dependencies | PASS: `bin/li-catalog.py:95-127,545-594`; 10 metadata-object and three byte-exact CLI baseline comparisons, canonical Markdown equality and stdlib-only check passed. Missing/malformed descriptor is not read by ordinary metadata/generation/check. Missing YAML/helper dependencies refuse rather than using target code or installing anything. |
| S10 - Substantive original preservation | PASS: `reports/P13-skills-preservation.md:10-69,71-198`; read all 46 workflow + 80 capability audit records, including recommendations/reasons/evidence, and all map rows. Useful methods/outputs, canonical paths, owner/leaves, deliberate retention/change rationales, examples and remaining gaps are traceable. |
| S11 - Historical/source facts | PASS: map `:20-53,200-210`; independently reproduced 86 unchanged/40 previously changed original skill blobs. All 196 canonical skill/role blobs and modes are unchanged in A+B. Original 76-path Swarm history and P04 map remain distinct; P09's 69-role map is retained evidence. |
| S12 - Alias and mode retention | PASS: map `:212-239`; all 46 skill aliases remain, including all 35 exact module suffix methods and remaining arguments. Registry and canonical bodies/modes, including native begin/end and receiver modes, are unchanged. No generated dispatch/native-registration claim is inferred. |
| S13 - Scope and acceptance honesty | PASS: `skills/catalog/references/selections.md:103-152`, map `:241-256`; no activation, policy/model/tool controls, installation, format production, versioning or generated fan-in. Installed resource/alias/provenance closure remains coordinator/P10. |

The preservation pass is substantive source/audit reconciliation, not just a row count:
retained hypotheses, decision methods, bounded retrieval, craft/authoring outputs and
recovery boundaries were compared with their original recommendations. Historical
merge/retire/pack/staged proposals remain visible without becoming deletion or activation
authority. U86/C40 describes original-to-accepted Git bytes, not new model behavior.
No unchanged 196-body corpus or retained 31-test suite is claimed as newly authored work;
map scenarios and structural tests are not 127 executed workflows.

## QUALITY, only after SPEC eligibility

QUALITY was completed and frozen at **2026-09-22 17:36:56 UTC**, after the SPEC record.

| Control | Verdict |
|---|---|
| Q01 - Design and maintainability | PASS: one inventory/parser, shared matcher, bounded source-path helpers and deterministic dependency ordering; no duplicate catalog, cache or execution engine. |
| Q02 - Correctness and failures | PASS: full validation precedes projection/output; type guards protect subsequent operations; diagnostics are explicit; ordinary generation retains the stdlib-only path. |
| Q03 - Adequacy of evidence | PASS: reviewed all 19 selection methods and the ten independent canonical/adversarial probes; retained metadata/registry suites provide regression evidence. Weak body-output-only assertions are supplemented by the independent bounded-read guard. |
| Q04 - Documentation and preservation | PASS: descriptor, public references and all preservation records agree on actual source methods and conservative evidence. Example headings are checked separately by tests; query execution does not read example bodies. |
| Q05 - Scope and simplicity | PASS: seven-path delta only, no new dependencies, installer, scheduler, actor, canonical corpus changes or generated outputs; frozen product diff passes whitespace checking. |

**Findings: P1 0, P2 0, P3 0.** No actionable finding or repair request. Prior F01/F02
remain closed by the separately accepted first unit; the retained-baseline classification
of original F02 is not rewritten as an A+B regression.

## Checks actually executed and evidence

All commands used preopened stdout/stderr logs and preserved real exits. The bounded
suite modules ran directly through the inspected outer Python harness, not an
uninspected shell-wrapper environment.

| Check | Actual outcome |
|---|---|
| Frozen `tests/unit/catalog-selection.py` | 19 methods, OK, exit 0 |
| Retained `tests/unit/catalog-metadata.py` | 31 methods, OK, exit 0 |
| Retained `tests/unit/client-capabilities.py` | 16 methods, OK, exit 0 |
| Independent `independent_spec.py` | 10 methods, 0 failures/errors/skips, exit 0 |
| Independent `preservation.py` | Exact 126-key/audit/map correspondence; U86/C40; 196 unchanged prompt blobs/modes; 76 historical Swarm paths; local links and unchanged contracts verified, exit 0 |
| Default compatibility probes | 10 metadata objects, three exact CLI outputs, canonical Markdown and stdlib-only generation/check in approved fixtures; missing parser/helper and duplicate-identity preservation negatives passed |
| Minimum-version syntax | Production generator and new Python tests parse with Python 3.9 grammar; not a Python 3.9 runtime run |
| Shell wrapper and diff | `bash --noprofile --norc -n` on selection wrapper and `git diff --check 204ea725 72253ed` passed |

Canonical demo JSON stdout SHA-256:
`4b1d44dbe52919a27057001e4daec117892dce2ba4f6ca4696563259d068e7b8`.
Canonical Markdown SHA-256:
`adc2232421ac2b60b44aba37fa39d6a439c199ba936f419c159f1f2bc34af181`.
Default Windows CRLF messages and JSON LF output were compared without normalization.
Generation/no-write adversarial work used private approved fixtures; no source regeneration.

Every product import/call, including outer baseline comparisons, had an inspected
allowlisted synthetic HOME/USERPROFILE/AppData/temp/XDG/Claude/Copilot/Lintel/target and
derived-root environment, explicit executables/PATH/PATHEXT and fixture Git ceilings.
Fixture Git configuration was separate from source `core.autocrlf=true` identity.
Process guards recorded 210 suite children, eight preservation Git children and 64
independent-probe children, with source seals unchanged. Counters are process receipts,
not additional test methods. Failed setup evidence was retained; a pre-payload launch
failure is not hidden or counted as a product test. No personal-home/global-settings,
network/GitHub, policy, install or nested-agent action was performed.

Private evidence is frozen under `p13-selection-review/`: `context/selection.json`,
original-record projections, complete diff/report, unit and independent results,
preservation records, stage decisions, process/environment receipts and source seals.
Its 1,543-file manifest SHA-256 is
`8c4d72467a74e814d6c2537dacaa08d14971b3d11acb569d6dbb042a4fe0aa7f`.
Later report staging/commit verification receipts are separate from that manifest.

## Host limits and next owner

Observed Windows 10.0 build 26200, Python 3.11.9 AMD64, existing PyYAML 6.0.3 and
Git 2.53.0.windows.4; existing Git Bash supplied syntax checking. No Python 3.9 runtime,
Linux/macOS run, full suite or dependency installation. Reparse checks include mocked
Windows attributes, not newly created junctions. No live model, native client,
independent demo actor, rehearsal, rendered PPT or installed-consumer execution occurred.

Recovery coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481` may integrate this source-unit
PASS and join actual installed alias/public-provenance/selection/notice closure with P10.
Future accepted producer changes need explicit stage/map reconciliation at their new
source pin. Parent A18/A19/P13 acceptance, status/welcome, generated/version integration
and human review remain separate. No product repair is requested from the original owner.
