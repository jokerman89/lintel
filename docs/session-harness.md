# Lintel as a session harness

This explains the mental model for v3 and beyond. If you're new to Lintel, read this first.

---

## What "session harness" means

Lintel is not a skill library you happen to invoke. Lintel is **the harness around your agent's session** — the file structure, documentation, and mechanisms that together shape HOW the agent behaves, from first prompt to last commit.

A session has four phases. Lintel covers all four.

---

## Phase 1 — Session start ritual

When Claude Code (or Codex, Cursor, Gemini, etc.) loads in your repo, Lintel ensures it:

1. **Reads canonical session instructions** — `AGENT-INSTRUCTIONS.md` (always loaded via per-CLI entrypoint file: CLAUDE.md / AGENTS.md / GEMINI.md).
2. **Reviews accumulated lessons** — `tasks/lessons.md` so the agent doesn't repeat past mistakes.
3. **Checks compliance posture** — `scaffolding/02-sdl/HARD-RULES.md` (5 always-on rules: no customer data, no secrets, no prod mutations without auth, MS SSO only, first-party first).
4. **Scans existing ADRs** — `docs/adr/` for prior architectural decisions.
5. **Loads persona context** — `tasks/personas.md` if engagement-specific personas defined.
6. **Resolves agent precedence** — repo-local `.claude/agents/` overrides user-global `~/.claude/agents/`.
7. **Sets voice tier** — internal / trailblazer / mixed per the engagement.

Result: the agent enters mid-session with full context. No re-explaining how this team operates.

---

## Phase 2 — Mid-session interventions

While the agent is working, Lintel provides:

### Hook enforcement

15 hooks in `hooks/shared/` enforce hard rules. Operator opts in by symlinking. Examples:
- `customer-data-block` — BLOCKS commits containing customer names
- `secret-scan-block` — BLOCKS commits with detected secrets
- `no-direct-main-push` — WARNS on direct main-branch pushes
- `no-en-vocab-in-trailblazer` — WARNS when Trailblazer-tagged docs use AI-vocabulary

### Skill invocation

81 skills available via the agent CLI's plugin system. Examples:
- `/qa` — test + fix loop
- `/release-ev2` — pre-flight checks + PR creation
- `/safe-deploy-ring` — canary rollout
- `/investigate` — bug investigation
- `/rais-customer-voice-check` — Trailblazer voice gate before customer-facing artifact ships
- `/onecs-check` — 1CS compliance gate
- `/agt-tier-stamp` — AGT framework tier stamp
- `/match` — semantic router when you don't remember the exact skill name

### Subagent spawning

78 agents organized per domain. The agent CLI spawns these as subagents when context calls for it:
- `ms-specific/AzureArchitect` — Azure architecture review
- `security/ThreatModelDrafter` — STRIDE-based threat model
- `compliance/EUAIActReviewer` — EU AI Act risk tier classification
- `customer/ProposalDrafter` — customer engagement proposal draft
- `communication/EmailCustomerDrafter` — customer-facing email
- `engineering/RegressionDetective` — git bisect regression investigation

### Compliance gates

Mid-workflow, the agent invokes RAIS / OneCS / AGT / voice gates per the workflow contract:
- `/rais-customer-voice-check` before any Trailblazer-tier artifact
- `/onecs-check` before customer-bound deliverable
- `/agt-tier-stamp` before agentic system deploys

### Pause-reports

At decision points, the agent surfaces a structured pause-report. Lintel patterns establish what gets surfaced (alternatives + recommendation + completeness score), reducing operator decision fatigue.

---

## Phase 3 — Session end capture

When work wraps up, Lintel ensures durable artifacts:

### Lessons captured

Corrections during the session → `tasks/lessons.md` entries. The `/learn` skill formalizes this.

Generalizable lessons → promote to Lintel global via `bin/lintel:li-lessons-promote`. Lands in `scaffolding/01-foundation/tasks/lessons.md` so every future scaffolded repo inherits.

### ADRs drafted

Non-trivial architectural decisions → `docs/adr/NNNN-<slug>.md` via `bin/lintel:li-adr-new` or `/adr-new` skill. Travels with the repo.

### EVOLUTION-LOG appended

Changes to `CLAUDE.md` itself → entry in `EVOLUTION-LOG.md`. Future contributors see how guidance evolved + why.

### Memory committed

Cross-session durable state → `tasks/memory.md`. The `/context-save` skill writes; `/context-restore` reads next session.

### Todo handoff

If work doesn't complete → `tasks/todo.md` updated for next session. Items pre-categorized (in-progress / blocked / next).

---

## Phase 4 — Cross-session continuity

Beyond a single session:

### Memory persistence

`tasks/memory.md` lives in the repo, read on every session start. Long-term state about the engagement.

### Lessons sync

Operator-opt-in via `bin/lintel:li-lessons-sync`. Private git repo holds lessons from multiple engagement repos. Pull on machine A, lessons from machine B available.

### Brand + voice corpus sync

`~/.lintel/brand/` (MS brand assets) + `~/.lintel/voice/` (OurVoice corpus) — operator pulls from MS portal. `brand-staleness-warn` hook fires when >90 days old.

### Cross-machine state

`gstack-brain`-style pattern for syncing skill catalog updates + accumulated patterns across operator's machines.

---

## Two categories of content

Lintel ships TWO distinct categories:

### Kategori A — Agent-invokable

What the agent CLI sees via plugin manifest:
- `skills/<name>/SKILL.md` — slash commands
- `agents/<category>/<Name>.md` — subagent roles
- `hooks/shared/<name>/HOOK.md` + `run.sh` — pre/post hooks

Lives at repo root. Discovered by Claude Code, Codex, Cursor, Gemini, etc. via their native plugin marketplaces.

### Kategori B — Repo-scaffolding

What gets copied INTO other repos via `li-scaffold init`:
- `scaffolding/01-foundation/` — CLAUDE.md template, CORE-PRINCIPLES, EVOLUTION-LOG, tasks/, docs/adr/, .claude/agents/, TEMPLATE-skill.md, TEMPLATE-agent.md
- `scaffolding/02-sdl/` — compliance reference
- `scaffolding/03-ms-team/` — voice corpus + doc-gen templates

The agent CLI doesn't "load" scaffolding. The operator copies it into their working repo so future sessions in that repo have everything in place.

---

## Why this matters for MS-CAIP-SE

Without Lintel, every new customer engagement starts from blank:
- New CLAUDE.md (60-180 min to write)
- New compliance checklist
- New voice guidance
- No agent precedence resolution
- No accumulated lessons

With Lintel:
- `li-scaffold init` → 30 seconds for full base
- All skills/agents/hooks via single plugin install
- Voice corpus + compliance refs available immediately
- Lessons from prior engagements visible (via opt-in sync)

The session-harness compounds value across engagements. That's the design goal.

---

## When you contribute

Ask: "Does this contribute to the harness mechanism, or is it just a useful skill?"

Both are valuable, but harness-level work (improving session-start ritual, adding cross-cutting hooks, deepening compliance enforcement, expanding scaffolding templates) has higher leverage than single-purpose skills.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the process.
