# Client adapters

Choose the exact surface, not just its vendor. Every listed route preserves canonical
planning, build, review and resume resources. Native-format wrappers are generated only
where the project discovery root is documented. Other routes are plainly manual.

## Install and inspect one surface

From a reviewed local checkout:

```bash
python3 bin/li-client-capabilities.py list
python3 bin/li-client-capabilities.py show --client <surface>
python3 bin/li-adapter.py init --client <surface> --target <project>
python3 bin/li-adapter.py check --target <project>
```

Use actual values for the placeholders. Repeat `--client` to select multiple surfaces in
one invocation. The existing inventory preserves previously selected clients. One managed
source bundle serves them all; shared roots produce identical wrappers rather than duplicate
copies of the method. No user-global installation, enablement, model or hook command exists
in this helper.

`show` returns official URLs checked on 2026-09-20 with version/conditions, the delivered route
and observed evidence per operation. These dates describe source checks, not client runs.
All live workflows remain unrun here except the explicitly limited Copilot App session
observations. Locally exercised installer fixtures do not establish discovery or model quality.

## Client-specific routes

**GitHub Copilot:** `copilot-cli`, `copilot-app`, `copilot-vscode`, `copilot-cloud` each select
the existing `.github/skills` and custom-agent kit. Organization policy and available APIs
still differ. Other Copilot IDEs use `other` until their contracts are verified.
The [dedicated guide](copilot.md) preserves the native kit and CLI plugin.

**Claude:** `claude-code` and `claude-desktop` select `.claude/skills` for CLI and Desktop
Code local respectively. This does not cover Chat, Cowork or cloud. The
[Claude guide](claude-code.md) retains plugin skills/agents and separately activated hooks.

**Codex:** `codex-cli`, `codex-desktop`, `codex-ide` select the documented `.agents/skills`
route. Invocation follows the surface: CLI/IDE skills UI or `$` references, desktop's UI.
`codex-cloud` is a manual handoff until that integration is separately verified. The
existing `.codex-plugin/plugin.json` is preserved; no fictional enable/disable marker is used.

**Cursor:** `cursor-cli`, `cursor-ide`, `cursor-cloud` select project `.cursor/skills`
according to the skills documentation. Repository skills are not personal skill sync.
The existing `.cursor-plugin/plugin.json` remains; inspect the installed host's plugin UI
instead of assuming an old `/add-plugin` command or universal settings contract.

**Gemini:** `gemini-cli` selects `.gemini/skills`; the existing `gemini-extension.json`
context route remains. Skills, consent, subagent restrictions and experimental features
follow the exact version, not the obsolete assumption that Gemini has no native skills.

**OpenCode:** `opencode-cli` selects `.opencode/skills`. `opencode-desktop` and `opencode-ide`
use manual handoff until their specific discovery/API contracts are established. The
existing `.opencode/INSTALL.md` route is preserved, not proof of desktop parity.

**Factory:** `droid-cli` selects `.factory/skills`. `factory-desktop` and `factory-cloud`
are separate manual routes. Custom droids' restrictions, including question/nesting limits,
are not inherited from the main CLI's tool list.

**Antigravity:** `antigravity-cli`, `antigravity-desktop`, `antigravity-ide` select the
documented project `.agents/skills` root. Sharing that root does not mean sharing plugin
controls, permissions or Gemini's extension API.

**Kiro:** `kiro-cli`, `kiro-ide`, `kiro-web` select documented workspace `.kiro/skills`.
Custom-agent resource selection and argument substitution vary; no settings are changed.
Existing specifications remain authoritative.

**Devin/Cascade:** `devin-desktop` is Cascade (formerly Windsurf), using `.windsurf/skills`;
`devin-cli` uses `.devin/skills`. `devin-local` and `devin-cloud` remain separate manual
routes. Do not treat old Windsurf naming or CLI model/permission settings as Cascade parity.

**Junie:** `junie-cli` selects documented `.junie/skills`. `junie-ide` records documented
skill capability but keeps a manual route because the precise IDE discovery binding was
not established by the CLI location contract.

**Cline:** `cline-ide` selects `.cline/skills`; `cline-cli` remains manual pending a precise
discovery binding. Experimental research subagents are read-only and are not parallel
implementers or a browser/MCP workaround.

**Continue:** `continue-ide` and `continue-cli` retain distinct manual routes. Plan/Agent
modes, model-dependent tools and CLI profile selection are not subagent delegation.

**Aider:** `aider-cli` uses explicit canonical-file handoff. Ask/read-only/load/save and
architect/editor methods remain useful but do not establish independent review or browser
automation.

**Unidentified:** `other` installs the same manual entry without claiming native discovery.
Unknown IDs are refused rather than silently choosing a different client.

## Manual does not mean discarded

Ask the approved host to read `.github/lintel/START.md`, project instructions and the selected
canonical workflow. Use actual file/shell tools where permitted, otherwise export the original
package brief for another actor. Preserve work-map paths, leaf IDs, acceptance, effective
profile reference, actual result and next action. Keep independent review outstanding until
it occurs. See [the Universal contract](../shims/universal/ADAPTER.md).

The generator preserves unrelated files and project-owned knowledge, manages only its own
files/protocol blocks and refuses modified managed content before writes. Review upgrades
and rollback through normal repository changes; never delete an entire host or knowledge
directory. [Getting started](getting-started.md) gives the common first-task walkthrough.
