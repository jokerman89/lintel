# Multi-CLI support

Lintel is markdown and bash. That is the whole reason it runs on more than one agent CLI: there is
no runtime to port, only files a CLI can be pointed at. What differs between CLIs is how much of the
harness the tool can *invoke* for you, and that difference is declared once in `lib/cli-tiers.yaml`
rather than described in prose.

The short version: **the enforcement hooks fire on Claude Code only.** Everything else — the 125
skills, the 69 agents, the cycle discipline, the pack-driven knowledge — reaches every CLI that has
a plugin mechanism, and reaches the rest as instructions an operator applies by hand.

---

## The two mechanisms

Lintel avoids per-CLI duplication with exactly two moving parts.

### 1. One instruction source

[`AGENT-INSTRUCTIONS.md`](../AGENT-INSTRUCTIONS.md) at the repo root is the canonical session ritual
— read order, compliance checklist, memory map, auto-mode bounds, precedence. Every CLI reaches it
through whatever root file that CLI reads:

| Root file | Read by | Present in this repo |
|---|---|---|
| [`CLAUDE.md`](../CLAUDE.md) | Claude Code | yes |
| [`AGENTS.md`](../AGENTS.md) | Codex, OpenCode, and other CLIs following the `AGENTS.md` convention | yes |
| [`GEMINI.md`](../GEMINI.md) | Gemini CLI (declared as `contextFileName` in `gemini-extension.json`) | yes |
| `.github/copilot-instructions.md` | GitHub Copilot | **no** — see the Copilot note below |

Those root files are pointers plus a short "CLI-specific notes" section. They never override the
canonical file: if a CLI quirk forces different behaviour, the canonical file changes, not the
pointer. `shims/` holds the same three files as templates (`shims/CLAUDE.md`, `shims/AGENTS.md`,
`shims/copilot-instructions.md`) for repos that Lintel scaffolds and that do not already have one.

### 2. Per-CLI plugin manifests

Skills live once at `skills/<name>/SKILL.md`, agents once at `agents/<category>/<Name>.md`. Each CLI
that supports plugins gets a small manifest that points at those same two directories:

| Manifest | For |
|---|---|
| `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` | Claude Code — and, through Claude-plugin interop, GitHub Copilot CLI and Factory Droid, which ship no manifest of their own |
| `.codex-plugin/plugin.json` | Codex CLI and Codex App (carries the extra `interface` block the App shows) |
| `.cursor-plugin/plugin.json` | Cursor |
| `gemini-extension.json` | Gemini CLI |
| `.opencode/INSTALL.md` | OpenCode — not a manifest but a fetch-and-follow install document; OpenCode loads the skill and agent markdown as content |

No skill or agent is written twice. Adding one makes it available on every CLI that can discover it.

---

## The capability table

This table is generated from `lib/cli-tiers.yaml` by `cli_tiers_markdown_table` in
`lib/cli-tiers.sh`. That file is the single source: `/li:welcome` reads it to print your CLI's tier
on first run, and `tests/shape/cli-tiers-sync.sh` fails the build if the copy in the
[README](../README.md) drifts from it.

| CLI | Tier | Skills | Subagents | Hooks |
|---|---|---|---|---|
| Claude Code | full | native | native | yes |
| Codex CLI / App | full | native | native | no (Claude Code only) |
| Cursor | full | native | sequenced | no (Claude Code only) |
| Gemini CLI | supported | manual | none | no (Claude Code only) |
| OpenCode | supported | manual | none | no (Claude Code only) |
| GitHub Copilot CLI | supported | native | none | no (Claude Code only) |
| Factory Droid | supported | native | none | no (Claude Code only) |
| Cline / Continue / Aider | best-effort | manual | none | no (Claude Code only) |

> The README's copy of this table sits between generated markers and is shape-tested against the
> source. The copy above is hand-maintained, so if the two ever disagree, `lib/cli-tiers.yaml` wins.

Reading the columns:

- **Tier** — `full` means skills are invocable and delegation works in some form. `supported` means
  the plugin or instruction layer loads but delegation does not. `best-effort` means instructions
  only.
- **Skills** — `native` means you type `/li:cycle` and the CLI runs it. `manual` means you point the
  CLI at the file: *"Follow instructions from `skills/ship/SKILL.md` and execute on this branch."*
  The content is identical; the invocation is not.
- **Subagents** — `native` means the CLI can delegate to a role in `agents/`. `sequenced` means
  delegation happens, but in sequence rather than in parallel. `none` means the main agent does the
  work itself, using the agent file as a prompt.
- **Hooks** — whether Lintel's enforcement layer actually fires. It fires on Claude Code and nowhere
  else. This is the one gap worth taking seriously, and it is covered under
  [what the canonical file assumes](#what-the-canonical-file-assumes).

---

## Per-CLI notes

### Claude Code — full

```
/plugin marketplace add jokerman89/lintel
/plugin install li@jokerman-lintel
```

- **Root file:** `CLAUDE.md`, at user-global (`~/.claude/CLAUDE.md`) and per-repo. Per-repo wins.
- **Skills:** surface as `/li:<skill>` after the plugin install.
- **Subagents:** first-class. The plugin ships the whole `agents/` fleet; a repo-local
  `.claude/agents/<Name>.md` shadows a plugin agent of the same name.
- **Hooks:** the only CLI where they run. On a plugin install, 9 of the 33 hook directories under
  `hooks/shared/` auto-register through `hooks/hooks.json` across five events, with no edit to your
  `settings.json`. On a bare install they ship inert until you arm them — see
  [getting started](getting-started.md) for the activation contract (ADR-0008).
- **Plan mode:** built in, and read-only.

The canonical instructions are written against this CLI's capabilities and degrade from here.

### Codex CLI / App — full

```
/plugins  →  search lintel  →  Install
```

- **Root file:** `AGENTS.md`, by convention rather than enforcement.
- **Skills:** native. They surface as `/li:<skill>` through `.codex-plugin/plugin.json`.
- **Subagents:** native. Agents load through the manifest and can be delegated to directly. For
  scripted one-shot work, `codex exec` with a scoped prompt is still a valid pattern.
- **Hooks:** none. The secret-scan and customer-data blocks are discipline here, not a gate.
- **Plan-first:** operator-driven, not tool-enforced. The canonical rule still applies — write the
  plan to `.claude/plans/todo.md` and tick items off.

Codex is a full-tier CLI. The only thing it does not get is the hook enforcement layer.

### Cursor — full

```
/add-plugin lintel
```

- **Root file:** none specific to Cursor ships here. Point it at `AGENTS.md`, which redirects to the
  canonical file like every other root pointer.
- **Skills:** native, through `.cursor-plugin/plugin.json`.
- **Subagents:** sequenced. Delegation resolves to the right agent prompt, but runs one at a time.
  Anything in a skill that fans work out in parallel collapses into a sequence.
- **Hooks:** none.

### Gemini CLI — supported

```
gemini extensions install https://github.com/jokerman89/lintel
gemini extensions update li          # to update; the extension is named li
```

- **Root file:** `GEMINI.md`, declared as `contextFileName` in `gemini-extension.json`.
- **Skills:** manual. Gemini extensions are context files plus markdown — there is no slash-command
  discovery, so you reference a skill by path. `GEMINI.md` carries a short list of the ones you will
  reach for most; the full set is in [the skill catalog](../skills/CATALOG.md).
- **Subagents:** none. Ask Gemini to read `agents/<category>/<Name>.md` for role context and do the
  work in the main session.
- **Hooks:** none.

### OpenCode — supported

```
Fetch and follow .opencode/INSTALL.md
```

- **Root file:** `AGENTS.md`, then `AGENT-INSTRUCTIONS.md`.
- **Skills:** manual, loaded as content from `skills/<name>/SKILL.md`.
- **Subagents:** none.
- **Hooks:** none. `.opencode/INSTALL.md` says so explicitly and tells the agent to read each
  `HOOK.md` and apply the discipline by hand.

### GitHub Copilot CLI — supported

```
copilot plugin marketplace add jokerman89/lintel
copilot plugin install li@jokerman-lintel
```

- **Skills:** native. Copilot CLI reads the `.claude-plugin/` marketplace descriptor through
  interop, so `/li:<skill>` works without a Copilot-specific manifest.
- **Subagents:** none. Where a skill says "delegate to agent X", run the agent's prompt yourself.
- **Hooks:** none.
- **Root file:** this repo has **no** `.github/copilot-instructions.md`. Only the template at
  `shims/copilot-instructions.md` exists. To wire the instruction layer into a repo of your own,
  copy or symlink that shim to `.github/copilot-instructions.md` there. If you copy it, treat the
  copy as derived and refresh it when the shim changes.

The Copilot **IDE** experience is a different product and is not a Lintel target — it has no plugin
mechanism to load skills or agents from. The instruction shim can still be used there, but you get
the written disciplines only.

### Factory Droid — supported

```
droid plugin marketplace add jokerman89/lintel
droid plugin install li@jokerman-lintel
```

- **Skills:** native, via the same `.claude-plugin/` interop path Copilot CLI uses. No Droid-specific
  manifest exists or is needed.
- **Subagents:** none.
- **Hooks:** none.

### Cline, Continue, Aider and anything else — best-effort

No plugin discovery. Add `AGENT-INSTRUCTIONS.md` as the tool's custom-instructions file and invoke
skills by pointing at their path. You get the read order, the compliance checklist, the memory map
and the precedence rules; you do not get slash commands, delegation or gates.

Anything `skills/cli-fingerprint` cannot identify also lands here. `cli_tier_field` returns safe
defaults for an unknown CLI — tier `best-effort`, hooks off — so a CLI Lintel has never seen
degrades honestly instead of over-claiming.

---

## What the canonical file assumes

`AGENT-INSTRUCTIONS.md` is written to survive the worst target, not to exploit the best one:

- **No subagents.** Every delegation reads as "delegate this; if you cannot delegate, sequence it."
- **No hooks.** Every rule the hooks enforce is also written down as a rule. On Claude Code the
  block is mechanical; elsewhere it is a stated obligation an agent can still skip.
- **Filesystem conventions that work everywhere** rather than CLI-specific tools:
  `.claude/memory/lessons.md`, `.claude/memory/working-state.md`, `.claude/memory/personas.md`,
  `.claude/plans/todo.md`, `.claude/decisions/`, and the gitignored
  `.claude/runtime/state/00-state.md`. Operator identity — active pack, mode, role — sits outside
  the repo at `~/.lintel/profile.yaml`.
- **Pointers over inlining.** State is cited by location, so a CLI with a smaller context window
  reads what it needs instead of carrying everything.

**Be clear-eyed about what this does and does not buy you.** A Gemini or Copilot CLI operator gets
the same compliance checklist, the same memory protocol and the same precedence rules as a Claude
Code operator. What they do not get is the part that does not depend on the agent cooperating: on
Claude Code, `secret-scan-block` and `customer-data-block` refuse the `git commit`. Everywhere else,
those are sentences in a markdown file. A written rule and an enforced gate are not the same
guarantee, and the tier table exists so nobody has to guess which one they have.

---

## Adding a new CLI

1. **Declare it.** Add a row to `lib/cli-tiers.yaml` with `label`, `tier`, `hooks_supported`,
   `skills_native`, `subagents` and `install`. Until you do, the CLI resolves to the safe
   best-effort defaults — correct, just pessimistic.
2. **Regenerate the table.** `source lib/cli-tiers.sh && cli_tiers_markdown_table`, then paste the
   output between the `CLI-TIERS` markers in the README. `tests/shape/cli-tiers-sync.sh` fails the
   build if you skip this.
3. **Give it a manifest — if it needs one.** A small file pointing at `./skills/` and `./agents/`,
   next to the existing ones. If the CLI reads the Claude plugin format through interop, skip this.
4. **Give it a shim — if it reads a root file Lintel does not already cover.** Add
   `shims/<filename>` that points at `AGENT-INSTRUCTIONS.md` plus a CLI-specific notes section.
   Notes layer; they never override.
5. **Teach the fingerprinter.** If the CLI reports an identifier that `cli_tier_normalize` in
   `lib/cli-tiers.sh` does not recognise, map it onto its row so `/li:welcome` shows the right tier.
6. **Document the install** in [getting started](getting-started.md).

If a CLI reads no per-repo instruction file and has no plugin mechanism, Lintel cannot reach it.
That is a real limit, not a gap waiting to be filled.

---

## When the canonical file should change

Change `AGENT-INSTRUCTIONS.md` when the behaviour should be uniform everywhere — a new compliance
step, a new memory section, a revised precedence rule, or a section that is wrong in the same way on
every CLI.

Do not change it when the need is specific to one CLI (that belongs in that CLI's root file or
shim), specific to one repo (that repo's `CLAUDE.md`), or a personal preference (user-global
`~/.claude/CLAUDE.md`).

If a per-repo rule and the canonical file conflict, the per-repo rule wins. If a CLI shim and the
canonical file conflict, the canonical file wins — the shim layers, it does not override. When an
agent hits a conflict mid-task it halts and reports rather than picking a side.
[Precedence](precedence.md) has the full order, for both instruction files and agent selection.

---

## See also

- [Getting started](getting-started.md) — install commands per CLI, and how hook activation works
- [Architecture](architecture.md) — the spine, the pack, and where state lives
- [Precedence](precedence.md) — which instruction file wins, and which agent gets picked
