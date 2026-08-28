---
name: context-warm-related
layer: foundation
description: Heuristic context warm — search codebase for files related to a topic, load top N most-relevant.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-related skill — topic-heuristic loading.

## What this skill does

Given a topic (e.g., "rate limiter", "auth flow", "retry pattern"), heuristically finds the top N most-relevant files across cwd + `~/.lintel/scaffolding/` + `.claude/engineering/design-archive/` and loads them via `/li:context-warm`.

## When to use

- Operator says "warm context with everything related to X"
- Pre-PLAN when DISCOVER identified topic-relevant files
- Cross-repo topic understanding (e.g., compare current repo's X with scaffolding template's X)

## When NOT to use

- Specific files known — use `/li:context-warm <paths>` directly
- Whole-repo context needed — too broad for heuristic, use targeted patterns

## Workflow

### Step 1 — Topic + scope

```bash
topic="$1"
scope="${2:-cwd}"  # cwd | repo | lintel-home | all
limit="${3:-10}"
```

### Step 2 — Heuristic search

Multi-source search:
- Filename match: `find . -iname "*<topic>*"`
- Content match: `grep -rli "<topic>" --include='*.md' --include='*.ts' --include='*.py' --include='*.go'`
- Frontmatter match (for skills/agents): `grep -li "<topic>" skills/*/SKILL.md agents/*/*.md`

Score files:
- 3 points: filename match
- 2 points: ≥5 content matches
- 1 point: 1-4 content matches

Top N by score.

### Step 3 — Surface candidate list

```
CANDIDATE FILES (related to "<topic>") — top <N> by relevance:

| Score | File | Match type |
|---|---|---|
| 5 | .claude/engineering/design-archive/lintel-v3-plan.md | filename + 12 content |
| 4 | src/lib/rate-limiter.ts | filename + 8 content |
| 3 | .claude/engineering/design-archive/CONTEXT-ENGINE.md | 7 content |
| ... | | |

Estimated tokens to load all <N>: ~<X>k

Load all? (Y / select subset / cancel)
```

### Step 4 — Delegate to context-warm

If operator selects all or subset:
```bash
/li:context-warm <space-separated-paths>
```

### Step 5 — 00-state.md append

```yaml
event: context_warm_related
ts: <timestamp>
topic: <topic>
candidates_surfaced: <N>
loaded: <count>
tokens_added: <approx>
```

## Integration

Reads codebase + delegates to `/li:context-warm`. Writes to budget tracking via that skill.

## Anti-patterns

- **Loading 50+ files because "related" is broad** — cap at N=10 default, operator can extend
- **Skipping confirmation** — heuristic match isn't always right
- **Using broad topics like "api"** — too many matches; suggest narrower
