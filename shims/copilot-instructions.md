# GitHub Copilot session entry

For work on Lintel itself, read [AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md)
and the [Copilot adapter contract](copilot/COPILOT.md).

For another repository, run `bash bin/li-copilot init --target /path/to/repo`
from a reviewed Lintel checkout, or `bash bin/li-scaffold init --copilot --target /path/to/repo`.
The installer creates supported `.github/skills/li-*/SKILL.md`, `.github/agents/*.agent.md`
and instructions with correct repository-relative links. Do not copy this source-only
shim into a consumer repository; its relative links describe the Lintel source tree.

Copilot CLI, VS Code and the GitHub cloud agent have different tool capabilities.
Use native delegation when available and accurately label a sequential fallback.
The kit does not pin models, install hooks or change enterprise permissions.
See [the Copilot guide](../docs/copilot.md) for setup and limitations.
