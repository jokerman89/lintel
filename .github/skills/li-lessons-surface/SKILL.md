---
name: li-lessons-surface
description: Use before or during a task for keyword-ranked lessons, the complete index or an exact lesson ID, without changing the memory store.
---

> **Lintel on GitHub Copilot.** Generated from `skills/lessons-surface/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Lessons surface

Read the selected repository's lessons through `lib/memory.sh` and `bin/li-lessons.py`.
This combines task-oriented lookup with the short SENSE/PLAN/BUILD warm-up. It neither
writes lessons nor grants authority to override current requirements or accepted decisions.
Use `/li-lessons-add` to add, update or supersede a rule.

## Inputs

- `--keyword <text>`: top three matching active lessons. Keywords are literal text.
- `--all`: complete heading index, with superseded entries visibly marked.
- `--id <L-NNN>`: the exact full block, including its supersession markers.
- No flag: derive keywords from the selected repository's branch and recent commit
  subjects, then surface at most two lessons for the short cycle warm-up.
- `--legacy-operator`: an explicitly requested, authorized read-only view of the old
  operator JSONL store. Do not inspect personal stores during ordinary project lookup.

These are mutually exclusive modes. Keep existing `LESSONS_TOP_N` caller overrides for
keyword lookup; an all/index request is not silently reduced to the default top three.

## Read the selected store

Resolve the trusted source independently of the working target. Pass mode arguments as
an array to this block; never interpolate keywords or IDs into shell source.

```bash
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/lib/memory.sh"
case "${1:-}" in
  --keyword)
    [ "$#" -eq 2 ] && [ -n "$2" ] || { echo 'Supply one nonempty keyword value.' >&2; exit 2; }
    lessons_surface "$2" ;;
  --all)
    [ "$#" -eq 1 ] || { echo 'Use one lessons lookup mode.' >&2; exit 2; }
    lessons_index ;;
  --id)
    [ "$#" -eq 2 ] || { echo 'Supply one lesson ID.' >&2; exit 2; }
    lessons_helper get --id "$2" ;;
  --legacy-operator)
    [ "$#" -eq 1 ] || { echo 'Use one lessons lookup mode.' >&2; exit 2; }
    lessons_legacy_operator ;;
  "")
    repo="$(lintel_repo_root)" || exit 1
    [ -n "$repo" ] || { echo 'No project lessons store (unobserved).' >&2; exit 1; }
    branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null) || branch=""
    subjects=$(git -C "$repo" log -3 --format=%s 2>/dev/null) || subjects=""
    keywords="$(printf '%s\n%s' "$branch" "$subjects" | tr '/-\n' '   ')"
    LESSONS_TOP_N=2 lessons_surface "$keywords" ;;
  *) echo 'Unknown lessons lookup mode.' >&2; exit 2 ;;
esac
```

`lintel_lessons_file` owns store selection, including unmigrated `tasks/lessons.md`.
When both old and new stores exist, relay the helper's diagnostic naming the store read
and the ignored one. Absence is **unobserved**, not an existing empty store or proof that
no lessons apply. Do not create a store during lookup.

The shared grammar recognizes `## L-<digits>` headings outside fenced code and reports
malformed headings, duplicate IDs, missing supersession targets and dated legacy blocks.
Relay stderr diagnostics. Keyword ranking skips superseded entries; index and ID lookup
retain them. Do not add a competing parser, invented relevance score or recency bonus.
`lessons_find_related <keywords>` provides the uncapped matching index for a requested
deeper review or the CAPTURE update phase.

## Read and apply the full lesson

For each selected ID, use `lessons_helper get --id <L-NNN>` to read the complete block.
Exit 1 means absent; exit 2 means duplicated or malformed. With no supported Python,
full-block retrieval is unavailable; the shell ranking/index/count readers still work.
Do not call a ranked heading a full lesson or silently guess its body.

Show the original rule, its source/date when present, and one sentence explaining its
relevance to the current task. Default to at most three full blocks; paginate a larger
explicit review. A conflicting or outdated lesson is a finding to reconcile, not a
reason to erase history. Supersede it through `/li-lessons-add` when authorized.

## Optional cross-repository history

The legacy operator view is labelled **not ID-managed** and is never imported or written.
If the operator has separately opted into lesson synchronization, read only the explicitly
authorized synced files. Neither a lookup request nor a missing project store activates a
global sink, private synchronization or promotion. `/li-lessons-promote` keeps its own
explicit destination and authority.

## Result

Report the selected store, actual mode, lesson IDs, relevant full blocks and diagnostics.
No matches in an existing readable store is a valid empty result. Missing/unreadable
sources and invalid arguments remain visible as incomplete/blocked lookup, never a
healthy empty result. An advisory SENSE warm-up may continue with that limitation recorded.

Examples:

```text
/li-lessons-surface --keyword "checkpoint ownership"
/li-lessons-surface --id L-037
/li-lessons-surface --all
```

This is read-only awareness. Authoring, enforcement, promotion and host memory remain
separate operations.
