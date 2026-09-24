# ADR draft: MARS — deliberate multi-model adversarial review & screening

**Status:** Proposed (number allocated on the coordinator's released base)
**Date:** 2026-09-24
**Decider:** operator requested MARS, its defaults and a live four-model pilot

## Context

Lintel has several host-specific "outside voice" hooks (define Step 7, review Step 6,
plan-eng-review, code-review's Codex gate). Hosts such as the Copilot App now select a model
per child and report which model ran, but many hosts override or fall back silently.
Swarm (ADR-0027) fans out implementation; it is the wrong tool for a targeted second look.

## Decision

Add `/li:mars`: a canonical skill plus a stdlib data helper (`bin/li-mars.py`,
`lib/mars_contract.py`, `lib/mars-defaults.json`). The helper resolves the latest model per
family from the host's live list, gates offers, and keeps panel state; it never dispatches,
consents or closes. The coordinator dispatches with host tools, registers every child, and
closes only registered, owned, collected nested sessions.

Defaults: latest Claude (Opus first), GPT, Grok and MAI; extra-high effort and 1M context,
clamped per model and recorded; one blind pass, a challenge round only when contested;
automatic offers only at the full-cycle PLAN gate or once per standalone review; auto mode
is never consent; `release_clearance: false` always.

## Alternatives

1. Prompt-only skill — cannot test gating, close safety or identity evidence.
2. **Skill + small data helper over host tools (chosen)** — portable, testable, no runtime.
3. Provider-API runner — credentials, routing and billing outside host policy.

## Consequences

One place for multi-model review; existing optional outside-voice hooks route to it
(integration snippets in `skills/mars/references/integration.md`). Identity is only as
strong as the host's evidence; self-reports never count. Nested-session reviewers in a
repository with large instructions cost ~45-75k input tokens per call (pilot measurement),
so subagents are the default transport.

## Verification

`tests/unit/mars-contract.sh` (roster, offer gate, panel ownership/close, budgets, summary).
Live pilot 2026-09-24: two panels × four models on the Copilot App, host usage events used
as identity evidence; see `.claude/plans/mars/pilot-2026-09-24.md`.
