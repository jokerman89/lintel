# Lane review: WF (pending, non-clearing)

Actor `copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e` wrote this independent local lane review. It covers the WF
worker report whose SHA-256 is `4719be91a83fa8be21ae5081d9699b95d6ad37ad3079b2b7cab8c8afa7d61981`, at frozen head
`ebd087eca0358acde8e3cfc47703e220ec5c30f3`. Intended publication path:
`.claude/plans/reusable-patterns/swarm/reviews/WF.md`.

**This review is intentionally non-clearing.** Its status, verdict and both stages are PENDING. Two things block it:

- 4.3.c real PDF conversion is BLOCKED.
- 5.2.a per-consumer model, render and host behavior is UNVERIFIED.

It is not a successful review-input, a closed gate, the P05 v2 decision, QA, corroboration or the integrated review.

## How the binding was derived

Before binding, I checked that the report was stable. It gave the same SHA-256 twice, 20 s apart, with the file's
LastWriteTime unchanged. I then placed a copy at its intended path in my own scratch git-archive export of `ebd087ec`.

- **Native review-input refused the report, correctly.** `LINTEL_SOURCE_ROOT=<scratch> python -I -B bin/li-swarm.py
  review-input --repo . --coord .claude/plans/reusable-patterns/swarm/coordination.json --task WF` returned rc 1 and
  `ok: false`, with exactly three diagnostics: `report.incomplete`, `report.leaves` and `report.checks`. The report is
  honestly `pending`, and it carries BLOCKED and UNVERIFIED leaf and top-level checks. No acceptance, result, digest,
  scope or provenance diagnostic was raised.
- **I derived the binding with the public helper.** I called `swarm_contract.review_binding(root, "WF", report)` on the
  report as parsed by `_read_evidence`, which gave 0 read diagnostics. The helper does not change the report's status.
  Its result equals the supplied attempt, acceptance, result and report values. This is a status-review binding, not a
  successful review-input.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-review",
  "initiative": "reusable-patterns",
  "task_id": "WF",
  "status": "pending",
  "reviewer": "WF lane independent integration reviewer (read-only GitHub Copilot app session 24bf5df0)",
  "actor_ref": "copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e",
  "mode": "independent",
  "changed_paths": [".claude/plans/reusable-patterns/swarm/reviews/WF.md"],
  "binding": {
    "work_map": ".claude/plans/reusable-patterns/work.json",
    "package_id": "WF",
    "leaf_ids": ["4.1.a", "4.1.b", "4.1.c", "4.2.a.wf", "4.2.b.wf", "4.2.c", "4.3.a", "4.3.b", "4.3.c", "4.3.d", "5.1.a", "5.1.b", "5.1.c", "5.2.a", "5.2.b"],
    "attempt_id": "reusable-patterns-WF-consolidation-ebd087ec-1",
    "acceptance_digest": "089b7e2a383e40c8239ff685f320cf6e3afbc2e1c254dda75e90d6f66f0941d9",
    "result_digest": "96c3e4b6f0890a86510b00c5e3cb342bddade696f749ad96b92d20c2bd951991",
    "report_digest": "4719be91a83fa8be21ae5081d9699b95d6ad37ad3079b2b7cab8c8afa7d61981"
  },
  "verdict": "PENDING",
  "stages": {
    "spec": "PENDING",
    "quality": "PENDING"
  },
  "checks": [
    {
      "name": "report hash stability before binding",
      "status": "OBSERVED",
      "evidence": "SHA-256 4719be91... read twice 20 s apart with unchanged LastWriteTime; the bound copy has the same hash"
    },
    {
      "name": "native li-swarm review-input for WF in a reviewer-owned scratch export of ebd087ec, with the report at its intended path",
      "status": "REFUSED",
      "evidence": "rc 1, ok false, exactly 3 diagnostics: report.incomplete, report.leaves, report.checks; no acceptance/result/digest/scope/provenance diagnostic. Correct refusal of an honest pending report."
    },
    {
      "name": "binding derived with public swarm_contract.review_binding from the raw report (status-review binding, not a successful review-input)",
      "status": "OBSERVED",
      "evidence": "0 read diagnostics; work_map, package, 15 leaves, attempt, acceptance 089b7e2a..., result 96c3e4b6... and report_digest 4719be91... equal the supplied values; recomputed acceptance digest 089b7e2a...; the report does not change status"
    },
    {
      "name": "result readback: SHA-256 of git cat-file blob ebd087ec:<path> for all 45 scope files against result.files digests",
      "status": "OBSERVED",
      "evidence": "45/45 equal; WF.file-snapshot.json SHA-256 equals the export's snapshot_file_sha256 (4fb13dac...)"
    },
    {
      "name": "attribution readback: 45 scope blobs at lane head 14492a49, fdb9f27b and ebd087ec",
      "status": "OBSERVED",
      "evidence": "44/45 byte-identical between 14492a49 and ebd; only skills/pattern/references/consumer-contract.md differs, via coordinator/INT commits 87c2b476 and ea2c139d (reviewed in my INT b831 and fdb closure reviews; not WF authorship); 0/45 differ between fdb and ebd; fdb..ebd changes only plan.md and build-log.md (+9/-7)"
    },
    {
      "name": "historical local WF helper/CLI/launcher acceptance at lane head 14492a49 (my separate WF144 closure review)",
      "status": "HISTORY",
      "evidence": "my own runs at 14492a49: V09 31/31 (0 skipped), V10 26/26, V11 18/18 (0 skipped), CORE 135/135, design-contract 18 rc 0; 723 findings M1-M4 and L1-L6 closed, I1 retained. This is local card acceptance at helper level, not the full WF spec PASS."
    },
    {
      "name": "fixed-head V09/V10/V11 rerun at fdb9f27b or ebd087ec",
      "status": "UNVERIFIED",
      "evidence": "not rerun by me or by the owner at these heads; 44/45 bytes are identical from 14492a49, and the one changed file is documentation"
    },
    {
      "name": "4.3.c real PDF conversion (host case C-PDF)",
      "status": "BLOCKED",
      "evidence": "host-observations.json 858c8bd0...: provider-blocked; no PDF produced; Chrome DevTools endpoint not verified; DOC-01 unverified in PDF. Local V09 proves selection invariance only."
    },
    {
      "name": "5.2.a per-consumer model/render/host behavior (V17)",
      "status": "UNVERIFIED",
      "evidence": "only host case A was observed (li-cycle/li-pattern/li-build dashboard; project_visual/validate_visual; Chromium; positive plus DASH-03 negative). generate-web, design-dna, frontend-typography, frontend-motion, frontend-shader and generate-app have no host observation. Local V11 helper cases for 10 consumers are helper-level only."
    },
    {
      "name": "4.3.b real generate-word DOCX host case",
      "status": "PARTIAL",
      "evidence": "parent-observed C1 (DOCX through Word Canvas, DOC-01 present) and C2 (marked negative refused, review exit 7). Word page rendering is required and unverified. Observed by the parent; I did not execute it."
    }
  ],
  "limitations": [
    "Non-clearing by design: status, verdict and stages stay PENDING while 4.3.c is BLOCKED and 5.2.a is UNVERIFIED. Expected native state: WF invalid_report (the report has 3 diagnostics), which would become rework_required if those cleared; li-swarm verify fails, and the global close stays BLOCKED. The framework was not modified to accept pending as PASS.",
    "File-snapshot mode only: the binding proves the current content of 45 files at ebd087ec, not Git attribution of one worker diff. Git mode is refused because the integrated union diff includes out-of-scope paths and consumer-contract.md received post-join coordinator writes 87c2b476 and ea2c139d. No reviewer Git base or head was invented.",
    "The snapshot records every file as mode 100644. This is a swarm helper limitation; it is consistent between capture and verify and is not fixed here.",
    "Substantive review history is my separate records: WF 723 (M1-M4, L1-L6, I1-I3), 5abe (I1 follow-up), 14492a49 closure, INT b8312bb7 and INT closure fdb9f27b. They are cited, not rehashed. Local helper-code acceptance at 14492a49 is not a full WF specification PASS.",
    "Host observations are the parent's (host-observations.json 858c8bd0...): one Copilot App client and model, Chromium only. I did not execute them. release_clearance false; native_v2_review_record false.",
    "Host: Windows, Git for Windows bash/MSYS, Python 3.11.9, LongPathsEnabled=0. POSIX and macOS are unobserved by this reviewer.",
    "Not run: full suite, strict run-all --require-all, full kit, or new host tests. P05 shared context/QA/corroboration, V17, the integrated review and release clearance remain separate gates."
  ]
}
-->

## Severity counts

Critical 0 / High 0 / Medium 0 / Low 0 / Info 4. No new findings. The lane is PENDING because of open host gates, not
because of a defect I found.

## Specification review (PENDING)

| Leaf | Local evidence (owner report, 14492a49; my WF144 rerun) | Host/V17 | Review status |
|---|---|---|---|
| 4.1.a | V09 ConsumerContract, including the real launcher | n/a | local covered |
| 4.1.b | V09 Startup | n/a | local covered |
| 4.1.c | V09 PlanEquivalence | n/a | local covered |
| 4.2.a.wf | V09 Continuation | D (cold resume blocked on pinned_revoked), parent-observed | local covered |
| 4.2.b.wf | V09 Review through core (exit 7) | n/a | local covered |
| 4.2.c | V09 Capture | n/a | local covered |
| 4.3.a | V09 DocumentPipeline attachment | n/a | local covered |
| 4.3.b | V09 clause equality / exit 7 | C1/C2 DOCX observed; Word page render unverified | PARTIAL |
| 4.3.c | V09 selection invariance only | C-PDF BLOCKED | **BLOCKED** |
| 4.3.d | V09 Engineering | n/a | local covered |
| 5.1.a | V10 Legacy | n/a | local covered |
| 5.1.b | V11 legacy capture → read_asset bytes | n/a | local covered |
| 5.1.c | V10 Projection/Validation | n/a | local covered |
| 5.2.a | V11 10-consumer helper cases | A only (li-cycle/li-build route); six consumer cells unobserved | **UNVERIFIED** |
| 5.2.b | V11 real-launcher roundtrip | A (Chromium) | local covered |

"Local covered" means the V09/V10/V11 cases at 14492a49, which are byte-identical to ebd apart from consumer-contract.md.
It is not a fixed-head rerun at ebd. Case A is the li-cycle/li-build/browser route. It is not relabelled as
generate-web, which remains an explicitly unobserved route.

## Quality review (PENDING)

I found no new quality issues. The closure of my 723 findings at 14492a49 stands:

- M2: `_report` calls the public `validate_selection_report` with no private bridge.
- M3: the fallback is visible and never empty.
- M4: the consumer table has honest deferrals.
- L1-L6: closed.
- I1: retained.

The only post-lane change in scope is coordinator/INT documentation. The quality stage stays PENDING only because the
lane review is not cleared as a whole.

Info:

1. **Refused review-input.** The native refusal (`report.incomplete`, `report.leaves`, `report.checks`) is the correct
   outcome for an honest pending report. It is recorded as a diagnostic, not worked around.
2. **consumer-contract.md.** The file differs from the lane head through 87c2b476 and ea2c139d (coordinator/INT). I
   reviewed both commits at INT; they are not WF authorship.
3. **Fixed-head suites.** V09/V10/V11 were not rerun at fdb or ebd. The byte identity makes a regression unlikely, but
   the owner correctly reports this as UNVERIFIED.
4. **Mode 100644.** The snapshot records mode 100644 for every file. This is a tool limitation, as in the PACK lane.

## Verification and limitations

- My evidence is under my session files `swarm-consolidation\`:
  - `WF-owner-report-copy.md`
  - `review-input-WF.json` and `.err`
  - `binding-WF.txt`
  - `scratch-ebd\` (my own export)
- My reviewer worktree and the frozen clone `lp64\review\e` are clean at `ebd087ec`.
- I made no source, branch, shared-clone, other-actor or P05 JSON writes.
- Expected native close errors if this review is placed at its intended path:
  - WF lane state `invalid_report`, from the 3 report diagnostics;
  - `li-swarm verify` fails;
  - the global close stays BLOCKED.
- Once the report diagnostics clear, a pending review gives `rework_required`, not PASS.
