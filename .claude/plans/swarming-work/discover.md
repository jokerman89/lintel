# Discover report: swarming work

**Date:** 2026-09-08
**Method:** three independent read-only agents plus coordinator verification.

## Existing substrate to reuse

- `skills/build/SKILL.md` already dispatches one bounded implementer per task and separates spec
  from quality review.
- `skills/spec-kit/references/work-map.md` and `bin/li-work-artifacts.py` already provide one
  committed map for cold resume.
- `bin/_jobs.sh` already models step status and dependency gates, but its shared `job.yaml` is a
  coordinator-owned runtime store, not a concurrent worker ledger.
- `lib/envelope-schema.yaml` already defines subagent and reply handoffs.
- `lib/cli-tiers.yaml` already distinguishes native, sequenced, and absent subagent capability.
- `scaffolding/01-foundation/SESSION-PROTOCOL.md` already requires bounded ownership, independent
  review, and coordinated writes to shared state.

## Gaps

- BUILD explicitly prohibits parallel implementers and has no opt-in safe exception.
- No canonical artifact owns waves, write scopes, reducer ownership, agent briefs, or fan-in.
- Work-map validation checks artifact pointers only; it cannot validate swarm ownership or evidence.
- Brief Forge's skill overstates automatic hook activation. Swarming must invoke it explicitly and
  remain correct when hooks are unavailable.
- Copilot generation exposes a selected workflow set and therefore needs a generated `li-swarm`
  adapter; other full-tier plugins discover canonical skills directly.
- The scaffolded subagent guide says local agents live under `.claude/agents/`, while current
  scaffolding deliberately avoids local shadows. The guide needs correction.
- Shared worktree state, the cycle ledger, and full test runner are not concurrency-safe.

## Required integration surface

1. Canonical swarm skill, schema, validator, templates, and dogfood artifacts.
2. PLAN/BUILD/REVIEW/RESUME/CAPTURE/CYCLE integration without changing sequential defaults.
3. Session protocol, subagent guidance, scaffold, and Copilot adapter generation.
4. Architecture/cycle/multi-CLI/public docs and generated catalog/wiki where applicable.
5. Shape, unit, integration, compatibility, and full-suite verification.
6. Unique plugin version across distribution manifests before delivery.

## Risks

- Shared-tree writes can corrupt code or coordination state; disjoint ownership and one coordinator
  are hard invariants, with worktrees as the escape hatch.
- A new task list would split authority; coordination references existing card IDs only.
- Host APIs differ; the skill describes abstract dispatch and records actual execution mode.
- Parallel full suites race on `.claude/runtime/state/00-state.md`; verification runs serially.

