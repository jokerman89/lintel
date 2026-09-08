# Independent lane review: BC2 — swarm contract and deterministic gates

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-review",
  "initiative": "swarming-work",
  "task_id": "BC2",
  "status": "complete",
  "reviewer": "swarm_bc2_review",
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "python -B tests/unit/swarm-contract.py — 20/20 tests",
      "status": "PASS"
    },
    {
      "name": "Independent 26-case adversarial matrix covering aliases, Windows path identity, universal coordinator paths, malformed evidence, strict structured checks, paths-file whitespace, DRAFT/COMPLETE non-dispatch, and DEL-ref rejection",
      "status": "PASS"
    },
    {
      "name": "python -B bin/li-swarm.py validate --repo . --coord .claude/plans/swarming-work/swarm/coordination.json",
      "status": "PASS"
    },
    {
      "name": "python -B bin/li-swarm.py wave and status against the current initiative",
      "status": "PASS"
    },
    {
      "name": "python -B bin/li-swarm.py check-scope for the exact 11-file BC2 staged change set",
      "status": "PASS"
    },
    {
      "name": "python -B bin/li-swarm.py verify returned the expected incomplete-lane failure before review closure",
      "status": "PASS"
    },
    {
      "name": "git diff --cached --check, exact staged-scope inspection, and staged mode verification for both CLI entry points",
      "status": "PASS"
    },
    {
      "name": "Static inspection of all staged BC2 files for standard-library-only, read-only, non-executing behavior",
      "status": "PASS"
    }
  ],
  "limitations": [
    "Full repository-runner integration belongs to BC3 and was not executed in this isolated BC2 review.",
    "Linux and macOS execution were unavailable; the Bash launcher was inspected and its executable mode was verified on Windows."
  ]
}
-->

## Severity counts

P0: 0 · P1: 0 · P2: 0 · P3: 0

## Specification review

No findings.

The implementation traces to ADR-0026, the approved specification, BC2’s build-card requirements,
the swarm charter, and the declared lane scope. It preserves the existing mapped task artifact as
authority while adding coordination-only topology and evidence. Old work maps without swarm fields
remain valid.

The schema, parser, CLI, templates, and tests cover the required topology, safe paths, duplicate
identities, lane ownership, same-wave overlap, isolation, ready-frontier calculation, report/review
evidence, and close gating. The current initiative contract validates successfully.

## Quality review

No findings.

The production implementation uses only Python’s standard library and treats Markdown and JSON
artifacts strictly as data. No artifact execution, subprocess launch, network operation, or shared
state mutation is performed.

Path decisions use repository-contained, symlink-resolved, platform-normalized identities.
Reviewer-owned artifacts, coordination data, universal coordinator paths, escaping aliases, unsafe
drive-qualified paths, overlapping lane scopes, and whitespace-altered changed paths fail closed.

Report and review evidence requires exact integer schema identity, nonempty worker/reviewer
identities, structured check objects with nonempty names and exact `PASS` status, string-only
limitations, declared scope, worker report ownership, a real product change, independent reviewer
identity, and passing specification and quality stages. Invalid report evidence remains
`invalid_report` before review instead of advancing to `awaiting_review`.

Work-map statuses `DRAFT`, `APPROVED`, and `COMPLETE` remain structurally valid, while dispatch is
permitted only for `APPROVED`. Both `DRAFT` and `COMPLETE` return empty ready and dispatch sets with
a fail-closed diagnostic. Unsafe Git ref syntax, including ASCII DEL, is rejected.

## Verification and limitations

- `python -B tests/unit/swarm-contract.py` — PASS, 20/20.
- Independent 26-case adversarial matrix — PASS.
- Current initiative `validate` — PASS with no diagnostics.
- Current initiative `wave` and `status` — PASS; BC2 is `awaiting_review` and no lane dispatches.
- Exact staged BC2 change set through `check-scope` — PASS.
- Current initiative `verify` — expected failure because BC2 awaits review and BC3–BC5 have not
  started.
- `git diff --cached --check` — PASS.
- Staged scope — exactly the 11 declared BC2 files.
- Staged CLI modes — `100755` for both `bin/li-swarm` and `bin/li-swarm.py`.
- Full repository-runner integration belongs to BC3 and was not executed in this isolated review.
- Linux and macOS execution were unavailable; the Bash launcher was inspected and its executable
  mode was verified on Windows.
