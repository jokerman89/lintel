# P12 existing document pipeline input binding

Date: 2026-09-23. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`,
runtime `0a75211f-455c-4318-864f-bc8023ce9142`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Status: bounded source join frozen for SAME reviewer SPEC, then QUALITY.**
The existing document inputs now have an executable read-only admission boundary.
This is not a renderer, native artifact acceptance, P05 decision/corroboration,
new persisted interchange envelope or completion of A15/P12 parents.

## Authority and exact ancestry

Release **`98895a0cbce5430ace5960b1cf9289acdfa856b8`**, the full **Existing document
pipeline input binding** section of `packages\P12.md`, was read from Git.
Its condition is met by the complete eleven-file common/Word/PPT source review
`f2c1d09ba473c20a91adfb6f1e5c9967ed758008`, read in full and verified against
Git-byte SHA-256 `fe1cc9b776a131b67605e4cf5a0b7224cd0b5e20a3841534ffa0f21c870b46e8`.
That review accepts source at `32dac88`, not the remaining native gates.

Started clean at frozen PDF repair report
`124780e24d459162bb6cf024342465babba8eab2`, parent `1ba9f9b`.
The exact authorized dependency was merged, not cherry-picked or reconstructed:

| Identity | Exact revision |
|---|---|
| Accepted dependency | `2531a2a9046791b0bf77c2ee9bcfd6fba841f57b` |
| Dependency merge / new product base | `1b723ad9f00d5c1a8697e60752d644b0b44cf50f` |
| Merge parents, in order | `124780e24d459162bb6cf024342465babba8eab2`, `2531a2a9046791b0bf77c2ee9bcfd6fba841f57b` |
| Frozen product | **`d4e91881634867642567ba841bb7c092153986a1`** |
| Product's sole parent | `1b723ad9f00d5c1a8697e60752d644b0b44cf50f` |

This report is a separate report-only child. The handoff supplies its exact commit,
parent and Git-byte digest; no self-referential commit ID is invented here.

The merge retains accepted P08 `aa5cf0e`, its accepted P04 parser dependencies,
P09 `5c99612` and P11 `a1b3a45`/`e1cb9d2`, including their source closure.
The sole conflict was an append-only P11 report continuation. Its original 852
lines are an exact prefix of the accepted 1,254-line report; the latter was retained
byte-for-byte in Git, SHA-256
`4e51c9427e6443e822f33a0f0c2c5e1b374a7ebfa9529478c05fa7030dd5116f`.
The conflict/verification exits and both input reports remain in owned logs.
Every P12 source/report was unchanged by that dependency merge.

No unaccepted P10/final-P04 source was separately imported. The dependency's accepted
shared/discovery/generated changes retain their existing attribution. This product
does not edit those providers or regenerate anything.

## Owned product files

| Path | Change |
|---|---|
| `skills\generate\scripts\pipeline_inputs.py` | New read-only current-input loader and CLI |
| `skills\generate\SKILL.md` | Admission before existing document consumers, not circular finished-output QA |
| `skills\generate-word\SKILL.md` | Existing Word projection/input join; all standalone variants/defaults retained |
| `skills\generate-ppt\SKILL.md` | Existing PPT projection and full notes join; no presentation-content truncation |
| `skills\generate-qa\SKILL.md` | Reverify pipeline input identity while retaining actual final artifact obligations |
| `skills\generate-pdf\SKILL.md` | Admitted complete source feeds existing HTML/converter/print method |
| `skills\generate-xlsx\SKILL.md` | Admitted complete source feeds existing workbook/formula/cache method |
| `skills\generate-write\references\fidelity-and-evidence.md` | One public admission procedure, current interfaces and limitations |
| `tests\integration\document-pipeline-binding.py` | Thirty focused synthetic real-provider cases |
| `tests\integration\document-pipeline-binding.sh` | Existing-runner-style explicit-interpreter entry |

Exactly ten product paths changed. Frozen standalone implementations, native
references, old document/PDF/workbook tests and earlier P12 reports are untouched.
All familiar flags in the six changed skill bodies remain present versus the
product base. Three Word variants/template/default precedence, PPT count/duration
advice, language, full content and native inspection obligations are preserved.

## Actual input contract and behavior

`load_pipeline_inputs` and its CLI return complete original source text and design
objects plus current-input diagnostics. They do not write an output file or invent
a versioned renderer envelope. `executed:false` and `release_clearance:false` are
always explicit. The CLI has no `--out`; invalid input/option combinations refuse
without artifact publication.

P03 owns rooted bounded reads. P05 owns strict JSON, external v2 prepared context,
raw snapshot/current-work verification and immutable QA obligations. P07 owns the
unchanged v1 reference and actual live required-policy bridge. P08 supplies original
tasks/packages and its P05 binding; no second work/visibility parser is introduced.
The shared Markdown classifier identifies eligible source positions before the
format-owned section/field markers are read.

The actual canonical siblings are `brief.md`, `outline.md`, `content.md`,
`design-spec.json`, and `speaker-notes.md` for PPT. Paths as well as current bytes
must be selected. Existing brief -> outline -> content -> notes/design hash
meanings remain. Full Markdown, literal examples, CRLF bytes, tables, citations,
language, target formats, voice, section IDs and fields survive in returned inputs.
An identical file at a different path cannot replace a consumed sibling.

Document-only v1.0 projections use P11 compatibility validation, without fabricating
web renderability. Selected Word sections/PPT layouts must cover original sections,
reference present source fields and retain documented type/hook semantics. Word
semantic destinations are heading/body; PPT destinations are title/subtitle/body.
Duplicate or unknown destinations refuse. Multiple continuation layouts may refer
to one original section; full source is still retained, not reduced to mapped slots.
Native template-specific slot existence and layout are not established here.

Genuine mixed web/document input additionally runs the accepted P11 `load_design`,
including its actual sibling-content binding and live profile/design checks.
Legacy unresolved web input cannot masquerade as document-only admission. The web
renderer registry/schema was not extended. PDF/XLSX do not acquire invented layout
projections, converters, formula engines or native acceptance.

Explicit template/config overrides and referenced template/logo inputs must be
selected with current bytes. An absent projection template is not implicit
`--use-defaults` or a brand-policy waiver. The existing standalone selection and
actual format-template validation still apply.

Recognized package/leaf membership must agree with the external prepared work.
Original linked-handoff grouping uses the existing P09 admission pattern: an explicit
whole-file acceptance path, not inferred prose membership. The caller still verifies
that original assignment and actual prerequisite acceptance. Returned prerequisite
booleans remain **source-status-only**; an incomplete prerequisite is not relabelled
accepted merely because its input files can be inspected.

Selected upstream domain data is verified through P09 `verify_result` using its
OWN request, external final context and explicit live profile. Request, start,
result, artifacts and evidence must also be selected downstream. Document QA is
never grafted onto that original request. Upstream `review:not_evaluated` and
`release_clearance:false` remain intact; ordinary documents need no domain wrapper.

Input admission intentionally does not require a future artifact's QA. Declare
obligations before generation, then prepare a fresh final context after outputs/
edits and verify actual observations. The existing `qa-report.json` v1.0 remains
the presentation report. Missing mandatory rendering still blocks through P05.

## Checks actually run

`D` is the existing owned evidence root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
Outer commands use the existing `p12-pdf-run.ps1`; logs under `D\logs` include
preopened stdout/stderr, executable/argv/environment and actual exit JSON.

| Log label | Observed result |
|---|---|
| `pipeline-binding-tests-red` | Exit 1 before the new helper existed; missing product, not a missing dependency/install request |
| `pipeline-binding-tests-first` | Exit 0, 23 initial cases pass |
| `pipeline-binding-upstream-tests` | Exit 0, four selected upstream/path cases pass |
| `pipeline-binding-full-tests` | Exit 0, all 30 cases pass before freeze |
| `pipeline-binding-bash-entry` | Exit 0, real Bash entry and real CLI positive/unknown/duplicate-option refusal |
| `pipeline-binding-committed-bash-full` | **Exit 0 at d4e9188, 30/30**, zero failures/errors/skips through the actual Bash entry |
| `pipeline-binding-retained-first-unit` | Exit 1: 16 methods pass; six native-retention errors from the private runner's wrong artifact subdirectory |
| `pipeline-binding-retained-exact-artifacts` | Exit 0, **22/22 unchanged methods** against the verified original artifact paths/hashes |
| `pipeline-binding-committed-retained` | Exit 0 at d4e9188, **22/22**, zero failures/errors/skips and no remaining case directories |
| `pipeline-binding-artifact-preservation` | Exit 0, all 397 earlier artifact/QA inventory entries unchanged |
| `pipeline-binding-grammar-links`, `pipeline-binding-final-source-grammar` | Exit 0, local links and Python 3.9 grammar; not minimum-runtime execution |
| `pipeline-binding-shell-syntax`, `pipeline-binding-staged-check` | Exit 0; syntax and exact staged whitespace checks |
| `pipeline-binding-freeze-product` | Exit 0; ten product identities, thirty unchanged source/dependency files, preserved flags/artifacts and clean product freeze |

The 30-case suite covers document-only and genuine mixed input, complete long
source/notes, CRLF and optional fields, wrong-path/same-bytes, every hash link,
snapshot drift, section/slot/anchor/type/hook errors, continuations, package/parent/
approval identity, original linked authority, prerequisite status, profile/policy
drift, selected templates/config/logo, read bounds, root/Windows path spelling,
strict JSON/version refusal, and required later-QA nonclearance.

P09 tests use inert fixtures in its existing request/start/result shapes and real
P05/P07 producers plus the real P09 verifier. They are not new domain executions,
checkpoint publication or independent review. No `record`/decision/corroboration
writer runs. The mixed design's font/version/license evidence is explicitly
synthetic; no font, license, package or runtime compatibility observation is claimed.

The retained first-unit runner invokes the unchanged classes rather than their
original environment-resetting main, preserving complete synthetic PATH/PATHEXT,
HOME/USERPROFILE/AppData/temp/Lintel roots and Git ceilings. Its initial path mistake
selected the parent target, not `target\verified-artifacts`; correction selected the
exact DOCX/PPTX hashes before running. Both exits remain. No artifact or original
assertion was modified to pass.

The new Bash entry was formatted to LF per existing `.gitattributes`, then actually
executed. Git Bash path conversion names the same explicit installed Python and
script; it is not a different interpreter, installer or security workaround.
Observed runtime is Python 3.11.9; no other CLI or minimum-runtime matrix is claimed.

Each new case has allowlisted synthetic paths, preflight/source seals, real Git
ancestor refusal and exact initialized-root checks. Fixture Git configuration is
separate from source Git. No inherited token, personal profile or policy redirect
is used. These are process controls, not an OS sandbox. New synthetic case files
and logs remain under `D\pipeline-checks` as evidence; no server/daemon was started
and command processes completed. Retained test case cleanup reports an empty list.

## Frozen evidence and remaining gates

| Evidence relative to D | SHA-256 |
|---|---|
| `pipeline-freeze-product\freeze.json` | `d6fdf2c222f979f5016b600e863f78a3ad6261e38bc3ecc7e1a1deb30b90c40b` |
| `pipeline-checks\pipeline-tests-10stn5v_\result.json` | `e94cc6a13d59ce02e92453ec9d8db2cfef5140d8a9368fa4009814f75348829e` |
| `retained-drjolsun\result.json` | `d19ec450794af1d087b831c5a749be97739037f874eebb47bae5d9306f8abfe5` |

The freeze includes separate Git-byte and working-byte product seals, exact parent
checks, all retained argument names and thirty unchanged source/dependency hashes.
All **397** old inventory entries match: first unit 135, workbook 135, presentation
60 and PDF 67. Old native artifacts, QA, source refs and failure diagnostics were
not rewritten or reassigned to this product.

Builder self-review only: no outstanding owned-code P1/P2/P3 finding asserted.
Return this exact source/report to SAME
`31c39265-13e5-4057-9e78-49bf658749a5` for SPEC then eligible QUALITY.
No extra implementer or reviewer was created.

This advances existing shared-source binding, not full A15.1/A15.2/A15.3.shared or
native parents. Word pagination remains permission-blocked; workbook saved-cache/
layout gates remain; the original PDF still has sixteen unresolved page-3 origins
and unverified complete visual inspection. Converter/TLS and experimental reader
failures are retained. Visio still lacks an established actual writer/editor seam.
There was no Office/UI/COM, browser/server/print/raster, alternate reader, dependency/
network/install, P05 decision/corroboration, SHIP or remote operation.

Canonical nine-phase work and original task authority are unchanged; resume is
still a utility. MasterSession owns independent intake, integration and remote
delivery. No parent was auto-closed and no new backlog or shared schema was created.
