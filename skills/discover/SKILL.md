---
name: discover
layer: foundation
description: Use after DEFINE, before PLAN, to gather context before planning — maps the codebase, surfaces relevant ADRs and lessons, and identifies reusable patterns, agents, and skills for the chosen wedge. Read-only; produces the grounding PLAN needs so it does not reinvent or contradict prior decisions.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
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

Retain the explicitly selected [work map](../spec-kit/references/work-map.md) and
verify its P07 reference before policy consumption. `bin/li-work-artifacts.py
--view context` supplies the original specification/design/task paths. For research,
the research question is sufficient input: no approved implementation design is
required and no BUILD/SHIP authority follows.

### Step 1 — Codebase map (Grep/Glob, targeted)

From the selected design or research question, extract a few focused keywords
(technology, domain, function names). Use P03's bounded literal selector:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_context.sh"
context_select --glob 'src/**/*.ts' --glob 'src/**/*.js' --glob 'src/**/*.py' \
  --glob 'src/**/*.go' --glob 'src/**/*.rs' --glob 'docs/**/*.md' \
  --topic "${keyword:?select a literal topic}" --limit 20
```

Substitute the repository's real directories/extensions and explicit glob arguments;
do not pass a quoted brace expression to `grep --include`. This reader finds content-only
matches too and reports unmatched selectors/omissions instead of manufacturing a complete
map. It returns metadata; use permitted file reads for the relevant content.

If wedge area is large (>1000 files match), surface to operator: "Scope is large. Narrow further or accept partial map?"

### Step 2 — ADR scan

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_context.sh"
context_select --glob '.claude/decisions/[0-9]*-*.md' --adr-status all \
  --topic "${keyword:?select a literal topic}" --limit 20
```

For relevant ADRs:
- Status: Accepted / Proposed / Deprecated / Superseded — report
- If ADR contradicts the proposed approach, FLAG explicitly (don't bury)
- Surface ADR-IDs that the new design must respect or supersede
- P03's `adr_metadata` reads both YAML and actual Markdown `Status`/`Date`
  conventions. Unknown status remains visible; deprecated/superseded documents
  remain discoverable as history. Use the repository's declared legacy ADR directory
  when applicable, never a second status parser.

### Step 3 — Lessons scan (filtered by relevance)

Invoke `/li:lessons-surface` skill OR inline:
- Read the project lessons store through `lib/memory.sh` (`lessons_find_related <wedge keywords>`;
  the store is `lintel_lessons_file`, and a second ignored store is named, never hidden)
- Filter by keyword match + topic similarity to wedge
- Surface top 3-5 lessons with "Why this might apply now: <one-line>"; print a full block with
  `bin/li-lessons.py get --id L-NNN`

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
for skill in "${LINTEL_SOURCE_ROOT:?select trusted source}"/skills/*/SKILL.md; do
  description=$(grep '^description:' "$skill" | head -1)
  # If description contains wedge-keywords, surface
done
```

If skills overlap >50% with proposed work:
- Flag operator: "Skill /li:<existing> already covers <area>. Extend it or build new?"
- Recommend `/li:skill-new` if an authorized new skill is needed rather than an extension

### Step 6 — Related agent scan (PLAN dispatch hints)

Match wedge to existing agents that should be subagent-pulled in PLAN/BUILD:

```bash
# For each agent category, score relevance to wedge
# Categories are directory-derived so the scan can never drift from agents/.
for cat_dir in "${LINTEL_SOURCE_ROOT:?select trusted source}"/agents/*/; do
  cat=$(basename "$cat_dir")
  for agent in "$cat_dir"*.md; do
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

When invoked in research-dive mode (via `/li:cycle --from SENSE --to DISCOVER`) or when the work spans many sources, use an available, authorized `ResearchSynthesizer` role to aggregate the codebase map, ADRs, lessons and dependencies into a structured brief. Without real delegation, synthesize serially and label that limitation:

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
- Relevant ADRs — `/li:context-warm` with its ADR-topic selection mode
- Related skills overlap (~5k tokens) — `/li:context-warm 'skills/li-*'`
- Selected infrastructure templates — `/li:context-warm 'infra/*'`

Use the actual selected inputs and known host headroom; otherwise report the
estimate and capacity as unknown."

Operator decides whether to warm up before PLAN.

### Step 8 — Write discover-report.md

```yaml
# .claude/runtime/state/discover-report-<datetime>.md
---
phase: DISCOVER
ts: <timestamp>
cycle_id: <selected cycle>
work_map: <selected work.json or explicitly unmapped research>
profile: <verified P07 reference, not a pack name alone>
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

Link the exact report from the selected work handoff. PLAN and
`/li:inspect --target plan` consume the same reuse map, accepted constraints and
unresolved findings; discovery does not grant review or implementation clearance.

### Step 9 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation:

```bash
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/lib/state.sh"
state_append DISCOVER "${discover_status:?set actual discovery status}" next=PLAN \
  "report_path=${discover_report:?select the persisted report}" \
  "files_mapped=${files_mapped:?record observed count}" \
  "adrs_found=${adrs_found:?record observed count}" \
  "lessons_applied=${lessons_applied:?record observed count}"
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
- The project lessons store (`lintel_lessons_file`), through `lib/memory.sh`
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
- **No ADRs matched**: report the selectors and bounded coverage; missing/unreadable
  metadata is not proof that no prior constraint exists
- **Codebase has no convention**: surface honestly, don't fabricate patterns

## Voice tier behavior

`voice: internal`. Report is engineering-internal.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
