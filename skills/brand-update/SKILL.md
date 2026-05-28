---
name: li-brand-update
layer: ms-team
description: Pull/register MS brand assets to ~/.lintel/brand/ — version tracking, cache invalidation.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
---

# /brand-update

Operator-driven workflow to register a brand asset pull. Lintel doesn't automate the actual download (auth + corporate-portal access is operator-side). This skill:

1. Validates a staging directory the operator populated
2. Moves assets to `~/.lintel/brand/`
3. Records version + pull metadata
4. Invalidates cache (P3 fix T12)
5. Optionally restarts brand-staleness-warn hook timer

## When to use

- First brand pull (initial v2.0 setup)
- Periodic refresh (typically quarterly OR on `brand-staleness-warn` trigger)
- After MS brand portal version update
- Operator wants to verify current brand state

## When NOT to use

- Brand assets unchanged since last pull — `--register` re-validates without re-import
- Local-only modifications (not from portal) — those should be operator-authored templates, not brand updates

## Inputs

- `--staging <path>` — path to operator's staging dir containing pulled assets
- `--register` — just register metadata + invalidate cache (no asset move)
- `--invalidate-cache` — force cache rebuild without re-import
- `--verify` — check current `~/.lintel/brand/` state without changes
- `--version <text>` — brand portal version stamp (e.g. "2026-Q2")

## Workflow

1. **Verify staging structure** (`--staging` mode):
   ```
   <staging>/
     ppt-templates/       ≥1 .pptx
     word-templates/      ≥1 .docx
     web-templates/       ≥1 .html or directory
     azure-assets/        ≥10 .svg
     voice/               markdown files (optional)
   ```
   Reject if structure malformed; show what's missing.

2. **Confirm move** via AskUserQuestion:
   > "Move <count> assets from <staging> to ~/.lintel/brand/? Existing brand will be backed up."

3. **Backup existing.** `~/.lintel/brand/` → `~/.lintel/brand-backup-<timestamp>/`. Keep last 3 backups; older ones pruned.

4. **Move staging → live.** `cp -r <staging>/* ~/.lintel/brand/`.

5. **Write `brand-version.txt`**:
   ```
   version: 2026-Q2
   pulled_at: 2026-05-27T22:00:00Z
   pulled_by: <operator>
   source: MS brand portal
   asset_counts:
     ppt-templates: 4
     word-templates: 6
     web-templates: 2
     azure-assets: 87
     voice: 3
   ```

6. **Invalidate cache.** Remove `~/.lintel/brand/.cache/*`. Cache rebuilds on next doc-gen.

7. **Reset brand-staleness watcher.** Touch `~/.lintel/brand/.staleness-watcher-reset`.

8. **Report.**

## Report format

```
Brand update — 2026-Q2

Staging dir: /Users/operator/brand-staging-2026-q2
Validated: 4 PPT templates, 6 Word templates, 2 web templates, 87 Azure SVGs
Existing brand backed up: ~/.lintel/brand-backup-20260527-220000/
Backup retention: last 3 (pruned 0 older backups)
Cache invalidated: 47 cached entries cleared

brand-version.txt:
  version: 2026-Q2
  pulled_at: 2026-05-27T22:00:00Z
  asset_counts: { ppt: 4, word: 6, web: 2, azure: 87, voice: 3 }

Staleness watcher reset. Next warn: 2026-08-27 (90 days).

Doc-gen now uses pulled brand. Verify:
  /generate-ppt --use-defaults=false (test brand path)
  /asset-search "azure-sql" (test asset index)
```

## Compliance integration

- Brand assets are MS-internal IP. NOT customer data → no Layer 2 customer-data scan.
- Asset paths stored locally. NOT committed to git (`~/.lintel/brand/` is in `.gitignore` per BRAND-INTEGRATION.md).
- Backup retention bounded to prevent disk bloat.
- Audit log entry per pull: `~/.lintel/audit/brand-updates.jsonl`

## Voice tier note

`voice: internal`. Asset management is engineering-internal.

## Failure modes

- **Staging structure malformed** — refuse + name what's missing. Operator fixes.
- **Existing brand has uncommitted operator modifications** (rare; brand is normally not edited locally) — backup catches them. Surface to operator.
- **Disk space insufficient for backup** — refuse + free up space first.
- **Cache invalidation fails** (file permissions) — log + continue. Next doc-gen will warn about stale cache.

## Examples

**First-time pull:**
```
> /brand-update --staging ~/Downloads/ms-brand-2026-q2 --version 2026-Q2
[Validates structure, backs up, moves, registers]
✓ Brand 2026-Q2 active. 99 assets across 5 categories.
```

**Just register (assets already moved manually):**
```
> /brand-update --register --version 2026-Q2
[Validates ~/.lintel/brand/ contents, writes brand-version.txt]
✓ Registered. Cache invalidated.
```

**Verify current state:**
```
> /brand-update --verify
Current brand: 2026-Q1 (pulled 2026-02-15, 95 days ago — STALE warning likely)
Asset counts: { ppt: 4, word: 5, web: 2, azure: 82, voice: 2 }
```

## See also

- `BRAND-INTEGRATION.md` — full architecture
- `/asset-search` — search registered brand assets
- `brand-staleness-warn` hook — auto-warn at >90 days
- `/generate-ppt`, `/generate-word`, `/generate-web` — consumers
