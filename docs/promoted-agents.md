# Promoted agents

The agents and skills our team has decided are worth invoking by default. "Promoted" means: vetted, kept up to date, and lifted to **precedence level 3** in the [agent selection model](precedence.md).

The list is intentionally short. Every promoted agent has earned its slot. New additions follow the promotion process below.

> **Important.** All agents listed here come from upstream repos via `install/upstream-sources.yaml`. We do not vendor their code. License obligations follow the upstream license — see each row.

## Active list

### From AgentShield — `affaan-m/agentshield` (MIT)

**1. AgentShield (root tool)**
- **Upstream:** [github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **Install path:** `~/.claude/skills/agentshield/`
- **What it does:** Scans agent configurations (CLAUDE.md, .cursorrules, agent.json, custom configs) for vulnerabilities: hardcoded secrets, permission misconfigs, hook injection, MCP server risks, prompt-injection vectors. 102 static rules, 1,282 tests.
- **Why promoted:** This is the closest match to the secret-scanning needs a company pack's compliance tier declares. We treat it as the first line of defense before any new repo accepts an agent setup. Run before every `git push` that touches `.claude/` or `CLAUDE.md`.
- **When to invoke:** New repo setup, any time `CLAUDE.md` or `.claude/` is edited, before any release that includes agent config changes.

### From Trail of Bits — `trailofbits/skills` (CC-BY-SA-4.0 — restricted)

> **License note.** All Trail of Bits skills below are CC-BY-SA-4.0. Invoking them from the install path is fine. Copy-pasting any of their content into an MIT-licensed repo would require that derivative work to also be CC-BY-SA-4.0 — **incompatible with MIT**. Use them as installed tools, never as code to inline.

**2. differential-review**
- **Install path:** `~/.claude/skills/trailofbits/plugins/differential-review/`
- **What it does:** Differential code review — compares two states (PR vs. base, before vs. after) and identifies semantic differences that matter for security: changed authn paths, new untrusted inputs, deleted sanitization.
- **Why promoted:** Catches the security-relevant subset of PR changes that a generic code-reviewer misses. Use alongside (not instead of) our `CodeReviewer` subagent.
- **When to invoke:** Any PR that touches authentication, authorization, input handling, or trust boundaries.

**3. insecure-defaults**
- **Install path:** `~/.claude/skills/trailofbits/plugins/insecure-defaults/`
- **What it does:** Scans for framework / library settings that ship insecure by default — TLS versions, CORS settings, cookie flags, hash algorithms, deserialization options.
- **Why promoted:** Most production security incidents start with a default that should have been changed but wasn't. This catches them before they ship.
- **When to invoke:** New service setup, dependency upgrades, framework migrations.

**4. supply-chain-risk-auditor**
- **Install path:** `~/.claude/skills/trailofbits/plugins/supply-chain-risk-auditor/`
- **What it does:** Audits dependencies for supply-chain risk: typosquats, abandoned maintainers, recently-transferred packages, known-bad versions, lockfile drift.
- **Why promoted:** Customer engagements increasingly require an SBOM + supply-chain story. This produces the artifact directly.
- **When to invoke:** Pre-release, after any `package.json` / `requirements.txt` / `go.mod` edit, on a cadence (monthly) for active services.

**5. agentic-actions-auditor**
- **Install path:** `~/.claude/skills/trailofbits/plugins/agentic-actions-auditor/`
- **What it does:** Audits GitHub Actions workflows for security vulnerabilities in AI agent integrations. Detects misconfigurations specific to Claude Code Action, Gemini CLI, OpenAI Codex, GitHub AI Inference in CI/CD pipelines.
- **Why promoted:** We are pushing agent-driven CI patterns to customers; this audits the patterns we recommend.
- **When to invoke:** Before any PR that adds or modifies a workflow file that calls an agent action.

### From Anthropic — `anthropics/skills` (Apache-2.0 / source-available — restricted tier)

> **License note.** Most Anthropic skills are Apache-2.0 (bundle-safe). The document-creation skills (docx/pdf/pptx/xlsx) are source-available but not open-source per Anthropic's repo README. Check per-skill before bundling. Installed via `~/.claude/skills/anthropic/`.

**6. mcp-builder**
- **Install path:** `~/.claude/skills/anthropic/mcp-builder/`
- **What it does:** Scaffolds a new MCP (Model Context Protocol) server from a description. Generates the boilerplate, tool registration, and basic transport setup.
- **Why promoted:** MCP is our preferred extension surface for customer-facing AI tooling. The scaffold is correct; saves an hour per server.
- **When to invoke:** Starting a new MCP server, including for a customer PoC.

**7. skill-creator**
- **Install path:** `~/.claude/skills/anthropic/skill-creator/`
- **What it does:** Scaffolds a new Claude Code skill (slash command) following Anthropic's structural conventions: SKILL.md frontmatter, prompt body, output contract.
- **Why promoted:** Internal demand for project-specific skills is growing. Using the authored convention keeps them portable across repos.
- **When to invoke:** Promoting a recurring prompt pattern into a reusable skill.

## Promotion process

A new agent reaches "promoted" status by passing the bar below and getting a PR merged that adds it here.

### Bar for promotion

1. **Used in three distinct project contexts.** Not the same project three times.
2. **At least one of those uses was non-obvious** — i.e., the agent caught or enabled something the operator would have missed.
3. **Licensed permissively** (MIT/Apache) **or explicitly flagged** as restricted with a license note (see Trail of Bits entries above).
4. **No replacement of an existing promoted agent.** If the new agent overlaps, the PR also argues which one to demote.
5. **Active maintenance.** Upstream has had a commit in the last 6 months.

### How to propose

1. File a PR adding the agent here with: install path, what it does, why promoted, when to invoke, license note if needed.
2. Update `install/upstream-sources.yaml` if the new agent is not from an already-installed upstream.
3. Tag two reviewers (e.g. the maintainers listed in CODEOWNERS).
4. Once merged: next `bash install/install.sh` run picks it up.

### Demotion

A promoted agent can be demoted if:

- It has not been used in 6 months (signal that we promoted it prematurely).
- A bug or behavior makes it untrusted (an incident, a wrong recommendation that shipped).
- Its license changed to incompatible terms.

Demotion is a PR — same template as promotion, with a "why demoting" paragraph. Moved to the "deprecated" section below rather than deleted, so the history is visible.

## Deprecated

<!-- Entries moved here when an agent is demoted. Keep with date + reason. -->

(none yet)

## Notes on verifying install paths

The exact subdirectory names within `~/.claude/skills/trailofbits/` and `~/.claude/skills/anthropic/` follow the upstream repo's `plugins/` or top-level layout. After `bash install/install.sh`, verify with:

```bash
ls ~/.claude/skills/trailofbits/plugins/   # expect: differential-review, insecure-defaults, supply-chain-risk-auditor, agentic-actions-auditor, ...
ls ~/.claude/skills/anthropic/             # expect: mcp-builder, skill-creator, plus other Anthropic skills
```

If a subdirectory listed above has been renamed upstream, this doc is stale — file a PR to update.
