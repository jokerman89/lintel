---
name: jstack-sync-brain
v1_alias: [jstack-sync-gbrain]
description: Refresh the gbrain index from the current worktree — incremental or full.
color: blue
tools: Read, Bash
voice: internal
cli_support: [claude-code]
---

# /sync-brain

Refreshes the gbrain index for the current worktree. Incremental by default (only changed files since last sync); `--full` re-indexes everything.

Idempotent — re-running is safe. If gbrain isn't set up: this skill suggests `/setup-brain` and exits without errors.

## When to use

- Made significant changes (refactor, large diff merge) — semantic queries should reflect new state
- New session, worktree is stale relative to last sync
- After branch switch, want gbrain to reflect the new branch's content
- Periodic refresh (consider configuring as a daily auto-run)

## When NOT to use

- gbrain not installed/configured — run `/setup-brain` first
- Tiny change (1-2 file edit) — incremental sync is cheap but the noise floor exists; just keep working
- Mid-session, no significant content change — wasted cycles

## Inputs

- Optional `--full` — re-index everything (slower, useful after major changes)
- Optional `--source <name>` — sync a specific source (default: pinned worktree)
- Optional `--quiet` — suppress progress, report only final state

## Workflow

1. **Preflight.** Check `gbrain` binary + `~/.gbrain/config.json` + worktree `.gbrain-source` pin. If any missing: surface what's missing + recommend `/setup-brain`.
2. **Compliance check.** Quick sanity-scan of newly-changed files (since last sync) for customer-data patterns. Block on hit. Logged commit hash of last sync to `~/.jstack/audit/gbrain-sync.jsonl`.
3. **Resolve source.** Read `.gbrain-source` pin or use `--source`.
4. **Determine sync scope.**
   - Incremental: git diff between last-sync commit and HEAD, file list.
   - Full: entire worktree.
5. **Invoke gbrain.** `gbrain index <source> [--incremental --since <commit>]`. Stream progress unless `--quiet`.
6. **Update config.** Write `indexed_at` + `last_sync_commit` to `~/.gbrain/config.json`.
7. **Report.**

## Report format

```
Sync gbrain: jokerman-session-setup-main

Mode: incremental
Last sync: 2026-05-27T14:22:01Z (commit a60c46c)
Current: 7255bfc

Files since last sync: 9 changed, 5 added, 0 deleted
Indexed: 14 files updated
Skipped: 2 (binary, lockfile)
Duration: 1.8s

## Validation
✓ gbrain doctor --fast: green
✓ Test query ("trailblazer corpus"): returns updated OurVoice-corpus.md
```

## Compliance integration

- Layer 2 sanity-scan on every newly-changed file before indexing. Block any that match customer-data patterns.
- In remote-http mode: content leaves the machine to the brain server. Treat brain server as a trusted but external system; do NOT sync if brain server policy isn't compatible with operator data class.
- Audit log records every sync with commit range + files-indexed count.

## Voice tier note

`voice: internal`. Sync ops are engineering-internal.

## Failure modes

- **gbrain not set up:** surface `/setup-brain` recommendation. Exit cleanly (not an error).
- **gbrain server unreachable (remote mode):** retry once; report failure with brain URL. Operator decides — wait or skip.
- **Compliance scan blocks a newly-changed file:** STOP sync, report which file + which pattern hit. Do not partial-index.
- **Index would exceed reasonable size (configurable cap):** WARN — large indexes degrade query performance. Recommend pruning .gbrain-source scope.
- **Git history rewritten since last sync:** detect via mismatch; recommend `--full` re-sync. Do not silently proceed with stale incremental delta.

## Examples

**Standard incremental:**
```
> /sync-brain
14 files updated, 1.8s. gbrain doctor green.
```

**Full after major refactor:**
```
> /sync-brain --full
64 files reindexed, 8.4s. Test query passes.
```

**gbrain not yet configured:**
```
> /sync-brain
gbrain config not found at ~/.gbrain/config.json
Run /setup-brain to initialize.
```

## See also

- `/setup-brain` — one-time configuration
- `gbrain` CLI — underlying tool
- `~/.gbrain/config.json` — config file
- `.gbrain-source` — per-worktree pin
