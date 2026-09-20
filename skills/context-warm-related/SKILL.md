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

Given a literal topic (e.g., "rate limiter", "auth flow", "retry pattern"), rank files
within an explicitly selected root and bounded patterns, then load them via `/li:context-warm`.
Repository, installed scaffolding and design-archive comparisons remain available, but no
personal home or external repository is searched implicitly.

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
source "${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}/bin/_context.sh"
topic="${1:?Supply a literal topic}"
pattern="${2:?Supply a bounded relative glob}"
limit="${3:-10}"
context_select --glob "$pattern" --topic "$topic" --limit "$limit"
```

### Step 2 — Heuristic search

The selector searches literal topic occurrences in filenames and bounded file contents,
including frontmatter when skill/agent files are selected. The topic is not a shell command
or a regex. Links/reparse escapes, ignored paths and byte/file limits use the base reader.
For multiple patterns, pass each as a separate `--glob`; never join filenames into one string.

The familiar `cwd`, `repo`, `lintel-home` and `all` scope choices are requests to identify
explicit roots, not recursive scans of a user's workspace. For `lintel-home`, select the
authorized installed scaffolding root only. For `all`, preview each authorized root
separately, preserving its source identity and exclusions. Missing scope is a decision,
not permission to inspect private trees.

Score files:
- 3 points: filename match
- 2 points: ≥5 content matches
- 1 point: 1-4 content matches

Top N by score, with deterministic path tie-breaking and an explicit omitted count.
The helper implements this ranking; the preview lists actual paths and byte estimates.

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

If the operator selects all or a subset, pass each manifest path as a separate literal
`--path` to `/li:context-warm` in the same explicit root. Recheck changed sources before
reading. State unknown capacity as unknown; ranking is not a headroom measurement.

### Step 5 — 00-state.md append

```yaml
event: context_warm_related
ts: <timestamp>
topic: <topic>
candidates_surfaced: <N>
loaded: <count>
estimated_input_tokens: <source-byte heuristic, not measured active usage>
```

## Integration

Reads codebase + delegates to `/li:context-warm`. Writes to budget tracking via that skill.

## Anti-patterns

- **Loading 50+ files because "related" is broad** — cap at N=10 default, operator can extend
- **Skipping confirmation** — heuristic match isn't always right
- **Using broad topics like "api"** — too many matches; suggest narrower
