# Independent lane review: BC4

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-review",
  "initiative": "swarming-work",
  "task_id": "BC4",
  "status": "complete",
  "reviewer": "CodeReviewer-swarm-bc4-review",
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "documented Copilot environment selects installed LINTEL_SOURCE_ROOT for bundled li-scaffold",
      "status": "PASS"
    },
    {
      "name": "source-checkout and scaffold-consumer template paths are both documented accurately",
      "status": "PASS"
    },
    {
      "name": "removal of every mandatory SWARM_RESOURCES dependency refuses before target writes",
      "status": "PASS"
    },
    {
      "name": "synchronized tests/integration/copilot-kit.py, 22 tests",
      "status": "PASS"
    },
    {
      "name": "tests/unit/session-protocol-sync.sh",
      "status": "PASS"
    },
    {
      "name": "li-swarm.py check-scope for all staged BC4 paths",
      "status": "PASS"
    },
    {
      "name": "bundled scaffold idempotent rerun and swarm-template installation",
      "status": "PASS"
    },
    {
      "name": "git diff --cached --check",
      "status": "PASS"
    }
  ],
  "limitations": [
    "The four coordinator-owned protocol consumers remain intentionally drifted in the isolated lane and were synchronized only in a temporary review copy.",
    "Generated repository Copilot outputs remain coordinator-owned and were not changed in this lane.",
    "No authenticated Copilot client, cloud-agent execution, enterprise tenant policy, push, deployment, production behavior, or integrated full repository suite was exercised."
  ]
}
-->

## Severity counts

P0: 0 · P1: 0 · P2: 0 · P3: 0

## Specification review

No findings. The lane implements BC4/R5/R6/R8/R10 within its declared ownership. The canonical
protocol source, subagent guides, scaffold factory, Copilot generator and integration assertions
compose correctly after the coordinator-owned protocol reducer runs.

The prior source-root defect is closed: `li-scaffold` prefers adapter-supplied
`LINTEL_SOURCE_ROOT`, retains executable-relative standalone fallback and does not reinterpret
Copilot's repository-runtime `LINTEL_HOME` as installed source.

The guides now distinguish canonical templates in a Lintel source checkout from copied templates
in a scaffolded consumer. The staged path set contains only declared BC4 sources/tests plus BC4's
own report.

## Quality review

No findings. The Copilot generator preflights all 21 direct swarm workflow, validation, handoff,
policy, audit/path, environment and template dependencies. The negative test removes each member
individually and proves generation fails before writes.

Scaffolding remains non-clobbering and idempotent, creates no repository-local agent fleet, and
installs all five templates as user-owned seeds. Existing traversal, collision, CRLF, clone,
inventory, protocol-preservation and environment behavior remains green in the complete 22-test
Copilot suite.

## Verification and limitations

- Full `tests/integration/copilot-kit.py` on a temporary copy after the real protocol synchronizer:
  PASS, 22/22.
- `tests/unit/session-protocol-sync.sh`: PASS.
- `bin/li-swarm.py check-scope` over every staged BC4 path: PASS with no diagnostics.
- Documented Copilot bootstrap followed by bundled scaffold initialization and idempotent rerun:
  PASS.
- Direct `bin/li-instructions.py check` reports only the four expected coordinator-owned drift
  targets; the synchronized temporary copy passes.
- `git diff --cached --check`: PASS.
- No authenticated Copilot client, cloud execution, tenant policy or complete integrated repository
  suite was tested. Those remain coordinator/BC6 verification boundaries.
