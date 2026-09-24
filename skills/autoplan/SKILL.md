---
name: autoplan
layer: foundation
description: Use to compose task-relevant intake, discovery and canonical PLAN with applicable review lenses, preserving the same original work map and approval as direct planning.
color: purple
tools: Read, Bash, Edit
voice: internal
necessity: OPTIONAL
gap_if_skipped: "The same pipeline is reachable by hand (/li:office-hours → /li:plan-ceo-review → /li:plan-eng-review → …); without autoplan the operator drives each review step manually and synthesizes the verdicts."
cli_support:
  - cli: claude-code
    level: full
---

# /li:autoplan

A convenience entry into canonical DEFINE/DISCOVER/PLAN, not a second planner or
approval system. `office-hours` remains an optional exploratory intake mode;
engineering, applicable UI and DX review retain their detailed methods. The
venture/strategy lens is optional, never inferred from task size.

Follow [task-relevant intake](../define/references/intake.md) and the
[shared work-map contract](../spec-kit/references/work-map.md), validated by
`bin/li-work-artifacts.py`. Identical input/authorization must reach the same
original artifacts and approval state as invoking PLAN directly.

## When to use

- Big feature or initiative — full plan pipeline is appropriate
- Customer-engagement prep where multiple review tiers add value
- New repo / new project — get scaffolded design + reviews in one chain

## When NOT to use

- Trivial fix / refactor — too heavy. Use `/li:fix`, or `/li:review` then `/li:ship`.
- Plan already exists — skip `/li:office-hours`, run individual review skills.
- Ongoing iterative work — chain overhead exceeds value per cycle.

## Inputs

- Optional `--skip <skill>` — skip a specific skill in the chain (e.g., `--skip plan-design-review` for backend-only work)
- Optional `--include-devex` — explicitly include the developer-workflow lens
- Optional `--mode <full|minimal>` — depth of applicable planning, not an approval shortcut
- Optional `--map <work.json>` / `--lens venture` — retain the original selection or opt
  into strategy questions; required acceptance/review cannot be skipped by an alias

## Workflow

1. **Select and verify.** Retain the explicit map, original IDs and verified P07
   reference/required policy through `workflow_resume`; ask only unresolved decisions.
2. **Existing approved work.** Invoke canonical PLAN's mapped-work branch to
   reconcile the original design/spec/tasks/handoff. Do not regenerate them or
   repeat DEFINE's interview.
3. **New work.** Use office-hours/DEFINE to explore only missing decisions.
   Office-hours returns DRAFT until scoped approval; it does not produce the
   APPROVED map by itself. DISCOVER supplies code/ADR/lesson grounding.
4. **Canonical PLAN.** Run PLAN once with those exact inputs. PLAN owns the trio/map,
   unchanged leaf/package IDs, applicable engineering/UI/DX reviews, dependency
   analysis, handoff budget and approval. Do not invoke its review passes a second time.
5. **Optional strategy lens.** When explicitly requested, apply plan-ceo-review to
   the same design. Material scope changes return to PLAN; a skipped optional lens
   is not silently forced back into the chain.
6. **Synthesize.** Link actual reports and unresolved findings by original ID.
   Use [P05 evidence](../review/references/evidence.md), not old CLEAR strings.
7. **Return canonical status.** Ready for authorized BUILD only when PLAN's
   selected map is APPROVED and required evidence is satisfied. No automatic
   SHIP, publication, task copying or independent-review claim follows.

## Report format

```
Autoplan Status: <branch>

Chain: optional intake → DEFINE/DISCOVER as needed → canonical PLAN
Mode: full
Skipped: plan-devex-review (default)

Intake: existing answers reused; <explicit design path and actual status>
Strategy lens: not selected (or its actual report)
PLAN: <actual spec/quality/applicable UI/DX results and unresolved IDs>

Final status: <canonical PLAN status, not a new verdict>
Work map: <exact path>; original tasks: <exact mapped path and IDs>
Next: authorized BUILD, or the precise unresolved PLAN decision/evidence
```

## Compliance integration

- Each chained skill applies the active pack's compliance gates at invocation (`resolve_pack_field compliance.hooks`; none in the neutral `_default` pack).
- Mandatory applicable failure/unverified/error blocks its dependent action through
  P05's shared control interpretation. Advisory findings remain advice.

## Failure modes

- **`/li:office-hours` returns "NEEDS_CONTEXT" or "BLOCKED":** chain pauses. Operator addresses, then re-runs autoplan (idempotent — reads existing design doc if present).
- **`/li:plan-ceo-review` returns REVISE:** chain pauses. Operator updates design doc per CEO findings, then re-runs autoplan.
- **A required planning review remains incomplete:** keep that gate open with the
  actual host/manual handoff. A native ExitPlanMode API or a last-heading convention
  is not a Universal permission requirement.
- **Any chained skill times out:** report which skill, allow operator to re-run that skill standalone, then resume autoplan.

## Idempotency

Resume the same explicit map and completed phase evidence. Reuse reviews only when
the shared latest-reader still validates the exact context; file existence or age
alone cannot establish reuse. Repair only affected work and renew affected evidence.

## Examples

**Full pipeline:**
```
> /li:autoplan
Chain: DEFINE/DISCOVER as needed → PLAN with applicable review lenses
[original work map becomes APPROVED only within actual authority and required review]
```

**Backend only, skip design-review:**
```
> /li:autoplan --skip plan-design-review
Chain: canonical planning; no UI lens because no UI scope
[the same approved work map and original task IDs]
```

**Minimal:**
```
> /li:autoplan --mode minimal
Chain: minimal task-relevant intake → PLAN
[required engineering review retained; optional strategy lens not selected]
```

**Blocked mid-chain:**
```
> /li:autoplan
PLAN: NEEDS_CONTEXT — migration rollback ownership remains unresolved
Independent planning can continue; dependent BUILD stays open.
```

## See also

- `/li:office-hours` — design generator (first step of chain)
- `/li:plan-ceo-review` — step 2
- `/li:plan-eng-review` — step 3 (the required gate)
- `/li:plan-design-review` — step 4 (UI scope only)
- `/li:plan-devex-review` — opt-in step 5
- `/li:ship` — separate, authorized delivery after actual BUILD/REVIEW/QA
