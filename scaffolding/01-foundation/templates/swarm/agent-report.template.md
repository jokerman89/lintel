# Agent report: <package-id>

Copy the observed identity/result from `li-swarm.py snapshot` for this attempt. Do not invent a
commit, file change or PASS. Record actual checks for every original leaf. Verification-only work
must be explicit in the authoritative plan and has no fabricated product change.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-report",
  "initiative": "replace-me",
  "task_id": "P1",
  "status": "pending",
  "worker": "replace-with-worker-identity",
  "actor_ref": "replace-with-observed-host-session-or-manual-handoff-reference",
  "isolation_ref": "replace-with-attributable-worktree-patch-or-session-handle",
  "work_map": ".claude/plans/replace-me/work.json",
  "package_id": "P1",
  "leaf_ids": [],
  "attempt_id": "replace-with-new-attempt-id",
  "acceptance_digest": "copy-from-snapshot",
  "result": null,
  "result_digest": "copy-from-snapshot",
  "changed_paths": [
    "path/owned-by-p1/file.ext",
    ".claude/plans/replace-me/swarm/reports/P1.md"
  ],
  "leaf_results": {},
  "checks": [],
  "limitations": []
}
-->

## Changed files

- `path/owned-by-p1/file.ext` — what changed and why.

## Checks

- `exact command` — PASS/FAIL and the exact observed result.
- Put the same observed checks under the corresponding leaf IDs in `leaf_results`.

## Findings

- Record implementation findings or `None`.

## Limitations

- Record anything not verified or `None`.

## Downstream notes

- State what the coordinator and dependent lanes need to know.
- File snapshots prove current content/existence, not a Git diff or actor identity. Git mode also
  verifies base/head and the actual changed-path set. Describe the evidence level honestly.
- Historical v1 reports stay historical. A new source/result/attempt needs new bound review;
  shared P05/P08/P09 identity and corroboration are the A22.7 integration boundary.
- This v2 record is a local observation, not the P05 v2 review format. Shared status/frontier/close
  require external caller-selected P05 context/QA and review, live P07 verification, and fresh P09
  observations when declared. Do not put that final context/digest inside the report it hashes.
