# ADR-0014: prompt craft v2 — trigger-form descriptions, dial-back imperatives, judgment-first agents

**Status:** Accepted (2026-06-13)
**Decided by:** operator ("raise the bar again … fixate on how competitors write agents/prompts/skills … flavour our own")
**Implements:** .claude/engineering/audits/2026-06-13-cli-issues-craft-synthesis.md (workstream 3)

## Context

Field research (Anthropic best-practices, obra/superpowers, wshobson/VoltAgent agent collections,
the Cursor/Cline/Windsurf/Aider/AGENTS.md rules-format authors, 2026 prompt SOTA) found Lintel's
craft is above the public median but tuned to a PRE-4.5 model generation in two measurable ways:
(1) our skill `description:` fields summarize the workflow — the exact pattern superpowers proved
makes Claude follow the description instead of the body (one review instead of two); (2) our spine
leans on ALL-CAPS MUST/NEVER/CRITICAL, which Anthropic now names a yellow flag because current
models OVERTRIGGER on it. Both are cheap, high-leverage, evidence-backed fixes.

## Decision

1. **`description:` = trigger, not summary.** Skill descriptions state WHEN to use (third person,
   `Use when/after/to`, concrete trigger nouns), never the steps/phases. A shape guard
   (`tests/shape/skill-descriptions-trigger.sh`) fails a description with no trigger phrase.
2. **Dial back aggressive imperatives.** State the rule + the WHY instead of ALL-CAPS mandates;
   reserve hard `MUST`/`NEVER` for genuine one-way doors (safety/data-loss), with the reason attached.
3. **Judgment-first agents.** Agent files gain a Core-principles stance + a Behavioral-traits
   disposition block (wshobson's consistency engine), trigger-form `Use proactively when…`
   descriptions, and a one-line tool-scoping rationale.
4. **Positive over negative framing; one excellent worked example; word/instruction budgets;**
   persona-as-voice-not-accuracy; no hand-prescribed CoT for capable models; one verifier-anchored
   self-critique pass; structural anti-sycophancy. All codified in docs/concepts/prompt-house-style.md.
5. **Evidence over intuition (staged).** The eval-harness (ADR-0021) is the real arbiter; until it
   exists this house-style is the best-evidence default, applied with judgment.

## Honesty notes (from the v5.3 independent review)

- `lib/auto-decide.sh: is_one_way_door` is a real, unit-tested function (tests/unit/auto-decide.sh).
  The cycle skill instructs the agent to call it before auto-deciding, but the live `--auto` path
  is still LLM-executed prose, not hard control flow — the guard is "a real function the agent is
  told to call", not yet a mechanical gate that runs regardless. Full wiring is staged with the
  eval-harness (ADR-0021), which is what would let us prove the gate fires.
- The trigger-description guard (tests/shape/skill-descriptions-trigger.sh) enforces opening-verb
  + no-archaeology, not trigger SUBSTANCE — a cleverly-worded summary that opens with "Use to" can
  still pass. It is a ratchet against regression, not a substance judge; substance is settled by
  review and, eventually, the eval.

## Consequences

- docs/concepts/prompt-house-style.md is the contract for every new skill/agent and the bar
  existing ones are rewritten to. The skill/agent TEMPLATES are updated to match.
- The description→trigger rewrite lands highest-traffic skills first; the full-surface sweep and
  the field-wide aggressive-language dial-back are incremental (own follow-ups), guarded by the
  new shape test so new skills can't regress.
- Tension acknowledged: superpowers' Cialdini-based "be pushy/MUST" thesis is evidence for an
  OLDER model generation; Anthropic's current guidance for the generation Lintel runs on (Fable 5)
  is the opposite. We follow the current-generation evidence, keeping hard imperatives only for
  real one-way doors.
- Risk: trigger-form descriptions could UNDER-trigger if too terse — mitigated by naming concrete
  trigger nouns (Anthropic's "be specific, include key terms"), and ultimately settled by the eval.
