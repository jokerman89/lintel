---
name: scaffold
layer: foundation
description: Use when setting up a new or existing repo to work with Lintel to install the base templates interactively — the repo instruction file, the lessons store, the evolution log, and the decisions directory. Reach for it to bootstrap the per-repo scaffolding the disciplines depend on.
color: cyan
tools: Read, Bash, Edit, Write, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the li-scaffold skill.

## What this skill does

Sets up a new repo (or initializes scaffolding in existing repo) with Lintel's Category B templates: CLAUDE.md (from template + repo-specific variables), CORE-PRINCIPLES.md, EVOLUTION.md, EVOLUTION-LOG.md, .claude/memory/{lessons,working-state,personas}.md, .claude/plans/todo.md, .claude/decisions/{README,TEMPLATE}.md, TEMPLATE-skill.md. (Subagents come from the plugin fleet — no repo-local `.claude/agents/`.)

This is how new repos get Lintel defaults inside 30 seconds.

## When to use

- Brand-new repo, no CLAUDE.md yet
- Existing repo joining Lintel standards
- Per-engagement template initialization

## When NOT to use

- Repo already has CLAUDE.md (warn before overwrite)
- Scratch / throwaway repo (outside scope; recommend lighter setup)

## Workflow

1. **Verify target.** Current cwd = target repo? Confirm via AskUserQuestion.

2. **Check for collisions.** Files that would be created or overwritten:
   - `CLAUDE.md` — overwrite or merge?
   - `.claude/memory/` — exists with content?
   - `.claude/decisions/` — exists?
   Recommend backup if collisions.

3. **Locate Lintel scaffolding source.**
   - Primary: `~/.lintel/scaffolding/01-foundation/`
   - Fallback: clone or fetch from `jokerman89/lintel`

4. **Gather repo-specific variables (AskUserQuestion):**
   - Repo name
   - Team / owner
   - Engagement type (customer-engagement / internal-tool / mvp / research)
   - Default voice tier (resolved from the active pack — `internal` by default)
   - Compliance level (resolved from the active pack — `advisory` by default)
   - GitHub URL (if known)

5. **Render CLAUDE.md from template.** Substitute variables. Result: project-specific CLAUDE.md.

6. **Copy other scaffolding files.**
   ```bash
   cp scaffolding/01-foundation/CORE-PRINCIPLES.md .
   cp scaffolding/01-foundation/EVOLUTION.md .
   cp scaffolding/01-foundation/EVOLUTION-LOG.md .
   mkdir -p .claude/memory .claude/plans .claude/decisions docs/personas
   cp scaffolding/01-foundation/.claude/memory/* .claude/memory/
   cp scaffolding/01-foundation/.claude/plans/* .claude/plans/
   cp scaffolding/01-foundation/.claude/decisions/* .claude/decisions/
   cp scaffolding/01-foundation/docs/personas/* docs/personas/
   # No .claude/agents/ — the subagent fleet ships with the plugin; a repo-local agent
   # would shadow the fleet's same-named one (removed 2026-06-14, ADR-0015 subtraction).
   cp scaffolding/01-foundation/.claude/SUBAGENT-GUIDE.md .claude/
   cp scaffolding/01-foundation/TEMPLATE-skill.md .
   cp scaffolding/01-foundation/TEMPLATE-agent.md .
   ```

7. **Initial commit (interactive — confirm with operator):**
   ```bash
   git add CLAUDE.md CORE-PRINCIPLES.md EVOLUTION.md EVOLUTION-LOG.md docs/ .claude/ TEMPLATE-*.md
   git commit -m "chore: scaffold Lintel base via li-scaffold"
   ```

8. **Add compliance template (optional).** If the active pack ships compliance scaffolding (`resolve_pack_field compliance.hooks` non-empty), apply the pack's compliance templates too. The `_default` pack ships none.

9. **Report.** Files created + next steps.

## Output format

```
JSTACK-SCAFFOLD: <repo name>

Variables collected:
- Repo: <name>
- Team: <team>
- Engagement type: <type>
- Voice tier default: <tier>
- Compliance level: <level>

Files created:
- ✓ CLAUDE.md (rendered from template)
- ✓ CORE-PRINCIPLES.md
- ✓ EVOLUTION.md, EVOLUTION-LOG.md
- ✓ .claude/memory/{lessons,working-state,personas}.md
- ✓ .claude/plans/todo.md
- ✓ .claude/decisions/{README,TEMPLATE}.md
- ✓ docs/personas/EXAMPLE.md
- ✓ .claude/SUBAGENT-GUIDE.md (subagents come from the plugin fleet — no repo-local agents)
- ✓ TEMPLATE-skill.md, TEMPLATE-agent.md

If the active pack ships compliance scaffolding:
- ✓ pack-provided compliance docs (none in _default)

Commit: <SHA>

Next steps:
- [ ] Review CLAUDE.md, adjust project-specific sections
- [ ] Customize .claude/memory/personas.md with engagement-specific personas
- [ ] Install Lintel plugin for your CLI: see docs/per-cli/
- [ ] First /qa to verify setup
```

## Edge cases

- **Existing CLAUDE.md** — backup first, merge interactively, OR offer dry-run preview.
- **No Lintel scaffolding source available** — recommend `git clone jokerman89/lintel ~/.lintel`.
- **Non-git directory** — recommend `git init` first.
- **Customer wants to fork Lintel** — see `docs/compliance.md` for what they'd need to change.

## Why this matters

Without this skill, every new repo starts CLAUDE.md from scratch. With it, every new repo starts with proven defaults. 30-second setup vs 30-minute setup.

This is Category B (Repo-scaffolding) in action — the templates Lintel curates get applied to make every new project consistent.
