# Agent report: BC5

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-report",
  "initiative": "swarming-work",
  "task_id": "BC5",
  "status": "complete",
  "worker": "swarm_bc5_implement",
  "changed_paths": [
    "README.md",
    "docs/GLOSSARY.md",
    "docs/README.md",
    "docs/architecture.md",
    "docs/concepts/swarming-work.md",
    "docs/faq.md",
    "docs/multi-cli.md",
    "docs/the-cycle.md",
    "skills/brief-forge/SKILL.md",
    "tests/unit/brief-forge-evaluator-runs.sh",
    ".claude/plans/swarming-work/swarm/reports/BC5.md"
  ],
  "checks": [
    {"name": "git diff --check", "status": "PASS"},
    {"name": "tests/shape/no-swedish.sh", "status": "PASS"},
    {"name": "explicit Swedish-letter and high-signal-word scans for untracked swarming-work.md", "status": "PASS"},
    {"name": "tests/shape/frontmatter-lint-all.sh", "status": "PASS"},
    {"name": "tests/shape/skill-descriptions-trigger.sh", "status": "PASS"},
    {"name": "tests/unit/brief-forge-evaluator-runs.sh including all default nested policies and unknown-evaluator blocking", "status": "PASS"},
    {"name": "tests/shape/claude-home-paths.sh", "status": "PASS"},
    {"name": "tests/shape/audit-writes-via-helper.sh", "status": "PASS"},
    {"name": "tests/shape/cli-tiers-sync.sh", "status": "PASS"},
    {"name": "tests/shape/swarm-contract.sh", "status": "PASS"},
    {"name": "tests/unit/swarm-contract.py", "status": "PASS"},
    {"name": "li-swarm.py validate current coordination", "status": "PASS"},
    {"name": "li-swarm.py check-scope BC5 attributable paths", "status": "PASS"},
    {"name": "introduced local Markdown targets exist", "status": "PASS"}
  ],
  "limitations": [
    "No live client smoke test was run in this documentation lane.",
    "The stale public Brief Forge concept page is outside BC5 ownership and needs a coordinator correction before integrated review.",
    "Catalog and wiki regeneration remains coordinator-owned after fan-in."
  ]
}
-->

## Changed files

- `docs/concepts/swarming-work.md` — adds the complete operator guide: selection criteria,
  artifact tree, authority table, lifecycle, trusted helper use, native/sequenced/none degradation,
  failure recovery and the integrated close gate.
- `README.md` and `docs/README.md` — add concise public entry points and capability framing.
- `docs/architecture.md` and `docs/the-cycle.md` — define swarming as an opt-in execution profile
  over PLAN, BUILD and REVIEW, with coordinator-only reducers and final integrated review.
- `docs/multi-cli.md` — explains dispatch and evidence behavior for native, sequenced and
  no-subagent hosts.
- `docs/faq.md` and `docs/GLOSSARY.md` — add operator decisions, recovery answers and canonical
  swarm vocabulary.
- `skills/brief-forge/SKILL.md` — replaces automatic-interception claims with the verified explicit
  invocation contract, names the absent pre-spawn/pre-phase hooks, routes envelope/stats evidence
  through the unified audit policy, resolves its three-level hand-off fields from the authoritative
  merged pack cache, and blocks an evaluator that active-pack integration did not actually load.
- `tests/unit/brief-forge-evaluator-runs.sh` — executes the exact policy helpers extracted from the
  skill, covers every default event plus cold-path policy, and proves an unknown evaluator blocks
  with audit evidence before envelope construction.

## Checks

- `git diff --check` — PASS; no whitespace errors.
- `tests/shape/no-swedish.sh` — PASS; tracked shipped surface is English-only.
- Explicit `rg` scans for Swedish letters and high-signal words in the new untracked concept guide
  — PASS; no matches.
- `tests/shape/frontmatter-lint-all.sh` — PASS; 127 skills and 69 agents met the frontmatter floor.
- `tests/shape/skill-descriptions-trigger.sh` — PASS; Brief Forge remains trigger-form and carries no
  version archaeology.
- `tests/unit/brief-forge-evaluator-runs.sh` — PASS; the three built-ins, envelope helpers, all five
  default event policies, default cold-path bypass, and unknown-evaluator block/audit path passed.
- `tests/shape/claude-home-paths.sh` — PASS; the repository is v5-layout and `_audit.sh` exposes
  scope routing.
- `tests/shape/audit-writes-via-helper.sh` — PASS; executable audit writers remain routed through
  `audit_log`.
- `tests/shape/cli-tiers-sync.sh` — PASS; the generated README capability table still matches
  `lib/cli-tiers.yaml`.
- `tests/shape/swarm-contract.sh` — PASS; workflow links, opt-in fallback, shared parser and task
  authority assertions hold.
- Bundled Python `tests/unit/swarm-contract.py` — PASS; 20 tests.
- Bundled Python `bin/li-swarm.py validate --repo . --coord
  .claude/plans/swarming-work/swarm/coordination.json` — PASS with no diagnostics.
- Bundled Python `bin/li-swarm.py check-scope` for the eleven attributable BC5 paths — PASS with no
  diagnostics.
- Exact existence check for every newly introduced local Markdown target — PASS; no missing target.

## Findings

- `docs/concepts/brief-forge.md` remains a public source of false activation claims. It says every
  hand-off carries an envelope, calls Brief Forge mandatory/automatic, and names nonexistent
  `hooks/shared/brief-forge-pre-spawn.sh` and `hooks/shared/brief-forge-pre-phase.sh`. That file is
  outside BC5's declared write scope. The coordinator was notified and must correct it before the
  integrated review.
- The two Brief Forge lane-review P2 findings are corrected in the owned skill source. The runnable
  sequence and Integration section now agree on explicit `LINTEL_AUDIT_DIR`, v5 repository-local,
  and operator-global fallback routing. They name only security, completeness and stale as built-ins;
  a pack policy name without a pre-sourced function records `brief_forge_blocked` and stops dispatch.
- The final Brief Forge P1 is corrected without widening the generic PackResolver's intentional
  two-level contract. A skill-local block-scoped helper reads
  `brief_forge_handoffs.<event>.{enabled,evaluators}` and `cold_path_bypass.eligible_skills` from the
  already merged session cache. The executable regression reaches all shipped defaults and proves
  an unknown configured evaluator fails closed with an audit record.
- Adding `/li:swarm` changed the `workflow_root` inventory to ten. The glossary now names the actual
  ten roots, including `/li:spec-kit`, instead of retaining the earlier incorrect `uniformity`
  entry.

## Limitations

- No live Claude Code, Codex, Copilot, Cursor, Gemini, OpenCode or Droid client smoke was performed;
  the documentation states declared adapter behavior and evidence boundaries only.
- External links and anchors were not crawled. Newly introduced repository-relative targets were
  checked for exact file existence.
- The full suite belongs to BC6 and was not run concurrently with another lane.

## Downstream notes

- Coordinator reducer: correct `docs/concepts/brief-forge.md` to match explicit invocation and remove
  nonexistent hook claims, then include the page in integrated documentation review.
- Coordinator reducer: regenerate/check `skills/CATALOG.md` and generated wiki surfaces after BC4 and
  BC5 fan-in; do not hand-edit generated files.
- Integrated REVIEW should verify cross-document terminology, final adapter output, link/anchor
  integrity and the reconciled-tree behavior after the Brief Forge reducer correction.
