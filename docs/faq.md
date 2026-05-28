# FAQ

Short answers. Links into deeper docs when the answer is non-trivial.

## Setup

### Q: Do I need Claude Code specifically?

No. Works with Claude Code, GitHub Copilot Enterprise (with Opus model picker), Codex CLI, and any agent CLI that reads a per-repo instructions file. See [multi-cli.md](multi-cli.md).

### Q: Can I use this if I only have GitHub Copilot Enterprise (no Claude Code)?

Yes, with limitations. Copilot has no subagent equivalent and no skill/slash-command support, so anything that depends on those degrades to manual or sequential. The compliance check, memory protocol, and precedence rules still work.

### Q: Do I need `yq` if I use the PowerShell installer?

No. The PowerShell installer uses the `powershell-yaml` module (auto-installed for current user on first run). `yq` is only required for the bash installer.

### Q: Where does the scaffolding actually land after install?

`~/.claude-scaffolding/`. The upstream tools land at the install paths declared in `install/upstream-sources.yaml` (typically under `~/.claude/skills/` or `~/.claude/`).

## Customer-data + compliance

### Q: Can I use this with customer data?

**No.** Customer data never lands in this scaffolding repo. The scaffolding is for tooling setup, not for customer artifacts. See [compliance.md](compliance.md) for the full rule set.

Customer-data work happens in a customer-scoped repo with its own `CLAUDE.md` that adds rules on top of the standard 15.

### Q: What if I accidentally committed customer data?

Treat it as an incident:

1. Stop. Do not push.
2. If already pushed: contact MS-internal security following standard incident procedure.
3. Rewrite history with `git filter-branch` or BFG, but only after security has acknowledged. Do not silently rewrite.
4. Add a lesson to `tasks/lessons.md`.
5. Audit why it happened — the compliance check at step 2 should have caught it.

### Q: Does the installer phone home?

No. The install scripts make `git clone` calls to public GitHub repos. That is the entire network surface. No telemetry to MS or to anyone else.

(The upstream tools you install — gstack, GSD, AgentShield, etc. — may have their own telemetry. Check each upstream's docs.)

## Updates + maintenance

### Q: How do I update the upstream tools?

Re-run the installer:

```bash
bash install/install.sh
```

Already-cloned sources do `git pull --ff-only` instead of re-cloning. New sources added to `install/upstream-sources.yaml` since your last install get cloned for the first time.

### Q: How do I update the scaffolding itself?

Pull the latest of this repo, then re-run the installer:

```bash
cd ~/Workspace/jokerman-lintel
git pull
bash install/install.sh
```

The installer overwrites `~/.claude-scaffolding/` from the repo. **It does not touch per-repo `CLAUDE.md` files** — your project-specific customizations are safe.

### Q: An upstream source has disappeared / been deleted. Now what?

1. Re-run `install.sh` will fail on the missing source.
2. Mark the source as `install_type: deprecated` in `upstream-sources.yaml` and the installer will skip it.
3. File a PR to either remove it or replace it with a successor.

Fallback strategies for high-importance sources are written into [promoted-agents.md](promoted-agents.md) per source.

### Q: How often is `upstream-sources.yaml` re-verified?

`last_verified` field per source. Aim for quarterly re-verification at minimum. Add a calendar reminder or build it into a quarterly cleanup PR.

## Contributing

### Q: How do I contribute back?

PR against `main`. Reviewers: anyone on the CAIP SE team listed in `CODEOWNERS` (TBD when published). Typical PRs:

- Adding a new agent to [promoted-agents.md](promoted-agents.md). Follow the promotion process.
- Updating canonical instructions in `AGENT-INSTRUCTIONS.md`. Log the change in `scaffolding/EVOLUTION-LOG.md`.
- Adding a new shim under `shims/` for a new CLI.
- Fixing wrong paths / outdated information.

### Q: Can I add my own customizations without PRing?

Yes, with the standard trade-off: customizations that live only in your local `~/.claude-scaffolding/` will be overwritten the next time you run the installer. Either:

- PR the change so it lands canonically, or
- Maintain a separate fork (only worth it for major divergence).

## Tooling

### Q: I want a skill that does X, but it doesn't exist in any of the promoted sources. What do I do?

1. Look in `~/.claude/skills/anthropic/skill-creator/` — Anthropic's skill scaffold can produce one quickly.
2. Write the skill in your own project's `.claude/skills/` first.
3. Once it has proved itself across 3+ contexts, propose promotion via PR (see [promoted-agents.md](promoted-agents.md)).

### Q: Can I install a non-promoted skill or agent?

Yes, but personally — at your own risk. The promoted list is the team's vetted set. Non-promoted skills do not get reviewed and are not guaranteed to remain compatible.

If you find a non-promoted skill genuinely useful, promotion is the path to bring it into the team's default set.

### Q: A promoted agent gave me a wrong recommendation. What do I do?

1. Verify the recommendation against an authoritative source (docs, code, an expert).
2. If genuinely wrong: file an issue in the upstream repo of the agent.
3. Capture a lesson in `tasks/lessons.md` so the next person in your team is on guard.
4. If the wrongness is severe enough: propose demotion (see [promoted-agents.md](promoted-agents.md) → Demotion).

## Auth + access

### Q: Does this scaffolding need any special auth?

For the install: only public GitHub access (which `git clone` over HTTPS provides). For the agent CLI itself: whatever auth that CLI requires (MS SSO for Copilot Enterprise, Anthropic API key for Claude Code, etc.).

### Q: Can I use this from a corporate-network machine that blocks public GitHub?

If GitHub is blocked, the install will fail at the `git clone` step. Options:

- Use a personal machine + Microsoft SSO from there.
- Set up a corporate-network proxy that allows GitHub access for engineering tools.
- Mirror the upstream repos to an internal GitHub Enterprise instance and edit `upstream-sources.yaml` to point at the mirrors.

The third option is the most robust for long-term enterprise use but adds maintenance.

## Multi-CLI gotchas

### Q: Two CLIs are looking at the same repo. Whose state wins?

The state is in files (`tasks/`, `docs/adr/`, `CLAUDE.md`). Both CLIs read the same files. Whoever writes last wins, last-writer-wins style.

If two CLIs are operating on the same repo simultaneously: that's a coordination problem you have to solve manually. The scaffolding does not mediate.

### Q: A skill works in Claude Code but not in Copilot. Why?

Copilot does not support Claude Code skills (slash commands). Skills are Claude Code's native feature. Codex has its own model. Cross-CLI portability for skills is intentionally not promised by this scaffolding.

## When something is wrong

### Q: The agent isn't following the canonical instructions. What do I do?

Check in order:

1. Did the agent actually read the shim file? (Open the shim, see the redirect to `AGENT-INSTRUCTIONS.md`.)
2. Does the shim actually point to a `AGENT-INSTRUCTIONS.md` that exists? (Relative-path resolution differs across CLIs.)
3. Is there a competing rule in a per-repo `CLAUDE.md` that overrides it? (Per-repo rules win.)
4. Is the operator using a CLI that does not actually read the shim file? (Some CLI versions only read user-global instructions, not per-repo.)

If still wrong: file an issue with the specific CLI + shim file + agent behavior.

### Q: I'm getting lost. Where do I start over?

Read [README.md](../README.md), then [getting-started.md](getting-started.md), then the doc closest to what you are trying to do. If still stuck, post in `#caip-se-tooling` (or your team's equivalent) with what you've already tried.
