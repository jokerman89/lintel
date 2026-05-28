---
name: codex
layer: foundation
description: Outside-voice second opinion via Codex CLI. Independent review of diff, plan, or hypothesis.
color: purple
tools: Bash, Read
voice: internal
cli_support: [claude-code]
---

# /codex

Invokes the Codex CLI as an independent reviewer. Codex sees the same files but not this session's prior context — that disconnect is the point. Use when you want a second opinion uncontaminated by the framing already in this conversation.

The skill itself runs in Claude Code (which is why `cli_support: [claude-code]` is single-entry). Codex is invoked as a subprocess; its output is parsed and surfaced back here.

## When to use

- Pre-`/release-ev2` outside-voice review on a non-trivial diff
- `/investigate` produced a confident root cause and you want it independently challenged
- A design decision was made in conversation and you want a fresh-eyes critique
- `/plan-eng-review` cleared with caveats — use Codex to triangulate the caveats

## When NOT to use

- The work is trivial — Codex tokens cost real money
- You've already disagreed with Codex twice on this same diff — escalate to a human reviewer instead
- Codex CLI isn't installed — surface that as a setup gap, do not silently fall back to "Claude reviewing itself"

## Inputs

- Required: target (one of `--diff`, `--plan <file>`, `--code <file>`, `--hypothesis "<text>"`)
- Optional `--prompt-style <strict|exploratory>` — strict = "find what's wrong", exploratory = "what would you do differently"
- Optional `--budget <tokens>` — cap Codex call (default: 50k tokens)

## Workflow

1. **Preflight.** Verify `codex` is on PATH. If not: report missing setup + exit. No fallback.
2. **Construct prompt.** Inject the target (diff, plan body, code excerpt, hypothesis statement). Wrap in a directive: "You are reviewing this independently. The author has their own reasoning; surface what you'd push back on."
3. **Run Codex.** `codex exec --quiet --output json --prompt-file <tmp>` (or equivalent — adjust to current Codex CLI flags). Capture stdout, stderr, exit code.
4. **Parse output.** Codex returns structured findings (severity, location, claim, evidence). Normalize to Lintel's P1/P2/P3 severity.
5. **Compare to local reasoning.** If invoked mid-`/investigate` or post-`/review`: explicitly diff Codex's findings against what was already concluded. Surface AGREEMENT and DISAGREEMENT separately.
6. **Persist via gstack-review-log** with `skill: codex` so downstream `/release-ev2` can read.
7. **Report.**

## Report format

```
Codex Review: <target>

Codex CLI: codex@1.4.2 (exec mode, exploratory style, budget 50k)
Tokens used: 31,400 / 50,000

## Findings from Codex (3)

[P1] (Codex confidence: 9/10) src/lib/dlxClient.ts:87
   "The retry logic creates an AbortController but never resets between attempts. Second retry will abort itself."
   ← AGREES with /investigate root cause from this session.

[P2] (Codex confidence: 7/10) src/lib/dlxClient.ts:42
   "Error handling swallows the original stack trace. Hard to debug downstream."
   ← NEW finding, not raised in local review.

[P3] (Codex confidence: 6/10) src/lib/dlxClient.ts:120
   "Magic number 30000 should be a named constant."
   ← Style nit, agree.

## Synthesis
- 1 finding agrees with local conclusion (strengthens confidence)
- 1 new finding (P2) — recommend addressing before /release-ev2
- 1 style nit (P3) — defer or include in same diff
```

## Compliance integration

- Codex sees code. Per Layer 2: code is not customer-data, so no auth gate. But: if the target includes a fixture path containing customer-data patterns, BLOCK the Codex call and surface (Codex would receive that data).
- Token spend logged to `~/.lintel/audit/codex-spend.jsonl`.
- First-party-first reminder: Codex is OpenAI. For MS-internal: prefer Azure OpenAI gateway if configured per `~/.lintel/config.yaml`.

## Voice tier note

`voice: internal`. Outside-voice review is engineering-internal. Codex's voice is its own — we do not rewrite it.

## Failure modes

- **Codex CLI missing:** report + exit. No fallback to Claude self-review (that defeats the purpose).
- **Codex returns malformed output:** capture raw stdout to `~/.lintel/audit/codex-raw-<ts>.txt`, report parse failure, exit.
- **Budget exceeded mid-call:** Codex's own truncation kicks in. Report partial findings + budget overflow.
- **Codex output contains a finding referencing a file we never sent:** flag as hallucination, suppress from main report, log to debug appendix.

## Examples

**Outside opinion on a diff:**
```
> /codex --diff
Codex found 2 P2 findings the local review missed. Recommend addressing before /release-ev2.
```

**Challenge a hypothesis:**
```
> /codex --hypothesis "retry abort controller bug at dlxClient:87"
Codex agrees (9/10 confidence). Strengthens the root cause.
```

**Style-only review:**
```
> /codex --code src/components/case/AgentModeChip.tsx --prompt-style exploratory
3 stylistic suggestions, no correctness issues.
```

## See also

- `/review` — local diff review (use `/codex` as a follow-up for important diffs)
- `/investigate` — `--with-codex` flag chains automatically
- `/plan-eng-review` — uses `/codex` internally as the outside-voice step
- `/release-ev2` — reads codex review-log entries as part of clearance check
