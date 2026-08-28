# Feature Request — Brief Forge + standardized payload + 1:1 wiki

**Compiled:** 2026-05-28 · from a design conversation between operator and Claude.
**Status:** Standalone feature request. Consolidated into v4.0 via [`.claude/engineering/design-archive/lintel-v4.0-reframe-design.md`](../design/lintel-v4.0-reframe-design.md) Chapter 2.
**Scope:** A universal hand-off gate that fires on every context boundary crossing, a standardized payload envelope for progress-tracking, and a generated 1:1 wiki that stays in sync with the system.

**Locked decisions (operator):**
- Gate runs at **every hand-off**, not just subagent-spawn.
- Gate does three things: **curate, hydrate, dispatch** (security/compliance/other checks as policy-driven evaluators).
- Built into the current system, not parallel to it.
- Payload standardization (head/body/tail) ships parallel to the gate so progress can be tracked end-to-end.
- Wiki is included as Chapter C — can begin now.

---

> Original full text preserved in the project's external archive. This file is the canonical reference within the repo. v4.0 design doc consolidates and interprets — see [Chapter 2 of v4.0 reframe](../design/lintel-v4.0-reframe-design.md#chapter-2--brief-forge--envelope--generated-wiki) for the unified implementation plan.

## What "every hand-off" means concretely

A hand-off is any moment when one execution context passes work to another execution context that starts with different (usually less) state. Five moments in Lintel:

1. Skill → subagent
2. Phase → phase within a workflow
3. Workflow → sub-workflow
4. Workflow → cold executor
5. Operator → skill/workflow

All five fire the gate. Same mechanism, different policy.

## Summary of the three chapters

**FR-A — Brief Forge: the universal hand-off gate.** Three-phase mechanic per hand-off:
- **Curate** (sender's responsibility): structured curation declaration of context, task, anticipated needs, deliberate exclusions
- **Hydrate** (gate's responsibility): policy-driven enrichment from knowledge-base, lessons, context-warming, freshness check, dependency completeness
- **Dispatch** (gate's responsibility): direct pass / policy-matched evaluators in parallel / block-with-override

Evaluator catalog: security-eval, compliance-eval, voice-eval, stale-eval, completeness-eval, knowledge-overlap-eval, legality-eval.

Pack-driven policy via `brief_forge:` block in `pack.yaml`. Mechanical-first; single hard budget (~5k tokens); parallel where possible; override-with-audit.

**FR-B — Standardized payload envelope.** HEAD (addressing + metadata) + BODY (free-form per `content_type`) + TAIL (provenance + integrity). Every hand-off produces an envelope. Logged to `~/.lintel/jobs/<id>/envelopes/`. Enables progress tracking, replay/debug, audit, wiki generation, cross-CLI portability.

**FR-C — Generated 1:1 wiki.** `bin/li-wiki-gen` reads all frontmatter + manifests + navigation declarations + envelope schemas. Generates `docs/wiki/` structure. Committed to repo. Regenerated on demand or via pre-commit hook.

## Operator validation criteria

1. Operator can trace any cycle invocation end-to-end by reading envelopes in chronological order from the job's envelope log.
2. BUILD's implementer-spawn produces a curated, hydrated, evaluated envelope. The implementer subagent starts with verified-complete context.
3. An evaluator-fail surfaces in one line with override option.
4. Generated wiki accurately reflects current 141 skills × 83 agents × 18 hooks × N packs without manual editing.
5. Switching pack changes which evaluators fire at hand-offs without code changes — pack policy alone.
6. Default pack hand-offs add < 1 second overhead measured against current.

## Decisions still open

1. **Gate-name confirmation.** "Brief Forge" — keep, change, or another name? Bikeshed safe.
2. **Envelope storage retention.** Forever in `_archive/`, or trim after N days? Recommended: forever, they're small and grep-able.
3. **CI enforcement on wiki staleness** — fail build, or warn-only? Recommended: warn-only for v1, harden once wiki has proven useful.

See [v4.0 design Chapter 2.2-2.4](../design/lintel-v4.0-reframe-design.md#chapter-2--brief-forge--envelope--generated-wiki) for AI interpretation + recommendations.
