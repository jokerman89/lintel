# Lintel maintainer gates

This is the single method owner for M1–M4. Load it only for `meta-infra` work
modifying Lintel itself, as selected by the operator or the existing SENSE Step 0c
path detection with its operator override. This is not a new opt-in: when that
mode applies, all four gates remain required at their existing phase boundaries.
Read the applicable gate before its phase; do not run maintainer procedures for
an unrelated consumer task or treat a skipped phase as completed gate evidence.

`meta-infra` is the operator's mode when modifying Lintel itself (scaffolding). Lintel changes ripple across every downstream cycle, so REVIEW + CAPTURE run heavier and four meta-gates activate:

**M1 — Structure-impact assessment** (in DEFINE)
Before merging design, write a structure-changes/<date>-<slug>.md entry documenting: what changed, backward-compat, migration path, forward-compat, verification, rollback. Template: `.claude/engineering/evolution/_TEMPLATE.md`.

**M2 — Compatibility audit** (in REVIEW)
Run `bin/li-compat-audit` to produce mechanical GREEN/YELLOW/RED sweep across four questions:
1. Did any frontmatter contract change? (REQUIRED_SKILL_FIELDS, REQUIRED_AGENT_FIELDS)
2. Were skills/agents/hooks renamed or moved?
3. Did defaults change for any existing field?
4. Did any shared helper signature change? (lib/*.sh)

Output: `.claude/engineering/compat-audits/<date>-<slug>.md`. RED requires explicit override.

**M3 — Shape-tests** (in REVIEW)
Run `bash tests/runner/run-all.sh --shape-only`. The 8 shape-tests assert structural invariants (see `tests/shape/_README.md`). Any FAIL blocks SHIP.

**M4 — Future-operator clarity** (in CAPTURE)
CAPTURE writes a recap that future-operator (or future-you) can use cold. Specifically: surface every migration that future operators need to run, every new convention introduced, every deprecated path. Append to `docs/migrations/_INDEX.md` if any migration ships.

## M4 swarm recap

Load this additional M4 detail only when `mode=meta-infra` and the selected work
map opts into swarming. Ordinary swarm evidence still belongs to
[CAPTURE Step 6a](../../capture/SKILL.md#step-6a--reaffirm-swarm-evidence-and-future-operator-clarity);
this reference does not replace its integrated REVIEW/SHIP conditions.

For meta-infra M4, the future-operator recap must name:

- the explicit opt-in fields and coordination path;
- the actual host tier used (`native`, `sequenced`, or `none`) and whether writers really ran
  concurrently;
- the isolation/attribution method and deterministic integration order;
- lane reports/reviews plus final integrated review evidence;
- any lost attempts, sequenced fallback, migration, deprecation, or unverified host behavior.

Never claim independent review when the same identity implemented and reviewed a lane. Honest
degradation is part of the durable outcome, not a concern to hide.
