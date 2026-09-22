# Lane review: <package-id>

Use `li-swarm.py review-input` to obtain the exact binding, then perform the review. Exporting
input is not review. Preserve the worker's report; an implementer repairs findings, not the reviewer.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-review",
  "initiative": "replace-me",
  "task_id": "P1",
  "status": "pending",
  "reviewer": "replace-with-independent-reviewer-identity",
  "actor_ref": "replace-with-observed-host-session-or-human-reference",
  "mode": "independent",
  "changed_paths": [".claude/plans/replace-me/swarm/reviews/P1.md"],
  "binding": {
    "work_map": ".claude/plans/replace-me/work.json",
    "package_id": "P1",
    "leaf_ids": [],
    "attempt_id": "copy-from-review-input",
    "acceptance_digest": "copy-from-review-input",
    "result_digest": "copy-from-review-input",
    "report_digest": "copy-from-review-input"
  },
  "verdict": "PENDING",
  "stages": {
    "spec": "PENDING",
    "quality": "PENDING"
  },
  "checks": [],
  "limitations": []
}
-->

## Severity counts

Pending review; do not prefill zero findings.

## Specification review

List findings with `file:line` citations, or `No findings`.

## Quality review

List findings with `file:line` citations, or `No findings`.

## Verification and limitations

Record exact evidence and anything the review could not prove. A reviewer reports; the coordinator
decides and an implementer fixes accepted findings.

Check the reviewer's actual changed paths with `check-scope --actor reviewer` after review.
Use local Git base/head attribution where available. Only an explicitly mechanical package may
record `mode: coordinator`; substantive work still needs a real independent actor. Distinct strings
alone do not corroborate independence. Record the host/human evidence and retain the A22.7 shared
corroboration gate rather than treating these local declarations as final delivery clearance.

This Markdown record remains a local observation. The canonical shared decision is the lane's
`shared_evidence.review` JSON, owned by its reviewer under `.claude/runtime/reviews/`.
Use P05's actual v2 contract and writer; do not construct it by changing this record's version.
The coordinator separately supplies expected context, QA and host/human corroboration. It binds
the raw local report/review before the canonical decision, preventing a self-hashing cycle.
After publication the log-backed P05 reader can revoke older PASS evidence; local inspection never
overrides a later rejection. The final P08 selected-work/resume join remains separately gated.
