---
name: research
layer: foundation
description: Composite shortcut for research-dive — runs SENSE + DEFINE + DISCOVER, no BUILD/SHIP. For "understand before commit" mode.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: OPTIONAL
gap_if_skipped: "Operator loses the research-dive shortcut; the same SENSE+DEFINE+DISCOVER chain is still reachable via /li:cycle --mode research-dive, so only the convenience is lost."
---

You are the RESEARCH composite shortcut — research-dive mode pre-baked.

## What this skill does

Research-dive workflow: explore + understand, no code yet. Equivalent to:
```
/li:cycle --mode research-dive
```

Runs 3 phases (SENSE → DEFINE → DISCOVER). Skips PLAN/BUILD/REVIEW/SHIP/CAPTURE.

Output: sourced findings, explicit uncertainties and options, plus a discover report
when artifact writing is authorized. DEFINE frames the research question and source
boundary; it does not demand an APPROVED implementation design or venture interview.
Later implementation needs its own scoped design/PLAN approval.

Follow [task-relevant intake](../define/references/intake.md) and the
[work-map contract](../spec-kit/references/work-map.md). Preserve an existing selected
map through `bin/li-work-artifacts.py`; do not create a competing implementation
backlog for an investigation. If all writes were forbidden, report findings without
creating runtime or design files.

## When to use

- New domain / unfamiliar territory
- Pre-engagement "what do we have for X?" survey
- Customer asks "what would this look like?" — design + discovery before commit
- Operator wants to understand existing patterns before extending
- Cost expectation: ~10-20k tokens, 20-40 min

## When NOT to use

- Ready to build — use `/li:cycle` (full)
- Known territory — skip DISCOVER, just `/li:define`
- Just want a quick lookup on a single topic — a focused web search is enough
- No design discussion needed — use `/li:discover` standalone

## Workflow

### Step 1 — Pre-flight

Use the requested research scope. Ask only missing source-access or material
research questions through the host's actual channel; do not ask again whether to
perform the research the operator just requested.

### Step 2 — Delegate to /li:cycle

```bash
/li:cycle --mode research-dive
```

Mode preset handles:
- audience=solo
- voice_tier=internal
- Applicable read/data-handling policy still applies; read-only is not a policy exemption
- Cost expectation pre-set medium

### Step 3 — Post-research output

After DISCOVER DONE, surface:
```
RESEARCH COMPLETE — <wedge>

Artifacts produced:
  - Research brief: <explicit selected path, if writing was authorized> (findings, not implementation approval)
  - Discover report: <.claude/runtime/state/discover-report-*.md>

Findings:
  - ADRs surfaced: <N>
  - Lessons applied: <N>
  - Existing skills overlap: <N>
  - Recommended agents for future PLAN: <list>

Next options:
  • PLAN can use the findings after implementation scope is actually authorized
  • /li:capture → write findings as standalone artifact (no full cycle)
  • Decide later — design doc + discover-report persist
```

## Pause-points

- Only unresolved research questions, missing access authority or genuinely
  contested premises. Optional strategy questions require the selected venture lens.

## Integration

Delegates to `/li:cycle --mode research-dive`.

## Anti-patterns

- **Research-then-immediate-build without re-running PLAN** — research validates direction, PLAN turns it into tasks
- **Treating research completion as an approved design or permission to build/ship** —
  preserve the requested read operation, findings and uncertainty
