---
name: li-retro
layer: foundation
description: Session retrospective — what shipped, what got stuck, what to /learn from.
color: yellow
tools: Read, Bash, Grep, Glob, Write
voice: internal
cli_support: [claude-code, codex]
---

# /retro

End-of-session reflection. Reads git log, audit trail, todo state, recent skill invocations — synthesizes a structured summary of what happened, what worked, what got stuck, and what should be `/learn`-recorded for next time.

Optional `/learn` emission: skill can offer to write 1-3 lesson entries on the operator's behalf (operator confirms each).

## When to use

- End of a working session, want a clean handoff before pausing
- After a deploy or ship cycle, before moving to next initiative
- Periodic team retro (weekly, sprint-end)
- After an incident or production issue resolution — capture lessons while fresh

## When NOT to use

- Mid-session — too early to reflect; tasks are still in flight
- After a 5-minute hotfix — overhead exceeds value
- As a substitute for `/context-save` — retro reflects, context-save persists

## Inputs

- Optional `--since <ref|time>` — start of the retro window (default: last `/context-save` timestamp, else 24h ago)
- Optional `--scope <session|day|week>` — preset windows
- Optional `--emit-lessons` — auto-propose `/learn` entries for confirmation (default: off — just reports)
- Optional `--out <path>` — write retro to file (default: stdout only)

## Workflow

1. **Determine window.** Resolve `--since` to a concrete timestamp.
2. **Gather signals:**
   - Git log since window start (commits + messages)
   - Audit log entries (`~/.lintel/audit/*.jsonl`) within window
   - Todo state changes (if tracked)
   - Skill invocations within window (from `~/.lintel/analytics/skill-usage.jsonl`)
3. **Structured analysis:**
   - **Shipped:** what landed (commits + PRs + deploys)
   - **Stuck:** unresolved items (audit log entries marked BLOCKED, failing CI runs, abandoned skills)
   - **Surprises:** unexpected events (auto-rollbacks, compliance blocks, repeated retries)
   - **Patterns worth recording:** recurring corrections, new workflows that emerged, quirks discovered
4. **Optional lesson proposals.** If `--emit-lessons`: for each pattern-worth-recording, draft a `/learn` entry. Operator confirms each before write.
5. **Report.**

## Report format

```
Retro: jokerman-lintel / main

Window: 2026-05-27 09:00 → 17:55 (8h 55min, active session)
Signals: 7 commits, 32 audit entries, 14 skill invocations

## Shipped
- f6f8ac3 — batch 8 release+safety skills (benchmark, canary, freeze, unfreeze, setup-deploy)
- a60c46c — batch 7 design+DX skills
- 547768c — batch 6 browser skills
- 3a18068 — batch 5 QA+investigate skills
- 3a637cd — batch 4 ship pipeline (carryover from prior session)

## Stuck
- /sync-brain not yet written (planned batch 10)
- T0 voice corpus still empty (operator-blocked, awaiting Copilot material gather)

## Surprises
- gh CLI returned case-normalized jokerman89 URL — push worked anyway, but display surprised
- CRLF warnings on every commit (Windows git default) — not blocking but noisy

## Patterns worth recording
1. Skill files consistently land at ~150-250 lines following TEMPLATE-skill.md — write velocity 5 skills/batch in parallel works
2. cli_support: [claude-code] for browser-dependent skills (Codex/Copilot lack browser control) — established convention
3. Voice tier: internal default, mixed only when skill consumes trailblazer content as standard (e.g. /design-review copy pillar)

## Lesson proposals (--emit-lessons enabled)
[Operator confirms each before /learn is invoked]

1. Pattern — "When writing skill batches of 5, use parallel Write tool calls + single git commit. Avoid sequential — eats clock time." [y/n]
2. Quirk — "Windows CRLF warnings during git add are normal, not blocking." [y/n]
3. Skillify-candidate — "Recurring batch-skill workflow (mkdir × 5 + Write × 5 + commit + push) could become /batch-skills." [y/n]
```

## Compliance integration

- Read-only on audit logs (which are append-only by design).
- Retro output sanity-scanned before optional `--out` write.
- Lesson proposals go through `/learn`'s Layer 2 scan when emitted.

## Voice tier note

`voice: internal`. Reflection is engineering-internal.

## Failure modes

- **No commits in window:** report empty retro, suggest widening `--since`.
- **Audit log unreadable / missing:** retro proceeds with git-log signal only, note degraded data.
- **Operator says "yes to all" on lesson proposals:** require per-lesson confirmation regardless. Bulk-confirm is too easy to fire by reflex.
- **Skill detects no patterns worth recording:** that IS the result. Report it honestly. Not every session needs a lesson.

## Examples

**Daily retro:**
```
> /retro --scope day
[Reads last 24h]
3 commits, 1 stuck item, 2 patterns. No lessons proposed (no surprises).
```

**Session retro with lesson emission:**
```
> /retro --emit-lessons
[Synthesizes, proposes 3 lessons]
Operator confirms 2 of 3. /learn fires twice. Audit logged.
```

**Sprint retro to file:**
```
> /retro --scope week --out docs/retros/2026-W22.md
[8 days of signal]
Retro written to docs/retros/2026-W22.md. 14 commits, 4 stuck, 6 patterns.
```

## See also

- `/learn` — what /retro --emit-lessons drives
- `/context-save` — for actual session-end persistence
- `tasks/lessons.md` (project) / `~/.lintel/lessons.jsonl` (global) — where lessons land
- Project CLAUDE.md "Self-improvement loop" — the discipline /retro enables
