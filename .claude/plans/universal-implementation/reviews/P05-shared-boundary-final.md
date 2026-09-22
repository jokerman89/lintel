# P05 shared-boundary independent review

**Date:** 2026-09-20. **Final owned specification verdict: FAIL.**
**Findings: 0 P1 / 1 P2 / 0 P3.**
**Quality: started after provisional specification PASS, then stopped on the
specification counterexample below; no completed quality approval.**
**Component acceptance and final joined acceptance: BLOCKED.**

This is the same independent reviewer as the three preceding P05 reports, not
the implementer or provider. No product, helper, test, plan, shared state or memory
was repaired. The only reviewer repository output is this report. Earlier report
branches remain at their original commits.

## Exact authority and reviewed revisions

| Role | Immutable reference |
|---|---|
| Original baseline | `40c279520a86945cc7e607692355bf5231446ff1` |
| Initial core | `7a7a50a1273ec4c04ed51118a9cfb2e3c85b246d` |
| First effective candidate | `9354fb174bd0398270989cd102de1c2906ef91a7` |
| Second product / frozen report | `54147fd5c6e3115c590bc3f47b5a9cdbb96a055f` / `e5b92a4fd2ac8c757a0370254ea73a2a76601038` |
| Third product / frozen report | `3adae4b0f14c341f0562a9c9ce35f0efe5f6fdb8` / `5a4933e1894557fff63faf5968a14df6eacf62f0` |
| Approved v2 decision / interface checkpoint | `c6736e56ac6d89da52c66016b4d4837d60dcddb1` / `da9d26fa29d93023efdc8b7c5aa29f6995ebd77b` |
| Approved narrow shared-boundary card | `7a892b4996f242cf4c51d3e460fff841ead2f885`, `packages/P05-P06-markdown-boundary.md` |
| Original dependency-only import | `3794f9c12293eea8ad5b42967efa4d6bb952deb4` |
| Current dependency-only retarget | `bd96a47704112284197c632b0197015dd26e9409` |
| Exact P06 provider | `74259605c1a172a444d1d4d2e838aea2b120ef92` |
| Current owned consumer | `fd63e6906d9a6ac0ec9ee42eeba548e7d7c3e6a2` |
| Effective frozen candidate; report-only child of consumer | `9c8ef727ba66a2ed574022143b4827cd83dca8b5` |
| Preserved first / second / third reviewer reports | `aef81d425a2ca36588a8b8ab01bc1a8321d9bc3d` / `d83ed02e46171d3ef2c87395dd0d7721f94651ef` / `85e8d908329bae18203dc2fa855436e982270afd` |

Authority includes repository/adapter instructions, ADR-0028, the initiative
specification, P05 card, the approved shared-boundary card and scoped audit
WF-01/02, AG-03/04/11/15, CP-08 and RU-01. The four owned consumer files are
`lib/review_contract.py`, `skills/review/references/evidence.md`,
`tests/unit/review-source-target.sh` and `tests/unit/review_evidence.py`.
The two dependency commits modify only `lib/markdown_source.py`; `9c8ef727`
modifies only the builder report.

The current helper's immutable Git bytes match the approved provider:
blob `0b3da55046358864fcd3075ba5bfb6c2348b1fec`, **19,988 bytes**, SHA-256
`331c1c62e932b5555089336d1fdcc7031f545780508f1d0f2e11bd9f2a7a8ebf`.
This verifies attribution and dependency identity, not separate P06 approval.
The rejected predecessor `09148b71cb57df0a5bb5cc21f3f1681d6715390e`
is not the effective dependency.

## Stages and full quality scope

The original S01-S04/R01 regressions and requested current literal/progress cases
passed the bounded suites and independent replays. On that evidence, owned Stage 1
was provisionally passed and the first full bounded quality review was started.
That review exposed Q01. **The provisional specification PASS is retracted**:
passing the original fixtures does not establish exact acceptance identity.
Stage 2 is therefore neither the old candidates' NOT-RUN state nor a completed
quality PASS; it was started and stopped with this one confirmed specification
blocker. No further broad audit or product repair followed.

The quality inspection covered the full original-base-to-consumer P05 surface,
not only the four repair files: the contract/schema, evidence CLI, shell writer
and reader; review, code-review, QA, QA-only, SHIP and compliance-gate skills;
the evidence reference; GDPRReviewer, EUAIActReviewer, ComplianceOfficer,
DependencyAuditor, SBOMAuditor, DesignSystemAuditor, CodeReviewer and TestRunner;
the optional hook and documentation; and the six focused test/bridge files.
These are 28 P05 product/documentation/test paths, plus necessary facts from the
separately owned shared helper. The builder report is evidence, not approval.

Inspection retained the distinction between GDPR Articles 33 and 34, ISO
27001:2022's 93 Annex A controls, current AI Act source/version/scope, actual
license use/distribution, mandatory accessibility observations and advisory
design scores. It checked latest-decision ordering, persisted audit verification,
source/target routing, exact-content rather than age-based reuse, read-only
QA/SHIP, and the optional unregistered warn-only hook. No additional
high-confidence finding is reported from that inspection. This is not a completed
quality approval or a new general Markdown/security/regulatory audit.

## P05-Q01: excerpt identity loses the classification that authorizes normalization

**Severity: P2. Confidence: high; reproduced through the real writer, reader,
QA and SHIP. Owner: P05 consumer.**

| Source | Relevant behavior |
|---|---|
| `lib/review_contract.py:490-495` | Classifies the complete source and temporarily normalizes eligible progress characters. |
| `lib/review_contract.py:514-522` | Slices the normalized excerpt and hashes only those bytes; surrounding container/classification facts are not bound. |
| `lib/review_contract.py:677-682` | Recomputes work and accepts equality, so the identity collision survives freshness verification. |

The approved requirement is not satisfied merely by calling the classifier on
the full file. The context that determines whether the selected text is a real
task or literal code must remain relevant to its identity. Otherwise an
out-of-excerpt wrapper can turn every selected task into a literal example while
the old review still clears.

Initial mapped `plan.md`, with selected excerpt start `# P1` and end `# End`:

```text
# P1
- [ ] A1 Required task
- [ ] A2 Required task
# End
```

After valid v2 review, audit persistence, corroboration and QA, prepend a
` ```markdown ` fence line and append its closing fence outside the excerpt.
Do not change any selected line. The provider correctly reports zero list items
and a fenced-code region instead of two ordinary task items. Nevertheless
`bind_work` returns the identical work object and the actual reader/QA/SHIP all
exit **0**, with reader and SHIP `ok: true`.

This is also a literal-byte collision, not only a rendering observation. Starting
with `[x] A1` in the real task, the reviewed canonical excerpt contains `[ ] A1`.
Enclose it in a fence or raw `<pre>` and change that now-literal character to a
space: the literal excerpt equals the earlier normalized bytes. The old context
and old QA still clear. Retaining literal `x` instead correctly blocks, showing
that the missing distinction is the normalization context, not reader bypass.

| Executed case | Work equality | Actual reader / QA / SHIP | Correct result |
|---|---|---|---|
| Initially unchecked tasks; add surrounding fence only | Same | `0 / 0 / 0`, SHIP true | Block changed task/literal context |
| Initially checked A1; add fence, retain literal `x` | Different | `3 / 1 / 3`, SHIP false | Block; negative control passes |
| Initially checked A1; add fence, now-literal state becomes space | Same | `0 / 0 / 0`, SHIP true | Block; false clearance |
| Initially checked A1; add raw `<pre>`, now-literal state becomes space | Same | `0 / 0 / 0`, SHIP true | Block; false clearance |
| No container change; genuine task `x` to `X` | Same | `0 / 0 / 0`, SHIP true | Reuse; preservation control passes |
| Select whole task file; add fence and change state to space | Different | Pure `bind_work` comparison only | Wrapper is detected; not claimed as a pipeline test |

In the four checked-state pipeline cases, the previously valid QA bytes were
restored before SHIP. Thus this is not an artifact of producing a new permissive
QA result. Exact package, both leaf IDs, accepted QA obligations, review,
corroboration, product selection and policy stayed unchanged. The independently
calculated initial excerpt SHA-256 matched the manifest.

The provider reports the correct fenced-code/raw-HTML facts in these fixtures.
This finding does not require a P06 parser repair, authenticated receipts, an
age limit, or a new mandatory test for docs-only work. It requires binding the
relevant interpretation used to authorize normalization while preserving genuine
progress and unrelated out-of-selection changes. Blanket hashing of all raw task
bookkeeping is not an acceptable substitute. Implementation/design ownership
remains with the coordinator and builder; the reviewer made no repair.

### Executable checked-state replay

Run this with `python -B -` and the pinned candidate as the working directory. It uses existing
fixture helpers only, isolated target repositories/homes and disabled global/system
Git configuration. The approved jq, if needed, must be on the process-local PATH.
The assertions below reproduce this candidate's observed behavior; their success
does **not** mean the two false-clearance cases satisfy the specification.

```python
import hashlib
import json
import os
import sys
from pathlib import Path

for key in list(os.environ):
    if key.startswith(("LINTEL_", "CLAUDE_", "GIT_")) or key == "GSTACK_HOME":
        os.environ.pop(key, None)
os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                  PYTHONDONTWRITEBYTECODE="1")
sys.path.insert(0, str(Path.cwd() / "tests" / "unit"))
from review_evidence import Fixture
from markdown_source import classify_markdown
from review_contract import bind_work

f = Fixture()
f.setUp()
try:
    before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
    path = f.repo / "plan.md"
    path.write_bytes(before.encode())
    f.request["acceptance_paths"] = [
        "spec.md", {"path": "plan.md", "start": "# P1", "end": "# End"},
    ]
    f.record()
    f.log()
    f.corroborate()
    assert f.qa().returncode == 0
    f.read()
    f.ship()
    old_qa = f.qa_file.read_bytes()
    work = f.expected["work"]
    canonical = "# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n"
    entry = next(x for x in work["acceptance_manifest"] if x["path"] == "plan.md")
    assert entry["sha256"] == hashlib.sha256(canonical.encode()).hexdigest()
    cases = [
        ("fence-retains-x", "```markdown\n" + before + "```\n", False),
        ("fence-literal-space",
         "```markdown\n" + before.replace("[x]", "[ ]") + "```\n", True),
        ("pre-literal-space",
         "<pre>\n" + before.replace("[x]", "[ ]") + "</pre>\n", True),
        ("genuine-progress", before.replace("[x]", "[X]"), True),
    ]
    for label, after, same in cases:
        path.write_bytes(after.encode())
        current = bind_work(
            f.repo, work_map=work["work_map"], package_id=work["package_id"],
            leaf_ids=work["leaf_ids"], acceptance_paths=work["acceptance_paths"],
        )
        assert (current == work) == same
        reader = f.read(ok=None)
        qa = f.qa()
        f.qa_file.write_bytes(old_qa)
        ship = f.ship(ok=None)
        codes = [reader.returncode, qa.returncode, ship.returncode]
        assert codes == ([0, 0, 0] if same else [3, 1, 3])
        source = classify_markdown(after)
        print(label, codes, json.loads(ship.stdout)["ok"],
              len(source.list_items), sorted({r.kind for r in source.regions}))
    path.write_bytes(before.encode())
    whole_before = bind_work(
        f.repo, work_map=work["work_map"], package_id=work["package_id"],
        leaf_ids=work["leaf_ids"], acceptance_paths=["spec.md", "plan.md"],
    )
    path.write_bytes(("```markdown\n" + before.replace("[x]", "[ ]") + "```\n").encode())
    whole_after = bind_work(
        f.repo, work_map=work["work_map"], package_id=work["package_id"],
        leaf_ids=work["leaf_ids"], acceptance_paths=["spec.md", "plan.md"],
    )
    assert whole_before != whole_after
finally:
    f.doCleanups()
```

The actual paired replay exited 0 and printed the four outcomes above; the
separate all-unchecked replay also exited 0 and printed the incorrect clearance.
No renderer/browser was run for these new fixtures. Literal interpretation is
the unambiguous enclosing Markdown fence/raw PRE and the provider's correct
full-source facts, not a claim of separately verified browser behavior.

## Previous findings and preservation

| Prior finding | Current disposition and evidence |
|---|---|
| S01 malformed latest decision revives old PASS | Closed for the reproduced direct, wrapped and full-context variants. Active validation precedes scope filtering; real reader/SHIP block malformed latest records. Valid unrelated package/map/skill decisions and explicitly imported history remain usable. Tests `review_evidence.py:573-769`. |
| S02 ordinary task completion invalidates acceptance | Genuine selected structural progress, including nested/excerpt marker changes, now reuses. Only the selected ASCII state character is eligible. This preservation fix is not permission for Q01's classification-changing reuse. |
| S03 invented mandatory tests for docs-only work | Closed for grounded mandatory document checks with tests N/A or no test obligation. Actual document assertions plus advisory failure cleared reader/QA/SHIP. Actual mandatory zero/fail/skip, N/A-only and advisory-only remain blocked. |
| S04 mandatory/advisory prose contradiction | Closed in the inspected QA/SHIP/compliance instructions. Configured/advisory controls are not automatically hard stops; applicable mandatory failure/error/unverified remains blocking. |
| R01 observation-defined QA obligations | Closed in bounded v2 cases: exact expected IDs/kinds/requirement/applicability/policy, typed review consistency, required coverage, omission/downgrade/retype/reclassification/policy change/duplicates and forged QA rejection. Tests `review_evidence.py:979-1098`. |
| R02 indented/compound/raw literal normalization | The old specific reproductions are repaired, including compound fences and PRE. The broader exact-identity requirement remains open through Q01: full-source interpretation is used but not bound for excerpts. |

Current independent byte-oracle replays supplemented the passing suite:

| Fixture | Mutation and observed reader / QA / SHIP |
|---|---|
| Compound `- -` fence containing selected-ID checkbox | Literal state change blocked: `3 / 1 / 3` |
| Raw `<pre>` example containing selected-ID checkbox | Literal state change blocked: `3 / 1 / 3` |
| `Paragraph\n2. [ ] A1 continuation` | Changed literal continuation blocked: `3 / 1 / 3` |
| `Paragraph\n\n2. [ ] A1 progress` | Genuine ordered-list progress reused: `0 / 0 / 0` |
| `Paragraph\n1. [ ] A1 progress` | Genuine interrupting ordered-list progress reused: `0 / 0 / 0` |
| Excerpt already inside an outer list fence | Literal mutation blocked: `3 / 1 / 3` |
| Excerpt inside a genuine nested list; start marker includes the task | Task/start-marker progress reused: `0 / 0 / 0` |
| Raw PRE with Unicode and CRLF | Literal mutation blocked: `3 / 1 / 3` |

These eight cases used manually expected source bytes, not classifier-generated
hash oracles, and restored stale QA before SHIP. They preserve the original
repair evidence but do not cover Q01's transition into a literal container.

Two additional independent docs-only pipelines executed real Python assertions
against the document heading and a local link target before recording the
mandatory document observation. One accepted grounded tests N/A plus a failed
advisory control; the other declared no test obligation and retained the failed
advice. Both returned reader/QA/SHIP **0/0/0**. The first also compared selected
product bytes and Git status before/after QA, reader and SHIP: unchanged.
Document checks actually ran; corroboration/control receipts remained synthetic
fixtures, not authenticated host or human testimony.

## Per-leaf results

| Leaf | Current bounded verdict |
|---|---|
| A02.1 | PASS: strict result/status/applicability/mandatory-advisory shapes; malformed/duplicate/non-finite input rejected. V2 review/context/QA obligations are immutable; unchanged control/profile/corroboration/work-map versions are not silently migrated. |
| A02.2 | PASS: applicable mandatory failure/error/unverified blocks independently of advisory count or score; valid advisory failures remain visible and nonblocking. |
| A02.3 | PASS in scope: policy source/version/applicability and regulatory scope remain explicit; normal-text 3.5:1 is not AA pass; corrected narrow role guidance retained. No legal certification inferred. |
| A02.4 | PASS: zero-run actual mandatory tests, missing browser and unresolved required policy stay nonclearing. Docs-only applicability is not replaced by invented tests. |
| A03.1 | PASS: exact enums, complete nonempty bindings, decision validation before filtering, latest applicable append ordering, later negative/error revocation and fresh-v2 recovery. |
| A03.2 | FAIL: ordinary selected base/head/index/worktree/new/deleted/config/docs/evidence identities pass; Q01 loses relevant excerpt interpretation and admits stale acceptance. |
| A03.3 | Shared-gate/provenance cases PASS; overall acceptance withheld. Actual writer/reader/QA/SHIP share the same context and therefore also share Q01. Declared actor strings/digests are not authentication. |
| A03.4 | FAIL: plain criteria/docs/config/new-file changes and later rejections block, but Q01's changed task/literal context falsely retains clearance. |
| A03.5 | Valid unchanged/unrelated/progress reuse cases PASS. Q01 is invalid additional reuse, not justification to remove useful exact-content reuse. |
| A03.2.s1 | PASS: one exact shared provider, no remaining local P05 block parser, no helper authorship or extra external dependency. |
| A03.2.s2 | PARTIAL/FAIL: selected one-character eligibility and original-offset excerpt handling pass existing cases, but the facts authorizing normalization disappear from excerpt identity. |
| A03.2.s3 | FAIL: original literal/criteria/approval/product mutations block and real nested progress reuses; Q01 transition fixtures still clear. |
| A03.2.s4 | BLOCKED: independent specification reopened as FAIL; first full bounded quality review started, not approved. |

Historical raw inspection, valid unrelated scopes, explicit selection exclusions,
unmapped ad-hoc inspections with `release_clearance: false`, source/target roots,
actual audit-persistence errors and read-only same-context QA/SHIP were retained
in the passing bounded coverage. Direct `verify` checks the supplied artifact;
only the log-backed reader/SHIP establishes latest-decision precedence. An old
direct artifact check is not a substitute for that gate.

## Commands, actual evidence and limits

All current checks ran from the separate pinned reviewer worktree using synthetic
fixture targets/homes. No full repository suite, network, private profile, global
configuration mutation, real PR, push, deploy or optional-hook registration ran.

| Check actually run | Observation |
|---|---|
| `bash tests/unit/review-evidence.sh`; `bash tests/unit/mandatory-controls.sh`; `bash tests/integration/no-merge-without-review.sh` | Combined reviewer driver `p05-shared-tests` completed exit 0. Independent source inventory is 81 evidence + 12 controls + 2 hook methods. Completion retrieval did not retain a per-method transcript; no reviewer elapsed time is claimed. |
| `bash tests/unit/review-source-target.sh` | Exit 0; 9.188 s. Installed source and target-owned audit behavior retained. |
| `bash tests/shape/audit-writes-via-helper.sh` | Exit 0; 11.266 s. |
| `bash tests/shape/skill-descriptions-trigger.sh` | Exit 0; 8.218 s. |
| `bash tests/shape/agents-categorized.sh` | Exit 0; 12.172 s. |
| `bash tests/shape/claude-home-paths.sh` | Exit 0; 4.453 s. |
| `bash -n` on the seven changed shell files | All passed: both adapters, hook, three unit shell entrypoints and hook integration entrypoint. |
| Independent eight-case byte/pipeline replay, `p05-shared-independent` | Exit 0; exact positive/negative outcomes recorded above. |
| Actual document-check pipelines, `p05-shared-docs` | Exit 0; both valid docs/advisory cases and the first read-only comparison passed. |
| New excerpt-context replay, `p05-excerpt-context` | Exit 0 confirms the all-unchecked false clearance; not a specification pass. |
| Paired new replay, `p05-excerpt-context-pairs` | Exit 0 confirms both checked-to-literal false clearances, two pipeline controls and the pure whole-file comparison. |
| Embedded report replay, `p05-report-replay` | Executed verbatim with `python -B`, the hash-checked approved jq and isolated fixtures; exit 0 reproduced the reported negative/positive outputs exactly. The two false clearances remain RED specification evidence. |
| API/AST/immutable-byte probe | Public signatures unchanged from `3ada` to `fd63`; only retained function with changed AST is `bind_work`. `_task_acceptance` and `_task_progress_pattern` removed; `_task_progress_spans` added. Schema, evidence CLI and both shell adapters byte-identical across that repair. Exact helper blob/length/SHA verified. |
| Python 3.9 grammar check on contract, classifier, CLI, evidence tests and profile bridge | Passed under Python 3.11.9. This is not live Python 3.9 execution. |
| `git diff --check 40c2795... fd63e690...` | Passed. |

The builder's 81-method/864.564-second claim is separate implementer evidence,
not the reviewer's timing or sufficient acceptance. Two initial metadata-probe
mistakes (wrong bridge filename and incomplete removed-helper expectation) were
corrected; neither is a product finding. The correct bridge file is
`tests/unit/review_profile_bridge.py`.

The focused-check driver exited 1 only during removal of its empty temporary
HOME, after every check above had passed. The exact empty directory
`p05-quality-home-7pwsve8g` remained Windows-locked on bounded retries. No broad
cleanup or process termination was attempted. Other fixture cleanup completed.
Disabling global Git configuration exposed 37 CRLF-only checkout differences:
`--ignore-cr-at-eol` and raw byte comparison confirmed no source edits, and
per-command `core.autocrlf=true` status was clean before this report. No
normalization, reset or source rewrite was performed.

The approved jq binary was checked against SHA-256
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
its use was process-local, with no install or global PATH change. Runtime was
Python 3.11.9 / Git 2.53.0.windows.4 / Git Bash 5.3.15. Windows symlink coverage
may use Git-object fallback where actual link creation is unavailable. No
performance-scale, live-browser, legal-policy authenticity or live Python 3.9
claim is made.

## Dependency and final integration gates

P06's exact provider is attributable and classifies the new Q01 fixtures
correctly. The coordinator acknowledged this finding and confirmed that accepted
provider `74259605` remains unchanged. This report does not reopen or substitute
for P06's own review; neither the helper hash nor these P05 tests supplies that
separate approval. The defect and required repair are in the P05 consumer.

P07 evidence levels remain distinct. At `912420f91729f1618b8f22804ea7ccd95bd7f6e8`
three Python bridge cases passed while the public saved-reference shell lost
required policy. Coordinator/builder evidence at
`d02bb248b61dbbc703eb5252f5b46d86bdfc102b` passed four saved-reference cases.
The previous reviewer pass independently ran those four cases against archived
`56981edc4bd73020fea78e20526b10d62e822305` in 50.348 s. No new bridge execution
is claimed for this fourth checkpoint. None establishes ordinary bootstrap,
host-enforcement approval, P07 independent acceptance or final joined acceptance.
The historical P07 producer defect is not assigned to P05.

Bound review/context/QA remain v2 under the approved decision; work-map/profile/
corroboration retain their existing versions. Older strict v1/error records
remain ordered and nonclearing, fresh valid v2 can recover, and later bad
decisions revoke. Two actor strings and a digest do not authenticate independence.
A separately supplied host/human receipt is caller-trusted provenance, not a
security boundary.

**Next authorized action:** return Q01 to the original P05 owner/coordinator for
the relevant binding decision and an immutable repair checkpoint. The reviewer
stops with this report, without product/helper edits or an unrelated audit.
P05 component approval is withheld; P04/P06/P07/P08/P14 final joined acceptance
remains open regardless of the passing bounded controls.
