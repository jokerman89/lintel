# P06 independent specification recheck

**Date:** 2026-09-20.
**Reviewer:** independent `lintel-reviewer`, session
`08ffd693-ae70-44aa-912f-94cc1bb2faec`.
**Original P06-C01:** CLOSED individually; all seven omitted destinations now survive installation and a real Git clone.
**Stage 1 (component specification):** FAIL; two new P2 literal-navigation defects.
**Stage 2 (first full P06 quality review):** NOT RUN; specification has not passed.
**New findings:** P0 0, P1 0, P2 2, P3 0.
**Package, joined integration and live-client acceptance:** NOT GRANTED.

The reviewer made no product repair, launched no nested agent, and performed no
network, real-client/model/account, private-profile or global-install operation.
Only this report is authored in the repository. Synthetic reproduction content lived
in disposable archives, not the candidate checkout.

## Exact references and preserved review history

| Role | Immutable reference |
|---|---|
| Repaired candidate reviewed here | `be696488fb88ac23eea4269233f5a9fd32b45e02` |
| Its parent / original report snapshot | `4a277f7e899101308995b107e967127f96bb8085` |
| Original P06 product | `6f5d665cd4e3831c2dd6516199c924a2922fba10` |
| Full P06 comparison base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Preserved original independent report | `dbe5d3953322d02db118ff4b87af3a28aafbc3e7` |

The clean review worktree was switched to the newly created
`jokerman-microsoft-universal-adapters-recheck` branch at the repaired candidate.
`jokerman-microsoft-universal-adapters-review` remains at `dbe5d395`, preserving
`reviews\P06-component.md` and its original rejection. No builder or coordinator
branch was reset, merged or modified. A subsequent commit of this report is not a
new product candidate.

The repair changes exactly eight paths relative to its parent:
`bin\li-copilot.py`, `docs\client-adapters.md`, `docs\multi-cli.md`,
`tests\unit\adapter-navigation.py`, `tests\unit\adapter-navigation.sh`,
`tests\integration\universal-adapters.py`, `tests\integration\copilot-kit.py`,
and `reports\P06.md`. The full base-to-candidate delta is 40 paths, including the
builder report. No shared reducer, generated wrapper, hook or protocol source was
changed by the repair.

The original review's repository/adapter/scoped-shim instructions, ADR-0024/0025/0028,
L-030 through L-032 and mapped P06 authority remain applicable. The explicit
Universal work map and four synchronized protocol blocks were checked again.
The recheck covers the requested repair and preservation/specification boundaries;
it does **not** claim the conditional full base-to-candidate quality review occurred.

## Original finding closure

**P06-C01 is closed for its seven specific missing source targets.** In a pristine
archive of `be696488`, a manual `other` installation produces 387 managed files.
A real local Git commit and clone with `core.autocrlf=true` retains:

```text
docs/README.md
docs/faq.md
docs/concepts/engineering-modules.md
docs/concepts/pack-resolver.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
CHANGELOG.md
```

The clone's own `.github\lintel\bin\li-adapter.py check --target <clone>` returns 0.
The original source checkout is not needed for that check. Further verified examples
include pack inheritance, agent memory, showcase README/HTML, the referenced wiki
skills page and migrations index. All inspected files match their managed hashes.

LICENSE, CODE_OF_CONDUCT, design attribution, both retained third-party license texts
and the actual `.claude-plugin\plugin.json` match source bytes after intended LF
normalization. Source-only links in CONTRIBUTING are explicitly labeled rather than
presented as consumer-local files. The bundle contains no `.claude` knowledge/runtime
directory or synthetic company pack.

The following adversarial cases now work as intended:

- Removing `docs\faq.md` **and** its inventory entry still makes the installed-source
  check fail with `Required source file is missing`, without writing anything.
- A stray unmanaged target file cannot satisfy the planned documentation graph.
- An ordinary missing transitive Markdown target blocks installation before writes.
- A locally modified managed guide makes both check and update fail; its bytes and
  every other consumer byte survive the refused update.
- Public-document symlinks, escaping paths and nonportable absolute references are
  rejected. Hidden/private/runtime synthetic content is neither read nor bundled.

This closure does not establish complete literal-resource parsing. Both traversal
and verification consume the same scanner, so an omitted token can be missed twice.
The new findings below are within the advertised local-link contract, not remote
URL, heading-fragment or arbitrary JavaScript-execution debt.

## New specification findings

| ID | Severity | Candidate source | Finding | Confidence |
|---|---|---|---|---|
| P06-C02 | P2, must fix | `bin\li-copilot.py:152-154,184,245-247,541` | Valid HTML resource attributes can be ignored by both bundling and installed verification. | 10/10 |
| P06-C03 | P2, must fix | `bin\li-copilot.py:183-200,207-211` | Markdown escapes and line-wrapped labels are interpreted incorrectly, producing false rejection or false closure. | 10/10 |

### P06-C02: retain literal resource attributes while excluding executable bodies

**Expected semantics:** a script element's `src` attribute is a literal resource
reference, not code inside its body. Reading that attribute does not execute JavaScript.
A `>` inside a quoted HTML attribute value does not close the tag or hide a later
`href`. These are ordinary literal HTML paths covered by
`docs\client-adapters.md:121-124` and the repair report at `reports\P06.md:33-39`.

**Root cause:** the masking expression at `bin\li-copilot.py:153-154` removes the
whole script element, including the opening tag and `src`. The HTML expression at
line 184 cannot traverse `>` inside a preceding quoted attribute. Both
`bundle_documentation` and `verify_links` then see no destination.

**Exact synthetic source:** append this line to the disposable archive's
`docs\faq.md`:

```markdown
[Public asset page](review-fixture/page.html)
```

Create `docs\review-fixture\page.html` with:

```html
<!doctype html>
<html><body><script src="app.js"></script>
<a title="1 > 0" href="guide.md">Guide</a></body></html>
```

Create both source targets: `app.js` containing `window.fixture = true;` and
`guide.md` containing `# Real local guide`. No JavaScript is executed.

**Actual real-process output** from the immutable generator and subsequently the
installed generator, with disposable absolute paths abbreviated:

```text
python -B -S <source>\bin\li-adapter.py init --target <consumer> --client other
exit 0
Lintel kit ready: 388 managed files; vendored source; clients=other.

python -B -S <consumer>\.github\lintel\bin\li-adapter.py check --target <consumer>
exit 0
Lintel kit verified: 388 managed files; vendored source; clients=other; no live-host validation.
```

The HTML page is installed, but neither `app.js` nor `guide.md` is present or inventoried.
Deleting both from the disposable source and repeating `init` into a fresh target
still returns 0 and writes 388 files: missing-source preflight also overlooks them.
Direct scanner probes independently return no links for either construct.

**Required correction:** recognize literal attributes on valid opening tags without
parsing body examples as resources; handle quoted attribute delimiters correctly.
Exercise both present-source and missing-source cases through actual init and the
installed-source check. Preserve the existing no-execution, no-fetch and privacy
boundaries. Do not resolve this by dropping meaningful HTML navigation or relabeling
literal `src` validation as unsupported JavaScript execution.

### P06-C03: honor Markdown escaping and valid wrapped link labels

**Expected semantics:** `\[` is a literal opening bracket, so it must not introduce a
link. Backslash-escaped ASCII punctuation in a real destination is decoded before
filesystem validation; `a\_b.md` denotes `a_b.md`, not a Windows path. An ordinary
inline link label may span lines while retaining its literal destination.

**Root cause:** line 187 matches a bracket even when escaped and explicitly excludes
newlines from labels. Line 200 only unescapes backslash, space and parentheses.
Line 210 consequently rejects other valid Markdown escapes as filesystem separators.
These are syntax boundaries in the newly introduced scanner, not a missing source file.

Three real-install reproductions used separate fresh consumers and changes only to
the disposable source's `docs\faq.md`:

| Exact appended Markdown | Source setup | Actual result |
|---|---|---|
| `\[Example, not a link](review-fixture/does-not-exist.md)` | No target is needed for literal text. | `init` exits 1: `ERROR: Required source file is missing: <source>\docs\review-fixture\does-not-exist.md`. The existing consumer sentinel survives. |
| `[Guide](review-fixture/a\_b.md)` | `docs\review-fixture\a_b.md` exists. | `init` exits 1: `ERROR: Non-portable local documentation link in docs/faq.md`. Target remains empty. |
| The two-line label shown below | The same `a_b.md` exists. | `init` exits 0 with 387 managed files, omits `a_b.md`, and installed-source `check` also exits 0. |

```markdown
[Read the
wrapped guide](review-fixture/a_b.md)
```

Thus the current scanner can both block a valid source and certify an incomplete
bundle. Existing positive tests for escaped parentheses, code/comments and simple
one-line labels do not discriminate these cases.

**Required correction:** implement the declared literal Markdown token/escape
semantics before resolving paths. Continue rejecting actual Windows/absolute/escaping
filesystem paths after decoding. Add regressions for escaped literal openers, normal
punctuation escapes and wrapped labels, including real installed-consumer verification;
do not require authors to remove valid prose or duplicate a guide to obtain a pass.

## Leaf preservation and stage gate

| Leaf | Recheck disposition |
|---|---|
| A06.1 | PASS retained. Registry, reader and compatibility API are byte-unchanged from original P06; distinct surfaces and alias negatives pass again. |
| A06.2 | PASS retained. Vendor/delivery/observation separation and unknown/partial identities remain; no new observation or blanket support is introduced. |
| A06.3 | PASS retained. Actual-tool selection, permission restrictions, native/serial/manual paths and outstanding independent review remain; registry and installed consumer cases pass. |
| A06.4 | PASS retained. Unsupported plugin/model/hook controls still fail explicitly. Assigned skills and shared review-owner references are unchanged, not silently reimplemented. |
| A05.1 | PASS retained. Task-first onboarding remains, with additional public navigation instead of lost content. |
| A05.2 | FAIL on P06-C02/C03. Original seven-omission C01 is individually closed; ordinary HTML/Markdown literal-resource preservation is not yet complete. |
| A05.3 | PASS retained within the assigned component scope. No new company/vendor/retention/venture defaults or private-data copying; specialist methods remain. |
| A05.4 | PASS retained for architecture, exact shared protocol and coordinator-owned reducer boundaries. This is not clearance of the failed navigation guarantees above or final integrated truth. |

The six assigned workflows retain their earlier reviewed methods: task-first welcome,
actual-host fingerprinting, scoped pairing, Codex second opinions including non-release
ad-hoc inspection, careful owned recovery and exact instruction parity. All six and the
registry/shims are unchanged by this repair. Native Copilot entry points and Claude
plugin/agent/optional-hook paths are preserved.

**Stage 2 remains NOT RUN.** This recheck neither substitutes a navigation-only quality
pass nor inherits one from the original report, which also stopped at specification.
Once the corrected immutable candidate passes Stage 1, the first quality review must
cover the entire bounded P06 change from `40c2795`, not only its latest repair.

## Checks actually run

Host: Windows, Python 3.11.9, Git Bash 5.3.15. Runs used short disposable temporary
paths, fake HOME/USERPROFILE/XDG directories, disabled bytecode writes and isolated
Git configuration. No client or package dependency was installed. The approved
task-local jq hash was reverified as
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`
and its directory was supplied only through per-process PATH.

| Command/scenario | Actual result |
|---|---|
| `python -B -S tests\unit\adapter-navigation.py` | 10 PASS, zero skips, including actual symlink refusal and LF/text versus PNG-byte preservation. |
| `python -B -S tests\unit\client-capabilities.py` | 16 PASS, zero skips. |
| `python -B -S tests\integration\universal-adapters.py` | 10 PASS, zero skips, including all 38 surface selections, the real navigation Git clone, transitive missing-source and modified-guide tests. |
| `python -B -S tests\integration\copilot-kit.py` | 22 PASS, zero skips; native-route/ownership/resource/CRLF/legacy preservation remains. |
| Additional pristine archive -> manual install -> real autocrlf Git clone -> installed-source check | PASS for original C01, six transitive examples, retained notices/product metadata, and managed hashes. |
| Additional deleted document and removed inventory entry; modified-guide update; unmanaged stray-file substitution | Intended failures reproduced with byte-preservation assertions. |
| Exact HTML/Markdown synthetic cases above, executed through real init/check | Five documented parser deviations reproduced and grouped into two findings; successful repro assertions are **not** passing product acceptance. |
| Six additional parser controls | PASS for ordinary inline/title/reference/HTML links, escaped parentheses, code versus list continuation, and comment/template exclusions. |
| `python -B -S bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; same explicit approved source map. |
| `python -B -S bin\li-instructions.py check` | PASS, all four protocol blocks. |
| Disposable archive: instruction sync, catalog generation, wiki generation, local adapter init, their checks, CLI-table guard, then repeat generation | PASS; second full-tree generation is byte-identical and authored-tree hashes remain unchanged. |
| Python 3.9 grammar parse of changed implementation/focused tests; base-to-candidate `git diff --check` | PASS. Python 3.9 runtime itself was not run. |

The four suite processes exit 0. Their fake homes remain empty except for the unchanged
legacy Copilot scaffold test's `.lintel\audit\migration.jsonl`, confined to that test's
fake home and previously attributed in `P06-component.md`. Direct adapter/clone/repro
fixtures leave fake homes empty. No real home or private profile is involved.
All owned temporary fixture trees were cleaned.

Session-local logs: `p06-recheck-existing-tests.log`,
`p06-recheck-clone-boundaries.log`, `p06-recheck-parser-regressions.log` and
`p06-recheck-regeneration.log`. The exact commands, normalized output and synthetic
inputs necessary to understand the failures are also preserved above.

## Limits and next handoff

The accepted documentation boundary still excludes remote URL availability, fragment
existence, rendered layout and arbitrary HTML/CSS/JavaScript execution. This review
does not reopen those limits; both new findings concern ordinary literal local paths
the repair explicitly promises to preserve.

No new-module preflight, P05 evidence API, P07 required-policy pin/resume, P08 lifecycle,
strict full-suite, CI or final joined review gate is closed here. The old P04 `02be6cb`
composition remains historical test evidence, now explicitly identified as rejected
component input by the builder report; it was not recomposed or endorsed in this recheck.
P06 `profile_ref` transport is still not proof of policy pinning, recovery or enforcement.
Coordinator-owned generated outputs were exercised only in a disposable archive.

All new live client/model/account scenarios remain unrun; the unchanged partial Copilot
App source observations do not establish live support for any of the 38 surface records.
No source URL was fetched and no private company policy or enterprise control was tested.

Return P06-C02/C03 to the original builder for a scoped literal-resource parser repair.
Preserve C01's now-working closure, notices, privacy, ownership and clone behavior.
Review the next exact immutable candidate for specification before starting the first
full bounded quality stage. This report authorizes no product mutation or publication.
