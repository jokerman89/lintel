# P06 third immutable component specification review

**Date:** 2026-09-20.
**Reviewer:** independent `lintel-reviewer`, session
`08ffd693-ae70-44aa-912f-94cc1bb2faec`.
**Previous findings:** C01, C02 and C03 CLOSED individually on this candidate.
**Stage 1 (component specification):** FAIL; new P06-C04 and P06-C05.
**Stage 2 (first full bounded P06 quality review):** NOT RUN.
**Open findings:** P0 0, P1 0, P2 2, P3 0.
**Component, joined integration and live-client acceptance:** NOT GRANTED.

The `final` filename identifies this immutable review report, not acceptance. The
reviewer made no product repair and launched no nested agent. Only this report is
authored in the repository; synthetic sources, consumers and local clones were
disposable. No network, remote Git/GitHub, publication, real-client/model/account,
private-profile or global-install/configuration operation occurred.

## Exact references and scope

| Role | Immutable reference |
|---|---|
| Third candidate reviewed here | `560e64ac70468b7c482085fcce08824145715103` |
| Candidate parent / first repair | `be696488fb88ac23eea4269233f5a9fd32b45e02` |
| Preserved second independent report | `3e8abb997b2e495efe3dcea4374f43880f20b5b7` |
| Original report snapshot | `4a277f7e899101308995b107e967127f96bb8085` |
| Original P06 product | `6f5d665cd4e3831c2dd6516199c924a2922fba10` |
| Preserved first independent report | `dbe5d3953322d02db118ff4b87af3a28aafbc3e7` |
| Full P06 comparison base | `40c279520a86945cc7e607692355bf5231446ff1` |

The clean reviewer workspace was pinned on
`jokerman-microsoft-universal-adapters-final` at `560e64ac`.
`jokerman-microsoft-universal-adapters-recheck` remains at `3e8abb99`, and
`jokerman-microsoft-universal-adapters-review` remains at `dbe5d395`.
No builder, coordinator or main-checkout branch was reset or modified. The subsequent
report-only commit is not a replacement product candidate.

The candidate reopens exactly five owned paths relative to `be696488`:
`bin\li-copilot.py`, `docs\client-adapters.md`,
`tests\unit\adapter-navigation.py`, `tests\integration\universal-adapters.py`,
and `.claude\plans\universal-implementation\reports\P06.md`.
The full `40c2795..560e64ac` component delta remains 40 paths. The registry,
capability reader, compatibility shims, six assigned workflows and other previously
reviewed adapter/documentation sources are unchanged by this five-path repair.
Generated root reducers remain deliberately unchanged.

Authority remains the repository/adapter/scoped-shim instructions,
ADR-0024/0025/0028, lessons L-030 through L-032, the mapped initiative specification,
`packages\P06.md`, and `reports\host-source-research.md`. The explicit approved work
map and four synchronized protocol blocks were checked again. Source documentation
is not installed-host evidence. This is the requested specification recheck and
preservation review, not the conditional full base-to-candidate quality pass.

## Individual closure of C01, C02 and C03

**C01 remains closed for its seven originally omitted targets.** A pristine immutable
archive produces a manual `other` consumer with 387 managed files. Actual init, its
installed-source check, a real local Git commit/clone with `core.autocrlf=true`, and
the clone's own installed-source check all return 0. Both consumers retain:

```text
docs/README.md
docs/faq.md
docs/concepts/engineering-modules.md
docs/concepts/pack-resolver.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
CHANGELOG.md
```

Additional verified transitive examples are pack inheritance, agent memory, showcase
README/HTML, the linked wiki skills page and migrations index. LICENSE,
CODE_OF_CONDUCT, design attribution, both third-party license texts and
`.claude-plugin\plugin.json` retain their actual source bytes after intended LF
normalization. Every managed clone file matches the original managed bytes and its
manifest hash. No bundled `.claude` knowledge/runtime directory is introduced.

The exact C02 source was replayed:

```markdown
[Public asset page](review-fixture/page.html)
```

```html
<!doctype html>
<html><body><script src="app.js"></script>
<a title="1 > 0" href="guide.md">Guide</a></body></html>
```

With `app.js` containing `window.fixture = true;` and `guide.md` containing
`# Real local guide`, real init/check/clone/check return 0 with **390** managed files.
The HTML page, script and guide are present and inventoried. Removing the source
guide blocks a fresh init before changing its sentinel. The rerun integration test
also removes each HTML resource separately, then removes each installed resource
and its inventory entry: each required failure occurs. No script is executed.

All three exact C03 sources were independently replayed through real init, installed
check, separate actual local clones, and each clone's own check:

| Source | Actual result |
|---|---|
| `\[Example, not a link](review-fixture/does-not-exist.md)` | PASS, 387 files; literal text does not select the nonexistent resource. |
| `[Guide](review-fixture/a\_b.md)` | PASS, 388 files; the actual `a_b.md` is selected. |
| The wrapped label below | PASS, 388 files; the actual `a_b.md` is selected. |

```markdown
[Read the
wrapped guide](review-fixture/a_b.md)
```

For the last two cases, removing `a_b.md` from source blocks fresh init before writes.
Existing consumer sentinels survive. These close the exact earlier findings, not
every possible Markdown boundary. Both bundling and verification use the same
scanner; their agreement alone cannot prove that a destination was recognized.

## New specification findings

| ID | Severity | Candidate source | Finding | Confidence |
|---|---|---|---|---|
| P06-C04 | P2, must fix | `bin\li-copilot.py:454-464`, especially `460` | A used reference definition with a title at EOF is dropped, allowing an incomplete bundle and successful check. | 10/10 |
| P06-C05 | P2, must fix | `bin\li-copilot.py:392,410-416`; compare `368-375` | Indented code inside a blockquote is interpreted as navigation, wrongly refusing valid source or bundling a code-only target. | 10/10 |

Both findings affect A05.2 and the static local contract at
`docs\client-adapters.md:107-132`. They do not request remote fetching, heading
verification, rendered-layout analysis or arbitrary script/CSS execution.

### P06-C04: accept a valid titled reference definition ending at EOF

**Expected semantics:** a used Markdown reference definition may terminate at EOF.
A quoted title does not require a final newline. This valid reference must select
the local guide, and an absent source guide must prevent writes.

**Exact fixture:** append the following to the disposable original `docs\faq.md`
after a blank line. The closing quote is the last byte of the file: **no final
newline**. Create `docs\review-fixture\guide.md` containing `# Real local guide`.

```markdown
[Guide][p06-eof]

[p06-eof]: review-fixture/guide.md "Title"
```

The exact append bytes used were:

```python
b'\n[Guide][p06-eof]\n\n[p06-eof]: review-fixture/guide.md "Title"'
```

**Actual output**, with disposable absolute paths abbreviated and only explanatory
post-success boilerplate omitted:

```text
python -B -S <source>\bin\li-adapter.py init --target <consumer> --client other
exit 0
Lintel kit ready: 387 managed files; vendored source; clients=other.

python -B -S <consumer>\.github\lintel\bin\li-adapter.py check --target <consumer>
exit 0
Lintel kit verified: 387 managed files; vendored source; clients=other; no live-host validation.

git -c core.autocrlf=true clone -q <consumer> <clone>
exit 0

python -B -S <clone>\.github\lintel\bin\li-adapter.py check --target <clone>
exit 0
Lintel kit verified: 387 managed files; vendored source; clients=other; no live-host validation.
```

The real source guide is absent from both installed bundles and their inventory.
The valid reference remains in FAQ. The local clone cannot obtain the guide from
the reviewer's original source, yet its check still succeeds.

Two discriminating real-process controls reproduced the same cause:

| Control | Actual result |
|---|---|
| Remove the guide from source, retain the no-newline FAQ, init a fresh target. | Incorrect exit 0; writes the 387-file kit rather than refusing missing source. |
| Restore the guide and append only one LF to FAQ. | Init and installed check exit 0 with 388 files; guide is now included. |

Direct scanner controls likewise select no destination for the titled EOF
definition, but select it after a final LF or when the title is absent.

**Root cause:** lines 454-456 parse the title and advance `separated`, but line 460
accepts this definition only if the destination ends at `line_end`, the remaining
line is blank, or `separated > line_end`. At EOF with a title,
`separated == line_end == len(text)`; the other alternatives are false because the
title lies after the destination. A valid used definition is never recorded.

**Required correction:** make valid EOF termination part of the existing reference
grammar, preserving title/escape validation and original source spans. Add the exact
EOF case and newline-only control to scanner and real-consumer regressions, including
absent-source pre-write refusal and installed/clone checks. Do not weaken missing-link
checks or require an author to remove a valid reference/title.

### P06-C05: exclude indented code inside a blockquote

**Expected semantics:** a blockquote marker consumes its optional following space;
the remaining four spaces introduce indented code. Link-shaped text in that code
is an example, not a bundle dependency. The ordinary guide link below it must
continue to work.

**Exact fixture**, appended to the original disposable `docs\faq.md`:

```markdown
>     [Code example](review-fixture/does-not-exist.md)

[Real guide](review-fixture/guide.md)
```

There are **five spaces after `>`**. Exact bytes, including the final LF:

```python
b'>     [Code example](review-fixture/does-not-exist.md)\n\n[Real guide](review-fixture/guide.md)\n'
```

Create the real `guide.md`; do not create the code-example target. Actual init:

```text
python -B -S <source>\bin\li-adapter.py init --target <consumer> --client other
exit 1
ERROR: Required source file is missing: <source>\docs\review-fixture\does-not-exist.md
```

The consumer sentinel and all prior bytes survive the refusal, so refusal atomicity
is preserved; choosing a dependency from code is the defect.

Two controls establish the mistaken selection without broadening scope:

| Control | Actual result |
|---|---|
| Add a harmless `does-not-exist.md` containing `# Code-only example, not a dependency` plus LF. | Init/check/local Git clone/clone check all exit 0 with 389 files. The code-only file is incorrectly inventoried and copied, with matching managed bytes in the clone. |
| Remove that file and remove only the `> ` prefix, leaving ordinary four-space indented code. | Init/check exit 0 with 388 files, include the real guide, and exclude the example. |

In the successful control, installed and clone checks each report:

```text
Lintel kit verified: 389 managed files; vendored source; clients=other; no live-host validation.
```

**Root cause:** `markdown_fence` at lines 368-375 removes quote/list container
prefixes for fenced-code recognition. Indented-code recognition instead computes
indentation from the original line at 392. A leading `>` gives zero indentation,
so lines 410-416 do not exclude the code and the inner bracket is later scanned
as a real link.

**Required correction:** recognize the container-relative indented-code boundary
while retaining exact original source spans and following real navigation. Add this
literal fixture, its unquoted control and real init/check/clone assertions. Do not
drop useful guide links or redefine valid code examples as unsupported prose.

## Per-leaf preservation and sequential gate

| Leaf | Specification disposition | Quality disposition |
|---|---|---|
| A06.1 | PASS retained. The unchanged registry/reader retain 38 distinct surfaces and conservative aliases; collapse/malformed-record negatives pass again. | NOT RUN |
| A06.2 | PASS retained. Vendor sources, shipped routes and observations round-trip separately; unknown remains unknown and no new live observation is claimed. | NOT RUN |
| A06.3 | PASS retained. Actual tool names, availability versus permission, native/serial/manual selection, attributable isolation and independent-review-pending semantics pass the rerun registry/consumer cases. | NOT RUN |
| A06.4 | PASS retained. Unsupported enablement/model/global options and missing controls fail explicitly; no fabricated `.disabled` or cross-host hook mechanism is added. | NOT RUN |
| A05.1 | PASS retained. Unchanged task-first onboarding remains; the repair preserves useful public navigation rather than dropping its content. | NOT RUN |
| A05.2 | FAIL on C04/C05. C01/C02/C03 close individually; the declared ordinary reference/code boundary still fails. Native Copilot/Claude route preservation does not cure this defect. | NOT RUN |
| A05.3 | PASS retained within assigned scope. Neutral defaults and optional specialist methods remain; no new private/company/retention/venture assumptions or copying. | NOT RUN |
| A05.4 | PASS retained for architectural/protocol agreement and explicit integration/live limits, not clearance of the failed navigation guarantees or final integrated truth. | NOT RUN |

The assigned welcome, cli-fingerprint, pair-agent, codex, careful and
instruction-parity-check workflows are unchanged by the parser repair. Their earlier
reviewed useful methods remain, including authorized ad-hoc Codex second opinions
without a duplicate evidence reader, invented P05 clearance or mandatory full-plan
ceremony. Native Copilot discovery and Claude plugin/agent/optional-hook paths remain.

**Stage 1 FAIL; first full quality NOT RUN.** Neither earlier independent report
performed that stage. This report does not relabel specification regression work as
quality. When a later authorized immutable candidate passes specification, the first
quality pass still must cover the complete bounded change from `40c2795`, not just
the parser repair.

## Checks actually run on 560e64ac

Host: Windows, Python 3.11.9 and Git Bash 5.3.15. Test runs used fake
HOME/USERPROFILE/XDG paths, isolated Git configuration, short disposable roots and
disabled bytecode/user-site loading. The approved task-local jq executable was
reverified at SHA256
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
only child-process PATH was amended. No dependency was installed.

| Command or scenario | Actual evidence |
|---|---|
| `python -B -S tests\unit\adapter-navigation.py` | 16 PASS, zero skips; includes 126 composed inline subcases, structured HTML/entities/source spans, code/comments/templates, symlink/path/private-source boundaries and LF/binary preservation. The 126 subcases do not cover C04/C05. |
| `python -B -S tests\unit\client-capabilities.py` | 16 PASS, zero skips; real CLI consumers, 38 surfaces, evidence layers, aliases, availability/permission and isolation/review negatives. |
| `python -B -S tests\integration\universal-adapters.py` | 12 PASS, zero skips; all 38 client selections, additive/shared-root installs, manual handoff, actual clone, C01/C02/C03, source failure, modified-guide refusal, inventory/ownership and fake-home boundaries. |
| `python -B -S tests\integration\copilot-kit.py` | 22 PASS, zero skips; native compatibility, resources, notices/protocol ownership, installed-source preference, idempotence, CRLF clones, collision/symlink and legacy preservation. |
| Additional immutable archive -> manual consumer -> local autocrlf Git clone -> clone's own check | C01 and all exact C02/C03 closures independently retained, with inventory, hashes and managed-byte assertions. |
| Additional exact C04/C05 consumer, clone, absent-source and one-change controls | Both deviations reproduced. Successful reproduction assertions are not passing product acceptance. |
| `python -B -S bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; same explicit approved work map. |
| `python -B -S bin\li-instructions.py check` | PASS, four synchronized entry files. |
| Disposable archive: instruction sync, catalog/wiki generation, Copilot local init, each check and CLI-table guard | PASS; 20-file repository-mode kit verified. No authored reducer was changed. |
| Disposable archive: `bash tests/unit/cli-tiers.sh` and `bash tests/unit/copilot-capabilities.sh` | PASS; unknown-ID warnings are intentional conservative fallback diagnostics, not suppressed support claims. |
| Repeat all four disposable generators | PASS; complete generated tree is byte-identical. |
| Python 3.9 grammar parse of eight changed implementation/focused-test files; full base-to-candidate `git diff --check` | PASS. Python 3.9 runtime itself was not run. |

All four primary suites exit 0: **66 test methods, zero skips**. A missing installed
FAQ or HTML resource still fails when its inventory entry is also removed. The unit
case verifies that an existing unmanaged stray file cannot substitute for the planned
bundle. Missing transitive source fails before writes, and modified managed guides
survive refused updates unchanged. Existing tested source-only/internal/private/runtime
boundaries remain: explicit upstream navigation is not a locally available resource
or pinned acceptance evidence.

The suite fake homes are empty except for the unchanged Copilot legacy scaffold
test's `.lintel\audit\migration.jsonl`, confined to its fake home as previously
reported. Independent navigation and regeneration fixtures leave fake homes empty.
Owned disposable fixture trees were cleaned.

Two reviewer-harness errors were corrected before the successful complete reruns:
the initial clone assertion compared unmanaged foundation bytes despite intentional
autocrlf conversion; it now compares all managed bytes and hashes. A regeneration
run's console encoding failed on an existing arrow character; the session-only
harness was set to UTF-8. Neither was a product finding. No product code was changed
to obtain the final results.

Session-local evidence: `p06-final-unit.log`, `p06-final-universal.log`,
`p06-final-copilot.log`, `p06-final-navigation-probes.log` and
`p06-final-regeneration.log`; reproduction/environment drivers remain alongside them.
The navigation log retains the initial incomplete harness attempt followed by its
successful full rerun. Exact finding inputs and decisive outputs are preserved above.

## Open gates and bounded handoff

Accepted limits remain remote URL availability, fragments, rendered layout and
arbitrary HTML/CSS/JavaScript execution. C04/C05 are ordinary static local syntax
inside the documented contract, not reasons to expand it into a Markdown crawler.

No new-module preflight, joined P04/P05/P07/P08 contract, strict full-suite, CI,
final integrated regeneration or independent integration-review gate closes here.
The historical P04 `02be6cb` composition and four real helper tests remain historical
evidence, not newly rerun or accepted joined input. P06 `profile_ref` transport is
not proof of end-to-end policy pinning or a fix for the separately reproduced P07
shell-reference policy-loss defect in old `912420f`.

No new live client/model/account behavior was run. The existing limited Copilot App
observation is not general host acceptance; generated native-format files prove
neither discovery, permission, isolation nor execution in any other host. No source
URL was fetched, and no private/enterprise control was tested.

MasterSession received C04/C05 and returned them to the original builder, requiring
a narrow boundary re-plan before further code after three specification iterations.
Preserve C01-C03, documented valid syntax and existing ownership/privacy checks;
do not weaken checks. The next repair/review checkpoint requires the coordinator's
explicit repair card and immutable candidate. This reviewer commits only this report,
sends its SHA, and remains read-only idle. No quality or further parser audit is
authorized by this handoff.
