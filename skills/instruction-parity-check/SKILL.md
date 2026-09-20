---
name: instruction-parity-check
layer: foundation
description: Use to verify shared session protocol equality and client-entry links without overwriting project prose or confusing similarity with authority.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex, copilot, cursor, gemini, opencode, droid]
---

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
