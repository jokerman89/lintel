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

## Host dispatch and identity

Inspect the current host's actual tools, permission and live roster before using
these mappings. They are integration guidance, not a tool-availability claim or
another dispatch engine. Pass the consented roster's effective model, effort and
context settings; never infer them from a current-model example.

For Copilot App, where the inspected surface exposes them:

- `task`: subagent fields `model`, `reasoning_effort`, `context_tier`.
- `create_session`: `kickoff.model`, `kickoff.reasoning_effort`,
  `kickoff.context_tier`, `kickoff.mode: autopilot`,
  `coordinate_with_creator: false`, `notify_on_idle: once`.
- `always` may keep producing idle notices after archive; for the challenge round
  read the actual round-2 report from the supported session store rather than
  assuming another notification. Retain the same child identity.
- Local session-store `assistant_usage_events.model` and `reasoning_effort` per
  child can supply host-observed identity when actually available. A different
  surface may expose different usage evidence; no observation means unverified,
  not the reviewer's self-description upgraded to `host-usage`.

Other hosts use their observed native per-child model API and identity evidence.
Missing capability, denied permission or unsupported continuation preserves the
limitation; no fallback to a new provider or role-played panel. Keep the accepted
subagent default, opt-in nested sessions, exact registration and owned/collected/
idle close checks from the main MARS method.

## Applied hooks

| Workflow | Hook | Behavior |
|---|---|---|
| `skills/plan/SKILL.md` Step 10 | option E, or a lone offer when approval is retained | the cycle's single offer; findings return to Step 9; `mars_offer` recorded on the PLAN entry |
| `skills/cycle/SKILL.md` Step 5 | surfaces PLAN's `mars_offer` | never offers, repeats or upgrades |
| `skills/review/SKILL.md` Stage 1/2 | the shared method packet | same packet a MARS slot receives |
| `skills/review/SKILL.md` Step 6b | panel mode, standalone only | REVIEW records its own decision from the adjudicated outcome |
| `skills/code-review/SKILL.md` | optional panel for high-risk diffs | optional cross-check pass and evidence gate unchanged |
| `skills/inspect/SKILL.md` Report and reconcile | optional outside voice, standalone only (caller `inspect`) | informational; never sets the verdict |
| `skills/define/SKILL.md` Step 7 | cross-model second opinion, subject kind `problem` or `spec`, standalone only (caller `define`) | review input, not approval; inside a cycle PLAN owns the offer |
| `skills/cross-check/SKILL.md` When to use | keeps one independent reviewer | a multi-model request is `/li:mars`, never a role-played panel |
| `agents/engineering/CodeReviewer.md` Workflow | follows a dispatched method packet | its dimension list is background, not a second rubric |

## Distribution

- `bin/li-copilot.py`: `mars` in `WORKFLOWS`; `MARS_RESOURCES` is the required closure
  (skill, references, both helpers, both schemas, defaults, question catalog, method).
- `skills/CATALOG.md`: regenerate with `python3 bin/li-catalog.py`.
- `lib/cli-tiers.yaml`: no new capability flag. MARS reads delegation and model control
  plus live per-child model evidence; there is no blanket `supports_mars`.
- `tests/shape/skill-descriptions-trigger.sh`: `mars` is in `MIGRATED`.

## Decision record

[ADR-0036](../../../.claude/decisions/0036-mars-multi-model-review.md).
