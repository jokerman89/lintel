# ADR-0020: a tools-only lintel-state MCP server for portable memory access

> Renumbered 0016 → 0020 (2026-06-14): 0016 collided with the anthropic-default design ADR
> created earlier (first claimant keeps the number); 0018 reserved for extension-pack-contract.

**Status:** Accepted-direction, build staged (2026-06-13)
**Implements:** docs/audit/2026-06-13-cli-issues-craft-synthesis.md (workstream 1)

## Context

Lintel has zero MCP story. Its state/lessons/jobs map is file-based (great — beads' incidents
validate keeping it dumb + git-native). But access is grep-only, which works only on CLIs that
grep. A tools-only MCP server reaches ~10 MCP clients with ONE artifact — more portable reach
than 6 manifests. Tools are universal (100% of MCP clients); resources are not (~39%, and Codex
drops them), so the server must expose TOOLS, not resources.

## Decision

Build a small stdio MCP server exposing `state_read` / `state_append` / `state_list`
(jobs, lessons, working-state, ADRs) as TOOLS over the existing file layout (lib/state.sh,
lib/memory.sh, bin/_jobs.sh are the implementations). Answer `resources/list` empty to dodge the
Codex availability bug. It does NOT replace skills/hooks — it gives portable read/write to the
memory map across every MCP CLI.

## Consequences (when built)

- Portable state across Claude Code, Codex, Cursor, Gemini, Copilot, Droid, opencode, Cline,
  Continue, Windsurf, Zed — config mechanism differs per CLI but the server + schema is one.
- Staged: small build (an afternoon), but it's net-new surface that deserves its own cycle + the
  eval to confirm it earns its keep.
