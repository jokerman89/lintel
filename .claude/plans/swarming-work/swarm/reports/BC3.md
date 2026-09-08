# Agent report: BC3

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-report",
  "initiative": "swarming-work",
  "task_id": "BC3",
  "status": "complete",
  "worker": "Architect-swarm-bc3",
  "changed_paths": [
    "bin/li-work-artifacts.py",
    "skills/swarm/SKILL.md",
    "skills/plan/SKILL.md",
    "skills/build/SKILL.md",
    "skills/review/SKILL.md",
    "skills/resume/SKILL.md",
    "skills/capture/SKILL.md",
    "skills/cycle/SKILL.md",
    "skills/full-engineering-pass/SKILL.md",
    "skills/spec-kit/references/work-map.md",
    "tests/shape/swarm-contract.sh",
    "tests/integration/swarm-workflow.py",
    "tests/integration/swarm-workflow.sh",
    ".claude/plans/swarming-work/swarm/reports/BC3.md"
  ],
  "checks": [
    {"name": "python tests/unit/swarm-contract.py (20 tests)", "status": "PASS"},
    {"name": "python tests/integration/swarm-workflow.py", "status": "PASS"},
    {"name": "bash tests/integration/swarm-workflow.sh", "status": "PASS"},
    {"name": "bash tests/shape/swarm-contract.sh", "status": "PASS"},
    {"name": "bash tests/unit/work-artifacts.sh with bundled-Python interpreter substitution", "status": "PASS"},
    {"name": "focused existing shape checks", "status": "PASS"},
    {"name": "bash tests/runner/run-all.sh --scope integration (6/6)", "status": "PASS"},
    {"name": "bash tests/runner/run-all.sh --tag swarm (2 selected tests)", "status": "PASS"},
    {"name": "trusted-source fail-closed shape assertions", "status": "PASS"},
    {"name": "li-swarm.py check-scope --task BC3", "status": "PASS"}
  ],
  "limitations": [
    "The full suite and final integrated REVIEW are coordinator-owned BC6 checks and were not run in this lane.",
    "This lane validated deterministic host-tier instructions but did not execute a second real multi-writer wave.",
    "Scaffolding, generated Copilot outputs, public docs, catalogs, and manifests are outside BC3 ownership and remain downstream work."
  ]
}
-->

## Changed files

- `skills/swarm/SKILL.md` — added the opt-in init/run/status/resume/verify workflow, coordinator
  boundaries, Brief Forge handoffs, host-tier degradation, isolation, scope, evidence, integration,
  and recovery rules.
- `skills/{plan,build,review,resume,capture,cycle}/SKILL.md` — connected candidate detection,
  explicit opt-in, candidate-wave BUILD with authoritative prerequisite checks, integrated close
  review, cold resume, durable evidence/M4, and the unchanged nine-phase cycle.
- `skills/full-engineering-pass/SKILL.md` — routed the DA/SC parallel-eligible stage through a
  validated host-aware swarm while preserving the serial fallback.
- `skills/spec-kit/references/work-map.md` — documented the atomic additive fields and kept mapped
  tasks as the sole authority.
- `bin/li-work-artifacts.py` — imported BC2's shared `validate_work_map_swarm_fields` entry point;
  no swarm schema or parser logic was duplicated.
- `tests/shape/swarm-contract.sh` — asserted links, fallback language, shared-parser use, wrapper
  discovery, and absence of task-authority fields from lanes.
- `tests/integration/swarm-workflow.{py,sh}` — added the discovered roundtrip fixture and wrapper;
  it covers legacy maps plus map validation, candidate waves, scope rejection, evidence, and close.

## Checks

- Bundled Python `tests/unit/swarm-contract.py` — PASS, 20/20.
- Bundled Python `tests/integration/swarm-workflow.py` — PASS.
- Git Bash `tests/integration/swarm-workflow.sh` — PASS; invokes both BC2 unit coverage and BC3
  integration coverage.
- Git Bash `tests/shape/swarm-contract.sh` — PASS.
- Legacy `tests/unit/work-artifacts.sh` — PASS using the bundled Python path substituted only in
  the execution stream because this host exposes no `python3` command.
- Focused existing shape checks — PASS: frontmatter, workflow-root navigation, skill descriptions,
  no-Swedish, bin executable modes, and full-engineering-pass contract.
- Ordinary discovery runner `tests/runner/run-all.sh --scope integration` — PASS, 6/6, zero skips,
  failures, or partial assertions.
- Focused discovery runner `tests/runner/run-all.sh --tag swarm` after review fixes — PASS, both
  selected wrapper tests passed.
- `li-swarm.py check-scope --task BC3` over all 14 changed paths — PASS with no diagnostics;
  `status` reports BC3 as `awaiting_review`.
- `git diff --check` — PASS.

## Findings

- The established BUILD anti-pattern was the only direct contradiction: it now prohibits parallel
  implementers outside a validated mapped swarm while leaving ordinary BUILD sequential.
- Independent review identified that BC2's `wave` gate intentionally knows evidence/topology but
  not the task source's dependency semantics. SWARM and BUILD now require the coordinator to verify
  every mapped-card prerequisite and its evidence before handoff, and to return to PLAN on mismatch.
- Independent review also found that the DA/SC stage could call an empty swarm and record failure on
  an unused aggregate key. It now requires a nonempty stage and marks every selected module FAILED,
  which the existing SHIP verdict consumes.
- Final review found that the initial swarm snippets trusted the working repo as a default helper
  source. SWARM, BUILD, REVIEW, RESUME, and the other scoped workflow guidance now resolve only
  explicit `LINTEL_SOURCE_ROOT`, then Claude's `CLAUDE_PLUGIN_ROOT`, and return `NEEDS_CONTEXT`
  before helper invocation when neither exists. Tests/self-checks export the source root explicitly;
  the working repo remains only the `--repo` data argument.
- `li-work-artifacts.py` can remain the single work-map entry point because it delegates optional
  swarm fields to BC2's parser; distributors must therefore ship `lib/swarm_contract.py` and its
  schema with the helper.
- The host's direct Git Bash invocation omits `/usr/bin` and Python from PATH. Checks used an
  explicit hermetic PATH and the bundled runtime; no repository workaround was added.

## Limitations

- The full suite and final integrated REVIEW belong to BC6 and were not duplicated here.
- Real multi-writer concurrency is exercised by the coordinator's isolated lane orchestration, not
  by this deterministic fixture.
- BC4 must propagate canonical skill/templates through scaffold and Copilot resources; BC5 must
  update public guidance and Brief Forge's overstated automatic-hook claims.

## Downstream notes

- BC4 should include `skills/swarm/SKILL.md`, `lib/swarm_contract.py`, `lib/swarm-schema.json`,
  `bin/li-swarm*`, and the swarm templates in portable bundles before generated-output checks.
- The coordinator should regenerate catalogs/wiki and synchronized adapters only after BC4/BC5
  fan-in, then run final scope/evidence validation on the reconciled branch.
