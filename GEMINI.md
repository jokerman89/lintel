# Gemini CLI session entry for Lintel repo

This file is read by Gemini CLI when working **on the Lintel repo itself**.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

Lintel is a company-neutral, pack-driven session harness — markdown scaffolding for agent-based development. Company identity loads from a separate, installable pack.

- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/architecture.md` — the architecture reference (decisions: `.claude/decisions/`)

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `.claude/memory/lessons.md` for accumulated lessons
3. Check [docs/architecture.md](docs/architecture.md) + recent ADRs in `.claude/decisions/` for current architecture state

## Gemini-specific notes

### Extension install

This repo is a Gemini extension (see `gemini-extension.json`). Install via:

```bash
gemini extensions install https://github.com/jokerman89/lintel
```

Update via (the extension is named `li`):

```bash
gemini extensions update li
```

### Skill discovery on Gemini

The existing extension/context-file route is retained. Current Gemini CLI documentation also
defines workspace skills under `.gemini/skills` (and `.agents/skills`). The repository adapter
can generate `li-*` wrappers there without changing personal settings or installing a client.
Inspect actual discovery and activation consent; documentation is not a live session test.

To invoke a skill on Gemini, reference the file path:

```
Follow instructions from skills/ship/SKILL.md and execute on the current branch.
```

### Available skill catalog

Common skills (see `skills/` for full list):
- `/li:verify` — run checks without repairs by default; repair requires explicit authorization
- `/li:cycle` — 9-step work cycle (sense→capture)
- `/li:ship` — pre-flight checks + PR creation
- `/li:diagnose` — scoped bug investigation and owned recovery
- `/li:code-freeze` with `--lift <path>`, `--lift --all` or `--list` — advisory freeze controls
- `/li:inspect --target plan|repo --lens engineering|design|devex` — plan and repository inspection
- `/li:define` — task-relevant requirements and design; strategy is an explicit lens
- `/li:cross-check` — independent review through an actual permitted reviewer
- `/li:pause` / `/li:resume` — checkpoint and continue the selected work
- `/li:ta`, `/li:da`, `/li:sc`, `/li:dh`, `/li:tq` — engineering-domain modules
- `/li:compliance-gate` — runs the active pack's compliance gates
- `/li:generate-ppt`, `/li:generate-word`, `/li:generate-web` — doc generation
- `/li:scaffold`, `/li:scaffold-internal-tool`, `/li:scaffold-mvp` — repo scaffolds

### Subagents

Gemini documents subagents with surface/version restrictions, including no nested subagents.
Use actual available delegation tools rather than Claude tool names. Keep canonical role methods
as scoped inputs; missing delegation retains serial/manual handoff, not fictional independence.
Experimental worktrees or browser agents need their own availability and permission evidence.
See the Universal contract at `shims/universal/ADAPTER.md` and `lib/cli-tiers.yaml`.

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines: no customer data, no secrets in prompts, no prod mutations without auth. Tiered rules (identity policy, vendor preference, regulatory gates) come from the active pack.

### Voice corpus

Voice is supplied by the active pack (`resolve_pack_field voice.corpus`; none in `_default`). A company pack supplies its own calibrated corpus.
