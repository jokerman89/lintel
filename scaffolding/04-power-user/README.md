# Layer 4 — Power user

Experimental patterns the team is actively learning together. NOT "advanced topics, ignore for now." This is the live edge.

## What lives here

(Pending Phase 5 — currently placeholder. Files below land during Phase 5 implementation.)

- **`memory-protocols.md`** — cross-session `memory.md` structure + sub-sections (operator profile, project context, feedback patterns, external references).
- **`workflow-templates/`** — per-project-type scaffolding starters. v1 ships 3 of 5: `customer-demo.md`, `internal-tool.md`, `wiki-content.md`. (`frontend-mvp.md` + `backend-mcp.md` deferred to v1.1.)
- **`compliance-hooks/`** — 4 opt-in scripts (`secret-scan.sh`, `data-classification.sh`, `ms-policy-refresh.sh`, `repo-clean-state.sh`). Files land here. Activation = operator manually symlinks from `~/.jstack/hooks/` to `~/.claude/hooks/`.
- **`multi-repo-workspace.md`** — parent-CLAUDE.md + symlinked memory pattern for working across related repos.
- **`skill-activation-rules.md`** — per-harness-context activation policy (which skills fire in which repo types).
- **`mcp-orchestration.md`** (deferred to v1.1 per design Effort-vs-Scope cut) — per-repo MCP allowlist policy.
- **`lessons-tagging.md`** (deferred to v1.1) — category tag schema + quarterly synthesis ritual.
- **`deliverable-provenance.md`** (deferred to v1.1) — DELIVERABLE-PROVENANCE.md template + schema.

## Change rate

**Experimental — actively learning.** Files here are NOT load-bearing. Adapt freely. Promotion-to-Layer-3 path: if a Layer 4 pattern has proven value in 3+ contexts, promote it via PR.

## Hook activation philosophy (per Eng review session 2 A1)

Hook files install at `~/.jstack/hooks/jstack-X.sh` — **NOT** at `~/.claude/hooks/`. They are inert by default because Claude Code doesn't auto-load from `~/.jstack/hooks/`.

To activate a hook:

```bash
# Unix/Mac/WSL/Git-Bash
ln -sf ~/.jstack/hooks/jstack-secret-scan.sh ~/.claude/hooks/jstack-secret-scan.sh

# Windows PowerShell (DevMode or admin)
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\hooks\jstack-secret-scan.sh" -Target "$env:USERPROFILE\.jstack\hooks\jstack-secret-scan.sh"
```

Or use `scaffold-repo.sh --enable-hook jstack-secret-scan` (planned for v1.2).

This means: install != activate. Operator owns the call about which hooks fire.

## The "experimental" promise

Layer 4 patterns are documented + installed so the team learns together day 1 (per office-hours D3). They are NOT proven at scale. Expect:
- Some patterns will graduate to Layer 3 (promoted) when they prove out
- Some will be archived in `EVOLUTION-LOG.md` when they don't work
- The set you see today will evolve — that's by design
