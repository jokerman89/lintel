---
name: jstack-pair-agent
description: Pair with a named subagent in the loop — explicit two-mind collaboration on a focused task.
color: green
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code]
---

# /pair-agent

Pair-programming style with a named subagent. Operator describes a task; skill brings in a specialist subagent (CodeReviewer, SecurityAuditor, PerformanceAnalyzer, etc.) to ALTERNATE with the main agent on each step. Output: two-perspective trace + final synthesis.

Distinct from `/codex` (outside-voice review post-hoc) and from spawning a subagent for a one-shot question. Pair-mode means the subagent is in the loop alongside the main agent throughout.

`cli_support: [claude-code]` only — subagent orchestration uses the Agent tool, which is Claude Code-native.

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

- Required `--agent <name>` — registered subagent name (e.g. `CodeReviewer`, `SecurityAuditor`, `Architect`, `Refactorer`)
- Required: task description (inline prose)
- Optional `--turns <N>` — how many alternation turns (default: 3)
- Optional `--scope <files>` — restrict subagent's reads to these files

## Workflow

1. **Resolve subagent.** Look up `--agent` in user-level (`~/.claude/agents/`) then repo-level (`.claude/agents/`). If not found: list available + exit.
2. **State the task.** Print the task description so operator sees what both minds will work on.
3. **Turn loop.**
   - **Main turn:** main agent proposes a step (a diff, a decision, an investigation move). Output is shown.
   - **Subagent turn:** subagent reviews the proposal from its specialty. Spawned via Agent tool with focused prompt + scope.
   - **Operator gate:** AskUserQuestion — accept, modify, or skip this step.
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
PerformanceAnalyzer: benchmark check — function call overhead negligible (<1µs). No regression.
Operator: ACCEPTED.

## Turn 3
Main: add reset-controller on retry per /investigate finding.
PerformanceAnalyzer: micro-benchmark — adds 50ns per retry, immaterial.
Operator: ACCEPTED.

## Synthesis
3 turns, 3 accepted. PerformanceAnalyzer raised 1 minor concern (resolved via benchmark). No perf regression detected.
Final diff: src/lib/dlxClient.ts +18 -7.
Recommendation: /qa-only before /release-ev2.
```

## Compliance integration

- Each main-agent Edit goes through normal Layer 2 sanity-scan.
- Subagent invocations logged to `~/.jstack/audit/pair-agent.jsonl`.
- Subagent inherits scope restriction from `--scope`; cannot read outside that set.

## Voice tier note

`voice: internal`. Pair collaboration is engineering-internal.

## Failure modes

- **Subagent not found:** list registered agents from `~/.claude/agents/` and `.claude/agents/`, suggest one. Exit.
- **Subagent disagrees fundamentally with main agent's first proposal:** stop, report the disagreement, ask operator which path to take. Do not auto-resolve.
- **Operator rejects 3 turns in a row:** suspect the wrong specialist was paired. Suggest different `--agent` and exit.
- **Turn budget exhausted, task incomplete:** report partial state. Operator can re-run with higher `--turns`.
- **`Agent` tool unavailable (running in Codex/Copilot):** STOP — this skill is claude-code only. Surface alternative (use `/codex` post-hoc instead).

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

## See also

- `/review` — post-hoc diff review (lighter than pair)
- `/codex` — outside-voice review post-hoc
- `~/.claude/agents/` — registered specialist subagents
- `/skillify` — if pair-mode for a specific task becomes recurring, formalize as a skill
