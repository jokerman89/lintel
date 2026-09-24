# MARS — Multi-Model Adversarial Review & Screening

MARS asks several **different** models to review the same thing independently, then lets
them challenge each other once if they disagree. You get agreed findings, preserved dissent
and the gaps nobody covered. It is a deliberate second look, not a gate and not Swarm.

## When it runs

| Situation | What happens |
|---|---|
| You ask for it (`/li:mars`, "multi-model review", "outside opinion") | Capability check, roster proposal, one confirmation, run. |
| Full `/li:cycle` at the PLAN approval gate, capable host | One offer. "No" is remembered; nested phases never re-offer. |
| Hotfix, research-only or partial cycle | No offer. You can still ask explicitly. |
| Standalone review, code-review, plan-eng-review or define | At most one offer for that target. |
| Host can't pick a model per child or can't show which model ran | No offer; an explicit request explains why it can't run. |

Auto mode never opts in. An offer is not consent.

## Defaults

- **Roster:** the latest model in each family — Claude (Opus preferred), GPT, Grok, MAI.
  Gemini and others can be added. Minimum 2 distinct models, default 4, maximum 8.
  "Latest" is resolved from the host's live model list on every run.
- **Effort:** extra high, clamped to what each model supports. **Context:** 1M where
  available. The report shows the effective values.
- **Rounds:** one blind pass; a challenge round only when claims are contested.
- **Transport:** subagents by default (cheapest). Visible nested sessions on request; they
  are closed after their reports are collected.

Settings live in `lib/mars-defaults.json`.

## How a panel works

1. **Freeze a brief** — the subject, the questions and the reviewer rules.
2. **Blind pass** — every reviewer gets the identical brief and no peer output.
3. **Collect and verify identity** — reports are recorded with the model the host says ran,
   not the model's self-description.
4. **Challenge (if contested)** — reviewers see an anonymized claim matrix and defend,
   revise or refute with evidence.
5. **Synthesize** — the coordinator decides against the source, not by vote.
6. **Close** — only the sessions this panel spawned and registered, after collection.

## What you get

Agreed findings with the strongest evidence, unique catches, disputed claims with both
sides, rejected claims with reasons, uncovered gaps, recommended checks, and a summary:
requested vs verified distinct models, calls used, and `release_clearance: false`.

## What it is not

- Not Swarm: no implementation lanes, write scopes or merges.
- Not a release gate: `/li:review`, QA and `/li:ship` keep their controls.
- Not a model catalog: nothing pins model names; the host decides what is available.

## Try it

```bash
python3 bin/li-mars.py roster --host tests/fixtures/mars/copilot-app-host-2026-09-24.json
bash tests/unit/mars-contract.sh
```

See `skills/mars/SKILL.md` for the full workflow and `skills/mars/references/protocol.md`
for the reviewer and challenge templates.
