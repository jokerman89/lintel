# Source selections

`lib/capability-selections.json` is an additive projection over the existing catalog's
canonical IDs, not a second skill inventory. The first pilot is `demo-script`: accepted
DemoNarrativeArc Plan/Critique methods, DemoNarratorJunior and SlideNarrationCritic. It
does not supply a PPT renderer, register an agent or establish an independent actor.

## Read-only operations

From the loaded trusted `LINTEL_SOURCE_ROOT`, with an available permitted shell:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --list-selections
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script --kind=agent
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script --name=DemoNarrativeArc
```

`python` can replace `python3` when it is the Python 3 command. Source/parser dependencies
and explicit source/target boundaries are the [existing metadata contract](metadata.md).
An explicitly approved `--source-root` selects data only; helpers remain script-bound.
No selection input is interpolated into a shell command or treated as a glob, regex,
path or executable instruction.

`--selection` may be repeated for a union of different IDs. Unknown, blank or repeated
IDs fail; IDs are exact kebab-case strings. `--list-selections` lists source definitions
and source-stage evidence and cannot be combined with query/kind filters or a selection.
Both operations require `--json` and cannot be combined with `--check` or generation.

Selection defaults to both skill and agent kinds. Ordinary `--json` still defaults to
skills, with exactly its existing output, and does not read or require the descriptor.
Default Markdown generation/check retain their exact bytes/messages and stdlib-only
dependency floor. A missing optional selection descriptor cannot break default discovery.

## One declared data contract

The strict shared data loader reads the descriptor and the existing declaration-only
`install/upstream-sources.yaml` provenance registry. It never executes a registry recipe.
Unknown fields or invalid types in selection definitions fail; no guessed fallback or
second YAML/profile/host parser is used.

| Descriptor field | Contract |
|---|---|
| `schema_version` | Integer `1`; discovery-selection syntax only, not product or P07 feature semver |
| `shared` | Required selection ID included in every projection; currently `core` |
| `selections` | Nonempty map of selection IDs to the exact fields below |
| `source_stages` | Optional-in-content map of canonical IDs to explicit unknown or evidenced staged declarations; the map itself is required |

| Selection field | Contract |
|---|---|
| `source` | Explicit responsible source file |
| `members` | Nonempty unique exact canonical `skill:<name>` / `agent:<name>` IDs, not aliases or copied frontmatter |
| `requires` | Unique selection IDs; no unknown dependency or dependency cycle |
| `resources` | Unique explicit source files required by this source method, not globs or an inferred import graph |
| `provenance` | Unique IDs in the existing `bundled_materials` registry |
| `inputs`, `outputs`, `limitations` | Nonempty arrays of distinct descriptive strings, never executed or treated as observed results |
| `example` | `{path, heading}` pointing at a source file and exact Markdown heading; a worked source example, not a test receipt |

Paths are normalized, source-relative, regular files with exact source spelling. Absolute,
drive/UNC, backslash, traversal, dot/hidden-component, repeated-separator, linked/reparse,
missing and directory-as-file paths fail before output. The provenance registry's
`local_paths` may also name directories; these define component scope without glob-reading
their contents. Discovery does not read personal packs, target policy files or runtime state.

All selection definitions, dependencies, source-stage declarations and referenced
provenance/resources are checked before querying. An invalid unselected definition or a
no-match filter cannot hide a bad descriptor. The full existing canonical inventory still
enforces name/alias ownership before any projection.

The shared `core` selection retains the nine phase entrypoints, cycle, resume utility and
compliance-gate; source references point to the actual P05 review, P06 host and P07 profile
contracts. It does not parse, bind, activate or weaken any of them. Applicable company
requirements continue to resolve through P07 in the actual authorized workflow. Choosing
a customer-domain role does not select company identity or replace a failed required
profile with neutral policy. Absence of a selection never removes on-disk access.

## Deterministic closure and output

`--list-selections` returns source definitions, their shared root and explicitly recorded
source-stage evidence. `--selection` retains the ordinary metadata envelope and adds:

| `selection` field | Meaning |
|---|---|
| `requested` | Sorted explicit selection IDs |
| `order` | Deterministic dependency-before-dependent closure, including the shared core |
| `definitions` | Only the selected closure's source/input/output/example/limit records |
| `reasons` | Selection inclusion reasons: `requested`, `shared`, `required-by:<id>` |
| `members` | Deduplicated canonical IDs with every `member-of:<id>` reason |
| `resources` | Deduplicated paths with source/example/member/resource/notice/attribution reasons |
| `provenance` | Selected existing source/license/modification/notice records; unknown historical import stays null |
| `source_stages` | Selected members' explicit evidence or `{status: unknown, evidence: null}` |

Returned entry descriptions, identities, aliases, paths and `maturity: unknown` are the
same existing metadata objects. Kind/query/family/name/category/voice/client filters
affect displayed entries only, not required dependency/resource/provenance closure.
`total` counts closure members in the requested kind before filters; `matched` counts
displayed entries. Literal filters reuse the existing matcher. The helper returns paths
and metadata, never selected or unrelated prompt bodies, notice text or example bodies.

Known adapted component paths cannot omit their existing provenance ID. Selected notice
and attribution files must exist and be nonempty and join the resource closure. This
checks recorded source obligations, not license sufficiency, historical import accuracy,
installed distribution, legal clearance or endorsement. Existing records and notices
remain authoritative; no new content is copied and no import revision is guessed.

## Stage evidence without readiness inflation

An explicit stage record has exactly `status` and `evidence`. `unknown` requires null
evidence. `staged` requires `{path, description_sha256, quote}`: the path must be that
member's canonical source; SHA-256 must match its current full UTF-8 parsed description;
the literal quote must still appear in that description. Only this bounded frontmatter
evidence is consumed, not a corpus-wide scan of role/skill bodies.

The descriptor retains Visio's exact `TEMPLATE ONLY` declaration. PDF and XLSX now have
implemented source methods, so their obsolete template evidence is deliberately replaced
with explicit `unknown`/null evidence, not a readiness claim. Their native rendering,
cache and inspection gates remain separate. A changed/missing description, wrong
path/digest/quote or unknown member fails until the descriptor is deliberately reviewed
and updated. `mature`, `implemented` and `verified` are not accepted stage statuses.
A source repair alone does not upgrade maturity.
The legacy `maturity` output remains `unknown`; a source-stage label is a declaration,
not execution, independent review or a promised format capability.

The demo roles have accepted content methods, but no maturity promotion follows. P09's
role preservation and review reports are distinct historical evidence; live mode
dispatch, rehearsal and independent critique still require actual host evidence.

## Worked pilot and failure behavior

For an approved eight-minute synthetic duplicate-submission demo, list/select
`demo-script`, then read only the appropriate selected role:

1. DemoNarrativeArc **Plan mode** accepts the blank brief and returns `arc-DRAFT.md`.
2. DemoNarratorJunior consumes the approved arc and returns words, pacing and factual
   recovery cues. Without a supplied fallback, it acknowledges the missing result.
3. A separate reviewer may use DemoNarrativeArc **Critique mode** and SlideNarrationCritic
   after the script exists. The drafter cannot declare its own independent critique.

The authorized caller persists the named artifacts. Selecting metadata creates no
draft, phase, profile, registration or actor. With no permitted delegation, the same
methods can be read as serial/manual guidance, with independent review explicitly open.
Source example pointers are declaration references; the focused tests resolve their
actual headings separately, not by returning those bodies in a query.

All input/dependency failures return nonzero with a diagnostic and no JSON/partial
success. Source/target files remain unchanged. A valid no-match projection has zero
entries but still names its required closure. Missing runtime PyYAML remains a visible
metadata error and the existing disclosed skills-only catalog snapshot remains a
fallback; discovery never installs dependencies.

The full source bundle and default entrypoints remain intact. Selection does not change
installation, native wrappers, receipt formats, private policy, product versions or
generated outputs. The accepted-P06-engine core/demo installed pilot is separately
recorded evidence, not acceptance of the new P10 engine or every later selection.
New-family installed alias/resource/notice closure remains a coordinator/P10 join.
Physical pruning, external relocation and a new installer/scheduler were not selected.

## Optional family projections

The ten additional records use the same schema, inventory and literal operations.
They describe retained source methods, not ten new workflows or a private-policy choice.
The `core` and `demo-script` definitions remain unchanged.

| Selection | Declared dependency | Focus |
|---|---|---|
| `design-knowledge` | core | Retrieval, tokens and bounded design consultation |
| `frontend-design` | design-knowledge | Frontend decisions, rendering methods and evidence-aware review |
| `document-content` | design-knowledge | Full shared content preparation and repository documentation |
| `document-word` | core | Standalone editable Word method |
| `document-ppt` | design-knowledge | Editable slides, full notes and actual slide inspection |
| `document-pdf` | core | Existing preparation/print/reader path |
| `document-xlsx` | core | Workbook composition and persisted integrity |
| `document-visio` | core | Staged-slot discovery, not a writer |
| `customer-communication` | core | Drafts, empathy/claim review and explicit voice evaluation |
| `regulatory-review` | core | Scoped framework applicability and control evidence |

Use an explicit union for common content plus a chosen format or demo plus follow-up:

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json \
  --selection=document-content --selection=document-word
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json \
  --selection=demo-script --selection=customer-communication
```

There is no conditional-dependency language. Standalone Word/PDF/XLSX require neither
the common pipeline nor unrelated formats. A source/resource in closure is not a request
to read its whole body; choose the actual method/role first. Filters change displayed
entries, not the closure or policy. For example, `--name=match` can validly return no
entry inside a frontend projection while the unchanged ordinary `--json --name=match`
still resolves `skill:skill-router`.

Design resources explicitly enumerate the existing scripts, six contract/token
references, bundled profile and 35 corpus CSV files. Both actual design adaptation
IDs bring their MIT/Apache notices and shared attribution into closure. The recorded
v2.5.0 label is not substituted for an unknown import commit. Empty additional
provenance does not assert originality or legal sufficiency.

The examples below are worked **source procedures**, not newly executed model/native
scenarios. Paths such as `brief.md` refer to explicitly selected synthetic target data,
never private inputs bundled into the descriptor. Every example retains the trusted
source versus owned target boundary. The metadata query only returns declarations.

## Design knowledge example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=design-knowledge
```

**Inputs.** A synthetic case-list brief, an explicit question about changing the spacing
scale from 4px to 8px, and the project's selected current token/reference files. Carry
an existing verified profile reference if profile-bound advice is requested.

**Method and output.** Select frontend-design's advice mode for the decision, or design-dna's
bounded retrieval method for supporting rows. Compare retaining the 4px scale,
switching to 8px, and changing only section spacing; report cost, regression surface
and the brief-supported recommendation. Token/corpus resources and both notices remain
available without reading every CSV or adopting a different company profile.

**Negative.** An explicitly selected but missing profile asset is not permission to
use another brand. A query without relevant corpus hits reports that limitation;
it does not manufacture measured usability improvement.

**Evidence limit.** Source retrieval and alternatives do not render a page, measure
accessibility or prove a model followed the method. The existing bundled fallback
asset remains subject to the accepted P07/design precedence.

## Frontend design example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=frontend-design
```

**Inputs.** A sanitized brief for a small status page, explicit owned output,
the real existing project manifest, and a verified profile/design context. Choose
a single-file target with no shader and no motion or CSS-only reduced motion.

**Method and output.** Read the director and only the needed typography/motion methods.
Use the existing direct-design schema/helper for the bound spec and literal
`generate-web` renderer arguments. Produce and inspect an artifact only through the
actual authorized host operations. Retain the same content, profile and P05 obligations
through rendering/review; an empty library list and no-shader decision are valid.

**Negative.** A contradictory existing framework, unknown stack, changed profile
asset or missing required observation stops that route rather than installing a
preferred framework. No source example authorizes a personal output directory.

**Evidence limit.** Direct source A14.1-.4 is accepted; A14.5's required static visual
V1 remains unverified and framework TLS/build remains blocked. Browser source and
role declarations do not replace those observations or independent review.

## Document content example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-content
```

**Inputs.** A complete synthetic brief with a multi-paragraph decision, a units-bearing
table, citations and a material limitation; an audience/language and explicitly owned
run path. Name the requested formats rather than generating every format.

**Method and output.** The existing outline/write methods preserve source IDs and full
reasoning in `outline.md`/`content.md`, with actual speaker-note content for slides.
Use an explicit union with the desired format for shared-input production. For a
repository-reference task, select generate-docs and ground its signatures,
examples and caveats in the supplied code/tests instead of a slide outline.

**Negative.** Do not remove a qualification or truncate canonical content to forty
words to fit a layout. Missing or unaccepted shared design/input binding cannot be
filled with a fabricated `design-spec.json` or claimed as serialized-pipeline success.

**Evidence limit.** The repaired input-only admission source is accepted and
retains complete source, work and profile identity. It does not render, publish
an artifact, certify a native format or clear the remaining shared-runtime gates.
The earlier B01 rejection remains historical evidence, not the current source.
`document-content` includes the helper and its declared trusted preflight resources.

## Word example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-word
```

**Inputs.** An explicit `synthetic-brief.md`, target `technical`, an authorized blank
native/default choice through `--use-defaults`, and a new owned `synthetic.docx`.
No personal template search is authorized by these inputs.

**Method and output.** Follow generate-word's standalone example and the exact native
Word procedure only if those operations are actually available. Preserve headings,
full reasoning, editable tables and citations; use WordTechnicalEditor for the
format-specific review method. Report actual saved-content/edit/reopen observations.

**Negative.** Without `--use-defaults`, a required missing `technical.docx` template
is an unresolved input, not an implicit blank document. Missing page rendering is
unverified, not rescued by a successful content/model readback.

**Evidence limit.** Source acceptance does not clear the denied Word page-layout
route. This standalone projection excludes common pipeline and other format methods;
explicitly union `document-content` when requesting `--from-pipeline`. Selection
itself creates no document and grants no native permission.

## PowerPoint example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-ppt
```

**Inputs.** A synthetic workshop brief containing evidence and caveats, explicit
audience/time, authorized default/template choice and new owned PPTX output.

**Method and output.** Retain the required Design DNA slide-retrieval resources,
then read generate-ppt and the selected narrative/critique method. Compose concise
visible slides while retaining full reasoning in actual serialized notes or an
explicitly delivered long-form companion. Inspect real saved tables, notes and
rendered slide coverage through available tools.

**Negative.** Missing notes support or incomplete required visual coverage stays open;
a talk-track Markdown file is not automatically saved PPT notes. No fictitious
native actor, slide render or independent critique follows from a role name.

**Evidence limit.** Prior selected native PPT acceptance remains scoped to its actual
artifact. This query does not repeat it or certify a shared rendered pipeline.
Explicitly union `document-content` for `--from-pipeline` input admission. The
standalone projection includes design knowledge, not the entire frontend-role family.

## PDF example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-pdf
```

**Inputs.** An authorized local Markdown/HTML brief, explicit owned PDF output, page
size and exact source/page oracle; actual permitted converter, print and reader tools.

**Method and output.** Keep the original source, use the existing prepare/print
methods and accepted browser operation when available, then inspect text retention
and physical page boundaries with the existing checker. Record actual tool/version,
source/output and reader evidence separately from visual inspection.

**Negative.** A wrong physical page size, clipped effective boundary, absent reader
or missing required visual observation cannot be hidden by a nonempty PDF file.
Do not substitute a successful metadata query for conversion or print.

**Evidence limit.** PDF now has implemented accepted source methods; unknown maturity
does not mean TEMPLATE ONLY. Required visual/full-format and denied record routes
remain separate. Standalone conversion does not depend on the rejected shared join.

## Workbook example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-xlsx
```

**Inputs.** Synthetic typed quantities and unit prices, a formula/units specification,
new owned workbook, expected-cell oracle and actual permitted calculation/read APIs.
Choose CostAnalyzer or CapacityPlanner only for the matching brief.

**Method and output.** Preserve source rows and assumptions; create editable cells
and formulas through the actual writer. In the native reference example, quantity 3
at price 12.5 yields live 37.5. Separately inspect the saved package/cache, reopen
editability and requested layout. Preserve original failed or unverified evidence.

**Negative.** Live 37.5 with an absent/stale saved cache does not pass persisted
integrity. The existing checker distinguishes missing, stale, malformed and supported
cached/formula evidence; no metadata projection performs recalculation.

**Evidence limit.** XLSX source is implemented, maturity remains unknown, and native
cache/layout gates remain incomplete. No common pipeline, frontend role or another
document format is forced into this standalone selection.

## Staged Visio example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=document-visio
```

**Inputs.** A sanitized request for an editable topology diagram, with its desired
labels/connectors and output type stated only for discovery.

**Method and output.** Return the real generate-visio description, canonical path
and exact staged proof. Identify missing writer, connector/label and editable-render
acceptance. SystemArchitect remains a source reasoning method, not a diagram engine.

**Negative.** Refuse to describe the slot as an implemented VSDX/SVG/PNG/drawio writer.
Do not create NetworkArchitect from a stale name hint, run speculative recipes or
assume access to personal stencil/template directories.

**Evidence limit.** This is deliberately a staged-discovery scenario. The unchanged
TEMPLATE ONLY digest is source evidence; no native diagram or completed format is
claimed, and a frontmatter `full` hint cannot promote it.

## Customer communication example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=customer-communication
```

**Inputs.** Sanitized supplied meeting facts, recipient role, medium and decision ask;
explicit applicable voice requirements. Select corpus/rubric/verdict evidence only
if the operator actually requests the separate eval method.

**Method and output.** Select EmailCustomerDrafter for a decision-ask draft and
CustomerEmpathyCheck for the relevant review; use the proposal/RFP/briefing roles
only for those distinct outputs. Keep customer copy separate from internal pricing,
legal and pre-send checks. The authorized caller owns persistence and any later sending.

**Negative.** An unknown deadline remains a question, not invented urgency or a
commercial commitment. No corpus/evaluator evidence means NOT_EVALUATED, not whole-corpus
calibration. An email need not load demo narration; union with `demo-script` only
when its methods are explicitly needed.

**Evidence limit.** No message is sent, scheduled or published by source selection.
It does not scan private packs/personas/customer repositories or establish an
independent actor. Company identity remains the existing separate P07 overlay.

## Regulatory review example

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=regulatory-review
```

**Inputs.** A synthetic recruiting-assistance use description, actor/jurisdiction/date,
data flow and selected primary-source/control evidence. A requested framework is not
automatically an applicable mandatory company rule.

**Method and output.** Apply EUAIActReviewer's actual intended-use/actor analysis.
Using a third-party GPAI model does not alone remove an Annex III use analysis.
Select GDPRReviewer for the personal-data obligations and SOC2Reviewer only for an
applicable audit scope. Return sourced obligations, missing evidence and legal-owner
questions through the existing P05 control contract.

**Negative.** Unknown legal version, effective date, territory or required evidence
stays unverified. Do not infer N/A from a customer address, assert certification,
impose a universal SOC2 obligation or bypass required controls by deselecting this group.

**Evidence limit.** These are optional framework methods; generic security and
applicable policy remain shared core obligations. No legal lookup, legal decision,
compliance execution or rights clearance is supplied by this metadata query.
