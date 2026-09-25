---
name: generate-xlsx
layer: foundation
description: Produce an editable, source-backed workbook through available native tools, verifying formulas, actual recalculation, persisted caches and honest inspection limits.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# /generate-xlsx

Create an editable workbook for estimates, capacity models, comparison tables,
schedules or trackers. Standalone `--brief` needs no shared design-spec or domain
envelope. Reusable format methods belong here; actual customer data does not.
Source facts, formulas, actual engine results, saved caches and rendered layout
are different evidence layers.

## Inputs and retained entry paths

- `--brief <path|inline>`: complete source, including assumptions and evidence;
  retain inline text before hashing.
- `--from-pipeline <run-dir>`: use
  [existing input admission](../generate-write/references/fidelity-and-evidence.md#existing-pipeline-input-admission)
  with `--format xlsx`, external input context, original package/leaves and live
  profile. Feed the full admitted content into the existing workbook procedure,
  preserving Inputs/Calculation/Summary/Sources and formula/cache requirements.
  Do not invent a `per_format.xlsx` layout or call source admission recalculation.
  Shared artifact acceptance remains distinct from this input-only join.
- `--out <path>`: explicit new owned `.xlsx` path, default `<brief-stem>.xlsx`
  in the selected working directory. Refuse unapproved replacement.
- `--update-data <source>`: retain the existing workbook/source identity, apply
  only the selected update, then recollect calculation/cache/reopen evidence.
  A remembered total or an old receipt cannot cover changed input.
- `--template <path|name>`: explicit template or a name within the verified
  configured brand directory. No personal template scan.
- `--use-defaults`: explicit neutral blank/template route when policy allows.
- `--customer-share`: apply the current profile's actual customer-facing
  requirements to labels, notes, disclosures and the complete source.

## Capability and source preflight

Discover actual tool schemas and permissions before invoking them. Prefer a
native workbook writer/read API when available. The
[native workbook procedure](references/native-xlsx.md) describes an observed
Copilot canvas route; it is not a guarantee for every client or formula.

The existing declared library alternative is openpyxl, or an explicitly selected
available Node workbook library. A library's ability to write a formula is not
proof it calculates it. Do not install automatically/globally, start another
application, use macros, fetch external workbooks or bypass a denied permission.
Missing writer/calculation/persistence/render capability leaves the dependent
action blocked; independent source preparation can continue.

Use the accepted [P05/P07 fidelity procedure](../generate-write/references/fidelity-and-evidence.md):
explicit source/output roots, verified profile reference, required-policy bridge,
original work/leaf identity where supplied, and immutable QA obligations before
observations. Keep formula/source/config changes content-bound. Neutral mode does
not invent currency, retention, brand colors, compliance gates or a voice score.

## Workbook composition

1. **Read the entire source.** Inventory tables, units, input dates/versions,
   formulas, claims, citations, reasoning and material limitations. Distinguish
   measured inputs, assumptions, unknowns and calculated projections. Do not
   replace unknown input with zero or infer actual cost/utilization from a manifest.
2. **Separate responsibilities.** Keep Inputs, Calculation, Summary and
   Sources/Methods content, using separate Sources and Methods sheets when useful.
   One sheet per substantive table remains a useful organization, not a quota.
   Preserve long-form explanations in text cells or a delivered linked source;
   source references and limitations must stay discoverable from the workbook.
3. **Use editable cell types.** Quantities and rates are numeric with units;
   dates/currency/rounding follow the actual source. Treat literal formula-looking
   text such as `=1+1` as text unless it is explicitly a formula. Never promote
   imported prose to a formula. Preserve complete paragraphs, cell labels,
   provenance and source-backed table values.
4. **Use formulas for derived results.** Retain SUM/PRODUCT/AVERAGE and relevant
   cross-sheet dependencies rather than replacing them with hardcoded totals.
   Explicitly review references/ranges, rounding and missing-input behavior.
   Conditional formats, validation and charts are useful when available and
   requested; color alone cannot convey a result or substitute for a limitation.
5. **Use accepted specialist methods read-only.** CostAnalyzer supplies cost
   scope/date/currency/commitment/uncertainty discipline; CapacityPlanner supplies
   load/measurement/bottleneck reasoning. Use actual available delegation only
   when needed, otherwise label the builder's own pass honestly. No agent body
   or shared domain-result interface is changed by this format procedure.

## Recalculation, persistence and actual inspection

Collect observations from the **same exact workbook revision**. Read formula
text and typed values from the actual provider, change one controlled input,
and verify dependent results change. Independently inspect persisted OOXML
formula and cached value/type, then reopen a saved copy through the permitted
application/API. Edit/read back a cell and verify retention. Preserve the original
artifact and clearly identify the new version after any edit.

The release's small synthetic case is quantity 3 times 12.5, expected 37.5,
then quantity 4, expected 50, with a dependent cross-sheet SUM. These expected
values are an independent test oracle, **never constants written to formula
cells or caches as a substitute for actual engine behavior**. A later input
change or edit requires fresh observations.

Native observations on 2026-09-22 showed correct live results and dependency
recalculation but empty persisted `<v/>` formula caches. That is a real useful
native calculation path with a **blocked persistence gate**, not total XLSX
support. Writing Python-computed or copied values into the cache is not an
authorized workaround. No unlisted recalculate/save/export operation is assumed.

Check live errors and unsupported behavior even when file creation succeeded:
division by zero, unsupported function, circular dependency, missing sheet/range,
empty/unknown result and stale cached value cannot pass. Missing-sheet references
were observed to return an empty value in this host, so empty is not zero or proof
that the formula succeeded.

Inspect the rendered grid/print pages and any charts through an actual available,
permitted renderer: clipping, `####` displays, long-text wrapping, row/column
dimensions, table headers, units, color/contrast and print-page boundaries.
Model dimensions or a `wrapText` flag do not prove legibility. The observed canvas
has no explicit grid-render/export action; missing rendering stays unverified.
Never start Excel/LibreOffice or another Office application without its own
authority and permission.

## Read-only formula/cache integrity check

`scripts/check_xlsx.py` consumes only the exact selected local workbook and an
explicit expectation file. It reads all worksheets, including hidden sheets,
retains the literal/formula distinction and checks cached types/values and exact
source text. It does not evaluate formulas, publish caches, modify the workbook,
render anything or establish release clearance.

```text
python <trusted-source>\skills\generate-xlsx\scripts\check_xlsx.py \
  --root <owned-artifact-root> --workbook output.xlsx --expect expectations.json
```

Use the host's native path/line-continuation syntax. The paths after `--workbook`
and `--expect` are relative to the explicit owned root. A minimal expectation:

```json
{
  "cells": [
    {"sheet": "Inputs", "cell": "B2", "formula": null, "type": "number", "value": 4},
    {"sheet": "Calculation", "cell": "B2", "formula": "=Inputs!B2*Inputs!B3", "type": "number", "value": 50},
    {"sheet": "Summary", "cell": "B2", "formula": "=SUM(Calculation!B2)", "type": "number", "value": 50}
  ],
  "required_text": ["<exact source-backed limitation>"]
}
```

Include every formula and all relevant input/source cells, not just a favorable
sample. The numbers above are expectation data, not executed results. Missing
cache is `unverified`; stale values, changed formulas/types, unselected formulas
and lost source text fail. Omitted formula type and explicit `t="normal"` are
equivalent ordinary formulas. Shared/array/data-table types, unknown types or
other uninterpreted formula attributes remain unverified. An empty-string
formula cache is still ambiguous, not guessed to be a computed empty result.

Before decoding cells, the checker requires a valid `[Content_Types].xml`,
unambiguous declarations for every part, and matching declared kinds for the
workbook, worksheets, shared strings and supported style/theme relationships.
Every internal relationship is checked, including unconsumed ones: its owning
part must exist, its target must resolve inside the package to a present part,
and its declared kind must be consistent. Missing/malformed metadata, duplicate
declarations and traversal/directory/query/fragment targets are refused. This is
a bounded canonical package-URI reader; percent-escaped targets require another
explicitly supported reader, not silent URI reinterpretation.

Forbidden VBA/macro-enabled, OLE/embedded-package and external-link mechanisms
are rejected by content-type/relationship declarations as well as the retained
filename guards. Renaming an inert or executable payload cannot erase those
declarations. This checks declared package integrity; it is not a general malware
scanner, full OOXML schema validator or permission to open untrusted content.

Shared strings need the actual `sst` namespace/root and valid string entries.
Cell types and single formula/value/inline payload combinations are validated
before any missing-value branch. Legitimate blank cells, shared/inline strings,
rich-text runs and literal formula-looking text are retained. The native
`phoneticPr` formatting metadata is accepted without inventing phonetic text;
unsupported phonetic annotations remain explicit errors.

DTD/entity declarations in the XML parts decoded by this reader are refused
through the existing parser's declaration hook after encoding recognition,
including UTF-8 and UTF-16LE/BE. Ordinary
non-DTD UTF-16 and declaration-looking literal text remain readable. No external
entity resolution, custom XML framework or calculation engine is introduced.
The unchanged 64 MiB input/total-expanded, 16 MiB part and 10,000-entry bounds
refuse oversized input without truncation.

Exit 0 means only the declared persisted-integrity checks passed; exit 3 means
failed/unverified integrity and exit 2 is invalid/unreadable/unsupported input.
Record this result as P05 evidence alongside native calculation, edit/reopen and
render observations. Do not replace P05's control schema with this local diagnostic.

## Status and handoff

- **DONE:** source retention, real calculation, required persisted caches,
  editable reopen and all requested rendered/configured controls verified.
- **DONE_WITH_CONCERNS:** required observations complete, only advisory concerns.
- **BLOCKED:** a required observation fails, errors or remains unverified.
  Retain the editable/source artifacts with exact remaining gates.
- **NEEDS_CONTEXT:** missing source, output authority or unresolved data semantics.

Report exact paths/hashes, original work/profile references, provider/tool/actions,
formula/input changes, actual typed live results, persisted-cache inspection,
reopen/editability, rendered coverage and unresolved boundaries separately.
Keep qa-report.json and original P05 receipts; never replace historical failures
with a later passing-looking summary. PDF/Visio and shared theme/pipeline binding
remain their own releases, not prerequisites invented for this standalone route.
