# P05 excerpt-context final independent review

## Verdict and immutable scope

**Stage 1, complete owned specification re-review: PASS.**
**Stage 2, first whole bounded P05 quality review: PASS, now completed.**
Current owned-product findings: **0 P1 / 0 P2 / 0 P3** in each stage.
Q01 is closed on this candidate, not waived. This is component acceptance, not
acceptance of the reconciled initiative, an installed client, or a release.

The earlier specification pass was provisional and explicitly reopened as FAIL
in `0cdbf5962d52a0d8d5e82ac3316209140a5a597d`. The first whole quality review
then STARTED/STOPPED; it was not completed or approved. This continuation first
completed the specification re-review, then resumed and finished that whole
quality review. It does not retroactively approve an earlier candidate or reduce
quality scope to the small Q01 diff.

| Identity | Exact value |
|---|---|
| Original base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Original core implementation | `7a7a50a1273ec4c04ed51118a9cfb2e3c85b246d` |
| Original effective candidate | `9354fb174bd0398270989cd102de1c2906ef91a7` |
| Previous shared-boundary consumer | `fd63e6906d9a6ac0ec9ee42eeba548e7d7c3e6a2` |
| Previous frozen candidate / current product parent | `9c8ef727ba66a2ed574022143b4827cd83dca8b5` |
| Reviewed Q01 product | `b023e8c25a922ffc536ffde6dd911865bf2eea21` |
| Effective report-only candidate / this report's parent | `ec90b609423418ee4136f9fe425dfada11a08fae` |
| Exact prior rejection | `0cdbf5962d52a0d8d5e82ac3316209140a5a597d` |
| Dependency-only import | `bd96a47704112284197c632b0197015dd26e9409` |
| Exact P06 provider | `74259605c1a172a444d1d4d2e838aea2b120ef92` |
| Provider file | `lib\markdown_source.py` |
| Provider Git blob | `0b3da55046358864fcd3075ba5bfb6c2348b1fec` |
| Provider immutable size | 19,988 bytes |
| Provider SHA-256 | `331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf` |
| Separately supplied P06 acceptance | `1067da29cf1a0d91a25254c08a633736e70a2b74` |

Ancestry, the three product paths, the report-only child, and provider equality
were checked against local immutable Git objects. Q01 changes only
`lib\review_contract.py`, `skills\review\references\evidence.md`, and
`tests\unit\review_evidence.py`; the child changes only `reports\P05.md`.
AST comparison identifies `bind_work` as the only changed production function,
with its signature unchanged. The schema, CLI, shell adapters, other production
functions and public output/version domains are unchanged by Q01.

Authority is the selected `work.json`, original A02.1-A02.4/A03.1-A03.5,
`spec.md`, `packages\P05.md`, ADR-0028, the approved shared-boundary card
`7a892b4` at `packages\P05-P06-markdown-boundary.md`, and exact coordinator
`0ecdb520ddbfc628cc049860608484866986e3b9` for the appended Q01 refinement
and A03.2.e1-e3. The coordinator artifacts were read through `git show`; the
isolated task map was not rewritten. The v2 format authority remains decision
`c6736e56ac6d89da52c66016b4d4837d60dcddb1` and interface checkpoint
`da9d26fa29d93023efdc8b7c5aa29f6995ebd77b`.
Scoped audit backreferences remain WF01/02, AG03/04/11/15, CP08 and RU01.

This is the same independent reviewer, not the implementer. No nested agents,
product fixes, provider edits, shared-state/memory/plan edits, or unrelated audit
were performed. The only repository output of this continuation is this report.
The implementation report's Q01 section, commands, log identities, migration and
retracted self-confidence were inspected, not accepted as independent evidence.

## Stage 1: original and refinement leaves

PASS below is bounded to the owned component and the executed/static evidence.
It does not imply the live or joined acceptance listed at the end of this report.

| Leaf | Stage 1 | Stage 2 | Actual evidence and preserved constraint |
|---|---|---|---|
| A02.1 | PASS | PASS | Shared control/schema definitions and strict JSON validation; retained malformed, duplicate, non-finite and enum/ID cases. V2 expected QA inventory is distinct from observations. |
| A02.2 | PASS | PASS | Mandatory unknown/error/failure dominates scores; 12 control methods and real QA/SHIP mutation probes. Failed advisory remains visible without becoming a blocker. |
| A02.3 | PASS | PASS | Narrow regulatory/source/applicability and DesignSystemAuditor corrections inspected; contrast/regulatory/license fixtures pass. No legal certification or live legal-source verification inferred. |
| A02.4 | PASS | PASS | Mandatory zero/failed/skipped runs, absent browser evidence and unknown required policy block. Actual docs-only mandatory checks pass with grounded tests N/A or genuinely no test obligation. N/A-only/advisory-only does not replace an actual required gate. |
| A03.1 | PASS | PASS | Direct/wrapped/full-context validation precedes filtering; ordered malformed/v1/error/rejection candidates cannot revive old PASS. Valid unrelated scope/history and fresh-valid recovery remain usable. Independent direct-verify/latest-reader/QA/SHIP probe returned `0/3/0/3`. |
| A03.2 | PASS | PASS | Selected base/result, staged/dirty/untracked/deleted/config/doc identities, work-map/package/all-leaf coverage, exclusions and acceptance tested in the 91-method suite. Q01's selected interpretation is now bound. |
| A03.2.s1 | PASS | PASS | Exact unchanged shared provider; full source classified once; no P05 block parser. AST and provider blob/byte comparisons pass. |
| A03.2.s2 | PASS | PASS | Only positively classified selected-ID task markers authorize one ASCII state-character normalization. Excerpts use original full-source positions; relative identity and end permission are verified by fixed byte oracles. |
| A03.2.s3 | PASS | PASS | Retained root/tab/list-indented/fenced/compound/raw PRE/comment/quote/opaque/unknown, criterion/ID/approval/product negatives and real nested-progress positives. C06 paragraph-plus-ordered-2 literal blocks; blank-line-2 and interrupting-1 real progress reuse. |
| A03.2.s4 | PASS | PASS | Complete independent owned spec passed before completing this first whole quality review. Previous provisional pass/reopening and incomplete quality remain recorded. |
| A03.2.e1 | PASS | PASS | Exact original whole-source/excerpt transitions replayed through real preparation, writer, reader, QA and SHIP; old QA restored before SHIP. Four context-change negatives give `3/1/3`; genuine progress gives `0/0/0`. |
| A03.2.e2 | PASS | PASS | Exact domain prefix, sorted compact ASCII JSON, independently specified numeric offsets and hashes, explicit empty/null, and exclusive-end permission verified. No absolute offsets, local IDs, parent-byte hashing workaround or other-domain changes. |
| A03.2.e3 | PASS | PASS | Reverse and end-only permission transitions reject; Unicode/CRLF real progress, unrelated prefix/suffix/commit reuse pass. Old byte-only receipts remain history, require fresh preparation/review/corroboration/QA, and cannot silently upgrade. |
| A03.3 | PASS | PASS | Immutable v2 QA IDs/kind/requirement/applicability/policy and typed review consistency retained; producer and SHIP reject forged QA. Same-context gates are read-only. Corroboration is caller-trusted provenance, not authenticated independence. |
| A03.4 | PASS | PASS | Acceptance/config/new-file/evidence/later-rejection invalidation retained; Q01 adds the previously missed context transitions. Real latest-log and stale-context gates reject. |
| A03.5 | PASS | PASS | Unchanged relevant content, ordinary selected task progress and unrelated commits reuse evidence. Changed criteria/literals/approval/raw selected product bytes still invalidate; no age-window substitute. |

### Previous findings and closures

| Prior item | Current disposition | Supporting boundary |
|---|---|---|
| S01, malformed later decision revived old PASS | Closed, retained | `bin\li-review-evidence.py:60-114`; `lib\review_contract.py:637-686`. Actual reader/SHIP and ordered recovery tests pass, including validation before apparent skill/scope exclusion. |
| S02, completion-only acceptance invalidation | Closed, retained with Q01 refinement | `lib\review_contract.py:426-445,488-532`. Selected actual progress is normalized; genuine `x -> X`, nested/Unicode/CRLF and end-marker progress reuse pass. Literal state characters and actual criteria remain bound. |
| S03, invented docs-only mandatory tests | Closed, retained | `lib\review_contract.py:773-817` and accepted v2 inventory. Two fresh actual document-check pipelines clear; no observed-result-defined exemption is accepted. |
| S04, advisory/mandatory prose contradiction | Closed, retained | Owned QA/QA-only/SHIP/compliance/review instructions inspected against shared mandatory/advisory behavior; real failed-advisory docs checks clear while actual mandatory negatives remain blocked. |
| R01, observation-defined QA obligations | Closed, retained | `lib\review_contract.py:540-583,584-636,773-817`. Omission, retyping, downgrade, reclassification and policy change reject at both actual producer and SHIP consumer. |
| R02, literal examples normalized as task progress | Closed for approved owned boundary, retained | Shared provider plus `lib\review_contract.py:426-445,488-532`; all 35 prior boundary methods retained, with the exact C06 and literal/progress controls. Provider acceptance is separate. |
| Q01, selected-excerpt interpretation omitted from identity | Closed on `b023e8c` | `lib\review_contract.py:517-531`; exact independent negative/positive pipelines and fixed preimages below. Earlier consumer had a confirmed P2; this report does not erase that result. |

There are no current actionable P1/P2/P3 product findings to assign new
file:line/expected/actual/confidence entries. The Q01 closure has high confidence
within the explicit contract: unchanged normalized text with changed permission
must invalidate; it now does in the real consumer chain. This is not a proof of
unbounded Markdown conformance or caller honesty.

## Q01 exact replay and independent identity oracles

These are the same whole-source/excerpt inputs as the prior rejection, not
detached-slice parser tests. The selected references were:

```python
acceptance_paths = [
    "spec.md",
    {"path": "plan.md", "start": "# P1", "end": "# End"},
]
space = "# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n# End\n"
checked = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
cases = [
    ("all-space-fence", space, "```markdown\n" + space + "```\n"),
    ("fence-retains-literal-x", checked, "```markdown\n" + checked + "```\n"),
    ("fence-literal-space", checked,
     "```markdown\n" + checked.replace("[x]", "[ ]") + "```\n"),
    ("raw-pre-literal-space", checked,
     "<pre>\n" + checked.replace("[x]", "[ ]") + "</pre>\n"),
    ("genuine-progress", checked, checked.replace("[x]", "[X]")),
]
```

For each transition the independent fixture used the candidate's actual
preparation, `li-review-log`, `li-review-read`, QA and SHIP, initially proving
valid clearance. It saved the original valid QA bytes, changed the source,
ran reader and QA, restored those saved QA bytes, and then ran SHIP. Thus a
failed QA producer did not merely destroy the evidence that SHIP would inspect.
The existing `Fixture` pipeline in the immutable prior report's executable
replay was retained; the expected identity/exit oracle was corrected for Q01.

Exit triples below are **reader / QA / SHIP**, not three mocked assertions:

| Whole-source transition | Prior actual `fd63` / `9c8` result | Current independently observed result |
|---|---|---|
| All-space structural tasks enclosed in outside fence | Incorrect same work; `0/0/0` | Different work; `3/1/3`; reader/SHIP false |
| Fence retains now-literal x | Different work; `3/1/3` | Different work; `3/1/3`; retained negative |
| Fence plus literal-space collision | Incorrect same work; `0/0/0` | Different work; `3/1/3`; reader/SHIP false |
| Raw PRE plus literal-space collision | Incorrect same work; `0/0/0` | Different work; `3/1/3`; reader/SHIP false |
| Genuine structural x becomes X | Same work; `0/0/0` | Same work; `0/0/0`; retained positive |

The prior results are this reviewer's immutable rejection evidence, not a new
RED run at this checkpoint or copied builder timing. The current corrected run
also observed reverse literal-to-structural refusal, end-delimiter-only permission
changes in both directions, and legitimate end-marker progress. Negative QA
returns exit 1 with empty stdout and explicit stderr:

```text
li-review-evidence: Selected work/acceptance sources changed
```

Reader/SHIP return exit 3, `ok:false`, `status:"error"` and that problem.
The initial independent logging mistake described below was treating that empty
error stdout as JSON; it was not a missing product diagnostic.

### Exact hash bytes, not a production-generated oracle

The independently specified structural preimage is this byte literal:

```python
structural = (
    b'lintel:task-excerpt\x00'
    b'{"end_progress_span":null,"progress_spans":[[8,9],[31,32]],'
    b'"text":"# P1\\n- [ ] A1 Required task\\n- [ ] A2 Required task\\n"}'
)
literal = (
    b'lintel:task-excerpt\x00'
    b'{"end_progress_span":null,"progress_spans":[],'
    b'"text":"# P1\\n- [ ] A1 Required task\\n- [ ] A2 Required task\\n"}'
)
```

The prefix ends in exactly one zero byte. The rest is sorted-key JSON with
compact separators, ASCII escapes and no non-finite values. The numeric pairs
are half-open Unicode-codepoint offsets relative to the excerpt start, manually
specified rather than obtained from the production classifier. Empty permission
and null end permission are identity, not omitted defaults.

| Independently specified bytes | Observed SHA-256 |
|---|---|
| Structural preimage above | `fad53adafe277f79b3e39d91f96babb4e8a5c86cb436cf8dcc0df5b91887b5be` |
| Same normalized text, literal empty-permission preimage | `ad86dab228bb73105687431d48a7841060cb7f6c04e4d27e090d1d07d33cfe10` |
| Historical normalized-text-only bytes | `b6c7679535ffc6074358dbf63a351a239b3dc9b2b3b16583b28e48c11fed2463` |

For an exclusive end-marker-only transition:

```python
source = "# P1\nRequired criterion.\n- [ ] A1 Boundary\n"
start, end = "# P1", "- [ ] A1 Boundary"
preimage = (
    b'lintel:task-excerpt\x00'
    b'{"end_progress_span":[28,29],"progress_spans":[],'
    b'"text":"# P1\\nRequired criterion.\\n"}'
)
```

The structural hash is
`0acb98d121bf1897408e231c61d75838fb92b8155da33f8fecd8a5fd4887dc0f`.
Replacing only end permission with null produces
`165b6fb95621112b082ded7a20341cfc015cd806021a312b3d05ae03a0898010`.
Both direction changes returned `3/1/3`; genuine end progress returned `0/0/0`.
This permission must participate even though the end marker's text is excluded:
it authorizes normalization used to match the selected delimiter.

For nested Unicode/CRLF, the full source and excerpt start were:

```python
source = "- Parent\r\n    - [x] A1 \u03bb \U0001f600 task\r\n    - [ ] A2 Required task\r\n# End"
start, end = "    - [x] A1 \u03bb \U0001f600 task", "# End"
preimage = (
    b'lintel:task-excerpt\x00'
    b'{"end_progress_span":null,"progress_spans":[[7,8],[30,31]],'
    b'"text":"    - [ ] A1 \\u03bb \\ud83d\\ude00 task\\r\\n'
    b'    - [ ] A2 Required task\\r\\n"}'
)
```

The fixed SHA-256 is
`e77cc696cfe928c5722800dffd889329a16b2219ec21037fd49d9aaa63b01157`.
Real progress plus unrelated prefix reuse returned `0/0/0`. Changing a selected
criterion or converting the selected CRLF bytes to LF returned `3/1/3`.
Unrelated prefix/suffix edits and a later unrelated commit also retained
`0/0/0`. A separate independent check retained the original whole-task normalized
byte hash and non-task excerpt hash domains.

### Migration and history

The old byte-only v2 receipt remained structurally valid and visible in raw
`--json` history. Direct verification returned 3; reader/QA/SHIP returned
`3/1/3`. Fresh preparation alone did not clear it. Fresh review without new
corroboration remained blocked; fresh review/corroboration with old QA remained
blocked; fresh QA completed recovery. The old history lines remained byte-preserved.
There was no digest rewrite, guessed obligation insertion, or acceptance of
both hashes. Strict v1 history/error ordering and newer-v2 recovery were separately
retained in the 91-method suite.

## Stage 2: first whole bounded quality review

The reviewed owned range is **`40c279520a86945cc7e607692355bf5231446ff1` through
`b023e8c25a922ffc536ffde6dd911865bf2eea21`**, including the effective original
`9354` shell regression and docs change, every intervening owned repair and Q01.
It covers these 28 owned source/document/test surfaces, plus the necessary exact
provider interface/position facts:

| Area | Owned files reviewed |
|---|---|
| Contract/schema | `lib\review_contract.py`; `lib\review-schema.json` |
| CLI/shell | `bin\li-review-evidence.py`; `bin\li-review-log`; `bin\li-review-read` |
| Six workflows | `skills\review\SKILL.md`; `skills\code-review\SKILL.md`; `skills\qa\SKILL.md`; `skills\qa-only\SKILL.md`; `skills\ship\SKILL.md`; `skills\compliance-gate\SKILL.md` |
| Usage contract | `skills\review\references\evidence.md` |
| Eight roles | `agents\compliance\GDPRReviewer.md`; `agents\compliance\EUAIActReviewer.md`; `agents\security\ComplianceOfficer.md`; `agents\security\DependencyAuditor.md`; `agents\security\SBOMAuditor.md`; `agents\frontend\DesignSystemAuditor.md`; `agents\engineering\CodeReviewer.md`; `agents\engineering\TestRunner.md` |
| Optional hook | `hooks\shared\no-merge-without-review\run.sh`; `hooks\shared\no-merge-without-review\HOOK.md` |
| Six focused test/bridge files | `tests\unit\review-evidence.sh`; `tests\unit\mandatory-controls.sh`; `tests\unit\review_evidence.py`; `tests\unit\review-source-target.sh`; `tests\unit\review_profile_bridge.py`; `tests\integration\no-merge-without-review.sh` |

Acceptance selection, immutable obligations, history/migration, producer-consumer
agreement and read-only consumption were inspected end to end, rather than
inferring quality from green original tests. Relevant conclusions:

- The new preimage is localized to mapped-task excerpts. Classification still
  precedes slicing, and only approved source spans authorize normalization.
  Binding eligible relative positions solves the collision without hashing
  unrelated parent bytes, adding a local parser, or changing the provider.
- Review validation precedes active decision filtering. A malformed apparent
  other-scope entry cannot disappear to resurrect old PASS; validated unrelated
  scopes and explicitly imported history remain useful. A later valid applicable
  decision can recover without rewriting earlier errors.
- Direct artifact verification is deliberately different from latest-log
  clearance. With an old valid artifact and a later same-context rejection,
  independent direct verify / latest reader / current QA / SHIP returned
  **`0/3/0/3`**. QA success alone did not overrule the latest review.
- In the independent immutable-QA probe, omission, tests-to-check retyping,
  mandatory-to-advisory downgrade, applicability reclassification and policy
  version change each returned **QA 1 / SHIP 3**, including manually forged QA
  with rebound evidence. Restoring legitimate QA recovered. Requirements came
  from the expected v2 context, not incoming observations or control-name heuristics.
- Useful unmapped inspection/history does not require an invented full plan and
  cannot confer release clearance. Actual docs-only validation does not invent
  tests; real mandatory test zero/failure/skip cases remain blocked. Policy
  requirements and advisory outcomes stay separate.
- Writer/persistence and error paths, read-only reader/QA/SHIP, installed source
  versus target roots, and the actual engineering-review legacy-history snippet
  were inspected and exercised. Source-root lookup does not silently take a
  conflicting current-directory helper or target implementation.
- The narrow role changes retain their specialist purpose: GDPR Article 33
  authority notification versus Article 34 subject communication; ISO 27001:2022
  Annex A's 93 controls and scope/SoA; AI Act source/version/date/actor/territory;
  license obligations based on actual use/distribution; measured contrast and
  missing-browser limitations. Scores do not override applicable mandatory gates.
- The optional hook remains warn-only, uses the real reader, and is not registered
  or activated by this review. Two passing hook methods are not host enforcement.

### Actual docs-only QA and SHIP observations

Two independent fixtures selected `spec.md` and `guide.md` and actually executed:

```python
from pathlib import Path
text = Path("spec.md").read_text(encoding="utf-8")
assert text.startswith("# Acceptance\n")
assert "[Guide](guide.md)" in text
assert Path("guide.md").is_file()
print("document heading and link: PASS")
```

Both returned exit 0 and `document heading and link: PASS`. Accepted QA contained
mandatory `document-check` / `kind:check` / `applicability:applicable` / `status:pass`,
its command/exit/evidence, and a failed **advisory** `optional-style`.
One context also declared `tests` as grounded not-applicable, with policy and
reason explaining the selected Markdown-only scope; the other had no test
obligation. Neither declaration came from later observations.

Actual reader/QA/SHIP returned **`0/0/0`** for each. SHIP returned `ok:true`,
`status:"pass"` and exposed the failed advice without blocking. Internal aggregate
control status could still say `fail` because the advice failed; the explicit
`blocked:false` and mandatory results determine clearance. Product/audit file
hashes excluding `.git`, and Git status, were unchanged across these gates.
These were synthetic receipt fixtures, not actual host/human attestations.

## Commands, actual evidence and non-green attempts

All executions were local, bounded and hermetic, with synthetic homes, profiles
and repositories. Python was **3.11.9**, Git **2.53.0.windows.4**, Git Bash
**5.3.15**. The approved jq 1.8.2 binary's SHA-256 was reverified as
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
only per-process PATH was used. Inherited Lintel/Claude/Git/GSTACK settings were
scrubbed, global/system Git config disabled, and bytecode writing disabled.
No actual private/global configuration or logs were read.

The commands below ran from the pinned continuation worktree; Bash received the
explicit script paths. The inline independent Python runners imported the
unchanged repository `Fixture`, supplied their own fixtures/oracles, and called
the actual CLI/shell surfaces. They were not edits to the product test suite.

| Reviewer execution | Actual outcome |
|---|---|
| Initial `python -B -` inline independent runner | **ERROR**: 13 methods, 0 assertion failures, 8 logging errors, 0 skips; unittest 191.842 s. Preserved, not counted as a passing run. |
| Corrected `python -B -` inline `ExactReplay` runner | **PASS**: 9 methods, 0 failures/errors/skips; unittest 143.946 s; cleanup included. Fixed-byte oracles, exact Q01 negatives, reverse/end-only/Unicode/CRLF and migration. |
| `bash tests\unit\review-evidence.sh` | **PASS**: one 91-method run, 1148.052 s unittest / 1148.547 s wrapper; exit 0, zero skips. All 81 prior plus 10 Q01 methods retained. |
| `bash tests\unit\mandatory-controls.sh` | **PASS**: 12 methods, 35.346 s unittest / 35.844 s wrapper; exit 0, zero skips. |
| `bash tests\integration\no-merge-without-review.sh` | **PASS**: 2 methods, 15.511 s unittest / 15.922 s wrapper; exit 0, zero skips. |
| Retained-suite driver and cleanup | **PASS**: aggregate exit 0; `cleanup_error:null`, no remaining fixture root. |
| `python -B -` inline `WholeQuality` runner | **PASS**: 7 methods, 79.953 s, zero failures/errors/skips; cleanup included, exit 0. Latest-log semantics, five QA mutations, two actual docs pipelines, progress/unrelated-commit/domain preservation. |
| `bash tests\unit\review-source-target.sh` | Body **PASS**: all 3 assertions, exit 0, 11.047 s. |
| Four shape scripts under `tests\shape`: `audit-writes-via-helper.sh`, `skill-descriptions-trigger.sh`, `agents-categorized.sh`, `claude-home-paths.sh` | Bodies **PASS**, all exit 0; respectively 13.000, 12.406, 19.797, 6.781 s. No inline shell audit writers found across 73 inspected files; 69 agent metadata entries retained. |
| `bash -n` for writer, reader, optional hook, evidence/control/source-target wrappers and hook test | Seven scoped syntax commands, all exit 0. |
| `git -c core.autocrlf=true diff --check 40c279520a86945cc7e607692355bf5231446ff1 b023e8c25a922ffc536ffde6dd911865bf2eea21` | Body PASS, exit 0. |
| Source-target/shapes/syntax/diff driver cleanup | **ERROR, aggregate exit 1** despite all preceding body exits 0; Windows WinError 32 on the exact empty synthetic home described below. |
| Python `ast.parse(..., feature_version=(3,9))`, bounded AST/signature/API/test-inventory and immutable identity comparison | PASS, exit 0. Five Python files parse; only `bind_work` production AST changes; all 95 prior evidence/control/hook methods retained, ten new ones. **Not Python 3.9 runtime evidence.** |
| Read-only worktree byte/EOL, old-ref and provider identity verification | PASS, exit 0; no actual content dirt or normalization. Details below. |

The eight initial errors were the reviewer's `json.loads(qa.stdout)` logging
attempt after a correctly rejected stale context produced empty stdout. The
corrected runner preserves stdout/stderr verbatim. No product change was made
to obtain the subsequent passes; the initial failed aggregate remains evidence.

The separate source-target/shapes wrapper could not remove
`%TEMP%\p05-ec90-shapes-7__nxn_t\home` because Windows held it open.
A read-only inspection found only the empty ordinary `home` directory in that
exact synthetic root. A bounded, nonrecursive cleanup retry also exited 1 with
WinError 32. It is **unresolved environment cleanup**, not a green aggregate and
not an observed product defect. No process was killed, broad cleanup attempted,
or actual user data removed. The successful evidence/control/hook and independent
runners had their own successful cleanup; this limitation does not change their
recorded results.

Builder figures (including 1208.492 s for 91 methods and 52.691 s / 12 failures
for the five-method RED run) are builder evidence inspected in `reports\P05.md`,
not timings or runs attributed to this reviewer.

### Durable reviewer logs

These artifacts are retained in session
`6ed9c7df-4845-4d70-88c7-f0746ab28059`, under `files\`, not committed as
product/test changes. Structured companion JSON preserves wrapper exits and
cleanup state.

| Artifact | SHA-256 |
|---|---|
| `P05-ec90-independent-pipelines.log` | `70a4d5b6025787b3b2cf4f65aa7eb2edfeab56c0a002aaf137bece2634b6a3d2` |
| `P05-ec90-independent-corrected.log` | `2199b95e2ac551e76c6b86644c9bcc3e4e83f4c2d8d7bde31f4e597391afd714` |
| `P05-ec90-retained-suites.log` | `4676b33fa22b9f94b0c73846ebd105df9703d417d57f974741a7b999de3266e9` |
| `P05-ec90-quality-pipelines.log` | `1febb5aa2b1eeba269fcc69f38783a0d75832102268df28e7e72003818a3f646` |
| `P05-ec90-source-target-shapes.log` | `0a39a3fea3de4f8e91315920d3719689ce2a873ea6e16fd00f4f51a6bfd1dc53` |
| `P05-ec90-identity-api.json` | `385320a563223e94ef5bc2e71fce7abc9c84a9e2ab50c09d831102e1e9f888dd` |
| `P05-ec90-clean-identity.json` | `916f2d1e35b34eead45020195ff03d887b46d2956a8070966cdc776c94ce03a2` |

## Preservation, dependency and final integration gate

The continuation branch/worktree is `jokerman-microsoft-p05-excerpt-review`,
pinned at exact `ec90b609` before this report. Before writing, default Git status
under the isolated config reported 588 CRLF-only differences. Every reported
tracked path was compared read-only with its immutable Git bytes: **zero actual
content differences**. Checkout-equivalent
`git -c core.autocrlf=true status --porcelain` was empty. No file/index EOL
normalization, reset, discard, amendment, or source-test weakening was performed.
The report is the only intended staged/committed path; its exact commit SHA and
post-commit parent/status verification are supplied with the handoff.

These old branches and immutable report heads were verified preserved:

| Branch | Preserved head |
|---|---|
| `jokerman-microsoft-universal-evidence-review` | `aef81d425a2ca36588a8b8ab01bc1a8321d9bc3d` |
| `jokerman-microsoft-universal-evidence-recheck` | `d83ed02e46171d3ef2c87395dd0d7721f94651ef` |
| `jokerman-microsoft-universal-evidence-final` | `85e8d908329bae18203dc2fa855436e982270afd` |
| `jokerman-microsoft-universal-evidence-shared-boundary` | `0cdbf5962d52a0d8d5e82ac3316209140a5a597d` |

Provider blob, immutable size and SHA-256 match at `74259605`, `bd96a477`,
`b023e8c` and the effective candidate. P06's separately accepted provider was
not repaired, reopened or reapproved here. Its accepted facts are necessary
inputs to this P05 consumer review, not a substitute for correct consumption.

No new P07 source was imported and no new P07 bridge was run in this continuation.
Keep evidence levels separate: old `912420f` had three Python bridge passes but
its public saved-reference shell path lost required policy; `d02bb248` has the
reported four-case saved-reference pass; this reviewer previously ran the four
saved-reference cases against archived `56981edc` in 50.348 s. None proves ordinary
bootstrap, current P07 long-path repair acceptance, or host enforcement. Those
producer defects and pending work are not relabeled as P05 findings or waived.

Synthetic actor strings, digests and supplied host/human receipts bind declared
provenance but do not authenticate independence. Actual caller identity,
enterprise policy enforcement, legal certification, a live browser/client/model,
full CommonMark/rendering conformance, Linux/macOS and live Python 3.9 execution
are not claimed. No full repository suite, network/GitHub/private-profile/global
actions, real PR/deployment/publication, paid model call or hook activation ran.

**Final integration remains OPEN:** P04/P06/P07/P08/P10/P14 joins,
mandatory-source preflight, regenerated/installed consumer dependency closure,
and reconciled integrated strict acceptance still need their owners' evidence
and final independent review. This report completes the bounded owned P05
specification and first whole quality review only. It is not a merge/release
authorization, and the original builder retains ownership of any later repair.
