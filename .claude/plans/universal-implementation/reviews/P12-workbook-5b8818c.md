# P12 workbook source review

Date: 2026-09-22. **Independent source SPEC: FAIL. P1=0/P2=4/P3=0.
QUALITY: NOT STARTED.** Four checker defects are separate from the correctly
unverified native persisted-cache and rendered-workbook gates. No full XLSX,
A15.4.xlsx, P12 or parent acceptance is granted.

Reviewer project `f42bff7a-1c88-4784-80c9-60c37f683785`, runtime
`31c39265-13e5-4057-9e78-49bf658749a5`; original builder project
`09666ec2-ff03-4517-9169-8793149ea8cd`, runtime
`0a75211f-455c-4318-864f-bc8023ce9142`; coordinator
`88aecc43-40f9-41d4-8947-6c2fb0a55481`. This reviewer changed no product and
created no child reviewer, engine, cache publisher or P05 decision/corroboration.

## Exact scope

| Item | Identity |
|---|---|
| Standalone workbook release, read completely | `235d5bf1c94956ee7fe76fde3e962df6636f3aae`, P12 card |
| Product base | `b270475f6c45ac234b18133c0326542bace2fe50` |
| Five-file product | `5b8818c1223dc41dba5a0ff922dc2f0558d815a1`, sole parent above |
| Complete report / pinned review parent | `26bc070f36fee491be1bf9c316eb9a1cbc7f0cfd`, sole parent product |
| Builder report identity | `reports\P12-workbook.md`, 217 LF lines, 12,320 Git bytes; SHA-256 `e15a1e583e3a15d077c72e63d0d521283ab2c00ab0d53484a5af51872306509b` |
| Actual native workbook | `formula-probe.xlsx`, SHA-256 `c0cd1608350b78052f4f78f74074d615ade33cb93e102fd50afc71fc89d5c5db` |

The checkout was clean and detached at exact `26bc070`; the previous selected-PPT
report `5858268` and earlier review refs remain preserved. No moving builder tip
or later PDF work was read.

All five files were read fully, with the complete baseline delta:
`skills\generate-xlsx\SKILL.md`,
`skills\generate-xlsx\references\native-xlsx.md`,
`skills\generate-xlsx\scripts\check_xlsx.py`,
`tests\integration\document-workbook.py` and
`tests\integration\document-workbook.sh`.
Thirteen relevant accepted provider/fidelity/fixture dependencies are unchanged.
The original spec, map and format acceptance remain authoritative.

## Findings

All line references below are at exact `5b8818c`. `checker` abbreviates
`skills\generate-xlsx\scripts\check_xlsx.py`. The declared refusal contract is
`skills\generate-xlsx\SKILL.md:123-161`. Repros are synthetic OOXML packages,
not modified native workbooks, executable macros or engine observations.

| ID | Severity | Location | Finding | Confidence |
|---|---|---|---|---|
| W01 | P2 | checker:108-157, especially 115-136 | Package metadata and unconsumed relationship semantics bypass refusal | 10/10 |
| W02 | P2 | checker:156-157,180-208 | Invalid/ambiguous string and cell shapes produce integrity PASS | 10/10 |
| W03 | P2 | checker:69-75 | DTD/entity refusal only checks ASCII byte spelling | 10/10 |
| W04 | P2 | checker:281-283 | Explicit normal formula type is falsely classified as unsupported | 9/10 |

### W01 - Validate package metadata and relationships before cell acceptance

`[Content_Types].xml` is never parsed. Deleting it, making it malformed, or declaring
worksheet parts as chartsheets still returns **`status:pass`, CLI exit 0**.
The negative feature checks inspect filenames, not relationship/content types:
VBA-project, OLE-object and external-link declarations targeting
`xl/payload/item.bin` with inert marker data also pass. An unconsumed styles
relationship targeting `../../../escape.xml` passes because its target is never
validated. No target was followed, macro executed or network request made.

This is false persisted-integrity acceptance, not a claim that the checker itself
executes the forbidden content. `release_clearance:false` does not make a false
integrity result correct. The original positive fixture at
`tests\integration\document-workbook.py:53-64` omits content types entirely,
so the existing tests cannot detect that boundary.

**Fix:** validate the package content-type map and declared workbook/worksheet/
shared-string kinds before comparison; resolve and bound internal relationship
targets rather than only the consumed subset; reject forbidden mechanisms by
their relationship/content-type declarations irrespective of filenames. Refuse
malformed, missing or inconsistent metadata. Keep the reader bounded; no engine
or general spreadsheet implementation is needed. Add complete-package positive
fixtures and these seven refusal regressions.

### W02 - Validate string roots, payload multiplicity and types before decoding

Three distinct malformed inputs return **PASS / exit 0**: a shared-string part
whose root is `<wrongRoot>` instead of `<sst>`; a literal cell with two different
`<is>` payloads, where only the first is read; and an expected empty cell with
`t="not-a-cell-type"`, where the empty-value branch skips type validation.
Thus the checker can certify one chosen interpretation of ambiguous/invalid data.

**Fix:** require the proper shared-string root/namespace; enforce supported
single-cell payload combinations and at most one inline payload; validate the
declared cell type before accepting an absent value. Preserve legitimate blank,
shared-string, inline/rich-text and literal formula-looking values. Extend the
negative tests beyond the existing duplicate `<f>`/`<v>` cases.

### W03 - Reject declarations in every supported XML encoding

The same harmless internal entity (`safe_value` expands to the numeral `3`) is
rejected in UTF-8 but accepted in UTF-16LE and UTF-16BE. Both encoded variants
produce **PASS / exit 0** because the raw-byte substring guard misses the
declaration and `ET.fromstring` expands it. No external entity, amplification or
resource-exhaustion experiment was used.

**Fix:** enforce DTD/entity rejection with parser-level or encoding-aware
validation before constructing the tree. Cover all accepted encodings, retaining
ordinary UTF-16 documents if supported. The non-DTD UTF-16 control passes.
Do not describe the current byte scan as a complete declaration/bounds boundary.

### W04 - Recognize the default normal formula type

Adding only `t="normal"` to the valid formula element changes the result from
PASS to **`unsupported_formula`, CLI exit 3**, despite identical formula text,
numeric type, correct cache and expectations. `normal` is the ordinary formula
type, not shared/array/data-table semantics. Testing for any attribute makes
equivalent ordinary serializer output fail the promised basic integrity path.

**Fix:** classify formula type and attributes explicitly. Accept the supported
normal representation, including an explicit default, while retaining
unverified/refusal behavior for genuine shared, array, data-table or unknown
semantics. Add a paired omitted-type/explicit-normal regression; do not repair
this by calculating a value or weakening cache checks.

## Source preservation and original gates

The method itself adds useful native creation, dependency-edit/reopen, complete
Sources/Methods and honest inspection procedures. Existing `--from-pipeline`,
`--customer-share`, `--update-data`, estimate/capacity use cases and declared
library alternatives remain. Long reasoning is no longer excluded for being
non-tabular. Shared design stays gated, and explicit template/default selection
does not scan a personal directory or waive required policy.

| Control or original leaf | Exact result |
|---|---|
| Standalone method / source-retention procedure | **PASS** as reviewed procedure and retained source; not full route acceptance. |
| Read-only integrity checker source | **FAIL**, W01-W04. |
| Frozen workbook tests | **PASS**, 23/23; incomplete coverage of the above cases. |
| Independent discriminating SPEC cases | **FAIL**, 13 discrepancies across four roots; not an averaged score. |
| Actual native calculation | **PASS as supplied builder observation**, both formulas 37.5 -> 50 after quantity change; not re-executed by this reviewer. |
| Saved-copy editability | **PASS as supplied builder observation**, quantity 5 -> 62.5, restored to 4 -> 50. Restoration is semantic, not byte-exact. |
| Persisted-cache | **unverified**, actual native formula cells contain empty `<v/>`; independent checker CLI exits 3 with exactly two `cache_missing`. |
| Rendered-workbook | **unverified**, no exposed native renderer; application permission denied. No alternative route is authorized. |
| Source SPEC / eligible QUALITY | **FAIL / NOT STARTED**. Source defects must be repaired before quality; mandatory format gaps are not waived. |
| A15.4.xlsx and parents | **unverified/open**; no whole workbook, other-format or initiative completion. |

Independent readback of the saved OOXML confirms all ten complete paragraphs in
Methods!B4:B13, source citations, real capacity/claim cells and literal Inputs!B4
`=1+1` without a formula. Native error observations remain non-clearing:
division-by-zero, unsupported-name and circular typed errors, plus an empty
missing-sheet result. These observations do not establish persisted numeric caches.

The original P05 context selects A15.4.xlsx and still requires spec, quality,
workbook-tests, native-calculation, persisted-cache, native-reopen-editability
and rendered-workbook. All immutable QA fields and evidence hashes match.
Its actual recorded QA exit is 3; independent control evaluation/CLI also exits
3 for **persisted-cache and rendered-workbook**, regardless of advisory scores.
No old record was narrowed or rewritten.

## Checks and evidence

`W` is the read-only builder root:
`C:\Users\jokerman\.copilot\session-state\0a75211f-455c-4318-864f-bc8023ce9142\files\p12-workbook`.
`Q` is the reviewer root:
`C:\Users\jokerman\.copilot\session-state\31c39265-13e5-4057-9e78-49bf658749a5\files\r12`.

| Command | Actual outcome |
|---|---|
| `workbook-source-pin.ps1` | Exit 0: exact five-file product, original authority/report, unchanged dependencies and Git/CRLF comparison. |
| `review-run.ps1 -Label w-t01 -Mode workbook-tests` | Exit 0: **23/23**, zero failures/errors/skips; native checker CLI **exit 3**, exactly two empty caches. |
| `review-run.ps1 -Label w-c02 -Mode workbook-cases` | Exit **1**: 50 cases, 37 match their oracle; **12 invalid-input false PASS/CLI 0 plus one normal-formula false block/CLI 3**. Three further CLI boundary cases correctly exit 2. |
| `review-run.ps1 -Label w-e02 -Mode workbook-evidence` | Exit 0: all **135 workbook** and **135 prior first-unit** inventory files unchanged, ten Methods paragraphs exact, QA controls exit 3, Bash syntax and Python 3.9 grammar pass, two local links resolve. |

The 50-case matrix includes typed numbers/booleans/text, literal-error text,
stale/empty caches, promoted literals, hidden unselected formulas, errors, cell
and package aliases, namespaces, relationships, invalid expectations and actual
64 MiB input/expanded, 16 MiB part and 10,000-entry bounds. The exact 16 MiB part
control is accepted; over-limit cases refuse. The three CLI boundary cases are
path escape, duplicate JSON keys and over-limit input. None modifies its input.

All thirteen discrepant cases have retained `.xlsx`/expectation pairs under
`Q\w-c02\r` and real CLI stdout/stderr/exit records. `cases.json` names them,
records individual input hashes and maps results to the four findings above.
The initial `w-c01` is retained; `w-c02` adds explicit ordinary binary/shared-string
content types to the positive fixture. The same thirteen findings reproduce.
Neither run is relabelled green, and no product repair was made.

| Reusable evidence | SHA-256 |
|---|---|
| `Q\workbook-source-pin\source-pin.json` | `21930b48a466cb55e27527baea3b49ba9138a10625337ea5b644265a8f703d9b` |
| `Q\w-t01\results.json` | `80f99cad87ee4ee75ed68fa755dd6473919876d9fd7a17a7d8618c1b8c214be5` |
| `Q\w-c02\cases.json` | `61dfabaf3188e4898f5c0c17f0259f2d918b6006b877140f13a985d7fc61db5a` |
| `Q\w-e02\evidence.json` | `007961b61e47edd1d4bd204b70918d67ad2b20a354fb6540697be47b85c2dd09` |
| `Q\workbook-repro-manifest.json` | `cedd617ffa958e460bc0cde41184888c2f302faffdc415d7ba8d741c77778e38` |

Every product import/call ran after inspected source closure and per-process
synthetic HOME/USERPROFILE/AppData/temp/Lintel/derived paths/PATHEXT preflight.
Git ceiling/ancestor refusal was checked; source Git used separate configuration.
The unchanged test classes ran under this allowlist, not their environment-
replacing main. Logs were preopened and real exits/seals retained. The checker
was exercised only on owned copies or in-memory synthetic bytes. Original native
artifacts, contexts and profiles were neither edited nor relocated.

Runtime was Python 3.11.9; grammar checking is not a 3.9 runtime execution.
Numeric caches in the synthetic test packages are oracle fixtures only, not
published native caches or calculation evidence. No full suite, dependency install,
network request, UI/native/application action, COM, renderer/export workaround,
customer/private document, macro execution or policy/global-setting change occurred.

## Next bounded action

The original owner repairs W01-W04 in a new immutable candidate, retaining the
positive controls and all existing native failures. This same reviewer rechecks
source SPEC before any eligible QUALITY. No engine/cache publisher is requested.
Only separately authorized actual persistence/render observations could close
those remaining original format controls. P05 decision/corroboration persistence
remains denied; no manual or other-writer alternative was attempted. This report
completes the bounded source-review checkpoint, not the workbook initiative.
