# Independent lane review: BC3 — workflow integration

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-review",
  "initiative": "swarming-work",
  "task_id": "BC3",
  "status": "complete",
  "reviewer": "swarm_bc3_review",
  "verdict": "PASS",
  "stages": {"spec": "PASS", "quality": "PASS"},
  "checks": [
    {"name": "python -B tests/unit/swarm-contract.py — 20/20 tests", "status": "PASS"},
    {"name": "python -B tests/integration/swarm-workflow.py — separate consumer-repository round trip", "status": "PASS"},
    {"name": "bash tests/integration/swarm-workflow.sh — explicit LINTEL_SOURCE_ROOT", "status": "PASS"},
    {"name": "bash tests/shape/swarm-contract.sh — workflow, prerequisite, FEP, trusted-source, and runner assertions", "status": "PASS"},
    {"name": "bash tests/unit/work-artifacts.sh — legacy Lintel and Spec Kit maps", "status": "PASS"},
    {"name": "bash tests/runner/run-all.sh --tag swarm — 2 selected tests passed", "status": "PASS"},
    {"name": "frontmatter-lint-all and full-engineering-pass-contract focused shape checks", "status": "PASS"},
    {"name": "li-work-artifacts.py and li-swarm.py validate/status against the current initiative", "status": "PASS"},
    {"name": "BC3 report evidence and declared 14-path scope validation", "status": "PASS"},
    {"name": "git diff --cached --check and executable-mode verification", "status": "PASS"}
  ],
  "limitations": [
    "The full repository suite and final reconciled-tree REVIEW remain coordinator-owned BC6 checks.",
    "Linux and macOS execution were unavailable; shell entry points were exercised through Windows Git Bash.",
    "Real multi-writer concurrency is coordinator dogfood evidence rather than part of this deterministic fixture.",
    "Scaffolding, generated Copilot outputs, public documentation, catalogs, and manifests remain downstream BC4–BC6 work."
  ]
}
-->

## Severity counts

P0: 0 · P1: 0 · P2: 0 · P3: 0

## Specification review

No findings.

BC3 implements the approved opt-in execution profile without adding a cycle phase or changing
ordinary BUILD. Work-map swarm fields remain atomic, task text and dependencies stay authoritative
in the mapped tasks artifact, and coordination contains execution topology only.

`wave` is correctly described as an evidence/topology candidate rather than authoritative
dependency resolution. SWARM and BUILD require the coordinator to inspect every mapped-card
prerequisite and its completion evidence before handoff, and fail closed back to PLAN when the
candidate topology disagrees.

Worker startup, Brief Forge handoff, attributable isolation, lane scope, separate report/review
ownership, two-stage lane review, serial integration, reducer ownership, final integrated REVIEW,
RESUME recovery, CAPTURE evidence, and honest native/sequenced/none degradation are coherent.

The full-engineering-pass DA/SC stage invokes swarm only when nonempty and explicitly mapped. Its
serial fallback remains real, and a failed swarm marks every selected module FAILED through keys
consumed by the existing SHIP verdict.

## Quality and security review

No findings.

The working repository and installed Lintel source are separated consistently. Swarm helpers resolve
only from explicit `LINTEL_SOURCE_ROOT` or Claude’s `CLAUDE_PLUGIN_ROOT`; other adapters must provide
their known installed bundle path. Missing trusted roots return `NEEDS_CONTEXT`, and the consumer
repository is supplied only as `--repo`.

`li-work-artifacts.py` imports BC2’s shared parser from its own source tree and successfully validates
a distinct temporary consumer repository. Legacy maps without both swarm fields remain valid and
sequential. The new wrappers are discovered by the shell runner and retain mode `100755`.

## Verification and limitations

- BC2 unit contract — PASS, 20/20.
- Mapped consumer-repository workflow round trip — PASS.
- Integration and shape wrappers — PASS.
- Legacy work-artifact fixture — PASS.
- Tagged runner discovery — PASS, 2 selected tests.
- Frontmatter and full-engineering-pass focused checks — PASS.
- Current work map and coordination validation — PASS.
- Staged whitespace, exact scope, and wrapper modes — PASS.
- Full repository suite and final integrated REVIEW remain BC6 work.
- Linux/macOS and a second real multi-writer wave were not exercised in this lane review.
