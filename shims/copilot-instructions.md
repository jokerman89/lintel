# GitHub Copilot session entry

This file redirects to `AGENT-INSTRUCTIONS.md`, which is the canonical source for session bootstrap behavior across all agent CLIs.

**→ See [../AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md) for full session bootstrap.**

---

## Setup note

> **Which Copilot is this for?** This shim targets **Copilot in the IDE** (Copilot Enterprise),
> which reads `.github/copilot-instructions.md`. **GitHub Copilot CLI** is a different product and
> needs no shim — it reads the `.claude-plugin/` manifest directly and gets skills natively. See
> [docs/multi-cli.md](../docs/multi-cli.md).

Copilot in the IDE reads instructions from `.github/copilot-instructions.md` in the repo root. Two install options:

**Option A — symlink (recommended on macOS/Linux/WSL):**

```bash
mkdir -p .github
ln -sf ../shims/copilot-instructions.md .github/copilot-instructions.md
```

**Option B — copy (Windows without admin, or repos where symlinks are not desired):**

```bash
mkdir -p .github
cp shims/copilot-instructions.md .github/copilot-instructions.md
```

If you copy, treat `.github/copilot-instructions.md` as derived — re-copy when `shims/copilot-instructions.md` changes. The shim is short, so drift is unlikely, but it can happen.

---

## Copilot Enterprise-specific notes

These are tips that only apply when running under GitHub Copilot Enterprise. They do not override `AGENT-INSTRUCTIONS.md` — they layer on top.

### Model selection

Copilot Enterprise's model picker exposes multiple backends. For agent-style work (planning, multi-step reasoning, architectural decisions), select **Claude Opus** (or the latest Opus-class model available in your tenant). Default Copilot completions are tuned for inline suggestion, not session-level agency.

### Subagents

Copilot does not have a subagent abstraction comparable to Claude Code. Copilot Extensions exist but operate differently — they are integrations, not delegated workers.

When `AGENT-INSTRUCTIONS.md` says "use a subagent for X", the Copilot equivalent depends on context:

- For research / exploration: scope a focused conversation thread.
- For audits / reviews: open a separate review pass with a narrow prompt.
- For parallel work: not directly supported. Sequentialize.

### Tool access

Copilot's tool access is governed by enterprise policy. Auto-mode bounds in `AGENT-INSTRUCTIONS.md` are necessary but may not be sufficient — enterprise policy may further restrict what is callable.

### Context window

Copilot's effective context is smaller than a fresh Claude Opus session. Keep `.claude/memory/working-state.md` lean and high-signal. Use ADR pointers (file + section) rather than inlining ADR text.

### Customer-data check

The compliance check in `AGENT-INSTRUCTIONS.md` step 2 (customer-data check) applies with extra weight under Copilot Enterprise. Prompts traverse enterprise infrastructure but historical data-handling assumptions may not match your tenant. When in doubt: do not paste, summarize instead.
