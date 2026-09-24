# MARS integration points (for the coordinator merge)

MARS ships as new files only. The existing workflows below are shared with active
Universal/Swarm work, so their edits are **specified here, not applied**. Apply them on
the coordinator's released base, keeping each edit to the snippet shown.

## Offer rule (all callers)

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-mars.py" offer --request "$req"   # exit 0 = may offer
```

Request fields: `caller` (`cycle` | `review` | `code-review` | `plan-eng-review` | `define`),
`route` (cycle only: the actual ordered phase list from `state_cycle_phases`),
`checkpoint` (cycle: `PLAN-approval`), `declined`, `already_offered`, `is_participant`,
`dry_run`, and `host` (`per_child_model`, `separate_contexts`, `delegate_permission`,
`identity_evidence`, `models`). Unknown host facts are omitted, which suppresses the offer.
The decision is never consent; ask with the offer text in `skills/mars/SKILL.md`.

## 1. `skills/cycle/SKILL.md` — Step 5 (pre-BUILD confirm gate)

Insert before "Proceed with BUILD?":

```markdown
**Optional MARS offer (full cycles only).** If the selected phase list equals the canonical
nine phases (no mode skips, no --from/--to/--skip, no SCOPE reroute) and `li-mars.py offer`
returns 0, offer MARS once on the approved plan/spec. Record the answer with
`state_append PLAN DONE mars_offer=<accepted|declined>`; nested phases read it and never
re-offer. `--auto` never accepts. Declining changes nothing else.
```

## 2. `skills/plan/SKILL.md` — Step 10 (founder approval gate)

Add option E to the approval question, shown only when the cycle offer gate passed:
`E) Run MARS on this plan first (<roster>, ≤ <calls> calls)`. Findings return to Step 9
fix/accept handling; the approval question is asked again afterwards.

## 3. `skills/review/SKILL.md` — Step 6 (optional outside voice)

Replace the Codex-only prompt with:

```markdown
### Step 6 — Optional MARS (gated)

Standalone review: if `li-mars.py offer` (caller `review`) returns 0 and MARS was not
already offered or declined, offer it once for the reviewed diff. Inside a cycle, use the
cycle's recorded `mars_offer`; never offer here. Surface MARS findings under
"MARS (multi-model):" and feed P1/P2 into the existing Stage 2 decisions. MARS never marks
the review PASS. If the host lacks MARS capability, skip silently unless the operator asked.
```

## 4. `skills/plan-eng-review/SKILL.md` — "Optional: Outside voice"

Point the existing optional outside-voice step at `/li:mars` (caller `plan-eng-review`).
Keep "informational, not auto-applied".

## 5. `skills/define/SKILL.md` — Step 7 (cross-model second opinion)

Route the optional second opinion to `/li:mars` with subject kind `problem` or `spec`
(standalone only; inside a cycle the single offer is at PLAN).

## 6. `skills/code-review/SKILL.md`

Keep the large-diff Codex P1 gate unchanged. Add: "Optional MARS for high-risk diffs —
offer once when `li-mars.py offer` (caller `code-review`) passes."

## 7. Distribution (generated — regenerate, do not hand-edit)

- `bin/li-copilot.py` `WORKFLOWS`: add
  `"mars": "Use when a problem, plan, spec, implementation or review needs a deliberate multi-model adversarial review with bounded rounds and preserved dissent."`
  and add `skills/mars/SKILL.md`, `skills/mars/references/*`, `bin/li-mars.py`,
  `lib/mars_contract.py`, `lib/mars-defaults.json` to the portable resource closure.
  The committed `.github/skills/li-mars/SKILL.md` matches what the generator emits.
- `skills/CATALOG.md`: regenerate with `python3 bin/li-catalog.py`.
- `lib/cli-tiers.yaml`: no new capability flag. MARS reads `delegate` + `model_control`
  plus live per-child model evidence; do not add a blanket `supports_mars`.
- `tests/shape/skill-descriptions-trigger.sh`: add `mars` to `MIGRATED`.

## 8. Decision record

Allocate the next free ADR number on the released base from
`.claude/plans/mars/adr-draft.md`.
