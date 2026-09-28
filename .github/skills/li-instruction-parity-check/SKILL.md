---
name: li-instruction-parity-check
description: Use to verify shared session protocol equality and client-entry links without overwriting project prose or confusing similarity with authority.
---

> **Lintel on GitHub Copilot.** Generated from `skills/instruction-parity-check/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** paths relative to this skill's own folder (such as `<base>`,
>   `scripts/`, `references/`, `data/` or `${LINTEL_SKILLS_DIR:-skills}/…`) mean
>   `../../../skills/instruction-parity-check/` in the Lintel source, not this generated folder. `bin/li-run` exports
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

# Instruction parity

Read the accepted ADR-0025 contract: `scaffolding/01-foundation/SESSION-PROTOCOL.md`
is the complete shared source. Marked blocks in root AGENTS.md, CLAUDE.md and both
foundation templates must match it exactly. Short client pointers are intentionally
different; their job is to lead to that complete authority, not repeat six similar files.

This is a read-only verification workflow. Do not replace client-specific instructions
or project prose with a fuzzy similarity target.

## Procedure

1. Identify the working repository and trusted source bundle. Read the actual entry files,
   generated adapter inventory and their referenced source. Keep requirements, ownership,
   human approvals and host permission boundaries separate.
2. In the Lintel source checkout, run the existing checker from the repository root:

   ```bash
   python3 bin/li-instructions.py check
   ```

   Its exact block checks, malformed-marker failures and preservation tests implement
   synchronization. If it cannot run, report an unverified check; character counts or
   word-similarity scores are not substitutes.
3. In a consumer repository, run the installed generator's integrity check:

   ```bash
   python3 .github/lintel/bin/li-adapter.py check --target .
   ```

   The preserved `li-copilot.py check` entry works for Copilot installations. Check records
   of every selected surface; installed files do not prove the host discovered them.
4. Read the remaining short entry pointers and host-specific notes. Flag contradictions
   about authority, data handling, permissions, original work IDs, independent review,
   source/target paths or hook activation. Cite actual files and lines. Do not demand that
   a shim and the full protocol have identical text or claim this judgment ran in CI.
5. Report exact commands, results, mismatched blocks/links, project-owned prose preserved
   and live-host limitations. A missing source, malformed marker or failed command is not
   a clean result. Keep substantive independent review separate from this implementer's
   self-check.

## Repairs and ownership

Propose repairs at the canonical source. Synchronization uses `li-instructions.py sync`,
then adapter regeneration and checks, only when the owner authorizes those writes.
In coordinated work, the coordinator owns shared generated outputs. Never manually patch
one generated protocol block or erase local managed-file edits to make `check` pass.

The actual tests are `tests/shape/session-protocol-parity.sh` and the consumer adapter
integration tests. A future CI workflow or doctor subcommand is not assumed to exist.
No missing or unreadable entry should silently lower the check to a successful partial pass.
