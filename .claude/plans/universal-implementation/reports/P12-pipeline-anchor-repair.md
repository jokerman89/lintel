# P12 B01 eligible section-anchor correction

Date: 2026-09-23. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`,
runtime `0a75211f-455c-4318-864f-bc8023ce9142`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Status: narrow B01 correction frozen for SAME31 complete source SPEC, then
first eligible whole ten-path source QUALITY.** All seven recorded discrepancies
are corrected in actual API/CLI replay. Builder verification is not independent
acceptance; no native, source-unit integration or parent gate is closed.

## Authority and exact source

Read the complete **Pipeline B01 eligible anchor spans** release from Git
`12a40ccb031d460fb94660f23ff3e1baf49ba6f9`, without merging it.
Independent review `e85f70a269f5f7fb43a7bdbf088e139212409d89`, parent
`7c0ae2967650a269030da2e2916e21b5ff6babf2`, was read in full: 194 LF lines,
13,918 Git bytes, SHA-256
`5ae7efcb8173e3672a2ffbd5b0439f2852b7aae93a6b8a68a72a16a804e7e62d`.
Its verdict remains selected SOURCE SPEC FAIL, one P2 B01, whole QUALITY not started.
The other thirteen source-control PASS results retain that review/revision's
attribution; this correction does not reissue their independent verdicts.

Product **`fa5139cf2b2507828accbb810832457d2886bbe5`** has sole parent
**`7c0ae2967650a269030da2e2916e21b5ff6babf2`**, the unchanged report-only child of
original pipeline product `d4e91881634867642567ba841bb7c092153986a1`.
The accepted dependency merge `1b723ad` and its ancestry remain unchanged.
No merge, rebase, reset or dependency import occurred in this repair.

Exactly three product paths changed:

- `skills\generate\scripts\pipeline_inputs.py`: candidate anchor eligibility only.
- `tests\integration\document-pipeline-binding.py`: three added regression methods.
- `skills\generate-write\references\fidelity-and-evidence.md`: four directly
  related lines explaining eligible anchors and optional/required semantics.

This report is a separate report-only child; its exact commit, parent and Git-byte
digest are supplied in the handoff. Original pipeline report and all previous
failure/review artifacts are unchanged. Both commits carry the required trailer.

## Root cause and correction

The original routine checked classifier overlap for the heading prefix, but then
used raw `findall` across the entire heading for anchors. Literal examples could
therefore supply a required anchor or falsely count as a second/mismatched anchor.
The accepted classifier already identified the relevant protected regions.

The replacement uses `finditer` candidate offsets. Each candidate's local start/end
is translated by the existing line's `content_start` into the unchanged classified
source. Any overlap with an existing protected/opaque region excludes that candidate
before the unchanged identity/multiplicity comparison. No text is stripped,
rewritten or normalized; no new parser or shared-provider change was made.

Content still requires exactly one eligible matching anchor. Outline/notes may
omit anchors, but any eligible anchor still must be unique and match the section.
Real mismatches, duplicate real anchors and missing required anchors still refuse.
A real anchor beside inline-code/comment/HTML-attribute/escaped examples remains
valid while the full original examples remain in returned source.

The helper module AST outside `_sections` is identical. All original thirty test
method ASTs are identical. Existing package/work/profile, snapshot/hash, design,
upstream, template/config, CLI and non-clearing QA behavior remains under the
unchanged providers and retained tests.

## Exact reviewer-input replay

Reviewer root `Q`:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12\bi-a01`.
Verified `anchor-input-manifest.json` SHA-256
`ca69b4046a872d9ed204349fadc628e064c70fbf141fc129e3968d21e3aaa8a0`
and `anchor-results.json` SHA-256
`d90114efd2c1d4d728a7faee2798230d9906ed076c01e1a291ce1aac25e4b805`.
All 54 sealed files across nine cases match their recorded sizes/hashes.

Only the five exact brief/outline/content/notes/design files per case become
active inputs, copied into new owned targets. Reviewer contexts are read as data
for identity comparison only, never activated or relocated. Each replay creates
nine fresh owned repositories, P07 pins and external P05 contexts. Their profiles
and snapshot identities differ from the saved reviewer contexts; the nine owned
profile digests are distinct. Reviewer helper code is never executed.

| Exact saved case | Before CLI | Repaired CLI | API outcome after repair |
|---|---:|---:|---|
| `ordinary-anchor` | 0 | 0 | Accept |
| `inline-code-only` | 0 | 2 | Refuse |
| `comment-only` | 0 | 2 | Refuse |
| `html-attribute-only` | 0 | 2 | Refuse |
| `escaped-only` | 0 | 2 | Refuse |
| `ordinary-plus-inline-example` | 2 | 0 | Accept |
| `ordinary-plus-comment-example` | 2 | 0 | Accept |
| `ordinary-plus-attribute-example` | 2 | 0 | Accept |
| `real-mismatched-anchor` | 2 | 2 | Refuse |

All nine API/CLI pairs were executed before, after and on the committed repair.
Before reproduces the same seven discrepancies. After and committed replay both
match all nine requirements. Each admission leaves its target unchanged; accepted
results retain the exact complete source/design bytes with `executed:false` and
`release_clearance:false`. Failed calls do not publish partial success output.

## Checks and evidence

Builder root `D`:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-pdf`.
Outer commands use the existing allowlisted `p12-pdf-run.ps1`; each label below
has preopened stdout/stderr, argv/environment and actual exit JSON under `D\logs`.

| Log label | Actual outcome |
|---|---|
| `pipeline-b01-intake-digests` | Exit 0; exact review, manifest and original discrepancy record verified |
| `pipeline-b01-replay-before` | Exit 1; nine API/CLI cases, the same seven discrepancies, nine fresh owned pins |
| `pipeline-b01-regressions-red` | Exit 1; three new methods expose B01, including optional-anchor and original-offset contrasts |
| `pipeline-b01-regressions-green` | Exit 0; all three new methods pass |
| `pipeline-b01-replay-after` | Exit 0; all nine saved API/CLI requirements match |
| `pipeline-b01-full-bash-tests` | Exit 0; **33/33**, zero failures/errors/skips through the unchanged actual Bash entry |
| `pipeline-b01-committed-bash-tests` | Exit 0 at fa5139c; **33/33**, zero failures/errors/skips |
| `pipeline-b01-replay-committed` | Exit 0 at fa5139c; all nine saved API/CLI pairs match with fresh owned contexts |
| `pipeline-b01-preservation-working`, `pipeline-b01-preservation-committed` | Exit 0 each; original 30 methods, 37 other source/dependency files and all 397 old artifact/QA entries preserved |
| `pipeline-b01-whitespace`, `pipeline-b01-staged-check` | Exit 0; exact narrow diff and whitespace checks |
| `pipeline-b01-product-clean`, `pipeline-b01-product-range` | Exit 0; clean product checkpoint and exact three-path parent delta |

The new regression methods exercise nine full binding API/CLI pairs; optional
outline/notes anchors with both absent/literal examples and real mismatch/duplicates;
and actual classifier/source-reader offsets with non-ASCII text, supplementary
Unicode, three-space indentation and LF/CRLF/lone-CR separators. The optional
case also exercises the full binding API with both real outline and notes files.
No new source parser, text-stripping routine or normalization surrogate is used.

The complete retained thirty-method suite still exercises document-only/mixed
input, original work/profile/source identity, upstream own-context verification,
template/config selection and actual missing mandatory QA nonclearance.
Its passing count is source-test evidence, not rendered artifact acceptance.
The previous standalone 22-method/native-retention results retain their original
attribution; those were not rerun or relabelled as new native observations here.

Every actual import/helper/API/CLI call uses recorded synthetic HOME/USERPROFILE,
AppData/temp/Lintel/source/target paths, explicit executables and Git ceilings.
Fixture setup verifies actual ancestor refusal and exact initialized root.
Source Git remains separate from fixture configuration; inherited credentials
and policy redirects are absent. These are process controls, not an OS sandbox.
Owned fixture sources/contexts/logs remain as evidence. No server/daemon was
started; synchronous child commands completed. No broad cleanup was performed.

| Evidence relative to D | SHA-256 |
|---|---|
| `pipeline-b01\before\results.json` | `1c57f44ac3ba068b6d336666e314ebcaac104e6f34c60d96c2e98c9b04871299` |
| `pipeline-b01\after\results.json` | `1467266860c95a09987f0d5d545374783dd1bd844b6553aacf6651b991d958cf` |
| `pipeline-b01\committed\results.json` | `578c08d9724f0cd1415eb97d33e37881968ad561cd8e753e2eecd99b25700d51` |
| `pipeline-b01\verify-committed\results.json` | `1e269d0ba7c6399d4061bee86b5b10b5d2c4ec177cf6c1da16d1bf4255d7a183` |
| `pipeline-checks\pipeline-tests-f1aa_bbz\result.json` | `435d29064443d5e6c0a32344ccf3c4b7c1d666ab1d2b7e99b83b71bfb2fe6f88` |

Preservation results retain raw working-source hashes and prior Git-byte seals.
Only checkout/Git source comparison accounts for CRLF versus LF; actual source
input/artifact identities are raw bytes and are never normalized. Python 3.9
grammar and local reference links pass; runtime is the existing Python 3.11.9.
No other host/minimum-runtime or full-repository suite claim is made.

## Remaining acceptance

Builder self-review only: no remaining owned B01 finding asserted, P1/P2/P3
counts zero for this correction. SAME `31c39265-13e5-4057-9e78-49bf658749a5`
must recheck complete selected SPEC before starting the first eligible whole
ten-path source QUALITY. The original failed review and all red evidence remain.

All **397** prior artifact/QA files match: first unit 135, workbook 135,
presentation 60 and PDF 67. Word pagination permission, XLSX persisted-cache/
layout, the original PDF's sixteen page-3 origins and complete visual inspection,
converter/TLS limitations and Visio writer/editor seam are unchanged. No old
artifact, QA receipt or native source identity was rewritten.

No Office/UI/COM, browser/server/print/raster, alternative reader, network/install,
shared provider/schema, policy/installer or denied-route action occurred. No
P05 decision/corroboration writer or substitute checkpoint was used. No remote
operation, source-unit integration, SHIP or parent closure follows from this
freeze. MasterSession alone owns independent intake, integration and delivery.
