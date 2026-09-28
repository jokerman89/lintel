---
name: li-fix
description: Use for a known bug with a clear fix path that needs to ship now — runs the abbreviated SENSE, BUILD, REVIEW, SHIP path and skips design, discovery, and planning. The hotfix shortcut; reach for it when the diagnosis is already done and only the fix remains.
---

> **Lintel on GitHub Copilot.** Generated from `skills/fix/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** paths relative to this skill's own folder (such as `<base>`,
>   `scripts/`, `references/`, `data/` or `${LINTEL_SKILLS_DIR:-skills}/…`) mean
>   `../../../skills/fix/` in the Lintel source, not this generated folder. `bin/li-run` exports
>   `LINTEL_SKILLS_DIR` for shell steps.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the FIX composite shortcut — hotfix mode pre-baked. Not nestable — /li-fix is itself the hop-in shortcut.

## When to use

- Known bug + path to fix is clear
- No design discussion needed (e.g., "null pointer at line 47, add null check")
- Production incident requiring fast ship
- Operator already understands root cause
- Cost expectation: ~5-15k tokens, 10-30 min

## When NOT to use

- New feature work — use `/li-cycle` (full)
- Unclear root cause — use `/li-diagnose` first, then `/li-fix`
- Customer-deliverable involved — use `/li-cycle --mode customer-engagement` (the active pack's voice + compliance gates apply)
- Significant architecture change — needs DEFINE + PLAN phases

## Workflow

### Step 1 — Pre-flight

Confirm hotfix mode is appropriate:
- Reuse the supplied diagnosis and authority. Ask through the actual host channel
  only if the root cause, intended behavior or mutation scope is unresolved.
- If the diagnosis is missing, use `/li-diagnose`; do not improvise a fix from
  a review/research request.

Keep BUILD's work contract even though the full PLAN ceremony is skipped. Use the
[selected work map](../../../skills/spec-kit/references/work-map.md) and `bin/li-work-artifacts.py`.
An existing defect task keeps its original ID. For a new bounded authorized fix,
record a minimal native spec/plan/prompt/work.json with the reproduction, intended
behavior, owned files, one stable leaf, regression check and existing scope approval.
The map's tasks points to that plan; no extra backlog or unrelated interview.
If required planning/review is missing, the alias remains incomplete.

### Step 2 — Delegate to /li-cycle

```bash
/li-cycle --mode hotfix --from SENSE --to SHIP --skip DEFINE,DISCOVER,PLAN,CAPTURE
```

Mode preset handles:
- audience=solo
- voice_tier=internal
- compliance=minimal (HARD-RULES still enforced per the pack's compliance mode; default advisory)
- Same verified P07 profile/required-policy reference and original task selection
- Cost expectation pre-set low

### Step 3 — Post-fix

After SHIP DONE, surface:
```
HOTFIX SHIPPED — <commit/PR>

Skipped phases:
  - DEFINE (no design needed for known fix)
  - DISCOVER (no codebase mapping needed)
  - Full PLAN ceremony (minimal approved mapped work and acceptance were retained)
  - CAPTURE (no durable artifacts to capture)

If this fix reveals a pattern worth capturing (lesson for /li-lessons-promote),
run /li-capture manually now.
```

This is a soft prompt — operator decides if CAPTURE is worth running post-hoc.

## Integration

Delegates to `/li-cycle --mode hotfix`. No new behavior beyond that.

## Anti-patterns

- **Using /li-fix for new feature work** — bypass DEFINE/PLAN = guaranteed scope drift
- **Skipping CAPTURE when fix reveals durable lesson** — soft-prompted post-hoc, don't ignore
