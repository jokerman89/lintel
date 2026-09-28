---
phase: DISCOVER
ts: 2026-09-28
cycle_id: native-client-parity-20260928
work_map: .claude/plans/native-client-parity/work.json (DRAFT, created in PLAN)
profile: _default (verified by workflow_begin; compliance advisory, voice internal)
wedge_keywords: [li-copilot, native skills, custom agents, hooks adapter, plugin, cli_support]
files_mapped: 60
adrs_relevant: 10
lessons_applied: 12
deps_flagged: 0
agents_recommended: 4
skills_overlap: 0
---

# Discover report: native client parity, increment 1 (Copilot)

The detailed consumer map, with `path:line` evidence for every assertion, is committed at
[research/consumer-map.md](research/consumer-map.md). This report summarizes what binds PLAN.

## Codebase map (top 20)

- `bin/li-copilot.py`: the shared generator.
  - `generate()` 675-862: pointer skills at 747-765, agents at 766-779, instructions at
    780-802, other roots at 814-836, START at 837-856.
  - Managed inventory and check at 999-1160.
  - `COMPONENTS` (line 60) excludes `hooks`.
- `bin/li-adapter.py:15-21`: Universal entry point. It calls `main(universal=True)`, so every route
  changes.
- `bin/li-lifecycle.py:933-941`: `--copilot`/`--client` routing into `li-copilot.py`.
- `lib/cli-tiers.yaml`: surface facts.
- `lib/client_capabilities.py:50-108`: validator.
  - `hook_adapter.path` must be in `preserved` (85-88).
  - Observed records need a `host_version` and a 40-hex `lintel_revision` (93-108).
- `bin/li-catalog.py:48-72,176-190,248-286`: stdlib frontmatter reader and `cli_support` validation.
  Reuse its reader.
- `hooks/shared/_input.sh`: stdin field adapter. It needs Copilot `new_str`/`old_str`/`file_text` and
  camelCase `toolArgs`.
- `hooks/shared/*/run.sh`: nine auto-registered hooks.
  - Blocks use exit 2 with stderr; warnings print stdout.
  - `session-digest`, `cycle-incomplete-warn`, `memory-budget-warn` and `no-customer-data-in-message`
    print plain stdout.
  - `cycle-position-inject` prints Claude JSON context.
- `hooks/hooks.json`: the canonical registration list. Derive the Copilot registration from it.
- `.github/plugin/{plugin,hooks,marketplace}.json`: Copilot plugin files. Hooks are empty today, and
  every manifest is at 0.12.0.
- `.gitattributes:28-34`: LF rules for generated kit paths. Expand them to all agents and the hook
  files.
- `.github/workflows/ci.yml:144,150,153`: runs the catalog check, `li-copilot.py check --target .
  --source .` and `li-wiki-gen --check`.
- Tests that change:
  - `tests/integration/copilot-kit.py`
  - `tests/integration/universal-adapters.py`
  - `tests/integration/catalog-installed.py`
  - `tests/e2e/harness-critical-path.sh:115-127`
  - `tests/unit/cli-tiers.sh:20-47`
  - `tests/unit/copilot-capabilities.sh:17`
  - `tests/unit/native-command-surface.py:1281-1325`
  - `tests/unit/adapter-navigation.py`
  - `tests/shape/hooks-registration-safe.sh`
- Documentation that changes:
  - `shims/copilot/COPILOT.md:23-24,83-84,107-110`
  - `shims/universal/ADAPTER.md:34-37,76-82`
  - `docs/copilot.md`, `docs/client-adapters.md:33-42`, `docs/getting-started.md`
  - `docs/architecture.md:330-336`
  - `hooks/shared/README.md:3-10`
  - `.github/copilot-instructions.md`
  - generated wiki and catalog output (regenerate; do not hand-edit)

## ADRs (relevant)

- **ADR-0024** Copilot native adapter (Accepted). Superseded in part: pointer wrappers and "never
  import Claude hook JSON". The Copilot hooks are Copilot-format registrations, not imported Claude
  JSON.
- **ADR-0035** four client families (Accepted). Bounds this scope: Copilot, Claude, Codex, Cursor.
- **ADR-0008** activation contract (Accepted). Auto-registered hooks source only their own tree, never
  repository code. This applies to plugin hooks.
- **ADR-0013** fail-closed block gates (Accepted). Keep exit 2 semantics; the adapter maps them to
  JSON deny.
- **ADR-0022/0023** continuity hooks (Accepted). The Stop hook stays warn-only, and prompt context
  injection never blocks.
- **ADR-0028** Universal evidence (Accepted). Keep documented, delivered and observed facts separate.
- **ADR-0030/0031** installation without Python and native path spelling (Accepted). Keep generator
  path safety.
- **ADR-0032/0037** CI shards and tiering (Accepted). Hook and bin changes trigger the full
  three-OS matrix, and Windows must avoid System32 WSL Bash.
- **ADR-0034** native workflow consolidation (Accepted). No conflict.
- Conflict with the approach: only ADR-0024, handled by the new ADR-0038.

## Lessons applied

- L-016: hooks carry continuity, and the Stop hook is warn-only. Its note that there is no PreCompact
  hook is outdated for Claude (research) and for Copilot (`preCompact` exists); update it at CAPTURE.
- L-020: bump the version uniquely to 0.13.0.
- L-030: host-neutral identity.
- L-007: independent review of meta-infra diffs, and verify the reviewer.
- L-053: `jokerman89` only.
- L-054: no new packages (no `jq` requirement).
- L-055/L-060: no amend or reset.
- L-056: generated files inside delegated scopes (catalog, wiki, native kit).
- L-059: commit only on this branch.
- L-061: verify byte-bound checks with LF.
- New this session:
  - refresh with `merge --ff-only`, not `reset`;
  - capture only an explicit allowlist of environment names.

## Dependencies flagged

None. Stdlib Python, Bash, and PowerShell for the Windows launcher only. No package is added.

## Recommended agents for PLAN/BUILD dispatch

| Category | Agent | Why |
|---|---|---|
| engineering | `lintel-builder` (Copilot role) | package implementation with verification evidence |
| engineering | `lintel-reviewer` / `code-review` | independent Stage 1 and Stage 2 package review |
| security | `security-review` | hook adapter fail-open/deny paths and secret handling |
| engineering | `rubber-duck` | design and plan critique |

## Skills overlap

None. This extends the existing adapter generator rather than adding a workflow.

## Open questions for PLAN

- Registry model for a generated Copilot hook adapter whose path must appear in `preserved` (validator
  lines 85-88).
- Whether VS Code Local matches PascalCase hooks with Claude tool names. It is recorded as conditional
  or unverified.
- Codex skill-list budget (2% or 8,000 characters). Increment 2; it may need short descriptions.
