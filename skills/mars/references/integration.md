# MARS integration points

MARS is optional everywhere. Removing it, declining it or running on a host without the
capability leaves every workflow on its single-reviewer path.

## Offer rule (all callers)

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-mars.py" offer --request "$req"   # exit 0 = may offer
```

Request fields: `caller` (`cycle` | `plan` | `review` | `code-review` | a consolidated
review workflow), `route` (inside a cycle: the actual ordered phase list after every mode,
range, skip and reroute), `checkpoint` (`PLAN-approval` for the cycle offer), `declined`,
`already_offered`, `is_participant`, `dry_run`, and `host` (`per_child_model`,
`separate_contexts`, `delegate_permission`, `identity_evidence`, `models`). Unknown host
facts are omitted, which suppresses the offer. A caller inside a cycle always sends the
route, so only PLAN's approval gate of a full nine-phase cycle can pass. The decision is
never consent; ask with the offer text in [the skill](../SKILL.md).

## Applied hooks

| Workflow | Hook | Behavior |
|---|---|---|
| `skills/plan/SKILL.md` Step 10 | option E, or a lone offer when approval is retained | the cycle's single offer; findings return to Step 9; `mars_offer` recorded on the PLAN entry |
| `skills/cycle/SKILL.md` Step 5 | surfaces PLAN's `mars_offer` | never offers, repeats or upgrades |
| `skills/review/SKILL.md` Stage 1/2 | the shared method packet | same packet a MARS slot receives |
| `skills/review/SKILL.md` Step 6b | panel mode, standalone only | REVIEW records its own decision from the adjudicated outcome |
| `skills/code-review/SKILL.md` | optional panel for high-risk diffs | Codex gate and evidence gate unchanged |

## Pending hooks for the consolidated planning and quality workflows

The native planning consolidation replaces `plan-eng-review` (and related plan reviews)
with a consolidated inspection workflow and rewrites `define`; the quality consolidation
renames `codex` to `cross-check` and revises `CodeReviewer`. Apply these on that base,
not to the files being removed:

- **Inspection (replacing `plan-eng-review`):** its optional outside-voice step routes to
  `/li:mars` with caller `plan-eng-review` or the new workflow name; stays informational.
- **`define` spec review:** the optional cross-model second opinion routes to `/li:mars`
  with subject kind `problem` or `spec`, standalone only (inside a cycle PLAN owns the offer).
- **`cross-check`:** keeps the single independent reviewer; a multi-model request is
  `/li:mars`, never a role-played panel inside `cross-check`.
- **`CodeReviewer`:** when dispatched with a method packet, follow the packet's rubric and
  report shape; its own dimension list is background, not a second rubric.

## Distribution

- `bin/li-copilot.py`: `mars` in `WORKFLOWS`; `MARS_RESOURCES` is the required closure
  (skill, references, both helpers, both schemas, defaults, question catalog, method).
- `skills/CATALOG.md`: regenerate with `python3 bin/li-catalog.py`.
- `lib/cli-tiers.yaml`: no new capability flag. MARS reads delegation and model control
  plus live per-child model evidence; there is no blanket `supports_mars`.
- `tests/shape/skill-descriptions-trigger.sh`: `mars` is in `MIGRATED`.

## Decision record

[ADR-0034](../../../.claude/decisions/0034-mars-multi-model-review.md).
