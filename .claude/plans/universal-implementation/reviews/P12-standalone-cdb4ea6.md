# P12 standalone content, Word and PowerPoint review

Date: 2026-09-22. **Independent SPEC: FAIL. P1: 0; P2: 1; P3: 0.**
**QUALITY: NOT STARTED.** F01 is a source/default-preservation defect; missing
Word pagination and complete PPT visual inspection are separate unverified gates,
not evidence of a source/layout defect. No P12, A15 parent or full-format acceptance.

Reviewer: project `f42bff7a-1c88-4784-80c9-60c37f683785`, runtime
`31c39265-13e5-4057-9e78-49bf658749a5`. Builder: project
`09666ec2-ff03-4517-9169-8793149ea8cd`, runtime
`0a75211f-455c-4318-864f-bc8023ce9142`. Coordinator:
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. This reviewer implemented none of the
product and created no child reviewers. Actor separation follows the supplied
host/session records; this report is not fabricated P05 corroboration.

## Exact source and authority

The clean checkout and complete four-commit chain were independently checked:

| Role | Commit |
|---|---|
| Source base | `3ee602f026486da037844322428a7f1d50728d33` |
| Eleven-file product, direct child of base | `cdb4ea660135dbddfd70bb1bfedf676d46f6b670` |
| First report-only child | `9d6fd374132b81ab9b27ae9fd7d6dc47d7fa63b2` |
| Final report-only child; parent required for this review commit | `30bd4e303749819178c76beda036b103baa9ebb4` |

Read startup instructions, Copilot/Universal adapters, review/evidence procedure,
memory, relevant accepted ADRs, selected `work.json`, `spec.md`, `prompt.md`,
interfaces and the COMPLETE P12 card and report. Original acceptance remains
`plan.md:331-342`, `packages\P12.md` and the audited
`action-plan.md:231-243`; the current commission additionally requires preserved
defaults. No replacement task map, reduced QA inventory or shared schema was made.

The frozen builder report is exactly **295 LF lines, 18,872 Git bytes**, SHA-256
`b194d2951387e4979f805f7e2885138b41a97ee106b602fb6614d8164deac015`.
Its checkout is 19,167 CRLF bytes; normalization establishes identity, not a source
edit. Product Git bytes and working bytes are separately sealed. The ten selected
P05/P07/provider dependencies are unchanged from base. Only the builder report
changes after the product commit.

All eleven owned product files and their baseline differences were reviewed:

| Files | Reviewed responsibility |
|---|---|
| `skills\generate-outline\SKILL.md` | Source coverage, language, section IDs, planning hints |
| `skills\generate-write\SKILL.md` | Complete bodies, notes, citations, tables and uncertainty |
| `skills\generate-word\SKILL.md` | Standalone/default/variant compatibility and native procedure |
| `skills\generate-ppt\SKILL.md` | Standalone/default compatibility, narrative and real notes |
| `skills\generate\SKILL.md` | Coupled fidelity, orchestration and honest staged routes |
| `skills\generate-qa\SKILL.md` | Non-destructive fixes and mandatory inspection controls |
| `skills\generate-write\references\fidelity-and-evidence.md` | Existing P05/P07 binding; no new schema |
| `skills\generate-word\references\native-word.md` | Actual reopen/edit path and absent page-render operation |
| `skills\generate-ppt\references\native-powerpoint.md` | Serialized notes, table readback and SVG limits |
| `tests\integration\document-format-pipeline.py` | All source/control/retention cases and fixture behavior |
| `tests\integration\document-format-pipeline.sh` | Interpreter/failure entry and syntax |

Relevant retained consumers and the accepted WordTechnicalEditor,
PPTNarrativeArchitect and SlideNarrationCritic methods were also read. Agents,
shared design, P08/P10 and other formats were not changed or re-reviewed as products.

## F01 - Restore compatible defaults without restoring content caps

**P2, confidence 9/10.** Keeping flag names is not sufficient when their documented
default selection disappears. Exact base-to-product evidence:

| Current location at cdb4ea6 | Base behavior at 3ee602f | Regression |
|---|---|---|
| `skills\generate-word\SKILL.md:64-70` (especially 66), `104-109` | Same file, line 54: omitted `--template` selects `<target>.docx` from brand | The optional flag now describes only an explicit path/name. No step derives the target template when it is omitted. |
| `skills\generate-ppt\SKILL.md:60-64` | Same file, line 51: slide-count default `20-30 based on duration` | The PPT-only fallback is replaced by an unspecified material/duration estimate. |
| `skills\generate-outline\SKILL.md:122-128` | Same file, line 114: PPT planning range `8-15`, default `12` | The presentation-only default disappears together with the rightly removed universal section restrictions. |

For an already verified configured template directory containing the three target
templates, `--brief ... --target technical` with neither `--template` nor
`--use-defaults` no longer tells a cold executor to use `technical.docx`. It can
unnecessarily request a template or choose a different composition. Likewise the
no-count PPT routes have lost their documented starting hints. This is a defect
in the shipped instructional contract, not a claim that an unrun CLI parser or
native application selected the wrong template.

**Concrete repair:** restore `<target>.docx` derivation inside the verified
configured template directory, with explicit `--template` overriding that name.
Keep `--use-defaults` as the explicit permitted neutral/default route; it must not
silently override required policy or require a personal-directory scan. Retain the
legacy PPT-only numbers as **advisory planning fallbacks**, with explicit count,
brief/duration constraints and explained adjustment taking precedence. Do not
restore the 40-word cap, Word/web section quotas, forced Swedish pronoun, content
truncation or a mandatory slide-count gate.

Add focused preservation checks for omitted versus explicit template selection
across all three Word variants and for these PPT-only fallbacks. The current
flag-presence test at `document-format-pipeline.py:310-324` cannot catch loss of a
default; the existing 18 green methods therefore do not disprove this finding.
Evidence: `Q\g01\source-review.json` and its immutable base captures
`019.stdout`, `021.stdout`, `022.stdout`.

## Per-leaf SPEC and acceptance

The content component has useful verified results, but the original prepared
P05 context requires `spec`, `quality`, source retention, both editability checks,
PPT render execution and both rendered-inspection controls for the selected leaves.
These obligations were not narrowed to manufacture a leaf or QUALITY pass.

| Original leaf | Exact current verdict | Evidence and remaining gate |
|---|---|---|
| A15.2 | **unverified** for bound acceptance | Source/content component **PASS**: uncapped reasoning and exact saved retention below. Original required review/render controls remain outstanding; no checkbox closure. |
| A15.3.word | **FAIL** | F01 default compatibility; native creation/reopen/edit and retained content observed. Actual page/layout inspection remains **unverified**, now also permission-blocked. |
| A15.3.ppt | **FAIL** | F01 PPT planning-default preservation; native notes/reopen/edit and six SVGs observed. Complete visual inspection remains **unverified**. |
| A15.1 / A15.3.shared | **unverified** | Full shared-design/profile/work binding is not selected or established by this standalone source. |
| A15.4.pdf | **unverified** | Outside this review; writer/export and page/text-fidelity acceptance not supplied here. |
| A15.4.xlsx | **unverified** | Outside this frozen unit; no verdict on the separately proceeding workbook unit. |
| A15.4.visio | **unverified** | Outside this review; connector/label/rendered-editability acceptance not supplied here. |

**QUALITY eligibility:** none for the complete selected unit. SPEC has F01 and
mandatory observations remain unknown. No whole-unit or artificial source-only
QUALITY PASS was issued. Formal compliance/release clearance was not attempted.

## Verified reusable observations

The source removes universal body/bullet/notes truncation and forced language
conventions while retaining Title/Subtitle/Body/Bullets/Data-viz, hashes, section
IDs/anchors, artifact names, familiar arguments and all three Word variants.
Language follows explicit brief/profile/choice rather than a fixed pair.
Standalone `--brief` needs no fabricated design input; `--from-pipeline` is retained
but explicitly gated. Configured mandatory policy outranks scores; neutral style
advice does not become policy. Default preservation is the exception in F01.

The retained 1,258-word en-GB synthetic brief contains ten paragraphs of **107-115
words each**. Independent extraction from the actual saved files confirms all ten
complete paragraphs and both citations, not merely matching word counts. Frozen
tests additionally verify the exact capacity and claim-ledger cells in two editable
Word tables and the editable PPT capacity table. The full ledger, assumptions,
reasoning and material storage/idempotency limitation survive in actual PPT notes.
Six slides resolve to six distinct note parts with the correct section content.
Visible SVG text preserves "ideal", "not a benchmark", non-exactly-once and
untested-failure qualifiers. Citation paths are literal local bundle references;
clickable native hyperlinks are not claimed.

| Actual saved specimen | Independently matched SHA-256 |
|---|---|
| DOCX | `8c8698d12d634e4358bf5f136b6397e066470e6a3a1eada9aca9c0d1099f6bf5` |
| PPTX | `a5910cf41de35a0ab10433089fee8c3b58201a764c765a54f9636d639cdd8e93` |
| Historical failed PPTX, retained as failure | `ad5edca90b2be495446fcc97071c38afacd5e00ebf04afbe10cd595636c085d4` |

The failed deck still aliases every slide to one notes part and loses all ten long
paragraphs. Separate serialized `set_notes` calls are a supported observed repair
procedure, not a claimed fix to the external host. The frozen suite's physical
alias mutation of an owned copy also fails its retention guard as intended.

Supplied native models show saved-copy Word title/table edit markers and PPT title
edit markers; restored models and saved copies match final artifact hashes.
PPT cell readback is recorded as an actual `read_package_entry` operation because
`get_model` omits its cells. These are reviewed builder observations, **not new
reviewer native actions**. API editability is not every-Office-client acceptance.
The six actual returned 960-by-720 SVGs were inspected as XML/text data, not complete
pixels. No model count, ZIP parse or renderer call was upgraded to visual acceptance.

P05 context/QA hashes match the frozen report. All 12 referenced evidence files,
selected artifact/source bytes and immutable QA declarations match. Byte copies of
the original map/acceptance sources match this checkout; the accepted `bind_work`
reader, called only on a reviewer-owned copy, reproduces acceptance digest
`d9da85e023745dcc24480f1fda94c0da4933654dc894600aeb942b3ec468a14b`.
Actual recorded QA exits **3**, with `qa_pass:false`. Independent control evaluation
and CLI execution retain precisely the two mandatory inspection blockers even at
advisory score 100. Fresh synthetic neutral P07 binding does not establish company
policy enforcement; an empty control inventory stays unverified, not a QA pass.

## Checks, isolation and retained evidence

`R` is the supplied, read-only builder evidence root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12`.
`Q` is this reviewer's private evidence root:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

| Executed check | Actual result | Private evidence |
|---|---|---|
| `source-checks.ps1 -Label g01` | Exact chain, eleven product paths, unchanged providers, Git/working-byte identities, defaults comparison and whitespace: exit 0 | `Q\g01\source-review.json` |
| `review-run.ps1 -Label t03 -Mode frozen-tests` | **18/18**, zero failure/error/skip, exit 0; no remaining case directories | `Q\t03\results.json`, `stderr.log` |
| `review-run.ps1 -Label o03 -Mode observations` | Independent long-source, historical loss, notes relationships, model/copy hashes and SVG-data checks: exit 0 | `Q\o03\observations.json` |
| `review-run.ps1 -Label c03 -Mode controls` | Original work identity, bound evidence and refusal confirmed: harness exit 0; actual controls CLI **exit 3** | `Q\c03\controls.json`, `controls-cli.*` |
| `review-run.ps1 -Label s01 -Mode shell-syntax` | Bash parse, Python 3.9 grammar and 14 local references: exit 0 | `Q\s01\syntax-links.json` |

Runtime is Python 3.11.9; a 3.9 grammar parse is not execution on 3.9. All 18 frozen
test methods ran unchanged, imported after the reviewer's preflight. The original
test `main` environment bootstrap was not used: it replaces the environment and
omits explicit PATHEXT/derived bindings. This run preserves the commission's
stricter allowlist throughout instead. The original Bash entry's full 18/18 run is
builder evidence; this reviewer separately parsed its exact shell bytes.

Each product import/call, including direct comparisons, ran inside a cleared
per-process HOME/USERPROFILE/AppData/temp/Lintel/derived-path/PATHEXT allowlist.
Fixture Git ceilings were tested by actual ancestor-discovery refusal; initialized
fixture roots were checked. Subprocess arguments/environments and source seals
are retained. Logs were opened before execution, actual exits preserved. Source
Git/CRLF checks used separate checkout configuration. This is scoped process
isolation, not an OS sandbox or a claim about native-host isolation.

Reviewer harness failures remain recorded: `preflight` failed on Windows' null
audit executable before any product import; `t01` rejected an inherited-but-owned
cwd (17/18 passed); `o01` wrongly required integer-spelled SVG dimensions.
Only these private oracles were corrected. `preflight-v2`, `t02`, `o02` and the
sealed final runs pass. No failed result was relabelled or product file changed.

| Reusable result file | SHA-256 |
|---|---|
| `Q\g01\source-review.json` | `5d7f3afefa8f56d649584dace8cab003fac930c329e88d1a1c61fc462c9db5d7` |
| `Q\t03\results.json` | `d8ea940f26984368b811e113c2171c3db1ea0f3a12e24ec782f8ca44de2e2770` |
| `Q\o03\observations.json` | `b53769c5314ebec6112b6c382c063b168db8f752f0a849f8226df041c4fea3b3` |
| `Q\c03\controls.json` | `be168d67f6482ec7ef68d46e6e581d93cd21f3c8bfd276fdf991a5f38505af57` |
| `Q\s01\syntax-links.json` | `bc61ca9e2c95124fa7e3d2b28bf5c7d071fdc8d03edcd2c6e3dbbb9ba11984e6` |

Each run also has `seal.json`; final product-call runs retain their launcher/check
source copies. No full suite, dependency installation, private-home scan, global
setting/policy change, upload, macro, personal Office input or UI/browser/application
automation was performed. No library fallback, multilingual native matrix or
customer-summary/transparency-note artifact run is claimed from the technical sample.

## Exact next gate and handoff

The original owner repairs only F01 after coordinator release and freezes a new
immutable candidate for this same reviewer. The valid observations above remain
reusable only where source, acceptance and artifact identities remain applicable.
Two changed Word/PPT descriptions still need coordinator-owned generated fan-in.

Word page breaks, heading orphans, table continuation, margins, references and
clipping need actual permitted inspection of the exact saved DOCX. The coordinator
reported Word access was declined; it is **permission-blocked and unverified**.
No retry, COM/shell launch or alternative route is authorized. Complete PPT
wrapping/overflow/overlap/legibility/assets inspection of all six slides is also
unverified. Denied GitHub Copilot UI access must not be retried or bypassed.
The coordinator must supply any newly authorized observations; this review sought
no route around either denial.

Retain this reviewer session for the repaired source or additional valid
observations. Continue SPEC before any eligible QUALITY, then retain normal
independent/compliance/integration gates. No task checkbox, shared ledger, P05
decision/corroboration, remote branch, PR or product source was modified here.
