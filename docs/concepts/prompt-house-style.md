# Lintel prompt house-style (v2)

> ADR-0014. Lintel writes skills and agents around concrete triggers, bounded methods and
> verifiable outputs, using the current host's configured model rather than requiring a
> particular model. The dated evidence and source citations remain in
> .claude/engineering/audits/2026-06-13-cli-issues-craft-synthesis.md. This is the
> authoring contract; historical comparisons do not establish current execution results.

## The two rules that change the most

### 1. `description:` is a TRIGGER, not a summary
The description is the auto-invocation mechanism — Claude reads it to decide WHEN to use the
skill, often WITHOUT reading the body. If it summarizes the workflow, Claude follows the summary
instead of the body. The cited historical regression describes a summary saying "code review
between tasks" leading to one review when the body specified two; that observation is not a
new test result.

- State **when to use**, in third person, with concrete trigger terms. Lead with `Use when …` /
  `Use after …` / `Use to …`.
- Do **not** describe the steps, the phases, or the implementation. That lives in the body.
- Name the situations/nouns a user's request would contain — those are what the picker matches.

> Bad:  `Phase 5 of the Lintel cycle — execute plan via TDD + subagent-driven development with two-stage review.`
> Good: `Use to implement an approved plan task-by-task. Trigger after PLAN is approved, when a plan.md exists and code needs writing.`

### 2. Dial back the ALL-CAPS imperatives
Current models OVERTRIGGER on aggressive `MUST` / `NEVER` / `CRITICAL` / `BLOCKING`. Anthropic
names ALL-CAPS mandatory language a **yellow flag** and a cause of overtriggering for Opus 4.5+.

- State the rule, then the **why** — "never use ellipses, because the TTS engine can't pronounce
  them" generalizes better than "NEVER USE ELLIPSES."
- Reserve hard imperatives for genuine one-way doors (safety blocks, data loss). Everywhere else,
  normal prompting ("Use this when…", "Prefer X because…").
- If you're writing `ALWAYS`/`NEVER` in caps, that's the yellow flag — reframe with the reason.

## Writing skills

- **Trigger-form description** (rule 1). A `tests/shape/skill-descriptions-trigger.sh` guard fails
  a description that has no `Use when/after/to` trigger phrase.
- **Budget**: aim under ~500 lines / a tight instruction count; push reference detail to linked
  files (progressive disclosure — references one level deep, TOC if a ref file > 100 lines).
- **Imperative + why** (rule 2). State the rule and the reason; the model generalizes from reasons.
- **Positive framing**: "compose flowing prose" beats "don't use markdown." Convert each "don't X"
  to "do Y"; keep a hard prohibition only when it's a real one-way door, with its reason attached.
- **One excellent worked example**, Good/Bad paired where a failure mode is subtle, wrapped in
  `<example>` tags. Not five contrived ones, not multi-language.
- **When NOT to use** stays — it's a Lintel strength most public skills lack.
- Drop version-archaeology ("Phase 4 v4.2", "Cohort 2 item 1.6") from descriptions and operational
  prose — it's noise that dilutes the trigger signal. Provenance lives in ADRs.

## Writing agents

Lintel agents are already above the public median (When-NOT, report contracts, uniform rhythm).
The bar-raise adds judgment, not length:

- **Trigger description** ending in a `Use proactively when …` / `Use after …` clause that names
  concrete capability nouns (what the orchestrator string-matches).
- **Core principles** (2-4 lines, after the persona) — the agent's stance for the gray zone the
  workflow doesn't enumerate ("favor simplicity over premature optimization"; "never trust input").
- **Behavioral traits** (5-8 bullets) — what the agent ALWAYS does first / defers / refuses.
  Distinct from Voice (how it sounds): traits are what it does. This is the consistency engine.
- **Tool scoping with a one-line why** (Anthropic: "no Edit/Write because this agent only reviews").
- **Memory/model** through the actual host adapter; retain useful memory without making
  optional host features or a model name mandatory (ADRs 0012 and 0028).
- **Output contract**: a concrete report shape the caller can rely on (priority-bucketed, or a
  fielded/JSON handoff envelope for the module agents that hand off).
- **Internal voice**: direct engineering prose about decisions, evidence, risks and next actions.
  Customer-facing voice remains an explicitly selected pack concern. Preserve required notices
  for retained third-party material; neutral wording is not license clearance.

## What the field taught us NOT to do

- **Persona-for-accuracy is overrated** — "you are a world-class expert" does not improve factual
  accuracy on current models. Roles steer voice/behavior; don't sell them as an accuracy lever.
- **Don't hand-prescribe step-by-step reasoning** to capable models — "think thoroughly" beats a
  hand-written CoT; reserve explicit reasoning scaffolds for cheap models or when you branch on the
  steps. (With thinking off, prefer "consider/evaluate/reason through" over the literal word "think".)
- **Cap self-critique at one verifier-anchored pass** — reflection without an external signal
  (tests, grep, a fresh-context judge) can turn a right answer wrong. Anchor it to pass/fail criteria.
- **Anti-sycophancy is structural** — a fresh-context judge agent and question-reframing beat "be
  harsh." Our subagent review already fits; lean on it, don't add "are you sure?" loops.

## The discipline behind the discipline

Every craft rule above should ultimately be decided by an **eval** (20-50 real tasks per critical
skill, pass/fail verifier, positive + negative cases) — not by intuition. "Generically better"
prompt edits can hurt a specific skill; only a task-suite tells you. The eval-harness is staged as
ADR-0021; until it exists, this house-style is the best-evidence default, applied with judgment.
