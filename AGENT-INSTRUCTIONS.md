# Agent instructions — JStack canonical navigation pointer

Read this file at session start. Each agent CLI (Claude Code, GitHub Copilot Enterprise, Codex, others) has a shim that points here.

This file is **navigation, not content.** Load-bearing content lives in the layer files below. Follow the order; each layer file is short and authoritative.

---

## Order of operations at session start

Walk these in order. Each step references the authoritative layer file.

### 1. Read principles

**Layer 1 — `scaffolding/01-foundation/CORE-PRINCIPLES.md`** — 10 load-bearing rules. Authoritative. Plan before code. Subagents for parallel work. Self-improvement loop. Verify before done. Deviation flagging. Auto-mode bounds. Cleanup when bound crossed. Shared schema discipline. Simplicity first. Documented change beats silent change.

Do NOT re-state the rules inline here. They live in CORE-PRINCIPLES.md and change rarely. Read once, hold them as load-bearing for the session.

### 2. Run the compliance checklist

**Layer 2 — `scaffolding/02-sdl/SESSION-START-CHECK.md`** — the 5-step checklist. Authoritative.

A clean five-OK pass is the floor for any non-trivial action. Trivial actions (typo fix, doc edit, question) can skip. The five steps:

1. Authority scope
2. Customer-data check
3. Production-mutation check
4. Secrets check
5. Hard-rule check (see `scaffolding/02-sdl/HARD-RULES.md` for the 5 always-on rules)

This is an operator-confirmed checklist, NOT automated enforcement. The harness surfaces the items; the operator confirms.

### 3. Load personas

**Layer 1 — `tasks/personas.md`** in the active repo (scaffolded from `scaffolding/01-foundation/tasks/personas.md`).

Calibrates communication style for the operator. Read once per session.

### 4. Load memory

**Layer 1 — `tasks/memory.md`** in the active repo.

Long-running state. Operator profile, project context, feedback patterns, external references.

### 5. Recent lessons

**Layer 1 — `tasks/lessons.md`** in the active repo — read the most recent 10-15 entries. Older entries are reference material.

### 6. ADR scan

**Layer 1 — `docs/adr/`** in the active repo — list filenames first, read full content only for ADRs whose title is relevant to the current task.

### 7. Agent selection precedence

**Layer 3 — `scaffolding/03-personal-advanced/precedence/README.md`** — 5-level precedence model:

1. Operator pin (named in prompt)
2. Repo-level override (`.claude/agents/<Name>.md`)
3. Promoted list (`scaffolding/03-personal-advanced/promoted-agents.md`, tier-stamped)
4. User-global (`~/.claude/agents/`)
5. Fallback (main agent, no delegation)

This precedence is enforced by skill instructions in v1 — no runtime policy engine. Agents reading this file follow the rule.

---

## Layer index

| Layer | Path | Change rate | When to read |
|---|---|---|---|
| 1 Foundation | `scaffolding/01-foundation/` | Stable (EVOLUTION.md process) | Every session-start |
| 2 Compliance | `scaffolding/02-sdl/` | MS-policy-driven (quarterly) | Every session-start (checklist) + on-demand (`/compliance-check`) |
| 3 Personal advanced | `scaffolding/03-personal-advanced/` | Opinionated (team PR) | When delegating to subagents OR when output is customer-facing |
| 4 Power user | `scaffolding/04-power-user/` | Experimental (free adaptation) | Only when task explicitly invokes a Layer 4 pattern |

Full architecture rationale in [`LAYERS.md`](LAYERS.md).

---

## Voice tier (Layer 3)

If this session involves an agent generating customer-facing or official-communication content: the agent declares `voice: trailblazer` in its frontmatter, and output is checked via `/rais-customer-voice-check` against the 12-cell Microsoft Our Voice grid.

If the session is internal dev work (code review, planning, tests, install): `voice: internal` — direct, builder-talking-to-builder, no Trailblazer overhead.

Voice tier is the per-agent honest split between marketing voice (for customers) and engineering voice (for the team). See `scaffolding/03-personal-advanced/voice/README.md`.

---

## Self-maintenance — context-bloat watchers (Layer 4, opt-in)

If activated (operator symlinks from `~/.jstack/hooks/` to `~/.claude/hooks/`), the watchers print soft warnings when:

- Token count hits 50k (warn) or 80k (escalate)
- Tool-call count hits 80 (warn) or 130 (escalate)

The watchers do NOT auto-compact — Claude can't compact its own conversation. They surface the right move (`/context-save` + restart in a fresh session) before bloat hits productivity.

Configure thresholds in `~/.jstack/config.yaml`.

---

## Per-CLI capability matrix

JStack ships with honest degradation. Not every skill works on every CLI.

- **Claude Code:** full support — skills + agents + hooks + slash commands.
- **GitHub Copilot Enterprise (with Opus picker):** degraded — `.github/copilot-instructions.md` reads canonical instructions; no skill mechanism, no subagent delegation. Skills that depend on these degrade to "operator-runs-manually."
- **Codex CLI:** degraded — `AGENTS.md` reads canonical instructions; no first-class skills; subagents sequentialize.
- **Other CLIs:** capability TBD per CLI. Run `verify.sh --cli-matrix` for the up-to-date table.

Every skill / agent in JStack declares `cli_support` in YAML frontmatter. `verify.sh --cli-matrix` prints the table.

---

## Auto-mode bounds (always apply)

OK without prompt: file edits, feature-branch commits/pushes, local tests/builds/lints, subagent invocations.

Requires explicit per-call authorization: production mutations, secrets, role/policy changes, DDL against live DB, container push to live registry, deploy triggers, `git push` to `main`.

Borderline (ask first): production audit events, production data access even read-only, branch builds wired to live deploys.

When in doubt: ask. Asking has small cost. Acting outside authorization has large cost.

---

## Cleanup pattern when a boundary has been crossed

1. Stop immediately. Do not push through.
2. Verify state with read-only checks.
3. Report honestly — what was done, current state, risks.
4. Propose options with trade-offs.
5. Wait for explicit authorization.

---

## When this file conflicts with a more specific source

Precedence order:

1. **Per-repo `CLAUDE.md`** — wins for that repo
2. **This file (`AGENT-INSTRUCTIONS.md`)** — cross-CLI canonical pointer
3. **CLI shim under `shims/`** — CLI-specific tips, never overrides core
4. **User-global `~/.claude/CLAUDE.md`** — fallback when no repo rule

If two sources conflict: surface to operator before acting. Do not silently choose.

---

## End of session

A clean end:

- `tasks/todo.md` has a Review section or is cleared for the next task.
- Any new lessons in `tasks/lessons.md`.
- Any new memory in `tasks/memory.md`.
- Any new ADRs in `docs/adr/`.
- Commits are atomic, no WIP debris.

If session ended mid-task: `tasks/todo.md` makes the next session able to pick up cold.
