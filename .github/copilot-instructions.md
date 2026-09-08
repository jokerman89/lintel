# Lintel repository instructions

Read [the repository instructions](../AGENTS.md), then the
[Copilot adapter contract](../shims/copilot/COPILOT.md) for multi-step work.

Use `/li-welcome` to inspect setup, `/li-plan` to create a spec and build cards,
`/li-build` to execute authorized cards, and `/li-review` to verify changes.
Use `/li-cycle` for the complete workflow and `/li-resume` to continue a saved plan.
If slash discovery is unavailable, ask Copilot to read the corresponding
`.github/skills/li-<name>/SKILL.md` and carry out its instructions.

Read project memory and relevant decisions before edits. Verify actual behavior and
report checks, outcomes and limitations. Keep secrets and customer data out of artifacts.
Repository instructions do not replace enterprise policy, tool permissions or human review.
