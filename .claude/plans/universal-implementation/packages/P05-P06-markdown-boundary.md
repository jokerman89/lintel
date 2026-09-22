# Shared Markdown source-boundary checkpoint

**Status:** APPROVED, 2026-09-20.
**Authority:** A03.2 exact acceptance identity, A05.2 valid navigation, A23.2 shared consumers.
**Baselines:** P05 `3adae4b`/`5a4933e`; P06 `9f6b69d`.

## Decision

Use one stateless source-boundary helper rather than maintaining two incomplete block
parsers. Extend the proven P06 logical-source model with explicit facts; its current
`kind=prose`, `content_start` and opaque context IDs are NOT sufficient to authorize
task-progress normalization. Moving that class unchanged would not fix the defect.

Alternatives rejected for this checkpoint: independent P05 exclusions repeat the same
boundary interpretation; a new external parser/runtime dependency broadens installation
before this bounded shared contract is tested. Do not claim full CommonMark rendering,
dynamic dependency analysis or a universal task schema.

## One owner and sequential write scope

P06 is the only writer of `lib/markdown_source.py`, its generator import/use/preflight,
`tests/unit/markdown-source.py` and `.sh`, and its owned nav/consumer preservation tests,
client guide and P06 report. It must preserve all C01-C05 fixes, public-resource closure,
private exclusions, actual opening HTML attributes and installed-source operation.

P05 owns only its later classifier consumption, selected-leaf matching, one-character
normalization/excerpt handling, clearance regression tests, evidence docs and P05 report.
It must not fork a block parser or edit the common module. No QA-v2, policy, work-map,
profile or corroboration semantics change under this card.

MasterSession owns fan-in, shared reducers and acceptance. P06 freezes and verifies a
provider checkpoint first; MasterSession supplies that exact source/API before P05 BUILD.
No caller may treat an unreviewed provider as final acceptance. The P06 reviewer reviews
the helper and complete component; the P05 reviewer reviews its actual consumer. Final
combined producer/consumer checks run before integration is called complete.

## Shared API, version 1

`classify_markdown(text: str) -> MarkdownBoundaries`, Python 3.9 standard library only.
Invalid input types fail explicitly. No files, subprocesses, target imports, policy,
task IDs, normalization or mutation are part of this function.

Immutable result types are declared once in that module:

| Type | Fields |
|---|---|
| Span | start, end |
| Container | id, parent_id, kind (quote/list), marker: Span, content_column |
| LineBoundary | start, end, next_start, body: Span, content_start, residual_indent, container_ids, kind |
| Region | span, kind, tag (optional) |
| ListItemOccurrence | marker, content, line_index, container_ids, classification |
| MarkdownBoundaries | original, lines, containers, regions, list_items |

Line kinds: prose, blank, fenced_code, indented_code, raw_html, opaque, unknown.
Region kinds: inline_code, fenced_code, indented_code, quote, html_tag, raw_html_body,
comment, opaque, unknown. Item classification: prose, quoted, literal, unknown.

Offsets are zero-based half-open Python Unicode codepoint positions in the EXACT
supplied string, not rendered/stripped text or implicit UTF-8 byte offsets. CRLF occupies
two codepoints; line end excludes terminators, next_start includes them; EOF may be both.
Tabs use four-column stops without modifying the string. Parse-local container IDs are
not durable identities. Deterministically ordered regions may overlap.

Consume compound quote/list prefixes before indentation/block classification. Item
occurrences record a real structural marker, not a continuation or checkbox-shaped
string. Marker spans cover the bullet/ordered marker; content spans identify the first
physical item's content after syntactic padding, preserving residual whitespace.
Literal/raw/comment facts must cover same-line HTML too; absence of a code label is not
positive eligibility. Ambiguous/unsupported spans remain explicit and identity-bearing.

P06 may inspect permitted opening-tag spans for literal resource attributes before
excluding raw bodies; a script `src` must survive while script text is never executed.
P05 considers only positively classified ordinary item occurrences in the authoritative
mapped tasks file, matches a selected leaf, and normalizes only its single ASCII checkbox
state character. Quoted/literal/opaque/unknown content stays byte-for-byte significant.
Classify the FULL supplied raw task source before selecting an excerpt; an excerpt must
not lose a surrounding literal container. Excerpt processing consumes the SAME eligible
spans, never another independent row parser.

## Stable refinements and verification

Checkbox authority remains plan.md.

| Leaf | Owner | Dependency | Acceptance |
|---|---|---|---|
| A05.2.s1 | P06 | Approved API | Capture manually expected original-span and classification matrix |
| A05.2.s2 | P06 | s1 | Extract/refine one helper without changing supplied text or navigation policy |
| A05.2.s3 | P06 | s2 | Real generator/preflight/installed bundle consumes the same helper; missing helper fails before writes |
| A05.2.s4 | P06 reviewer | s3 | C01-C05 and full owned adapter spec/quality preserve behavior |
| A03.2.s1 | P05 | Frozen provider checkpoint | Replace the local block parser with the shared facts |
| A03.2.s2 | P05 | s1 | Normalize only selected real progress-char spans, including excerpt identity |
| A03.2.s3 | P05 | s2 | Literal/criteria/approval/product mutations block actual reader/QA/SHIP; real nested progress reuses |
| A03.2.s4 | P05 reviewer | s3 | Independent exact consumer spec then first full owned quality |

Required shared cases: exact compound `- -` fenced checkbox, root/list/quote nesting,
indented and tab-indented code, raw PRE/CODE/SCRIPT/STYLE and same-line fragments,
HTML comments, ordinary paragraphs/continuations, EOF/LF/CRLF and Unicode. Validate
source spans themselves with independent expected values, not scanner-generated oracles.

Retain P06's EOF/title/container/link grid, real init/check/clone/missing-source and
installed-target-removal/sentinel/privacy/binary cases; keep reducers temporary. Retain
P05's v2 obligations, ordered legacy/error recovery and docs-only/advisory positives.
Run the same literal versus real-task mutations through actual clearance commands.
A local Markdown renderer can corroborate interpretation, not replace span/behavior tests.

Freeze exact provider and consumer commits, record actual dependency bytes, and keep
both independent review gates open until verified. No global install, network or
unrelated parser expansion is authorized.

## Q01 consumer identity refinement

The immutable independent rejection `0cdbf596` (report-only, parent `9c8ef727`;
integrated report `29ae5d9`) reopens P05 specification. Its first full quality pass
started but stopped on this counterexample; no quality approval exists.
Provider `7425960` remains accepted and unchanged.

P05 must bind the relevant full-source classification/normalization eligibility into
acceptance identity, not merely use it before hashing the resulting excerpt bytes.
Adding an enclosing fence or raw PRE outside the selected excerpt must invalidate old
reader/QA/SHIP clearance even when every checkbox is already a space, or when a formerly
normalized x is changed to a now-literal space. Keep full-source classification first,
one exact provider and one-character progress eligibility.

Use deterministic selection-relative facts: parse-local IDs or absolute offsets that
change with unrelated text before the selection are not durable identities. Preserve
genuine structural space/x/X progress, nested lists, Unicode/CRLF, unchanged acceptance
and unrelated out-of-selection edits. Do not fix this by hashing the whole raw task file,
by duplicating Markdown parsing, or by changing QA/policy/provenance rules. Existing
public signatures and version domains remain unchanged. Document any revised hash
preimage precisely; old insufficient receipts do not silently acquire new clearance.

Refinements in plan.md: A03.2.e1 reproduces exact all-space, fence-retains-x,
fence-literal-space and raw-PRE transitions with stale QA restored before SHIP;
A03.2.e2 binds the relevant interpretation through the single consumer; A03.2.e3
verifies those negatives and retained real-progress/outside-selection positives.
The original A03.2.s4 still requires the same independent reviewer to pass complete
owned spec, then finish the first whole bounded quality review on a new frozen SHA.
Only the four existing consumer-owned paths plus P05's own report may change.
