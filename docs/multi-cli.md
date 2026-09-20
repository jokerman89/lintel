# Universal client support

Lintel keeps one shared workflow in `skills/`, specialist roles in `agents/`, and reusable
helpers/templates in `lib/` and `scaffolding/`. Thin adapters expose documented native
discovery formats or a useful explicit file handoff. Universal means continuity of intent,
work, policy and evidence, not identical client tools or blanket support.

## Three separate facts

`lib/cli-tiers.yaml` is the canonical schema-version-2 registry. It uses JSON-compatible YAML
so the same standard-library reader serves the installer, shell compatibility API, onboarding
and generated [README view](../README.md#multi-cli-support).

| Layer | What it establishes | What it does not establish |
|---|---|---|
| Vendor | Dated official URL, version scope and documented/conditional/unsupported operation | Availability, permission or execution in your session |
| Delivered | Generated native-format path or explicit manual/operation-contract binding | That a host discovered it, ran it or honored the instructions |
| Observed | Scenario, host version, Lintel revision, date, evidence and limitations | Parity with another surface/version or an unrun scenario |

Unknown vendor capability remains `unknown`. Unrun observation remains `not_run`. Partial
session observations cannot become complete client acceptance. CLI, desktop, IDE and cloud
are separate records, including Copilot, Codex, Cursor, OpenCode, Factory and newer clients.
Use the [adapter guide](client-adapters.md) and registry output rather than another support matrix.

```bash
python3 bin/li-client-capabilities.py show --client copilot-app
python3 bin/li-client-capabilities.py validate
```

## One instruction source and one installer engine

The full `scaffolding/01-foundation/SESSION-PROTOCOL.md` is synchronized into marked blocks
in AGENTS.md, CLAUDE.md and both foundation templates (ADR-0025). Short client pointers
lead to that authority; personal global instructions are not required. Project prose outside
managed blocks remains project-owned.

`bin/li-adapter.py` is a small entry into `bin/li-copilot.py`, not another installer. It
reuses the same scoped source bundling, safe paths, ownership inventory, conflict refusal,
foundation seeding and integrity checks. A mixed-client repository gets one `.github/lintel/`
source bundle and each selected native root; manual-only clients get `START.md` and canonical
files, without invented discovery paths. Updates retain the installed surface set.

No hooks, clients, settings, credentials, permissions or user-global files are installed.
The source product manifest is retained for product constraints, not fabricated from a
version label in prose. `check` validates local files, not live models or enterprise controls.

## Bind semantic operations to the actual host

The [Universal contract](../shims/universal/ADAPTER.md) covers questions, planning,
instructions/skills, read/edit/shell/browser, delegation/isolation, memory/resume, hooks
and plugin/model controls. Populate a session declaration only from inspected tool schemas
and permissions. It carries the actual stable session ID, exact surface, version if known,
selected work map, unchanged effective profile reference and isolation evidence.

`li-client-capabilities.py resolve --session <file>` selects routes; it never calls tools.
It returns `executed: false` and `evidence_level: declared-session-bindings`. The runtime
host still owns execution and permission. No fixed tool name, model ID or vendor table is
required to ask a question or perform a review.

| Missing capability | Retained useful behavior |
|---|---|
| Native skill discovery | Explicitly read the selected canonical file through `START.md` |
| Question tool | Conversation, only if the host has no question channel |
| Safe attributable parallel writes | Serial execution of the same approved briefs |
| Delegation | Bounded manual/external handoff, reports, status and restart |
| Independent reviewer | Keep the review requirement open for a real separate actor |
| Browser | Keep the browser evidence task open; search is not browser automation |
| Hook/plugin/model API | Explicit unsupported result, not marker files or fictional settings |

Denied permission blocks; pending/unknown permission requires resolution, not a fallback
around the host. A worktree is change isolation, not a security sandbox. The effective
profile reader and shared review evidence implementation remain authoritative in their domains.

## Preserved client routes

### GitHub Copilot

The native `.github/skills` and `.github/agents` kit and `.github/plugin/` manifest remain.
CLI, App, VS Code and cloud have individual records. Use the [Copilot guide](copilot.md).
Lintel does not translate Claude hooks into Copilot's distinct hook API.

### Claude Code

The `.claude-plugin/` route, canonical skills, agents and optional hooks remain. The
repository-only `.claude/skills/li-*` route is additive and deliberately hook-free.
Desktop Code local is separate from CLI, Chat, Cowork and cloud. See [Claude Code](claude-code.md).

### Other clients

Codex and Cursor manifests, the Gemini extension and OpenCode manual guide are retained.
The [client adapter guide](client-adapters.md) identifies native-format and manual routes for
those clients and Antigravity, Kiro, Devin/Cascade, Junie, Factory, Cline, Continue and Aider.
Do not use a retired install incantation or a neighboring surface's settings API without
checking the intended host's current documentation and available commands.

## Swarm compatibility

All modes preserve the original work map, dependencies, ownership, package/leaf acceptance
and evidence. `resolve` selects `native-isolated` only when delegation and isolation bindings
are available/permitted and the session supplies attributable isolation evidence. Otherwise
use `serial`, or `manual-handoff` when delegation is absent. Review remains outstanding;
selection is not proof of actor independence.

The old `cli_tier_*` functions remain a conservative reader over the same registry.
`subagents=sequenced` means a source-backed delegation feature still needs live binding;
`none` means use the manual path. No static row authorizes concurrent writers. An unknown
legacy ID warns and degrades to manual; explicit installer requests reject unknown IDs.
The [swarm guide](concepts/swarming-work.md) retains the complete artifact and recovery method.

<a id="adding-a-new-cli"></a>

## Adding or verifying a surface

Add a distinct record with official sources, version conditions and a documented discovery
root, or keep an explicit manual route. The shared validator and generator must consume it;
add behavioral selection and consumer installation cases. Regenerate shared outputs through
their owner. Then run a real client pilot with exact version/revision, discovery, permitted
plan/build/review and cold resume. Do not mark source research or fixture tests as that pilot.
