---
name: pair-agent
layer: foundation
description: Use to pair with an available specialist context or a durable external handoff, retaining scoped turns and honest review attribution.
color: green
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot, cursor, gemini, opencode, droid]
---

# /pair-agent

Pair-programming style with a named subagent. Operator describes a task; skill brings in a specialist subagent (CodeReviewer, SecurityAuditor, PerformanceAnalyzer, etc.) to ALTERNATE with the main agent on each step. Output: two-perspective trace + final synthesis.

Distinct from `/codex` (outside-voice review post-hoc) and from spawning a subagent for a one-shot question. Pair-mode means the subagent is in the loop alongside the main agent throughout.

Bind delegation and questions through the [Universal adapter](../../shims/universal/ADAPTER.md).
Use the actual host tools and permissions. A specific tool name is not a portability boundary.
When native delegation is missing, keep the same turn brief and report for an external actor;
serial self-analysis is useful but must not be called two independent minds.

## When to use

- Sensitive change where two-perspective review during AUTHORING beats post-hoc review
- Security-sensitive code path — main agent writes, SecurityAuditor inspects each step
- Performance-critical refactor — main agent edits, PerformanceAnalyzer measures each step
- Cross-domain change where one specialist's vocabulary keeps drift in check

## When NOT to use

- Trivial change — pair overhead dominates the task
- Pure post-hoc review — use `/review` or `/codex`
- Subagent name not registered — skill won't invent agents

## Inputs

- Required `--agent <name>` — registered subagent name (e.g. `CodeReviewer`, `SecurityAuditor`, `Architect`, `Refactorer`, `DevOpsToolchain`, `ReadOnly`)
- Required: task description (inline prose)
- Optional `--turns <N>` — how many alternation turns (default: 3)
- Optional `--scope <files>` — restrict subagent's reads to these files

## Workflow

1. **Resolve subagent.** Apply operator pin, repository, active-pack and host discovery precedence.
   Inspect the actual available agent inventory; a canonical role file is not automatically a
   registered host agent. Retain a bounded external handoff when no suitable native context exists.
2. **State the task.** Print the task description so operator sees what both minds will work on.
3. **Turn loop.**
   - **Main turn:** main agent proposes a step (a diff, a decision, an investigation move). Output is shown.
   - **Specialist turn:** delegate through the actual available tool, or pause for the separately
     attributable external actor. Include the original work map/leaf IDs, profile reference,
     exact proposal/revision, read scope and report requirements. The specialist does not repair
     its own findings. Serialize writers unless isolated changes and disjoint ownership are proven.
   - **Operator gate:** use the host question channel for a missing decision: accept, modify or
     skip. Honor authorization already given for the scoped turn; do not repeat approval by habit.
4. **Iterate** until `--turns` reached or task complete.
5. **Synthesis.** Final summary: what was built, what subagent flagged, what was kept/skipped.

## Report format

```
Pair Agent: refactor src/lib/dlxClient.ts retry logic
Specialist: PerformanceAnalyzer
Turns: 3

## Turn 1
Main: propose extracting retry into separate function for testability.
PerformanceAnalyzer: structure neutral for perf; recommend benchmarking before + after.
Operator: ACCEPTED.

## Turn 2
Main: apply extraction. Diff shown.
PerformanceAnalyzer: record the actual before/after command and measured result; unrun is unverified.
Operator: ACCEPTED.

## Turn 3
Main: add reset-controller on retry per /investigate finding.
PerformanceAnalyzer: inspect actual measurements; do not infer performance from code shape.
Operator: ACCEPTED.

## Synthesis
Record actual turns, accepted decisions, remaining findings and owned changed paths.
Only claim no regression if the comparison ran against the relevant revisions.
Recommendation: /qa-only before /ship.
```

## Compliance integration

- Apply required policy controls and record whether a compatible hook, accepted equivalent or
  explicit review actually ran. Hook files or a pack label are not enforcement.
- Persist non-sensitive turn evidence through the shared audit writer when configured.
- `--scope` is an instruction boundary unless the host enforces it. Do not claim it prevents
  reads outside the set. Worktrees attribute changes but are not security sandboxes.

## Failure modes

- **Subagent not found:** list the plugin fleet's agents (`/li:catalog`), suggest one. Exit.
- **Subagent disagrees fundamentally with main agent's first proposal:** stop, report the disagreement, ask operator which path to take. Do not auto-resolve.
- **Operator rejects 3 turns in a row:** suspect the wrong specialist was paired. Suggest different `--agent` and exit.
- **Turn budget exhausted, task incomplete:** report partial state. Operator can re-run with higher `--turns`.
- **Delegation unavailable or prohibited:** keep the original scoped brief, status and next
  action for manual/external execution. Do not silently call a paid external client.
- **Independent review missing:** mark it outstanding; changing a role or model name is not
  independent review. Follow the shared evidence contract before claiming clearance.

## Examples

**Security pair on auth refactor:**
```
> /pair-agent --agent SecurityAuditor --turns 4 "refactor JWT validation to use jose library"
[4 turns: main proposes, auditor scans, operator gates]
✓ 3/4 accepted. 1 turn revised after auditor flagged token-leak in error message.
```

**Architect pair on new module:**
```
> /pair-agent --agent Architect "design new src/lib/billing/ module structure"
[3 turns of layout proposals + architectural critique]
✓ Module structure agreed: billing/{api,domain,fixtures}.ts split.
```

**Quick check pair:**
```
> /pair-agent --agent CodeReviewer --turns 1 "review this rename across 12 files"
[Single turn: main shows diff, reviewer checks for missed references]
✓ Reviewer found 2 missed references in tests/. Fix proposed.
```

**DevOps pair on CI/CD change:**
```
> /pair-agent --agent DevOpsToolchain --turns 3 "add a canary stage to the deploy workflow"
[Main proposes pipeline edits, DevOpsToolchain reviews each for SRE/observability gaps]
✓ 3/3 accepted. DevOpsToolchain added a rollback trigger on canary error-rate breach.
```

**Read-only context pair:**
```
> /pair-agent --agent ReadOnly --scope src/lib/ "explain how retry/backoff is wired before I refactor"
[Main asks, ReadOnly explores src/lib/ non-destructively and returns cited findings]
✓ ReadOnly surfaced 3 retry call-sites + 1 undocumented backoff cap.
```

## See also

- `/li:review` — post-hoc diff review (lighter than pair)
- `/li:codex` — outside-voice review post-hoc
- `/li:catalog` — lists the plugin's specialist subagent fleet
- `/li:skillify` — if pair-mode for a specific task becomes recurring, formalize as a skill
