---
slug: setup-hardening
date: 2026-06-14
cycle_id: setup-hardening
operator: jokerman
affected_paths:
  - lib/cycle-footer.sh
  - hooks/hooks.json (+ Stop event)
  - hooks/shared/cycle-incomplete-warn/ (NEW)
  - hooks/shared/session-digest/run.sh
  - skills/cycle/SKILL.md
  - .claude/agents/ (REMOVED — 4 files)
  - scaffolding/01-foundation/.claude/agents/ (REMOVED — 4 files)
  - CLAUDE.md · scaffolding/01-foundation/CLAUDE.md.template · install/verify.sh · skills/scaffold/SKILL.md · bin/li-scaffold
  - .claude/decisions/{0019,0020,0021}-*.md (RENAMED from 0015/0016/0017)
  - tests/unit/cycle-continuity.sh (NEW) · tests/shape/adr-numbers-unique.sh (NEW)
risk_class: medium
breaking_change: false
---

# Structure change: setup-hardening

> Gate M1 (structure-impact analysis) artifact for ADR-0022.

## What changed (shape)

1. **NEW hook event `Stop`** registered in `hooks.json` → `cycle-incomplete-warn` (warn-only). First
   Stop hook in the fleet. NEW hook dir `hooks/shared/cycle-incomplete-warn/{run.sh,HOOK.md}`.
2. `session-digest` gains a `Current cycle:` line (reads `state_cycle_segment`).
3. `lib/cycle-footer.sh` auto/full tier gains a "cycle starting" branch (behavior fix, same entry point).
4. **REMOVED** `.claude/agents/` (repo, 4 files) + `scaffolding/01-foundation/.claude/agents/`
   (template, 4 files). The subagent fleet now comes solely from the plugin manifest.
5. ADR files `0015-agents-md-primary`, `0016-lintel-state-mcp`, `0017-eval-harness` **RENAMED** to
   `0019/0020/0021` (collision resolution).

## Backward-compat

- All existing cycle invocations work unchanged — the footer fix + Stop hook + digest line are
  additive; the footer's hard behavior for active/complete/no-cycle states is identical (10
  assertions lock it).
- Skill agent dispatch by bare name (`CodeReviewer`, `TestRunner`, …) still resolves — to the
  *richer* plugin-fleet version now that the shadowing repo copies are gone.
- Scaffolding a new repo no longer creates `.claude/agents/`; `verify.sh` no longer asserts the
  template agents. No consumer action required.
- The Stop hook is Claude-Code-only; other CLIs keep the prose footer convention (documented).

## Migration path

No migration needed — additive + internal. Downstream repos that had previously scaffolded the 4
template agents may delete their local copies (optional; they would shadow the fleet) — surfaced
here, not enforced.

## Forward-compat

Enables: mechanical continuity guarantees that survive long work + resume (the substrate is now a
registered Stop hook + a state-aware digest, not prose). Forecloses: nothing — removing the hook +
reverting 5 doc edits returns to prose-only.

## Verification

- M2 compat audit: `bin/li-compat-audit` (expected GREEN — additive; one new hook, no frontmatter/
  helper-signature change).
- M3 shape suite: `tests/runner/run-all.sh` green on the committed tree, incl. the 2 new tests
  (`cycle-continuity`, `adr-numbers-unique`).
- The ADR-collision is now guarded: `adr-numbers-unique.sh` fails CI on the next duplicate.

## Rollback procedure

`git revert` the setup-hardening commit range on `feat/setup-hardening`. The repo agents can be
restored from history if a project-specific override is later wanted (precedence still supports it).
The global `~/.claude/CLAUDE.md` edits are outside this repo (operator's personal file) — revert
manually if desired.
