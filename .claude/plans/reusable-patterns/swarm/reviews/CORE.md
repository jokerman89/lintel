# Lane review: CORE (attempt reusable-patterns-CORE-integration-2ce4cfcc-1)

This is a new independent local lane review of the actual CORE report for this attempt.
- Report: `CORE-2ce4cfcc.md`, SHA-256 `393208e4f56503642a2c774afe0c3b4edfe251c8e63fb2c54fc4cbc8d991e0b3`.
- Frozen integrated candidate: `2ce4cfcc062e6806e0b3349d5e49a443097d4737`, tree
  `52900c7d562dcb5aa6a6701446e98a44645e2c0d`.
- Reviewer: session `c3015de8-134b-499b-bd3d-fa14d965701b` (c301). It is not the implementer and is
  distinct from report actor `11d27634`.
- Procedure: li-review, SPEC stage then QUALITY stage.

My earlier fdb (`cea7831d…`) and ebd (`81ac89fd…`) reviews remain verbatim history. This record
does not transfer their PASS. It independently assesses the current acceptance, the current report
and the current bytes, with proportional reuse disclosed below.

This is a local observation. It is not a P05 native v2 decision, QA, corroboration, aggregate
review or SHIP/release clearance.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-review",
  "initiative": "reusable-patterns",
  "task_id": "CORE",
  "status": "complete",
  "reviewer": "github-copilot-app:claude-opus-5.5:reusable-patterns-core-independent-reviewer",
  "actor_ref": "copilot-session:c3015de8-134b-499b-bd3d-fa14d965701b",
  "mode": "independent",
  "changed_paths": [".claude/plans/reusable-patterns/swarm/reviews/CORE.md"],
  "binding": {
    "work_map": ".claude/plans/reusable-patterns/work.json",
    "package_id": "CORE",
    "leaf_ids": [
      "2.2.a",
      "2.2.b",
      "2.2.c",
      "3.1.a",
      "3.1.b",
      "3.1.c",
      "3.2.a",
      "3.2.b",
      "3.2.c",
      "3.3.a",
      "3.3.b",
      "4.2.a.core",
      "4.2.b.core"
    ],
    "attempt_id": "reusable-patterns-CORE-integration-2ce4cfcc-1",
    "acceptance_digest": "2773195fe94204ab0fb18bf6b7dceeebe7e487841d4b294af9dbc852f9f32a0f",
    "result_digest": "47c6960c1bb4368189cd4a3efe31cdca0132d1411dbb9a9e68872f708d8b1033",
    "report_digest": "393208e4f56503642a2c774afe0c3b4edfe251c8e63fb2c54fc4cbc8d991e0b3"
  },
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "Input identity",
      "status": "PASS",
      "observed": "Recomputed sha256: report 393208e4... (UTF-8 LF), export CORE.json 3379494e..., CORE.file-snapshot.json b68799de..., parent scratch review-input 65a2a980... (ok true, 0 diagnostics; review_requirement substantive; release_clearance false). The scratch binding equals this binding. snapshot.result equals review-input.result. Scratch clone not treated as the P05 target"
    },
    {
      "name": "Acceptance and result recomputed on the actual target worktree (read-only)",
      "status": "PASS",
      "observed": "Imported lib/swarm_contract.py from the 2ce4cfcc Windows worktree with python -I -B and isolated HOME/TEMP; no checkout, normalization or write. acceptance_digest(...) = 2773195f... and value_digest(capture_result(write_scope)) = 47c6960c... both match. package_sources CORE leaf_ids = the 13 IDs, review substantive. git rev-parse HEAD/tree = 2ce4cfcc/52900c7d; git status --porcelain empty before and after"
    },
    {
      "name": "Current acceptance delta against the reviewer's last binding (ebd087ec..2ce4cfcc)",
      "status": "PASS",
      "observed": "git diff: plan.md changes only 4.3.b, 4.3.c, 5.2.a and 6.2.b (RN-14/15/16 wording and status); spec.md, contract.md, topology.md, work.json and coordination.json are unchanged. No CORE leaf text or verification key changed. The other changed files are build-log, handoff, reconciliation and swarm reports/reviews, which are coordinator ledgers. spec.md is CRLF in the worktree (LF in the index); acceptance_digest reads it with read_text universal newlines, and the digest was reproduced on those raw worktree bytes"
    },
    {
      "name": "CORE write_scope byte identity",
      "status": "PASS",
      "observed": "At the 2ce4cfcc worktree: bin/li-pattern.py 49cb6a2c (index 100755), lib/patterns.py 7742521e, skills/pattern/SKILL.md bca7ad1e, tests/unit/patterns.py 1b247ff7, tests/unit/patterns.sh d9dd1c29; all equal the result. git diff ebd087ec..2ce4cfcc over the five paths is empty. These are the bytes this reviewer source-reviewed through 8fb265cf and its SKILL.md docs delta"
    },
    {
      "name": "Report test evidence and head validity (author-run, inspected, not executed by this reviewer)",
      "status": "PASS",
      "observed": "j-unit-patterns.log sha256 3d23c7d1... header ISOLATED head=4c6ce841 cwd=target worktree, cmd bash tests/unit/patterns.sh, 'Ran 137 tests' OK rc 0; per-class ok lines Pin 14, Lifecycle 9, Maintenance 10, Bundle 6, ReviewCoverage 5, SelectionReport 9, no non-ok. j-V09-workflows.log sha256 1342d9d4... head=4c6ce841, cmd bash tests/integration/pattern-workflows.sh, Ran 31 OK rc 0. 4c6ce841 is an ancestor of 2ce4cfcc; 4c6ce841..2ce4cfcc changes only tests/integration/pattern-portability.py, tests/unit/wiki-gen-idempotency.sh and two build logs, none an input of patterns.sh or V09"
    },
    {
      "name": "Per-leaf mapping and SPEC/QUALITY source assessment (proportional reuse)",
      "status": "PASS",
      "observed": "The report maps 2.2 to Pin, 3.1 to Lifecycle, 3.2 to Maintenance, 3.3 to Bundle, 4.2.a.core to Pin+V09 and 4.2.b.core to ReviewCoverage+SelectionReport+V09. That matches the test class contents this reviewer listed by AST on the byte-identical tests/unit/patterns.py. Source correctness rests on this reviewer's independent CORE reviews P0/P1..R11 and 8fb265cf on the same runtime bytes, not on another actor's verdict"
    }
  ],
  "limitations": [
    "This reviewer executed no product test at 2ce4cfcc or 4c6ce841. Test evidence is the author's 4c6ce841 run on byte-identical CORE scope, inspected and hash-checked. This reviewer's own earlier runs (fdb 62 plus V09 31) are prior corroboration only. No full-suite, hosted Windows/Linux or native CI run is claimed.",
    "The result is a FILE snapshot, not Git attribution. CORE commits interleave with same-actor coordinator/INT commits, and SKILL.md coordinator edits (87c2b476, ea2c139d) are not separated. The file-snapshot mode 100644 vs the Git index 100755 for bin/li-pattern.py is a disclosed snapshot-layer quirk. No Git actor attribution is claimed.",
    "The P05 target is the CORE Windows worktree with raw bytes as-is. Eight selected historical md/.gitattributes files are CRLF in the worktree vs LF in HEAD (owner option a). This reviewer did not normalize, check out, or claim raw-byte equivalence with any LF clone. The committed reviews/CORE.md slot currently holds this reviewer's ebd review (worktree raw 81ac89fd), which binds stale acceptance and correctly blocks strict swarm until coordinated publication.",
    "The report's 3.3.b V18 entry cites historical milestone reviews and says the current lane review is pending; this record is that current review. The report's changed_paths names the repository report slot, which is not yet written; the coordinator publishes it.",
    "The non-CORE plan changes (4.3.b/c, 5.2.a MET at source/helper level with six visual host cells DEFERRED, 6.2.b) are WF/visual/host/INT scope. They are neither assessed nor covered here.",
    "Known product limits are retained: unkeyed digests authenticate no one; Windows paths over about 260 characters report missing; the casefold namespace rule is portable-safe only.",
    "Local swarm-review evidence only. No canonical P05 JSON, lane context, QA or corroboration exists (P07 gen2 context is the parent's). The final aggregate review, full CI and publication remain open. release_clearance is false."
  ]
}
-->

## Severity counts

| P0 | P1 | P2 | P3 |
|---|---|---|---|
| 0 | 0 | 0 | 0 |

## Specification review

No findings.

The line references below are to the current `plan.md` and `tests/unit/patterns.py` at `2ce4cfcc`.

| Leaf | Current acceptance (plan.md) | Evidence (report plus reviewer basis) | Result |
|---|---|---|---|
| 2.2.a | `:165` includes, cycles, depth, digest conflict | PinTests 14 (`_IncludeCases` `:932`) | met |
| 2.2.b | `:166` lock/verify-lock, no silent pin upgrade | PinTests (`_LockCases` `:1065`) | met |
| 2.2.c | `:167` map/project schema, unmapped blocks, no partial lock | PinTests (`_MappingCases` `:1197`) | met |
| 3.1.a | `:175` capture draft-only in explicit scope | LifecycleTests 9 (`:1312`) | met |
| 3.1.b | `:176` exclusive lock/CAS, catalog-last, index | LifecycleTests | met |
| 3.1.c | `:177` approve newer, deps, deprecate/remove→index | LifecycleTests (`:1430-1432`) | met |
| 3.2.a | `:181` update, events, impact, pins unchanged | MaintenanceTests 10 (`:2164`) | met |
| 3.2.b | `:182` apply, attestations, renewal digest, reduction preview | MaintenanceTests | met |
| 3.2.c | `:183` remove preview, history protection, bounded scan | MaintenanceTests | met |
| 3.3.a | `:187` exact closure export, no private copy or root leak | BundleTests 6 (`:2429`) | met |
| 3.3.b | `:188` children-first import; skill documents operations | BundleTests; SKILL.md names every CLI operation (unchanged bytes); this review is the V18 record | met |
| 4.2.a.core | `:203` verify-lock/projection for BUILD/RESUME | PinTests plus V09 31 | met (core part only) |
| 4.2.b.core | `:206` coverage verdict, exit 7, waived-not-passed | ReviewCoverageTests 5, SelectionReportTests 9, V09 | met (core part only) |

**Proportionality.** No CORE leaf text changed in `ebd087ec..2ce4cfcc`, and no CORE runtime or
test byte changed. The only acceptance change is in non-CORE leaves (RN-14/15/16 wording).

**Reused source assessment.** This reviewer's source-level spec assessment of these exact bytes
still applies:
- ADR-0029 `profile_context` ownership;
- ADR-0028 as the release authority;
- no retired readers restored.

WF parts (4.2.a.wf/4.2.b.wf) and the joined parents are outside this lane.

## Quality review

No findings.

The runtime, CLI, tests and wrapper are byte-identical to the state this reviewer passed for
QUALITY at 8fb265cf, plus the reviewed SKILL.md documentation delta.

The new report is accurate:
- it states the test head (`4c6ce841`) rather than implying execution at `2ce4cfcc`;
- it proves the reuse delta;
- it discloses the snapshot mode quirk, CRLF option (a) and uncleared gates;
- it does not claim this review.

Every hash and count cited in the report was independently rechecked above.

## Verification and limitations

See the checks and limitations in the marker.
- Commands (all read-only and isolated): SHA-256 of the inputs and logs; `git rev-parse`, `diff`,
  `merge-base --is-ancestor`, `ls-files --eol/-s` and `status` on the target; an in-process
  recompute of the acceptance and result digests with `python -I -B`; log parsing.
- Writes: only this file, in this reviewer's session. No write to the CORE repository, shared
  ledger, P05, audit, report or older reviews. No commit.
- The intended repository path `.claude/plans/reusable-patterns/swarm/reviews/CORE.md` is published
  by the coordinator.
