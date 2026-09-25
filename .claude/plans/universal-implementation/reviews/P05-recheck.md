# P05 independent repair recheck

**Date:** 2026-09-20.
**Original initiative base:** `40c279520a86945cc7e607692355bf5231446ff1`.
**Original core:** `7a7a50a1273ec4c04ed51118a9cfb2e3c85b246d`.
**Repair base / first reviewed candidate:** `9354fb174bd0398270989cd102de1c2906ef91a7`.
**First independent report:** `aef81d425a2ca36588a8b8ab01bc1a8321d9bc3d`.
**Repair product:** `54147fd5c6e3115c590bc3f47b5a9cdbb96a055f`, directly atop `9354fb1`.
**Effective reviewed snapshot:** `e5b92a4fd2ac8c757a0370254ea73a2a76601038`;
its only change after `54147fd` is the builder's report.
**Reviewer:** same independent session `c8e62d27-4511-4af6-a0af-16e4dcd3c3bc`,
not an implementation author.

**Stage 1 - specification recheck: FAIL.** The four original reproductions are
addressed, but two repair-induced false-clearance regressions remain:
**1 P1, 1 P2, 0 P3** new findings.
**Stage 2 - full bounded P05 quality review: NOT RUN**, because the specification
still fails. **Final joined acceptance/delivery: BLOCKED.**

## Isolation, authority and delta

Created a separate clean worktree/branch
`jokerman-microsoft-universal-evidence-recheck` at exact `e5b92a4`. The original
`jokerman-microsoft-universal-evidence-review` branch and report remain at `aef81d4`;
no source, builder or coordinator worktree was reset. Candidate implementation
files remained unchanged during review. This commit adds only this report.

Scope remains the original P05 spec, package card, ADR-0028, A02/A03 and the
original audit leaves. The recheck concentrates on S01-S04, their preserved
positive behavior and regressions introduced by the repairs. It is not a new
whole-repository audit or an authenticated-identity assessment.

Read the complete repair delta: `bin\li-review-evidence.py`,
`lib\review_contract.py`, `lib\review-schema.json`, `skills\qa-only\SKILL.md`,
`skills\ship\SKILL.md`, `skills\review\references\evidence.md`,
`tests\unit\review_evidence.py`, and the revised `reports\P05.md`.
The new public API is
`validate_decision(record: Mapping[str, Any], *, history: bool = False) -> Json`.
The builder report now accurately distinguishes its initial missed defects,
repair self-verification and outstanding independent approval. Its old P07
Python/saved-reference evidence is not mislabeled ordinary-bootstrap validation.

## Original findings: disposition

| Original finding | Recheck disposition |
|---|---|
| S01: malformed later decisions revive old PASS | CLOSED for the original and expanded active-decision cases. Re-ran the original report's missing/null/empty-skill replay: each actual reader and SHIP returns 3 / false. Direct/wrapped/current-context validation now precedes filtering. Malformed apparent-other scopes block; valid unrelated skill/map/package decisions and explicit history remain usable. |
| S02: selected task completion invalidates unchanged acceptance | Original checkbox-only failure FIXED. Selected `[ ]`/`[x]`/`[X]` updates reuse evidence; task text/IDs, non-progress markers, fenced examples, spec boxes, raw product-selected documents and revoked approval still bind in supplied tests. The narrower normalization invariant remains OPEN because indented code literals are now erased from acceptance identity (R02). |
| S03: docs-only QA invents executable-test requirements | Original docs-only failure FIXED: real mandatory document check plus grounded tests N/A passes review/QA/SHIP. N/A-only/advisory-only QA and actual mandatory zero/fail/skip cases block. The acceptance invariant remains OPEN because QA can now omit or reclassify a bound required test obligation (R01). |
| S04: SHIP promotes advisory gates to hard requirements | CLOSED for the owned contradiction. SHIP preflight, stop, customer-share, status, pause and recovery instructions now distinguish applicable mandatory outcomes from advice. QA-only/shared guidance also permit genuine non-test validation without changing actual mandatory test requirements. |

These closures describe the precise old defects, not approval of the package.

## New specification findings

### P05-R01 - P1: QA observations can remove or reclassify a bound mandatory obligation

**Locations:** `lib\review_contract.py:708-720`;
`bin\li-review-evidence.py:136-140`. **Confidence:** 10/10.
**Requirements:** A02.2/A02.4/A03.3, same-context acceptance, S03 preservation.

The repaired `verify_qa` verifies the context digest but derives all QA
requirements, kinds and applicability from the incoming observations. It only
requires *some* applicable mandatory control. It does not require the QA evidence
to satisfy the expected validation obligations or reject a required control's
downgrade, unlike review validation at `lib\review_contract.py:560-567`.

In the reproduced fixture, unchanged approved `spec.md` explicitly requires
`fixture-mandatory-tests` with nonzero execution, zero failures and zero skips;
`required_controls` includes `tests`, and the independently corroborated review
contains that exact mandatory `tests` control. No acceptance/context or reviewed
product input is changed. The following incoming QA variants all produce real
**QA exit 0 and SHIP exit 0 / `ok: true`**:

| Incoming observation | Invalid clearance |
|---|---|
| Omit `tests`; provide only a passing mandatory `document` check | No observation for the explicitly required test obligation. |
| Keep ID `tests`, report failure/exit 1, but mark it advisory beside a document pass | A bound mandatory failed test becomes advice; SHIP's top-level status remains pass. |
| Keep mandatory ID `tests`, replace kind `tests` with generic `check` and empty observation | No command/count observation is required for the formerly bound executable test. |

The replay uses a separate `qa-observed.txt` containing the corresponding actual
synthetic QA result, content-hashed by the real QA producer. It does not reuse a
stale passing output file as purported failed-run evidence. Baseline `9354`
blocks all three variants; `54147fd` introduces their clearance. An actual
mandatory `tests` control with zero executions still blocks on both revisions.

**Required correction:** bind the required QA validation IDs, types,
mandatory/advisory classification and applicability to the immutable expected
acceptance, not the incoming observation list. Coordinate any shared API/schema
change with downstream owners. Retain genuine docs-only document checks and
grounded tests N/A; do not restore a universal executable-test requirement or
mistake review-only controls for QA obligations.

This is a consistency/fail-closed contract defect, not a claim that declarations
or a content digest authenticate actors.

### P05-R02 - P2: task-progress normalization changes Markdown code-literal identity

**Location:** `lib\review_contract.py:423-442` (particularly 425-427, 439-440).
**Confidence:** 10/10.
**Requirements:** A03.2/A03.4/A03.5 and S02's only-task-progress boundary.

The normalizer accepts arbitrary leading spaces/tabs and only tracks backtick
or tilde fences. A four-space-indented Markdown code example matching a selected
leaf ID is consequently normalized as task progress. In this exact mapped
`plan.md` excerpt (`start: "# P1"`, `end: "# P2"`):

```markdown
# P1
- [ ] A1 Fix fixture
- [ ] A2 Preserve config

Required literal example:

    - [ ] A1 Required literal code sample

# P2
```

Changing only the example's four-space-indented `[ ]` to `[x]` leaves the
acceptance digest unchanged. The actual reader and SHIP both return
**exit 0 / `ok: true`**, reusing the old review despite changed selected literal
acceptance. Baseline `9354` correctly returns reader 3 / SHIP 3. This is not a
real task checkbox completion, and the plan is not product-selected.

**Required correction:** recognize actual mapped task-progress syntax and retain
code-literal bytes, including indented code. Do not fix it by banning all indented
tasks: legitimate nested task progress must remain reusable. Preserve the
existing fenced/spec/raw-product/changed-ID/changed-criterion negatives.

## Executable new-regression replay

Run from the exact repair worktree root in PowerShell. All repositories/homes,
observations and receipts are synthetic and disposed by the fixture:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
@'
from copy import deepcopy
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path.cwd() / "tests" / "unit"))
from review_evidence import Fixture, control, encoded

f = Fixture()
f.setUp()
try:
    f.request["required_controls"].append("tests")
    f.write("spec.md", "# Acceptance\nA1 and A2 require fixture-mandatory-tests, "
            "nonzero execution, zero failed and skipped.\n")
    tests = control("tests", "tests")
    tests["observation"] = {
        "command": "fixture-mandatory-tests", "executed": 3,
        "failed": 0, "skipped": 0, "exit_code": 0,
    }
    f.record(controls=[control(), control("quality"), tests])
    f.log()
    f.corroborate()
    f.read()
    document = control("document")
    document["evidence"] = ["qa-observed.txt"]
    advisory = deepcopy(tests)
    advisory.update(requirement="advisory", status="fail",
                    evidence=["qa-observed.txt"])
    advisory["observation"].update(failed=1, exit_code=1)
    changed_kind = deepcopy(tests)
    changed_kind.update(kind="check", observation={},
                        evidence=["qa-observed.txt"])
    zero = deepcopy(tests)
    zero["evidence"] = ["qa-observed.txt"]
    zero["observation"]["executed"] = 0
    cases = [
        ("omitted", [document], "document passed; mandatory tests not executed\n"),
        ("advisory", [document, advisory],
         "document passed; fixture-mandatory-tests: 3 executed, 1 failed, exit 1\n"),
        ("kind", [changed_kind], "generic check; no executable test observation\n"),
        ("zero", [document, zero],
         "document passed; fixture-mandatory-tests: 0 executed\n"),
    ]
    for name, controls, output in cases:
        f.write("qa-observed.txt", output)
        inputs = f.root / "qa-input.json"
        inputs.write_text(encoded({"controls": controls}), encoding="utf-8")
        qa = f.cli("qa", "--repo", f.repo, "--expected", f.expected_file,
                   "--input", inputs, ok=None)
        f.qa_file.write_text(qa.stdout, encoding="utf-8")
        ship = f.ship(ok=None)
        print(name, "qa", qa.returncode, "ship", ship.returncode,
              json.loads(ship.stdout)["ok"])
finally:
    f.doCleanups()

f = Fixture()
f.setUp()
try:
    text = ("# P1\n- [ ] A1 Fix fixture\n- [ ] A2 Preserve config\n\n"
            "Required literal example:\n\n"
            "    - [ ] A1 Required literal code sample\n\n# P2\n")
    f.write("plan.md", text)
    f.request["acceptance_paths"] = [
        "spec.md", {"path": "plan.md", "start": "# P1", "end": "# P2"},
    ]
    f.record()
    f.log()
    f.corroborate()
    f.qa()
    f.read()
    f.ship()
    f.write("plan.md", text.replace("    - [ ] A1", "    - [x] A1"))
    read = f.read(ok=None)
    ship = f.ship(ok=None)
    print("code-literal", "read", read.returncode, "ship", ship.returncode,
          json.loads(ship.stdout)["ok"])
finally:
    f.doCleanups()
'@ | python -
```

Observed candidate output: `omitted`, `advisory`, `kind` each `qa 0 ship 0 True`;
`zero qa 3 ship 3 False`; `code-literal read 0 ship 0 True`.
Equivalent probes ran against preserved `9354` implementation under report-only
`aef81d4`: the first three returned QA 1 / SHIP 3 / false, zero stayed blocked,
and code-literal returned reader 3 / SHIP 3 / false.

## Actual checks and preserved behavior

Windows, Python 3.11.9, Git 2.53.0.windows.4 and Git Bash 5.3.15; bytecode disabled.
Tests used isolated fixture homes/repositories, with temporary HOME and
system/global Git configuration isolation for supplemental shell checks.
No product mutation was used to obtain these results.

| Check | Result |
|---|---|
| `bash tests\unit\review-evidence.sh` | PASS, 38 tests, 444.165 seconds. |
| `bash tests\unit\mandatory-controls.sh` | PASS, 12 tests, 60.741 seconds. |
| `bash tests\integration\no-merge-without-review.sh` | PASS, 2 tests, 16.602 seconds; merge strings are data only. |
| `bash tests\unit\review-source-target.sh` | PASS, all three source/target/history scenarios. |
| `bash tests\shape\audit-writes-via-helper.sh` | PASS. |
| `bash tests\shape\skill-descriptions-trigger.sh` | PASS. |
| `bash tests\shape\agents-categorized.sh` | PASS, 69 agents retained. |
| `bash tests\shape\claude-home-paths.sh` | PASS. |
| Original S01 report replay on repaired tree | All three variants now reader 3 / SHIP 3 / false. |
| New R01/R02 probes, old-versus-repaired product | Both regressions reproduced; exact results above. |
| Python 3.9 grammar parsing, both helpers and both Python tests | PASS; not live Python 3.9 execution. |
| Repair-range `git diff --check` | PASS. |

Source/target separation, actual persistence-error detection, legacy raw inspection,
valid unrelated scope, declared-versus-corroborated identity, per-selected-leaf
coverage, dirty/staged/new/deleted/symlink identity and useful non-release unmapped
inspection remain covered by passing tests. Ordinary selected task progress and
docs-only positive scenarios now pass. Those positives do not mask the new
acceptance false-clearances.

### Current leaf disposition

| Leaf | Disposition |
|---|---|
| A02.1 | Existing strict schema/control tests pass; the immutable QA obligation gap is R01, not a claim of complete acceptance. |
| A02.2 | FAIL: incoming QA can downgrade a bound mandatory failure to advisory (R01). |
| A02.3 | Narrow inherited regulatory/contrast corrections retained; mandatory-control tests pass. No legal certification. |
| A02.4 | Properly declared mandatory zero/fail/skip/browser/policy negatives pass; acceptance remains FAIL where QA can remove their bound obligation (R01). |
| A03.1 | PASS for reviewed repair: full active-decision validation precedes filtering; later negative/error and malformed decisions do not revive PASS. |
| A03.2 | Product snapshot binding retained; selected acceptance identity is incomplete for code literals (R02). |
| A03.3 | FAIL: QA/SHIP can clear without the bound validation obligation (R01). |
| A03.4 | FAIL: changed selected code-literal acceptance reuses old PASS (R02). |
| A03.5 | Real checkbox-only progress and unrelated input reuse restored, but normalization is too broad (R02); not accepted as complete. |

## P07 boundary evidence and limits

Independently reran the unchanged four-case
`tests\unit\review_profile_bridge.py` on **this** `e5b92a4` P05 tree against a
disposable read-only archive of P07
`d02bb248b61dbbc703eb5252f5b46d86bdfc102b`: **4/4 PASS**, 48.737 seconds.
It covers the three Python cases plus explicit saved-reference public-shell
verification/resume, with no host ID and changed `CLAUDE_SESSION_ID`, followed
by real P05 writer/reader/QA/SHIP.

This is not ordinary-bootstrap/pinning evidence and does not approve P07.
The prior `912420f` Python-pass/public-shell-fail history remains distinct; it was
not rerun in this pass. The separately pending `56981` P07 source was not reviewed
or consumed here. No P07 defect is assigned to P05, and no saved-reference bridge
result waives actual bootstrap or final joined acceptance.

No full suite, Linux/macOS run, live Python 3.9 run, real browser/client/model,
private profile, network, global configuration/log action, dependency installation,
hook activation, real PR, merge, push or deployment. Symlink evidence retains the
suite's explicit Git-object fallback where Windows link creation is unavailable.
Actor receipts in fixtures are synthetic. A supplied host/human receipt remains
caller-trusted provenance; actor strings and digests are not authentication.

## Handoff and gates

Return R01/R02 to the original builder; reviewers do not repair findings.
Retain the new regressions, original S01-S04 positives and all applicable negative
controls in the next exact immutable candidate. Coordinate immutable QA-contract
changes with dependent consumers. Only a passing specification re-review unlocks
the previously unrun full bounded P05 quality stage.

P07 independent review, original-authority work membership, downstream consumers,
generated reconciliation, stable integrated-tree tests and independent final
integration review remain separate gates. Neither these passing local suites nor
the saved-reference bridge establish final joined approval.

**Position:** specification recheck FAILED -> builder repair -> new immutable
independent spec review; quality and delivery remain blocked.
