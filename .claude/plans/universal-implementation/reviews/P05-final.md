# P05 third-candidate independent review

**Date:** 2026-09-20.
**Original base:** `40c279520a86945cc7e607692355bf5231446ff1`.
**Original core:** `7a7a50a1273ec4c04ed51118a9cfb2e3c85b246d`.
**First candidate/report:** `9354fb174bd0398270989cd102de1c2906ef91a7` /
`aef81d425a2ca36588a8b8ab01bc1a8321d9bc3d`.
**Second product/candidate/report:** `54147fd5c6e3115c590bc3f47b5a9cdbb96a055f` /
`e5b92a4fd2ac8c757a0370254ea73a2a76601038` /
`d83ed02e46171d3ef2c87395dd0d7721f94651ef`.
**Current product:** `3adae4b0f14c341f0562a9c9ce35f0efe5f6fdb8`, directly atop `e5b92a4`.
**Effective candidate:** `5a4933e1894557fff63faf5968a14df6eacf62f0`;
the only subsequent change to `3adae4b` is the builder report.
**Reviewer:** same independent session `c8e62d27-4511-4af6-a0af-16e4dcd3c3bc`,
not an implementation author.

**Stage 1 - specification: FAIL.** R01 is closed; R02's literal-preservation
invariant remains open in two reproducible forms. Remaining findings:
**0 P1, 1 P2, 0 P3**.
**Stage 2 - full bounded P05 quality: NOT RUN**, still gated on specification.
**Final integrated acceptance/delivery: BLOCKED.**
The report filename is not a claim of final approval.

## Authority, isolation and scope

Read the coordinator's explicit v2 decision at
`c6736e56ac6d89da52c66016b4d4837d60dcddb1` and producer/consumer interface at
`da9d26fa29d93023efdc8b7c5aa29f6995ebd77b`,
`.claude\plans\universal-implementation\interfaces.md`, alongside the existing
P05 specification, package, ADR-0028 and original findings.

The authorized semantic change requires immutable `qa_requirements` with exact
ID/kind/requirement/applicability/policy. Bound context/review/QA use v2;
profile, work-map, corroboration and standalone control results keep v1.
Old strict v1 is non-clearing, not silently rewritten. A newer valid applicable
v2 review can supersede old insufficient/error evidence; a later bad or rejecting
candidate revokes clearance. Valid unrelated decisions and explicit history
retain their distinct meanings.

Created a new clean worktree/branch `jokerman-microsoft-universal-evidence-final`
at exact `5a4933e`. The earlier review branches remain at `aef81d4` and `d83ed02`.
No builder/coordinator/source worktree was reset. Only this report is written
and committed by this pass; candidate product and shared state remain unchanged.

Read the complete third-product delta across `lib\review_contract.py`,
`lib\review-schema.json`, `bin\li-review-evidence.py`, `bin\li-review-log`,
`skills\code-review\SKILL.md`, `skills\qa-only\SKILL.md`,
`skills\review\SKILL.md`, `skills\review\references\evidence.md`,
`skills\ship\SKILL.md` and `tests\unit\review_evidence.py`, plus the separate
builder report. Rechecked the shared contract against the authorized interface.
No unrelated subsystem audit or product repair was performed.

## Previous finding dispositions

| Finding | Disposition on this candidate |
|---|---|
| S01: malformed later decision revives old PASS | CLOSED. Direct/wrapped/full-context malformed records cannot disappear through skill/scope filtering. Expanded order tests also preserve newer-valid recovery rather than permanently poisoning history. |
| S02: normal completion invalidates unchanged acceptance | Original failure CLOSED. Selected real task progress, including tested nested unordered/ordered/tab lists and excerpt markers, reuses evidence. R02 still prevents acceptance of the overall normalization boundary. |
| S03: genuine documentation-only QA invents tests | CLOSED. Mandatory document validation with grounded tests N/A, or genuinely no test obligation, is usable. Accepted N/A-only/advisory-only inventories do not establish QA. |
| S04: advisory controls become mandatory in SHIP prose | CLOSED for the owned contradiction. Current QA/SHIP/shared instructions retain applicable mandatory stops and distinct advisory findings. |
| R01: observations omit/reclassify/retype QA obligations | CLOSED. Immutable v2 inventory and typed review consistency reject omissions, downgrade, retype, new N/A, changed policy, duplicates and extras at both producer and forged-receipt SHIP consumer. |
| R02: literal examples normalized as progress | PARTIALLY FIXED, still OPEN. Original root/tab/list-indented and single-list-fenced examples now bind. Compound-list fences and preformatted literal blocks still lose checkbox bytes (finding below). |

## Remaining finding

### P05-R02 - P2: literal code still loses acceptance identity in additional valid Markdown forms

**Locations:** `lib\review_contract.py:458-478,480-484`.
**Confidence:** 10/10.
**Requirements:** A03.2/A03.4/A03.5; normalize only real selected mapped-task
progress, retaining literal examples/criteria.

The parser recognizes only one list marker per line when looking for a fence;
its block-state detection also does not recognize HTML preformatted blocks.
It consequently normalizes these selected literal checkboxes as task progress:

| Case | Literal example in the mapped tasks file |
|---|---|
| Compound list fence | A line `- - ```markdown`, then four spaces followed by `- [ ] A1 literal`, then a four-space-indented closing triple-backtick fence. |
| Preformatted block | `<pre>`, a line `- [ ] A1 literal`, then `</pre>`. |

The exact fixtures select a `# P1` through `# End` acceptance excerpt of
`plan.md`, which is the mapped tasks source and is not product-selected. The
excerpt also contains unchanged actual A1/A2 task rows. After an actual passing
writer/reader/QA/SHIP round trip, change only the literal example's `[ ]` to `[x]`.
Both cases retain the old acceptance identity and return **reader exit 0,
SHIP exit 0, `ok: true`**. No accepted task status, requirement, actor or product
input was changed.

Confirmed the interpretation locally with PowerShell's built-in
`ConvertFrom-Markdown`, without installing a parser or fetching content.
The compound-list case renders nested lists containing:

```html
<pre><code class="language-markdown">- [ ] A1 literal
</code></pre>
```

The second remains a `<pre>` literal block. These are literal examples, not real
task progress. This is the same R02 preservation defect, not two independent
findings or a new requirement to grant new capabilities.

**Required correction:** distinguish actual task-progress nodes from literal
content in the supported Markdown authority. Handle compound container prefixes
and preformatted blocks without relaxing changed-criterion checks or banning
genuine nested tasks. Add these actual reader/SHIP negatives alongside the
passing nested-progress and literal preservation cases. Do not blanket-exclude
task documents or repair review evidence by changing an old digest.

The third specification candidate still fails this boundary. Return the remaining
normalization work to the coordinator/original builder for a bounded repair plan;
the reviewer does not repair it or proceed to quality review.

### Executable remaining-finding replay

Run from this exact candidate's worktree root in PowerShell. The test creates
and cleans only synthetic fixture repositories/homes:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
@'
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path.cwd() / "tests" / "unit"))
from review_evidence import Fixture
from review_contract import bind_work

cases = [
    ("compound-list-fenced",
     "- - ```markdown\n    - [ ] A1 literal\n    ```\n",
     "    - [ ] A1 literal", "    - [x] A1 literal"),
    ("preformatted",
     "# Example\n\n<pre>\n- [ ] A1 literal\n</pre>\n",
     "- [ ] A1 literal", "- [x] A1 literal"),
]
for label, example, before, after in cases:
    f = Fixture()
    f.setUp()
    try:
        original = ("# P1\n- [ ] A1 Actual task\n- [ ] A2 Actual task\n\n"
                    + example + "\n# End\n")
        f.write("plan.md", original)
        f.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# End"},
        ]
        f.record()
        f.log()
        f.corroborate()
        assert f.qa().returncode == 0
        f.read()
        f.ship()
        f.write("plan.md", original.replace(before, after))
        work = f.expected["work"]
        now = bind_work(f.repo, **{key: work[key] for key in (
            "work_map", "package_id", "leaf_ids", "acceptance_paths",
        )})
        read = f.read(ok=None)
        ship = f.ship(ok=None)
        print(json.dumps({
            "case": label,
            "same_acceptance": now["acceptance_digest"] == work["acceptance_digest"],
            "reader_exit": read.returncode, "ship_exit": ship.returncode,
            "ship_ok": json.loads(ship.stdout)["ok"],
        }))
    finally:
        f.doCleanups()
'@ | python -
```

Both observed outputs have `same_acceptance: true`, `reader_exit: 0`,
`ship_exit: 0`, `ship_ok: true`. Correct behavior is to invalidate the old review
for the changed literal, while retaining genuine task-progress reuse.

Ran this exact replay against both preserved earlier product worktrees as well:

| Product (review-only commit on top) | Both literal variants |
|---|---|
| `9354fb1` (`aef81d4`) | Acceptance digest changes; reader 3 / SHIP 3 / false. |
| `54147fd` (`d83ed02`, via report-only `e5b92a4`) | Acceptance digest unchanged; reader 0 / SHIP 0 / true. |
| `3adae4b` (`5a4933e`) | Acceptance digest unchanged; reader 0 / SHIP 0 / true. |

Thus these variants persist from the original normalization repair; they are
not attributed to the separately approved v2 QA/ordering changes.

## Checks actually run

Windows, Python 3.11.9, Git 2.53.0.windows.4 and Git Bash 5.3.15.
Bytecode disabled; fixture repos/homes and supplemental shell HOME/Git
configuration were isolated. Commands used resolved script paths.

| Check | Actual outcome |
|---|---|
| `bash tests\unit\review-evidence.sh` | PASS: 46 tests, 519.194 seconds. |
| `bash tests\unit\mandatory-controls.sh` | PASS: 12 tests, 37.242 seconds. |
| `bash tests\integration\no-merge-without-review.sh` | PASS: 2 tests, 13.816 seconds; merge strings are data, never executed. |
| `bash tests\unit\review-source-target.sh` | PASS: three source/target/history scenarios. |
| `bash tests\shape\audit-writes-via-helper.sh` | PASS. |
| `bash tests\shape\skill-descriptions-trigger.sh` | PASS. |
| `bash tests\shape\agents-categorized.sh` | PASS. |
| `bash tests\shape\claude-home-paths.sh` | PASS. |
| Independent seven-case QA obligation replay | Valid declared tests/document inventory passes; omit/downgrade/retype/reclassify/policy/duplicate/extra each returns QA 1 and forged-QA SHIP 3 / false. |
| Independent accepted-inventory QA preservation | Accepted N/A-only and advisory-only inventories return QA 1 / SHIP 3; mandatory docs plus declared failing advice with no test obligation returns QA 0 / SHIP 0. |
| Independent literal-code replay | Root-indent, tab-indent, list-indent and single-list fence each block reader/SHIP (3); the two R02 forms incorrectly clear (0). |
| Identical two-case replay across earlier products | Original `9354` blocks both; second `54147` and current `3ada` both retain the false-clearance. Preserved reviewer branches were not changed. |
| `ConvertFrom-Markdown` on both R02 examples | Confirmed literal rendering using the existing local renderer. |
| Independent ten-scenario version/order replay | Strict v1 alone blocks; old v1/error followed by current applicable v2 clears; later v1/error revokes; unrelated valid result does not erase a blocker; new applicable v2 restores after it; explicit valid history is not a new decision; invalid UTF-8 follows the same append-order rule. |
| Python 3.9 grammar parse of both helpers and both Python test files | PASS; grammar only, not live Python 3.9. |
| `git diff --check` from original base through effective candidate | PASS. |

The supplied suite covers actual mandatory zero/failure/skip, missing browser,
unknown/error required policy, normal 3.5:1 contrast, malformed/duplicate/non-finite
JSON, full supplied leaf coverage, dirty/staged/new/deleted inputs, symlink state,
evidence-file changes, config/docs/criteria/approval changes and audit persistence
failure. Passing suite totals do not cover or negate R02.

### Per-leaf specification disposition

| Leaf | Disposition and evidence |
|---|---|
| A02.1 | PASS in scope: one shared schema/control evaluator; required v2 QA inventory, exact types/fields/IDs and strict JSON tests pass. |
| A02.2 | PASS in scope: mandatory fail/error/unknown dominance, declared advisory preservation and immutable QA classification verified; S04/R01 closed. |
| A02.3 | Narrow inherited corrections retained; control tests verify source/version/applicability and normal/large-text contrast thresholds. No legal sign-off. |
| A02.4 | PASS in scope: actual mandatory missing/zero/failed/skipped/browser/policy evidence blocks; legitimate docs/no-test acceptance retained. |
| A03.1 | PASS: active decisions validated before filtering, old v1/error ordered without upgrading, later negative revocation and newer applicable recovery verified. |
| A03.2 | FAIL for selected acceptance identity (R02); product manifest/base/index/worktree/attempt/profile bindings remain verified in existing tests. |
| A03.3 | PASS for same-context immutable v2 QA and independent provenance requirements; package clearance still denied by R02. |
| A03.4 | FAIL: the two changed literal acceptance forms reuse old PASS (R02); other selected config/docs/criteria/evidence and rejection negatives pass. |
| A03.5 | PARTIAL: real nested progress and unrelated changes reuse evidence, but the normalizer also erases literal changes (R02). |

Original-authority package/leaf membership parsing remains a downstream
work-map/Swarm responsibility; the P05 coverage checks bind every supplied
selected leaf and required control, not an invented claim that no leaf was omitted.
The coordinator's final integration gate must check that authority mapping.

## P07 bridge and evidence limits

Independently ran the unchanged four-case `tests\unit\review_profile_bridge.py`
using a disposable read-only archive of P07
`56981edc4bd73020fea78e20526b10d62e822305` and this exact P05 v2 tree:
**4/4 PASS**, 50.348 seconds. Profile references remain v1 across v2
writer/reader/QA/SHIP. This includes the Python cases and explicit saved-reference
public-shell verify/resume with no host ID and a changed `CLAUDE_SESSION_ID`.

This does **not** prove ordinary bootstrap, later Windows containment/comparison
repairs, P07 independent acceptance or a final merged tree. Prior `912420f`
Python/shell outcomes and `d02bb248` saved-reference evidence are not relabeled
as current ordinary-bootstrap proof. No P07 defect is assigned to P05.

No full suite, live Python 3.9, Linux/macOS, browser/client/model, private profile,
network, global configuration/log action, dependency installation, dormant-hook
activation, real PR, push, merge, deployment or product edit occurred. Fixture
actor receipts remain synthetic; separately supplied host/human corroboration is
caller-trusted provenance, not authentication by actor strings/digests.
Symlink tests retain their explicit Git-object fallback where link creation is
not permitted. Local regulatory fixtures are not fresh legal research.

## Remaining gates

Only a new immutable candidate that closes R02 while retaining current positives
can pass specification. The first full bounded P05 quality review must then cover
the entire original-base-to-product change, not just the next repair; it has not
been performed in any of these three passes.

The coordinator has stopped implementation at the three-spec-iteration boundary
and will provide a narrow normalization repair card before another implementation.
No proposed classifier reuse or future repair is approved by this report.

P04/P06/P07/P08/P14 consumer joins, authority membership, generated reconciliation,
stable integrated acceptance and independent final review remain mandatory.
Neither v2 migration success nor saved-reference bridge success waives them.

**Position:** third specification review FAILED -> bounded normalization repair
and re-review; full quality and final joined delivery remain blocked.
