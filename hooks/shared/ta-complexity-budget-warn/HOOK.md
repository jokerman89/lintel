---
name: ta-complexity-budget-warn
tier: warn-only
event: PreToolUse (Edit|Write)
fires_on: edited file's cyclomatic OR cognitive complexity exceeds profile.engineering.tech_architecture.complexity_budget_*
override: pass --ignore-complexity flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# ta-complexity-budget-warn

Surfaces when an edit pushes a file over the operator's complexity budget. Warning, not block — sometimes complexity is unavoidable (state machine, parser, etc.); operator decides.

## What it does

- Reads thresholds from `~/.lintel/profile.yaml` `engineering.tech_architecture.complexity_budget_cyclomatic` (default 12) and `complexity_budget_cognitive` (default 18)
- Detects language + invokes appropriate tool (gocyclo / radon / lizard) on the edited file
- If either metric exceeds budget: WARN with the score + budget delta

## Why warn-only

- Budget is a target, not a hard rule
- Some code is inherently complex (parsers, state machines, optimizers)
- Block at edit time would interrupt operator flow; warn lets them complete + revisit
- `/li:ta single --action complexity-audit` is the full-pass tool with refactor recommendations

## Override path

`--ignore-complexity "reason"` on the edit. Reason logged to audit. Frequent overrides on the same file signal a refactor candidate.

## What's NOT in scope

- Refactor recommendations (that's `/li:ta complexity-audit`)
- Aggregating per-component scores (sub-skill aggregates; hook is per-file)
- Hard-blocking on complexity (warn-only by design; v4.2+ may add per-pack opt-in block)

## Audit format

```jsonl
{"hook":"ta-complexity-budget-warn","tier":"warn","ts":"...","file_edited":"src/parser.go","cyclomatic":18,"cognitive":24,"budget_cyclomatic":12,"budget_cognitive":18,"operator":"<operator>"}
```
