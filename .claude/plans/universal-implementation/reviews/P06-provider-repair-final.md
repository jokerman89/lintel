# P06 provider repair and complete component review

**Date:** 2026-09-20.
**Reviewer:** independent P06 review session; not the implementation actor.
**Candidate:** `74259605c1a172a444d1d4d2e838aea2b120ef92`.
**Candidate tree:** `3085a0513e15b20ed3a166f16e8446724ba7208c`.
**Whole-component baseline:** `40c279520a86945cc7e607692355bf5231446ff1`.
**Rejected provider baseline:** `09148b71cb57df0a5bb5cc21f3f1681d6715390e`.
**Stage 1, complete owned specification:** PASS.
**Stage 2, first complete bounded component quality review:** PASS.
**Scope:** P06 and its authorized shared provider, not P05 consumer clearance,
integrated-branch acceptance, release approval or live-client certification.

## Authority and review sequence

The selected work map is
`.claude/plans/universal-implementation/work.json`; its mapped specification,
plan, original task IDs and P06 package remain authoritative.
The approved refinements are:

- `e76ed6c56e26a4d66590d6a0ca4c4456d18513ac`,
  `packages/P06-markdown-repair.md`: one logical EOF/container/span model,
  preservation of C01-C05 and actual consumer checks before quality review.
- `7a892b4996f242cf4c51d3e460fff841ead2f885`,
  `packages/P05-P06-markdown-boundary.md`: one stateless provider, the exact
  immutable API and original-source coordinates, sole P06 provider ownership
  and a separately reviewed P05 consumer.
- The coordinator's bounded C06/C07 repair authorization: repair paragraph
  interruption and multiline inline-code precedence without changing API
  fields, task-normalization policy, private boundaries or another package.

C06/C07 and retained closures were verified first. Only after the full owned
specification passed did this reviewer perform the first quality review of the
complete `40c2795..7425960` component, not merely the latest five-path checkpoint
(four product/test files and its implementer report).
The component comparison contains 43 paths, including its implementer report.
No implementation, shared reducer, plan state or other package was changed.

Earlier failures remain historical evidence, not retroactively passing reviews:

| Review commit | Artifact under `reviews/` | Historical outcome |
|---|---|---|
| `dbe5d3953322d02db118ff4b87af3a28aafbc3e7` | `P06-component.md` | C01; specification failed |
| `3e8abb997b2e495efe3dcea4374f43880f20b5b7` | `P06-recheck.md` | C02/C03; specification failed |
| `6b874c78dc3fa54e818013d1b3cc340e93253abc` | `P06-final.md` | C04/C05; specification failed |
| `96fdcc4a34f51a2e2e042b01506948d7fe6be90c` | `P06-shared-boundary-final.md` | C06/C07 on `09148b7`; specification failed |

Those reviews did not establish a prior whole-component quality pass.

## Owned leaf decisions

The quality column records the subsequent Stage 2 pass; it was not used to
waive Stage 1. These are component decisions, not shared-plan checkbox edits.

| Leaf | Stage 1 | Stage 2 | Evidence and boundary |
|---|---|---|---|
| A06.1 | PASS | PASS | Registry and validator retain 38 distinct surface records, explicit aliases and a manual fallback. Malformed records/session declarations fail; desktop, IDE and cloud are not collapsed into a vendor boolean. |
| A06.2 | PASS | PASS | Official source conditions, delivered bindings and observations remain separate. Missing claims/observations expand to unknown/not_run. Partial historical Copilot App observations retain missing version/revision limitations rather than acquiring this review's identity. |
| A06.3 | PASS | PASS | Real CLI consumers select a differently named question binding, serial/manual paths and attributable isolation. Permission denial/uncertainty remains blocking; a selected native binding is not execution or independent-review evidence. |
| A06.4 | PASS | PASS | Unsupported model/plugin controls stay unsupported. Unknown clients and invented control options refuse before writes. No enablement marker, global setting, hook activation or paid client invocation is introduced. |
| A05.1 | PASS | PASS | README and start/enterprise guides lead with the common planning, build, review and resume value before selecting a client. The source-local manual entry remains usable. |
| A05.2 | PASS | PASS | Retained Copilot kit and Claude routes, documented native-format roots, manual fallbacks and source-relative resources survive actual installation and local Git clones. C01-C07 closure and shared-provider proof are detailed below. This is not live discovery certification. |
| A05.3 | PASS | PASS | Owned public entry points and six assigned skills avoid imposing company, contact, vendor, retention or venture defaults. Optional expertise remains optional; actual project/pack authority still applies. |
| A05.4 | PASS | PASS | Canonical operation adapter, architecture and entry prose distinguish delivered files from host permission and observation. Four session-protocol blocks agree. Coordinator-owned generated outputs were exercised only in disposable regeneration. |

| Refinement | Stage 1 | Stage 2 | Evidence and preservation |
|---|---|---|---|
| A05.2.m1 | PASS | PASS | Exact C04/C05 RED evidence remains in immutable `6b874c78`; this pass retains those failures as historical baselines, not newly passing results. |
| A05.2.m2 | PASS | PASS | Original-source logical line/container/span facts handle EOF and line terminators without input mutation. |
| A05.2.m3 | PASS | PASS | Reference, inline and code-exclusion consumers share the provider's source boundaries. |
| A05.2.m4 | PASS | PASS | Manually expected EOF/title/container/code grids preserve destinations and spans. |
| A05.2.m5 | PASS | PASS | Current actual init/check/clone tests cover missing/present/code-only resources, drift/refusal, binary/text and private boundaries. |
| A05.2.m6 | PASS | PASS | C01-C03 and focused navigation/registry/Universal/Copilot/disposable generator cases remain green. |
| A05.2.m7 | PASS | PASS | Same independent reviewer closes the repair and then performs this first complete bounded quality pass. |
| A05.2.s1 | PASS | PASS | Independently expected Unicode/CRLF/structural/literal span matrices, including exact C06/C07 and positive controls. |
| A05.2.s2 | PASS | PASS | One immutable, stateless stdlib provider; no task policy, normalization or replacement parser. |
| A05.2.s3 | PASS | PASS | Real generator and installed copies consume exact provider bytes; absence refuses before writes without target-module substitution. |
| A05.2.s4 | PASS | PASS | C01-C05 and all original owned leaves preserved before the complete quality verdict. |

P05's A03.2.s* normalization, excerpt identity, reader, corroboration and
QA/SHIP behavior have not been reviewed by this report.

## C06: actual item occurrences

The exact rejected source now yields no list-item occurrence:

```python
"Paragraph\n2. [ ] A05.2 ordinary continuation\n"
```

The following independently expected controls remain genuine occurrences.
These spans are half-open Unicode-codepoint coordinates, not byte offsets:

| Source | Expected marker span | Expected content span |
|---|---|---|
| `"Paragraph\n\n2. [ ] A05.2 real item\n"` | `(11, 13)` | `(14, 33)` |
| `"Paragraph\n1. [ ] A05.2 real item\n"` | `(10, 12)` | `(13, 32)` |
| `"1. First\n2. [ ] second\n"` | `(0, 2)`, `(9, 11)` | `(3, 8)`, `(12, 22)` |

The review exercised these facts through the provider from an actual installed
consumer's fresh autocrlf Git clone, not only a source import. The expanded
repository grid also covers ordered delimiters/numbers, quote/list contexts,
blank-line starts, siblings and LF/CRLF.

**C06: CLOSED on `7425960`.** The provider does not claim the ordinary ordered
paragraph continuation is positively eligible structural task content.
Relevant implementation anchors are `lib/markdown_source.py:127` (paragraph
interruption), `:154` (container continuation) and `:193` (paragraph lookahead).

## C07: multiline inline code before HTML discovery

The exact rejected source is:

```python
'`<script src="review-fixture/code-only.js">\n</script>`\n\n[Real](review-fixture/guide.md)\n'
```

The expected inline-code region is `(0, 54)`; no opening HTML tag/resource
inside that region is selected. The sole literal navigation destination is
`review-fixture/guide.md`, at `(63, 86)`.

Independent actual-source/consumer checks established:

1. With the code-only JavaScript absent, source `init`, installed `check`,
   repeated idempotent `init` and fresh local autocrlf Git-clone `check` pass.
2. Creating that JavaScript in the source still does not copy it or put it in
   the managed inventory. The real guide remains mandatory and is bundled.
3. The same-line inline-code control behaves identically.
4. Omitting the real guide refuses before writes. Removing the installed guide
   and its inventory entry still fails, rather than hiding incomplete closure.
5. Removing only the backticks restores a real script opening-`src` dependency:
   absent source refuses before writes; present source is bundled and survives
   installed checks and a fresh clone.

**C07: CLOSED on `7425960`.** Literal source examples and real HTML resource
attributes are distinguished without suppressing the real guide or raw HTML
opening attributes.
Relevant entry points are `lib/markdown_source.py:290` and `:310`, and the
consumer navigation view at `bin/li-copilot.py:311`.

Representative actual consumer results, with temporary paths shortened:

```text
Source init --client other / exit 0:
Lintel kit ready: 389 managed files; vendored source; clients=other.
Installed check, including fresh autocrlf clone / exit 0:
Lintel kit verified: 389 managed files; vendored source; clients=other; no live-host validation.
Real guide omitted / exit 1:
ERROR: Required source file is missing: <fixture>\s\docs\review-fixture\guide.md
Real un-backticked HTML, JavaScript omitted / exit 1:
ERROR: Required source file is missing: <fixture>\s\docs\review-fixture\code-only.js
```

The first init line is shortened after its source/client summary; its original
output also directs the operator to review the managed inventory/foundation.
The passing HTML control contains 390 managed files, including the real script.

## Shared provider and retained C01-C05

The candidate's `lib/markdown_source.py` is 19,988 bytes:

- Git blob: `0b3da55046358864fcd3075ba5bfb6c2348b1fec`.
- SHA-256: `331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf`.

Actual installed copies and their managed hashes match those trusted bytes.
The provider has the declared immutable result fields, preserves the complete
original Unicode input, uses exact LF/CRLF/EOF and tab-aware coordinates and
contains no file, task-ID, normalization, profile or clearance operations.
The tests independently assert structural markers and literal-region spans;
they do not derive expected eligibility from the same classifier.

Same-line PRE/CODE/SCRIPT/STYLE bodies, comments, compound list fences, quoted
and indented examples, opaque/unknown spans and full-source-before-excerpt
semantics remain covered. A `prose` item start does not erase a later literal
span. Actual installed-source tests prove missing-provider refusal before
writes and no replacement-provider execution from the target/PYTHONPATH.

| Earlier finding | Current disposition and actual coverage |
|---|---|
| C01, incomplete portable navigation | CLOSED. README/public transitive resources and notices remain reachable in installed sources and fresh clones. Missing targets and drift fail; unmanaged target files do not substitute for bundle inventory. |
| C02, HTML resource parsing | CLOSED. Opening script `src`, quoted `>` and exact attribute/entity spans survive; bodies/comments/code are not executed or treated as navigation. |
| C03, Markdown destination parsing | CLOSED. Escaped opening brackets remain literal; escaped punctuation in destinations, balanced/wrapped labels and reference forms retain their expected resources. |
| C04, titled reference at EOF | CLOSED. Real installed/clone tests and the independently enumerated EOF/LF/CRLF/title grid retain the guide; omission/removal remains a failure. |
| C05, container-relative indented code | CLOSED. Residual quote/list/tab indentation keeps code-only links out, including when those source files exist; real in-container/after-container guides remain required. |

Private/hidden/source-only boundaries, sentinel bytes, non-copied personal
configuration and binary versus normalized text assets remain preserved.
External source links are explicitly labelled navigation to public `main`,
not pinned acceptance evidence or a reason to read private local records.

## Stage 2: first complete bounded quality pass

**Result: PASS. Open findings: P1 = 0, P2 = 0, P3 = 0.**

The full component review covered registry validation and resolution, the
shell/CLI compatibility consumers, the shared provider and navigation
integration, managed installation/update/refusal behavior, six assigned
skills, adapter/entry/public documentation and focused tests.

The provider owns source-boundary facts once; navigation retains destination
parsing and path policy rather than moving task semantics into the provider.
The Universal entry reuses the existing ownership engine instead of maintaining
a second installer. Errors remain explicit, and collision/dependency checks
precede target writes. Tests exercise generated and installed consumers,
positive controls, negative preflights, byte preservation and local clones,
not just source strings or mocks.

The six assigned skills retain their useful methods: welcome, CLI fingerprint,
outside opinion, paired review, cautious operation and instruction parity.
In particular, `skills/codex/SKILL.md` retains ad-hoc inspection without inventing
a work map or requiring a new planning ceremony. It references the single
shared evidence API, explicitly withholds release clearance for inspection and
does not implement a competing reader. Pending P05 helpers/consumer acceptance
remain a disclosed dependency, not clearance supplied by this prose review.

No actionable component finding was identified in the authorized diff.
This bounded static-source review is not a full CommonMark renderer audit,
an arbitrary web crawler audit or a guarantee of unknown host behavior.
Remote URL availability and heading-fragment resolution were not tested;
the documentation leaves those outside its static local-source claim.

## Checks actually run on this candidate

| Check | Result |
|---|---|
| `tests/unit/markdown-source.py` | 15 tests PASS |
| `tests/unit/adapter-navigation.py` | 29 tests PASS |
| `tests/unit/client-capabilities.py` | 16 tests PASS |
| `tests/integration/universal-adapters.py` | 17 tests PASS, including actual installed-source and Git-clone cases |
| `tests/integration/copilot-kit.py` | 22 tests PASS; existing native kit, ownership, source bootstrap and portable Swarm resources preserved |
| Reviewer-authored source-fact probes | 12 tests PASS, including exact C06/C07 and independent positive/negative spans |
| Reviewer-authored actual consumer probes | PASS for absent/present code-only resources, same-line control, required-guide omission/removal, real HTML control, idempotence and autocrlf clones |
| Work-map validator | PASS; explicit map resolves APPROVED mapped artifacts |
| Instruction check and disposable sync/check | PASS; four canonical protocol blocks |
| Disposable catalog and wiki generation/check | PASS |
| Disposable native adapter init/check | PASS |
| CLI-table synchronization after disposable regeneration | PASS |
| `tests/unit/cli-tiers.sh`, `tests/unit/copilot-capabilities.sh` | PASS |
| Second disposable generation | Byte-idempotent |
| Python 3.9 grammar check | PASS; actual execution runtime was Python 3.11.9, not Python 3.9 |
| `git diff --check 40c2795 7425960` | PASS |

The five repository Python suites total 99 tests, with no skipped cases.
They ran with Python `-B -S` and isolated fixture homes. The Copilot suite
created only its expected fixture `.lintel/audit/migration.jsonl`; the other
reported fake homes remained empty. Disposable fixture trees were cleaned.
Raw commands/results remain in this review session's `files/` artifacts:
`p06-provider-{unit,facts,consumers,universal,copilot,regeneration}.log`.
No product or coordinator-owned generated file was rewritten to obtain a pass.

The separate historical P06 + P04 `02be6cb` installed-source composition and
its four helper runs were subset evidence, not acceptance of that rejected P04
checkpoint. They do not replace current fan-in checks. Likewise, transporting
`profile_ref` through P06 is not evidence that P07 pins policy end to end.

## Remaining gates and handoff

This report permits the coordinator to treat this exact P06/provider
checkpoint as independently component-reviewed. It does not clear:

- P05's actual selected-leaf, single-character normalization, full-source
  excerpt identity, clearance-reader and QA/SHIP consumer behavior.
- Joined P04/P05/P07/P08 integration, current mandatory-resource preflights,
  stable profile/resume semantics or actual cross-component handoff behavior.
- Coordinator-owned root reducers, catalog/wiki/native adapter/README-table
  regeneration and checks on the reconciled integration branch.
- The integrated strict suite, final independent integrated review,
  configured enterprise/pack compliance and human/release approval.
- A24 live client/version discovery, tool execution, browser, model and
  fresh-session resume evidence. Source research and these fixtures do not
  promote any host to fully observed support.

No new clients/dependencies, private/global configuration, network requests,
paid/authenticated model runs, nested reviewers, release actions or external
publication were used for this review. The only repository write for this
review is this versioned report. The coordinator owns subsequent integration
and may supply this exact reviewed provider to its separately gated consumer.
