---
name: jstack-setup-gbrain
description: Configure gbrain semantic-index integration — initialize config, pin worktree, register sync.
color: orange
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code]
---

# /setup-gbrain

One-time setup for gbrain integration. Writes `~/.gbrain/config.json`, creates the per-worktree `.gbrain-source` pin, and registers the worktree for `gbrain search` / `gbrain code-def` / `gbrain query` semantic operations.

gbrain is a third-party (gstack-ecosystem) tool — JStack integrates with it but does not require it. If gbrain isn't installed, this skill reports the install path + exits.

## When to use

- New machine setup — first time using gbrain anywhere
- New worktree on an existing machine — pin this worktree to a gbrain source
- Switching gbrain modes (local-stdio vs remote-http)
- Validate existing gbrain config — `--check` runs read-only

## When NOT to use

- gbrain not installed and operator doesn't want it — skip entirely
- Existing gbrain setup working fine — `/sync-gbrain` is what you actually want
- Customer-data-bearing repo — STOP. gbrain indexes content; Layer 2 blocks production-data indexing.

## Inputs

- Optional `--mode <local-stdio|remote-http>` — gbrain transport (default: local-stdio)
- Optional `--remote-url <url>` — when mode=remote-http
- Optional `--source-name <name>` — name this worktree's source (default: repo name + branch)
- Optional `--check` — validate existing config, do not modify

## Workflow

1. **Preflight.** Verify `gbrain` binary present on PATH. If absent: print install instructions + exit.
2. **Compliance gate.** Verify current worktree's content does not match Layer 2 prod-data patterns (sanity-scan a sample of files). If hit: BLOCK with explanation.
3. **Read existing config.** `~/.gbrain/config.json`. Create if absent with sane defaults.
4. **Mode interview (if not specified).** AskUserQuestion: local-stdio (default, fastest, single-machine) vs remote-http (shared brain across machines, requires brain-server URL).
5. **Write config.** Atomic write to `~/.gbrain/config.json`.
6. **Pin worktree.** Write `.gbrain-source` file at git toplevel containing the source name. Add to `.gitignore` if not present.
7. **Initial index.** Trigger `gbrain index <source-name>` to build the first index. Stream progress.
8. **Validate.** Run `gbrain doctor --fast --json` and parse for green.
9. **Report.**

## Config schema

```json
{
  "version": 1,
  "mode": "local-stdio",
  "sources": {
    "jokerman-session-setup-main": {
      "path": "/e/Workspace/jokerman-session-setup",
      "indexed_at": "2026-05-27T18:14:03Z",
      "files_indexed": 64
    }
  },
  "remote": {
    "url": null
  }
}
```

## Report format

```
Setup gbrain: jokerman-session-setup-main

gbrain version: 0.14.2
Mode: local-stdio
Source: jokerman-session-setup-main
Path: /e/Workspace/jokerman-session-setup
Pin: /e/Workspace/jokerman-session-setup/.gbrain-source (added to .gitignore)

## Initial index
Indexed: 64 files (.md, .ts, .tsx, .py — see ~/.gbrain/config.json for full extension list)
Skipped: 12 files (binaries, lockfiles, build artifacts)
Duration: 8.2s

## Validation
✓ gbrain doctor --fast: all green
✓ gbrain search test ("voice corpus"): returns 3 matches in TRAILBLAZER-CORPUS.md

Ready: gbrain search <query> | gbrain code-def <symbol> | gbrain query <semantic question>
Refresh: /sync-gbrain
```

## Compliance integration

- Layer 2 pre-flight content scan — refuses to index any path containing customer-data patterns.
- `.gbrain-source` file added to `.gitignore` — pins are local, not shared across team checkouts.
- In remote-http mode: brain URL stored in config; URL itself is NOT a secret but treat as sensitive (don't commit, don't share publicly).
- Indexed content is local (local-stdio) or sent to the configured brain server (remote-http). Operator must trust the brain server in remote mode.

## Voice tier note

`voice: internal`. Setup ops are engineering-internal.

## Failure modes

- **gbrain not installed:** report install instructions for the operator's platform + exit. Do not silently degrade to Grep fallback.
- **Initial index crashes:** capture stderr, write to `~/.jstack/audit/gbrain-setup-<ts>.log`, report failure mode (most common: file-permission, OOM on huge repos, unsupported binary file).
- **Config file unwriteable:** report exact path + permission issue.
- **Remote mode without `--remote-url`:** prompt via AskUserQuestion.
- **`.gbrain-source` would overwrite existing pin:** ask whether to replace. Do not auto-overwrite.

## Examples

**Default local setup:**
```
> /setup-gbrain
[Interview: local-stdio confirmed]
[Indexes 64 files in 8.2s]
✓ Source pinned. /sync-gbrain to refresh later.
```

**Remote (shared) brain:**
```
> /setup-gbrain --mode remote-http --remote-url https://brain.example.com
[Verifies URL reachable, registers]
✓ Configured for remote mode. Indexing happens server-side on push.
```

**Validate existing:**
```
> /setup-gbrain --check
✓ Config valid, 3 sources registered, last sync 2h ago.
```

## See also

- `/sync-gbrain` — refresh the index after this skill set things up
- `gbrain` CLI — the underlying tool
- Layer 2 compliance — production-data indexing block
