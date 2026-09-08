# Independent lane review: BC5 — public swarming surface

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-review",
  "initiative": "swarming-work",
  "task_id": "BC5",
  "status": "complete",
  "reviewer": "swarm_bc5_review",
  "verdict": "PASS",
  "stages": {
    "spec": "PASS",
    "quality": "PASS"
  },
  "checks": [
    {
      "name": "bash tests/unit/brief-forge-evaluator-runs.sh — three built-ins, all five default event policies, cold_path_bypass, default-enabled validation, and unknown-evaluator block/audit",
      "status": "PASS"
    },
    {
      "name": "bash tests/shape/no-swedish.sh — English-only shipped surface",
      "status": "PASS"
    },
    {
      "name": "bash tests/shape/frontmatter-lint-all.sh and tests/shape/skill-descriptions-trigger.sh",
      "status": "PASS"
    },
    {
      "name": "bash tests/shape/claude-home-paths.sh and tests/shape/audit-writes-via-helper.sh — v5 scope routing and unified writer contract",
      "status": "PASS"
    },
    {
      "name": "bash tests/shape/cli-tiers-sync.sh and tests/shape/swarm-contract.sh",
      "status": "PASS"
    },
    {
      "name": "python tests/unit/swarm-contract.py — 20/20 tests",
      "status": "PASS"
    },
    {
      "name": "python bin/li-swarm.py validate against current coordination including coordinator-owned BC5 scope expansion",
      "status": "PASS"
    },
    {
      "name": "python bin/li-swarm.py check-scope for the exact eleven-path BC5 change set",
      "status": "PASS"
    },
    {
      "name": "git diff --check, git diff --cached --check, staged/unstaged ownership inspection, and introduced local Markdown target existence",
      "status": "PASS"
    },
    {
      "name": "Independent static review of nested policy parser allowlists, merged-cache use, pre-construction failure ordering, audit routing, and pack evaluator loading claims",
      "status": "PASS"
    }
  ],
  "limitations": [
    "The full repository suite and final reconciled-tree review remain coordinator-owned BC6 checks.",
    "No live Claude Code, Codex, Copilot, Cursor, Gemini, OpenCode or Droid client smoke was performed.",
    "Linux and macOS execution were unavailable; focused shell checks ran through Windows Git Bash.",
    "External links and anchors were not crawled; newly introduced repository-relative Markdown targets were checked for existence.",
    "docs/concepts/brief-forge.md remains known coordinator fan-in work outside the BC5 lane scope.",
    "The coordinator-owned coordination and BC5 brief scope expansion was reviewed from its current unstaged state and must be included during fan-in."
  ]
}
-->

## Severity counts

P0: 0 · P1: 0 · P2: 0 · P3: 0

## Stage 1 — specification and scope

**PASS. No findings.**

BC5 satisfies its card, brief and R1–R10 documentation responsibilities. The public surface
consistently presents swarming as an explicit PLAN/BUILD/REVIEW profile, preserves mapped-task
authority, distinguishes worker/reviewer/coordinator ownership, requires attributable isolation,
retains final integrated REVIEW, and documents native/sequenced/none degradation, recovery and
unchanged external authority.

The coordinator-owned scope expansion correctly adds `tests/unit/brief-forge-evaluator-runs.sh` to
BC5 ownership and adds executable policy regression to the brief. The exact eleven worker/report
paths pass `check-scope`; the coordination and brief edits themselves remain coordinator-owned.

The corrected Brief Forge sequence reads all five default event policies and
`cold_path_bypass.eligible_skills` from PackResolver's merged immutable cache. Default
`subagent_spawn` resolves enabled with `security,stale`, reaches evaluator validation, and does not
take the disabled bypass. An unknown configured evaluator records `brief_forge_blocked`, names the
unloaded evaluator, returns failure, and executes before envelope construction.

## Stage 2 — quality, security and compatibility

**PASS. No findings.**

The skill-local nested reader preserves PackResolver's intentional two-level public contract. It
allowlists event and field names before reading the merged cache, treats configuration as data,
performs no evaluation or command interpolation, and fails closed on an unreadable or missing
enabled policy.

Built-in inventory is exactly security, completeness and stale. Pack policy selects names but does
not claim to load code; pack-contributed functions must be sourced by trusted active-pack
integration. Unknown functions cannot fall through to the helper's legacy score result in the
documented workflow because validation blocks and audits before construction.

Envelope pointers and emitted/bypassed/blocked statistics consistently use the unified audit
router: explicit `LINTEL_AUDIT_DIR`, then v5 repository-local runtime audit, then operator-global
fallback. The regression extracts the exact marked helper source from the skill, reducing
prose/test drift, and confines fixtures and audit output to a temporary sandbox.

The remaining public Brief Forge concept-page correction is correctly reserved for coordinator
fan-in and does not invalidate the lane result.
