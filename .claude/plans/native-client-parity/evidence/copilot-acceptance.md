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
  - The generated file is 26,922 bytes (SHA-256
    `01fc5c5178e6cb3d5c7f5d41be09b0875d325573193edb1d13a4771704d078b8`). The host envelope
    removes its 151-byte frontmatter block and the single blank line (1 byte) after it.
  - The raw invoked content is the remaining 26,770 bytes, byte for byte, including the final
    newline, with no carriage returns. Both have SHA-256
    `9c88c9039b3df4e42a4fa07ba4766211417ff6104e58fea50c8436083d3a73d4`.
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
  with the same envelope. The generated file is 27,060 bytes (SHA-256
  `459fcca202e0cac0ba34abf61f80effc32e718d579bcbd0d11d0201f2af8dd70`). The raw invoked content is
  the remaining 26,908 bytes, byte for byte, including the final newline. Both have SHA-256
  `1c8c031ed735106f18436059c5efd7bf4eb1887cf09497e7de58146f5778483a`; the vendored preamble
  names `../../lintel`.
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

## Correction record (2026-09-29)

The first version of this record (commit `5389f94f`) gave these hashes for the 6.2.b equality:

- plugin route: `2ba25dc832f12268476bd2fef5da1e3fb40752c58fd784f97e9f7b4fab6ab764`, labeled 26,770 bytes;
- kit route: `7190621593741415b4ac5a5579fb5fc7b05d99d8a80b97ff28575fd4f7ccb3bd`, labeled 26,908 bytes.

They are correct SHA-256 values, but of different inputs than stated. The coordinator's analysis
hashed both sides after trimming leading and trailing newlines: 26,769 and 26,907 bytes, without
the final newline. The labeled byte counts were those of the untrimmed content, and the note "no
other byte changes" was right. MasterCoordinator found the mismatch by hashing the immutable
generated file independently.

The corrected values above come from the same raw `skill.invoked` events and generated files,
with no new probe or model call. On both routes, exact byte equality holds for the untrimmed
content.

The probe script's own log line compared other hashes (`b1e97363…` and `f4e8bd19…` on the plugin
route) and fell back to ordered line coverage. That comparison is void: a PowerShell function
returned its provenance note together with the invoked text, which prepended 252 bytes, and its
expected side kept the blank separator line. The raw events show no such prefix. The original
script log is kept unchanged as history.
