---
applyTo: "**"
---

This repository uses Lintel. Its workflows are native skills: invoke `/li-plan` before
substantive work, `/li-build` for authorized cards, `/li-review` before delivery and
`/li-<name>` for any other Lintel workflow. Lintel roles such as `CodeReviewer` are custom
agents. Read [the Copilot adapter](../../shims/copilot/COPILOT.md) before a multi-step task.
Load the repository's AGENTS.md and relevant memory and decisions. Keep plans and durable
lessons in .claude/; the directory name is shared storage, not a requirement to use Claude
Code. Existing user authorization remains valid; ask only for missing scope or a new
permission boundary. Lintel instructions and reviews complement host permissions and branch
rules; they do not enforce them.
