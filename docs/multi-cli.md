# Multi-CLI support

Lintel keeps a shared workflow in `skills/`, role definitions in `agents/`, and reusable resources
in `lib/` and `scaffolding/`. Client adapters expose the parts each host can discover. Installation,
invocation, delegation and hook activation are separate capabilities.

## The capability table

The [README capability table](../README.md#multi-cli-support) is generated from
`lib/cli-tiers.yaml` and checked by `tests/shape/cli-tiers-sync.sh`. It is the single published
matrix; this page does not keep a second copy that can drift.

- **Tier:** Lintel's declared integration level, not a promise of full end-to-end certification.
- **Skills:** whether the host discovers native skills or requires explicit file references.
- **Subagents:** how the integration can delegate work; actual availability depends on the host.
- **Hooks:** whether Lintel supplies an activated compatible hook integration, not whether the
  host has a hook API of its own.

The Copilot repository kit supports native core skills and custom agents. Its integration remains
beta and does not translate Lintel's Claude Code hooks. Other hosts may expose features beyond
what the current Lintel adapter uses.

## One instruction source

`AGENT-INSTRUCTIONS.md` is the canonical Lintel workflow entry in this repository. Client-specific
entry files link to it or to installed portable resources:

| Entry | Client |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | Codex and clients that read this convention |
| `GEMINI.md` | Gemini CLI extension |
| `.github/copilot-instructions.md` | GitHub Copilot |

AGENTS.md and CLAUDE.md repeat the full shared session protocol inline, generated from `scaffolding/01-foundation/SESSION-PROTOCOL.md`. This makes startup independent of personal user-global files. Short client pointers still need to resolve inside the target environment. A path into one developer's plugin cache
or private home directory will not work in another developer's checkout or a cloud agent job.
The Copilot repository kit therefore carries its resources under `.github/lintel/`.

The host decides automatic instruction loading. Lintel's own [precedence](precedence.md) describes
how to reconcile its workflow documents after loading, not a universal override of host rules.

## GitHub Copilot

Recommended for shared repository adoption:

```bash
bash bin/li-copilot init --target ../your-repo
bash bin/li-copilot check --target ../your-repo
```

This exposes native `.github/skills/li-*/SKILL.md` workflows and
`.github/agents/lintel-*.agent.md` profiles. Use `/li-plan`, `/li-build`, `/li-review` and
`/li-resume` where supported. The source kit is portable across machines and cloud checkouts.

Copilot CLI also has a plugin route:

```bash
copilot plugin marketplace add jokerman89/lintel
copilot plugin install li@jokerman-lintel
```

The repository ships a Copilot manifest at `.github/plugin/plugin.json`, separate from the Claude
manifest. Confirm names in the installed plugin's discovery view. Client and repository skill
copies can overlap, so choose an adoption route deliberately.

Copilot has native hooks, but Lintel does not adapt its Claude Code hook contract in this release.
That is an integration limit, not a claim that Copilot lacks hooks or delegation. Use the
[Copilot guide](copilot.md) for the surface matrix, installation, verification and cloud setup.

## Claude Code

```text
/plugin marketplace add jokerman89/lintel
/plugin install li@jokerman-lintel
```

`CLAUDE.md` is the entry point, skills use `/li:<skill>`, and the plugin supplies agent definitions.
The selected hook registrations in `hooks/hooks.json` apply through the Claude plugin. A bare
installation copies hooks without activating them. See
[hook activation](getting-started.md#how-hook-activation-works).

The Copilot repository kit is additive; it does not replace the existing Claude manifest or
change Claude's hook protocol. Keep the original integration when your team uses both clients.

## Codex CLI / App

Use `/plugins`, search for Lintel, and install. Codex uses `.codex-plugin/plugin.json` and
`AGENTS.md`. Skills and subagents are native to the declared integration; plan-first workflow is
an instruction convention. Lintel's Claude hooks do not run through this adapter.

## Cursor

The declared installation is `/add-plugin lintel`, using `.cursor-plugin/plugin.json`. Point
repository instructions at `AGENTS.md`. Lintel declares native skills and sequenced delegation.
Check the installed client's actual behavior; the adapter does not supply Lintel hooks.

## Gemini CLI

```bash
gemini extensions install https://github.com/jokerman89/lintel
gemini extensions update li
```

`gemini-extension.json` loads `GEMINI.md`. Lintel's declared integration uses explicit skill-file
references and main-session role prompts. This describes the adapter shipped here, not every
capability the current Gemini host may offer.

## OpenCode

Read and follow [`.opencode/INSTALL.md`](../.opencode/INSTALL.md). The integration uses `AGENTS.md`
and explicit skill/agent file references. Lintel does not register hooks on this route.

## Factory Droid

```bash
droid plugin marketplace add jokerman89/lintel
droid plugin install li@jokerman-lintel
```

The declared adapter uses Claude plugin interoperability for native skills; delegation is treated
as main-session role use. Lintel hooks are not supplied as a Droid integration.

## Other clients

For Cline, Continue, Aider and unknown clients, use `AGENT-INSTRUCTIONS.md` as explicit task context
and point to the required skill by path. This is best-effort workflow guidance. Skill discovery,
delegation and automatic state injection should not be assumed.

## What degrades

Without native discovery, read the required `SKILL.md` explicitly. Without subagents, sequence
the roles and report that review was not independently delegated. Without compatible registered
hooks, read state and rules explicitly at session start and preserve state at handoff.

The shared `.claude/memory/`, `.claude/plans/` and `.claude/decisions/` files work across clients.
Do not run simultaneous writers against the same task state without coordinating ownership.
Use independent branches or worktrees for separate implementation tasks.

## Adding a new CLI

1. Declare the adapter in `lib/cli-tiers.yaml` and regenerate the README table.
2. Verify the host's current primary documentation and actual discovery/input/output contracts.
3. Add only the manifest or generated adapter the host needs; keep canonical source content shared.
4. Add an instruction entry point that resolves inside the installed environment.
5. Update CLI fingerprint normalization where needed.
6. Add deterministic discovery/installation checks and document an actual client smoke procedure.
7. State untested behavior and unsupported hooks explicitly in [getting started](getting-started.md).

Do not infer a working integration from a manifest that merely parses. Scope advertised support
to the artifacts and behavior that were verified.
