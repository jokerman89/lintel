---
name: li-research
layer: foundation
description: Composite shortcut for research-dive — runs SENSE + DEFINE + DISCOVER, no BUILD/SHIP. For "understand before commit" mode.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the RESEARCH composite shortcut — research-dive mode pre-baked.

## What this skill does

Research-dive workflow: explore + understand, no code yet. Equivalent to:
```
/lintel:li-cycle --mode research-dive
```

Runs 3 phases (SENSE → DEFINE → DISCOVER). Skips PLAN/BUILD/REVIEW/SHIP/CAPTURE.

Output: APPROVED design doc + discover-report.md. Operator can later resume with `/lintel:li-resume` to PLAN if research validates the direction.

## When to use

- New domain / unfamiliar territory
- Pre-engagement "what do we have for X?" survey
- Customer asks "what would this look like?" — design + discovery before commit
- Operator wants to understand existing patterns before extending
- Cost expectation: ~10-20k tokens, 20-40 min

## When NOT to use

- Ready to build — use `/lintel:li-cycle` (full)
- Known territory — skip DISCOVER, just `/lintel:li-define`
- Just want quick info on a service — use `/lintel:li-az-tldr <service>` (Azure toolbox)
- No design discussion needed — use `/lintel:li-discover` standalone

## Workflow

### Step 1 — Pre-flight

AskUserQuestion (brief): "Research mode produces design doc + discover-report but no code. Continue? (Y/n)"

### Step 2 — Delegate to /lintel:li-cycle

```bash
/lintel:li-cycle --mode research-dive
```

Mode preset handles:
- audience=solo
- voice_tier=internal
- compliance=none (read-only, no compliance gates apply)
- Cost expectation pre-set medium

### Step 3 — Post-research output

After DISCOVER DONE, surface:
```
RESEARCH COMPLETE — <wedge>

Artifacts produced:
  - Design doc: <docs/design/lintel-*-design-*.md> (APPROVED)
  - Discover report: <.lintel/state/discover-report-*.md>

Findings:
  - ADRs surfaced: <N>
  - Lessons applied: <N>
  - Existing skills overlap: <N>
  - Recommended agents for future PLAN: <list>

Next options:
  • /lintel:li-resume → continue to PLAN if direction validated
  • /lintel:li-capture → write findings as standalone artifact (no full cycle)
  • Decide later — design doc + discover-report persist
```

## Status protocol

Inherits from /lintel:li-cycle. Most often DONE (research can't really fail unless DISCOVER blocks on scope).

## Pause-points

- Initial mode-confirmation
- DEFINE forcing questions (all 6, per office-hours discipline)
- Premise check + alternatives + design doc approval gate

## Hop-in support

n/a — research-dive is the shortcut.

## Integration

Delegates to `/lintel:li-cycle --mode research-dive`.

## Anti-patterns

- **Research-then-immediate-build without re-running PLAN** — research validates direction, PLAN turns it into tasks
- **Skipping the design doc approval gate because "this is just research"** — design doc commits to a wedge, gate confirms it

## Voice tier behavior

`voice: internal`. Research output is operator-internal. If operator later wants to share findings with customer, voice gate fires at that downstream skill (e.g., `/lintel:li-exec-brief`).
