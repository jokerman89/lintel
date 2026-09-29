# Lane review: WF R2 (integrated head 2ce4cfcc)

Actor `copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e` wrote this independent local lane review, reusing the
original WF reviewer role. It covers the WF worker report R2, SHA-256
`6aef024ed368222360f4ec511ecb87f5779eb97c00dadb3e83ef6b9346909aa9` (UTF-8, LF), written by a different actor,
`copilot-session:a2f55ec5-b687-49a5-8e33-796c743dff20`. The frozen integrated head is
`2ce4cfcc062e6806e0b3349d5e49a443097d4737` (tree `52900c7d562dcb5aa6a6701446e98a44645e2c0d`).

- **Intended publication path:** `.claude/plans/reusable-patterns/swarm/reviews/WF.md`.
- **Binding source:** copied from CORE's structural input `WF-2ce4cfcc-r2.review-input.scratch.json`
  (SHA-256 `13a585c4adf4ca38c98f536ea282f2d25313ddaaaa9616af39e71209eefeafa8`), `review_input.binding`, rc 0, `ok: true`,
  `diagnostics: []`. That proves structural admission only.
- **Recomputed independently:** acceptance and result digests with the unchanged `lib/swarm_contract.py` against the
  actual CORE Windows worktree and my own clone, and the report digest from its bytes.

This is a local observation, not the P05 v2 decision, QA, corroboration, aggregate review, SHIP or release clearance.
My earlier WF review at `ebd087ec` (`reviews\WF-ebd087ec.md`, SHA-256
`cb6f1ccd3fbd27991d43be6ad15b0a585453365f84536b7f5eb3ec367a3e351b`, non-clearing PENDING) and all earlier V18/adjudication records stay byte-identical. No earlier verdict is
transferred; this one rests on the current acceptance and evidence below.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-review",
  "initiative": "reusable-patterns",
  "task_id": "WF",
  "status": "complete",
  "reviewer": "WF lane independent integration reviewer (read-only GitHub Copilot app session 24bf5df0)",
  "actor_ref": "copilot-session:24bf5df0-f0f7-432b-9321-3e8283e78e9e",
  "mode": "independent",
  "changed_paths": [
    ".claude/plans/reusable-patterns/swarm/reviews/WF.md"
  ],
  "binding": {
    "acceptance_digest": "d1b2858fea27c2cfd773b97124269b1337e352223bb66f2ec180c09c12aac745",
    "attempt_id": "reusable-patterns-WF-integration-2ce4cfcc-1",
    "leaf_ids": [
      "4.1.a",
      "4.1.b",
      "4.1.c",
      "4.2.a.wf",
      "4.2.b.wf",
      "4.2.c",
      "4.3.a",
      "4.3.b",
      "4.3.c",
      "4.3.d",
      "5.1.a",
      "5.1.b",
      "5.1.c",
      "5.2.a",
      "5.2.b"
    ],
    "package_id": "WF",
    "report_digest": "6aef024ed368222360f4ec511ecb87f5779eb97c00dadb3e83ef6b9346909aa9",
    "result_digest": "bdad240949efa44195a32f897672d4a50e525769483f37a9172bedda2f5af1a2",
    "work_map": ".claude/plans/reusable-patterns/work.json"
  },
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "binding: CORE structural review-input wrapper (review_input.binding) plus independent recomputation at 2ce4cfcc",
      "status": "PASS",
      "evidence": "wrapper sha256 13a585c4adf4ca38c98f536ea282f2d25313ddaaaa9616af39e71209eefeafa8, rc 0, ok true, diagnostics []; swarm_contract.acceptance_digest(WF lane) = d1b2858f...c745 in the actual CORE Windows worktree and in the reviewer's own clone; verify_result(Path(root), write_scope, result) returned no error in both; value_digest(result) = bdad2409...a1f2; report bytes sha256 = 6aef024e...09aa9 (67649 bytes, LF only). changed_paths = 45 result files + swarm/reports/WF.md; binding leaf_ids are the 15 work.json WF leaves"
    },
    {
      "name": "Verify-column fidelity: the R2 per-leaf mapping versus plan.md:196-230 and V definitions plan.md:101-110",
      "status": "PASS",
      "evidence": "15/15 leaves map to the original Verify columns (4.1.a V09; 4.1.b V09,V18; 4.1.c V09; 4.2.a.wf V09; 4.2.b.wf V09; 4.2.c V09; 4.3.a V09,V18; 4.3.b V09,V17; 4.3.c V09,V18; 4.3.d V09,V18; 5.1.a V10; 5.1.b V10,V18; 5.1.c V10; 5.2.a V11,V18; 5.2.b V10,V11,V15). Artifact Word/PDF, C-PDF, six 5.2.a host cells and direct-entry host extras are listed as limitations, not leaf gates, per RN-14/15/16. The 4.3.c summary row prints 'V09, V18, RN-14'; RN-14 is the plan annotation, not a Verify column (Info)"
    },
    {
      "name": "scope/delta attribution over the 45 WF paths",
      "status": "PASS",
      "evidence": "git diff 4c6ce841..2ce4cfcc over scope: empty; whole-repo 4c6c..2ce touches only two build-log.md files, tests/integration/pattern-portability.py and tests/unit/wiki-gen-idempotency.sh (none WF-cited), so 4c6c logs are input-identical for WF. 14492a49..2ce: 30 files, all attributed: 87c2b476 (in INT b831) and ea2c139d (in fdb9f27b) consumer-contract CORE docs; 18489982 (closed 118d1c71); 23e8e194 (b02b10cc R-4 recheck); 99de0741 (d4acf3e7 D1/M1 closure); 948ab2dc/50047570 and 77eb3794. d4acf3e7..2ce: 22 files +40/-6"
    },
    {
      "name": "independent V18 of the d4acf3e7..2ce4cfcc delta (948ab2dc cli_support metadata, 77eb3794 <style> literal) that the author admits had no independent V18",
      "status": "PASS",
      "evidence": "PyYAML parse of all 59 changed skills frontmatters (22 in WF scope): every non-cli_support key equal to d4acf3e7, cli_support = old list + 'copilot' (5 inline, 17 block '- cli: copilot / level: full'); bodies byte-identical except skills/generate-style-learn/SKILL.md:68 '- Parse <style> + linked CSS' -> '- Parse `<style>` + linked CSS', which only stops a raw HTML tag being swallowed by Markdown renderers. No WF behaviour, clause, precedence or pattern contract changed. The copilot 'full' host claim itself is native-lane/coordinator scope, not a WF leaf"
    },
    {
      "name": "V09 pattern-workflows (4.1.a-4.3.d)",
      "status": "PASS",
      "evidence": "native-join t/j-V09 sha256 1342d9d4..., CORE worktree ISOLATED head 4c6ce841 (WF-input-identical to 2ce), Ran 31 OK; observer 11d27634 (not this reviewer)"
    },
    {
      "name": "V10 pattern-visual (5.1.a-c, 5.2.b)",
      "status": "PASS",
      "evidence": "t/j-V10 sha256 077384d1..., head 4c6ce841, 26 OK"
    },
    {
      "name": "V11 pattern-visual-roundtrip (5.2.a, 5.2.b)",
      "status": "PASS",
      "evidence": "t/j-V11 sha256 c6195fc3..., head 4c6ce841, 23 OK; supporting design-contract f7e10363 29 OK skipped 0 and document-pipeline-binding c521ecb3 36 OK at 4c6c"
    },
    {
      "name": "V15 compatibility (5.2.b), split by observer/platform/head",
      "status": "PASS",
      "evidence": "parent 61d813e7 Linux Ubuntu 24.04 at exact 2ce4cfcc (log c5cd5854..., Python 3.12.3, git 2.43.0): design-dna-search 14 PASS, ALL PASS, EXIT 0 (lines 10-26); copilot-kit Ran 52 tests in 1983.105s OK, EXIT 0, no skips (lines 190-195); AGGREGATE_EXIT 0, final HEAD unchanged. frontend-design-roundtrip (c45f4235, All PASSED, schema/wiring only, not rendering proof) and design-validator (bc8a91cb, PASS) by 11d27634 on Windows CORE at input-identical 4c6ce841. copilot-kit diagnostic lines POST_ADMISSION_GUARD_NOT_PROTECTED and long linked-worktree UNVERIFIED are disclosed test diagnostics, not platform enforcement"
    },
    {
      "name": "V17 4.3.b C1/C2",
      "status": "PASS",
      "evidence": "host-observations.json sha256 858c8bd0..., frozen_source b8312bb7: C1 real DOCX with DOC-01 Rollback Heading1, 96/96 blocks, release_clearance false; C2 marked negative: pattern review exit 7 DOC-01 mandatory_unmet, shared QA blocked, SHIP exit 3. b8312bb7..2ce on generate-word/generate-ppt is only the 948ab2dc cli_support metadata (+2 each); workflow test changes are covered by current V09. Word page render stays BLOCKED/unverified as artifact QA (RN-14)"
    },
    {
      "name": "V18 for 4.1.b, 4.3.a, 4.3.c, 4.3.d, 5.1.b, 5.2.a",
      "status": "PASS",
      "evidence": "reviewer 24bf5df0 records, unchanged: wf-14492-closure-review 5f2d14ea (all 45 at 14492a49), v18-rn14-82e97d74 d10a528f, v18-m1-118d1c71 72dc0ae5, r4-fix-b02b10cc 432754e4, d1-m1-d4acf3e7 ecae2489/9b316e3b, plus this record's d4ac..2ce V18. 5.1.b files changed after 14492a49 only by cli_support metadata and the <style> backtick"
    },
    {
      "name": "quality: report integrity, attribution and honesty",
      "status": "PASS",
      "evidence": "R2 is a new file (old fb38094c/ebd4719 records untouched), reclassifies artifact/supplemental observations out of mandatory leaves per RN-14, cites the current parent V15 rather than fdb169/59f23 CI, admits the missing V18 of 948ab2dc/77eb3794 (closed here), and keeps release_clearance false. Owner-claimed 172-entry clpattern guard (0 findings) was not rerun by this reviewer"
    }
  ],
  "limitations": [
    "Local lane observation only: not the P05 v2 decision, QA, corroboration, aggregate/integrated review, SHIP or release clearance; the native grant stays unissued.",
    "This reviewer ran no suites for this record; V09/V10/V11/V15/V17 results are observed by 11d27634 (CORE, 4c6ce841, Windows), parent 61d813e7 (Linux, 2ce4cfcc) and the parent's host tasks (b8312bb7). Input identity to 2ce4cfcc was checked by the reviewer by scoped git diff.",
    "Artifact states unchanged: Word rendered pages BLOCKED; produced PDF text/pages UNVERIFIED; C-PDF BLOCKED; six 5.2.a per-consumer model/render/host cells DEFERRED; direct SCOPE/DEFINE/DISCOVER, direct generate-subskill and engineering-entry host observations UNVERIFIED.",
    "6.2.a/b/c remain coordinator gates, PENDING. Historical fdb169 and 59f23 CI runs are not the current joined matrix. POSIX/macOS beyond the parent's Linux V15 run is unobserved.",
    "Binding target is the actual CORE Windows worktree (EOL decision (a): 8 historic CRLF working files kept as-is); the file snapshot's 100644 versus Git 100755 mode quirk is retained; no normalization, rebind or borrowed P07 by this reviewer.",
    "RN-15/RN-16 boundary stays as closed at d4acf3e7: design_contract and li-pattern runtime paths are mechanical; other consumers carry a documented workflow obligation."
  ]
}
-->

## Severity counts

Critical 0 · High 0 · Medium 0 · Low 0 · Info 6.

## SPEC (PASS)

Each leaf is judged only against its original Verify column (plan.md:196-230); RN-14/15/16 are authoritative.

| Leaf | Verify | Evidence (observer, head) | Status |
| --- | --- | --- | --- |
| 4.1.a | V09 | j-V09 31 OK (11d, 4c6c ≡ 2ce) | MET |
| 4.1.b | V09, V18 | V09; V18 wf-14492 closure + d4ac..2ce metadata V18 here | MET |
| 4.1.c | V09 | V09 | MET |
| 4.2.a.wf | V09 | V09 (V17 D cold resume supplemental only) | MET |
| 4.2.b.wf | V09 | V09; ship delta 99de0741 reviewed in d1-m1-d4acf3e7 | MET |
| 4.2.c | V09 | V09 | MET |
| 4.3.a | V09, V18 | V09; V18 v18-rn14, v18-m1, d1-m1 (18489982, 99de0741) + d4ac..2ce here | MET |
| 4.3.b | V09, V17 | V09; V17 C1/C2 at b8312bb7, later word/ppt delta metadata-only | MET |
| 4.3.c | V09, V18 | V09; V18 v18-rn14 d10a528f, closure v18-m1 72dc0ae5 | MET |
| 4.3.d | V09, V18 | V09; V18 wf-14492 + d4ac..2ce metadata here | MET |
| 5.1.a | V10 | j-V10 26 OK | MET |
| 5.1.b | V10, V18 | V10; V18 wf-14492 + d4ac..2ce (cli_support, `<style>` literal) here | MET |
| 5.1.c | V10 | V10 (23e8e194 frontend-design delta reviewed at b02b10cc) | MET |
| 5.2.a | V11, V18 | j-V11 23 OK; V18 d1-m1-d4acf3e7 SPEC MET A1-A7 | MET |
| 5.2.b | V10, V11, V15 | V10, V11; V15 split: parent Linux 2ce (design-dna-search 14 PASS, copilot-kit 52 OK) + 11d Windows 4c6c (frontend-design-roundtrip, design-validator) | MET |

## QUALITY (PASS)

The report is honest and attributable. It reclassifies artifact and supplemental observations out of mandatory leaves,
cites the current V15 run instead of historical CI, attributes every post-14492 change to its actual commit, and admits
the one missing V18 (948ab2dc/77eb3794). I close that V18 here: the delta is host-hint metadata plus one Markdown
literal fix, with no WF behaviour change.

## Info findings

- I-1 (Info): 4.3.c summary row prints `V09, V18, RN-14`; RN-14 is an annotation, not a Verify column. No effect on the verdict.
- I-2 (Info): V15 is split by observer, platform and head (Linux 2ce parent; Windows 4c6c CORE). copilot-kit's
  POST_ADMISSION_GUARD_NOT_PROTECTED and long linked-worktree UNVERIFIED diagnostics are test disclosures, not platform
  enforcement.
- I-3 (Info): Cited native-join logs are at 4c6ce841; WF input identity to 2ce was checked by scoped and whole-repo git diff.
- I-4 (Info): V17 C1/C2 are at b8312bb7; later generate-word/ppt changes are cli_support metadata only.
- I-5 (Info): The `copilot: full` cli_support claim added in 948ab2dc belongs to native/coordinator scope, not WF leaves.
- I-6 (Info): The owner-claimed 172-entry clpattern guard was not rerun by me; frontend-design-roundtrip is schema/wiring
  evidence, not rendering proof.

## Limits

See the marker's `limitations`. No full, stress, provider, browser, model, host or install run; no edits to CORE,
shared ledgers, P05, audit or commits.
