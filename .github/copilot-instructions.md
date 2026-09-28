# Lintel repository instructions

Read [the repository instructions](../AGENTS.md), then the
[Copilot adapter contract](../shims/copilot/COPILOT.md) for multi-step work.

Lintel workflows are native skills. Use `/li-welcome` to inspect setup, `/li-plan` to create
a spec and build cards, `/li-build` to execute authorized cards, and `/li-review` to verify
changes. Use `/li-cycle` for the complete workflow, `/li-resume` to continue a saved plan and
`/li-<name>` for any other Lintel workflow. Lintel roles such as `CodeReviewer` are custom
agents; delegate to them by name.

Read project memory and relevant decisions before edits. Verify actual behavior and
report checks, outcomes and limitations. Keep secrets and customer data out of artifacts.
Repository instructions do not replace enterprise policy, tool permissions or human review.
