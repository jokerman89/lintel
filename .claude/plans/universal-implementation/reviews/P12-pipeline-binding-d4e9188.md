# P12 document pipeline input-binding source review

**Verdict: selected source SPEC FAIL; whole source QUALITY NOT STARTED.**
One P2 finding, B01, with seven confirmed API/CLI discrepancies. P1: 0; P2: 1;
P3: 0. This is the complete commissioned ten-path source review, not native
acceptance, a product repair, or acceptance of the dependency ancestry generally.

Independent reviewer: `31c39265-13e5-4057-9e78-49bf658749a5`, distinct from original
builder runtime `0a75211f-455c-4318-864f-bc8023ce9142` / actor
`09666ec2-ff03-4517-9169-8793149ea8cd`. Coordinator:
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. Final SPEC assessment:
2026-09-22T23:17:49Z. No QUALITY phase or structured P05 decision/corroboration
was started, persisted or represented as authorized.

## Exact authority and source

| Item | Identity |
|---|---|
| Complete release card | `98895a0cbce5430ace5960b1cf9289acdfa856b8`, P12, Existing document pipeline input binding |
| Accepted standalone source prerequisite | `f2c1d09ba473c20a91adfb6f1e5c9967ed758008` |
| Product base / dependency merge | `1b723ad9f00d5c1a8697e60752d644b0b44cf50f` |
| Merge parents, ordered | `124780e24d459162bb6cf024342465babba8eab2`, `2531a2a9046791b0bf77c2ee9bcfd6fba841f57b` |
| Selected product | `d4e91881634867642567ba841bb7c092153986a1`, sole parent the product base |
| Frozen report / this review's sole parent | `7c0ae2967650a269030da2e2916e21b5ff6babf2`, sole parent the product |
| Complete builder report | `reports\P12-pipeline-binding.md`, 213 LF lines / 13,907 Git bytes |
| Builder report SHA-256 | `52e5e9076044c50a6e0f1aac4a79518d3cff3c31c44b5b804f101aa53b86da4b` |

Read the complete release and builder report, all ten selected product files,
the six caller deltas and relevant accepted P03/P04/P05/P07/P08/P09/P11 APIs.
Pinned raw Git and actual working bytes separately; CRLF was not normalized in
product input or evidence. The exact ten-file diff and thirty needed unchanged
dependency/reference files were checked against the base. No moving builder tip,
new provider, native operation or unrelated source review was selected.

## B01: literal anchor text is treated as source identity

**P2, confidence 10/10.** `skills\generate\scripts\pipeline_inputs.py:101-115`,
particularly raw `re.findall` at line 113.

The classifier-overlap check covers only the leading `##` / section-ID match.
The later anchor scan ignores the classifier and reads every `{#sec-*}` occurrence
in the entire heading. Consequently a code example, comment, HTML attribute or
escaped marker can supply the required anchor; conversely, a literal example
beside a real anchor makes valid source fail. This violates the released reuse
of shared source facts, source-identity preservation and explicit refusal of
missing references. It is not a defect in the accepted classifier: the actual
classifier marks all offending spans as inline_code, comment, html_tag or opaque.

Using the unchanged long-content fixture, replace only the first heading's
`{#sec-1}` with the following. Recompute the real downstream hash chain and
prepare a fresh external P05 context; retain the original map, source text,
profile, Word/PPT projections and mandatory inventory. Both the actual Python
API and actual CLI reproduce the same outcome:

| Heading anchor text | Required CLI exit | Actual exit |
|---|---:|---:|
| Ordinary `{#sec-1}` | 0 | 0 |
| Only inline-code `{#sec-1}` enclosed in backticks | 2 | 0 |
| Only `<!-- {#sec-1} -->` | 2 | 0 |
| Only `<span data-example="{#sec-1}"></span>` | 2 | 0 |
| Only escaped `\{#sec-1}` | 2 | 0 |
| Real `{#sec-1}` plus backtick-enclosed `{#sec-999}` | 0 | 2 |
| Real `{#sec-1}` plus `<!-- {#sec-999} -->` | 0 | 2 |
| Real `{#sec-1}` plus `<span data-example="{#sec-999}"></span>` | 0 | 2 |
| Real mismatched `{#sec-900}` | 2 | 2 |

The four incorrect admissions return `verification: current_inputs`; the three
incorrect refusals report `Source section anchor disagrees with` section 1.
`executed:false` and `release_clearance:false` remain honest, but do not repair
incorrect input validation. No file was changed by these admission calls.

**Concrete fix for the original owner:** use candidate anchor spans with offsets
into the unchanged classified source, exclude every overlap with its protected/
opaque regions, then validate the eligible anchor identity and multiplicity.
Reuse the existing classifier; do not strip examples, normalize text, add another
parser or weaken the missing/mismatched-anchor refusal. Preserve optional-anchor
semantics in outline/notes and required anchors in content. Add these paired
regressions to `tests\integration\document-pipeline-binding.py:294-333`; its current
anchor/literal cases cover a plain mismatch and block examples, not these spans.

## Complete selected SPEC disposition

PASS below means the stated source obligation was verified, not whole-unit
admission or QUALITY. The open B01 control blocks the aggregate.

| Source control | SPEC | Evidence / boundary |
|---|---|---|
| Exact owned scope, accepted dependency API use | PASS | Ten paths only; P03 reads, P05 JSON/context, P07 live identity, P08 work, P09 verifier, P11 compatibility/full validation |
| Canonical sibling paths and every source hash link | PASS | Same-bytes wrong-path refusal, fresh-snapshot stale hashes, later drift; original bytes retained |
| Full text, notes, citations, tables, language and stable field order | PASS | Long-source comparisons, CRLF/optional fields, retained native content tests; no truncation or summary substitution |
| Eligible section-anchor identity | FAIL | B01; seven actual CLI discrepancies with matching API results |
| Document-only v1.0 Word/PPT references | PASS | Present sections/fields, coverage, destinations, hooks and types checked; continuation layouts retain IDs |
| Genuine mixed P11 validation | PASS | Full load_design, exact sibling binding, profile/provenance checks; contradictory/unresolved/unselected input refused |
| P05 external context and P07 live required policy | PASS | Wrong generation/policy and real required-profile drift refuse; no neutral fallback |
| P08 original package/leaves/approval | PASS | Wrong package, parent leaf and changed approval refuse; linked authority explicitly bound, not inferred |
| Prerequisites at honest evidence level | PASS | Incomplete prerequisite remains false/source-status-only; execution/acceptance still a caller responsibility |
| Upstream P09 own request/context/profile | PASS | Actual verifier, distinct context identities, selected request/start/result/artifact/evidence; stale, partial, wrong-path and mandatory-unverified cases refuse |
| Templates, logo and explicit configuration | PASS | Selection/current hashes enforced; standalone defaults and override precedence retained |
| Noncircular QA and error/nonpublication behavior | PASS | Inputs admitted without future output QA; actual later mandatory unverified blocks despite score 100; no --out or renderer |
| PDF/XLSX existing production boundaries | PASS | Full source goes to existing methods; no invented projections, converter, formula engine or native acceptance |
| Standalone entry/default preservation | PASS | Retained 22 methods and six argument inventories; three Word variants and distinct PPT advice unchanged |

| Owned path | SPEC disposition | Whole source QUALITY |
|---|---|---|
| `skills\generate\scripts\pipeline_inputs.py` | FAIL, B01 | NOT STARTED |
| `skills\generate\SKILL.md` | PASS, correct caller wiring; aggregate admission blocked by B01 | NOT STARTED |
| `skills\generate-word\SKILL.md` | PASS, source retention/defaults/native gates retained; B01 dependency open | NOT STARTED |
| `skills\generate-ppt\SKILL.md` | PASS, complete notes/continuations/advice retained; B01 dependency open | NOT STARTED |
| `skills\generate-qa\SKILL.md` | PASS, fresh context and real artifact obligations retained; B01 dependency open | NOT STARTED |
| `skills\generate-pdf\SKILL.md` | PASS, original HTML/CSS/converter provenance retained; B01 dependency open | NOT STARTED |
| `skills\generate-xlsx\SKILL.md` | PASS, original organization/formula/cache method retained; B01 dependency open | NOT STARTED |
| `skills\generate-write\references\fidelity-and-evidence.md` | PASS, states intended source eligibility and non-clearing limits; implementation violates B01 | NOT STARTED |
| `tests\integration\document-pipeline-binding.py` | FAIL, required anchor distinction uncovered by B01; existing 30 methods pass | NOT STARTED |
| `tests\integration\document-pipeline-binding.sh` | PASS, explicit existing-interpreter entry and syntax | NOT STARTED |

## Actual independent checks and retained evidence

Private root `Q`:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.
Commands were `Q\review-run.ps1 -Label <label> -Mode <mode>`, not builder reruns
represented as reviewer observations. Logs are preopened, actual exits retained.

| Label / mode | Actual outcome |
|---|---|
| `binding-source-pin.ps1` | Exit 0; exact source/authority/report export, raw/working hashes, scope and unchanged provider checks |
| `bi-t01` / `binding-tests` | Exit 0; 30/30 original new methods, zero failures/errors/skips; completed 23:14:19Z |
| `bi-e01` / `binding-evidence` | Exit 0; 22/22 retained methods, 397 old artifacts, 21 local links, six argument inventories, Bash syntax, Python 3.9 grammar only |
| `bi-x01` / `binding-extra` | Exit 1; seven of eight additional methods pass; original inline-anchor discrepancy retained, zero errors/skips |
| `bi-a01` / `binding-anchor` | Exit 1; nine saved actual API/CLI contrasts, two agree with requirements and seven reproduce B01; zero harness errors; completed 23:16:24Z |

The extra passing contrasts cover document-only format subsets, no invented
PDF/XLSX layouts, wrong-path upstream requests, mandatory-unverified upstream
data, unselected mixed provenance, unchanged external context/target, and invalid
format/leaf arguments. The nine anchor contrasts are confirmation of one finding,
not nine additional product bugs or nine independent reviews.

Every product import/call was inside the inspected allowlisted Python 3.11.9
process. The test's per-case environment replacement was separately checked:
HOME/USERPROFILE/AppData/temp/Lintel/derived paths, PATH/PATHEXT, trusted source
and exact Python/Git, empty config, hooks and fixture Git ceilings. Each subprocess
was checked/logged; inherited tokens, network and undeclared executables were
not allowed. These checks are not an OS sandbox. Outer source-Git/CRLF operations
were separate. The unchanged test classes were invoked after preflight rather
than inheriting their original main bootstrap. Reviewer Bash evidence is syntax;
builder's actual Bash-entry run remains builder-attributed.

P09 fixtures are inert existing-schema request/start/result data, not real domain
execution, P05 decisions, corroboration or use of a record publisher. Mixed font/
license evidence is explicitly synthetic, not real license or rendering proof.
Failed test exits and original sources remain intact; no product fix was made.

| Evidence under Q | SHA-256 |
|---|---|
| `binding-source-pin\source-pin.json` | `caa779f1f4c7f0b3af48655f6e0b55bf2478450c7e698c585ecf33e95fae492d` |
| `bi-t01\results.json` | `dd916bbffc183f92aebdc8535acb3ece6f887801343bb566c6e41dde5b5f907d` |
| `bi-e01\evidence.json` | `d93df066689b4087dc93312ad731c35370498b782b3eee21d313a1579f6b665e` |
| `bi-x01\extra-results.json` | `b261200df1a0eee1bfa0a0b9ba19e399b0f8134410bd0461af5a81d798dc906c` |
| `bi-a01\anchor-results.json` | `d90114efd2c1d4d728a7faee2798230d9906ed076c01e1a291ce1aac25e4b805` |
| `bi-a01\anchor-input-manifest.json` | `ca69b4046a872d9ed204349fadc628e064c70fbf141fc129e3968d21e3aaa8a0` |

The anchor manifest seals all nine complete source/design sets and their actual
external contexts. Results identify exact per-command preflights, stdout/stderr
and exits; they also retain the shared classifier's actual protected spans.
Run launch records, private harness copies, subprocess transcripts and seals
remain available for the original owner's exact replay.
Replays must prepare their own explicit synthetic context/profile rather than
relocating these existing pins.

Independently checked builder freeze/result digests:
`d6fdf2c222f979f5016b600e863f78a3ad6261e38bc3ecc7e1a1deb30b90c40b`,
`e94cc6a13d59ce02e92453ec9d8db2cfef5140d8a9368fa4009814f75348829e`,
`d19ec450794af1d087b831c5a749be97739037f874eebb47bae5d9306f8abfe5`.
These corroborate attribution/identity, not a substitute for the runs above.

## Preserved acceptance boundaries and next action

All 397 earlier artifact/QA files match their original manifests: first unit 135,
workbook 135, selected PPT 60, PDF 67. No artifact, prior failed QA, native source
identity or accepted review was rewritten. Common `f2c1d09`, selected PPT
`5858268`, F01 `02e8028`, workbook `21e5228` and PDF `ae793d3` remain separately
preserved at their reviewed source scopes; this report imports no blanket acceptance.

The original owner alone should repair B01, retain the saved negatives and paired
positives, and return a new immutable candidate to this same reviewer. Complete
selected SPEC must then pass before the first whole eligible source QUALITY.
No P1 does not mean this P2 source deviation is accepted or waived.

Word page/layout permission, XLSX persisted caches/layout, the native PDF's sixteen
unresolved page-3 origins and complete visual inspection, converter/TLS limitations,
and Visio's real writer/editor seam remain open. Previously accepted native PPT
SVG evidence retains only its exact declared scope. No Office/UI/COM, browser/
server, raster/alternate reader, network/install, P05 decision/corroboration,
SHIP or remote action occurred. Shared artifact serialization, full A15.1/.2/
A15.3.shared, format and P12 parent acceptance remain OPEN.
