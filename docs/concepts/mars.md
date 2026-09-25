# MARS — Multi-Model Adversarial Review & Screening

MARS asks several **different** models to review the same thing independently, then lets
them challenge each other once if they disagree. You get agreed findings, preserved dissent
and the gaps nobody covered. It is a deliberate second look, not a gate and not Swarm.

## When it runs

| Situation | What happens |
|---|---|
| You ask for it (`/li:mars`, "multi-model review", "outside opinion") | Capability check, roster proposal, one confirmation, run. |
| Full nine-phase `/li:cycle` at PLAN's approval gate, capable host | One offer (option E). "No" is remembered; later phases never re-offer. |
| Hotfix, research-only, partial or rerouted cycle | No offer. You can still ask explicitly. |
| Standalone `/li:review` (panel mode), `/li:code-review` or `/li:plan` | At most one offer for that target. |
| Host can't pick a model per child or can't show which model ran | No offer; an explicit request explains why it can't run. |

Auto mode never opts in. An offer is not consent.

## Defaults

- **Roster:** the latest model in each family — Claude (Opus preferred), GPT, Grok, MAI.
  Gemini and others can be added. Minimum 2 distinct models, default 4, maximum 8.
  "Latest" is resolved from the host's live model list on every run.
- **Effort:** extra high, clamped to what each model supports. **Context:** 1M where
  available. The report shows the effective values.
- **Rounds:** one blind pass; a challenge round only when claims are contested.
- **Transport:** subagents by default (nothing to close). Visible nested sessions on request; they
  are closed after their reports are collected.

Settings live in `lib/mars-defaults.json`.

## How a panel works

1. **Freeze a brief** — the shared [Review Method](../../skills/review/references/method.md)
   packet: subject, standing questions, evidence levels and one severity rubric. For
   repository content, the exact selection is snapshotted; records that would sit inside
   it are refused before anything is written.
2. **Blind pass** — every reviewer gets the identical brief and no peer output. A single
   `/li:review` reviewer gets the same body, so single and panel results are comparable.
3. **Collect and verify identity** — reports are recorded with the model the host says ran,
   not the model's self-description.
4. **Challenge (if contested)** — reviewers see an anonymized claim matrix and defend,
   revise or refute with evidence.
5. **Synthesize** — the coordinator decides against the source, not by vote. The adjudicated
   counts use the same decision rule as a single review; a partial panel, missing coverage
   or a changed input is `incomplete`, never a pass.
6. **Close** — only the sessions this panel spawned and registered, after collection.

## What you get

Agreed findings with the strongest evidence, unique catches, disputed claims with both
sides, rejected claims with reasons, uncovered gaps, recommended checks, and a summary:
requested vs verified distinct models, calls used, and `release_clearance: false`.
`li-mars.py panel inspection` turns it into a content-bound inspection record for REVIEW.

## What it is not

- Not Swarm: no implementation lanes, write scopes or merges.
- Not a release gate: `/li:review`, QA and `/li:ship` keep their controls. In REVIEW panel
  mode, REVIEW records its own decision from the adjudicated result.
- Not a model catalog: nothing pins model names; the host decides what is available.

## Try it

```bash
python3 bin/li-mars.py roster --host tests/fixtures/mars/copilot-app-host-2026-09-24.json
python3 bin/li-review-packet.py questions --kind implementation --stage quality --tags path
bash tests/unit/mars-contract.sh && bash tests/unit/review-method.sh
```

See [the MARS skill](../../skills/mars/SKILL.md) for the full workflow and
[the protocol](../../skills/mars/references/protocol.md) for headers, the challenge round
and synthesis.
