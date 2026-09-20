# Agent report: BC4

<!-- lintel-swarm-evidence:v1
{
  "schema_version": 1,
  "artifact_kind": "swarm-report",
  "initiative": "swarming-work",
  "task_id": "BC4",
  "status": "complete",
  "worker": "DevOpsToolchain-swarm-bc4",
  "changed_paths": [
    "scaffolding/01-foundation/SESSION-PROTOCOL.md",
    "scaffolding/01-foundation/.claude/SUBAGENT-GUIDE.md",
    ".claude/SUBAGENT-GUIDE.md",
    "bin/li-scaffold",
    "bin/li-copilot.py",
    "tests/integration/copilot-kit.py",
    ".claude/plans/swarming-work/swarm/reports/BC4.md"
  ],
  "checks": [
    {"name": "six focused Copilot resource/scaffold tests after coordinator protocol sync in an isolated temporary copy", "status": "PASS"},
    {"name": "tests/unit/session-protocol-sync.sh", "status": "PASS"},
    {"name": "negative removal test for every mandatory swarm dependency", "status": "PASS"},
    {"name": "li-swarm.py check-scope --task BC4", "status": "PASS"},
    {"name": "repository and scaffold subagent-guide byte comparison", "status": "PASS"},
    {"name": "git diff --check", "status": "PASS"}
  ],
  "limitations": [
    "The four synchronized protocol consumers are coordinator-owned and intentionally remain drifted in this lane.",
    "Generated repository Copilot wrappers and managed outputs are coordinator-owned and were not changed.",
    "No authenticated Copilot client, tenant policy, hosted agent, push, deployment, or production behavior was exercised.",
    "The integrated full suite and final independent review remain coordinator-owned BC6 checks."
  ]
}
-->

## Changed files

- `scaffolding/01-foundation/SESSION-PROTOCOL.md` — added the opt-in swarm contract: one
  coordinator, single-writer reducers, attributable writer isolation, sequential/no-subagent
  fallback, recovery from committed evidence, and final integrated review.
- `.claude/SUBAGENT-GUIDE.md` and
  `scaffolding/01-foundation/.claude/SUBAGENT-GUIDE.md` — corrected discovery from the installed
  `agents/` fleet, documented optional local shadowing, separated implementer/reviewer ownership,
  and added repo-local swarm seed and recovery guidance. The two files are byte-identical.
- `bin/li-scaffold` — resolves canonical scaffold inputs from an adapter-supplied trusted
  `LINTEL_SOURCE_ROOT`, with executable-relative discovery only as the standalone fallback. It no
  longer mistakes Copilot's repo-runtime `LINTEL_HOME` for installed source. It validates all five
  templates before writes, installs them as user-owned seeds under `.claude/templates/swarm/`,
  lists the output, and creates no `.claude/agents/`.
- `bin/li-copilot.py` — added the native `li-swarm` workflow, included the public swarm guide when
  present, declared all 21 direct workflow, validation, handoff, policy, audit/path and template
  dependencies, and fails generation when any member is absent. The copied
  `lib/copilot-env.sh` derives `LINTEL_SOURCE_ROOT` from its installed bundle path rather than the
  working repository.
- `tests/integration/copilot-kit.py` — asserts the generated wrapper, every inventory/resource
  member, fail-closed behavior when each mandatory dependency is removed, installed trusted source
  root, bundled helper/schema/template presence, all five legacy-scaffold seeds, and successful
  bundled scaffolding after `copilot-env.sh` has set runtime `LINTEL_HOME`.

## Checks

- `C:\Progra~1\Git\bin\bash.exe C:\Users\jokerman\AppData\Local\Temp\lintel-bc4-python-tests.sh
  tests\integration\copilot-kit.py` with the six focused resource/source-root/scaffold test names,
  in an isolated copied tree after `python bin/li-instructions.py sync --root .` — PASS, 6/6 in
  35.722 seconds. This includes removal of each `SWARM_RESOURCES` member in turn with no target
  writes, bundled `copilot-env.sh` → bundled `li-scaffold`, executable-relative fallback, trusted
  source-root checks, exact inventory, and the legacy scaffold contract.
- `C:\Progra~1\Git\bin\bash.exe C:\Users\jokerman\AppData\Local\Temp\lintel-bc4-bash-tests.sh tests\unit\session-protocol-sync.sh`
  — PASS; source synchronization preserves project prose, detects drift, rejects malformed
  markers, and needs no personal home.
- Bundled Python `bin/li-swarm.py check-scope --repo . --coord
  .claude/plans/swarming-work/swarm/coordination.json --task BC4` over the six implementation paths
  — PASS with `diagnostics: []`.
- `fc /b .claude\SUBAGENT-GUIDE.md
  scaffolding\01-foundation\.claude\SUBAGENT-GUIDE.md` — PASS, no differences.
- `git diff --check` — PASS.

## Findings

- The existing repository and scaffold guides claimed the installed agent fleet lived in
  `.claude/agents/`, while the factory deliberately avoids creating that directory because a local
  definition can shadow the plugin fleet. Both sources now distinguish installed discovery from an
  intentional repository override.
- Copying whole `bin`, `lib`, `skills`, and foundation components already made swarm resources
  transitively available to portable Copilot kits, but no contract proved the set was complete.
  `SWARM_RESOURCES` now covers the swarm/work-map CLIs, schema/parser, CLI-tier declaration, Brief
  Forge skill and helpers, envelope and pack contracts, neutral fallback pack, direct audit/path
  dependencies, environment adapter, and all five templates. A negative test removes each of those
  21 files in turn and proves generation refuses before target writes.
- Copilot's environment helper deliberately sets `LINTEL_HOME` to repository runtime storage.
  Treating that variable as the scaffold source made the installed bundled scaffold unusable after
  correct environment initialization. `li-scaffold` now consumes trusted `LINTEL_SOURCE_ROOT` and
  reserves executable-relative source discovery for standalone use.
- The host's direct non-login Git Bash starts without `/usr/bin`, so the first run could not find
  `dirname`. The recorded green checks use small temporary wrappers that set the host PATH and the
  bundled Python interpreter; no host-specific workaround was added to repository code.

## Limitations

- `python bin/li-instructions.py check` correctly reports drift for `AGENTS.md`, `CLAUDE.md`,
  `scaffolding/01-foundation/AGENTS.md.template`, and
  `scaffolding/01-foundation/CLAUDE.md.template`. Editing those files here would violate the
  coordinator-only reducer boundary.
- The full Copilot suite was therefore proven in a temporary copied tree after the real
  synchronizer updated those four consumers. The coordinator must repeat it on the integrated tree.
- Generator tests prove deterministic files and links, not real Copilot discovery, model behavior,
  cloud execution, enterprise controls, or independent human approval.

## Coordinator reducer steps

1. Integrate the six owned source/test paths plus this report; the worker made no commit.
2. After BC4 fan-in, run bundled Python `bin/li-instructions.py sync`, inspect the four generated
   entry diffs, then require `bin/li-instructions.py check` to pass.
3. After BC5 documentation fan-in, run bundled Python `bin/li-copilot.py init --target . --source
   .` so the root `li-swarm` wrapper and all other managed Copilot outputs are regenerated from the
   final canonical sources; inspect the generated diff and run `check`.
4. Run `tests/unit/session-protocol-sync.sh`, `tests/shape/session-protocol-parity.sh`, and
   `tests/integration/copilot-kit.py` on the reconciled branch with the host's explicit Git Bash
   PATH/Python setup.
5. Verify a fresh temporary consumer contains `.claude/templates/swarm/`, a native
   `.github/skills/li-swarm/SKILL.md`, every `SWARM_RESOURCES` inventory entry, and a bundled
   `lib/copilot-env.sh` whose installed path becomes `LINTEL_SOURCE_ROOT`.
6. Keep catalog/wiki generation, manifest/version changes, plan/runtime ledgers, commits, and final
   integrated review coordinator-owned.
