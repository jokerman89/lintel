# Native workbook procedure

Use `functions.list_canvas_capabilities` for `excel` on the current host before
calling operations. The observed provider is `connection:1`; its application/
engine build version was not supplied. These are observed bindings, not a
universal API or a promise that every formula is implemented.

## Author through actual operations

Open a new explicit owned `.xlsx` with `functions.open_canvas`, `canvasId: "excel"`,
a caller-chosen instance and nested `artifact` (`scope`, `path`, spreadsheet media
type), `initialize: true`. Omit overwrite. Then inspect `get_model`; the observed
blank file starts with `Sheet1`. Do not guess a rename/delete-sheet operation.
Use the existing sheet as an index if no such operation is available.

`add_sheet` accepts `sheet`. The observed route created Inputs, Calculation,
Summary, Sources and Methods. Native sheet names cannot contain `/`; the phrase
Sources/Methods describes their responsibilities, not a literal worksheet name.

Use `batch` for related edits, checking saved results after the batch. Actual
`set_cells` inputs have `edits`, each containing `sheet`, 1-based `row`/`column`
and a tagged `value`. Text remains text:

```json
{
  "edits": [
    {"sheet": "Inputs", "row": 2, "column": 2, "value": {"type": "number", "number": 3}},
    {"sheet": "Inputs", "row": 3, "column": 2, "value": {"type": "number", "number": 12.5}},
    {"sheet": "Inputs", "row": 4, "column": 2, "value": {"type": "text", "text": "=1+1"}}
  ]
}
```

`set_formula` accepts `sheet`, `row`, `column`, `formula`. The controlled probe
used `=Inputs!B2*Inputs!B3` in Calculation!B2 and
`=SUM(Calculation!B2)` in Summary!B2. `get_range` with `sheet` and `range: "B2"`
returns an `artifactVersion`, exact formula and typed live value.

Do not set an expected numeric result in a formula cell. `format_range` supports
number format, font, alignment and wrapText. That schema is not a column-width,
row-height or rendered-layout API. Structured edit `expectedVersion` is advisory,
not a concurrency lock; reinspect before edits and stop on unapproved user changes.

## Observed calculation versus saved cache

On the actual synthetic native workbook, both formula cells read 37.5 at quantity
3. Changing only Inputs!B2 to 4 made both read 50. A reopened saved copy edited
to quantity 5 read 62.5, then returned to 50 when restored to 4. Formula text and
literal `=1+1` were retained. These are actual calculation observations for the
named simple formulas, not tests of the whole Excel function library.

But `read_package_entry` for both worksheet parts returned `<f>...</f><v/>`
with `t="str"`: the live numeric engine value was **not persisted as a cache**.
Independent ZIP/XML reading confirmed the empty values. A `get_range` result and
the package's saved `<v>` are not interchangeable. No explicit recalculate,
cache-write, save/export or grid-render operation was exposed. Do not guess one,
write computed cache constants or start an alternative application.

An error probe on a separate owned copy returned `#DIV/0!` for `=1/0`, `#NAME?`
for an unsupported function, `#CIRCULAR!` for self-reference and **empty** for a
missing-sheet reference. Each is a non-clearing result. The saved error-formula
caches were also empty. Source validity and live error behavior both matter.

## Reopen, retention and renderer boundary

Create a hash-verified saved copy at a new owned path, open it without initialize,
and read back the input/formula/value/source cells. A same-path open can be
deduplicated by the host, so opening alone is not a second-session proof. Make
one scoped edit, read it back, then restore or retain it as a new explicit version.
Restoring semantic values may leave additional internal shared strings and a
different archive hash; do not claim byte-exact restoration unless verified.

Read complete source paragraphs, ledger/citations and table cells from their
saved locations. Keep the full long-form source bundle as well. The native file's
default narrow columns/row heights plus a wrapText flag do not establish readable
layout. `inspect_document` is a package/security hint report; it identified no
external relationships in the synthetic case but selected no rich renderer.
No rendered grid/chart/print-page inspection is claimed by these API reads.

The host API is **not an OS sandbox** and does not inherit a shell's synthetic
HOME. Use only explicit owned files, no personal profiles/templates, macros,
external workbook links or uploads. A denied application/UI route cannot be
retried through COM, shell, export or an alternate launcher.

Keep exact action inputs, returned artifact versions, local file hashes and
source copies. Use the accepted P05/P07 procedure for bound QA: native calculation
and editability can pass while persisted-cache and required-renderer controls
remain unverified. Independent review and shared pipeline release are separate.

## Read-only package integrity is a separate layer

The format checker validates required content types and all internal relationship
targets before interpreting workbook/worksheet/shared-string parts. Renamed
VBA/OLE/external-link declarations remain forbidden; a filename alone is not the
mechanism's identity. It validates actual SST roots, declared cell types and
unambiguous value/formula/inline payloads before decoding even an empty cell.
Plain/rich/shared/inline text, native `phoneticPr` formatting metadata and literal
`=1+1` remain distinct from formulas.

For the XML parts it decodes, the existing parser rejects DTDs at its declaration
hook, so UTF-16 encodings do not bypass an ASCII-byte search. Normal XML in those encodings remains
supported. Only inert single-value declarations are used in regression tests;
there is no external-entity or amplification probe.

An explicit `t="normal"` on a formula is equivalent to its omitted default.
Shared/array/data-table/unknown forms or uninterpreted attributes remain
unverified. None of these structural corrections recalculates or publishes a
cache, changes the frozen native workbook, authorizes an application or clears
the existing persisted-cache/rendered-layout gates.
