# Lane review: CORE (rebind to ebd087ec)

This is an independent local swarm review of CORE consolidation report revision 3.
- Report SHA-256: `190effc22bf64bc6d9e0b07018658c44d113aa6599fe2e089fad201ee2a01bd3`.
- Acceptance is bound at metadata head `ebd087eca0358acde8e3cfc47703e220ec5c30f3`, whose parent
  is `fdb9f27b`.
- Product bytes are unchanged from `fdb9f27b65359d64b343aac5b0aa0e78dc73b536`.

The reviewer is session `c3015de8-134b-499b-bd3d-fa14d965701b`, not the implementer.

This record supersedes nothing by editing. The earlier fdb-bound review, `CORE.md` with SHA-256
`cea7831d994f9fde6c00cb5450c03807ed355d81149318f092ae3c458acb06d3`, is preserved unchanged as
history. It binds the stale acceptance `1596254e…` and report `7c102292…`, and does not approve ebd.

This is a local observation. It is not a P05 native v2 decision, QA, corroboration, or
integrated/release clearance.

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
    "attempt_id": "reusable-patterns-CORE-consolidation-ebd087ec-1",
    "acceptance_digest": "4be8bb68642b3b4cc07b3662f9009de3b838a4a0f6eaa001809e43bb837fce7b",
    "result_digest": "47c6960c1bb4368189cd4a3efe31cdca0132d1411dbb9a9e68872f708d8b1033",
    "report_digest": "190effc22bf64bc6d9e0b07018658c44d113aa6599fe2e089fad201ee2a01bd3"
  },
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "Acceptance delta fdb9f27b..ebd087ec read from actual Git",
      "status": "PASS",
      "observed": "git diff in clean clone lp64\\review\\e (HEAD ebd087ec, parent fdb9f27b): only plan.md (1 line: 5.2.a PENDING note now says V17 case A observed the li-cycle/li-build project_visual route, not generate-web; generate-web cell open) and build-log.md (INT review Info count 1->7; LF-only claim corrected to drop an unasserted trailing-newline assertion; 5.2.a deferred row). No CORE leaf text (2.2.*, 3.1.*, 3.2.*, 3.3.*, 4.2.a.core, 4.2.b.core) changed; 5.2.a is a WF/visual leaf and its pending state is not CORE coverage"
    },
    {
      "name": "Binding and result byte identity at ebd087ec",
      "status": "PASS",
      "observed": "report sha256 190effc2... recomputed; scratch review-input (sha256 47316c1b...) ok with no diagnostics and exact binding; result equals CORE.json snapshot; git diff --quiet fdb9f27b ebd087ec over all five write_scope paths rc 0; all five file sha256 values at ebd recomputed and equal to result (li-pattern.py 49cb6a2c, patterns.py 7742521e, SKILL.md bca7ad1e, tests/unit/patterns.py 1b247ff7, patterns.sh d9dd1c29)"
    },
    {
      "name": "Report revision 3 difference from revision 2",
      "status": "PASS",
      "observed": "git diff --no-index r2 (7c102292) vs r3 (190effc2): only the header head wording, attempt_id, acceptance_digest and one added limitation disclosing the rebind; leaf_results, checks, result and result_digest unchanged"
    },
    {
      "name": "Reused product tests (prior reviewer observation on identical bytes, not rerun)",
      "status": "PASS",
      "observed": "Reviewer-run at fdb9f27b (2026-09-28): Pin/Lifecycle/Maintenance/Bundle/ReviewCoverage/SelectionReport/CoreReview 62 tests OK, log sha256 8c82b6c7d2b137159a89234575686061cc20c3bd55cd80d8e468c5317acd417c; V09 pattern-workflows 31 OK, log sha256 91c0fd57845fcf4a747149475fa6ec91eea9c7b0ee928b5dd10aad8eb2e9764f. Valid for ebd only because write_scope bytes are identical (check above) and no CORE test or runtime dependency changed in fdb..ebd"
    },
    {
      "name": "Per-leaf mapping and V18 source review (reused, unchanged inputs)",
      "status": "PASS",
      "observed": "The mapping verified in review cea7831d (AST of tests/unit/patterns.py; plan leaf text) is still exact. CORE plan leaf lines and test bytes are unchanged at ebd. The CORE runtime is byte-identical to the reviewer-passed 8fb265cf, apart from the already-reviewed SKILL.md docs delta"
    }
  ],
  "limitations": [
    "The result is a FILE snapshot, not Git attribution. CORE commits are interleaved with same-actor coordinator/INT commits; skills/pattern/SKILL.md coordinator edits (87c2b476, ea2c139d) are not separated. No commit attribution is claimed.",
    "The file snapshot records mode 100644 for bin/li-pattern.py while the Git index has 100755 (core.filemode=false); this is a helper representation limit.",
    "No product test was rerun for ebd. Test evidence is this reviewer's fdb run, reused on byte-identical write_scope content. Windows only; the full 137-test suite was not rerun by this reviewer. Linux 137 OK at 8fb265cf is parent-observed.",
    "The build-log corrections (INT Info count, LF claim) are coordinator/INT metadata outside CORE scope. They were read for coupling only and are not reviewed as INT work.",
    "Leaf 5.2.a remains PENDING, with the generate-web, design-dna, typography, motion, shader and generate-app cells open. That is WF/visual and host scope; neither this PASS nor CORE coverage covers it.",
    "Export CORE.json field evidence_level still says 'at fdb'. That is accurate for product bytes, and it is export metadata, not the bound report.",
    "Known product limits are retained: unkeyed digests authenticate no one; Windows paths over about 260 characters report missing; the casefold namespace rule is portable-safe only.",
    "This is local swarm-review evidence only. No P05 context, QA or corroboration exists. WF, host, INT and publication gates remain open. release_clearance is false."
  ]
}
-->

## Severity counts

| P0 | P1 | P2 | P3 |
|---|---|---|---|
| 0 | 0 | 0 | 0 |

## Specification review

No findings.

The fdb..ebd acceptance change updates `plan.md:229`, the 5.2.a wording, and `build-log.md` hunks
at about lines 997, 1010 and 1046. None of these changes any CORE member leaf, its verification
key or a CORE-scoped file. The revision 3 per-leaf mapping is unchanged from revision 2, which
this reviewer verified against the test class contents. It remains correct at ebd.

The more conservative 5.2.a note, which states that generate-web is unobserved, narrows a WF/visual
host claim. It does not create or remove any CORE obligation.

## Quality review

No findings.

The product bytes at ebd are identical to fdb, and CORE's runtime is identical to the reviewed
8fb265cf. Revision 3 of the report discloses the rebind honestly and does not restate its checks
as new runs.

## Verification and limitations

See the checks and limitations in the marker. Reused test logs are in this session's
`files\swarm-consolidation\logs\`. The fdb review `CORE.md` (`cea7831d…`) is kept byte-identical.

No source, plan, report, old review, shared-clone or P05 writes were made. There were no commits,
network access or installs. The intended repository path is
`.claude/plans/reusable-patterns/swarm/reviews/CORE.md`. Publishing it there, and preserving the
history, are the parent's responsibility.
