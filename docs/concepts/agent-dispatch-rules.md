# Agent Dispatch Rules — Dedicated-vs-Inline (v3.6 backlog item 2.4)

**Last updated:** 2026-05-28
**Status:** Concept doc — referenced by LAYERS.md + skills/cycle/SKILL.md

> Encodes "when to spawn a dedicated subagent vs run inline" rule som Lintel
> redan tillämpar ad-hoc per run. Going-forward: this doc är canonical.

## The rule (2 conditions for dedicated, 2 for inline)

### Spawn a dedicated subagent (via Agent tool) when:

**(a) Step produces heavy intermediate reasoning you don't want in the main window.**

Examples:
- Code review / architecture review (returns top issues, not full deep-read)
- Adversarial review (wants fresh context — accumulated context biases the review)
- Codebase exploration (open-ended search across many files)

The subagent reads broadly, returns narrowly. Main context stays clean.

**(b) Adversarial review where fresh context IS the point.**

Examples:
- Security audit (any context-poisoning from main = compromised review)
- Codex outside-voice opinion (independence is the value)
- Spec-review loop post-design-doc (catch what main missed)

Fresh context is feature, not bug.

### Run inline when:

**(c) Cheap + deterministic.**

Examples:
- File read with known path
- Grep with specific pattern
- Single-file edit
- Frontmatter parse

Subagent overhead > task cost. Just do it.

**(d) Step needs accumulated context to be meaningful.**

Examples:
- SENSE phase (operator-intent-detection needs current conversation context)
- CAPTURE phase (synthesize what just happened, can't do without main thread)
- Phase-progress output (refers to current cycle state)

Stripping context breaks the step.

## Decision tree

```
Is the step open-ended (many files, unclear scope)?
  YES → dedicated subagent (rule a)
  NO  → continue
       │
       ▼
Does the step need adversarial/independent perspective?
  YES → dedicated subagent (rule b)
  NO  → continue
       │
       ▼
Is the step cheap + deterministic (single tool call)?
  YES → inline (rule c)
  NO  → continue
       │
       ▼
Does the step need conversation context to make sense?
  YES → inline (rule d)
  NO  → default to dedicated (when in doubt, isolate)
```

## Applied to Lintel's 8 phases

| Phase | Default mode | Why |
|---|---|---|
| SENSE | inline (rule d) | Reads conversation context to detect intent |
| DEFINE | inline (rule d) | Builds on SENSE output |
| DISCOVER | dedicated (rule a) | Open-ended codebase exploration |
| PLAN | inline (rule d) | Synthesizes prior phases |
| BUILD | dedicated per task (rule a) | Each task = fresh implementer (superpowers SDD pattern) |
| REVIEW | dedicated (rule b) | Adversarial — fresh context is the point |
| SHIP | inline (rule c) | Cheap: git ops + verify |
| CAPTURE | inline (rule d) | Synthesizes what just happened |

## Operator override

`/li:cycle --inline-all` forces all phases inline (for context-budget pressure).
`/li:cycle --dedicated-all` forces all phases dedicated (rare; usually wasteful).

Default is per-phase rule above.

## Token-cost implication

Dedicated subagent costs ~base-context warm-up overhead per spawn (~5-15k tokens).
Inline phase costs only the work itself.

Rule of thumb: if phase work < 5k tokens, inline wins on token-budget.
If phase work > 15k tokens AND independence-or-cleanliness matters, dedicated wins.

## References

- Backlog item 2.4 (concept doc requirement)
- `~/.claude/skills/gstack/superpowers/` subagent-driven-development pattern
- Lintel cycle SKILL.md `/li:cycle` Step 4 (phase execution)
- `[[L-001]]` scaffolding-not-content — this doc IS the scaffolding for the rule
