# Copilot live acceptance (PR-1a: skills and agents)

Recorded by the coordinator on 2026-09-29 for plan leaves 6.2.a, 6.2.b, 6.3.a (skill and agent
part), 6.3.b and 6.4.a. Hooks are not part of PR-1a; their leaves stay open for PR-1b.

## Provenance

| Item | Value |
|---|---|
| Lintel revision tested | `fd15197974908c457a495c98aeae53bdb7937c32` (branch `jokerman-microsoft-copilot-native-1a`) |
| Plugin version reported by the host | `li` 0.13.0 |
| Client | GitHub Copilot CLI 1.0.89-5, Windows 11, headless `-p` sessions |
| Model | `gpt-5-mini` |
| Environment variable names used (values never recorded) | `LINTEL_POWERSHELL` |
| Raw host event logs | kept local in the host's session store; not committed |

Each probe ran in a fresh temporary Git repository with its own session ID. The CLI was not given
Lintel hooks, custom instructions or any tool beyond the one named for the probe.

## Plugin route (`--plugin-dir` pointing at the tested revision)

- **6.2.a discovery:** `copilot skill list --json` listed 96 `li-*` skills with source `plugin`, all
  from the tested revision, including `li-pause`. The canonical source has 96 skills.
- **6.2.b whole-body delivery:** a `skill.invoked` event for `li-cycle` (source `plugin`, trigger
  `agent-invoked`) carried the generated `.github/skills/li-cycle/SKILL.md` body exactly.
  - The host envelope removes the frontmatter and the single blank line after it. No other byte
    changes, and the content has no carriage returns.
  - SHA-256 of the generated body without that envelope, and of the invoked content:
    `2ba25dc832f12268476bd2fef5da1e3fb40752c58fd784f97e9f7b4fab6ab764` (both, 26,770 bytes).
- **Custom agent selection:** asked to delegate to `CodeReviewer`, the model called the task tool
  with agent type `li:CodeReviewer`.
  - The host names plugin agents `<plugin>:<Name>` and shows the display name `CodeReviewer`.
  - The selected agent's description equals the generated profile's description, and the host's
    selected tool list (`Read`, `Grep`, `Glob`, `Bash`) equals the profile's declared `tools`.
  - The agent completed in 5.8 s without tool calls. The host then recorded a second completion
    marked cancelled when the headless session ended.

## Kit route (`li-copilot init --client copilot-cli`, vendored into a fresh repository)

- `init` then `check`: 609 managed files verified, vendored source, `hooks_installed: false`, and
  no hook registration file.
- **Discovery:** `copilot skill list --json` in the kit repository listed 96 `li-*` project skills,
  including `li-pause`. The kit holds 72 agent files (69 canonical agents plus 3 role profiles).
- **Whole-body delivery:** `li-cycle` (source `project`) carried the kit's generated body exactly,
  with the same envelope. SHA-256 (both):
  `7190621593741415b4ac5a5579fb5fc7b05d99d8a80b97ff28575fd4f7ccb3bd` (26,908 bytes; the vendored
  preamble names `../../lintel`).
- Agent selection on the kit route was not exercised; its agents are counted by file only.

## Gates (6.3.b)

- **Discovery metadata:** 40,691 bytes of native frontmatter for 96 skills and 72 agents (limit
  48 KB). This is the P1 measurement at tree `8f995fc5`; the later merges changed no native file.
- **Bundle growth:** the vendored kit above holds 609 managed files and 5,894,397 bytes. Against the
  `c3ffa153` baseline (457 files, 4,345,072 bytes), growth is 152 files and 1,549,325 bytes (limit
  2 MB).
- **Digest at most 8 KB:** a hook-route gate, left open for PR-1b.

## Limitations

- One operating system, one client version and one model. The Copilot app, VS Code and the cloud
  agent were not observed.
- Whole-body equality was checked for `li-cycle` only. The other skills were counted through
  discovery.
- The agent resource root that an agent's preamble names (review note L8) is not visible in host
  events. It stays a documented instruction, not an observed behavior.
- A custom agent's declared `tools` is what the host selected, which is not a claim that the host
  enforces read-only behavior.
- The seven vendored installation cases and the complete `copilot-kit.py` and
  `universal-adapters.py` suites run in hosted CI on the final candidate before any merge. This
  record does not replace them.
