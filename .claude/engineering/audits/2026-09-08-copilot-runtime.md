# Copilot runtime and onboarding review — 2026-09-08

**Scope:** Native discovery, downstream installation, canonical source resolution,
cross-platform behavior and honest verification boundaries. **Build card:** BC2 in
[the launch plan](../../plans/copilot-enterprise-launch/plan.md).

## Findings and disposition

| Severity | Finding | Resolution |
|---|---|---|
| P1 | No repository-native Copilot instructions, skills or custom agents were installed. The source shim's relative links were unsafe to copy downstream. | Added `bin/li-copilot init/check`, generated native entries and a self-contained source bundle under `.github/lintel/`. |
| P1 | Downstream planning required canonical templates and skill files unavailable in the target repository or a clean cloud clone. | Bundle selected canonical resource directories, plan templates and runtime documentation. Generated references are relative to each native entry file. |
| P1 | The pack resolver used the target repository root to load its own audit helper. Setting the correct project state root broke installed-only execution. | Split `LINTEL_SOURCE_ROOT` from `LINTEL_REPO_ROOT`; `lib/copilot-env.sh` initializes portable helper lookup and local gitignored runtime storage. |
| P1 | Blind overwrite or symlink-based onboarding could replace project policy or write outside the intended tree. | Preflight the complete update, refuse conflicting managed/unowned files and unsafe/reparse paths, preserve user-owned memory and instructions. |
| P1 | Raw text hashes and default Windows checkout conversion could invalidate an otherwise identical clone and break Bash scripts. | Normalize source text to LF, add scoped `.gitattributes` rules and test a real Git clone with `core.autocrlf=true`. |
| P2 | Existing shim claimed Copilot lacked subagents, required Enterprise and should select a fixed Claude model. | Replaced with capability-aware contract, native delegation where supported, explicit sequential/self-review fallback and host-selected models. |
| P2 | A prompt-file-first design would fail with VS Code's Agent Host. | Use native `li-*` skills as the common entry point; no dependency on prompt files. |
| P2 | Claude hook wording could be mistaken for Copilot enforcement. | Install no hooks or permission overrides; explicitly adapt automatic-hook language to verified host capabilities. |
| P1 | Files generated on Windows may have no executable bit in a later POSIX clone, breaking sibling helper execution or silently skipping envelope validation. | Launch shell siblings through Bash; explicitly refuse a missing validator; separate validator/schema source from project state. |
| P2 | check accepted missing runtime ignore rules, and scaffold --copilot silently dropped company-pack/customization flags. | Require the rule (plus effective Git ignore verification in Git repos); refuse unsupported scaffold flags before writes. |
| P2 | Non-object inventory JSON caused tracebacks; noncanonical path aliases could refer to the same managed file twice. | Validate inventory shape/types and canonical relative paths before processing or writing. |

## Implemented contract

`bash bin/li-copilot init|check --target PATH [--source PATH]` runs using Python 3.9+
and standard library only. `bash bin/li-scaffold init --copilot --target PATH` delegates
to the same atomic-preflight workflow. No network access or global install is required.

Consumer repositories receive `.github/skills/li-*/SKILL.md`, three focused custom
agents, an additive path-scoped instruction and (when absent) repository instructions.
The versioned source bundle contains bin, lib, canonical skills and agents, foundation
templates, the neutral pack and selected runtime documents. No hooks, credentials,
private/company packs, host settings or runtime data are copied. Lintel's own checkout
uses direct source references and does not copy itself recursively.

`init` also performs upgrades. Hash inventory is `.github/lintel/manifest.json`; local
edits to a managed file cause the entire update to fail before writing. An existing
team `.github/copilot-instructions.md` stays user-owned; the additive instruction supplies
the Lintel entry. Plans and memory are seeds, never overwritten on update. The complete
shared session protocol is appended to both AGENTS.md and CLAUDE.md with marked blocks;
updates hash only those blocks and preserve all surrounding project prose. Edited or
malformed protocol blocks refuse the whole update. Existing authorization comes from
the operator's explicit request to repeat the complete startup contract in each repo.
Obsolete inventory-listed files are removed only when their previous hash still matches.
There is no automatic uninstall, policy migration or company-pack activation.

## Evidence

`tests/integration/copilot-kit.sh` exercises actual adapter subprocesses: fresh onboarding,
repeat-run idempotence, clean-clone portability, source upgrades, custom instruction/memory
preservation, managed drift, missing files, unmanaged collisions, inventory traversal,
symlink parents, no-recursion dogfood, CRLF/autocrlf behavior and real Bash pack/path helpers.
It also checks portable full protocol replication, block conflict handling and source
updates, existing CRLF project prose, default source selection with an empty user home,
and legacy scaffold rendering from the same canonical protocol.
Host-dependent symlink creation is reported as a skip when Windows denies that capability;
Linux CI runs the real symlink case. Final aggregate results belong in the launch record.

**Final adapter regression run:** 19 tests passed in 179.627 seconds on Windows Git Bash
with the bundled Python runtime; zero skipped tests, including real native Windows symlinks.
This includes the independent review fixes for missing/negated runtime ignore, unsupported
scaffold flags, no-execute-bit sibling tools, absent envelope validators and malformed inventory
roots/path aliases. Existing pack resolver fallback (9 scenarios) and inheritance suites also
passed. The repository's `li-copilot init` then `check` validated all 18 native entry files.

`li-copilot check` validates generated entries, expected source snapshot, inventory hashes,
foundation files and adapter links. It does **not** validate tenant licensing, client discovery,
model behavior, organization policy, live subagent invocation or the cloud execution path.
The manual session acceptance sequence is in `shims/copilot/COPILOT.md`.

## Primary documentation checked

- [GitHub CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference): supported manifest locations, component paths and discovery precedence.
- [GitHub custom agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration): supported schema, environment differences, no model/tool restrictions required by the adapter.
- [GitHub CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions): instruction locations and supported discovery inspection.
- [GitHub CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills): supported skill folders, reload and inspection commands.
- [GitHub agent skills overview](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills): shared project skill support across clients.
- [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills): name/directory constraints and relative resource links.
- [VS Code prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files): Agent Host limitation; native skills are the portable entry surface.

Documentation verification is separate from live product validation. The launch must retain
that distinction and must not describe this local test run as a tenant pilot.
