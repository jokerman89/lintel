# FAQ

Short answers. Every claim here was checked against the repo it ships with; where the answer is
"no, that doesn't exist yet", it says so.

If you are entirely new, read [getting started](getting-started.md) first — this page assumes you
know roughly what Lintel is.

---

## Getting oriented

### Q: What is Lintel, in one paragraph?

A session harness for AI coding agents: markdown and bash that your CLI loads as a plugin. It gives
you a nine-phase development cycle (`/li:cycle`), 125 skills, 69 subagents across 8 categories,
33 hooks, and a per-repo memory layout so lessons and decisions survive a fresh session. There is no
runtime and no service — your CLI is the execution engine. See [architecture](architecture.md) for
how the pieces fit.

### Q: What does "beta" mean here?

This is **v0.9.0-beta**, the first public release. Concretely:

- The shape is stable enough to use daily — 90 tests (36 structural, 48 unit, 4 integration,
  1 behavior, 1 end-to-end)
  guard the contracts that skills depend on.
- Paths, skill names, and the pack schema may still move before 1.0. When they do, a migration note
  lands in [migrations](migrations/_INDEX.md), and deprecated names alias for a grace window rather
  than breaking on the spot.
- There is no uninstall script yet (see below), and three doc-generation skills
  (`/li:generate-pdf`, `/li:generate-xlsx`, `/li:generate-visio`) are self-labelled template-only
  slots — structure without curated content.
- Breaking changes are logged in the [changelog](../CHANGELOG.md).

### Q: Do I need Claude Code specifically?

No, but capability varies. `lib/cli-tiers.yaml` is the single source of truth, and the table in
[multi-cli](multi-cli.md#the-capability-table) is generated from it:

| CLI | Tier | Skills | Subagents | Hooks |
|---|---|---|---|---|
| Claude Code | full | native | native | **yes** |
| Codex CLI / App | full | native | native | no |
| Cursor | full | native | sequenced | no |
| Gemini CLI | supported | manual | none | no |
| OpenCode | supported | manual | none | no |
| GitHub Copilot CLI | supported | native | none | no |
| Factory Droid | supported | native | none | no |
| Cline / Continue / Aider | best-effort | manual | none | no |

The one load-bearing caveat: **hooks fire on Claude Code only.** Every other CLI gets the skills,
the cycle discipline, the memory layout and the pack-driven knowledge — but not the enforcement
layer. That is a limit of what those CLIs expose, not a roadmap item being hidden.

"Skills: manual" means the CLI does not surface `/li:<skill>` as a command; you point the agent at
`skills/<name>/SKILL.md` and it follows the instructions there. "Subagents: sequenced" means Cursor
runs delegated roles one after another rather than in parallel.

### Q: What actually happens on a CLI without hook support?

You lose enforcement, not function. The nine hooks that auto-register on a Claude Code plugin
install are: the session digest, a secret-scan warning on edits, secret-scan and customer-data
blocks at `git commit` and `push`, a direct-push-to-main warning, a memory-budget warning, a
cycle-position injector, a stop-time warning when a turn ends mid-cycle, and a customer-data check
on outgoing messages.

Elsewhere those same rules exist as *instructions* the agent is told to follow — read at session
start from `AGENT-INSTRUCTIONS.md` and the repo's `CLAUDE.md` — rather than as a mechanism that can
refuse the command. An instruction an agent can talk itself out of is weaker than a hook that
returns a non-zero exit code. Judge accordingly.

33 hook directories ship in `hooks/shared/`; 9 auto-register. The rest are opt-in, armed by
symlinking them into your Claude Code hooks directory. See
[getting started](getting-started.md#how-hook-activation-works) for the activation matrix.

### Q: What is a pack, and do I need one?

A pack is the **identity layer**: voice, compliance mode, personas, brand assets, roles. None of it
is hardcoded in the skills — every skill that needs an identity value resolves it at runtime through
`resolve_pack_field` (`lib/pack-resolver.sh`). That separation is what keeps the core
company-neutral.

**You do not need one.** Lintel ships exactly one pack, `_default`, and it is the neutral baseline:
voice tier `internal`, compliance mode `advisory`, no compliance hooks activated, no brand, no
roles, session-summary export to an external vault off. It enforces nothing. You can use Lintel
indefinitely without ever touching packs.

Write a pack when you want the harness to carry your own organisation's voice and rules — then
`/li:pack-switch` activates it and every skill picks it up. See
[pack defaults](concepts/pack-defaults.md), [pack resolver](concepts/pack-resolver.md), and the
[packs reference](wiki/packs.md).

---

## Install, files, and updates

### Q: Where do my files go?

Four roots, two machine-global and two in your repo:

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global | `profile.yaml` (active pack, mode, role), packs, cross-repo job registry, operator audit log |
| `~/.claude/` | machine-global | your CLI's own home — `settings.json`, hooks you symlinked in on a bare install |
| `<repo>/.claude/` | per-repo, **committed** | `memory/` (lessons, working state, personas), `decisions/` (ADRs), `plans/` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | cycle state, job data, session checkpoints, repo event log |

The specific files you will look for most:

- `<repo>/.claude/memory/lessons.md` — accumulated corrections, read at session start
- `<repo>/.claude/memory/working-state.md` — what is in flight across sessions
- `<repo>/.claude/plans/todo.md` — the current plan
- `<repo>/.claude/decisions/` — decision records
- `<repo>/.claude/runtime/state/00-state.md` — where the current cycle is
- `~/.lintel/profile.yaml` — active pack, default mode, active role

The committed/gitignored split is deliberate: knowledge travels in pull requests, runtime churn
stays local. A bare (non-plugin) install additionally copies `scaffolding/` and helper scripts into
`~/.lintel/`. Full detail in [getting started](getting-started.md#where-things-live).

### Q: Do I need `yq`?

Only for one cosmetic step. `install/install.sh` warns if `yq` is missing and skips listing the
entries in `install/upstream-sources.yaml` — that listing is the only thing `yq` is used for, and it
does nothing but print names. Everything else in the installer runs without it.

`install/install.ps1` parses no YAML at all, so the PowerShell path has no YAML dependency and no
module to install. (An earlier version of this FAQ claimed it used `powershell-yaml`. It does not.)

Both installers require `git`.

### Q: Does Lintel install, vendor, or update third-party tools?

**No.** This is the most common wrong assumption, and earlier docs made it worse.

`install/install.sh` ships only operator-authored content. `install/upstream-sources.yaml` is a
list-only stub: the installer counts the entries and prints their names, alongside the literal
message "this installer does not clone them". Nothing is fetched, nothing is vendored, nothing is
pinned.

Consequently there is no upstream-update workflow, no re-verification schedule, and no third-party
license obligation passed on to you. If you want a skill or agent from somewhere else, you install
it yourself, under your own CLI's rules.

### Q: How do I update?

Through your CLI's plugin manager — Lintel is distributed as a plugin, not as a vendored tree.
`bin/li-update` detects which CLIs you have and prints or runs the right command for each:

```
/plugin update li@jokerman-lintel        # Claude Code
gemini extensions update li              # Gemini CLI
copilot plugin update li@jokerman-lintel # GitHub Copilot CLI
```

Run `bin/li-update --dry-run` to see what it would do first. If a release needs a manual step, it is
listed in [migrations](migrations/_INDEX.md).

Updating never touches your repo's `CLAUDE.md`, `.claude/memory/`, `.claude/decisions/`, or
`.claude/plans/`. Those are yours.

### Q: How do I uninstall?

**There is no uninstall script.** Honestly: `grep -ri uninstall` across this repo turns up the
`/li:safe-install` skill admitting the same thing. Manual removal:

1. Remove the plugin through your CLI's plugin manager, the same place you installed it from.
2. `rm -rf ~/.lintel/` — this deletes your profile, packs, and operator audit log.
3. On a bare install, remove any hook symlinks you added under `~/.claude/hooks/` and the matching
   entries from `~/.claude/settings.json`.
4. Per-repo `.claude/` directories are ordinary files in your repo. Delete or keep them — the
   lessons and decision records are readable markdown and stay useful without Lintel.

The installer backs up an existing `~/.lintel/` to `~/.lintel-backup-<timestamp>` before writing, so
step 2 usually has a recoverable copy beside it. A real uninstall path is an open gap for 1.0.

### Q: How do I check the install worked?

`install/verify.sh --all` for a bare install, or `/li:doctor` from inside the CLI — it reports which
CLIs it can see, plugin install status, the Lintel version, and any drift it finds.

---

## Data, privacy, and compliance

### Q: Is my data sent anywhere?

Not by Lintel. It is markdown and bash: no telemetry, no analytics, no callback. The shipped scripts
under `bin/`, `lib/`, `hooks/`, and `install/` contain no outbound HTTP call — the only `curl` in the
tree sits inside a printed help message suggesting the public install one-liner.

What this does **not** cover, and you should account for:

- **Your CLI vendor still sees your prompts and files.** Lintel runs inside your agent CLI; whatever
  that CLI sends to its own provider is unchanged. Check that vendor's policy.
- **A few skills reach the network by design when you invoke them** — `/li:browse` drives a headless
  Chromium, `/li:research` does web lookups, `/li:scrape` fetches pages. They only do this when you
  call them.
- **The session-summary export is off by default.** The CAPTURE phase can additionally write a short
  session summary into an external notes vault, but `vault_sink_enabled` is `false` in the neutral
  pack, and even when switched on it writes to a local path you specify — it is write-only and
  transmits nothing.

### Q: Can I use this repo with customer data?

**No.** Lintel is tooling; customer artifacts never land in it. Customer-facing work belongs in a
customer-scoped repo with its own `CLAUDE.md` layering rules on top of the baseline.

On Claude Code, two hooks back this up mechanically: `customer-data-block` blocks a `git commit` or
`push` that introduces customer data, and `no-customer-data-in-message` checks outgoing messages.
Both are overridable with an explicit environment flag, and every override is written to
`~/.lintel/audit/`. On other CLIs this is instruction-level only.

### Q: What compliance rules does it enforce out of the box?

A neutral baseline plus whatever your active pack adds — there is no fixed corporate rule set built
in. The `_default` pack ships `compliance.mode: advisory` with no compliance hooks activated, which
means the baseline advises, while the safety hooks (secrets, customer data, direct pushes to the
default branch) still block on Claude Code.

The baseline rules are documented in [compliance](compliance.md). Read them critically: they are
derived from common enterprise patterns, not from your organisation's policy. If you need real
compliance behaviour, encode it in a pack and verify it against your own authoritative source.

### Q: What if I accidentally committed customer data?

Treat it as an incident, not a cleanup task:

1. Stop. Do not push.
2. If it is already pushed, follow your organisation's security incident procedure. For a problem in
   Lintel itself, see [SECURITY.md](../SECURITY.md).
3. Rewrite history only after security has acknowledged. Never silently.
4. Record a lesson in `<repo>/.claude/memory/lessons.md` (`/li:learn` writes it for you) so the next
   session starts knowing.
5. Ask why the check did not catch it — if you were on Claude Code and the hook did not fire,
   `/li:doctor` will say whether hooks are registered at all.

---

## Using it

### Q: 125 skills is a lot. Where do I start?

Five, in this order:

- `/li:welcome` — detects your CLI, states its honest tier, runs a dry cycle
- `/li:cycle "<your task>"` — the main loop; everything else is a detour off it
- `/li:learn` — record a correction so the next session inherits it
- `/li:catalog` — the generated index, when you want to browse
- `/li:doctor` — when something looks wrong with the install rather than the work

The other 120 are depth you reach for when you need it. [The cycle](the-cycle.md) explains the nine
phases; [power user](power-user.md) covers context warming, roles, jobs, budgets, and checkpoints;
the full list with triggers is [skills/CATALOG.md](../skills/CATALOG.md), generated from frontmatter.

### Q: Two CLIs are looking at the same repo. Whose state wins?

The last writer. All state is plain files under `<repo>/.claude/` and both CLIs read the same ones.
Lintel does not lock, merge, or mediate. If you run two agents against one repo simultaneously, that
coordination problem is yours to solve.

### Q: A skill works in Claude Code but not somewhere else. Why?

Check the tier table above first. If the CLI is `skills: manual`, it has no slash-command discovery
— the skill still works, you just have to point the agent at `skills/<name>/SKILL.md` yourself.

If the skill depends on parallel subagents, it degrades on `subagents: sequenced` (Cursor, one at a
time) and to inline work on `subagents: none`. If it depends on a hook, it does not enforce anywhere
but Claude Code.

Note that Codex is a **full** tier with native skills *and* native subagents — if something fails
there it is a bug worth reporting, not an expected degradation.

### Q: The agent is ignoring the instructions. What do I check?

In order:

1. Did the plugin actually install? Run `/li:doctor`.
2. Does the CLI read a per-repo instruction file at all, or only a user-global one? Some only do the
   latter — [multi-cli](multi-cli.md) lists the per-CLI entry points.
3. Does that entry file resolve to a real [AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md)?
   Relative-path handling differs across CLIs.
4. Is a rule in the repo's own `CLAUDE.md` overriding it? Repo rules win — that is intended. See
   [precedence](precedence.md) for the full order, including which agent gets picked when several
   match.

If it still misbehaves, open an issue naming the CLI, its version, and the exact file it should have
read.

### Q: There are two lessons tools. Which is which?

They are not interchangeable:

- `bin/li-lessons-promote` — promotes a lesson from this repo's `.claude/memory/lessons.md` into the
  scaffolding baseline, so every repo you scaffold afterwards inherits it.
- `bin/li-lessons-sync` — syncs your own lessons across your machines through a personal git remote.
  Opt-in and private to you; nothing to do with the baseline.

How the memory layer works is covered in [memory v2](concepts/memory-v2.md).

### Q: I want a skill that doesn't exist.

Write it. A skill is a directory with a `SKILL.md` and frontmatter — the contract is in
[skill protocol](concepts/skill-protocol.md). Keep it in your own project first; once it has earned
its place across a few different tasks, a pull request is the way to bring it in.

---

## Contributing

### Q: How do I contribute?

Feature branch, pull request against `main`, reviewers per `CODEOWNERS`. Conventional Commits,
atomic, one logical change per commit. Local tests green before you push:

```bash
bash tests/runner/run-all.sh
```

Typical contributions: a new skill or agent, a new CLI shim under `shims/`, corrections to
`AGENT-INSTRUCTIONS.md`, or fixing wrong paths in the docs. Full conventions in
[CONTRIBUTING.md](../CONTRIBUTING.md).

Note that `skills/CATALOG.md` and the files under `docs/wiki/` are generated — edit the frontmatter
they are built from, not the output.

### Q: Can I customise without opening a pull request?

Yes. Three places, in increasing order of durability:

- **Your repo's `CLAUDE.md` and `.claude/`** — never touched by an update. This is the right home
  for anything project-specific.
- **Your own pack** — the supported way to change voice, compliance, roles, and brand without
  forking anything.
- **`~/.lintel/` edits** — an installer run can overwrite these. Fine for experiments, wrong for
  anything you want to keep.

Fork only for genuine divergence from the design.

---

## Still stuck

Read the [documentation index](README.md), then the page closest to your problem:
[getting started](getting-started.md) to install and run the first cycle,
[architecture](architecture.md) for how it is built, and
[the glossary](GLOSSARY.md) when a term is unfamiliar.

If the docs are wrong, that is a bug — say so in an issue. Wrong documentation is how this file got
rewritten.
