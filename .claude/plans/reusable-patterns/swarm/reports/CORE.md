# Agent report: CORE

Current CORE report for attempt `reusable-patterns-CORE-integration-2ce4cfcc-1` at the frozen integrated candidate
`2ce4cfcc062e6806e0b3349d5e49a443097d4737` (tree `52900c7d562dcb5aa6a6701446e98a44645e2c0d`).
Identity is copied from `li-swarm.py snapshot` (file mode). This is a new report for a new
attempt, not a rebinding of an earlier verdict.

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
  "attempt_id": "reusable-patterns-CORE-integration-2ce4cfcc-1",
  "acceptance_digest": "2773195fe94204ab0fb18bf6b7dceeebe7e487841d4b294af9dbc852f9f32a0f",
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
        "name": "V06 PinTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "14 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "2.2.b": [
      {
        "name": "V06 PinTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "14 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "2.2.c": [
      {
        "name": "V06 PinTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "14 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.1.a": [
      {
        "name": "V07 LifecycleTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "9 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.1.b": [
      {
        "name": "V07 LifecycleTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "9 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.1.c": [
      {
        "name": "V07 LifecycleTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "9 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.2.a": [
      {
        "name": "V07 MaintenanceTests (in tests/unit/patterns.sh; 3.2 behavior)",
        "status": "PASS",
        "observed": "10 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.2.b": [
      {
        "name": "V07 MaintenanceTests (in tests/unit/patterns.sh; 3.2 behavior)",
        "status": "PASS",
        "observed": "10 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.2.c": [
      {
        "name": "V07 MaintenanceTests (in tests/unit/patterns.sh; 3.2 behavior)",
        "status": "PASS",
        "observed": "10 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.3.a": [
      {
        "name": "V08 BundleTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "6 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      }
    ],
    "3.3.b": [
      {
        "name": "V08 BundleTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "6 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      },
      {
        "name": "V18 independent source/diff review record",
        "status": "PASS",
        "observed": "Historical milestone acceptance of the CORE interface by reviewer c3015de8 at 1575a90a, 56d750d6 and 8fb265cf, and its CORE lane review of the ebd087ec-bound report; cited as history, not transferred as a verdict for this attempt. The current lane review for this attempt is pending."
      }
    ],
    "4.2.a.core": [
      {
        "name": "V06 PinTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "14 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      },
      {
        "name": "V09 tests/integration/pattern-workflows.sh",
        "status": "PASS",
        "observed": "Ran 31, OK, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-V09-workflows.log sha256 1342d9d40e04341a1c87bb4726614922dde4e982ac26d730453c18b06119c4a0"
      }
    ],
    "4.2.b.core": [
      {
        "name": "ReviewCoverageTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "5 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      },
      {
        "name": "SelectionReportTests (in tests/unit/patterns.sh)",
        "status": "PASS",
        "observed": "9 ok, 0 fail, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
      },
      {
        "name": "V09 tests/integration/pattern-workflows.sh",
        "status": "PASS",
        "observed": "Ran 31, OK, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-V09-workflows.log sha256 1342d9d40e04341a1c87bb4726614922dde4e982ac26d730453c18b06119c4a0"
      }
    ]
  },
  "checks": [
    {
      "name": "tests/unit/patterns.sh (whole file)",
      "status": "PASS",
      "observed": "Ran 137, OK, 0 skip; executed at 4c6ce841781bd4467a2f75d3853170cadf782549 (Windows, positive-allowlist parent+child, synthetic home/temp); CORE scope bytes identical at 2ce4cfcc; C:\\Users\\jokerman\\.copilot\\session-state\\11d27634-94dc-4a1a-8453-602cd1dbf84b\\files\\native-join\\t\\j-unit-patterns.log sha256 3d23c7d130ac7ba55d28aa28cfe024a11dcb79169a3a2d06968e9d81d665f72f"
    },
    {
      "name": "CORE scope byte identity ebd087ec..2ce4cfcc",
      "status": "PASS",
      "observed": "git diff ebd087ec 2ce4cfcc over the five write_scope paths is empty; result_digest 47c6960c\u2026 equals the ebd087ec-bound attempt"
    }
  ],
  "limitations": [
    "Result is a FILE snapshot of write_scope at 2ce4cfcc: current content, not a Git worker delta; CORE commits interleave with coordinator/INT commits by the same actor.",
    "skills/pattern/SKILL.md, in CORE scope, was also changed in the coordinator/INT role (87c2b476, ea2c139d); not separated.",
    "File-mode snapshot records 100644 for bin/li-pattern.py whose Git index mode is 100755 (known snapshot-layer limitation).",
    "Tests executed at 4c6ce841, not at 2ce4cfcc; reuse rests on zero CORE-scope Git delta and a 4c6ce841..2ce4cfcc delta limited to two unrelated tests and build logs.",
    "The P05 snapshot binds this Windows worktree's raw bytes; 8 selected files differ from HEAD only by CRLF line endings (owner decision (a)).",
    "Not cleared: the current CORE lane review, P05 lane context/QA/corroboration, the final aggregate review, hosted Windows/Linux full suites on the candidate and publication. No release clearance."
  ]
}
-->

## Changed files

The CORE write scope is byte-identical to the `ebd087ec`-bound attempt (`git diff ebd087ec 2ce4cfcc`
over the five paths is empty; result digest `47c6960c…` unchanged). The implementation history:

- `lib/patterns.py`, `bin/li-pattern.py`: P0/P1 `2d750892`, review revisions R1 to R11, portability
  fix `8fb265cf`.
- `tests/unit/patterns.py`, `tests/unit/patterns.sh`: 137 tests and the registered wrapper.
- `skills/pattern/SKILL.md`: the canonical workflow, also edited in the INT role.

## Checks

- `tests/unit/patterns.sh` at `4c6ce841`: 137 OK, no skip. Per class: PinTests 14, LifecycleTests 9,
  MaintenanceTests 10, BundleTests 6, ReviewCoverageTests 5, SelectionReportTests 9, all ok.
- `tests/integration/pattern-workflows.sh` (V09) at `4c6ce841`: 31 OK.
- Reuse proof: CORE scope unchanged since `ebd087ec`; `4c6ce841..2ce4cfcc` changes only
  `tests/integration/pattern-portability.py`, `tests/unit/wiki-gen-idempotency.sh` and two build logs.

## Findings

- None open in CORE.

## Limitations

See `limitations` in the record. Final shared gates are not cleared.

## Downstream notes

- The CORE lane review must come from a real independent reviewer for this attempt.
- The repository report slot is not written yet; the coordinator publishes after all actual reports and reviews exist, then re-prepares the final P05 context.
