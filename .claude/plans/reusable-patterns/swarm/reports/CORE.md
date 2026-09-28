# Agent report: CORE

Evidence-only consolidation of CORE's implemented and reviewed work. Product bytes frozen at
`fdb9f27b65359d64b343aac5b0aa0e78dc73b536`; acceptance bound at metadata head
`ebd087eca0358acde8e3cfc47703e220ec5c30f3`. Identity copied from `li-swarm.py snapshot`
(file mode, attempt `reusable-patterns-CORE-consolidation-fdb9f27b-1`). No new implementation was done for this report.

<!-- lintel-swarm-evidence:v2
{
  "schema_version": 2,
  "artifact_kind": "swarm-report",
  "initiative": "reusable-patterns",
  "task_id": "CORE",
  "status": "complete",
  "worker": "github-copilot-app:claude-opus-5.5:reusable-patterns-core-integration-owner",
  "actor_ref": "copilot-session:11d27634-94dc-4a1a-8453-602cd1dbf84b",
  "isolation_ref": "branch jokerman-microsoft-patterns-core-integration in worktree jokerman-microsoft-upgraded-doodle; shared with the coordinator/INT role, no separate lane worktree",
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
  "result": {
    "base": null,
    "files": {
      "bin/li-pattern.py": {
        "digest": "49cb6a2c638403608ba22f2e6b8e9018e04224638388a6e0687b11f39f859721",
        "mode": "100644",
        "type": "file"
      },
      "lib/patterns.py": {
        "digest": "7742521e7ec49b02998ebc5dbc929ecf270d419898b3f8311fedca8a812a94c1",
        "mode": "100644",
        "type": "file"
      },
      "skills/pattern/SKILL.md": {
        "digest": "bca7ad1e498b4f72d5b2b06bb2ad8d2fd0ef8327ed6aaf1827b06ba331bf2602",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/patterns.py": {
        "digest": "1b247ff77437ccbf58d8a689b8111c2eedbeb2f0d4a2b6e58689cf8b4666b932",
        "mode": "100644",
        "type": "file"
      },
      "tests/unit/patterns.sh": {
        "digest": "d9dd1c290b5ed57d6b12ee6b8c1ff2b31732a2ce39c2925036fedb083733323b",
        "mode": "100644",
        "type": "file"
      }
    },
    "head": null,
    "kind": "files"
  },
  "result_digest": "47c6960c1bb4368189cd4a3efe31cdca0132d1411dbb9a9e68872f708d8b1033",
  "changed_paths": [
    "bin/li-pattern.py",
    "lib/patterns.py",
    "skills/pattern/SKILL.md",
    "tests/unit/patterns.py",
    "tests/unit/patterns.sh",
    ".claude/plans/reusable-patterns/swarm/reports/CORE.md"
  ],
  "leaf_results": {
    "2.2.a": [
      {
        "name": "V06 python -I -B tests/unit/patterns.py PinTests",
        "status": "PASS",
        "observed": "Ran 14 tests, OK, 0 skipped (include, lock and mapping cases); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 9cfd1fcdf8aa9cec7fb9951671e5cbd75939bc365704f412b6101e81513c7278"
      }
    ],
    "2.2.b": [
      {
        "name": "V06 python -I -B tests/unit/patterns.py PinTests",
        "status": "PASS",
        "observed": "Ran 14 tests, OK, 0 skipped (include, lock and mapping cases); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 9cfd1fcdf8aa9cec7fb9951671e5cbd75939bc365704f412b6101e81513c7278"
      }
    ],
    "2.2.c": [
      {
        "name": "V06 python -I -B tests/unit/patterns.py PinTests",
        "status": "PASS",
        "observed": "Ran 14 tests, OK, 0 skipped (include, lock and mapping cases); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 9cfd1fcdf8aa9cec7fb9951671e5cbd75939bc365704f412b6101e81513c7278"
      }
    ],
    "3.1.a": [
      {
        "name": "V07 python -I -B tests/unit/patterns.py LifecycleTests",
        "status": "PASS",
        "observed": "Ran 9 tests, OK, 0 skipped (capture, lock/staging, index, approve); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 c99c1fd7b9d8d0c429d8b688aecc5769e865bfab8d3c2254742671f2b32e8d31"
      }
    ],
    "3.1.b": [
      {
        "name": "V07 python -I -B tests/unit/patterns.py LifecycleTests",
        "status": "PASS",
        "observed": "Ran 9 tests, OK, 0 skipped (capture, lock/staging, index, approve); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 c99c1fd7b9d8d0c429d8b688aecc5769e865bfab8d3c2254742671f2b32e8d31"
      }
    ],
    "3.1.c": [
      {
        "name": "V07 python -I -B tests/unit/patterns.py LifecycleTests",
        "status": "PASS",
        "observed": "Ran 9 tests, OK, 0 skipped (capture, lock/staging, index, approve); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 c99c1fd7b9d8d0c429d8b688aecc5769e865bfab8d3c2254742671f2b32e8d31"
      }
    ],
    "3.2.a": [
      {
        "name": "V07 (3.2 coverage) python -I -B tests/unit/patterns.py -v MaintenanceTests",
        "status": "PASS",
        "observed": "Ran 10 tests, OK, 0 skipped (update/impact, lifecycle events, apply add/replace/remove, URL/overdue attestations, renewal digest, remove protection, bounded lock scan, CLI); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 74db1c18c1a9e51310987b2e7658bc329cf168b132c54ba1405c4a1ed6270d19"
      }
    ],
    "3.2.b": [
      {
        "name": "V07 (3.2 coverage) python -I -B tests/unit/patterns.py -v MaintenanceTests",
        "status": "PASS",
        "observed": "Ran 10 tests, OK, 0 skipped (update/impact, lifecycle events, apply add/replace/remove, URL/overdue attestations, renewal digest, remove protection, bounded lock scan, CLI); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 74db1c18c1a9e51310987b2e7658bc329cf168b132c54ba1405c4a1ed6270d19"
      }
    ],
    "3.2.c": [
      {
        "name": "V07 (3.2 coverage) python -I -B tests/unit/patterns.py -v MaintenanceTests",
        "status": "PASS",
        "observed": "Ran 10 tests, OK, 0 skipped (update/impact, lifecycle events, apply add/replace/remove, URL/overdue attestations, renewal digest, remove protection, bounded lock scan, CLI); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 74db1c18c1a9e51310987b2e7658bc329cf168b132c54ba1405c4a1ed6270d19"
      }
    ],
    "3.3.a": [
      {
        "name": "V08 python -I -B tests/unit/patterns.py BundleTests",
        "status": "PASS",
        "observed": "Ran 6 tests, OK, 0 skipped; clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 5db64ea98ba69abca21dce6c70daa81a0534c10f0b4fb9a3f62ba79d39398155"
      }
    ],
    "3.3.b": [
      {
        "name": "V08 python -I -B tests/unit/patterns.py BundleTests",
        "status": "PASS",
        "observed": "Ran 6 tests, OK, 0 skipped; clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 5db64ea98ba69abca21dce6c70daa81a0534c10f0b4fb9a3f62ba79d39398155"
      },
      {
        "name": "V18 independent source/diff review record",
        "status": "PASS",
        "observed": "Reviewer c3015de8 SPEC/QUALITY PASS on the CORE interface at R9 1575a90a, R11 56d750d6 and portability 8fb265cf (0 P0/P1/P2); reports in that reviewer's session files. Milestone acceptance only, not ADR-0028 v2 clearance."
      }
    ],
    "4.2.a.core": [
      {
        "name": "V06 python -I -B tests/unit/patterns.py PinTests",
        "status": "PASS",
        "observed": "Ran 14 tests, OK, 0 skipped (include, lock and mapping cases); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 9cfd1fcdf8aa9cec7fb9951671e5cbd75939bc365704f412b6101e81513c7278"
      },
      {
        "name": "V09 python -I -B tests/integration/pattern-workflows.py",
        "status": "PASS",
        "observed": "Ran 31 tests, OK, 0 skipped (WF-owned test exercising the core helpers); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 096c32eea6136c5d1574f589c8e3c3dfdb59ac46b6f4354789f3f6bdba22758b"
      }
    ],
    "4.2.b.core": [
      {
        "name": "python -I -B tests/unit/patterns.py -v ReviewCoverageTests",
        "status": "PASS",
        "observed": "Ran 5 tests, OK, 0 skipped (coverage verdict, exit 7 on missing/failed/unverified/skipped mandatory, waiver needs locked exception, stale mapping, unmapped lock); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 70872376d522f326e4f6ee9128fb3c213b5635fd9459e06c54fa6112512ac03e"
      },
      {
        "name": "python -I -B tests/unit/patterns.py -v SelectionReportTests",
        "status": "PASS",
        "observed": "Ran 9 tests, OK, 0 skipped (public validate_selection_report); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 9608fc1e44174623397a98851907c8ad69642dcf51af23abff463f8b4498223a"
      },
      {
        "name": "V09 python -I -B tests/integration/pattern-workflows.py",
        "status": "PASS",
        "observed": "Ran 31 tests, OK, 0 skipped (WF-owned test exercising the core helpers); clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 096c32eea6136c5d1574f589c8e3c3dfdb59ac46b6f4354789f3f6bdba22758b"
      }
    ]
  },
  "checks": [
    {
      "name": "python -I -B tests/unit/patterns.py (all)",
      "status": "PASS",
      "observed": "Ran 137 tests, OK, 0 skipped; clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 c9c82f2d19c914f2766f61762dbf82ee421d1aa5b29174614cdfc0bcc3efe37b"
    },
    {
      "name": "bash tests/unit/patterns.sh (registered wrapper)",
      "status": "PASS",
      "observed": "Ran 137 tests, OK; clean LF clone of fdb9f27b, synthetic HOME/TEMP, Windows Python 3.11.9; log sha256 a797b148be846efc7e34132b8ea32e2ce4272b511729f6803f7aa659add525af"
    },
    {
      "name": "Linux python3 -I -B tests/unit/patterns.py at 8fb265cf (parent-run)",
      "status": "PASS",
      "observed": "Ran 137 tests, OK; parent artifact posix-8fb-patterns.log. Product core bytes unchanged from 8fb265cf to fdb9f27b except skills/pattern/SKILL.md docs."
    }
  ],
  "limitations": [
    "Result is a FILE snapshot of write_scope at fdb9f27b: it proves current content, not a Git worker delta. The CORE commits are interleaved on the integration branch with coordinator/INT commits by the same actor.",
    "skills/pattern/SKILL.md, in CORE scope, was also changed in the coordinator/INT role by 87c2b476 and ea2c139d; these are not separated out.",
    "File-mode snapshot records 100644 for bin/li-pattern.py whose Git index mode is 100755 (core.filemode=false clone); bin-scripts-executable and git ls-files -s show 100755.",
    "Local tests only; host acceptance of core behavior is limited to the coordinator-observed V17 cases on b8312bb7 (A, B, D). Not release clearance; no native ADR-0028 v2 review exists yet.",
    "Known limits kept: unkeyed digests authenticate no one; Windows paths over about 260 characters report missing (R12); Unicode casefold restriction is portable-safe, not a universal filesystem guarantee.",
    "The plan's V07 command key names only LifecycleTests; the 3.2 update/apply/attestation/remove behavior is tested in MaintenanceTests, run separately here and included in the 137. The per-leaf mapping above is explicit; a class name alone is not proof, so the reviewer should read the cited test names.",
    "Revision 3 rebinds revision 2 (7c102292) to acceptance at ebd087ec after the plan's 5.2.a wording correction (not a CORE leaf). CORE product bytes, result and all checks are unchanged; the checks were run at fdb9f27b, whose write_scope bytes equal ebd087ec's."
  ]
}
-->

## Changed files

- `lib/patterns.py` — typed data-only core: schemas, paths, selectors, authority, locks, lifecycle,
  sharing, attestations, review coverage and the public `validate_selection_report` helper.
- `bin/li-pattern.py` — the JSON CLI over the core (spec section 7, contract.md).
- `tests/unit/patterns.py`, `tests/unit/patterns.sh` — 137 unit tests and the registered wrapper.
- `skills/pattern/SKILL.md` — canonical pattern workflow (CORE-owned; also edited in the INT role).

## Checks

- V06 PinTests: 14 OK (2.2.*, 4.2.a.core). V07 LifecycleTests: 9 OK (3.1.*).
- MaintenanceTests: 10 OK (3.2.*; the V07 key names only LifecycleTests). V08 BundleTests: 6 OK (3.3.*).
- ReviewCoverageTests: 5 OK and SelectionReportTests: 9 OK (4.2.b.core).
- `tests/unit/patterns.py`: 137 OK; wrapper 137 OK. V09 `pattern-workflows.py`: 31 OK. No skips.
- All run in a clean LF clone of `fdb9f27b` with synthetic roots; log digests are in the record.
- Linux 137 OK at `8fb265cf` is the parent's run, cited, not re-run here.

## Original records

- P0/P1 `2d750892` (parent `7ba544a4`); review revisions R1-R11 and the portability fix
  `8fb265cf`, each an ordinary commit; build-log.md and contract.md record every revision.
- Independent reviewer c3015de8 accepted R9 `1575a90a`, R11 `56d750d6` and `8fb265cf`
  (SPEC/QUALITY PASS). Those are milestone acceptances, not this lane's swarm review.

## Findings

- None open in CORE.

## Limitations

- See `limitations` above: file snapshot, not Git attribution; same-actor coordinator edits in
  `skills/pattern/SKILL.md`; the file-mode executable-bit representation; no release clearance.

## Downstream notes

- The lane review must be a real independent reviewer writing only
  `.claude/plans/reusable-patterns/swarm/reviews/CORE.md` and its P05 JSON.
- Committing this report changes a selected path; the final P05 context must be re-prepared.
