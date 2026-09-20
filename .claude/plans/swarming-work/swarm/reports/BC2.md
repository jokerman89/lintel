# Agent report: BC2 — swarm contract and deterministic gates

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-report",
  "initiative": "swarming-work",
  "task_id": "BC2",
  "status": "complete",
  "worker": "swarm_bc2_implement",
  "changed_paths": [
    "lib/swarm-schema.json",
    "lib/swarm_contract.py",
    "bin/li-swarm",
    "bin/li-swarm.py",
    "scaffolding/01-foundation/templates/swarm/charter.template.md",
    "scaffolding/01-foundation/templates/swarm/coordination.template.json",
    "scaffolding/01-foundation/templates/swarm/agent-brief.template.md",
    "scaffolding/01-foundation/templates/swarm/agent-report.template.md",
    "scaffolding/01-foundation/templates/swarm/agent-review.template.md",
    "tests/unit/swarm-contract.py",
    ".claude/plans/swarming-work/swarm/reports/BC2.md"
  ],
  "checks": [
    {"name": "python -m py_compile lib/swarm_contract.py bin/li-swarm.py tests/unit/swarm-contract.py", "status": "PASS"},
    {"name": "python tests/unit/swarm-contract.py (20 tests including work-map dispatch state and DEL-ref validation)", "status": "PASS"},
    {"name": "python bin/li-swarm.py validate --repo . --coord .claude/plans/swarming-work/swarm/coordination.json", "status": "PASS"},
    {"name": "python bin/li-swarm.py wave --repo . --coord .claude/plans/swarming-work/swarm/coordination.json (BC2 frontier)", "status": "PASS"},
    {"name": "python bin/li-swarm.py check-scope ...", "status": "PASS"},
    {"name": "git diff --cached --check and executable-mode summary for bin/li-swarm plus bin/li-swarm.py", "status": "PASS"}
  ],
  "limitations": [
    "The repository runner discovers shell wrappers; BC3 owns that integration wrapper.",
    "Per-lane independent review and reconciled-tree integration remain coordinator work."
  ]
}
-->

## Changed files

- `lib/swarm-schema.json` defines the version-1 coordination shape and supported isolation values.
- `lib/swarm_contract.py` supplies the shared stdlib parser, structured diagnostics, canonical
  in-repo path identities, ownership checks, strict evidence states, ready frontier, and close
  verification.
- `bin/li-swarm.py` and `bin/li-swarm` expose read-only `validate`, `wave`, `check-scope`, `status`,
  and `verify` operations.
- `scaffolding/01-foundation/templates/swarm/` provides charter, coordination, brief, report, and
  independent-review templates.
- `tests/unit/swarm-contract.py` covers 20 positive and fail-closed contract cases, including in-repo
  and escaping aliases, universal coordinator roots, pre-review report validation, exact evidence
  types, work-map dispatch state, Git-ref controls, real product-change proof, and clean whitespace.

## Checks

- Bundled Python compile check — PASS.
- Focused unit suite — PASS, 20/20.
- Current initiative validation — PASS with no diagnostics.
- Current initiative ready frontier — PASS, wave 1 contains BC2.
- Attributable BC2 path set — PASS through `check-scope`.
- Staged whitespace and mode check — PASS; both launchers remain mode `100755`.

## Findings

- Markdown evidence uses one embedded JSON marker. This keeps reports readable while giving the
  close gate deterministic data without adding a YAML dependency or executing content.
- Path ownership, protected paths, reviewer ownership, wave overlap, and scope checking compare
  platform-normalized identities after resolving in-repo links; aliases outside the repo fail.
- `.git`, `.claude/runtime`, and `.claude/plans/todo.md` are universal coordinator-only identities;
  direct paths and in-repo aliases fail in topology, patch-scope, and close validation.
- Work-map status is structurally limited to `DRAFT`, `APPROVED`, or `COMPLETE`. Wave dispatch is
  fail-closed unless the value is exactly `APPROVED`; the other valid states remain inspectable.
- Integration branch validation rejects ASCII DEL as well as control characters and unsafe ref
  syntax.
- Evidence accepts only exact integer schema versions, structured checks with nonempty names and an
  exact `PASS` status, string-only limitation lists, its own report path, and at least one changed
  path from declared write scope. A report reaches `awaiting_review` only after every report-side
  gate passes. Paths-file input remains raw so whitespace fails closed.
- Multiple lanes in a wave may omit isolation only when `max_parallel` is 1; the validator emits an
  explicit sequenced-fallback warning.

## Limitations

- The Python unit file is intentionally not a repository-runner entry point. BC3 owns the discovered
  shell wrapper and workflow-level integration fixture.
- This lane does not author its review, mutate shared task state, commit, or integrate.

## Downstream notes

- BC3 should import `validate_work_map_swarm_fields` from `lib/swarm_contract.py` after validating
  the base work map, and use the CLI operations rather than reimplementing the contract.
- The current BC2 report moves its status to `awaiting_review`; the next wave must remain blocked
  until an independent BC2 review artifact passes both stages.
