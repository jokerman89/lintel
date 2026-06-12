---
name: discover
layer: foundation
description: Phase 3 of Lintel cycle — map codebase, surface ADRs, apply lessons, identify reusable patterns + agents/skills relevant to the wedge. Read-only context preparation for PLAN.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "PLAN flies blind on prior ADRs, applicable lessons, and existing skills/agents; work reinvents what already exists or contradicts decisions already made."
---

You are the DISCOVER skill — Phase 3 of the Lintel cycle.

## What this skill does

Maps the surface area relevant to the locked design. Surfaces prior decisions (ADRs), applicable lessons, dependencies that touch the wedge area, existing skills/agents to reuse (avoid duplication). Produces `discover-report.md` consumed by PLAN.

The principle: don't reinvent. Find what we have. Surface what constrains.

## When to use

- After DEFINE when scope is known and PLAN needs context
- Standalone when operator asks "what do we already have for X?"
- Pre-PLAN when changing area operator hasn't touched recently
- After SENSE if intent=research-dive (DISCOVER + DEFINE is the wedge for that mode)

## When NOT to use

- intent=hotfix (skip DISCOVER, go to BUILD)
- intent=ship-only (no discovery needed)
- Known territory operator has worked in this week (operator override)
- Trivial single-file edit

## Workflow

### Step 1 — Codebase map (Grep/Glob, targeted)

From DEFINE's design doc, extract 5-10 keywords (technology, domain, function names). Map:

```bash
# File presence
for keyword in "${keywords[@]}"; do
  # Find files matching keyword in path
  glob_matches=$(find . -type f -name "*${keyword}*" 2>/dev/null | head -5)
  # Find files containing keyword in content
  grep_matches=$(grep -rl "$keyword" --include='*.{ts,js,py,go,rs,bicep,yml,yaml,md}' . 2>/dev/null | head -10)
  # Report
done
```

Rule: cap at top 20 most-relevant files. Don't read every file — just identify.

If wedge area is large (>1000 files match), surface to operator: "Scope is large. Narrow further or accept partial map?"

### Step 2 — ADR scan

```bash
[ -d ".claude/decisions/" ] && {
  for adr in .claude/decisions/[0-9]*-*.md; do
    # Read title + status + summary
    title=$(grep '^# ' "$adr" | head -1)
    status=$(grep -i '^status:' "$adr" | head -1)
    # Match keywords
    for keyword in "${keywords[@]}"; do
      grep -qi "$keyword" "$adr" && relevant_adrs+=("$adr")
    done
  done
}
```

For relevant ADRs:
- Status: Accepted / Proposed / Deprecated / Superseded — report
- If ADR contradicts the proposed approach, FLAG explicitly (don't bury)
- Surface ADR-IDs that the new design must respect or supersede

### Step 3 — Lessons scan (filtered by relevance)

Invoke `/li:lessons` skill OR inline:
- Read `.claude/memory/lessons.md`
- Filter by keyword match + topic similarity to wedge
- Surface top 3-5 lessons with "Why this might apply now: <one-line>"

### Step 4 — Dependency audit (if wedge touches third-party)

Detect via package.json / requirements.txt / Cargo.toml / go.mod / etc:
```bash
# Examples
[ -f "package.json" ] && deps=$(jq -r '.dependencies | keys[]' package.json | head -20)
[ -f "requirements.txt" ] && deps=$(cat requirements.txt | head -20)
```

If wedge involves third-party libs:
- Surface relevant deps from manifests
- Note any deprecated/CVE-flagged libs (light check, not full audit)
- For deeper audit: recommend DependencyAuditor agent in PLAN phase

### Step 5 — Related skill scan (avoid duplication)

```bash
# Search skills/ for skills that overlap with the wedge
for skill in skills/*/SKILL.md; do
  description=$(grep '^description:' "$skill" | head -1)
  # If description contains wedge-keywords, surface
done
```

If skills overlap >50% with proposed work:
- Flag operator: "Skill /li:<existing> already covers <area>. Extend it or build new?"
- Recommend `/li:skillify` if creating new vs extending

### Step 6 — Related agent scan (PLAN dispatch hints)

Match wedge to existing agents that should be subagent-pulled in PLAN/BUILD:

```bash
# For each agent category, score relevance to wedge
# Categories are directory-derived so the scan can never drift from agents/.
for cat_dir in agents/*/; do
  cat=$(basename "$cat_dir")
  for agent in agents/$cat/*.md; do
    [ "$(basename "$agent")" = "_TEMPLATE.md" ] && continue
    [ "$(basename "$agent")" = "README.md" ] && continue
    name=$(basename "$agent" .md)
    description=$(grep '^description:' "$agent" | head -1)
    # If keywords match, add to recommended_agents[]
  done
done
```

Output recommended agents organized by category. PLAN uses this to know which subagents to dispatch.

### Step 6b — Synthesize findings via `ResearchSynthesizer` (research-dive mode, or on operator request)

When invoked in research-dive mode (via `/li:research`) or when the wedge spans many sources, dispatch `ResearchSynthesizer` to aggregate the codebase map + ADRs + lessons + deps into a single structured brief:

```bash
synth_brief=$(mktemp)
cat > "$synth_brief" <<EOF
task: Synthesize discover findings into a structured research brief
context_pointers:
  - codebase map (Step 1 output)
  - relevant ADRs (Step 2 output)
  - applicable lessons (Step 3 output)
  - flagged dependencies (Step 4 output)
constraints:
  - state of the art + gaps + recommendations
  - cite sources (file paths, ADR-IDs, lesson titles)
acceptance:
  - structured brief with state-of-the-art, gaps, recommendations, citations
EOF

/li:brief-forge subagent_spawn discover ResearchSynthesizer brief "$synth_brief"
```

### Step 7 — Context warmup hint (operator opt-in)

If discover-report identifies files outside what's currently in context, surface:

"Context warmup recommended for PLAN phase:
- 8 ADRs (~12k tokens) — `/li:context-warm-adrs networking`
- Related skills overlap (~5k tokens) — `/li:context-warm 'skills/li-*'`
- Infra templates (~15k tokens) — `/li:context-warm '~/Workspace/project-X/infra/*'`

Estimated total warm-up: ~32k tokens. Headroom available: <X>k."

Operator decides whether to warm up before PLAN.

### Step 8 — Write discover-report.md

```yaml
# .claude/runtime/state/discover-report-<datetime>.md
---
phase: DISCOVER
ts: <timestamp>
wedge_keywords: [...]
files_mapped: <count>
adrs_relevant: <count>
lessons_applied: <count>
deps_flagged: <count>
agents_recommended: <count>
skills_overlap: <count>
---

# Codebase map (top 20)
- <file path>: <brief why-relevant>
...

# ADRs (relevant)
- ADR-NNNN <title>: <Accepted | Proposed | Deprecated>
  - Constraint imposed: <one-line>
  - Conflict with proposed approach: <yes/no>
...

# Lessons applied
- <lesson title> (<date>): <why this might apply now>
...

# Dependencies flagged
- <pkg@version>: <CVE / deprecated / outdated / OK>
...

# Recommended agents for PLAN dispatch
| Category | Agent | Why |
|---|---|---|
| engineering | SystemArchitect | wedge involves system-level design |
| security | SecretsScanReviewer | wedge touches auth flow |
| ...

# Skills overlap (avoid duplication)
- /li:<existing>: <% overlap> — <extend vs new?>

# Context warmup recommendations
- <suggested warm-up sets with token estimates>

# Open questions for PLAN
- <gap 1>
- <gap 2>
```

### Step 9 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation:

```bash
source "$LINTEL_REPO_ROOT/lib/state.sh"
state_append DISCOVER DONE next=PLAN report_path=.claude/runtime/state/discover-report-<datetime>.md files_mapped=<count> adrs_found=<count> lessons_applied=<count>
```

## Status protocol

- **DONE** — report written, agents/skills identified for PLAN, no scope blockers
- **DONE_WITH_CONCERNS** — gaps surfaced (missing tests, stale docs, ADR conflicts to resolve)
- **BLOCKED** — wedge scope too large to map cheaply (>1000 file matches); operator must narrow
- **NEEDS_CONTEXT** — wedge unclear, return to DEFINE

## Pause-points

Optional: operator can ask "show me what you found" mid-phase. Otherwise runs to completion.

If ADR conflicts proposed approach: PAUSE, surface conflict, AskUserQuestion "Supersede ADR-NNNN or revise design?"

## Hop-in support

YES — standalone for "tell me what we have on X." Useful for research-dive mode + pre-PLAN orientation.

Skip-conditions: intent=hotfix, intent=ship-existing-branch, known territory operator override.

## Integration

**Reads:**
- cwd codebase (Grep/Glob, capped at top-20 files)
- `.claude/decisions/*.md`
- `.claude/memory/lessons.md`
- `package.json` / `requirements.txt` / `Cargo.toml` / etc
- `skills/*/SKILL.md` (description field only)
- `agents/<category>/*.md` (description field only)

**Writes:**
- `.claude/runtime/state/discover-report-<datetime>.md`
- `.claude/runtime/state/00-state.md` (DISCOVER entry)

**Triggers:**
- `/li:context-warm` recommendations (operator-driven, not auto)
- `/li:plan` next (or PLAN within /li:cycle)

## Anti-patterns

- **Reading every matched file** — pick top 20 most-relevant via heuristics
- **Re-running grep for keywords DEFINE already established** — DEFINE wrote them, use them
- **Ignoring ADRs that contradict the proposed approach** — flag, don't bury
- **Full dependency audit** — that's DependencyAuditor's job in PLAN/REVIEW, here just flag
- **Loading found files into context automatically** — only surface paths + token estimates, let operator warm
- **Recommending too many agents** — pick top 3-5 per category, not all 78
- **Skipping skill-overlap check** — duplication is bloat-risk

## Failure recovery

- **Scope too large** (>1000 file matches): surface to operator, ask to narrow or accept partial
- **No ADRs found**: note "No related ADRs — design has no prior constraints from this area"
- **Codebase has no convention**: surface honestly, don't fabricate patterns

## Voice tier behavior

`voice: internal`. Report is engineering-internal.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
