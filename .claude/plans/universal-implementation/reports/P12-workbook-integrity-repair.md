# P12 W01-W04 bounded workbook integrity repair

Date: 2026-09-22. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Status: source repair frozen for the SAME independent reviewer.** The exact
reviewer discrepancies are corrected in builder checks; independent source SPEC
recheck and eligible QUALITY remain pending. Full workbook cache/layout and all
parent acceptance remain blocked, not cleared by this repair.

## Authority, review and exact source

Read the complete W01-W04 card at
`764cf5328378a20140dc482fe7950af0a9c24a2a`, parent
`78631907f230c54cdb7af8fc2f98ca256ec8a474`.
Read all 211 lines of independent
`0c1a7115ef2a0c5e267f25ce04e9807eadf63936`,
`reviews/P12-workbook-5b8818c.md`, SHA-256
`cf1b45fcfada70ea826db6abf23a1e0e2cbaa9c3d5d64fb9be715eabe6a7847a`.
Its verdict is source SPEC FAIL, P1=0/P2=4/P3=0, QUALITY NOT STARTED.

Repair product:
`839e6df90193eaf7099e9f8d87fd2287d7bb195e`, sole parent
`9b4a8a1dc58d2f15e02376390169aa6ce30b5d0e`.
The current ancestry includes the preserved standalone PDF source/report and its
already accepted A16 dependency merge. None is re-reviewed, modified or mixed
into this repair. The delta from that parent is exactly:

- `skills/generate-xlsx/scripts/check_xlsx.py`
- `tests/integration/document-workbook.py`
- `skills/generate-xlsx/SKILL.md`
- `skills/generate-xlsx/references/native-xlsx.md`

This report is a separate report-only child; exact commit/hash is in the handoff.
No first-unit, F01, PDF, shared provider/schema, role, installer, registry,
generated output or master ledger changed.

## Root-cause corrections

| Finding | Corrected behavior |
|---|---|
| W01 | Required `[Content_Types].xml` is parsed and validated. Defaults/overrides are unambiguous and cover existing parts; workbook/worksheet/SST and supported style/theme relationship kinds match their content types. Every internal relationship, including unconsumed ones, has valid fields/owner and a bounded existing target. |
| W01 forbidden mechanisms | VBA/macro-enabled, OLE/embedded-package and external-link declarations are refused by their semantic content/relationship types, independently of names. Retained filename guards do not substitute for those checks. |
| W02 | SST root/namespace/entries, supported cell types and formula/value/inline payload multiplicity are checked before decoding or taking an empty-value branch. Duplicate or foreign payloads are not silently chosen/ignored. |
| W03 | The existing `ElementTree.XMLParser` uses its supported TreeBuilder declaration hook to reject DTDs before parsing their content. Encoding recognition precedes that hook, so UTF-16LE/BE cannot bypass ASCII spelling checks. No parser dependency/framework is added. |
| W04 | Omitted formula type and explicit `t="normal"` follow the same ordinary formula/cache/type checks. Shared/array/data-table/unknown types and uninterpreted attributes remain unverified; no value is recalculated. |

The package boundary rejects absent/malformed/inconsistent content declarations,
missing owners/targets, relation-part targets, traversal/directory/query/fragment
targets and malformed/duplicate relationship fields. Legitimate contained relative
and package-absolute targets remain usable. Uninterpreted opaque parts do not
become executable-safety certification; this remains a bounded transitional-OOXML
reader, not a full XML schema validator, antivirus or spreadsheet engine.

Blank cells, inline/shared/plain/rich strings, formula-looking literal text,
numeric lexical equivalents and typed booleans are preserved. The actual native
shared strings contain a legitimate empty `phoneticPr` formatting element; it is
accepted without treating it as extra text. Duplicate properties and unsupported
phonetic text annotations are not silently interpreted.

DTD refusal applies to XML parts this reader decodes: content types, relationship
parts, workbook, worksheets and shared strings. Ordinary non-DTD UTF-8/UTF-16
documents and declaration-looking literal/CDATA text remain readable. Only the
reviewed inert single entity whose value is `3` was used; no amplification,
external entity, resource-exhaustion or network experiment occurred.

The 64 MiB input/total-expanded, 16 MiB individual-part and 10,000-entry limits,
strict JSON expectations, owned CLI paths, cache/type distinctions and read-only
behavior remain. Complete positive fixtures now include actual content-type
metadata; the original 23 assertion methods were not weakened to accept incomplete
packages.

## Exact reviewer repros

`Q` is the supplied read-only reviewer root:

```text
C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12
```

`Q\workbook-repro-manifest.json` was verified at
`cedd617ffa958e460bc0cde41184888c2f302faffdc415d7ba8d741c77778e38`.
`Q\w-c02\cases.json` was verified at
`61dfabaf3188e4898f5c0c17f0259f2d918b6006b877140f13a985d7fc61db5a`.
Only exact manifest-verified `.xlsx`/expectation pairs were copied to private
fixture targets; reviewer originals were not modified or executed as helper code.

Fifteen saved CLI cases were replayed: all thirteen discrepancies, plus the
complete-package positive and UTF-8 declaration refusal controls. Before repair,
the exact thirteen discrepancies reproduced: twelve invalid-input false passes
and one explicit-normal false block. On the committed repair, **all fifteen
saved cases match their expected outcomes**, with zero discrepancies:

- Explicit normal formula: persisted-integrity pass, CLI 0.
- Complete transitional positive: persisted-integrity pass, CLI 0.
- Invalid cell/SST payloads, renamed forbidden mechanisms, missing/malformed/
  mismatched content types, escaping unused relationship and both UTF-16 DTD
  variants: explicit error, CLI 2.
- Existing UTF-8 DTD refusal: retained error, CLI 2.

The replay checks actual output status/exit and input bytes, not just a count.
Passing integrity still reports calculation/rendering/release clearance false.
The 50-method product suite adds parameterized complete-package positives and
negatives covering the other retained reviewer outcome classes; it is not
misrepresented as replay of unsaved original package bytes.

## Verification and evidence

`W` is this builder's existing workbook evidence root:

```text
C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-workbook
```

| Check | Actual outcome | Evidence |
|---|---|---|
| Original saved reviewer cases | exit 1, exact 13 discrepancies reproduced | `W\logs\w01-w04-reproduce-before.*`; `W\w01-w04\before\results.json` |
| Repaired exact saved cases | 15/15 expected outcomes, exit 0 | `W\logs\w01-w04-reproduce-fixed.*`; `W\w01-w04\after-fixed\results.json` |
| **Committed exact saved cases** | **15/15 expected outcomes, exit 0** | `W\logs\w01-w04-committed-review-cases.*`; `W\w01-w04\committed\results.json` |
| **Committed full workbook suite** | **50/50 methods, zero errors/skips, exit 0** | `W\logs\w01-w04-committed-tests.*` |
| Original test preservation | all 23 original method ASTs unchanged; positive fixture metadata corrected | `W\logs\w01-w04-preservation.json`, `w01-w04-final-preservation.*` |
| Frozen native workbook checker | actual CLI exit 3; exactly the same two `cache_missing` results as the old receipt | `W\logs\w01-w04-native-cache.*` |
| Prior format artifacts/evidence | **397 exact files unchanged** across Word/PPT, workbook, selected PPT packet and PDF inventories | `W\logs\w01-w04-preservation.json` |
| Frozen PDF/Word/PPT/shared code and earlier reports | source diff empty | `W\logs\w01-w04-frozen-source.*` |
| Grammar/links/whitespace | Python 3.9 grammar only, two direct links resolve, staged diff check exit 0 | preservation and staged-check logs |

The actual suite entry is `tests/integration/document-workbook.sh`, using explicit
`--fixture-root W\repair-checks` and `--native-root W\target`.
Runtime remains Python 3.11.9; no Python 3.9 execution is claimed.
Synthetic numeric caches belong only to bounded oracle test packages. None is
published to a native workbook or represented as engine execution.

All product calls use the recorded cleared synthetic HOME/USERPROFILE/AppData/
temp/Lintel/derived bindings, trusted source closure and explicit fixture roots.
Source Git uses separate checkout configuration. CLI logs open before execution;
real exits and source hashes remain. Temporary CLI input and test profile roots
are removed only inside their exact created fixtures. Replay inputs/results are
intentionally retained for independent recheck.

Private replay/verification sources are retained in the session files directory:
`p12-workbook-replay.py` and `p12-workbook-repair-verify.py`; the existing
`p12-workbook-run.ps1` supplies the allowlisted child environment.

## Retained intermediate failures

The initial expanded red suite and every failed development run remain recorded.
One first implementation typo indexed an XML Element as a mapping; positive
controls caught the resulting error instead of allowing an all-errors false
success. It was corrected to attribute access. Separately, an early test used an
encoding-declaration alias not supported by the existing parser; the test now
uses ordinary UTF-16 with explicit LE/BE BOMs, matching the actual reviewer input.
No new decoder or relaxed declaration guard was added.

After those corrections, the exact fifteen saved cases passed, but three native
preservation methods exposed the legitimate `phoneticPr` metadata. Its exact
shape was read from the pinned synthetic native workbook, the supported empty
formatting node was retained, and paired plain/rich/duplicate-property tests were
added. All original methods now pass. These failed runs are history, not
relabeled acceptance.

## Remaining gates and next actor

Native artifact SHA remains
`c0cd1608350b78052f4f78f74074d615ade33cb93e102fd50afc71fc89d5c5db`.
Its formula caches are still empty, and rendered-workbook evidence is still
unverified/permission-blocked. Original QA/context/evaluation files remain
byte-identical. No engine call, cache publisher, Office/UI/COM operation, renderer,
network/dependency action, structured P05 review decision or corroboration was
performed.

This is builder self-review and evidence, not independent SPEC/QUALITY.
Return the exact repair to SAME reviewer
`31c39265-13e5-4057-9e78-49bf658749a5` for source SPEC before eligible QUALITY.
PDF `5978def` / `9b4a8a1` and earlier format checkpoints remain frozen and separate.
No whole XLSX/A15/P12 completion, parent checkbox or remote delivery follows.

Preventive lesson for coordinator capture: valid fixtures must include protocol
metadata, not merely the data cells a reader happens to consume. Test equivalent
normal forms, inert encoded declarations and legitimate native metadata alongside
malformed cases. A no-release flag cannot excuse false integrity acceptance.
