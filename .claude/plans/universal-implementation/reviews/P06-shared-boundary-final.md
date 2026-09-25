# P06 shared-boundary component specification review

**Date:** 2026-09-20. **Stage 1: FAIL. Stage 2: NOT RUN.**
The shared-provider checkpoint has two reproducible P2 specification defects.
C01-C05 remain closed individually. This is an independent, read-only component
review, not implementation, full quality acceptance or joined release acceptance.
After receiving the preliminary findings, MasterSession explicitly directed this
reviewer to finish the bounded facts/init/check/clone proof and report, without
starting quality, repairing product code or expanding the syntax audit.

## Immutable scope and authority

| Reference | Exact commit |
|---|---|
| Full bounded P06 base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Original P06 product | `6f5d665cd4e3831c2dd6516199c924a2922fba10` |
| Original builder/report snapshot | `4a277f7e899101308995b107e967127f96bb8085` |
| Original C01 review | `dbe5d3953322d02db118ff4b87af3a28aafbc3e7` |
| First repaired product | `be696488fb88ac23eea4269233f5a9fd32b45e02` |
| C02/C03 review | `3e8abb997b2e495efe3dcea4374f43880f20b5b7` |
| Third product | `560e64ac70468b7c482085fcce08824145715103` |
| C04/C05 review | `6b874c78dc3fa54e818013d1b3cc340e93253abc` |
| Approved narrow EOF/container repair card | `e76ed6c56e26a4d66590d6a0ca4c4456d18513ac` |
| Approved shared-provider/API repair card | `7a892b4996f242cf4c51d3e460fff841ead2f885` |
| Current parent / narrow repaired baseline | `9f6b69d9b954f02bf6f3b37dc93406732faa46b3` |
| **Reviewed product** | **`09148b71cb57df0a5bb5cc21f3f1681d6715390e`** |

The approved cards are the exact Git objects above at
`.claude\plans\universal-implementation\packages\P06-markdown-repair.md` and
`packages\P05-P06-markdown-boundary.md`, respectively. The latter refines the former
with one P06-owned `lib\markdown_source.py` facts API; it does not authorize a
P05-local replacement parser.

The product was pinned on the clean reviewer branch
`jokerman-microsoft-universal-adapters-shared-review`. The prior report branches
`jokerman-microsoft-universal-adapters-review`, `...-recheck` and `...-final`
retain their exact dbe5d395, 3e8abb99 and 6b874c78 commits. No builder, coordinator
or earlier reviewer branch was reset. The only repository file authored by this
review is this report; synthetic fixtures and runners used session-local storage
and disposable directories.

The cumulative base-to-product delta contains 43 paths. The current checkpoint
changes exactly eight approved paths relative to its parent:

- `lib\markdown_source.py`
- `bin\li-copilot.py`
- `tests\unit\markdown-source.py`
- `tests\unit\markdown-source.sh`
- `tests\unit\adapter-navigation.py`
- `tests\integration\universal-adapters.py`
- `docs\client-adapters.md`
- `.claude\plans\universal-implementation\reports\P06.md`

Authority also includes the repository and Copilot/scoped-shim instructions,
ADR-0024/0025/0028, lessons L-030 through L-032, initiative `spec.md`,
`packages\P06.md`, the builder report and `reports\host-source-research.md`.
Earlier component-spec judgments are retained only for unchanged behavior and
the preservation checks identified below. No first whole-component quality
review of `40c2795..09148b71` has occurred.

## New specification findings

Severity counts: **P0: 0; P1: 0; P2: 2; P3: 0.**

| ID | Severity | Product source | Finding | Confidence |
|---|---|---|---|---|
| P06-C06 | P2, must fix | `lib\markdown_source.py:102,253-276,389-398` | An ordered-looking paragraph continuation is emitted as an actual structural item with positive `prose` classification. | 10/10 |
| P06-C07 | P2, must fix | `lib\markdown_source.py:316-328,341-344,364-374`; consumer `bin\li-copilot.py:338-343` | A multiline inline-code span containing a script tag loses its code boundary; code-only `src` becomes a required and bundled resource. | 10/10 |

These contradict the approved real-occurrence/literal-facts contract and
`docs\client-adapters.md:121-132,143-155`. They are not requests for remote URL
fetching, heading validation, rendering, arbitrary script execution or broader
Markdown crawling. A bounded parser may explicitly report unsupported facts; it
must not silently turn a continuation or a code example into a positive fact.

### P06-C06: paragraph continuation becomes a positive item

Exact supplied Unicode string:

```python
"Paragraph\n2. [ ] A05.2 ordinary continuation\n"
```

Expected: no `ListItemOccurrence`. In ordinary Markdown, an ordered list can
interrupt an existing paragraph only with start number 1. Here there is no blank
line and the marker is `2.`; the second line remains paragraph content. The shared
card specifically requires actual structural occurrences, not continuations.

Actual provider result:

```text
ListItemOccurrence(
    marker=Span(start=10, end=12),
    content=Span(start=13, end=44),
    line_index=1,
    container_ids=(1,),
    classification='prose')
regions=()
```

This was reproduced both against the immutable checkout and against the exact
installed helper inside a real local Git clone. The latter printed:

```json
{"source": "Paragraph\n2. [ ] A05.2 ordinary continuation\n", "items": [{"marker": [10, 12], "content": [13, 44], "classification": "prose"}], "regions": []}
```

The subprocess exited 0. The independent normative test instead asserts
`classify_markdown(text).list_items == ()`; it fails with the tuple above.

Both structural positive controls pass:

```python
"Paragraph\n\n2. [ ] A05.2 real item\n"
"Paragraph\n1. [ ] A05.2 real item\n"
```

Each correctly yields one `prose` item whose content is
`[ ] A05.2 real item`. Therefore suppressing all ordered markers, or simply
making everything unknown, would not satisfy the required preservation.

**Cause and required correction:** `_container` recognizes any permitted ordered
marker at line 102, and lines 265-276 create the candidate without enforcing
paragraph-interruption semantics. The exclusion/classification pass then has no
literal region to reject it and returns `prose` at line 398. Incorporate the
relevant paragraph/container context in the single provider's structural-item
decision. Preserve the valid controls and exact original spans. This is a
source-facts defect, not a new task-schema request. No P05 clearance command was
run, and no downstream clearance bypass is claimed.

### P06-C07: multiline inline code leaks an HTML resource

Exact supplied string, with one LF inside the single-backtick code span:

```python
text = (
    '`<script src="review-fixture/code-only.js">\n'
    '</script>`\n\n'
    '[Real](review-fixture/guide.md)\n'
)
```

Expected: `Region(Span(0, 54), "inline_code", None)` covers the entire code
example. Only `review-fixture/guide.md` is navigation. A matching backtick code
span may contain a line ending; the enclosed script tag is literal, not HTML.

Actual regions:

```text
Region(Span(1, 43), 'html_tag', 'script')
Region(Span(43, 44), 'raw_html_body', 'script')
Region(Span(44, 53), 'html_tag', 'script')
```

There is no covering `inline_code` region. The independent exact-span assertion
fails. The navigation consumer selects both the code-only script resource and
the real guide.

For actual consumer proof, the exact snippet was appended to the original
`docs\faq.md` as `original + b"\n" + text.encode("utf-8")` in a disposable archive
of `09148b71`. The fixture guide contained
`# Real local guide`; `code-only.js` was initially absent. A new target contained
only a sentinel, `keep.txt` with bytes `unchanged`. Every adapter entry point came
from the archived or installed product; no renderer, parser mock or replacement
module was used.

The following commands abbreviate the same native interpreter as `python` and
the random temporary root as `<temp>`; error/output text is otherwise exact:

```text
python -B -S <temp>\s\bin\li-adapter.py init --target <temp>\multiline-code --client other
ERROR: Required source file is missing: <temp>\s\docs\review-fixture\code-only.js
EXIT: 1
```

The target snapshot and sentinel were unchanged, so pre-write refusal still
works; the defect is requiring a nonexistent code example in the first place.

Adding only this synthetic resource:

```python
b"SYNTHETIC-CODE-ONLY-SHOULD-NOT-BUNDLE\n"
```

changes the same operation to:

```text
Lintel kit ready: 390 managed files; vendored source; clients=other. Review the managed inventory and foundation diff.
Start a new host session and inspect its discovery UI, or read .github/lintel/START.md explicitly. No hooks or host permissions were changed.
EXIT: 0
```

Both checks below exit 0:

```text
python -B -S <temp>\multiline-code\.github\lintel\bin\li-adapter.py check --target <temp>\multiline-code
Lintel kit verified: 390 managed files; vendored source; clients=other; no live-host validation.

python -B -S <temp>\multiline-code-clone\.github\lintel\bin\li-adapter.py check --target <temp>\multiline-code-clone
Lintel kit verified: 390 managed files; vendored source; clients=other; no live-host validation.
```

The second target was a real local `git clone`, not a directory copy. Both
inventories contain `.github/lintel/docs/review-fixture/code-only.js` with the
exact synthetic bytes. Every managed file/hash survived the autocrlf clone.
Successful hash checking therefore confirms reproducibility of the wrong
dependency selection, not correctness of the code boundary.

One-change controls:

| Change from exact snippet | Actual outcome |
|---|---|
| Remove only the LF between opening and closing script tags; retain both backticks; remove `code-only.js` from source | Init, installed check and actual clone/check pass with 389 managed files. The code-only resource is absent from the inventory and filesystem. |
| Remove only the two backticks; retain the LF; supply `code-only.js` | Init and installed check pass with 390 managed files. The now-real opening `src` is correctly retained. |

**Cause and required correction:** the first pass limits `_code_end` to the
physical line at line 317. It then interprets the enclosed `<script>` as a real
literal region, advances `literal_until` and labels the next line raw HTML.
The second pass extends its search limit only through consecutive `prose`
lines, so it cannot recover the multiline code span. The generator correctly
looks for a covering code region at lines 338-343, but none was supplied.
Resolve precedence and span continuity in the sole provider before HTML
resource eligibility is exposed; retain actual opening-tag attributes and
same-line code behavior. Do not mask this with a second parser in either
consumer or relax the missing-source/privacy checks.

## Retained earlier closures and boundaries

The rerun Universal suite exercises C01-C05 separately through actual consumers.
An additional independent combined fixture used the exact earlier HTML,
escaped-opener, escaped-underscore, wrapped-label, EOF-title and quoted-code
examples together, followed by installed checking and a real autocrlf clone.

| Finding | Disposition at `09148b71` | Current evidence |
|---|---|---|
| C01, seven missing README targets | CLOSED individually | Pristine manual `other` init/check/clone passed, 388 managed files. All seven original targets and transitive public guides/assets are managed. Removing installed `docs\faq.md` and its inventory entry still fails before writes. |
| C02, script `src` and quoted `>` | CLOSED individually | `<script src="app.js"></script>` and `<a title="1 > 0" href="guide.md">Guide</a>` retain both actual resources through init/check/clone. Script content is not executed. |
| C03, escapes and wrapped labels | CLOSED individually | The exact escaped opener selects nothing; `a\_b.md` selects `a_b.md`; the two-line wrapped label retains its guide through real consumers. |
| C04, titled reference at EOF | CLOSED individually | The exact `[p06-eof]: review-fixture/guide.md "Title"` remains at physical EOF without an added newline. Init/check/clone retains the guide; EOF/LF/CRLF grid and installed-removal negatives pass. |
| C05, blockquote-relative indented code | CLOSED individually | `>     [Code example](review-fixture/does-not-exist.md)` neither requires nor copies that absent code-only file, while the following real guide is retained. Present-code-only and source-graph negatives in the focused suite also pass. |

C06/C07 are separate remaining shared-boundary failures. They do not erase the
specific earlier repairs or falsely reopen their exact fixtures.

Additional preserved facts and consumer behavior:

| Contract | Independently observed result |
|---|---|
| Original Unicode/codepoint/CRLF positions | For `"\u03bb\r\n- [ ] \U0001f642"`, `original` is the supplied string; line triples are `(0,1,3)` and `(3,10,10)`, marker `[3,4)`, content `[5,10)`. These are manually expected codepoint values, not byte offsets or provider-generated oracles. |
| Immutable/no-I/O facts API | Existing immutable-type, invalid-input, deterministic-region and excerpt-context tests pass. Static provider inspection found only standard-library classification responsibilities, not file reads, subprocesses, task IDs, policy or clearance decisions. This does not cure C06/C07. |
| `prose` start is not blanket eligibility | For `- [ ] real ` followed by `` `not a task` <pre>raw</pre> <!-- comment --> ``, the item is `prose` but later inline code `[11,23)`, raw body `[29,32)` and comment `[39,55)` remain explicit. |
| Compound literal containers | Exact `- - ```markdown` fixture keeps both opening items literal, suppresses the enclosed checkbox as an occurrence and preserves a later real item. Existing root/list/quote/tab/raw/opaque/unknown cases pass. |
| Actual public source closure | Seven originals, transitive docs/showcase assets, `LICENSE`, design attribution, both third-party licenses and actual `.claude-plugin\plugin.json` remain managed. Missing public guide fails before writes. |
| Mapped bundle, not stray filesystem | Existing navigation negative rejects a resource absent from the generated file map even if an unmanaged target file exists. Actual installed-file deletion plus inventory deletion also fails. |
| Private/source-only boundary | Synthetic `.claude` memory/runtime, private-pack and hidden-doc targets are not copied. Bundled navigation remains useful with explicit source-only/not-fetched notices. Exclusion tests prevent private reads; the independent fixture also found no private sentinel bytes in the bundle. No real private profile was accessed. |
| Text/binary/EOF preservation | CRLF text assets become LF; binary PNG sentinel bytes are unchanged; the EOF reference remains without a newline. All managed bytes and inventory hashes match across four real local autocrlf clones. Unmanaged project prose is not falsely required to be byte-identical under Git autocrlf. |
| Ownership, drift and additive installs | Universal/Copilot suites preserve project prose, refuse managed/unmanaged collisions and tampered ownership, retain additive client selection and shared discovery roots, and pass idempotence/symlink/home-boundary cases. The independent modified-document update returned `ERROR: Modified managed file (preserved): .github/lintel/docs/faq.md` with the entire target unchanged. |
| Trusted helper and missing-helper preflight | Installed provider bytes/hash match source. Removing it rejects with `ERROR: Required source file is missing: ...\lib\markdown_source.py`, exit 1, no traceback or target changes. Synthetic target and `PYTHONPATH` replacement modules never execute, including when the real helper is missing. |

## Per-leaf stage dispositions

The table separates preservation from full acceptance. No pass below means that
all new clients work live or that the failed component is accepted.

| P06 leaf | Stage 1 specification disposition | Stage 2 quality |
|---|---|---|
| A06.1 | PASS retained: unchanged registry/reader keep 38 distinct surfaces and conservative aliases; malformed/collapsed-record tests pass again. | NOT RUN |
| A06.2 | PASS retained: vendor documentation, delivered adapter and observations round-trip separately; unknown remains unknown. | NOT RUN |
| A06.3 | PASS retained: actual available tool names versus permission, native/serial/manual paths, attributable isolation and independent-review-pending behavior pass the current registry/consumer cases. | NOT RUN |
| A06.4 | PASS retained: missing/denied controls fail explicitly; unsupported model/global/enablement options do not invent `.disabled`, hooks or permission bypasses. | NOT RUN |
| A05.1 | PASS retained: task-first onboarding and useful public navigation remain; source content was not dropped to obtain a green check. | NOT RUN |
| A05.2 | FAIL: C01-C05 close individually, but C06/C07 violate the required shared source-boundary/navigation contract. Native Copilot/Claude preservation and truthful manual output do not cure this. | NOT RUN |
| A05.3 | PASS retained within assigned scope: neutral defaults and optional expert methods remain; no private/company/retention/venture assumptions were introduced. | NOT RUN |
| A05.4 | Architectural/protocol/live-limit preservation retained; current shared-boundary behavioral claims are NOT accepted while C06/C07 contradict them. Final integrated truth remains pending. | NOT RUN |

The assigned welcome, cli-fingerprint, pair-agent, codex, careful and
instruction-parity-check sources are unchanged by this checkpoint. Their prior
bounded specification judgments are retained, not relabeled as fresh quality
review. Codex's useful ad-hoc inspection/second opinion is not made dependent on
bogus P05 clearance or a full-plan ceremony.

| Approved repair leaf | Disposition |
|---|---|
| A05.2.m1 | Historical immutable C04/C05 reproductions remain in `6b874c78`; exact cases now pass at the current checkpoint. |
| A05.2.m2 | PARTIAL: one original-coordinate model and EOL/EOF controls are present; correct boundary semantics are not complete, notably C07. |
| A05.2.m3 | Shared consumption is present, but shared incorrect facts still expose the C07 resource; not complete behavioral acceptance. |
| A05.2.m4 | Authored EOF/title/container grids pass; independent required-literal negative C07 fails. |
| A05.2.m5 | FAIL: earlier clone/drift/privacy cases pass, but the multiline code-only dependency both blocks when absent and is bundled when present. |
| A05.2.m6 | C01-C03 and current nav/registry/Universal/Copilot reruns pass. Current temporary regeneration is builder-reported, not independently rerun in this failed checkpoint. |
| A05.2.m7 | FAIL at specification; first whole-component quality remains NOT RUN. |
| A05.2.s1 | Incomplete required expected-facts coverage: shipped positives pass, but the independently grounded continuation and multiline-literal negatives fail. |
| A05.2.s2 | FAIL: the single immutable provider exists, but C06/C07 violate actual-occurrence/literal semantics without changing the supplied text. |
| A05.2.s3 | Exact installed helper, import boundary and preflight pass; actual generator behavior still fails C07. |
| A05.2.s4 | FAIL component specification; full owned quality cannot start. |

P05's A03.2.s1-s4 remain outside this review and pending the corrected exact
provider dependency plus independent actual-consumer acceptance.

## Checks actually run on this checkpoint

All five current repository suites ran with native Python 3.11.9, `-B -S`,
isolated fake homes, disabled ambient Git configuration/prompts and the approved
task-local jq on child-process PATH only. Approved jq SHA256 was verified as
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`.
The immutable checkout's HEAD/status remained unchanged during testing.

| Command or bounded probe | Actual outcome |
|---|---|
| `python -B -S tests\unit\markdown-source.py` | PASS, 11 methods, zero skips. |
| `python -B -S tests\unit\adapter-navigation.py` | PASS, 28 methods, zero skips; includes the authored 126 composed grammar, 648 reference and 60 container cases. |
| `python -B -S tests\unit\client-capabilities.py` | PASS, 16 methods, zero skips. |
| `python -B -S tests\integration\universal-adapters.py` | PASS, 15 methods, zero skips, including all 38 surface routes and real installed-source/clone/preflight cases. |
| `python -B -S tests\integration\copilot-kit.py` | PASS, 22 methods, zero skips. |
| Independent `p06-shared-boundary-probes.py facts` | 8 methods: 6 pass, 2 fail exactly on C06/C07; exit 1. These are specification assertion failures, not runner failures or skipped expectations. |
| Independent `p06-shared-boundary-probes.py consumers` | Completed exit 0 after asserting the documented failing behavior and controls, retained closures, privacy/bytes/drift/preflight and four real local clones. This is successful reproduction, NOT component acceptance. |
| Local Git scope/preservation inspection | Exact parent/current eight-path delta, cumulative 43 paths, clean product pin and three preserved report branches verified. |

The five repository suites total **92 passing methods, zero skips**. Green
authored suites do not outweigh the two independently failing contract cases.
Unit/Universal/probe fake homes were empty. The Copilot compatibility suite left
its expected fake-home `.lintel\audit\migration.jsonl`; it did not touch the real
home. Temporary repositories were local-only, and disposable fixture trees were
cleaned up. No new dependency, installed client, nested agent or network request
was used.

Exact session-local evidence, retained outside the repository:

| Artifact | SHA256 where useful |
|---|---|
| `p06-shared-suites.py`; `p06-shared-unit.log`; `p06-shared-universal.log`; `p06-shared-copilot.log` | Current suite runner and complete command/output records. |
| `p06-shared-boundary-probes.py` | `9c75e267bc95624ccf920d6336475cb11b9bac47a7e2160d7c7155194c37bb33` |
| `p06-shared-facts-probes.log` | `7c0a33c6d56e2fa4d5a7ee4e8ae6e4b75d192c7470d54064f07ea4e1952d4ab8` |
| `p06-shared-consumers-probes.log` | `a22021dbbcb74dd4d16cc020cc9ace4ecd69e596f4fa2d10ef4f9f4c799d5d1b` |

The literal fixtures and meaningful outputs are also embedded above so the
findings do not depend on access to this session's temporary paths.

## Limits and next gate

The coordinator-requested first full bounded P06 quality pass has **not run**.
No product repair, shared reducer regeneration, plan/memory update, global
configuration, private profile access, remote Git/GitHub operation, client login,
model/account invocation, publication or release acceptance occurred.

Temporary generator/idempotence successes in the builder report remain
builder evidence. The earlier review's disposable regeneration successes apply
to its earlier immutable product, not automatically to `09148b71`. Current
root generated reducers and final strict-suite/CI/integration gates remain
coordinator-owned and open.

P04/P05/P07/P08 joins, new-module preflight, P05 actual clearance-consumer
acceptance and final reconciled independent review remain pending. Historical
P06-plus-P04 installed-source composition does not accept the current combined
tree. P06 transporting a profile reference is not proof of P07 end-to-end policy
pinning or resolution of its separately reproduced shell-reference policy-loss
defect.

Vendor-source records are not delivered adapters; file generation is not actual
host discovery; an available tool is not permission. No new live
client/model/account behavior is established here. Remote URLs, heading
fragments, rendered layout and complete client pilots remain explicitly unrun,
without being used to dismiss C06/C07.

Return a corrected immutable provider/component checkpoint to this same reviewer.
Retain C01-C05, the real-versus-literal controls, trusted installed helper and
all privacy/ownership constraints. Stage 1 must pass before the first full
bounded P06 quality review can begin.
