# Specification: first-class swarming work

**Status:** APPROVED for implementation by the operator's 2026-09-08 instruction.
**Scope:** Lintel canonical harness, scaffolding, supported adapters, documentation, tests, and
delivery through PR merge to `main`.
**Design:** [design.md](design.md)

## Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| R1 | Swarming is an opt-in PLAN/BUILD execution profile, not a new cycle phase | ADR, skill contract, unchanged sequential path tests |
| R2 | One committed structure shows topology, ownership, briefs, reports, and reviews | swarm templates and dogfood directory |
| R3 | Existing task/spec/plan authority is not duplicated | additive work-map pointer and reference-only coordination metadata |
| R4 | Unsafe or unattributable swarms fail before dispatch | validator tests for paths, duplicates, missing briefs, overlap, and writer isolation |
| R5 | Every worker receives Lintel startup, scope, acceptance, and report contracts | agent-brief template and swarm skill handoff flow |
| R6 | Shared state and integration remain coordinator-owned | protocol text, scope guard, and review gate |
| R7 | Per-card spec/quality review and final integrated REVIEW both remain mandatory | BUILD/REVIEW integration and evidence checks |
| R8 | Native, sequenced, and no-subagent hosts use the same artifacts honestly | CLI-tier routing and Copilot adapter tests |
| R9 | Fresh sessions can reconstruct the ready frontier without private chat history | RESUME/CAPTURE integration and committed artifacts |
| R10 | The factory, docs, manifests, and generated surfaces ship together without drift | scaffold/Copilot/catalog checks, M1-M4, full suite, CI |

## Interfaces

- `.claude/plans/<initiative>/work.json` keeps schema version 1 and optionally declares
  `execution_mode: "swarm"` plus repository-relative `coordination`.
- `coordination.json` follows `lib/swarm-schema.json` and contains `initiative`, `work_map`,
  `charter`, `integration_branch`, `max_parallel`, and `lanes[]`.
- Every lane contains `task_id`, `wave`, `role`, non-empty `write_scope`, `brief`, `report`, and
  `review`. A multi-writer wave also declares an attributable `isolation` backend. Paths are
  repository-relative POSIX paths and may not escape the repo.
- Worker scope is exactly `write_scope` plus that lane's own `report`; reviewer scope is exactly
  that lane's own `review`. The validator checks both extensions and never treats them as shared
  lane ownership.
- Card text, dependencies, checkboxes, and acceptance remain in the mapped `tasks` artifact.
- `bin/li-swarm.py` is stdlib-only and provides read-only validation/status/scope/evidence gates;
  it never executes artifact content or mutates shared state.

## Constraints

- Preserve old work maps and sequential BUILD unchanged when swarm fields are absent.
- No daemon, network service, database, host-specific orchestration API, or hook dependency.
- No broad globs in write scopes; generated reducers and shared schemas get one owner. Workers do
  not own generated output; the coordinator regenerates it after source-lane fan-in.
- Final verification runs on the reconciled feature branch and never concurrently with another full
  suite.
- No customer data, secrets, production mutation, direct default-branch push, release tag, or
  marketplace publication beyond the explicitly requested PR merge.
