# P12 standalone workbook checkpoint

Date: 2026-09-22. Original builder `09666ec2-ff03-4517-9169-8793149ea8cd`.
Coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

**Source candidate frozen; workbook acceptance remains BLOCKED on persisted
caches and rendered inspection.** Native calculation and API editability are
observed, not guessed. No A15 parent, shared pipeline or other format is closed.

## Authority and product

Read exact release `235d5bf1c94956ee7fe76fde3e962df6636f3aae` and its complete
`packages/P12.md`, including "Standalone workbook second unit".
No P08/P11 WIP or replacement schema is needed or imported.

Product `5b8818c1223dc41dba5a0ff922dc2f0558d815a1`, sole parent
`b270475f6c45ac234b18133c0326542bace2fe50` (the separate F01 report).
This product contains only:

- `skills/generate-xlsx/SKILL.md`
- `skills/generate-xlsx/references/native-xlsx.md`
- `skills/generate-xlsx/scripts/check_xlsx.py`
- `tests/integration/document-workbook.py`
- `tests/integration/document-workbook.sh`

This report is a separate report-only child; exact identity/hash is in the handoff.
The earlier Word/PPT product/report and F01 commits are preserved, not amended.
No agent, shared API/schema, installer, registry, generated output or common ledger
was changed. The changed XLSX description needs coordinator catalog regeneration.

## Implemented method and retained value

Standalone brief/source-backed workbook creation now has a concrete native route,
capability preflight, Inputs/Calculation/Summary/Sources/Methods organization,
formula-versus-literal distinction and exact source/provenance retention.
Existing `--from-pipeline`, `--customer-share` and `--update-data` entry paths remain;
shared design binding is still separately gated. Explicit output/template/default
selection has no personal directory scan or invented neutral policy.

The format-local checker is read-only. It follows workbook/worksheet relationships,
reads hidden sheets and actual cells, preserves formula text, compares typed
persisted caches against an explicit expectation oracle and checks retained source.
It detects unselected formulas, stale values, changed/lost formulas, literal-text
promotion, cached errors, missing cells/source, duplicate/aliased parts and missing
caches. It refuses macros/external relationships/embeddings and unsupported
input forms. Shared/array/table formulas and ambiguous empty formula caches remain
unverified. It is a bounded transitional-OOXML reader, not a full spreadsheet
implementation, evaluator, renderer or cache publisher.

The CLI reuses unchanged accepted P03 owned-path/read primitives and P05 strict JSON
loading. All imports come from the trusted source closure; no shared helper changed.
Exit 0 means persisted integrity only; exit 3 means failed/unverified integrity;
exit 2 means invalid/unreadable/unsupported input. Each result explicitly declines
calculation-execution, rendered-layout and release-clearance claims.

## Exact owned evidence and artifacts

`W` means:

```text
C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-workbook
```

Stable positive native workbook:
`W\target\formula-probe.xlsx`, 13,014 bytes, SHA-256
`c0cd1608350b78052f4f78f74074d615ade33cb93e102fd50afc71fc89d5c5db`.
Size is inventory, not acceptance. `workbook-brief.md`, unchanged copies under
`technical-source`, explicit `expectations.json`, `profile-reference.json`,
native observation records and all intermediate failure snapshots are retained.
`W\logs\artifact-inventory.stdout.log` contains their exact byte hashes.

Actual native provider: `connection:1`; engine/build version unavailable.
Discovery: `functions.list_canvas_capabilities(excel)`. Author/open:
`functions.open_canvas`. Write/read/package operations:
`functions.invoke_canvas_action`.
This is the native canvas API, not Excel desktop, an OS sandbox or the shell's
synthetic process environment.

## Actual native execution

Instance `p12-workbook-native` created a new owned workbook. Separate `add_sheet`
calls created Inputs, Calculation, Summary, Sources and Methods; the initial
Sheet1 is retained as an index because no rename/delete-sheet operation was assumed.
`batch`, `set_cells`, `set_formula` and `format_range` authored actual editable
cells and formula expressions.

| State | Actual typed calculation observations | Saved artifact SHA-256 |
|---|---|---|
| Inputs quantity 3, unit value 12.5 | Calculation `=Inputs!B2*Inputs!B3` and Summary `=SUM(Calculation!B2)` both return number 37.5 | `d34618843c4a12b32030cc73811ba9abf522ca0ed921d635caf8427dc48a6e39` |
| Only quantity changed to 4 | Both actual `get_range` results become number 50, formulas unchanged | `f726fe2de549c414b9ca003728aff38f8f0a9c6dc80910d438269101c9c20e87` |
| Full source-retention content added | Same inputs/formulas, long source preserved | `c0cd1608350b78052f4f78f74074d615ade33cb93e102fd50afc71fc89d5c5db` |

Inputs!B4 was deliberately authored and read back as **literal text** `=1+1`,
with no formula. Neither expected 37.5 nor 50 was written into a formula/cache.

The complete first-unit ten long paragraphs are actual Methods cells B4:B13,
with section IDs, references and material limitation. Native `get_range` returned
them in full. Sources contains the exact claim ledger, capacity cells/units and
both citations; tests independently read those saved cells. Explanations remain
full source, not a slide-sized or table-only extract. Local source paths resolve
from the retained technical-source bundle.

### Persistence failure

After both correct live calculation states, actual `read_package_entry` of
`xl/worksheets/sheet3.xml` and `sheet4.xml` shows:

```xml
<c r="B2" t="str"><f>Inputs!B2*Inputs!B3</f><v/></c>
```

The Summary formula likewise has empty `<v/>`. Independent raw ZIP inspection
confirms absence of numeric persisted caches. Formula text is intact; native
dependency evaluation is real; **native persistence did not establish the cache
requirement**. Flags, successful file creation or a live `get_range` cannot clear it.
Original states remain at `observations\quantity-3.xlsx` and `quantity-4.xlsx`
with raw observation JSON.

A proposed two-formula cache publisher was considered read-only, then explicitly
declined by the coordinator. None was implemented. No Python arithmetic/cache
insertion, guessed recalculation API or alternate application was used.

### Saved-copy editing

A hash-identical saved copy opened as `p12-workbook-reopened` at
`reopen\retained-content.xlsx`. Editing quantity to 5 and Sources!A1 to a marked
title produced actual readbacks 62.5 in both formulas and the exact title marker,
at hash `b4536ed4aa247a948188a6fcc09662c90e90ee33dc4fec03e2a3fbe77e624671`.
Restoring quantity 4/title returned live 50. The restored copy's archive hash is
`c745608731bf4fe33541de85ab3e27cd33029e44c09a9b5598a756ec83167e85`;
semantic restoration is not claimed byte-exact. Original c0cd specimen is untouched.

### Native negative formulas and layout boundary

A separate copy, `negative-formulas.xlsx`, instance `p12-workbook-errors`, contains
Errors!A1:A4. Actual native results: `=1/0` -> `#DIV/0!`,
`=P12_UNSUPPORTED(1)` -> `#NAME?`, `=MissingSheet!A1` -> **empty**, and `=A4`
-> `#CIRCULAR!`. All remain non-clearing. Saved error caches are also empty.
Hash: `8be3b1c750770577eb4f252d8e97525f2cf28e6e89dd2409824ab49a66484000`.

The discovered API has no explicit recalculate, cache setter, save/export or grid
renderer action. `inspect_document` reports `richRendererSelected:false`.
Default narrow row/column dimensions and wrapText are **not** rendered legibility.
The separate Excel application path was rejected in the coordinator session;
it is permission-blocked, not missing software. This worker made no Office app,
COM, shell-export, alternate-launch or denied UI request.

`observations\native-actions.json` is an explicitly labelled builder transcription
of actual actions/results, not an automatic raw log or independent verdict.
Raw package snapshots and cache observations are separately retained.

## P05/P07 evidence and actual refusal

Fresh workbook-only P07 pin: `_default` 1.0.0, context
`p12-standalone-workbook`, generation 1, digest
`sha256:ead10c4cce8d33cdacee767d39768e8ed92c8d59c3717d5a17ca7af444b0662f`.
This is a new target/home context, not a transplanted Word/PPT reference.
Live verification precedes evidence consumption.

The synthetic Git target uses copies of the original selected work map/spec/plan/
prompt and the exact released workbook card. The actual map validator passed.
P05 prepared A15.4.xlsx with immutable obligations for tests, actual calculation,
persisted cache, saved-copy editability and rendered inspection; spec/quality
remain separately required. It binds the native XLSX, full source, expectations
and current profile. Acceptance and artifact identity are not inferred from counts.

Actual checker CLI on the native file: **exit 3**, exactly two `cache_missing`
observations (Calculation!B2 and Summary!B2), with all 29 selected cells and
the full required source retained. Actual P05 QA: **exit 3**, mandatory
`persisted-cache` and `rendered-workbook` unverified. `qa-report.json` is false.
Context, request, raw command outputs, QA and evaluated blockers are under
`W\target\observations\p05-binding`. No review decision/corroboration was invented.

## Verification and boundaries

| Check | Actual result | Evidence under `W\logs` |
|---|---|---|
| Before checker implementation | exit 1 at explicit missing trusted checker; no install | `checker-red.*` |
| First workbook suite | 21/21, zero skips/errors, exit 0 | `checker-first-run.*` |
| Bash entry including CLI refusal/coercion cases | 23/23, zero skips/errors, exit 0 | `workbook-bash-tests.*` |
| **Committed product `5b8818c`** | **23/23, zero skips/errors, exit 0** | `committed-tests.*` |
| Python 3.9 grammar/local links | pass; actual runtime Python 3.11.9, not a 3.9 execution claim | `syntax-links.*` |
| Source whitespace | exit 0 | `diff-check.*` |
| Frozen first-unit/F01 source diff | empty | `frozen-source-diff.*` |
| All 135 earlier artifacts/evidence and original report | exact hashes unchanged | `preservation-check.*` |
| Native integrity and bound QA | checker exit 3 and QA exit 3, not successful acceptance | `native-bound-qa.*` and nested P05 logs |

The 23 methods cover exact formula/type/cache distinction, stale or absent caches,
constant substitution, hidden/unselected formulas, errors, unsupported forms,
source loss, external/macro refusal, duplicate/aliased cells, invalid expectations,
CLI read-only/refusal behavior, real P05/P07 mandatory blockers and native saved
source/table retention. Handcrafted numeric caches exist **only in in-memory
unit-test packages**, never in the native output and never as engine evidence.

The workbook-specific runner clears the process environment and binds explicit
HOME/USERPROFILE/AppData/temp/Lintel/source/target/PATHEXT and derived roots.
Before product calls, accepted source closure bytes were verified against the
starting accepted commit. Fixture Git actually refused ancestor discovery and
verified its initialized root; source Git checks use separate configuration.
Every shell/helper command preopens logs and preserves actual exits. Test-created
profile directories are removed within their exact owned roots; native artifacts,
failure snapshots and evidence logs are intentionally retained. No broad cleanup.

No dependency installation, app launch, customer/private document, macro, external
workbook, remote upload, credential use or policy/global setting change occurred.
No runtime/OS isolation is claimed for native host operations.

## Next gate

Builder self-review only; independent SPEC and QUALITY remain with the SAME
reviewer `31c39265-13e5-4057-9e78-49bf658749a5`. The current source is a useful
standalone method with real native calculation/editability and honest remaining
cache/render gates, not a fully accepted XLSX route.
Only separately authorized actual engine persistence/render observations can
advance those controls; current denied application routes stay closed.
PPT evidence staging, Word page permission, PDF/Visio implementation and shared
pipeline/theme binding remain separate. No parent task is auto-closed.
